import argparse
import csv
import json
import logging
import os
import re
import shutil
import sys

import flywheel
from six.moves import reduce

from .supporting_files import bidsify_flywheel, classifications, utils
from .supporting_files.templates import Template, load_template

SECONDS_PER_YEAR = 86400 * 365.25

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bids-uploader")


####### Alphabetized, helper methods ########
def attach_json(fw, file_info, save_sidecar_as_metadata=False, overwrite=False):
    # Parse JSON file
    contents = parse_json(file_info["full_filename"])
    # Attach parsed JSON to project
    if "dataset_description.json" in file_info["full_filename"]:
        proj = fw.get_project(file_info["id"])
        if file_does_not_exist(proj.files, file_info["full_filename"]) or overwrite:
            proj.upload_file(file_info["full_filename"])
        # Following lines add the json contents as metadata
        # proj = fw.get_project(file_info["id"]).to_dict()
        # proj.get("info").get(template_namespace).update(contents)
        # fw.modify_project(
        #    file_info["id"],
        #    {"info": {template_namespace: proj.get("info").get(template_namespace)}},
        # )
    # Otherwise... it's a JSON file that should be assigned to acquisition file(s)
    elif file_info["id_type"] == "project":
        # Get sessions within project
        proj_sess = [s.to_dict() for s in fw.get_project_sessions(file_info["id"])]
        for proj_ses in proj_sess:
            # Get acquisitions within session
            ses_acqs = [
                a.to_dict() for a in fw.get_session_acquisitions(proj_ses["id"])
            ]
            for ses_acq in ses_acqs:
                # Iterate over every acquisition file
                for f in ses_acq["files"]:
                    # Determine if json file components are all within the acq filename
                    if (
                        compare_json_to_file(
                            os.path.basename(file_info["full_filename"]), f["name"]
                        )
                        and save_sidecar_as_metadata
                    ):
                        # JSON matches to file - assign json contents as file meta info
                        f["info"].update(contents)
                        fw.set_acquisition_file_info(
                            ses_acq["id"], f["name"], f["info"]
                        )
                    elif compare_json_to_file(
                        os.path.basename(file_info["full_filename"]), f["name"]
                    ) and (
                        file_does_not_exist(
                            ses_acq["files"], file_info["full_filename"]
                        )
                        or overwrite
                    ):
                        fw.upload_file_to_session(
                            ses_acq["id"], file_info["full_filename"]
                        )

    # Figure out which acquisition files within SESSION should have JSON info attached...
    elif file_info["id_type"] == "session":
        # Get session and iterate over every acquisition file
        ses_acqs = [a.to_dict() for a in fw.get_session_acquisitions(file_info["id"])]
        for ses_acq in ses_acqs:
            for f in ses_acq["files"]:
                # Determine if json file components are all within the acq filename
                if (
                    compare_json_to_file(
                        os.path.basename(file_info["full_filename"]), f["name"]
                    )
                    and save_sidecar_as_metadata
                ):
                    # JSON matches to file - assign json contents as file meta info
                    f["info"].update(contents)
                    fw.set_acquisition_file_info(ses_acq["id"], f["name"], f["info"])
                elif compare_json_to_file(
                    os.path.basename(file_info["full_filename"]), f["name"]
                ) and (
                    file_does_not_exist(ses_acq["files"], file_info["full_filename"])
                    or overwrite
                ):
                    fw.upload_file_to_session(ses_acq["id"], file_info["full_filename"])

    # Figure out which acquisition files within ACQUISITION should have JSON info attached...
    elif file_info["id_type"] == "acquisition":
        acq = fw.get_acquisition(file_info["id"]).to_dict()
        for f in acq["files"]:
            # Determine if json file components are all within the acq filename
            if (
                compare_json_to_file(
                    os.path.basename(file_info["full_filename"]), f["name"]
                )
                and save_sidecar_as_metadata
            ):
                # JSON matches to file - assign json contents as file meta info
                f["info"].update(contents)
                fw.set_acquisition_file_info(acq["id"], f["name"], f["info"])
            elif compare_json_to_file(
                os.path.basename(file_info["full_filename"]), f["name"]
            ) and (
                file_does_not_exist(acq["files"], file_info["full_filename"])
                or overwrite
            ):
                fw.upload_file_to_acquisition(acq["id"], file_info["full_filename"])


def attach_project_tsv(fw, project_id, info_rows):
    # Get sessions within project
    sessions = [s.to_dict() for s in fw.get_project_sessions(project_id)]
    sessions_by_code = {}

    for ses in sessions:
        code = ses["subject"]["code"]
        sessions_by_code.setdefault(code, []).append(ses)

    # Iterate over participants
    for row in info_rows:
        sessions = sessions_by_code.get(row["participant_id"], [])
        for ses in sessions:
            # If they supplied a session_id, we can verify
            have_session_id = "session_id" in row
            if have_session_id and row["session_id"] != ses["label"]:
                continue

            session_info = {"subject": {"info": {}}}
            for key, value in row.items():
                # If key is age, convert from years to seconds
                if key == "age":
                    if not have_session_id and len(sessions) > 1:
                        logger.warning(
                            "Setting subject age on session in a longitudinal study!"
                        )
                    session_info[key] = int(value * SECONDS_PER_YEAR)
                elif key in ["first name", "last name", "sex", "race", "ethnicity"]:
                    session_info["subject"][key] = value
                elif key not in ("participant_id", "session_id"):
                    session_info["subject"]["info"][key] = value

            subject_info = session_info.pop("subject", None)
            if subject_info:
                fw.modify_subject(ses["subject"]["id"], subject_info)

            if session_info:
                fw.modify_session(ses["id"], session_info)


def attach_session_tsv(fw, session_id, info_rows):
    """Attach info to acquisition files."""
    # Get all acquisitions within session
    acquisitions = [a.to_dict() for a in fw.get_session_acquisitions(session_id)]
    # Iterate over all acquisitions within session
    for row in info_rows:
        # Get filename from within tsv
        #     format is 'func/<filename>'
        filename = row.pop("filename").split("/")[-1]

        for acq in acquisitions:
            # Get files within acquisitions
            for f in acq["files"]:
                # Iterate over all values within TSV -- see if it matches the file

                # If file in acquisition matches file in TSV file, add file info
                if filename == f["name"]:
                    # Modify acquisition file
                    fw.set_acquisition_file_info(acq["id"], filename, row)


def attach_subject_tsv(fw, subject_id, info_rows):
    # Get sessions within subject
    sessions = [s.to_dict() for s in fw.get_subject_sessions(subject_id)]

    for row in info_rows:
        for ses in sessions:
            if row["session_id"] != ses["label"]:
                continue

            session_info = {"info": {}}
            for key, value in row.items():
                if key == "age":
                    session_info[key] = int(value * SECONDS_PER_YEAR)
                elif key != "session_id":
                    session_info["info"][key] = value

            fw.modify_session(ses["id"], session_info)


