import argparse
import json
import logging
import pickle
import re
import sys
from pathlib import Path

import flywheel

from .supporting_files import bidsify_flywheel, utils
from .supporting_files.project_tree import get_project_node, set_tree
from .supporting_files.templates import load_template
from .utils.curation_tools import find_how_curated

logger = logging.getLogger("curate-bids")


def clear_meta_info(context, template):
    if "info" in context:
        if template.namespace in context["info"]:
            del context["info"][template.namespace]
        if "IntendedFor" in context["info"]:
            del context["info"]["IntendedFor"]


def format_validation_error(err):
    path = "/".join(err.path)
    if path:
        return path + " " + err.message
    return err.message


def print_error_log(container, templateDef, errors):
    BIDS = container["info"].get("BIDS")
    bids_template = BIDS.get("template")

    error_message = ""

    if not bids_template:
        error_message += (
            "There was no BIDS template assigned in 'info.BIDS.template'. "
            "BIDS also encountered the following errors:\n"
        )
    else:
        error_message += (
            f"The BIDS template {bids_template} for this file encountered "
            f"the following errors:\n"
        )

    for ie, ee in enumerate(errors):
        error_message += (
            f"{ie + 1}:\n............................................................\n"
        )

        if ee.validator == "required":
            match = re.match("'(?P<prop>.*)' is a required property", ee.message)
            required_prop = match.group("prop")
            schema = templateDef.get("properties", {}).get(required_prop)
            schema.pop("auto_update", "")

            if schema is None:
                error_message += (
                    f"Schema for {required_prop} not found in template:\n"
                    f"{json.dumps(templateDef.get('properties'), indent=2)}"
                )
            else:
                error_message += (
                    f"The required property '{required_prop}' is missing or invalid.\n"
                    f"This property must exist, and must match the following conditons:\n"
                    f"{json.dumps(schema, indent=2)}\n\n"
                )

        else:
            prop = ee.path[0]
            schema = templateDef.get("properties", {}).get(prop)
            schema.pop("auto_update", "")

            error_message += (
                f"Property '{ee.schema.get('title')}' violates the"
                f" '{ee.validator}' requirement: {ee.message}\n"
            )
            error_message += (
                f"Property must match the following conditions:\n"
                f"{json.dumps(schema, indent=2)}\n\n"
            )

    return error_message


def validate_meta_info(container, template):
    """Validate meta information for files (only).

    Adds 'BIDS.NA' if no BIDS info present
    Adds 'BIDS.valid' and 'BIDS.error_message'
        to communicate to user if values are valid (!!! minimal being checked)

    TODO: validation needs to check for more than non-empty strings; e.g., alphanumeric

    """
    # Get namespace
    namespace = template.namespace

    # If 'info' is NOT in container, then must not
    #   have matched to a template, create 'info'
    #  field with object {'BIDS': 'NA'}
    if "info" not in container:
        container["info"] = {namespace: "NA"}
    # if the namespace ('BIDS') is NOT in 'info',
    #   then must not have matched to a template,
    #   add  {'BIDS': 'NA'} to the meta info
    elif namespace not in container["info"]:
        container["info"][namespace] = "NA"
    # If already assigned BIDS 'NA', then break
    elif container["info"][namespace] == "NA":
        pass
    # Otherwise, iterate over keys within container
    else:
        valid = True
        error_message = ""

        # Find template
        templateName = container["info"][namespace].get("template")
        if templateName:
            templateDef = template.definitions.get(templateName)
            if templateDef:
                errors = template.validate(templateDef, container["info"][namespace])
                if errors:
                    log_error = print_error_log(container, templateDef, errors)
                    logger.debug(log_error)

                    valid = False
                    error_message = "\n".join(
                        [format_validation_error(err) for err in errors]
                    )
            else:
                valid = False
                error_message += "Unknown template: %s. " % templateName

        # Assign 'valid' and 'error_message' values
        container["info"][namespace]["valid"] = valid
        container["info"][namespace]["error_message"] = error_message


