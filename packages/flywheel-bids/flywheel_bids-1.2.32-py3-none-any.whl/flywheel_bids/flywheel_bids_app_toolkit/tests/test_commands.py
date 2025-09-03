"""Module to test commands.py."""

from unittest.mock import Mock, patch

import pytest

from flywheel_bids.flywheel_bids_app_toolkit import BIDSAppContext
from flywheel_bids.flywheel_bids_app_toolkit.commands import (
    clean_generated_bids_command,
    generate_bids_command,
    run_bids_algo,
    validate_kwargs,
)


class MockBIDSAppContext(BIDSAppContext):
    def __init__(self, bids_app_binary, bids_app_options):
        self.bids_app_binary = bids_app_binary
        self.bids_app_options = bids_app_options


class MockZipFile:
    def __init__(self):
        self.files = []

    def __enter__(self):
        return Mock()

    def __exit__(self, *args, **kwargs):
        return Mock()

    def __iter__(self):
        return iter(self.files)

    def write(self, fname):
        self.files.append(fname)


# - when there are and when there aren't bids_app_args
@pytest.mark.parametrize(
    "bids_app_command", [None, "arg1 arg2 --my_arg aa1 aa2", "--work-dir"]
)
def test_generate_command(bids_app_command, extended_gear_context):
    """Unit tests for generate_command."""
    extended_gear_context.config.get.side_effect_dict["bids_app_command"] = (
        bids_app_command
    )
    extended_gear_context.config.get.side_effect = (
        lambda key: extended_gear_context.config.get.side_effect_dict.get(key)
    )
    mock_app_context = BIDSAppContext(extended_gear_context)
    cmd = generate_bids_command(mock_app_context)

    # Check that the returned cmd:
    # - is a list of strings:
    assert isinstance(cmd, list)
    assert all(isinstance(c, str) for c in cmd)
    # starts with the mandatory arguments:
    assert cmd[0:4] == [
        str(mock_app_context.bids_app_binary),
        str(mock_app_context.bids_dir),
        str(mock_app_context.analysis_output_dir),
        str(mock_app_context.analysis_level),
    ]

    # check that the bids_app_args are in the command:
    if bids_app_command:
        assert [arg in cmd for arg in bids_app_command.split()]


def test_clean_generated_command():
    cmd = ["--verbose=v", "--work-dir /path/to/work/dir", "--foo=bar fam", "----excess"]
    cmd = clean_generated_bids_command(cmd)
    assert cmd == [
        "-v",
        "--work-dir",
        "/path/to/work/dir",
        "--foo",
        "bar",
        "fam",
        "--excess",
    ]


@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.commands.exec_command",
    return_value=("--option1\n--option2\n--option3", "stderr", "exit_code"),
)
def test_validate_kwargs_catches_invalid(mock_exec):
    mock_app_context = MockBIDSAppContext(
        "/path/to/bids/app",
        {"option1": "value1", "option2": "value2", "invalid_option": "value"},
    )
    with pytest.raises(SystemExit) as excinfo:
        validate_kwargs(mock_app_context)

    assert (
        str(excinfo.value)
        == "Gear cannot run the algorithm with invalid arguments. Exiting."
    )


@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.commands.exec_command",
    return_value=("--option1\n--option2\n-o", "stderr", "exit_code"),
)
def test_validate_kwargs_passes(mock_exec, caplog):
    mock_app_context = MockBIDSAppContext(
        "/path/to/bids/app", {"option1": "value1", "option2": "value2", "-o": "value"}
    )
    validate_kwargs(mock_app_context)
    assert mock_exec.called
    assert len(caplog.messages) == 0


@patch("pathlib.Path.exists")
@patch("pathlib.Path.mkdir")
@patch("flywheel_bids.flywheel_bids_app_toolkit.commands.log.info")
@patch("flywheel_bids.flywheel_bids_app_toolkit.commands.exec_command")
def test_run_bids_algo(
    mock_exec_command,
    mock_log_info,
    mock_path_mkdir,
    mock_path_exists,
    extended_gear_context,
):
    extended_gear_context.bids_app_binary = "bids_app_binary"
    extended_gear_context.analysis_output_dir = "/path/to/analysis_output_dir"
    extended_gear_context.gear_dry_run = False
    command = ["command", "arg1", "arg2"]

    mock_path_exists.return_value = False
    mock_path_mkdir.return_value = None
    mock_log_info.return_value = None
    mock_exec_command.return_value = 0

    rc = run_bids_algo(extended_gear_context, command)

    assert rc == 0
    assert mock_path_exists.called
    mock_path_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_log_info.assert_called_once_with(
        "Creating output directory %s", "/path/to/analysis_output_dir"
    )
    mock_exec_command.assert_called_once_with(
        [*command], dry_run=False, shell=True, cont_output=False
    )