def attach_tsv(fw, file_info, overwrite=False):
    ## Parse TSV file
    contents = parse_tsv(file_info["full_filename"])

    ## Attach TSV file contents
    # Get headers of the TSV file
    headers = contents[0]

    # Normalize session
    if headers and headers[0] == "session":
        headers[0] = "session_id"

    tsvdata = contents[1:]

    info_rows = [dict(zip(headers, row)) for row in tsvdata]

    if file_info["id_type"] == "project":
        attach_project_tsv(fw, file_info["id"], info_rows)
    elif file_info["id_type"] == "subject":
        attach_subject_tsv(fw, file_info["id"], info_rows)
    if file_info["id_type"] == "session":
        attach_session_tsv(fw, file_info["id"], info_rows)


def check_bids_dir_name(path: str):
    """Validate the modality portion of the BIDS naming scheme is used for the uploaded path/metadata.

    Necessary to correct paths where extra entities or information are propagated
    the acquisition label or left in the directory name of the uploaded file.
    The metadata is used for curation and export, so the structure needs to
    follow BIDS convention, not the original upload structure.

    :param path (str): full path for the file being uploaded
    :return: correct path and foldername (str): corrected data for the metadata
    """
    foldername = path.split(os.sep)[-1]
    # Get the base name of the folder, if there are extra details in the name
    if re.search(r"[-_]", foldername, re.IGNORECASE):
        corrected_foldername = re.split("[-_]", foldername)[0]
        corrected_path = os.path.join(os.path.dirname(path), corrected_foldername)
        return corrected_path, corrected_foldername
    else:
        return path, foldername


def check_enabled_rules(fw, project_id):
    for rule in fw.get_project_rules(project_id):
        if not rule.get("disabled"):
            return True
    return False


def check_modality_supported(modality):
    """Check if the modality folder (i.e., 'anat') is in the dictionary of supported
    modality types. Only keys in the dictionary have been defined in the template.
    """
    if any(substr in modality for substr in classifications.classifications.keys()):
        return True
    elif "." not in modality:
        logger.warning(
            f"{modality} is not yet supported for BIDS import.\n"
            f"Expecting one of the following modalities as the folder name:\n"
            f"{classifications.classifications.keys()}"
        )
        return False
    else:
        # Has warning from previous search; silent return
        return False


def classify_acquisition(full_fname):
    """Return classification of file based on filename."""
    # Get the folder and filename from the full filename
    full_fname = os.path.normpath(full_fname)
    parts = full_fname.split(os.sep)
    folder = parts[-2]
    # In case the folder name is reproin or something longer than BIDS modality names
    if len(folder) > 4:
        folder = classifications.determine_modality(folder)
    filename = parts[-1]
    # Get the modality label
    modality_ext = filename.split("_")[-1]
    # remove extension
    modality = modality_ext.split(".")[0]

    # Collect the specific type of scans that have been defined for a given modality
    # These options are searched below to determine how to populate the metadata to
    # describe the image.
    result = classifications.classifications.get(folder).get(modality.lower())
    if not result:
        result = classifications.search_classifications(folder, filename)

    if result:
        for k in result.keys():
            v = result[k]
            if not isinstance(v, list):
                result[k] = [v]

    return result


def compare_json_to_file(json_filename, filename):
    """Determine if a JSON file's contents apply to a filename.

    json_filename: Name of the json filename
    filename: Name of the file in question, does
        the json file contents apply to this file?

    i.e.
        The following json_filename...

            'task-rest_acq-fullbrain_bold.json'

        ...applies to the following filenames:

        'sub-01_ses-1_task-rest_acq-fullbrain_run-1_bold.nii.gz'
        'sub-01_ses-1_task-rest_acq-fullbrain_run-2_bold.nii.gz'
        'sub-01_ses-2_task-rest_acq-fullbrain_run-1_bold.nii.gz'
        'sub-01_ses-2_task-rest_acq-fullbrain_run-2_bold.nii.gz'

    NOTE: files must be a nifti or tsv.gz file...

    """
    # First check if file is a nifti file...
    if (".nii" not in filename) and (".tsv.gz" not in filename):
        match = False
    else:
        # Remove .json extension from filename
        json_filename = re.sub(".json", "", json_filename)
        # Split json filename up into components
        components = json_filename.split("_")
        # Iterate over all components within JSON file,
        #   if any of them are missing, match is False
        match = True
        for c in components:
            if c not in filename:
                match = False
                break

    return match


def convert_dtype(contents):
    """Take the parsed TSV file and convert columns
    from string to float or int.
    """
    # Convert contents to array
    contents_arr = contents[1:]
    cols = list(zip(*contents_arr))

    # Iterate over every column in array
    for idx in range(len(cols)):
        # Get column
        col = cols[idx]

        # Determine if column contains float/integer/string
        #    Check if first element is a float
        if "." in col[0]:
            # Try to convert to float
            try:
                col = [float(x) for x in col]
            except ValueError:
                pass
        # Else try and convert column to integer
        else:
            # Convert to integer
            try:
                col = [int(x) for x in col]
            # Otherwise leave as string
            except ValueError:
                pass

        # Check if column only contains 'F'/'M'
        #   if so, convert to 'Female'/'Male'
        if set(col).issubset({"F", "M", "O"}):
            # Iterate over column, replace
            col = list(col)
            for idxxx, item in enumerate(col):
                if item == "F":
                    col[idxxx] = "female"
                elif item == "M":
                    col[idxxx] = "male"
                elif item == "O":
                    col[idxxx] = "other"
                else:
                    continue
        ### Take converted column and place back into the content list
        for idxx in range(len(contents[1:])):
            contents[idxx + 1][idx] = col[idxx]

    return contents


def disable_project_rules(fw, project_id):
    """Disables rules for a project, because the classifier and nifti will erase
    the information from the upload.
    """
    for rule in fw.get_project_rules(project_id):
        fw.modify_project_rule(project_id, rule.id, {"disabled": True})


def determine_acquisition_label(foldername, fname, hierarchy_type):
    """
    Use file structure naming schemes, specified by the hierarchy_type, to
    take local files and send them to Flywheel as BIDSified names.

    Args:
        foldername (str): name of the modality folder in the dataset currently
                            being processed (e.g., 'anat')
        fname (str): name of the file being uploaded (NOT the full path)
        hierarchy_type (str): option set by "--type" in import cmd args. Default is "Flywheel"
    Returns
        acq_label (str): name of the file that will be used as the acquisition.label in the hierarchy.
    """
    # If bids hierarchy, the acquisition label is
    if hierarchy_type == "BIDS":
        acq_label = foldername
    else:
        # Get acq_label from file basename
        #  remove extension from the filename
        fname = fname.split(".")[0]
        #  split up filename into parts, removing the final part, the Modality
        parts = fname.split("_")

        # reorder name parts and handle modality-specific cases
        if not hasattr(sys.modules[__name__], "reproin_%s" % foldername):
            foldername = classifications.determine_modality(foldername)

        if hasattr(sys.modules[__name__], "reproin_%s" % foldername):
            parts = getattr(sys.modules[__name__], "reproin_%s" % foldername)(parts)
            # Ensure no dups, as would happen, if the orig input was already reproin
            # + preserve order with the list.
            seen = {}
            parts = [seen.setdefault(x, x) for x in parts if x not in seen]
            # Rejoin filename parts to form acquisition label
            acq_label = "_".join(parts)
            # Remove any of the following values
            for pattern in [
                "sub-[0-9a-zA-Z]+_",
                "ses-[0-9a-zA-Z]+",
                "_recording-[0-9a-zA-Z]+",
                "_$",
            ]:
                acq_label = re.sub(pattern, "", acq_label)
                # Sometimes session is not followed by an underscore, so the regex has to be as above for multiple
                # files. However, that pattern leaves two underscores in a row, so that has to be corrected here.
            acq_label = re.sub("__", "_", acq_label)
        else:
            logging.error(
                f"No method for reproin_{foldername} has been created."
                f"Check whether the naming scheme of the folders"
                f"is ReproIn-compliant and then, check upload_bids"
                f"for available methods corresponding to various modalities."
            )
    return acq_label