def update_nifti_sidecar_fields(fw, acquisition_id, sidecar_name, sidecar_changes):
    """Set the values of the given field names to given values for the specified NIfTI file's .json sidecar.

    Since this uploads a new file (which becomes a new version of that file), it will lose metadata
    so info, classification, modality, and tags must be obtained from the original file and attached
    to the new file.

    Args:
        fw (Flywheel Client): to be able to access the file
        acquisition_id (str): The acquisition that the NIfTI and json files are in
        sidecar_name (str): Name of the NIfTI file's sidecar
        sidecar_changes (dict): add these key/val pairs to file.info
    """
    if isinstance(fw, flywheel.client.Client):
        acquisition = fw.get_acquisition(acquisition_id).reload()
        sidecar_file = acquisition.get_file(sidecar_name)
        sidecar_contents = acquisition.read_file(sidecar_name)
        if not sidecar_contents:
            print(f"Unable to load {sidecar_name}")
        sidecar_json = json.loads(sidecar_contents)
        need_to_write = False
        for key, val in sidecar_changes.items():
            if sidecar_json.get(key) != val:
                sidecar_json[key] = val
                need_to_write = True
        if not need_to_write:
            print(
                f"Skipping sidecar {sidecar_name} since it already has {sidecar_changes}"
            )
            return
        json_str = json.dumps(sidecar_json, indent=4)
        file_spec = flywheel.FileSpec(sidecar_name, json_str, "text/plain")
        acquisition.upload_file(file_spec)

        # make sure new file gets its old metadata back
        if len(sidecar_file.info) > 0:
            fw.set_acquisition_file_info(
                acquisition_id, sidecar_name, sidecar_file.info
            )
        if len(sidecar_file.classification) > 0:
            # This was added to avoid an exception, delete this someday
            if "Contrast" in sidecar_file.classification:
                # Contrast is not in the classification schema (yet?)
                del sidecar_file.classification["Contrast"]
            fw.modify_acquisition_file_classification(
                acquisition_id,
                sidecar_name,
                {
                    "replace": sidecar_file.classification,
                    "modality": sidecar_file.modality,
                },
            )
        if len(sidecar_file.tags) > 0:
            fw.add_file_tags(sidecar_file.file_id, sidecar_file.tags)

    else:  # must be a test
        print(f"Client is {type(fw)}.  Cannot update sidecar")


