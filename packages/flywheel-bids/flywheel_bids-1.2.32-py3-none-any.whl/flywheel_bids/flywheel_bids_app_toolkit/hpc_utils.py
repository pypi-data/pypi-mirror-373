"""Improve compatibility with HPC clients and tools."""

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Union

from flywheel_gear_toolkit.context import GearToolkitContext

log = logging.getLogger(__name__)


def check_and_link_dirs(gear_context: GearToolkitContext) -> None:
    """Set symlinks to writable dirs for smooth Singularity runs.

    Args:
        gear_context (GearToolkitContext): information about the gear run
    """
    if log.level == logging.DEBUG:
        check_container_type()
    if is_directory_writable(gear_context.work_dir):
        log.debug("%s is writable", gear_context.work_dir)
        setattr(gear_context, "writable_dir", gear_context.work_dir)
        log.debug("FYI: Container type is %s", check_container_type())
    else:
        log.warning(
            "%s is not writable. Creating a writable directory in /tmp.\nIf the algorithm is long-running, there may be issues with files from /tmp being output as the gear shuts down.",
            gear_context.work_dir,
        )
        setattr(gear_context, "writable_dir", create_temp_workspace())

    log.debug("Setting gear_context.writable_dir: %s", gear_context.writable_dir)

    # Handle FreeSurfer
    if os.environ.get("SUBJECTS_DIR", None):
        reset_FS_subj_paths(gear_context)


def old_check_and_link_dirs(
    gear_context: GearToolkitContext, root_dir: Union[Path, str]
) -> List[Tuple[str, str]]:
    """
    Traverse the specified directory. Identify and attempt to symlink unwritable folders.

    Args:
        gear_context (GearToolkitContext): information about the gear run
        root_dir (Union[Path,str]): Top-level directory (e.g., /conda) to search for (un)writable directories.

    Returns:
        List[Tuple[str,str]]: A list of tuples with the unwritable paths and error messages.
    """
    pass

    # unwritable_dirs = []
    # for dir_path, dir_names, filenames in os.walk(root_dir):
    #     dir_path = Path(dir_path)
    #     if not is_directory_writable(dir_path):
    #         for dir_name in dir_names:
    #             if (
    #                 os.environ.get("SUBJECTS_DIR", None)
    #                 and dir_name in os.environ["SUBJECTS_DIR"]
    #             ) or "fs" in dir_name:
    #                 # Necessary paths changed by reset_FS_subj_paths
    #                 pass
    #             else:
    #                 try:
    #                     # Send the link to /flywheel/v0/work
    #                     create_symlink_for_singularity(
    #                         dir_path / dir_name, Path(gear_context.work_dir) / dir_name
    #                     )
    #                 except Exception as e:
    #                     # Catch any other exceptions (e.g., permission errors when trying to os.walk)
    #                     unwritable_dirs.append(
    #                         (
    #                             str(dir_path / dir_name),
    #                             f"Unable to create symlink for unwritable dir: dir{str(e)}",
    #                         )
    #                     )
    # return unwritable_dirs


def check_container_type():
    """Determine whether the gear lauched with Singularity or Docker."""
    if "SINGULARITY_ENVIRONMENT" in os.environ:
        return "Singularity"
    elif any("docker" in key.lower() for key in os.environ):
        return "Docker"
    else:
        return "Not a container"


def create_symlink_for_singularity(
    source_dir: Union[Path, str], link_name: Union[Path, str]
):
    """
    Creates a symbolic link named link_name pointing to source_dir,
    intended for use with Singularity containers.

    Args:
        source_dir (Union[Path,str]): Path to the source directory.
        link_name (Union[Path,str]): Name of the symlink to be created.
    """
    # Ensure the source directory exists
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    # Construct the full path for the symlink
    link_path = os.path.abspath(link_name)

    # Check if the symlink already exists
    if os.path.islink(link_path):
        log.debug(f"Symlink {link_name} already exists. Overwriting...")

    # Create the symlink
    os.symlink(source_dir, link_path)
    log.debug(f"Created symlink {link_name} -> {source_dir}")