def determine_upload_status(overwrite, bc_context, field_to_check, fname):
    """To avoid overwriting existing versions, especially during testing, use this module to
    determine whether there are already files and if they should be overwritten.

    Args:
        overwrite (boolean): The files should be overwritten
        bc_context (object): FW metadata
        field_to_check (str): top-level key in the bc_context object to check
        fname (str): current filename being matched
    Return
        upload (boolean): decision to overwrite or not.
    """
    if not overwrite and bc_context[field_to_check].get("files", []):
        existing_files = [
            f["name"] for f in bc_context[field_to_check].get("files", [])
        ]
        if fname in existing_files:
            return False
        else:
            return True
    else:
        return True


def file_does_not_exist(filelist, filename):
    """Before overwriting, check for file."""
    if os.sep in filename:
        filename = os.path.basename(filename)
    try:
        return any([f for f in filelist if filename in f.name])
    except AttributeError:
        return any([f for f in filelist if filename in f["name"]])


def fill_in_properties(
    bc_context, path, use_template_defaults: bool, corrected_dir_name: str = None
):
    """Figure out BIDS metadata that should be populated for a file attached to a project, subject,
    session, acquisition, or a project-level directory that has been zipped for uploading.

    Returns: dictionary wth key "BIDS" with everything that can be filled in.
    """
    # Define the regex to use to find the property value from filename
    properties_regex = {
        "Acq": "_acq-[a-zA-Z0-9]+",
        "Ce": "_ce-[a-zA-Z0-9]+",
        "Rec": "_rec-[a-zA-Z0-9]+",
        "Run": "_run-[0-9]+",
        "Mod": "_mod-[a-zA-Z0-9]+",
        "Task": "_task-[a-zA-Z0-9]+",
        "Echo": "_echo-[0-9]+",
        "Dir": "_dir-[a-zA-Z0-9]+",
        "Recording": "_recording-[a-zA-Z0-9]+",
        "Modality": "_[a-zA-Z0-9]+%s" % bc_context["ext"],
    }
    path = os.path.normpath(path)
    path, correct_bids_dir = check_bids_dir_name(path)
    # Get meta info
    meta_info = bc_context["file"]["info"]
    # Iterate over all of the keys within the info namespace ('BIDS')
    for mi in meta_info["BIDS"]:
        if not use_template_defaults and meta_info["BIDS"][mi]:
            continue
        elif mi == "Filename":
            meta_info["BIDS"][mi] = bc_context["file"]["name"]
        elif mi == "Folder":
            if "sourcedata" in path:
                meta_info["BIDS"][mi] = "sourcedata"
            elif "derivatives" in path:
                meta_info["BIDS"][mi] = "derivatives"
            else:
                meta_info["BIDS"][mi] = correct_bids_dir
        elif mi == "Path":
            if corrected_dir_name:
                # for cases of blah/blah/anat-extra_stuff
                meta_info["BIDS"][mi] = os.path.join(
                    path.split(os.sep)[:-1], corrected_dir_name
                )
            else:
                meta_info["BIDS"][mi] = path
            # Search for regex string within BIDS filename and populate meta_info
        elif mi in properties_regex:
            tokens = re.compile(properties_regex[mi])
            token = tokens.search(bc_context["file"]["name"])
            if token:
                # Get the matched string
                result = token.group()
                # If meta_info is Modality, get the value before the extension...
                if mi == "Modality":
                    value = result[1 : -len(bc_context["ext"])]
                # Get the value after the '-'
                else:
                    value = result.split("-")[-1]
                # If value as an 'index' instead of a 'label', make it an integer (for search)
                if mi in ["Run", "Echo"]:
                    value = str(value)
                # Assign value to meta_info
                meta_info["BIDS"][mi] = value
    return meta_info


def handle_acquisition(fw, session_id, acquisition_label, subject_name):
    """Retrieve or create an acquisition from/on Flywheel.

    :param fw: Flywheel client
    :param str session_id: Flywheel identifier
    :param str acquisition_label: Specific acquisition to find
    :param str subject_name: BIDSified subject code (e.g., 01 for sub-01)

    :return dict session: dictionary detailing a Flywheel project based
                        on session_id and acquisition_label
    """
    # Get all sessions
    existing_acquisitions = fw.get_session_acquisitions(session_id)
    # Determine if acquisition_label within project project_id already exists
    found = False
    for ea in existing_acquisitions:
        if ea["label"] == acquisition_label:
            logger.info(
                "Acquisition %s was found. Adding data to existing acquisition."
                % acquisition_label
            )
            # Acquisition exists
            acquisition = ea
            found = True
            break
    # If acquisition does not exist, create new session
    if not found:
        logger.info(
            "Acquisition %s not found. Creating new acquisition for session %s."
            % (acquisition_label, session_id)
        )
        acquisition_id = fw.add_acquisition(
            {"label": acquisition_label, "session": session_id}
        )
        acquisition = fw.get_acquisition(acquisition_id)

    # In either case, check if there is BIDS information
    if not hasattr(acquisition["info"], "BIDS"):
        acquisition.update(
            {
                "info": {
                    "BIDS": {
                        "Subject": subject_name[4:],
                        "Label": acquisition_label,
                        "ignore": False,
                    }
                }
            }
        )

    return acquisition.to_dict()