def update_meta_info(
    fw: flywheel.Client, context: dict, save_sidecar_as_metadata: bool
) -> None:
    """
    Update metadata information for various Flywheel container types.

    This function updates the metadata information for files, projects, sessions,
    and acquisitions based on the provided context. It handles modifications to
    BIDS sidecar files and updates the Flywheel container metadata accordingly.

    Args:
        fw (flywheel.Client): The Flywheel client instance used to interact with the Flywheel API.
        context (dict): A dictionary containing the Flywheel context information for the update.
                        Expected keys include:
                        - "container_type" (str): The type of container to update (e.g., "file", "project", "session", "acquisition").
                        - "parent_container_type" (str): The type of the parent container (e.g., "acquisition", "project", "session").
                        - "file" (dict): Information about the file to update, including "info" and "name".
                        - "acquisition" (dict): Information about the acquisition, including "id".
                        - "project" (dict): Information about the project, including "id" and "info".
                        - "session" (dict): Information about the session, including "id" and "info".
        save_sidecar_as_metadata (bool): A flag indicating whether to save sidecar changes as metadata.

    Returns:
        None
    """

    # Modify file
    if context["container_type"] == "file":
        # Modify acquisition file
        if context["parent_container_type"] == "acquisition":
            bids_info = context["file"]["info"]["BIDS"]
            # Handle things like TaskName is required in BIDS, but it's not in the DICOM, so it has to be set here
            if "sidecarChanges" in bids_info:
                if save_sidecar_as_metadata:
                    for key, val in bids_info["sidecarChanges"].items():
                        context["file"]["info"][key] = val
                sidecar_name = context["file"]["name"]
                # only modify sidecar (NIfTI file also has sidecarChanges in BIDS)
                if sidecar_name.endswith(".json"):
                    update_nifti_sidecar_fields(
                        fw,
                        context["acquisition"]["id"],
                        sidecar_name,
                        bids_info["sidecarChanges"],
                    )
            fw.set_acquisition_file_info(
                context["acquisition"]["id"],
                context["file"]["name"],
                context["file"]["info"],
            )
        # Modify project file
        elif context["parent_container_type"] == "project":
            fw.set_project_file_info(
                context["project"]["id"],
                context["file"]["name"],
                context["file"]["info"],
            )
        # Modify session file
        elif context["parent_container_type"] == "session":
            fw.set_session_file_info(
                context["session"]["id"],
                context["file"]["name"],
                context["file"]["info"],
            )
        else:
            logger.info(
                "Cannot determine file parent container type: "
                + context["parent_container_type"]
            )
    # Modify project
    elif context["container_type"] == "project":
        fw.replace_project_info(context["project"]["id"], context["project"]["info"])
    # Modify session
    elif context["container_type"] == "session":
        fw.replace_session_info(context["session"]["id"], context["session"]["info"])
    # Modify acquisition
    elif context["container_type"] == "acquisition":
        fw.replace_acquisition_info(
            context["acquisition"]["id"], context["acquisition"]["info"]
        )
    # Cannot determine container type
    else:
        logger.info("Cannot determine container type: " + context["container_type"])


class Count:
    def __init__(self):
        self.containers = 0  # counts project, sessions and acquisitions
        self.sessions = 0
        self.acquisitions = 0
        self.files = 0


SIDECAR_NAME = "dataset_description.json"


def save_dataset_description_file(project, template_definition):
    """Write out dataset_description.json file using dictionary and substitute the project name.

    Args:
        project (Project container)
        template_definition (dict): the contents of the dataset_description.json file
    """
    json_data = dict()
    # get contents of definition to put into json file
    for key, value in template_definition["properties"].items():
        json_data[key] = value["default"]
        if key == "Name":
            json_data[key] = project.label
    json_str = json.dumps(json_data, indent=4)
    file_spec = flywheel.FileSpec(SIDECAR_NAME, json_str, "text/plain")
    project.upload_file(file_spec)


def save_project_files(project, template, save_sidecar_as_metadata):
    """Create required "dataset_description.json" sidecar and README files.

    They are created only if they don't already exist.

    Args:
        project (Project container)
        template (Template) the project curation template (has contents of dataset_description file)
        save_sidecar_as_metadata (bool): if true, save sidecar data as metadata also
    """
    proj_sidecars = [file for file in project.files if file.name == SIDECAR_NAME]

    if len(proj_sidecars) > 1:
        logger.debug("ERROR: multiple '%s' files exist", SIDECAR_NAME)
    elif len(proj_sidecars) == 1:
        logger.info("'%s' file already exists", SIDECAR_NAME)
    else:  # create and attach file to project
        logger.info("'%s' file does not exist, creating it...", SIDECAR_NAME)
        if "dataset_description_file" in template.definitions:
            save_dataset_description_file(
                project, template.definitions["dataset_description_file"]
            )
        elif "Acknowledgements" in template.definitions["project"]["properties"]:
            # then it is an old style template so use what is there
            save_dataset_description_file(project, template.definitions["project"])
        else:
            logger.debug(
                "ERROR: dataset_description_file data is missing from project curation template"
            )

    if save_sidecar_as_metadata != find_how_curated(
        project.info, "BIDS", save_sidecar_as_metadata=save_sidecar_as_metadata
    ):
        # find_how_curated will run through the various states of curation and report warnings where there are mismatches
        logger.warning(
            "save_sidecar_as_metadata is different from how the project has been curated. Respecting the explicit save_sidecar_as_metadata argument value: %s",
            save_sidecar_as_metadata,
        )

    # Create README file on project
    README_NAME = "README.txt"
    proj_readmes = [file for file in project.files if file.name == README_NAME]
    if len(proj_readmes) > 1:
        logger.debug("ERROR: multiple '%s' files exist", README_NAME)
    elif len(proj_readmes) == 1:
        logger.info("'%s' file already exists", README_NAME)
    else:  # create and attach file to project
        logger.info("'%s' file does not exist, creating it...", README_NAME)
        text_str = project.label
        file_spec = flywheel.FileSpec(README_NAME, text_str, "text/plain")
        project.upload_file(file_spec)


