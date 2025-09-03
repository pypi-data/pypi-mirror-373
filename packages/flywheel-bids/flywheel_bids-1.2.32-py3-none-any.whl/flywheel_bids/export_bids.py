import argparse
import copy
import json
import logging
import os
import re
import sys
import zipfile
from pathlib import Path

import dateutil.parser
import flywheel

from .supporting_files import errors, utils
from .supporting_files.errors import BIDSExportError
from .utils.curation_tools import find_how_curated
from .utils.fmaps import remove_orphaned_fmaps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EPOCH = dateutil.parser.parse("1970-01-01 00:00:0Z")


def validate_dirname(dirname):
    """Check the following criteria to ensure 'dirname' is valid
        - dirname exists
        - dirname is a directory
    If criteria not met, raise an error.
    """
    logger.info("Verify download directory exists")

    # Check dirname is a directory
    if not os.path.isdir(dirname):
        logger.error("Path (%s) is not a directory" % dirname)
        raise BIDSExportError("Path (%s) is not a directory" % dirname)

    # Check dirname exists
    if not os.path.exists(dirname):
        logger.info("Path (%s) does not exist. Making directory..." % dirname)
        os.mkdir(dirname)


def parse_bool(v):
    """Mainly to pass along only files without the "ignore" tag under BIDS curation."""
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v != 0

    return str(v).lower() == "true"


def get_metadata(ctx, namespace):
    """Retrieve and return BIDS information."""
    # Check if 'info' in f object
    if "info" not in ctx:
        return None
    # Check if namespace ('BIDS') in f object
    if namespace not in ctx["info"]:
        return None
    # Check if 'info.BIDS' == 'NA'
    if ctx["info"][namespace] == "NA":
        return None

    return ctx["info"][namespace]


def is_file_excluded_options(namespace, src_data, replace):
    def is_file_excluded(f, fpath):
        metadata = get_metadata(f, namespace)
        if not metadata:
            return True

        # ignored for BIDS
        if parse_bool(metadata.get("ignore", False)):
            return True

        if not src_data:
            path = metadata.get("Path")
            if path and path.startswith("sourcedata"):
                return True

        # Check if file already exists
        if os.path.isfile(fpath):
            if not replace:
                return True
            # Check if the file already exists and whether it is up to date
            time_since_epoch = timestamp_to_int(f.get("modified"))
            if time_since_epoch == int(os.path.getmtime(fpath)):
                return True

        return False

    return is_file_excluded


def timestamp_to_int(timestamp):
    return int((timestamp - EPOCH).total_seconds())


def is_container_excluded(container, namespace):
    meta_info = container.get("info", {}).get(namespace, {})
    if isinstance(meta_info, dict):
        return meta_info.get("ignore", False)


def warn_if_bids_invalid(f, namespace):
    """Logs a warning iff info.BIDS.valid = false."""
    metadata = get_metadata(f, namespace)
    if not metadata or metadata.get("valid") is None:
        return
    elif not parse_bool(metadata.get("valid")):
        logger.warning(
            "File {} is not valid: {}".format(
                metadata.get("Filename"), metadata.get("error_message")
            )
        )


def define_path(outdir, f, namespace):
    """Each potential download file is checked for BIDS status (i.e., is there an error msg for filename being too short, then it is skipped)
    metadata["Filename"] and full_filename are the original series name that was uploaded. (The session in metadata['Path'] actually has to be sanitized
    as it contains a "}").
    """
    metadata = get_metadata(f, namespace)
    filename = f.get("name", [])
    if not metadata:
        full_filename = ""
    elif metadata.get("Filename"):
        # Ensure that the folder exists...
        full_path = os.path.join(outdir, metadata["Path"])
        # Define path to download file to...
        full_filename = os.path.join(full_path, metadata["Filename"])
    elif any(ext in filename for ext in [".json", ".tsv"]):
        full_filename = os.path.join(outdir, f["name"])
    else:
        full_filename = ""
    return full_filename


def get_folder(f, namespace):
    metadata = get_metadata(f, namespace)
    if not metadata:
        return ""

    return metadata.get("Folder")