def handle_project(
    fw,
    group_id,
    project_label,
    template,
    template_is_old: bool = False,
    save_sidecar_as_metadata: bool = False,
    assume_upload: bool = False,
):
    """Retrieve or create a project from/on Flywheel.

    :param fw: Flywheel client
    :param str group_id: Flywheel identifier
    :param str project_label: Flywheel identifier for the name of the project
    :param Template template: BIDS Project template
    :param bool template_is_old: BIDS Project curation template wants to put dataset_description data in project.info.BIDS
    :param bool save_sidecar_as_metadata: Save dataset_description.json data in project.info.BIDS
    :param bool assume_upload: Should the container be uploaded?
    :return dict project: dictionary detailing a Flywheel project based
                        on group_id and project_label
    """
    # Get all projects
    # Using the mandatory group and project id's decreases the find time
    # and the number of projects to match in the ep loop
    existing_projs = fw.projects.find(f"group={group_id}")

    # Determine if project_label with group_id already exists
    project = [
        ep
        for ep in existing_projs
        if (ep["label"] == project_label) and (ep["group"] == group_id)
    ][0]  # Should be unique
    if project:
        if check_enabled_rules(fw, project.to_dict()["id"]):
            logger.warning(
                "Project has enabled rules, these may overwrite BIDS data. Either disable rules or run bids curation gear after data is uploaded."
            )
            if not assume_upload and not utils.confirmation_prompt("Continue upload?"):
                return

    # Add ingested files to an existing project. These files should be ingested the same way as the project has already been created and/or curated.
    # NOTE: Edge case is that the project is created in the UI, but not populated.
    # Use the check for BIDS in info to work around the edge case.
    if project and "BIDS" in project.info:
        if "Acknowledgements" in project.info["BIDS"]:
            # then project is storing sidecar in metadata on the project and all NIfTI files should
            # have sidecar data in file.info, and project.info.BIDS should not be modified.
            if not save_sidecar_as_metadata:
                save_sidecar_as_metadata = True
                logger.warning(
                    "The argument save_sidecar_as_metadata was passed in as False, "
                    "but dataset_description.json information was detected in project.info.BIDS "
                    "so save_sidecar_as_metadata has been changed to True because this "
                    "project already is saving sidecar data in metadata.  All NIfTI files "
                    "should have sidecar data in file.info and any real json sidecars will be "
                    "ignored."
                )

            # Don't replace project.info.BIDS with what is in the template
            if "properties" in template.definitions["project"]:
                del template.definitions["project"]["properties"]

        # Otherwise, dataset_description.json should be a file attached to the project, its data is not
        # stored in project.info.BIDS, and all NIfTI files should have real json sidecars.
        elif save_sidecar_as_metadata:
            raise ValueError(
                "The argument save_sidecar_as_metadata has been passed in as True "
                "but there is no dataset_description data in project.info.BIDS.  "
                "Either save_sidecar_as_metadata should be False (the default), or "
                "the project should be curated for BIDS with save_sidecar_as_metadata set "
                "to True."
            )
        elif template_is_old:
            raise ValueError(
                "The BIDS Project Curation template is old and expects to "
                "put dataset_description.json data in project.info.BIDS but "
                "this existing project has not yet been curated with sidecar data in "
                "project.info.BIDS and with sidecar data in file.info for NIfTI files.  "
                "Either the project should be curated with save_sidecar_as_metadata True "
                "or a new template should be used"
            )
    else:
        # New projects, either created in the UI or needing to be created automatically here.
        # As with older projects, save_sidecar_as_metadata and the provided template determine if sidecar data should be in metadata or in real sidecars.
        # Behavior should be consistent with "old" and "new" definitions of storing sidecars.
        if (
            save_sidecar_as_metadata and not template_is_old
        ):  # make the new template save sidecar data in metadata
            template.definitions["project"] = template.definitions[
                "dataset_description_file"
            ]

        if not save_sidecar_as_metadata and template_is_old:
            raise ValueError(
                "An old template is being used which will put data_description.json data into "
                "project.info.BIDS and NIfTI sidecar data in file.info, but save_sidecar_as_metadata"
                "is False (the default). Either a new template should be used or save_sidecar_as_metadata"
                "should be passed in as True."
            )
        if not project:
            logger.info(
                "Project %s not found. Creating new project for group %s."
                % (project_label, group_id)
            )

            project_id = fw.add_project(
                {"label": project_label, "group": group_id}, inherit=True
            )
            project = fw.get_project(project_id)
        disable_project_rules(fw, project.to_dict()["id"])

    return project.to_dict(), save_sidecar_as_metadata


def handle_session(fw, project_id, session_name, subject_name):
    """Retrieve or create a session from/on Flywheel.

    :param fw: Flywheel client
    :param str project_id: Flywheel identifier
    :param str session_name: Specific session to find
    :param str subject_name: BIDSified subject code (e.g., 01 for sub-01)

    :return dict session: dictionary detailing a Flywheel project based
                        on project_id and session_label

    """
    # Get all sessions
    existing_sessions = fw.get_project_sessions(project_id)
    # Determine if session_name within project project_id already exists, with same subject_name...
    found = False
    for es in existing_sessions:
        if (es["label"] == session_name) and (es["subject"]["code"] == subject_name):
            logger.info(
                "Session %s for subject %s was found. Adding data to existing session."
                % (session_name, subject_name)
            )
            # Session exists
            session = es
            found = True
            break
    # If session does not exist, create new session
    if not found:
        logger.info(
            "Session %s not found. Creating new session for project %s."
            % (session_name, project_id)
        )

        session_id = fw.add_session(
            {
                "label": session_name,
                "project": project_id,
                "subject": {"code": subject_name},
                "info": {
                    "BIDS": {
                        "Subject": subject_name[4:],
                        "Label": session_name[4:],
                        "ignore": False,
                    }
                },
            }
        )
        session = fw.get_session(session_id)

    return session.to_dict()


def handle_subject(fw, project_id, subject_code):
    """Returns a Flywheel subject based on project_id and subject_code."""
    # Get all subjects
    existing_subjects = fw.get_project_subjects(project_id)
    # Determine if subject_name within project project_id already exists, with same subject_name...
    found = False
    for es in existing_subjects:
        if es["code"] == subject_code:
            logger.info(
                "Subject %s was found. Adding data to existing subject." % subject_code
            )
            # Session exists
            subject = es
            found = True
            break
    # If subject does not exist, create new subject
    if not found:
        logger.info(
            "Subject %s not found. Creating new subject for %s."
            % (subject_code, project_id)
        )

        subject_id = fw.add_subject(
            {"code": subject_code, "label": subject_code, "project": project_id}
        )
        subject = fw.get_subject(subject_id)

    return subject.to_dict()


