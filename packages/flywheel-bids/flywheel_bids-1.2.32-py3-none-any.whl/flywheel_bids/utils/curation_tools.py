import logging
from enum import Enum

logger = logging.getLogger(__name__)


class TrinaryChoice(Enum):
    OLD = 1
    NEW = 0
    UNKNOWN = -1


def find_how_curated(
    project_info: dict,
    namespace: str = "BIDS",
    save_sidecar_as_metadata: str = "",  # "yes", "no", "auto" = ""
):
    """Determine if sidecar data is being stored in NIfTI file metadata or in sidecar files.

    Originally, BIDS sidecar data was stored in the file.info.BIDS of NIfTI files and the actual json sidecar was ignored. This caused a great deal of confusion, especially if the sidecar existed, because that information was in two places and because anyone doing BIDS outside of Flywheel expects the information to be in the real sidecar.
    The new way is to respect the sidecars and not copy that information into file.info.
    The Flywheel UI uses the presences of "BIDS" in project.info to know that it should
    display in BIDS View, so the new way adds a key-value pair:

      project.info["BIDS"]["Sidecar"] = "data is in sidecar, not file.info"

    This allows the UI to display in BIDS View, even for projects that don't put sidecar
    data in info.  The old way put the contents of dataset_description.json in
    project.info["BIDS"].  The new way stores that as a json file attached to the project (along with a README.txt and other files).

    All this means that to test how BIDS was curated for a project has to be like the
    below conditionals.  "Acknowledgements" is the first required part of dataset_description.json.  It will be present in project.info["BIDS"] if the project
    has been curated the old way, and absent if curation is being done the new way.

    Args:
        project_info (flywheel.Project.info = dict):
        namespace (str): key in Flywheel metadata info to search (always "BIDS")
        save_sidecar_as_metadata (str): Provided by user, "yes" will retain the sidecars produced by dcm2niix and NIfTI file metadata will not be used to create sidecars on exporting BIDS formatted data unless the sidecar file is missing.  If "no", json sidecar files will be created from NIfTI file metadata when exporting BIDS formatted data. If "auto" or "", this function will determine how the project has been curated.

    Returns:
        ignore_sidecars (bool): True if sidecars should be ignored and JSONs should be created from metadata
    """

    # First check project.info metadata to see if the project has been curated the old or new way

    old_or_new = TrinaryChoice.UNKNOWN
    if project_info and namespace in project_info:
        if "Acknowledgements" in project_info[namespace]:
            old_or_new = TrinaryChoice.OLD
        elif (
            "Sidecar" in project_info[namespace]
            and project_info[namespace]["Sidecar"]
            == "data is in json sidecar, not file.info"
        ):
            old_or_new = TrinaryChoice.NEW
        else:
            logger.warning(
                "The project has a '%s' key in project.info, but it does not have the expected value. "
                "This could be a problem.",
                namespace,
            )

    # Now see if the user wants to do it the old or new way

    if save_sidecar_as_metadata == "no":
        how_curated = (
            "an argument was provided to use the data in sidecars instead of storing that data in "
            "NIFTI metadata. If sidecars don't exist, NIfTI file.info['BIDS'] will be used to create "
            "sidecars when writing BIDS formatted data."
        )
        ignore_sidecars = False  # "new" (default) behavior

    elif save_sidecar_as_metadata == "yes":
        how_curated = (
            "an argument was provided to store sidecar data in NIfTI file.info['BIDS'], so any existing "
            "sidecars will be ignored."
        )
        ignore_sidecars = True  # "old" behavior

    # no argument was given as to how BIDS sidecar data has been stored.  Check if curate-bids has been run

    elif old_or_new == TrinaryChoice.OLD:
        how_curated = (
            "dataset_description.json information has been found in BIDS project metadata so "
            "NIfTI file.info['BIDS'] will be used to create sidecars and any existing json sidecar files will "
            "be ignored."
        )
        ignore_sidecars = True  # "old" behavior

    elif old_or_new == TrinaryChoice.NEW:
        how_curated = (
            "'Sidecar' has been found in BIDS project metadata so json sidecar files will be "
            "used instead of storing sidecar data in NIfTI file.info['BIDS'].  If sidecar files are missing, "
            "NIfTI metadata will be used to create sidecars."
        )
        ignore_sidecars = False  # "new" (default) behavior

    else:  # no information is available to determine how BIDS data has been curated
        how_curated = (
            "no information is available to determine if sidecar data is stored in sidecar files or in the NIfTI "
            "file.info['BIDS'] metadata so the default behavior is assumed:  actual sidecar data will be used, not NIfTI "
            "file metadata."
        )
        ignore_sidecars = False  # "new" (default) behavior

    # Log what is known about how the project has been curated and then warn if there is a conflict between
    # the project's curation state and the user's request.

    logger.info("How Curated: " + how_curated)

    if (
        old_or_new == TrinaryChoice.OLD and not ignore_sidecars
    ):  # old way but using sidecars
        logger.warning(
            "The project has been curated the old way, but the user has requested to use sidecar files. "
            "This will result in the data in sidecar files being used and NIfTI file.info['BIDS'] will be ignored."
        )
        logger.warning(
            "Flywheel recommends following the BIDS_sidecar_hierarchy_curator.ipynb to standardize the curation of BIDS data."
        )

    if (
        old_or_new == TrinaryChoice.NEW and ignore_sidecars
    ):  # new way but ignoring sidecars
        logger.warning(
            "The project has been curated the new way, but the user has requested to ignore sidecar files. "
            "This will result in the data in sidecar files being ignored and NIfTI file.info['BIDS'] will be used "
            "instead."
        )
        logger.warning(
            "Flywheel recommends following the BIDS_sidecar_hierarchy_curator.ipynb to standardize the curation of BIDS data."
        )

    return ignore_sidecars  # a.k.a. save_sidecar_as_metadata