def curate_bids(
    fw,
    project_id,
    subject_id="",
    session_id="",
    reset=False,
    recurate_project=True,
    template_name="",
    template_path="",
    pickle_tree=False,
    dry_run=False,
    save_sidecar_as_metadata=False,
):
    """Curate BIDS.

    If curating an entire project, loop over subjects to find all sessions.  Curate all sessions for a given
    subject at the same time so "resolvers" can work on all sessions for the subject.
    This can run on only one subject or session if desired by providing an ID.

    Args:
        fw (Flywheel Client): The Flywheel Client
        project_id (str): The Flywheel Project container ID.
        subject_id (str): The Flywheel subject container ID (will only curate this subject).
        session_id (str): The Flywheel session container ID (will only curate this session).
        reset (bool): Whether to erase info.BIDS before curation.
        recurate_project (bool): If project container is already curated, make this False
        template_name (str): Which template type to use. Options include:
                Default, BIDS-v1, ReproIn.
        template_path (str): Provide a specific template file. Supersedes template_name.
        save_sidecar_as_metadata (bool): sidecar data is in file.info (metadata) so for
                IntendedFors, update metadata instead of updating the actual json sidecar.
    """
    count = Count()

    project = fw.get_project(project_id)

    logger.debug("Trying to load %s template.", template_name)
    template = load_template(template_path, template_name, save_sidecar_as_metadata)

    if (
        "project" in template.definitions
        and "Acknowledgements" in template.definitions["project"]
        and not save_sidecar_as_metadata
    ):
        # then it is an old project curation template so warn of possible trouble.
        # if dcm2niix put sidecar data in NIfTI file.info.BIDS, everything will be fine
        # but if not (the new way where sidecars have that data), there will be an error.
        logger.warning(
            "An old style project curation template is being used: "
            "when exporting data in BIDS format, this will cause any json sidecar "
            "files TO BE IGNORED and BIDS Custom Information will be used instead to "
            "create sidecar files."
        )
        logger.warning(
            "If this is NOT the desired behavior, please use the BIDS_sidecar_hierarchy_curator.ipynb to standardize the curation style."
        )

    save_project_files(project, template, save_sidecar_as_metadata)

    p_name = f"project_node_{project_id}.pickle"
    if pickle_tree and Path(p_name).exists():
        logger.info("Using pickled %s", p_name)
        with open(p_name, "rb") as f:
            project_node = pickle.load(f)
    else:
        project_node = get_project_node(fw, project_id)

        if pickle_tree:
            with open(p_name, "wb") as f:
                pickle.dump(project_node, f)

    # Curate the project all by itself
    count = curate_bids_tree(
        fw,
        template,
        project_node,
        count,
        reset=reset,
        recurate_project=recurate_project,
        dry_run=dry_run,
        save_sidecar_as_metadata=save_sidecar_as_metadata,
    )

    if session_id:
        logger.info("Getting single session ID=%s", session_id)
        session = fw.get_session(session_id)
        subject_id = session.subject.id

    if subject_id:
        logger.info("Getting single subject ID=%s", subject_id)
    else:
        logger.info("Getting all subjects")

    for subject in project.subjects.iter():
        if subject_id and subject_id != subject.id:
            continue

        p_name = f"subject_node_{subject.id}.pickle"
        if pickle_tree and Path(p_name).exists():
            logger.info("Using pickled %s", p_name)
            with open(p_name, "rb") as f:
                project_node = pickle.load(f)
        else:
            # if session_id is set, this skips everything but that one
            set_tree(fw, project_node, subject, session_id)

            if pickle_tree:
                with open(p_name, "wb") as f:
                    pickle.dump(project_node, f)

        count = curate_bids_tree(
            fw,
            template,
            project_node,
            count,
            reset=reset,
            recurate_project=False,
            dry_run=dry_run,
            save_sidecar_as_metadata=save_sidecar_as_metadata,
        )

        project_node.children.clear()  # no need to keep previous subjects

    logger.info("Curated %s session containers", count.sessions)
    logger.info("Curated %s acquisition containers", count.acquisitions)
    logger.info("Curated %s files", count.files)
    num_proj_ses_acq = 1 + count.sessions + count.acquisitions
    if count.containers != num_proj_ses_acq:
        logger.warning(
            "Container_counter should be %s but it is %s",
            num_proj_ses_acq,
            count.containers,
        )


