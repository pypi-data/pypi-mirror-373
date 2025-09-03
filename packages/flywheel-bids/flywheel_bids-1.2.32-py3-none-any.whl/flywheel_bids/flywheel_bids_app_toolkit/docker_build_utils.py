# Use this module to whittle down the base, official BIDS app Docker image to only the files needed to run a BIDS app and add the files to a secure, Flywheel Dockerfile stage
# 1) creating a Docker image with the BIDS app as the second stage with reprozip installed (Dockerfile in setup folder)
# 2) running the BIDS app command within the Docker container using reprozip to generate the .reprozip-trace/config.yml file (`reprozip trace --dont-find-inputs-outputs`)
# 3) copying the .reprozip-trace/config.yml from the Docker container to the host machine (`docker cp <container_id>:.reprozip-trace/config.yml setup/reprozip_config.yml`)

import json
import logging
import os
import sys
from typing import Dict, List, Optional

import yaml

log = logging.getLogger(__name__)


def create_bare_algo_stage():
    """
    Creates a bare algorithm stage by performing the following steps:

    1. Finds the path of the 'reprozip_config.yml' file.
    2. Finds the path of the 'manifest.json' file.
    3. Creates the path for the output script named 'create_tar.sh' in the same directory as 'reprozip_config.yml'.
    4. Parses the reprozip YAML file using 'parse_reprozip_yml' function.
    5. Updates the environment variables in the manifest JSON file using 'update_manifest_environ' function.
    6. Retrieves the list of files to keep from the reprozip data using 'get_files_to_keep' function.
    7. Generates a script named 'create_tar.sh' that creates a tar file containing the files to keep.
    """
    rzp_yml_path = find_file("reprozip_config.yml")
    manifest_json_path = find_file("manifest.json")
    output_script = os.path.join(os.path.dirname(rzp_yml_path), "copy_files.sh")
    reprozip_data = parse_reprozip_yml(rzp_yml_path)
    update_manifest_environ(reprozip_data, manifest_json_path)
    files_to_keep = get_files_to_keep(reprozip_data)
    generate_shell_script(files_to_keep, output_script)


def create_unpack_app_script():
    """
    Create template script for multi-stage Dockerfile creation.

    If the gear does not have an unpack_app.sh script, create one.
    """
    script_content = """#!/bin/bash

# Define an array of directories to be moved
directories=("usr" "templateflow" "home" "etc" "opt")

# Loop through each directory and copy its contents to the root directory
for dir in "${directories[@]}"; do
    echo "Processing directory: $dir"
    if [ -d "$dir" ]; then
        # Create the target directory if it doesn't exist
        if [ ! -d "/$dir" ]; then
            echo "Creating target directory: /$dir"
            mkdir -p "/$dir"
        fi
        
        # Copy contents, skipping files that already exist
        # Skipping the files that already exist should ONLY affect the 
        # underlying Linux distro packages. These packages should be 
        # separate from the BIDS app, since a BIDS app could be installed 
        # on top of any Linux distro.
        echo "Copying contents of $dir to /$dir"
        rsync -av --ignore-existing "$dir/" "/$dir/"
    else
        echo "Directory $dir does not exist."
    fi
done
"""
    rzp_yml_path = find_file("reprozip_config.yml")
    output_script = os.path.join(os.path.dirname(rzp_yml_path), "unpack_app.sh")

    if not os.path.exists(output_script):
        # Ensure the setup directory exists
        os.makedirs(output_script, exist_ok=True)

        # Write the script content to the file
        with open(output_script, "w") as script_file:
            script_file.write(script_content)


def find_file(filename: str, search_path: str = os.getcwd()) -> Optional[str]:
    """
    Recursively searches for a file in the given directory and its subdirectories.
    Parameters:
        filename (str): The name of the file to search for.
        search_path (str): The directory to start the search from.
    Returns:
        str: The path to the found file, or None if not found.
    """
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)

    # If the file is not found, log an error and exit
    log.error(f"File {filename} not found in {search_path}")
    log.info(
        "See the top of the create_bare_algo_stage.py file in the BIDS App toolkit for more information."
    )
    sys.exit(1)


def parse_reprozip_yml(file_path: str) -> dict:
    """
    Parses the content of a YAML file and returns the data as a Python object.

    Parameters:
        file_path (str): The path to the YAML file.

    Returns:
        dict: The parsed data from the YAML file.
    """
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        return data


def get_files_to_keep(data: Dict[str, any]) -> List[str]:
    """
    Returns a list of files to keep based on the given data.

    These are the files that ReproZip identified as being used by the algorithm when the trace was generated from the initial, large Dockerfile pulled from the official image.

    Args:
        data (dict): A dictionary containing package information.

    Returns:
        files_to_keep (list): A list of files to keep.
    """
    files_to_keep = []
    exclude_general_dirs = [
        "/.dockerenv",
        "/",
        "/bin",
        "/lib",
        "/lib64",
        "/opt",
        "/opt/conda",
        "/run",
        "/usr/lib",
        "/usr/share/fonts",
        "/tmp",
        "/usr/bin/dash",
        "/usr/bin/mount",
        "/usr/bin/sh",
        "/usr/bin/uname",
        "/usr/lib/locale/locale-archive",
        "/usr/local/share/fonts",
    ]
    exclude_starting_substrings = [
        "/flywheel",
        "/proc",
        "/sys/module",
        "/sys/bus",
        "/opt/conda",
        "/usr/share/fonts",
    ]

    for package in data.get("packages", []):
        files_to_keep.extend(package.get("files", []))

    files_to_keep.extend(data.get("other_files", []))
    log.info("Filtering %d files", len(files_to_keep))

    # Filter out files
    files_to_keep = [f for f in files_to_keep if f not in exclude_general_dirs]
    files_to_keep = [
        f
        for f in files_to_keep
        if not any(f.startswith(sub) for sub in exclude_starting_substrings)
    ]
    log.info("Final file count is %d", len(files_to_keep))

    return files_to_keep


def generate_shell_script(files: List[str], output_script: str) -> None:
    """
    Generates a shell script that creates a tar archive of the specified files.

    Args:
        files (list): A list of file paths to include in the tar archive.
        output_script (str): The path to the output shell script.

    Returns:
        None
    """
    with open(output_script, "w") as script:
        script.write("#!/bin/sh\n")
        script.write("""files_to_copy="\n""")
        for file in files:
            script.write(f"    {file}\n")
        script.write(""""\n""" "")
        script.write("""for file in $files_to_copy; do\n""")
        script.write("""    cp -r --parents "$file" /app \n""")
        script.write("done\n")


def update_manifest_environ(reprozip_data: Dict[str, any], manifest_path: str) -> None:
    """
    Updates the manifest.json file with the environment variables from reprozip_config.yml.
    Parameters:
        reprozip_data (dict): The parsed data from reprozip_config.yml.
        manifest_path (str): The path to the manifest.json file.
    """
    environ = reprozip_data["runs"][0].get("environ", {})
    log.info(
        "Updating manifest.json with environment variables from the reprozip trace."
    )
    with open(manifest_path, "r") as file:
        manifest_data = json.load(file)

    if "environment" not in manifest_data:
        manifest_data["environment"] = {}

    manifest_data["environment"].update(environ)

    with open(manifest_path, "w") as file:
        json.dump(manifest_data, file, indent=4)


if __name__ == "__main__":
    create_bare_algo_stage()