def check_sidecar_exist(fw, filepath_downloads, outdir, ignore_sidecars):
    """Make sure all NIfTIs in acquisitions to be downloaded have a sidecar.

    If the sidecar exists (the json file is listed in filepath_downloads["sidecar"]),
    then nothing is changed or created and it will be downloaded with the NIfTI file
    when this returns to download_bids_files().
    If the sidecar does not exist, then the sidecar is created from the metadata
    and the newly generated sidecar is written to outdir.

    Args:
        fw: (Flywheel Client)
        filepath_downloads: {container_type: {filepath: {'args': (tuple of args for sdk download function), 'modified': file modified attr}}}
            args[0] = id
            args[1] = name from the platform
            args[2] = name at dest
            modified = Different, time-based representations of the last changes to the file
        outdir: (string) path to directory to download files to
        ignore_sidecars: (bool) true if sidecars should be created using file.info metadata
    """
    for acq, acq_details in filepath_downloads["acquisition"].items():
        if acq.endswith(".nii.gz"):
            sidecar_path = acq[:-7] + ".json"
        elif acq.endswith(".nii"):
            sidecar_path = acq[:-4] + ".json"
        else:
            continue  # only need sidecars from NIfTIs produced from DICOMs

        if ignore_sidecars:
            if sidecar_path in filepath_downloads["sidecar"]:
                logger.warning(
                    "Ignoring real sidecar file %s and using metadata in file.info instead.",
                    sidecar_path,
                )
                del filepath_downloads["sidecar"][sidecar_path]

        # else if not ignore_sidecars and sidecar_path is in filepath_downloads, it will be downloaded later.

        # At this point either ignore_sidecars is true and the path has been deleted from filepath_downloads
        # or ignore_sidecars is false and the path might be missing from filepath_downloads, so...

        if sidecar_path not in filepath_downloads["sidecar"]:
            # Need to find the NIfTI file in this acquisition to get its metadata to put in the sidecar
            f = [
                x
                for x in fw.get_acquisition(acq_details["args"][0]).get("files", {})
                if acq_details["args"][1] == x["name"]
            ][0]
            try:
                create_json_sidecar(f["info"], "BIDS", outdir)
            except:  # noqa: E722
                logger.error(f"{f['name']} does not have info section.")


def create_json_sidecar(metadata, namespace, outdir):
    """Create a JSON file with the BIDS info.

    Given a dictionary of the meta info and the path, creates a JSON file
    with the FW metadata, except for BIDS info.

    namespace in the template namespace, in this case it is 'BIDS'.

    Args:
        info (str or dict) : str is the acq_id; dict is BIDS namespace metadata
        namespace (str) : key in the meta_info to save (BIDS)
        outdir: directory where the json will be written
    """
    # Remove the 'BIDS' value from info
    try:
        ns_data = metadata.pop(namespace)
    except:  # noqa: E722
        ns_data = {}

    # If meta info is empty, simply return
    if not metadata:
        logger.info(
            f"No metadata, besides possibly {namespace}, available to create sidecar"
        )
        return

    # Perform delete and updates
    for key in ns_data.get("delete_info", []):
        metadata.pop(key, None)

    for key, value in ns_data.get("set_info", {}).items():
        metadata[key] = value

    # Get filepath of matching image file from the BIDS info
    img_bids_name = ns_data["Filename"]
    # Remove extension of path and replace with .json
    ext = utils.get_extension(img_bids_name)
    # BIDS filepath is in the namespace_data dict
    new_path = Path(
        outdir, ns_data["Path"], Path(img_bids_name[: -len(ext)]).stem + ".json"
    )

    # Write out contents to JSON file
    with open(new_path, "w") as outfile:
        json.dump(metadata, outfile, sort_keys=True, indent=4)
    return new_path


