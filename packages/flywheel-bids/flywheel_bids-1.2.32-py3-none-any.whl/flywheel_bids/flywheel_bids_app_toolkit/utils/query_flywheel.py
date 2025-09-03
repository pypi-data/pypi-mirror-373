#!/usr/bin/env python3
"""Access BIDS formatted data from the Flywheel platform.
Tooling also maps the Flywheel hierarchy to the BIDS data,
so that the containers can be located and modified.
"""

import functools
import logging
import os.path as op
import shutil
import warnings
from glob import glob
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from flywheel import ApiException, Client
from flywheel_gear_toolkit import GearToolkitContext

from flywheel_bids.export_bids import download_bids_dir
from flywheel_bids.flywheel_bids_app_toolkit.utils.tree import tree_bids
from flywheel_bids.supporting_files.errors import BIDSExportError
from flywheel_bids.utils.validate import validate_bids

log = logging.getLogger(__name__)


def deprecated(reason: str, version: str):
    """Decorator to mark a function as deprecated and issue a warning message when called.

    This decorator is used to indicate that a function is outdated and will be removed in future versions of the toolkit. It automatically generates a warning message based on the provided reason and version number, informing users of the deprecation and advising them to update their code accordingly.

    When applied to a function, it intercepts calls to that function and emits a DeprecationWarning with the specified reason and version. This helps maintain backward compatibility while guiding users towards newer alternatives.

    Usage:
        @deprecated("New feature replaces this.", "2.0")
        def old_function():
            pass

    Args:
        reason (str): explain why the function is deprecated and suggest an alternative.
        version (str): the version of the toolkit in which the function was deprecated.

    Examples:
        >>> @deprecated("Use new_method instead.", "2.0")
        def old_function():
            print("Old function called.")

        >>> old_function()
        /path/to/module.py:10: DeprecationWarning: old_function is deprecated since version 2.0. Reason: Use new_method instead.
          old_function()
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated since version {version}. Reason: {reason}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


@deprecated(
    "copy_bidsignore_file is deprecated in favor of the one-liner in the BIDS app template.",
    "1.2.14",
)
def copy_bidsignore_file(
    bids_path: Union[Path, str],
    input_dir: Union[Path, str],
    bidsignore_file: Union[Path, str] = None,
):
    """Create the bidsignore file once the bids_path is known.

    DEPRECATED in favor of using:
        if "bidsignore" in gear_context.config_json["inputs"]:
        shutil.copy(
            gear_context.config_json["inputs"]["bidsignore"]["location"]["path"],
            app_context.bids_dir / ".bidsignore",
        )


    bidsignore file will be at the top level of a project, if it exists.
    The file will be downloaded with `orchestrate_download_bids`; thus, a
    project-level bidsignore file is most likely in /flywheel/v0/work/bids.
    A specific .bidsignore entered in the config UI will land in
    /flywheel/v0/input and needs to be moved.

    Args:
        bids_path (Path): download path to the BIDS directory
        input_dir (Path): Most often /flywheel/v0/input
        bidsignore_file (Path): file with list of files/modalities to
                    exclude from BIDS processing or download
    """
    if bidsignore_file:
        try:
            shutil.copy(bidsignore_file, str(bids_path / ".bidsignore"))
        except shutil.SameFileError:
            pass
    else:
        log.info("Searching for bidsignore files")
        bidsignore_list = list(Path(input_dir).rglob("*bidsignore"))
        if len(bidsignore_list) > 0:
            bidsignore_path = str(bidsignore_list[0])
            if bidsignore_path:
                try:
                    shutil.copy(bidsignore_path, str(bids_path / ".bidsignore"))
                except shutil.SameFileError:
                    pass


def download_bids_data_for_run_level(
    gtk_context: GearToolkitContext,
    run_level: str,
    hierarchy: dict,
    folders: List[str],
    src_data: bool,
    dry_run: bool,
    do_validate_bids: bool = False,
) -> Tuple[Path, int]:
    """Download BIDS data as directed by run_level.

    Args:
        gtk_context (gear_toolkit.GearToolkitContext): flywheel gear context
        run_level (str): hierarchy level of the container (e.g., "session")
        hierarchy (dict): containing the run_level and labels for the
            run_label, group, project, subject, session, and
            acquisition.
        folders (List[str]): BIDS folders to included (['anat', 'func', etc.])
        src_data (Boolean): Download the source data files?
        dry_run (Boolean): Report on (true) or download (false) the data
        do_validate_bids (Boolean): Run a validator when downloaded?

    Returns:
        bids_path (Path): directory where the data was downloaded
        err_code (int): code to diagnose issues with the download
    """
    bids_dir = Path(gtk_context.work_dir) / "bids"
    err_code = None

    if run_level in ["project", "subject", "session"]:
        log.info(
            'Downloading BIDS for %s "%s"',
            hierarchy["run_level"],
            hierarchy["run_label"],
        )
        existing_dirs, reqd_dirs = list_existing_dirs(bids_dir, folders=folders)

        if len(existing_dirs) >= len(reqd_dirs):
            bids_path = bids_dir
        else:
            missing_dirs = list(set(reqd_dirs) - set(existing_dirs))
            subjects = [
                v for k, v in hierarchy.items() if "subject" in k and v is not None
            ]
            sessions = [
                v for k, v in hierarchy.items() if "session" in k and v is not None
            ]

            bids_path = gtk_context.download_project_bids(
                src_data=src_data,
                folders=missing_dirs,
                dry_run=dry_run,
                subjects=subjects,
                sessions=sessions,
            )
    elif run_level == "acquisition":
        if hierarchy["acquisition_label"] == "unknown acquisition":
            bids_path = None
            err_code = 23
        else:
            bids_path = bids_dir
            if not Path(bids_dir).exists():
                download_bids_dir(
                    gtk_context.client,
                    gtk_context.destination["id"],
                    "acquisition",
                    bids_dir,
                    src_data=src_data,
                    folders=folders,
                    dry_run=dry_run,
                    validation_requested=do_validate_bids,
                )
    else:
        bids_path = None
        err_code = 20

    return bids_path, err_code


def find_associated_bids_acqs(gear_context) -> List:
    """Search BIDS-related acquisitions from whichever level the gear is launched.

    This method helps address project-level analyses by BIDS app gears.
    Currently UNTESTED; may need to use `gear_context.get_parent_destination`
    and a gear_context-based `iter_find` in order to be able to test.
    The mock for `fw.acquisitions.iter_find` has been elusive when developing
    bids-qsiprep and specific testing within this toolkit.

    Args:
        gear_context (gear_toolkit.GearToolkitContext): flywheel gear context

    Returns:
        bids_acqs (List): list of acquisition objects
    """
    fw = Client(gear_context.get_input("api-key")["key"])
    destination = fw.get(gear_context.destination["id"])
    # Look up the acquisitions using the parent_id so that
    # all the files for the gear launch level are found, but
    # not more. i.e., don't find all the project files, if
    # the gear was launched for acquisition or subject.
    parent_id = destination.parents[destination.parent.type]

    # `iter_find` syntax should be 'subject=some_value'. Deviating
    # is likely to return none, since the quotes and syntax is so strict.
    acq_list = fw.acquisitions.iter_find(f"{destination.parent.type}={parent_id}")
    bids_acqs = []
    # acq_list is a list of FW objects.
    # The FW objects will most likely be project, subject, or acquisition
    for acq in acq_list:
        for f in acq.files:
            if f.info.get("BIDS"):
                bids_acqs.append(acq)
    return bids_acqs


def get_analysis_run_level_and_hierarchy(
    fw: GearToolkitContext.client, destination_id: str
) -> dict:
    """Determine the level at which a job is running, given a destination.

    Args:
        fw (gear_toolkit.GearToolkitContext.client): flywheel client
        destination_id (str): id of the destination of the gear

    Returns:
        hierarchy (dict): containing the run_level and labels for the
            run_label, group, project, subject, session, and
            acquisition.

    Raises:
        ApiException: Custom, Flywheel exception to indicate issues
            with locating a container.
    """
    hierarchy = {
        "run_level": "no_destination",
        "run_label": "unknown",
        "group": None,
        "project_label": None,
        "subject_label": None,
        "session_label": None,
        "acquisition_label": None,
    }

    try:
        destination = fw.get(destination_id)

        if destination.container_type != "analysis":
            log.error("The destination_id must reference an analysis container.")

        else:
            hierarchy["run_level"] = destination.parent.type
            hierarchy["group"] = destination.parents["group"]

            for level in ["project", "subject", "session", "acquisition"]:
                if destination.parents[level]:
                    container = fw.get(destination.parents[level])
                    hierarchy[f"{level}_label"] = container.label

                    if hierarchy["run_level"] == level:
                        hierarchy["run_label"] = container.label

    except ApiException as err:
        log.error(
            f"The destination_id does not reference a valid analysis container.\n{err}"
        )

    log.info(f"Gear run level and hierarchy labels: {hierarchy}")

    return hierarchy


def get_fw_details(gear_context: GearToolkitContext) -> Tuple[Any, Any, str]:
    """Information about the gear and current run, mostly for reporting.

    Args:
        gear_context (gear_toolkit.GearToolkitContext): flywheel gear context

    Returns:
        destination (GearToolkitContext.destination): Flywheel identification object
        gear_builder_info: Gear builder blob from the manifest
        gear_name_and_version (str): Basically, the last part of the Docker image
    """
    destination = gear_context.client.get(gear_context.destination["id"])
    if destination.parent.type == "project":
        log.warning("Analysis_level will be set to 'group'")
    gear_builder_info = gear_context.manifest.get("custom").get("gear-builder")
    # gear_builder_info.get("image") should be something like:
    # flywheel/bids-qsiprep:0.0.1_0.15.1
    gear_name_and_version = gear_builder_info.get("image").split(":")[0]

    return destination, gear_builder_info, gear_name_and_version


def list_existing_dirs(
    bids_dir: Union[Path, str],
    folders: Optional[List[str]] = ["anat", "func", "dwi", "fmap", "perf"],
) -> Tuple[List, List]:
    """Find the existing folders in the BIDS working directory to insure that all
    associated files are downloaded, but extra re-downloading is avoided.

    Args:
        bids_dir (path): The BIDS working directory
        folders (list, optional): the subset of folders to be included in the download

    Returns:
        existing_dirs (List): updated list to pass to download_bids_dir to limit
                re-download
        check_dirs (List): Any directories matching the required directory labels.
    """
    reqd_dirs = list_reqd_folders(folders)
    existing_dirs = []
    existing_paths = []
    for rd in reqd_dirs:
        if glob(op.join(bids_dir, "**", rd), recursive=True):
            existing_paths.append(glob(op.join(bids_dir, "**", rd), recursive=True))
            # Add to the exclusion list, so the data is not re-downloaded
            existing_dirs.append(rd)
    existing_dirs = list(set(existing_dirs))
    return existing_dirs, reqd_dirs


def list_reqd_folders(
    folders: Optional[List[str]] = ["anat", "func", "dwi", "fmap", "perf"],
) -> List:
    """Produce the complete list of folders that are required to be present
    for a BIDS analysis.

    Note: This method is implemented specifically to avoid incomplete downloads.

    Args:
        folders (list, optional): the subset of folders to be included in the download

    Returns:
        final_set (List): the set of folders that must be downloaded to produce
        the analysis.
    """
    std_set = ["anat", "func", "dwi", "fmap", "perf"]
    if not folders:
        final_set = std_set
    else:
        final_set = [x for x in std_set if x in folders]

    return final_set


def orchestrate_download_bids(
    gtk_context: GearToolkitContext,
    hierarchy: dict,
    tree: bool = False,
    tree_title: str = None,
    src_data: bool = False,
    folders: list = [],
    skip_download: bool = False,
    do_validate_bids=False,
) -> int:
    """Figure out run level, download BIDS, validate BIDS, tree work/bids.

    Args:
        gtk_context (gear_toolkit.GearToolkitContext): flywheel gear context
        hierarchy (dict): containing the run_level and labels for the
            run_label, group, project, subject, session, and
            acquisition.
        tree (boolean): create HTML page in output showing 'tree' of bids data
        tree_title (str): Title to put in HTML file that shows the tree
        src_data (boolean): download source data (dicoms) as well
        folders (List): only include the listed folders, if empty include all
        skip_download (boolean): don't actually download data if True
        do_validate_bids (boolean): [deprecated] run bids-validator after downloading BIDS data

    Returns:
        err_code (int): tells a bit about the error:
            0    - no error
            1..9 - error code returned by bids validator
            10   - BIDS validation errors were detected
            11   - the validator could not be run
            12   - TypeError while analyzing validator output
            20   - running at wrong level
            21   - BIDSExportError
            22   - validator exception
            23   - attempt to download unknown acquisition
            24   - destination does not exist
            25   - download_bids_dir() ApiException
            26   - no BIDS data was downloaded

    Note: information on BIDS "folders" (used to limit what is downloaded)
    can be found at https://bids-specification.readthedocs.io/en/stable/appendices/entity-table.html.
    """
    extra_tree_text = ""  # Text to be added to the end of the tree HTML file
    run_level = hierarchy["run_level"]

    # Show the complete destination hierarchy in the tree html output for clarity
    extra_tree_text += f"run_level is {run_level}\n"
    for key, val in hierarchy.items():
        extra_tree_text += f"  {key:<18}: {val}\n"
    extra_tree_text += f"  {'folders':<18}: {folders}\n"
    if src_data:
        extra_tree_text += f"  {'source data?':<18}: downloaded\n"
    else:
        extra_tree_text += f"  {'source data?':<18}: not downloaded\n"
    if skip_download:
        extra_tree_text += f"  {'dry run?':<18}: Yes\n"
    else:
        extra_tree_text += f"  {'dry run?':<18}: No\n"
    extra_tree_text += "\n"

    err_code = 0  # assume no error

    if run_level == "no_destination":
        msg = "Destination does not exist."
        log.critical(msg)
        extra_tree_text += f"ERROR: {msg}\n"
        bids_path = None
        return 24  # destination does not exist
    else:
        if gtk_context.destination["type"] == "acquisition":
            log.info("Destination is acquisition, changing run_level to 'acquisition'")
            acquisition = gtk_context.client.get_acquisition(
                gtk_context.destination["id"]
            )
            hierarchy["acquisition_label"] = acquisition.label
            extra_tree_text += (
                f"  {'acquisition_label':<18}: changed to " + f"{acquisition.label}\n\n"
            )
            run_level = "acquisition"

        try:
            bids_path, err_code = download_bids_data_for_run_level(
                gtk_context,
                run_level,
                hierarchy,
                folders,
                src_data,
                skip_download,
                do_validate_bids,
            )
        except BIDSExportError as bids_err:
            log.critical(bids_err, exc_info=True)
            extra_tree_text += f"{bids_err}\n"
            bids_path = None
            return 21
        except ApiException as err:
            log.exception(err, exc_info=True)
            extra_tree_text += f"EXCEPTION: {err}\n"
            bids_path = None
            return 25

    if bids_path and Path(bids_path).exists():
        log.info("Found BIDS path %s", str(bids_path))
        copy_bidsignore_file(
            bids_path, "/flywheel/v0/input", gtk_context.get_input_path("bidsignore")
        )

        try:
            if do_validate_bids:
                err_code = validate_bids(bids_path)
            else:
                log.info("Not running BIDS validation")
                err_code = 0
        except Exception as exc:
            log.exception(exc, exc_info=True)
            extra_tree_text += f"EXCEPTION: {exc}\n"
            err_code = 22
    else:
        msg = "No BIDS data was found to download"
        log.critical(msg)
        extra_tree_text += f"{msg}\n"
        err_code = 26

    if tree:
        tree_bids(
            bids_path,
            str(Path(gtk_context.output_dir) / "bids_tree"),
            tree_title,
            extra_tree_text,
        )

    return err_code