def handle_subject_folder(
    fw,
    bc_context,
    files_for_special_handling,
    subject,
    rootdir,
    sub_rootdir,
    hierarchy_type,
    subject_code,
    template: Template,
    use_template_defaults: bool,
    overwrite=False,
):
    #   In BIDS, the session is optional, if not present - use subject_code as session_label
    # Get all keys that are session - 'ses-<session.label>'
    if sub_rootdir:
        rootdir = os.path.join(rootdir, sub_rootdir)
    sessions = [key for key in subject if "ses" in key]
    # If no sessions, add session layer, just subject_label will be the subject_code
    if not sessions:
        sessions = ["ses-"]
        subject = {"ses-": subject}

    bc_context["subject"] = handle_subject(
        fw, bc_context["project"]["id"], subject_code
    )

    ## Iterate over subject files
    # NOTE: Attaching files to project instead of subject....
    subject_files = subject.get("files")
    if subject_files:
        for fname in subject.get("files"):
            # Exclude filenames that begin with .
            if fname.startswith("."):
                continue
            ### Upload file
            # define full filename
            full_fname = os.path.join(rootdir, subject_code, fname)

            if ".json" in fname or fname == (f"{subject_code}_sessions.tsv"):
                files_for_special_handling[fname] = {
                    "id": bc_context["subject"]["id"],
                    "id_type": "subject",
                    "full_filename": full_fname,
                }
                continue

            # Upload subject file
            bc_context["file"] = upload_subject_file(fw, bc_context, full_fname, fname)
            # Update the bc_context for this file
            bc_context["container_type"] = "file"
            bc_context["parent_container_type"] = (
                "project"  # TODO: should this be "subject"?
            )
            bc_context["ext"] = utils.get_extension(fname)
            # Identify the templates for the file and return file object
            # For BIDS upload, the template matches with the general bids_acquisition rule.
            bc_context["file"] = bidsify_flywheel.process_matching_templates(
                bc_context, template, upload=True
            )
            # Update the meta info files w/ BIDS info from the filename...
            full_path = os.path.join(sub_rootdir, subject_code)
            meta_info = fill_in_properties(bc_context, full_path, use_template_defaults)
            # Upload the meta info onto the subject file
            fw.set_subject_file_info(bc_context["subject"]["id"], fname, meta_info)

    ### Iterate over sessions
    for session_label in sessions:
        # Create Session
        bc_context["session"] = handle_session(
            fw, bc_context["project"]["id"], session_label, subject_code
        )
        # Hand off subject info to bc_context
        bc_context["subject"] = bc_context["session"]["subject"]

        ## Iterate over session files - upload file and add meta data
        for fname in subject[session_label].get("files"):
            # Exclude filenames that begin with .
            if fname.startswith("."):
                continue
            ### Upload file
            # define full filename
            #   NOTE: If session_label equals 'ses-', session label is not
            #       actually present within the original directory structure
            if session_label == "ses-":
                full_fname = os.path.join(rootdir, subject_code, fname)
                full_path = os.path.join(sub_rootdir, subject_code)
            else:
                full_fname = os.path.join(rootdir, subject_code, session_label, fname)
                full_path = os.path.join(sub_rootdir, subject_code, session_label)

            # Don't upload sidecars
            if ".json" in fname:
                files_for_special_handling[fname] = {
                    "id": bc_context["session"]["id"],
                    "id_type": "session",
                    "full_filename": full_fname,
                }
                continue
            # Upload session file
            bc_context["file"] = upload_session_file(fw, bc_context, full_fname, fname)
            # Update the bc_context for this file
            bc_context["container_type"] = "file"
            bc_context["parent_container_type"] = "session"
            bc_context["ext"] = utils.get_extension(fname)
            # Identify the templates for the file and return file object
            bc_context["file"] = bidsify_flywheel.process_matching_templates(
                bc_context, template, upload=True
            )
            # Update the meta info files w/ BIDS info from the filename...
            meta_info = fill_in_properties(bc_context, full_path, use_template_defaults)
            # Upload the meta info onto the project file
            fw.set_session_file_info(bc_context["session"]["id"], fname, meta_info)

            # Check if any session files are of interest (to be parsed later)
            #   interested in _scans.tsv and JSON files
            val = f"{subject_code}_{session_label}_scans.tsv"
            if fname == val:
                files_for_special_handling[fname] = {
                    "id": bc_context["session"]["id"],
                    "id_type": "session",
                    "full_filename": full_fname,
                }

        ## Iterate over 'folders' which are ['anat', 'func', 'fmap', 'dwi'...]
        #          NOTE: could there be any other dirs that would be handled differently?
        # get folders
        folders = [item for item in subject[session_label] if item != "files"]
        for foldername in folders:
            # Check as early as possible whether the modality is supported.
            if not check_modality_supported(foldername):
                # Just in case the BIDS mod is in the filename of the acq, not the folder name
                deeper_modality_check = subject[session_label][foldername].get("files")[
                    0
                ]
                if not check_modality_supported(deeper_modality_check):
                    break

            # Iterate over acquisition files -- upload file and add meta data
            for fname in subject[session_label][foldername].get("files"):
                # Exclude filenames that begin with .
                if fname.startswith("."):
                    continue
                # Determine acquisition label -- it can either be the folder name OR the basename of the file...
                acq_label = determine_acquisition_label(
                    foldername, fname, hierarchy_type
                )
                # Create acquisition
                bc_context["acquisition"] = handle_acquisition(
                    fw, bc_context["session"]["id"], acq_label, subject_code
                )
                ### Upload file
                # define full filename
                #   NOTE: If session_label equals 'ses-', session label is not
                #       actually present within the original directory structure
                if session_label == "ses-":
                    full_fname = os.path.join(rootdir, subject_code, foldername, fname)
                    full_path = os.path.join(sub_rootdir, subject_code, foldername)
                else:
                    full_fname = os.path.join(
                        rootdir, subject_code, session_label, foldername, fname
                    )
                    full_path = os.path.join(
                        sub_rootdir, subject_code, session_label, foldername
                    )

                # Check if any acquisition files are of interest (to be parsed later)
                #   interested in JSON files
                if ".json" in fname:
                    files_for_special_handling[fname] = {
                        "id": bc_context["acquisition"]["id"],
                        "id_type": "acquisition",
                        "full_filename": full_fname,
                    }

                # If overwriting existing files
                upload = determine_upload_status(
                    overwrite, bc_context, "acquisition", fname
                )

                if upload:
                    # Place filename in bc_context
                    bc_context["file"] = {"name": fname}

                    # Upload acquisition file
                    bc_context["file"] = upload_acquisition_file(
                        fw, bc_context, full_fname, fname
                    )
                    # Update the bc_context for this file
                    bc_context["container_type"] = "file"
                    bc_context["parent_container_type"] = "acquisition"
                    bc_context["ext"] = utils.get_extension(fname)
                    # Identify the templates for the file and return file object
                    bc_context["file"] = bidsify_flywheel.process_matching_templates(
                        bc_context, template, upload=True
                    )
                    # Check that the file matched a template
                    if bc_context["file"].get("info") and ".json" not in fname:
                        # Update the meta info files w/ BIDS info from the filename and foldername...
                        meta_info = fill_in_properties(
                            bc_context, full_path, use_template_defaults
                        )
                        # Upload the meta info onto the project file
                        fw.set_acquisition_file_info(
                            bc_context["acquisition"]["id"], fname, meta_info
                        )


def parse_json(filename):
    """ """
    with open(filename) as json_data:
        contents = json.load(json_data)
    return contents


def parse_tsv(filename):
    """"""
    contents = []
    with open(filename) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            contents.append(row)

    # If all values in the column are floats/ints, then convert
    # If only 'F' and 'M' in a column, convert to 'Female'/'Male'
    contents = convert_dtype(contents)

    return contents


def reproin_anat(parts):
    """Rearrange the anat names to have the final,
    BIDS label become the second portion of the anat- prefix.
    """
    parts.insert(0, "anat-" + parts.pop())
    return parts


def reproin_dwi(parts):
    """Reorder the pieces of the acquisition label for DWI acquisitions."""
    if parts[-1].lower() != "sbref":
        # Drop "_dwi"
        parts = parts[:-1]
    parts.insert(0, "dwi")
    return parts


def reproin_fmap(parts):
    """Reorder the pieces of the acquisition label for
    fmap-classified acquisitions.
    """
    if [p for p in parts if "acq-greSiemens" in p.lower()]:
        # The filenames will differ, but the acquisition
        # labels should all be the same
        parts = ["fmap-gre", "acq-siemens"]
    else:
        # For epi with opposite phases or other phase/mag
        parts.insert(0, "fmap-" + parts.pop())
    return parts