def download_bids_files(fw, filepath_downloads, dry_run, outdir, ignore_sidecars):
    """Args:
    fw: Flywheel Client
    filepath_downloads: {container_type: {filepath: {'args': (tuple of args for sdk download function), 'modified': file modified attr}}}
        args[0] = id
        args[1] = name from the platform
        args[2] = name at dest
        modified = Different, time-based representations of the last changes to the file
    dry_run: (bool) if true, don't actually do anything
    outdir: (string) path to directory to download files to
    ignore_sidecars: (bool) true if sidecars should be created using file.info metadata.
    """
    check_sidecar_exist(fw, filepath_downloads, outdir, ignore_sidecars)

    # Download all project files
    logger.info("Downloading project files")
    for f in filepath_downloads["project"]:
        args = filepath_downloads["project"][f]["args"]

        try:
            modified = filepath_downloads["project"][f]["modified"]
            logger.info(f"Downloading project file: {args[1]}")
            # For dry run, don't actually download
            if dry_run:
                logger.info(f"  to {args[2]}")
                continue
            fw.download_file_from_project(*args)
            # Set the mtime of the downloaded file to the 'modified' timestamp in seconds
            modified_time = float(timestamp_to_int(modified))
            os.utime(f, (modified_time, modified_time))
        except:  # noqa: E722
            logger.info(f"{f} not found")

        # If zipfile is attached to project, unzip...
        path = args[2]
        zip_pattern = re.compile("[a-zA-Z0-9]+(.zip)")
        zip_dirname = path[:-4]
        if zip_pattern.search(path):
            zip_ref = zipfile.ZipFile(path, "r")
            zip_ref.extractall(zip_dirname)
            zip_ref.close()
            # Remove the zipfile
            os.remove(path)

    for ft in ["session", "acquisition", "sidecar"]:
        # Download all files for the looped filetype
        logger.info(f"Downloading {ft} files")
        for f in filepath_downloads[ft]:
            args = filepath_downloads[ft][f]["args"]
            logger.info(f"Downloading {ft} file: {args[1]}")
            # For dry run, don't actually download
            if dry_run:
                logger.info(f"  to {args[2]}")
                continue

            modified = filepath_downloads[ft][f].get("modified")
            if ft == "sidecar":
                fw.download_file_from_acquisition(*args)
            else:
                getattr(fw, "download_file_from_" + ft)(*args)
            # Set the mtime of the downloaded file to the 'modified' timestamp in seconds
            if modified:
                modified_time = float(timestamp_to_int(modified))
                os.utime(f, (modified_time, modified_time))


