"""Tools to help zip, unzip, and process HTML, result, or archived files."""

import datetime
import fnmatch
import logging
import os
import re
from pathlib import Path
from shutil import copyfile
from typing import List, Optional, Tuple, Union
from zipfile import ZipFile

from bs4 import BeautifulSoup
from flywheel_gear_toolkit import GearToolkitContext
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive, zip_output

log = logging.getLogger(__name__)


def change_to_relative_dir(
    results_dir: Path, results_html_filename: Path
) -> Tuple[Path, Path]:
    """Cd and reset variable to relative link.

    To keep HTML paths for images functional on the platform and after
    download, use relative links. To do so, one must change directory
    into the results_dir.

    Note: This method only changes the results_html_filename to a relative
    path IF the originally specified filepath does not exist.

    Args:
        results_dir (Path): Location of BIDS App analysis output
        results_html_filename (Path): Specific results file that should be
                located in the output

    Returns:
        results_dir (Path): Results directory that is confirmed to have the
                specific HTML file; updated to cwd
        results_html_filename (Path): Confirmed path to the specified HTML

    """
    os.chdir(results_dir)
    if not results_html_filename.is_file():
        results_html_filename = Path(".") / Path(results_html_filename.name)
        if not results_html_filename.is_file():
            log.error("Location of the results html specified incorrectly.")

    # Reset the variable to be relative
    results_dir = "."
    return results_dir, results_html_filename


def walk_tree_to_exclude(root_dir: Path, inclusion_list: List) -> List:
    """Walks a tree and excludes files or directories.

    GTK requires an exclusionary list for `zip_output`. Thus, this method
    combs the tree and reports which files to pass to `zip_output` for exclusion.

    Args:
        root_dir (Path): directory to walk to locate files to exclude
        inclusion_list (List): Files to keep for zipping. If a file is
            encountered during the walk and not in this list, it will be returned
            as one of the files to exclude, when GTK zips the contents of the root_dir.

    Returns:
        excluded_items (List): Files that will not be zipped

    """
    excluded_items = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter and process the filenames
        for filename in filenames:
            if not any(
                fnmatch.fnmatch(filename, pattern) for pattern in inclusion_list
            ):
                file_path = os.path.join(dirpath, filename)
                excluded_items.append(file_path)

    return excluded_items


def prepend_index_filename(orig_filename: Union[Path, str]) -> Path:
    """Add the analysis date and time to the beginning of the filename.

    Sometimes, there is an index.html file in the analysis' output.
     This file will be need to be identified, temporarily renamed,
     and then restored to the original location. (Other htmls are
     temporarily named "index.html" prior to being zipped, so this
     method helps avoid files being overwritten.)

    Args:
        orig_filename (Union[Path, str]): full path to the file that needs to be
            temporarily renamed.

    Returns:
        updated_filename (Path): new location/name of the file, so that the file
            can be returned to its original location after the other results are
            marked and zipped.
    """
    now = datetime.datetime.now()
    updated_filename = Path(
        Path(orig_filename).parents[0],
        now.strftime("%Y-%m-%d_%H") + "_" + Path(orig_filename).name,
    )
    os.rename(orig_filename, updated_filename)
    return updated_filename


def unzip_archive_files(
    gear_context: GearToolkitContext, archive_key: str, unzip_dir: Optional[Path] = None
) -> Path:
    """Unzip archived files (e.g., FreeSurfer) from previous runs.

    This method is called when the BIDSAppContext object is instantiated.

    Args:
        gear_context (GearToolkitContext): Details about the gear run
        archive_key (str): Key to retrieve/set from app_options
        unzip_dir (Path, optional): target destination path for the unzipped archive

    Returns:
        unzip_dir (Path): newly unzipped directory
    """
    zipped_dir = gear_context.get_input_path(archive_key)
    # Keep all the unzipping in /flywheel/v0/work or output, if possible,
    # to be compatible with HPC
    if not unzip_dir:
        unzip_dir = Path(zipped_dir).with_suffix("")

    # Ensure that the destination exists
    Path(unzip_dir).mkdir(parents=True, exist_ok=True)

    unzip_archive(str(zipped_dir), str(unzip_dir))

    # Sanity check
    if unzip_dir.is_dir():
        log.debug(f"Unzipped archive to {unzip_dir}")

    return unzip_dir


