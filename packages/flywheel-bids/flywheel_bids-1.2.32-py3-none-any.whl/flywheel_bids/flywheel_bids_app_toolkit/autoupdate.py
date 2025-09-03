# Create a method at the top-level of a gear, incorporating the following code to run the autoupdate methods.

# import sys
# from flywheel_bids.flywheel_bids_app_toolkit.autoupdate import main, find_file


# def run():
#     dockerfile = find_file("Dockerfile")
#     manifest = find_file("manifest.json")
#     return main(dockerfile_path=dockerfile, json_file_path=manifest)


# if __name__ == "__main__":
#     success = run()
#     sys.exit(0 if success else 1)

# The code will attempt to find any updates to the gear algorithm and perform standardized updates to the dependencies. From there, the gear will be tested and successful runs will produce a git branch that can be submitted as an MR. Unsuccessful updates or runs will produce an error about which stage failed (and, hopefully, why).

# If there are no updates, then the script will exit without code or git changes.

import json
import logging
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Union

import requests

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
log.addHandler(handler)


def extract_repo_from_dockerfile(
    dockerfile_path: Union[Path, str],
) -> Tuple[str, str, str]:
    """
    Extracts the repository name and tag from a Dockerfile.

    Args:
        dockerfile_path (str): The path to the Dockerfile.

    Returns:
        tuple: A tuple containing the username and repository/tag extracted from the Dockerfile.
    """
    dockerfile_content = ""
    with open(dockerfile_path, "r") as file:
        dockerfile_content = reversed(file.readlines())

    # Regular expression to match the FROM line and capture the repository name
    regex = r"^FROM\s+(\S+)"

    for line in dockerfile_content:
        match = re.search(regex, line)
        if match:
            image_parts = match.group(1).split("/")
            if len(image_parts) == 1:
                # Official image like "ubuntu:20.1"
                username = None
                repo_with_tag = image_parts[0]
            else:
                # User repository like "my_user/my_repo:5.0"
                username = image_parts[0]
                repo_with_tag = image_parts[-1]

            repo_parts = repo_with_tag.split(":")
            repo_name = repo_parts[0]
            tag = repo_parts[1] if len(repo_parts) > 1 else "latest"

            return username, repo_name, tag

    raise ValueError("Could not find a valid FROM instruction in the Dockerfile")


def find_file(filename: str, search_subdirs: bool = False):
    """
    Find a file in the current directory or its parent directories using pathlib.Path.

    Args:
        filename (str): The name of the file to search for (e.g., 'Dockerfile').
        search_subdirs (bool): If True, also search in subdirectories.

    Returns:
        Path: The path to the found file.

    Raises:
        FileNotFoundError: If the file is not found.
    """
    current_dir = Path.cwd()
    root_dir = Path(current_dir.root)

    while current_dir != root_dir:
        search_pattern = f"{'**/' if search_subdirs else ''}*{filename}*"

        for file_path in current_dir.glob(search_pattern):
            if filename in file_path.name:
                return file_path

        current_dir = current_dir.parent

    raise FileNotFoundError(f"{filename} not found in any parent directory")


def find_gear_details(json_file_path: Union[Path, str]) -> Tuple[str, str]:
    """
    Isolates the Flywheel gear name from the manifest.

    Args:
        json_file_path (str): The path to the JSON file containing the manifest.

    Returns:
        Tuple str, str: The gear name extracted from the manifest and Flywheel gear version.
    """
    with open(json_file_path, "r") as f:
        data = json.load(f)
    return data["name"], data["version"].split("_")[0]


def generate_updates_dictionary(
    gear_name: str, gear_version: str, bids_algo_version: str
) -> dict:
    """
    Generates a dictionary of updates based on the Docker image tag.

    Args:
        gear_name (str): The gear name, replacing slashes with underscores.
        bids_algo_version (str): The Docker image tag.

    Returns:
        dict: A dictionary containing custom and version information for the updates.
    """
    fw_name = gear_name.replace("/", "_")
    return {
        "custom": {
            "gear-builder": {"image": f"{fw_name}:{gear_version}_{bids_algo_version}"}
        },
        "version": f"{gear_version}_{bids_algo_version}",
    }