def curate_bids_tree(
    fw,
    template,
    project_node,
    count,
    reset=False,
    recurate_project=True,
    dry_run=False,
    save_sidecar_as_metadata=False,
):
    """Curate BIDS tree.

    Given a BIDS project curation template and Flywheel hierarchy context, figure out the proper
    metadata fields to be able to save data in BIDS format.  The context must include the project
    information to be able to curate any subject or session.  The context should include no more
    than one subject in case there are very many subjects.  The context may consist of a single
    session.

    "Resolvers" are used here to fill in information across sessions.  The only current example
    is the "IntendedFor" BIDS field which is used to list the scans that a field map intends to
    correct.  All sessions for a given subject need to be processed at the same time to allow
    this to happen.

    Args:
        fw (Flywheel Client): The Flywheel Client
        template (template.Template): A collection of definitions and rules to populate definition values
        project_node (TreeNode): The context for BIDS processing: a tree of containers and files on them
        count (Count): The number of project|session|acquisition|files containers processed
        reset (bool): Whether to erase info.BIDS before curation.
        recurate_project (bool): The project_node is always provided, this allows the project to remain curated as is
    Return:
        count (Count)
    """
    # Curation begins: match, resolve, update

    # Match: do initial template matching and updating

    # Keep these so files can be ignored if these are already ignored
    current_session_ignored = False
    current_acquisition_ignored = False

    for context in project_node.context_iter():
        ctype = context["container_type"]

        if recurate_project is False:
            if ctype == "project":
                logger.debug("Not re-curating project container")
                continue
            elif ctype == "file" and context["parent_container_type"] == "project":
                logger.debug(
                    "Not re-curating project file %s", context["file"].data["name"]
                )
                continue

        # Cleanup, if indicated
        if reset:
            clear_meta_info(context[ctype], template)

        elif context[ctype].get("info", {}).get("BIDS") == "NA":
            continue

        # BIDSIFY: note that subjects are not bidsified because they have no BIDS information on them.
        if ctype in ["project", "session", "acquisition"]:
            logger.info(
                f"{count.containers}: Bidsifying Container: <{ctype}> <{context.get(ctype).get('label')}>"
            )

            count.containers += 1
            if ctype == "session":
                count.sessions += 1
            elif ctype == "acquisition":
                count.acquisitions += 1

            bidsify_flywheel.process_matching_templates(context, template)

            if ctype == "session":
                current_session_ignored = context["session"].data["info"]["BIDS"][
                    "ignore"
                ]
            elif ctype == "acquisition":
                current_acquisition_ignored = context["acquisition"].data["info"][
                    "BIDS"
                ]["ignore"]

            # Add run counter for session
            if ctype == "session":
                logger.debug(
                    f"adding run counter for session {context.get(ctype).get('label')}\n"
                )
                context["run_counters"] = utils.RunCounterMap()

        elif ctype == "file":
            logger.debug(
                f"\nBidsifying file: <{ctype}> <{context.get(ctype).get('name')}>"
            )

            count.files += 1

            # Process matching
            context["file"] = bidsify_flywheel.process_matching_templates(
                context, template
            )

            if current_session_ignored or current_acquisition_ignored:
                if "BIDS" in context["file"].data["info"]:
                    context["file"].data["info"]["BIDS"]["ignore"] = True
                else:
                    pass  # no BIDS metadata field to set

            # Validate meta information
            validate_meta_info(context["file"], template)

    if not dry_run:
        # Resolve: perform path resolutions, if needed.  Currently only used to handle "IntendedFor" field which
        # needs to happen after a subject has been curated.
        for context in project_node.context_iter():
            bidsify_flywheel.process_resolvers(context, template)

        # Update: send updates to Flywheel, if the Flywheel Client is instantiated
        if fw:
            logger.info("Updating BIDS metadata on Flywheel")
            for context in project_node.context_iter():
                ctype = context["container_type"]
                if recurate_project is False:
                    if ctype == "project":
                        logger.debug("Not updating BIDS for project container")
                        continue
                    elif (
                        ctype == "file"
                        and context["parent_container_type"] == "project"
                    ):
                        logger.debug("Not updating BIDS for project files")
                        continue
                node = context[ctype]
                if node.is_dirty():
                    update_meta_info(fw, context, save_sidecar_as_metadata)
        else:
            logger.info("Missing fw, cannot update BIDS metadata on Flywheel")
    else:
        logger.info("Dry run, NOT updating BIDS metadata on Flywheel")

    return count