def reproin_func(parts):
    """This is the fun modality, where nothing is guaranteed...
    well, at least that is how it seems.
    """
    if parts[-1].lower() not in ("physio", "sbref"):
        # Drop "_bold', '_events'
        parts = parts[:-1]
    if parts[-1].lower() == "physio":
        parts[-1] = "PhysioLog"
    parts.insert(0, "func-bold")
    return parts


def reproin_perf(parts):
    """Rearrange the ASL perfusion names to have the final, BIDS label
    become the second portion of the perf- prefix
    This method may be subject to change as REPROIN catches up with BIDS.
    For now, we'll assume that REPROIN uses perf, and not func, for the
    file names.
    """
    if parts[-1].lower() == "asl":
        parts = parts[:-1]
    if parts[-1].lower() == "physio":
        parts[-1] = "PhysioLog"
    parts.insert(0, "perf-asl")
    return parts


def upload_acquisition_file(fw, bc_context, full_fname, fname):
    """"""
    # Upload file
    fw.upload_file_to_acquisition(bc_context["acquisition"]["id"], full_fname)

    ### Classify acquisition
    # Get classification based on filename
    classification = classify_acquisition(full_fname)

    # Assign classification
    if classification:
        update = {"modality": "MR", "replace": classification}
        fw.modify_acquisition_file_classification(
            bc_context["acquisition"]["id"], bc_context["file"]["name"], update
        )

    # Return file
    return fw.get_acquisition_file_info(
        bc_context["acquisition"]["id"], fname
    ).to_dict()


def upload_project_file(fw, bc_context, full_fname, fname):
    """"""
    # Upload file
    fw.upload_file_to_project(bc_context["project"]["id"], full_fname)
    # Return file
    return fw.get_project_file_info(bc_context["project"]["id"], fname).to_dict()


def upload_session_file(fw, bc_context, full_fname, fname):
    """"""
    # Upload file
    fw.upload_file_to_session(bc_context["session"]["id"], full_fname)
    # Return file
    return fw.get_session_file_info(bc_context["session"]["id"], fname).to_dict()


def upload_subject_file(fw, bc_context, full_fname, fname):
    """"""
    # Upload file
    fw.upload_file_to_subject(bc_context["subject"]["id"], full_fname)
    # Return file
    return fw.get_subject_file_info(bc_context["subject"]["id"], fname).to_dict()


####### "Super" methods for upload_bids in order called ########
def validate_dirname(dirname):
    """Check the following criteria to ensure 'dirname' is valid
        - dirname exists
        - dirname is a directory
    If criteria not met, raise an error.
    """
    logger.info("Verifying directory exists")

    # Check dirname exists
    if not os.path.exists(dirname):
        logger.error("Path (%s) does not exist" % dirname)
        sys.exit(1)

    # Check dirname is a directory
    if not os.path.isdir(dirname):
        logger.error("Path (%s) is not a directory" % dirname)
        sys.exit(1)


def parse_bids_dir(bids_dir):
    """Creates a nested dictionary that represents the folder structure of bids_dir.

    if '/tmp/ds001' is bids dir passed, 'ds001' is first key and is the project name...
    e.g.,
    tmp
    |---ds001
    |---|--dataset_description.json
    |---|--anat
    |---|--|-example_t1.nii.gz
    |---|--func
    |---|--|-example_epi.nii.gz
    |---|--|-example_epi.json
    becomes {'ds001':{'files':['dataset_description.json'],
                   'anat':{'files':['example_t1.nii.gz']},
                   'func':{'files':['example_epi_nii.gz','example_epi.json']}
                   }
            }
    """
    ## Read in BIDS hierarchy
    bids_hierarchy = {}
    bids_dir = bids_dir.rstrip(os.sep)
    start = bids_dir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(bids_dir):
        folders = path[start:].split(os.sep)
        subdir = {"files": files}
        parent = reduce(dict.get, folders[:-1], bids_hierarchy)
        parent[folders[-1]] = subdir
    return bids_hierarchy


def parse_hierarchy(
    bids_hierarchy: dict,
    project_label_cli: str,
    rootdir: os.PathLike,
    include_source_data: bool = False,
    subject_label: str = None,
    session_label: str = None,
):
    """Use nested dictionary and CLI args to determine the values
    for the group_id and project_label information.

    Below is the expected hierarchy for the 'bids_hierarchy':

            project_label: {
                    sub-AAA: {},
                    sub-BBB: {},
                    ...
                }

    :param str project_label_cli: optionally defined by user from the CLI (-p)
    :param PathLike rootdir: BIDS dir captured from the CLI (--bids-dir)
    :param bool include_source_data: Include the source data in upload (--source-data)
    :param str subject_label: optional restriction to specific subject
    :param str session_label: option restriction to specific session

    :return:
        bids_hierarchy as expected structure with the project label as a top-level key for the hierarchy
        rootdir (PathLike): os.path.dirname of the input BIDS directory

    :raise Error: if project_label is not defined within bids_hierarchy
         structure AND not passed through the command line

    """
    # Initialize sub
    top_level = False
    second_level = False
    # Define sub directory pattern
    subdir_pattern = re.compile("sub-[a-zA-Z0-9]+")

    # Iterate over top level keys in bids hierarchy
    for k in bids_hierarchy:
        # If sub-YY pattern found at topmost level, project label is not defined
        if subdir_pattern.search(k):
            # subdirs found
            top_level = True
            break
        # Iterate over second level keys in bids hierarchy
        for kk in bids_hierarchy[k]:
            # If sub-YY pattern found, then project_label is defined as k (top level directory name)
            if subdir_pattern.search(kk):
                # subdirs found
                second_level = True

    # If sub-YY directories found at top level,
    #   project_label_cli must be defined
    if top_level:
        if project_label_cli:
            bids_hierarchy = {project_label_cli: bids_hierarchy}
            bids_hierarchy[project_label_cli]["files"] = []
            rootdir = os.path.dirname(rootdir)
        # If not defined, raise an error! project label is not defined
        else:
            logger.error("Project label cannot be determined")
            sys.exit(1)

    # If sub-YY directories found at second level
    #   project_label_cli does not NEED to be defined (no error raised)
    if second_level:
        if project_label_cli:
            bids_hierarchy[project_label_cli] = bids_hierarchy.pop(k)
        else:
            project_label_cli = k

    # If sub-YY directories are not found
    if not (top_level or second_level):
        logger.error("Did not find subject directories within hierarchy")
        sys.exit(1)

    if not include_source_data:
        bids_hierarchy[project_label_cli].pop("sourcedata", None)

    if subject_label and subject_label in bids_hierarchy[project_label_cli]:
        if (
            session_label
            and session_label in bids_hierarchy[project_label_cli][subject_label]
        ):
            bids_hierarchy = {
                project_label_cli: {
                    "files": [],
                    subject_label: {
                        "files": [],
                        session_label: bids_hierarchy[project_label_cli][subject_label][
                            session_label
                        ],
                    },
                }
            }
        elif session_label:
            logger.error("Could not find Session %s in BIDS hierarchy!" % session_label)
            sys.exit(2)
        else:
            bids_hierarchy = {
                project_label_cli: {
                    "files": [],
                    subject_label: bids_hierarchy[project_label_cli][subject_label],
                }
            }
    elif subject_label:
        logger.error("Could not find Subject %s in BIDS hierarchy!" % subject_label)
        sys.exit(2)

    return bids_hierarchy, rootdir