def get_latest_tag(username: Union[None, str], repo_name: str) -> str:
    """
    Fetches the latest tag for a given Docker Hub repository.

    Args:
        username (str): The Docker Hub username (dev) of the BIDS app.
        repo_name (str): The Docker Hub repository name of the BIDS app.

    Returns:
        str: The latest tag for the repository, or None if the fetch fails.
    """
    if username:
        url = f"https://hub.docker.com/v2/repositories/{username}/{repo_name}/tags/"
    else:
        url = f"https://hub.docker.com/v2/repositories_/{repo_name}/tags/"

    response = requests.get(url)
    if response.status_code == 200:
        tags = response.json().get("results", [])
        numeric_tags = [
            tag["name"]
            for tag in tags
            if str(tag["name"]).lower() != "latest" and is_numeric_version(tag["name"])
        ]
        try:
            return max(numeric_tags, key=lambda tag: parse_version(tag))
        except ValueError:
            log.error("%s does not have an official, numeric release", repo_name)
            return None
    else:
        print(f"Failed to fetch tags: HTTP {response.status_code}")
        return None


def get_script_path(script_name: str = "poetry_export.sh"):
    """Allow the python methods to find and run a shell script."""

    current_dir = Path(__file__).resolve().parent
    script_path = list(Path.rglob(current_dir, script_name))[0]
    return script_path


def is_numeric_version(version: str) -> bool:
    """
    Ensure that the returned tags follow semantic versioning.

    Args:
        version (str): semantic version to check
    """
    # This regex pattern matches versions like 1.0.0, 1.0, 1
    pattern = r"^\d+(\.\d+)*$"
    return bool(re.match(pattern, version))


def parse_version(version: str):
    """
    Means to compare numeric tag versions, when there are more than major versions to compare.
    """
    return tuple(map(int, version.split(".")))


def pull_latest_image(username: str, repo_name: str, tag: str):
    """
    Pulls the latest image using the Docker CLI.

    Args:
        username (str): The Docker Hub username.
        repo_name (str): The Docker Hub repository name.
        tag (str): The Docker image tag.

    Returns:
        None
    """
    try:
        subprocess.check_call(["docker", "pull", f"{username}/{repo_name}:{tag}"])
        print(f"Successfully pulled {tag} version.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to pull image: {e}")


def run_command(command: str) -> bool:
    """
    Runs a shell command.

    Args:
        command (str): The command to execute.

    Returns:
        Status of the run command (like result.returncode)

    Raises:
        Errors from the subprocess
    """
    try:
        subprocess.run(shlex.split(command), capture_output=True, check=True, text=True)
        log.info(f"Command executed successfully: {command}")
        return True
    except subprocess.CalledProcessError as e:
        log.error("Command failed: %s", e.stderr)
        raise


def update_json_file(json_file_path: Union[Path, str], updates: dict):
    """
    Updates a JSON file with new values.

    Args:
        json_file_path (str): The path to the JSON file to be updated.
        updates (dict): The updates to apply to the JSON file.

    Returns:
        None
    """
    with open(json_file_path, "r") as file:
        data = json.load(file)

    update_nested(data, updates)

    with open(json_file_path, "w") as file:
        json.dump(data, file, indent=4)


def update_nested(data: dict, updates: dict):
    """
    Handles nested entry updates for the manifest (or other) file(s).

    Updates in place.

    Args:
        data (dict): contents from a JSON, most likely
        updates (dict): fields and values to update in the data; these may be nested (e.g., "custom":{"gear-builder":"my_value"})
    """
    for key, value in updates.items():
        if isinstance(value, dict) and key in data and isinstance(data[key], dict):
            # If both value and data[key] are dictionaries, recurse
            update_nested(data[key], value)
        else:
            data[key] = value