def update_report_refs(
    soup: BeautifulSoup,
    results_html_filename: Path,
    results_dir: Path,
    zip_file: Path,
    bids_suffix: str,
    link_type: str = "img",
    source: str = "src",
) -> BeautifulSoup:
    """Isolate and change pieces of an html report that match the kwarg criteria.

    Args:
        tags (List): image or reportlet tags that need to be updated in the html source
                    code
        results_html_filename (Path): Original html produced by the BIDS app
        resutls_dir (Path): folder where the BIDS app has placed the files referenced
                    in the html report
        zip_file: Destination file (in /v0/flywheel/output) where the updated index
                    html will be built
        bids_suffix (str): e.g. T1w; matching criteria to make sure the file should be
                    copied and the reference updated
        source (str): identifier in the html report for the file reference; e.g., src
                    or data

    Returns:
        soup (BeautifulSoup object): updated BeautifulSoup object (used for HTML
                    creation)
    soup (BeautifulSoup): HTML with image or reportlet tags that need to be updated
    results_html_filename (Path): Original html produced by the BIDS app
    resutls_dir (Path): folder where the BIDS app has placed the files referenced in the
                    html report
    zip_file: Destination file (in /v0/flywheel/output) where the updated index.html will
                be built
    bids_suffix (str): e.g. T1w; matching criteria to make sure the file should be copied
                and the reference updated
    source (str): identifier in the html report for the file reference; e.g., src or data

    soup (BeautifulSoup): Updated HTML with updated image or reportlet tags
    """
    tags = soup.find_all(link_type)
    orig_tags = [it[source] for it in tags]
    for tag in tags:
        svg_name = tag.get(source, "")

        # Find summary htmls
        pattern = r"^sub-.*\.html*"
        regex = re.compile(pattern)

        # Filter the SVG files for the ones that match the
        # modality/suffix being reported and zipped
        if (
            svg_name
            and (bids_suffix and bids_suffix in svg_name)
            or (regex.match(str(results_html_filename.name)))
        ):
            svg_path = Path(results_dir) / svg_name
            # log.debug(f"svg_path: {svg_path}")
            # Send to the archive
            zip_file.write(svg_path, svg_path.name)
            # Update the relative link in the original (still
            # unzipped) HTML with the new location of the svg
            # img_tag["src"] = archive_name[:-4] + "/" + svg_path.name
            # Make the path relative to the output/destination folder,
            # where the image is moving. Then, it should be viewable
            # on the platform OR downloaded.
            tag[source] = "./" + svg_path.name
    updated_tags = "\n".join(t[source] for t in tags if t not in orig_tags)
    log.debug(f"Updating {link_type} tags:\n{updated_tags}")
    return soup


def zip_derivatives(app_context, alt_derivatives: Optional[List[str]] = None):
    """Zip any and all derivative folders created by the BIDS App.

    Args:
        app_context (BIDSAppContext): Details about the gear setup and BIDS options
        alt_derivatives (List, optional): Optional; any other directories to look
                    through for compression. e.g., qsirecon in addition to qsiprep
    """
    derivatives = [app_context.bids_app_binary]
    # In case there are other derivative directories to consider,
    # add them to the list. (Not all apps will have multiple dirs
    # to search)
    if alt_derivatives is not None:
        derivatives.extend(alt_derivatives)

    for derivative in derivatives:
        derivative_dir = Path(app_context.analysis_output_dir) / derivative

        if derivative_dir.exists():
            zip_file_name = (
                app_context.output_dir
                / f"{app_context.bids_app_binary}_{app_context.destination_id}_{derivative}.zip"
            )
            zip_output(
                str(app_context.analysis_output_dir),
                derivative,
                str(zip_file_name),
                dry_run=False,
                exclude_files=None,
            )
            zip_htmls(
                app_context.output_dir,
                app_context.destination_id,
                derivative_dir,
            )


def zip_htmls(
    output_dir: Union[Path, str], destination_id: str, results_dir: Union[Path, str]
):
    """Zip all .html files at the TOP LEVEL of the given path, so they
    can be displayed on the Flywheel platform.

    Each html file must be added to the main HTML zip archive, which
    is being called index.html.
    Somehow, renaming supporting files index.html and overwriting the
    index.html.zip with the newly renamed index.html via zip_it_zip_it_good
    makes the full HTML report available to the Flywheel platform.

    Args:
        output_dir (Path): Location for the zip to end up.
        destination_id (str): Flywheel ID
        results_dir (Path): Location to search for htmls to zip.
    """
    log.info("Creating viewable archives for all html files")

    if Path(results_dir).exists():
        unzipped_htmls = search_for_html_report_files(results_dir)
        log.debug(f"Located these HTML files:\n{unzipped_htmls}")
        if unzipped_htmls:
            for html in unzipped_htmls:
                try:
                    log.info(f"Zipping {html}")
                    zip_html_and_svg_files(
                        results_dir, Path(html.name), destination_id, output_dir
                    )
                except Exception as e:
                    log.error(
                        f"Unable to zip {html.name} properly.\n"
                        f"Continuing with gear clean-up. \n"
                        f"Error: {e}"
                    )
        else:
            log.warning("No *.html files at " + str(results_dir))
    else:
        log.error("Path NOT found: " + str(results_dir))