def upload_bids_dir(
    fw,
    bids_hierarchy: dict,
    group_id: str,
    rootdir: os.PathLike,
    hierarchy_type: str,
    template: Template,
    use_template_defaults: bool,
    assume_upload: bool,
    overwrite: bool,
    save_sidecar_as_metadata: bool = False,
):
    """:param fw: Flywheel client
    :param dict bids_hierarchy: BIDS hierarchy represented as a nested dict
    :param str rootdir: path to files
    :param hierarchy_type: either 'Flywheel' or 'BIDS'
            if 'Flywheel', the base filename is used as the acquisition label
            if 'BIDS', the BIDS foldername (anat,func,dwi etc...) is used as the acquisition label
    :param bool use_template_defaults:
            prioritize template default values for BIDS information
    :param bool assume_upload: from CLI (--yes). Assume yes to prompts, which
            effectively is yes to uploading files
    :param bool overwrite: overwrite existing files
    :param bool save_sidecar_as_metadata: save sidecar as metadata
    :return list files_for_special_handling: filtered list of files that need to be uploaded,
            but require special handling
    """
    # Iterate
    # Initialize BIDS-client context (bc_context) object.  This is a dictionary that contains the
    #    complete information about where in the Flywheel hierarchy a file is.  It changes as the
    #    hierarchy is traversed.
    bc_context = {
        "container_type": None,
        "parent_container_type": None,
        "project": None,
        "subject": None,
        "session": None,
        "acquisition": None,
        "file": None,
        "ext": None,
    }

    # Collect files to be parsed at the end
    files_for_special_handling = {}

    if (
        "project" in template.definitions
        and "Acknowledgements" in template.definitions["project"]
    ):
        # dataset_description.json data is in project.info.BIDS, sidecar data should be in
        # file.info.BIDS for all NIfTI files, and json sidecar files should be ignored
        template_is_old = True
    else:
        # dataset_description.json is a file attached to the project, json sidecars
        # should exist for all NIfTI files, no sidecar data should be in file.info,
        # and DICOM headers are in file.info.header.dicom on NIfTI files (the new way)
        template_is_old = False

    # Iterate over BIDS hierarchy (first key will be top level dirname
    # which we will use as the project label)
    for proj_label in bids_hierarchy:
        ## Validate the project
        #   (1) create a project OR
        #   (2) find an existing project by the project_label
        #   -- return project object
        bc_context["container_type"] = "project"
        bc_context["project"], save_sidecar_as_metadata = handle_project(
            fw,
            group_id,
            proj_label,
            template,
            template_is_old,
            save_sidecar_as_metadata,
            assume_upload,
        )
        if bc_context["project"] is None:
            continue

        # NOTE: template is the default.json file
        # and bc_context["project"] at this point is the entire Flywheel project container object
        bc_context["project"] = bidsify_flywheel.process_matching_templates(
            bc_context, template, upload=True
        )
        fw.modify_project(
            bc_context["project"]["id"],
            {"info": {"BIDS": bc_context["project"]["info"]["BIDS"]}},
        )

        ### Iterate over project files - upload file and add metadata
        # Specifically looking for dataset_description.json etc.
        for fname in bids_hierarchy[proj_label].get("files"):
            # Exclude filenames that begin with .
            if fname.startswith("."):
                continue
            ### Upload file
            # define full filename
            full_fname = os.path.join(rootdir, fname)
            # Don't upload json sidecars
            if ".json" in fname:
                files_for_special_handling[fname] = {
                    "id": bc_context["project"]["id"],
                    "id_type": "project",
                    "full_filename": full_fname,
                }

            # These files are in the BIDS specification:
            #        README {.md | .rst | .txt | <no extension>},
            #        CHANGES
            #        LICENSE
            #        participants.tsv
            #        participants.json
            #        samples.tsv
            #        samples.json

            try:
                upload = determine_upload_status(
                    overwrite, bc_context, "project", fname
                )

                if upload:
                    # Upload project file
                    bc_context["file"] = upload_project_file(
                        fw, bc_context, full_fname, fname
                    )
                    # Update the bc_context for this file
                    bc_context["container_type"] = "file"
                    bc_context["parent_container_type"] = "project"
                    bc_context["ext"] = utils.get_extension(fname)

                    if ".json" not in fname:
                        # Identify the templates for the file and return file object
                        # NOTE: template is the default.json file
                        bc_context["file"] = (
                            bidsify_flywheel.process_matching_templates(
                                bc_context, template, upload=True
                            )
                        )
                        # Update the meta info files w/ BIDS info from the filename...
                        full_path = ""
                        meta_info = fill_in_properties(
                            bc_context, full_path, use_template_defaults
                        )
                        # Upload the meta info onto the project file
                        fw.set_project_file_info(
                            bc_context["project"]["id"], fname, meta_info
                        )

                        # Check if project files are of interest (to be parsed later)
                        #    Interested in participants.tsv or any JSON file
                        if fname == "participants.tsv":
                            files_for_special_handling[fname] = {
                                "id": bc_context["project"]["id"],
                                "id_type": "project",
                                "full_filename": full_fname,
                            }
            except UnboundLocalError:
                logger.error("dataset_description.json file not present")

        ### Figure out which directories are subjects, and which are directories
        #       that should be zipped up and add to project
        # Get subjects
        subjects = [key for key in bids_hierarchy[proj_label] if "sub" in key]
        # Get source directory
        sourcedata_folder = [
            key
            for key in bids_hierarchy[proj_label].get("sourcedata", {})
            if "sub" in key
        ]
        # Get non-subject directories remaining
        dirs = [
            item
            for item in bids_hierarchy[proj_label]
            if item not in subjects + ["files", "sourcedata"]
        ]

        ### Iterate over project directories (that aren't 'sub' dirs) - zip up directory contents and add meta data
        for dirr in dirs:
            ### Zip and Upload file
            # define full dirname and zipname
            full_dname = os.path.join(rootdir, dirr)
            full_zname = os.path.join(rootdir, dirr + ".zip")
            shutil.make_archive(full_dname, "zip", full_dname)
            # Upload project file
            bc_context["file"] = upload_project_file(
                fw, bc_context, full_zname, dirr + ".zip"
            )
            # remove the generated zipfile
            os.remove(full_zname)
            # Update the bc_context for this file
            bc_context["container_type"] = "file"
            bc_context["parent_container_type"] = "project"
            bc_context["ext"] = utils.get_extension(full_zname)
            # Identify the templates for the file and return file object
            # NOTE: template is the default.json file
            bc_context["file"] = bidsify_flywheel.process_matching_templates(
                bc_context, template, upload=True
            )
            # Update the meta info files w/ BIDS info from the filename...
            full_path = ""
            meta_info = fill_in_properties(bc_context, full_path, use_template_defaults)
            # Upload the meta info onto the project file
            fw.set_project_file_info(
                bc_context["project"]["id"], dirr + ".zip", meta_info
            )

        ### Iterate over subjects
        for subject_code in subjects:
            subject = bids_hierarchy[proj_label][subject_code]
            handle_subject_folder(
                fw,
                bc_context,
                files_for_special_handling,
                subject,
                rootdir,
                "",
                hierarchy_type,
                subject_code,
                template,
                use_template_defaults,
                overwrite,
            )

        # upload sourcedata (If option not set, the folder was popped in parse_hierarchy)
        for subject_code in sourcedata_folder:
            subject = bids_hierarchy[proj_label]["sourcedata"][subject_code]
            handle_subject_folder(
                fw,
                bc_context,
                files_for_special_handling,
                subject,
                rootdir,
                "sourcedata",
                hierarchy_type,
                subject_code,
                template,
                use_template_defaults,
                overwrite,
            )

    return files_for_special_handling