def configure_logging(verbosity):
    my_logs = ["curate-bids"]

    loggers = [  # noqa: F841
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name in my_logs
    ]

    # Custom levels of 0 and 1 may be sent from legacy code;
    # 20 == INFO and 10 == DEBUG in modern python logging
    if verbosity in (0, 20):
        print('setting log level to "info"')
        logging.basicConfig(
            format="[ %(module)s %(asctime)2s %(levelname)2s] %(message)s"
        )
        logger.setLevel(logging.INFO)

    elif verbosity in (1, 10):
        print('setting log level to "debug"')
        logging.basicConfig(
            format="[ %(module)s %(asctime)2s %(levelname)2s: %(lineno)s] %(message)s"
        )
        logger.setLevel(logging.DEBUG)


def main_with_args(
    fw,
    session_id,
    reset,
    session_only,
    template_name,
    template_path=None,
    subject_id="",
    project_label="",
    group_id="",
    verbosity=1,
    pickle_tree=False,
    dry_run=False,
    save_sidecar_as_metadata=False,
):
    """Run BIDS Curation, called by curate-bids Gear or CLI."""
    configure_logging(verbosity)

    if group_id:
        project_id = utils.validate_project_label(fw, project_label, group_id=group_id)
    elif project_label:
        project_id = utils.validate_project_label(fw, project_label)
    elif subject_id:
        project_id = utils.get_project_id_from_subject_id(fw, subject_id)
    elif session_id:
        project_id = utils.get_project_id_from_session_id(fw, session_id)
    else:
        logger.error(
            "Either project label (group id optional) or subject/session id is required!"
        )
        sys.exit(1)

    # no longer passing session_only along.  Empty session_id means get all sessions.
    if not session_only:
        session_id = ""

    # Curate BIDS
    curate_bids(
        fw,
        project_id,
        subject_id=subject_id,
        session_id=session_id,
        reset=reset,
        recurate_project=True,
        template_name=template_name,
        template_path=template_path,
        pickle_tree=pickle_tree,
        dry_run=dry_run,
        save_sidecar_as_metadata=save_sidecar_as_metadata,
    )


