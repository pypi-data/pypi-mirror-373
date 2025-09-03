import json
import logging
import shutil
from os import walk
from pathlib import Path
from typing import List, Optional, Union

from flywheel_gear_toolkit import GearToolkitContext
from flywheel_gear_toolkit.utils.metadata import Metadata
from flywheel_gear_toolkit.utils.zip_tools import zip_output

from . import BIDSAppContext
from .compression import walk_tree_to_exclude, zip_derivatives, zip_htmls

log = logging.getLogger(__name__)


def report_errors(errors) -> str:
    """Create error strings for logs.

    Args:
        errors: Any errors collected from previous methods.

    Returns:
        msg (str): string to include in logs.
    """
    msg = "Previous errors:\n"
    for err in errors:
        if str(type(err)).split("'")[1] == "str":
            # show string
            msg += "  Error msg: " + str(err) + "\n"
        else:  # show type (of error) and error message
            err_type = str(type(err)).split("'")[1]
            msg += f"  {err_type}: {str(err)}\n"
    return msg


def report_warnings(warnings) -> str:
    """Create warning strings for logs.

    Args:
        warnings: Any warnings collected from previous methods.

    Returns:
        msg (str): string to include in logs.
    """
    msg = "Previous warnings:\n"
    for warn in warnings:
        msg += "  Warning: " + str(warn) + "\n"
    return msg


def package_output(app_context: BIDSAppContext, gear_name: str, errors: List[str]):
    """Move all the results to the final destination; clean-up.

    Args:
        app_context (BIDSAppContext): Details about the gear setup and BIDS options
        gear_name (str): gear name, used in the output file names
        errors (List[str]): list of errors found
    """
    # zip htmls first, so there are fewer issues updating the image file paths (?)
    if not app_context.gear_dry_run:
        # zip any .html files in output/<analysis_id>/
        html_dir = Path(app_context.analysis_output_dir) / app_context.bids_app_binary
        if html_dir.exists():
            zip_htmls(str(app_context.output_dir), app_context.destination_id, html_dir)
        elif app_context.post_processing_only:
            zip_htmls(
                app_context.output_dir, app_context.destination_id, app_context.bids_dir
            )

        # Catch all other htmls in the destination dir
        zip_htmls(
            str(app_context.output_dir),
            app_context.destination_id,
            app_context.analysis_output_dir,
        )

    # zip entire output/<analysis_id> folder into
    #  <gear_name>_<project|subject|session label>_<analysis.id>.zip
    zip_file_name = (
        f"{gear_name}_{app_context.run_label}_{app_context.destination_id}.zip"
    )
    zip_output(
        str(app_context.output_dir),
        app_context.destination_id,
        zip_file_name,
        dry_run=False,
        exclude_files=None,
    )
    zip_derivatives(app_context)

    # possibly save ALL intermediate output
    if app_context.save_intermediate_output:
        work_zip_file_name = f"{str(app_context.output_dir)}/{gear_name}_work_{app_context.run_label}_{app_context.destination_id}.zip"
        zip_output(
            str(Path(app_context.work_dir).parent),
            str(Path(app_context.work_dir).name),
            work_zip_file_name,
        )

    # possibly save intermediate files and folders
    if app_context.save_intermediate_files:
        selected_work_zip_filepath = f"{str(app_context.output_dir)}/{gear_name}_work_selected_files_{app_context.run_label}_{app_context.destination_id}.zip"
        excl_list = walk_tree_to_exclude(
            app_context.work_dir, app_context.save_intermediate_files.split()
        )
        zip_output(
            str(Path(app_context.work_dir).parent),
            str(Path(app_context.work_dir).name),
            selected_work_zip_filepath,
            exclude_files=excl_list,
        )

    if app_context.save_intermediate_folders:
        dirs = walk_tree_to_find_dirs(
            app_context.work_dir, app_context.save_intermediate_folders.split()
        )
        for dir in dirs:
            selected_work_zip_filepath = f"{str(app_context.output_dir)}/{gear_name}_work_{str(Path(dir).name)}_{app_context.run_label}_{app_context.destination_id}.zip"
            zip_output(
                str(Path(dir).parent), str(Path(dir).name), selected_work_zip_filepath
            )

    # clean up: remove output that was zipped
    if Path(app_context.analysis_output_dir).exists():
        if app_context.keep_output:
            log.info(
                'NOT removing output directory "%s"',
                str(app_context.analysis_output_dir),
            )
        else:
            log.debug(
                'removing output directory "%s"', str(app_context.analysis_output_dir)
            )
            shutil.rmtree(app_context.analysis_output_dir)

    else:
        log.info("Output directory does not exist so it cannot be removed")

    # Report errors at the end of the log, so they can be easily seen.
    if len(errors) > 0:
        msg = report_errors(errors)
        log.info(msg)


def save_metadata(
    context: GearToolkitContext,
    work_dir: Path,
    bids_app_binary: str,
    extra_info: Optional[dict] = None,
) -> None:
    """Write out any metadata.

    Args:
        context (GearToolkitContext): gear context
        work_dir (Path): path to the work dir
        bids_app_binary (str): algorithm being called (e.g., 'mriqc')
        extra_info (dict, optional): extra info to add to the metadata
    """
    analysis_based_metadata = {}
    # Get the analysis_output.json info generated by the gear:
    analysis_output_json = work_dir / f"{bids_app_binary}.json"
    if analysis_output_json.exists():
        with open(analysis_output_json, "r", encoding="utf8") as json_file:
            analysis_based_metadata = json.load(json_file)

    if extra_info:
        analysis_based_metadata.update(extra_info)

    if analysis_based_metadata:
        # Write the metadata (in the "results" namespace) using the gear_toolkit
        # Metadata class:
        my_metadata = Metadata(context)
        try:
            my_metadata.add_gear_info(
                "results", context.destination["id"], **analysis_based_metadata
            )
        except Exception as e:
            log.debug(f"{e}\nContainer type: {context.destination['type']}")
    else:
        log.info("No metadata to update.")


def walk_tree_to_find_dirs(root_dir: Union[Path, str], include_dirs: List[str]) -> List:
    """Locate matching paths.

    Args:
        root_dir (Path, str): base directory to search
        include_dirs List[str]: names of directories to search for

    Returns:
        matching_dirs (List): list of paths with directories that should be included
    """
    matching_dirs = []
    for dir_name in include_dirs:
        for match_root, subdirs, files in walk(root_dir):
            if Path(Path(match_root).name).match(dir_name):
                matching_dirs.append(match_root)

    return matching_dirs