def search_for_html_report_files(folder_path: Path) -> List:
    """Find and filter HTML files created by a BIDS app algorithm.

    Args:
        folder_path (Path): Typically the BIDS output folder, where
            the HTML/results files are expected to be located.

    Returns:
        html_files (List): Top-level HTML (i.e., not component HTML files
            within subject result folders) files that need to be modified
            so that the linked images can be displayed on the platform and
            when the modified BIDS directory is downloaded.

    """
    html_files = []
    exclusion_substrings = ["citation", "modality", "_fw"]
    path_exclusion_substrs = ["figure"]
    for file in list(Path(folder_path).rglob("*.html")):
        if not any(
            sub in str(file.name).lower() for sub in exclusion_substrings
        ) and not any(sub in str(file.parents[0]) for sub in path_exclusion_substrs):
            html_files.append(file)
    return html_files


def parse_BIDS_suffix(file_name: Union[Path, str]):
    """Find the modality/suffix.

    e.g., T1w, bold

    Args:
        file_name (Union[Path, str]): Name of the scan that needs
            to be parsed. Can have multiple extensions (e.g., .nii.gz)

    Returns:
        The BIDS suffix for the scan

    Raises:
        ValueError: returns None if there is no detected suffix
    """
    # import here to avoid circularity with importing BIDSAppContext in .utils.helpers
    from .utils.helpers import split_extension  # noqa: PLC0415

    root, ext = split_extension(file_name)
    try:
        return root[root.rindex("_") :]
    except ValueError:
        return None


def zip_html_and_svg_files(
    results_dir: Path,
    results_html_filename: Path,
    destination_id: str,
    output_dir: Path,
):
    """Find all related results files, update relative links, and zip.

    Args:
        results_dir: wherever the unzipped results live;
            probably app_context.analysis_output_dir
        results_html_filename (Path): PosixPath; access just the base name describing
            the zipped result; e.g., sub-TOME3024_ses-Session2_acq-MPRHA_T1w.html with results_html_filename.name
        destination_id: Unique identifier for the analysis
        output_dir: /flywheel/v0/output for all intents and purposes
    """
    zip_name = str(results_html_filename.name) + ".zip"
    archive_name = str(Path(output_dir).joinpath(Path(zip_name)))
    # Instantiate the zip_file object, which will have
    # the results_html_filename
    zip_file = ZipFile(archive_name, "w")

    # Is there a time when there will not be an underscore to differentiate the
    # modality? Should we handle a "super subject" html?
    bids_suffix = parse_BIDS_suffix(results_html_filename.name)

    results_dir, results_html_filename = change_to_relative_dir(
        results_dir, results_html_filename
    )

    # Copy the original HTML to avoid changing paths, if downloading the entire analysis
    # The cwd is already the results_dir, so there should be no issue creating and
    # finding the file.
    fw_html_filename = str(results_html_filename.stem) + "_fw.html"
    copyfile(results_html_filename, fw_html_filename)
    # Read the original HTML from the
    with open(fw_html_filename, "r") as f:
        contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")

    search_dict = {
        "img": {"source": "src", "class_": "svg-reporlet"},
        "object": {"source": "data", "class_": "svg-reporlet"},
        # "a":{"source":'href'}
    }
    for links, v in search_dict.items():
        soup = update_report_refs(
            soup,
            results_html_filename,
            results_dir,
            zip_file,
            bids_suffix,
            link_type=links,
            source=v["source"],
        )

    # Write the updated HTML back to the file
    with open(fw_html_filename, "w") as f:
        f.write(str(soup))

    # Zip the archive with the actual, file path-modified
    # html renamed to "index.html" for Flywheel platform
    # to display properly
    zip_file.write(fw_html_filename, "index.html")
    os.remove(fw_html_filename)