def main():
    parser = argparse.ArgumentParser(description="BIDS Curation")
    parser.add_argument(
        "--api-key", dest="api_key", action="store", required=True, help="API key"
    )
    parser.add_argument(
        "-p",
        dest="project_label",
        action="store",
        required=False,
        default=None,
        help="A Flywheel instance Project label.",
    )
    parser.add_argument(
        "-g",
        dest="group_id",
        action="store",
        required=False,
        default=None,
        help="A Flywheel instance Group ID.",
    )
    parser.add_argument(
        "--subject",
        dest="subject_id",
        action="store",
        required=False,
        default="",
        help="A Flywheel instance Subject ID; alternative to determine Project label.",
    )
    parser.add_argument(
        "--session",
        dest="session_id",
        action="store",
        required=False,
        default="",
        help="A Flywheel instance Session ID; alternative to determine Project label.",
    )
    parser.add_argument(
        "--reset",
        dest="reset",
        action="store_true",
        default=False,
        help="Hard reset of BIDS metadata before running.",
    )
    parser.add_argument(
        "--recurate_project",
        dest="recurate_project",
        action="store_true",
        default=True,
        help="Re-curate the project.",
    )
    parser.add_argument(
        "--template-type",
        dest="template_name",
        action="store",
        required=False,
        default=None,
        help="Which template type to use. Options include : Default, ReproIn, or Custom.",
    )
    parser.add_argument(
        "--template-file",
        dest="template_path",
        action="store",
        default=None,
        help="Template file to use. Supersedes the --template-type flag.",
    )
    parser.add_argument(
        "--pickle_tree",
        dest="pickle_tree",
        action="store_true",
        default=False,
        help="Use pickled context if available, save if not (used for debugging).",
    )
    parser.add_argument(
        "--dry_run",
        dest="dry_run",
        action="store_true",
        default=False,
        help="Dry run does not update Flywheel metadata.",
    )
    parser.add_argument(
        "--verbosity",
        dest="verbosity",
        action="store",
        type=int,
        default=1,
        help="Debug level (0, 10, 2, 20)",
    )
    parser.add_argument(
        "--save_sidecar_as_metadata",
        choices=["yes", "no", "auto"],
        default="auto",
        required=False,
        help="The BIDS sidecar is metadata in file.info. (default = auto)",
    )

    args = parser.parse_args()

    configure_logging(int(args.verbosity))

    # Prep
    # Check API key - raises Error if key is invalid
    fw = flywheel.Client(args.api_key)

    if args.group_id:
        project_id = utils.validate_project_label(
            fw, args.project_label, group_id=args.group_id
        )
    elif args.project_label:
        project_id = utils.validate_project_label(fw, args.project_label)
    elif args.subject_id:
        project_id = utils.get_project_id_from_subject_id(fw, args.subject_id)
    elif args.session_id:
        project_id = utils.get_project_id_from_session_id(fw, args.session_id)
    else:
        logger.error(
            "Either project label (group id optional) or subject/session id is required!"
        )
        sys.exit(1)

    project = fw.get_project(project_id)
    save_sidecar_as_metadata = find_how_curated(
        project.info, "BIDS", args.save_sidecar_as_metadata
    )
    # if save_sidecar_as_metadata is true, then the sidecar data is in NIfTI file metadata (file.info)
    # and any existing sidecar data will be ignored.

    # Curate BIDS project
    curate_bids(
        fw,
        project_id,
        args.subject_id,
        args.session_id,
        reset=args.reset,
        recurate_project=True,
        template_name=args.template_name,
        template_path=args.template_path,
        pickle_tree=args.pickle_tree,
        dry_run=args.dry_run,
        save_sidecar_as_metadata=save_sidecar_as_metadata,
    )


if __name__ == "__main__":
    main()