def update_tag_in_dockerfile(
    dockerfile_path: Union[Path, str], new_tag: str
) -> Tuple[str, str, str]:
    """
    Updates the tag in a Dockerfile using information from extract_repo_from_dockerfile.

    Args:
        dockerfile_path (Union[Path, str]): The path to the Dockerfile.
        new_tag (str): The new tag to replace the existing one.

    Returns:
        tuple: A tuple containing the username, repository name, and updated tag.
    """
    dockerfile_path = Path(dockerfile_path)

    # Extract current information
    try:
        username, repo_name, old_tag = extract_repo_from_dockerfile(dockerfile_path)
    except ValueError as e:
        raise ValueError(f"Error extracting information from Dockerfile: {e}")

    updated_content = []
    from_line_updated = False

    # Regular expression to match the FROM line
    regex = r"^FROM\s+(\S+)"

    with open(dockerfile_path, "r") as file:
        for line in file:
            match = re.search(regex, line)
            if match and repo_name in line and not from_line_updated:
                # Keep the name of the stage if it exists
                as_stage = (
                    "AS " + line.lower().split(" as ")[-1]
                    if " as " in line.lower()
                    else ""
                )
                if username:
                    updated_line = (
                        f"FROM {username}/{repo_name}:{new_tag} {as_stage}"
                        if as_stage
                        else f"FROM {username}/{repo_name}:{new_tag}\n"
                    )
                else:
                    updated_line = (
                        f"FROM {repo_name}:{new_tag} {as_stage}"
                        if as_stage
                        else f"FROM {repo_name}:{new_tag}\n"
                    )
                updated_content.append(updated_line)
                from_line_updated = True
                log.debug(f"Updated FROM line: {updated_line.strip()}")
            else:
                updated_content.append(line)

    if from_line_updated:
        # Write the updated content back to the Dockerfile
        with open(dockerfile_path, "w") as file:
            file.writelines(updated_content)

        return username, repo_name, new_tag
    else:
        raise ValueError("Failed to update the FROM instruction in the Dockerfile")


def main(
    dockerfile_path: Union[Path, str] = "./Dockerfile",
    json_file_path: Union[Path, str] = "./manifest.json",
    run_after_updates: bool = False,
):
    """
    Main function to orchestrate the workflow of extracting, pulling, updating, and running commands based on Dockerfile and manifest.

    What does the autoupdater update?
    (1) The last stage of the Dockerfile/build to the most recently tagged release of the third-party algorithm (e.g., mriqc)
    (2) The manifest to match the latest release
    (3) poetry managed dependencies
    (4) requirements.txt and requirements-dev.txt files, which are installed during Docker builds

    What does autoupdater do from there?
    (1) Uses `fw-beta gear build` to test the Docker build and update the manifest
    (2) Sends the updated gear to the test instance that you are logged into
    (3) Launches an SDK-based gear run of the newly updated and uploaded gear
    (4) Waits for the gear run to succeed for fail
    (5) If the gear run was successful, runs git commands to make a branch and push changes so an MR can be staged.

    In the event that there are no detected updated versions, the autoupdater will exit without changing the gear at all. No git branches will be created either.

    Args:
        dockerfile_path (str, optional): Path to the Dockerfile. Defaults to ".Dockerfile".
        json_file_path (str, optional): Path to the JSON file containing the manifest. Defaults to ".manifest.json".
        run_after_updates (bool, optional): Whether to run the gear after updating and/OR debugging. Defaults to false.

    Returns:
        None
    """
    username, repo_name, tag = extract_repo_from_dockerfile(dockerfile_path)
    latest_tag = get_latest_tag(username, repo_name)
    if latest_tag and latest_tag != tag:
        # pull_latest_image(username, repo_name,latest_tag)
        # Update Docker
        update_tag_in_dockerfile(dockerfile_path, latest_tag)
        # Update manifest
        gear_name, gear_version = find_gear_details(json_file_path)
        updates = generate_updates_dictionary(gear_name, gear_version, latest_tag)
        update_json_file(json_file_path, updates)
        try:
            # Update dependencies to keep Flywheel deps current; make sure the req files are also updated to reflect poetry changes.
            run_command("poetry update")
            run_command(f"{get_script_path('poetry_export.sh')}")
            # Make sure that the manifest is updated and valid
            run_command("fw-beta gear build")
            # Send the updated gear to an instance
            run_command("fw-beta gear upload")
            run_after_updates = True
        except subprocess.CalledProcessError:
            log.error("Script execution failed due to a command error")
            return False
        except Exception as e:
            log.error("An unexpected error occurred: %s", str(e))
            return False
    else:
        log.info("Already up to date.")

    if run_after_updates:
        log.info("Running tests.")
        try:
            gear_name, gear_version = find_gear_details(json_file_path)
            # Make sure the updated gear runs
            run_command(f"poetry run python -m tests.platform_test {gear_name}")
            # Manage source control consistently
            target_branch = f"dev-update-v{latest_tag}"
            run_command(f"git checkout -b {target_branch}")
            run_command(f"git commit -a -m 'Update to {latest_tag}' -n")
            run_command("git push")
            log.info("Update complete. Submit MR on Gitlab for %s", target_branch)
            return True
        except subprocess.CalledProcessError:
            log.error("Script execution failed due to a command error")
            return False
        except Exception as e:
            log.error("An unexpected error occurred: %s", str(e))
            return False
    else:
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