def create_temp_workspace(
    unwritable_dir: Union[Path, str] = "/flywheel/v0",
    writable_dir: str = "/tmp",
    tmp_dir_name: str = "gear_tmp_dir_",
) -> Path:
    """
    Create a temporary workspace directory with symlinks to the current directory's contents.

    This function creates a temporary directory within the specified writable directory,
    creates symlinks for all items in the current working directory to this new directory,
    and changes the current working directory to the newly created temporary directory.

    Args:
        unwritable_dir (Path, str): The directory that was detected as unwritable.
        writable_dir (str): The directory where the temporary workspace will be created.
                            This directory must be writable.
        tmp_dir_name (str): A prefix for the name of the temporary directory.

    Returns:
        Path: A Path object representing the newly created temporary workspace directory.

    Raises:
        OSError: If there are issues creating the temporary directory or symlinks.
        PermissionError: If the specified writable_dir is not actually writable.

    Example:
        >>> new_workspace = create_temp_workspace("/tmp", "my_tmp_")
        >>> print(new_workspace)
        /tmp/my_tmp_a1b2c3
    """
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix=tmp_dir_name, dir=writable_dir))
    log.debug(f"Running at path {temp_dir}")

    # Create symlinks for all files in unwritable directory
    for item in Path(unwritable_dir).iterdir():
        (temp_dir / item.name).symlink_to(item)

    # Change working directory
    os.chdir(temp_dir)
    log.debug("Using %s as working directory", Path.cwd())

    # Might need to update bids_app_context.analysis_output_dir?, gear_context.work_dir?

    return temp_dir


def find_bids_related_dirs(
    search_terms: List[str] = ["AFNI", "ANTS", "CONDA", "FSL", "TEMPLATEFLOW"],
) -> List[Path]:
    """
    Search the environmental variables from the manifest to populate a list of directories that need to be asssessed for writability.

    Args:
        search_terms (List[str]): what should be in the environmental settings that may need to be used/writable by nipype or the BIDS app executable directly?

    Returns:
        List[Path] of directories from the ENV to assess for writability
    """
    matching_vars = search_environ(search_terms)
    dirs_to_update = []
    if matching_vars:
        for k, v in matching_vars.items():
            dirs_to_update.append(Path(v))
    return dirs_to_update


def is_directory_writable(dir_path: Union[Path, str]):
    """Use file creation as robust test of writability.

    Args:
        dir_path (Union[Path,str]): Directory to check

    Returns
        boolean regarding writability status
    """
    try:
        # Create a temporary file in the directory
        temp_file_name = "temp_write_test.txt"
        temp_file_path = os.path.join(dir_path, temp_file_name)

        with open(temp_file_path, "w"):
            pass

        # Remove the temporary file after testing
        os.remove(temp_file_path)

        return True
    except IOError as e:
        log.error("Failed to write to directory: %s", str(e))
        return False
    except Exception as e:
        log.error("Error checking writability: %s", str(e))
        return False


def remove_tmp_dir(tmp_dir: Path) -> None:
    """
    Remove a tmp directory and all its contents.

    This function removes all symlinks within the specified directory,
    then removes the directory itself.

    Args:
        tmp_dir (Path): The Path object representing the tmp directory to be removed.

    Raises:
        OSError: If there are issues removing symlinks or the directory.

    Example:
        >>> tmp = Path("/tmp/my_tmp_dir")
        >>> remove_tmp_directory(tmp)
    """
    # Remove all symlinks in the directory
    for item in tmp_dir.iterdir():
        if item.is_symlink():
            item.unlink()
            log.debug("Unlinked symlink:%s", item.name)

    # Remove the entire directory
    shutil.rmtree(tmp_dir)
    log.debug("Removed tmp directory: %s", tmp_dir)


def reset_FS_subj_paths(gear_context: GearToolkitContext):
    """Update pointers to the writable locations of the FreeSurfer SUBJECTS_DIR

    To increase HPC-compatibility, change the SUBJECTS_DIR to a writable location (i.e., /flywheel/v0/work) and update pointers for all the averages folders to use the writable location.

    Args:
        gear_context (GearToolkitContext): _description_
    """
    # All writeable directories need to be set up in the current working directory
    orig_subject_dir = Path(os.environ.get("SUBJECTS_DIR", "/opt/freesurfer/subjects"))
    subjects_dir = Path(gear_context.writable_dir) / "freesurfer/subjects"
    # Send the new path back to the env
    os.environ["SUBJECTS_DIR"] = str(subjects_dir)
    log.debug("Setting SUBJECTS_DIR to %s", os.environ["SUBJECTS_DIR"])
    if not subjects_dir.exists():  # needs to be created unless testing
        subjects_dir.mkdir(parents=True)
        (subjects_dir / "fsaverage").symlink_to(orig_subject_dir / "fsaverage")
        (subjects_dir / "fsaverage5").symlink_to(orig_subject_dir / "fsaverage5")
        (subjects_dir / "fsaverage6").symlink_to(orig_subject_dir / "fsaverage6")


def search_environ(substrings: List[str]) -> Dict[str, str]:
    """
    Search os.environ for entries containing any of the given substrings in their keys.

    Args:
        substrings (List[str]): A list of substrings to search for in environment variable names.

    Returns:
        Dict[str, str]: A dictionary of matching environment variables and their values.
    """
    # Convert all substrings to uppercase for case-insensitive matching
    uppercase_substrings = set(sub.upper() for sub in substrings)

    return {
        key: value
        for key, value in os.environ.items()
        if any(sub in key for sub in uppercase_substrings)
    }