def parse_meta_files(
    fw, files_for_special_handling, save_sidecar_as_metadata=False, overwrite=False
):
    """i.e.

    files_for_special_handling = {
        'dataset_description.json': {
            'id': u'5a1364af9b89b7001d1f357f',
            'id_type': 'project',
            'full_filename': '/7t_trt_reduced/dataset_description.json'
            },
        'participants.tsv': {
            'id': u'5a1364af9b89b7001d1f357f',
            'id_type': 'project',
            'full_filename': '/7t_trt_reduced/participants.tsv'
            }
    }

    Interested in these files within the project:
        data_description.json
        participants.tsv
        sub-YYY_sessions.tsv
        sub-YYY_ses-YYY_scans.tsv

    """
    logger.info("Parsing meta files")

    # Handle files
    for f in files_for_special_handling:
        if ".tsv" in f:
            # Attach TSV file contents
            attach_tsv(fw, files_for_special_handling[f], overwrite=overwrite)
        elif ".json" in f:
            # Attach JSON file contents
            attach_json(
                fw,
                files_for_special_handling[f],
                save_sidecar_as_metadata=save_sidecar_as_metadata,
                overwrite=overwrite,
            )
        # Otherwise don't recognize filetype
        else:
            logger.info("Do not recognize filetype")


# The CLI calls this
def upload_bids(
    fw,
    bids_dir,
    group_id,
    project_label=None,
    hierarchy_type="Flywheel",
    validate=True,
    include_source_data=False,
    use_template_defaults=True,
    assume_upload=False,
    subject_label=None,
    session_label=None,
    overwrite=False,
    save_sidecar_as_metadata=False,
    template_path=None,
    template_name=None,
):
    ### Prep
    # Check directory name - ensure it exists
    validate_dirname(bids_dir)

    ### Read in hierarchy & Validate as BIDS
    # parse BIDS dir; returns dictionary of the hierarchy with
    #   {"files":[],"sub_dir":{"files:[], "sub_dir":{blah, blah}} all
    #   the way to the acquisition level
    # TODO: if there are a whole lot of files/folders in the BIDS dir, this will explode so
    #     each subject should be handled individually
    bids_hierarchy = parse_bids_dir(bids_dir)
    # TODO: Determine if project label are present
    bids_hierarchy, rootdir = parse_hierarchy(
        bids_hierarchy,
        project_label,
        bids_dir,
        include_source_data,
        subject_label,
        session_label,
    )

    # Determine if hierarchy is valid BIDS
    if validate:
        utils.validate_bids(rootdir)

    template = load_template(template_path, template_name, save_sidecar_as_metadata)

    ### Upload BIDS directory
    # upload bids dir (and get files of interest and project id)
    files_for_special_handling = upload_bids_dir(
        fw,
        bids_hierarchy,
        group_id,
        rootdir,
        hierarchy_type,
        template,
        use_template_defaults,
        assume_upload,
        overwrite,
        save_sidecar_as_metadata,
    )

    # Parse the BIDS meta files
    #    data_description.json, participants.tsv, *_sessions.tsv, *_scans.tsv
    parse_meta_files(
        fw,
        files_for_special_handling,
        save_sidecar_as_metadata=save_sidecar_as_metadata,
        overwrite=overwrite,
    )


def main():
    ### Read in arguments
    parser = argparse.ArgumentParser(description="BIDS Directory Upload")
    parser.add_argument(
        "--bids-dir",
        dest="bids_dir",
        action="store",
        required=True,
        help="BIDS directory",
    )
    parser.add_argument(
        "--api-key", dest="api_key", action="store", required=True, help="API key"
    )
    parser.add_argument(
        "-g",
        dest="group_id",
        action="store",
        required=True,
        help="Group ID on Flywheel instance",
    )
    parser.add_argument(
        "-p",
        dest="project_label",
        action="store",
        required=False,
        default=None,
        help="Project Label on Flywheel instance",
    )
    parser.add_argument(
        "--subject",
        default=None,
        help="Only upload data from single subject folder (i.e. sub-01)",
    )
    parser.add_argument(
        "--session",
        default=None,
        help="Only upload data from single session folder (i.e. ses-01)",
    )
    parser.add_argument(
        "--type",
        dest="hierarchy_type",
        action="store",
        required=False,
        default="Flywheel",
        choices=["BIDS", "Flywheel"],
        help="Hierarchy to load into, either 'BIDS' or 'Flywheel'",
    )
    parser.add_argument(
        "--source-data",
        dest="source_data",
        action="store_true",
        default=False,
        required=False,
        help="Include source data in BIDS upload",
    )
    parser.add_argument(
        "--use-template-defaults",
        action="store_false",
        default=True,
        required=False,
        help="Prioritize template default values for BIDS information",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Assume the answer is yes to all prompts",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        default=False,
        required=False,
        help="Existing files should be replaced. (default = false)",
    )
    parser.add_argument(
        "--save_sidecar_as_metadata",
        action="store_true",
        required=False,
        help="Upload the BIDS sidecar as metadata in file.info. (default no longer stores metadata, only the JSON sidecar)",
    )
    parser.add_argument(
        "--template-path",
        dest="template_path",
        action="store",
        required=False,
        default=None,
        help="Full path to project curation template (.json file)",
    )
    parser.add_argument(
        "--template-name",
        dest="template_name",
        action="store",
        required=False,
        default="default",
        choices=["default", "bids-v1", "reproin"],
        help="Project curation template, either 'default', 'bids-v1' or 'reproin'",
    )
    args = parser.parse_args()

    if args.session and not args.subject:
        logger.error("Cannot only provide session without subject")
        sys.exit(1)

    # Check API key - raises Error if key is invalid
    fw = flywheel.Client(args.api_key)

    upload_bids(
        fw,
        args.bids_dir,
        args.group_id,
        project_label=args.project_label,
        hierarchy_type=args.hierarchy_type,
        include_source_data=args.source_data,
        use_template_defaults=args.use_template_defaults,
        assume_upload=args.yes,
        subject_label=args.subject,
        session_label=args.session,
        overwrite=args.overwrite,
        save_sidecar_as_metadata=args.save_sidecar_as_metadata,
        template_path=args.template_path,
        template_name=args.template_name,
    )


if __name__ == "__main__":
    main()