def download_bids_dir(
    fw,
    container_id,
    container_type,
    outdir,
    src_data=False,
    dry_run=False,
    replace=False,
    save_sidecar_as_metadata="",  # currently, this is not provided by any code that calls this function
    subjects=[],
    sessions=[],
    folders=[],
    validation_requested=True,
):
    """Use container BIDS metadata to download BIDS formatted NIfTI files, sidecars, and other data.

    Args:
        fw: Flywheel client
        container_id: ID of the container to download BIDS formatted data
        container_type (str "project", "session", "acquisition"): type of container to download BIDS,
        outdir: path to directory to download files to, string
        src_data: Option to include sourcedata when downloading.
        dry_run: Option to not actually download any data, just print what would be exported
        replace: Option to replace files if the modified timestamps do not match
        save_sidecar_as_metadata (str): Provided by user, "yes" will retain the sidecars produced
            by dcm2niix and NIfTI file metadata will not be used to create sidecars on exporting
            BIDS formatted data unless the sidecar file is missing.  If "no", json sidecar
            files will be created from NIfTI file metadata when exporting BIDS formatted data.
            If "auto" or "", this function will determine how the project has been curated.
        subjects: list of subject codes to download
        sessions: list of session labels to download
        folders: list of folders to download
        validation_requested: Option to validate the downloaded data
    """
    # Define namespace
    namespace = "BIDS"
    is_file_excluded = is_file_excluded_options(namespace, src_data, replace)

    # Files and the corresponding download arguments separated by parent container
    filepath_downloads = {
        "project": {},
        "session": {},
        "acquisition": {},
        "sidecar": {},
    }
    valid = True

    if container_type == "project":
        # Get project
        project = fw.get_project(container_id)

        ignore_sidecars = find_how_curated(
            project.info, namespace, save_sidecar_as_metadata
        )
        # if ignore_sidecars is True, then the sidecar files will be created from NIfTI file metadata

        logger.info("Processing project files")
        # Iterate over any project files
        for f in project.get("files", []):
            # Define path - ensure that the folder exists...
            path = define_path(outdir, f, namespace)
            # If path is not defined (an empty string) move onto next file
            if not path:
                continue

            # Don't exclude any files that specify exclusion
            if is_file_excluded(f, path):
                continue

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            warn_if_bids_invalid(f, namespace)

            if path in filepath_downloads["project"]:
                logger.error(
                    "Multiple files with path {0}:\n\t{1} and\n\t{2}".format(
                        path, f["name"], filepath_downloads["project"][path]["args"][1]
                    )
                )
                valid = False

            filepath_downloads["project"][path] = {
                "args": (project["_id"], f["name"], path),
                "modified": f.get("modified"),
            }

        path = os.path.join(outdir, "./dataset_description.json")
        if ignore_sidecars:
            if path in filepath_downloads["project"]:
                logger.warning(
                    "dataset_description.json will be ignored because sidecar information "
                    "is stored in project Custom Information (project.info.BIDS)."
                )
                del filepath_downloads["project"][path]

            # create the required json file from project info
            fake_nifti_info = copy.deepcopy(project.info["BIDS"])
            fake_nifti_info["BIDS"] = {
                "Filename": "dataset_description.nii.gz",
                "Path": ".",
            }
            create_json_sidecar(fake_nifti_info, "BIDS", outdir)

        # Get project sessions
        project_sessions = fw.get_project_sessions(container_id)

    elif container_type == "session":
        project_sessions = [fw.get_session(container_id)]

    else:
        project_sessions = []

    if project_sessions:
        logger.info("Processing session files")
        all_acqs = []
        for proj_ses in project_sessions:
            # Skip session if we're filtering to the list of sessions
            if sessions and proj_ses.get("label") not in sessions:
                continue

            # Skip session if BIDS.Ignore is True
            if is_container_excluded(proj_ses, namespace):
                continue

            # Skip subject if we're filtering subjects
            if subjects:
                subj_code = proj_ses.get("subject", {}).get("code")
                if subj_code not in subjects:
                    continue

            # Get true session if files aren't already retrieved, in order to access file info
            if proj_ses.get("files"):
                session = proj_ses
            else:
                session = fw.get_session(proj_ses["_id"])
            # Check if session contains files
            # Iterate over any session files
            for f in session.get("files", []):
                # Define path - ensure that the folder exists...
                path = define_path(outdir, f, namespace)
                # If path is not defined (an empty string) move onto next file
                if not path:
                    continue

                # Don't exclude any files that specify exclusion
                if is_file_excluded(f, path):
                    continue

                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                warn_if_bids_invalid(f, namespace)

                if path in filepath_downloads["session"]:
                    logger.error(
                        'Multiple files with path {path}:\n\t{f["name"]} and\n\t{filepath_downloads["session"][path]["args"][1]}'
                    )
                    valid = False

                filepath_downloads["session"][path] = {
                    "args": (session["_id"], f["name"], path),
                    "modified": f.get("modified"),
                }

            logger.info("Processing acquisition files")
            # Get acquisitions
            # session_acqs[ix]['files'][ix]['name'] is the originally uploaded series name
            session_acqs = fw.get_session_acquisitions(proj_ses["_id"])
            all_acqs += session_acqs
    elif container_type == "acquisition":
        all_acqs = [fw.get_acquisition(container_id)]
    else:
        all_acqs = []

    if all_acqs:
        for ses_acq in all_acqs:
            # Skip if BIDS.Ignore is True
            if is_container_excluded(ses_acq, namespace):
                continue
            # Get true acquisition if files aren't already retrieved, in order to access file info

            acq = fw.get_acquisition(ses_acq["_id"])
            # Iterate over acquisition files
            for f in acq.get("files", []):
                # Skip any folders not in the skip-list (if there is a skip list)
                if folders:
                    folder = get_folder(f, namespace)
                    if folder not in folders:
                        continue

                # Define path - ensure that the folder exists...
                path = define_path(outdir, f, namespace)
                # If path is not defined (an empty string) move onto next file
                if not path:
                    continue

                # Don't exclude any files that specify exclusion or already exist in the destination folder
                if is_file_excluded(f, path):
                    continue

                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                warn_if_bids_invalid(f, namespace)

                if path in filepath_downloads["acquisition"]:
                    logger.error(
                        f"Multiple files with path {path}:\n\t{f['name']} "
                        f"and\n\t{filepath_downloads['acquisition'][path]['args'][1]}"
                    )
                    valid = False

                if ".json" in Path(path).suffix:
                    file_type = "sidecar"
                else:
                    file_type = "acquisition"
                filepath_downloads[file_type][path] = {
                    "args": (acq["_id"], f["name"], path),
                    "modified": f.get("modified"),
                }
    else:
        msg = (
            container_type
            + ", with subjects="
            + str(subjects)
            + " sessions="
            + str(sessions)
            + " folders="
            + str(folders)
        )
        logger.error("No valid BIDS data found in %s", msg)
        valid = False

    if not valid and validation_requested:
        # If the BIDS app has its own validation and the user does not want FW to
        # check before downloading the data (validation = False), then don't
        # stop the download and the gear.
        raise BIDSExportError(
            "Error mapping files from Flywheel to BIDS.\nHint: Check curation."
        )

    download_bids_files(fw, filepath_downloads, dry_run, outdir, ignore_sidecars)

    if not dry_run:
        remove_orphaned_fmaps(outdir)


