import json
import time
from pathlib import Path
from typing import Union

import flywheel
import yaml


def find_api_key(data: Union[dict, list], key: str) -> str:
    """
    Search configurations for API key.

    Args:
        data (dict,list): contents of config file to search
        key (key): title of the field with the API key

    Returns:
        Flywheel API key to activate Client
    """

    if isinstance(data, dict):
        for k, value in data.items():
            if key in k.lower():
                return value
            result = find_api_key(value[0], key)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_api_key(item, key)
            if result:
                return result
    return None


def get_api() -> str:
    """
    Use local, developer settings to locate API key.

    Assumes that you are logged into a Flywheel test instance
    using either `fw-beta` or `fw`.

    Returns:
        Flywheel API key to activate Client
    """
    user_json = Path(Path.home() / ".config/flywheel/user.json")

    if user_json.exists():
        with open(user_json) as json_file:
            contents = json.load(json_file)
            return find_api_key(contents, "key")
    else:
        # more modern fw-beta method
        user_json = Path(Path.home() / ".fw/config.yml")
        if user_json.exists():
            with open(user_json) as yaml_file:
                contents = yaml.safe_load(yaml_file)
                return find_api_key(contents, "api_key")


def poll_job_state(
    fw: flywheel.Client, job_id: str, interval: int = 10, timeout: int = 600
):
    """
    Poll a command until its status is not "pending" or "running".

    Args:
        job_id (str): Flywheel Job ID for the test run
        interval (int): Time in seconds between each poll. Default is 5 seconds.
        timeout (int): Maximum time in seconds to poll before giving up. Default is 300 seconds (10 minutes).

    """
    start_time = time.time()

    while True:
        result = fw.get_job(job_id).state
        if result and not any(
            status in result.lower() for status in ["pending", "running"]
        ):
            return

        # Check if we've exceeded the timeout
        if time.time() - start_time > timeout:
            raise TimeoutError(
                f"Command status remained 'pending' for more than {timeout} seconds"
            )

        # Wait for the specified interval before polling again
        time.sleep(interval)


def parse_job_state(state: str) -> int:
    """
    Translate the job status to sys.exit code

    Args:
        state (str): job status from fw.get_job.state

    Returns
        integer of 0 (successful) or 1 (unsucessful)
    """
    if "complete" in state.lower():
        return 0
    else:
        return 1