def determine_container(fw, project_label, container_type, container_id, group_id=None):
    """Figures out what container_type and container_id should be if not given."""
    cid = ctype = None
    if container_type and container_id:
        # Download single container
        cid = container_id
        ctype = container_type
    else:
        if bool(container_id) != bool(container_type):
            logger.error(
                "Did not provide all options necessary to download single container"
            )
            raise BIDSExportError(
                "Did not provide all options necessary to download single container"
            )
        elif not project_label:
            logger.error("Project label information not provided")
            raise BIDSExportError("Project label information not provided")
        # Get project Id from label
        cid = utils.validate_project_label(fw, project_label, group_id=group_id)
        ctype = "project"
    return ctype, cid


def export_bids(
    fw,
    bids_dir,
    project_label,
    group_id=None,
    subjects=None,
    sessions=None,
    folders=None,
    replace=False,
    dry_run=False,
    container_type=None,
    container_id=None,
    source_data=False,
    validate=True,
):
    ### Prep
    # Check directory name - ensure it exists
    validate_dirname(bids_dir)

    # Check that container args are valid
    ctype, cid = determine_container(
        fw, project_label, container_type, container_id, group_id=group_id
    )

    ### Download BIDS project
    download_bids_dir(
        fw,
        cid,
        ctype,
        bids_dir,
        src_data=source_data,
        dry_run=dry_run,
        replace=replace,
        subjects=subjects,
        sessions=sessions,
        folders=folders,
        validation_requested=validate,
    )

    # Validate the downloaded directory
    #   Go one more step into the hierarchy to pass to the validator...
    if validate and not dry_run:
        utils.validate_bids(bids_dir)


def write_bidsignore(fname, outdir):
    """Add entries to .bidsignore, so that validation is performed on the correct files
    Args:
        fname (str): entry to append to .bidsignore
        outdir (filepath): directory where output is directed.
    """
    bidsignore = os.path.join(outdir, ".bidsignore")
    with open(bidsignore, "a+") as f:
        contents = f.readlines()
        if fname not in contents:
            f.write(f"{fname}\n")


def main():
    ### Read in arguments
    parser = argparse.ArgumentParser(description="BIDS Directory Export")
    parser.add_argument(
        "--bids-dir",
        dest="bids_dir",
        action="store",
        required=True,
        help="Name of directory in which to download BIDS hierarchy. \
                    NOTE: Directory must be empty.",
    )
    parser.add_argument(
        "--api-key", dest="api_key", action="store", required=True, help="API key"
    )
    parser.add_argument(
        "--source-data",
        dest="source_data",
        action="store_true",
        default=False,
        required=False,
        help="Include source data in BIDS export",
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=False,
        required=False,
        help="Don't actually export any data, just print what would be exported",
    )
    parser.add_argument(
        "--replace",
        dest="replace",
        action="store_true",
        default=False,
        required=False,
        help="Replace files if the modified timestamps do not match",
    )
    parser.add_argument(
        "--subject",
        dest="subjects",
        action="append",
        help="Limit export to the given subject",
    )
    parser.add_argument(
        "--session",
        dest="sessions",
        action="append",
        help="Limit export to the given session name",
    )
    parser.add_argument(
        "--folder",
        dest="folders",
        action="append",
        help="Limit export to the given folder. (e.g. func)",
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
        "-g",
        dest="group_id",
        action="store",
        required=False,
        default=None,
        help="Group ID on Flywheel instance",
    )
    parser.add_argument(
        "--container-type",
        dest="container_type",
        action="store",
        required=False,
        default=None,
        help="Download single container (acquisition|session|project) in BIDS format. Must provide --container-id.",
    )
    parser.add_argument(
        "--container-id",
        dest="container_id",
        action="store",
        required=False,
        default=None,
        help="Download single container in BIDS format. Must provide --container-type.",
    )
    args = parser.parse_args()

    # Check API key - raises Error if key is invalid
    fw = flywheel.Client(args.api_key)

    try:
        export_bids(
            fw,
            args.bids_dir,
            args.project_label,
            group_id=args.group_id,
            subjects=args.subjects,
            sessions=args.sessions,
            folders=args.folders,
            replace=args.replace,
            dry_run=args.dry_run,
            container_type=args.container_type,
            container_id=args.container_id,
            source_data=args.source_data,
        )
    except errors.BIDSException as bids_exception:
        logger.error(bids_exception)
        sys.exit(bids_exception.status_code)


if __name__ == "__main__":
    main()
