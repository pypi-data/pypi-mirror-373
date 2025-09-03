from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from flywheel_bids.flywheel_bids_app_toolkit.report import (
    package_output,
    report_errors,
    report_warnings,
    save_metadata,
    walk_tree_to_find_dirs,
)


def test_report_errors():
    errors = [
        ValueError("Invalid value"),
        TypeError("Incorrect type"),
        "Custom error message",
    ]

    report = report_errors(errors)

    expected_message = (
        "Previous errors:\n"
        "  ValueError: Invalid value\n"
        "  TypeError: Incorrect type\n"
        "  Error msg: Custom error message\n"
    )
    assert report == expected_message


def test_warnings():
    warnings = ["don't slip and fall", "look up"]
    report = report_warnings(warnings)

    expected_msg = (
        "Previous warnings:\n  Warning: don't slip and fall\n  Warning: look up\n"
    )
    assert report == expected_msg


@patch("flywheel_bids.flywheel_bids_app_toolkit.report.Metadata")
@patch("builtins.open", new_callable=MagicMock)
@patch("pathlib.Path.exists", return_value=True)
def test_save_metadata_with_extra_info(
    mock_exists, mock_open, mock_Metadata, mock_context
):
    work_dir = Path("/tmp/workdir")
    bids_app_binary = "app"
    extra_info = {"key": "value"}

    # Mocking the open method to simulate reading a JSON file
    mock_open.return_value.__enter__.return_value.read.return_value = (
        '{"key": "original"}'
    )

    save_metadata(mock_context, work_dir, bids_app_binary, extra_info)

    mock_open.assert_called_once_with(
        work_dir / f"{bids_app_binary}.json", "r", encoding="utf8"
    )
    mock_Metadata.assert_called_once()
    mock_Metadata().add_gear_info.assert_called_once_with(
        "results", mock_context.destination["id"], key="value"
    )


@patch("flywheel_bids.flywheel_bids_app_toolkit.report.Metadata")
@patch("builtins.open", new_callable=MagicMock)
@patch("pathlib.Path.exists", return_value=False)
def test_save_metadata_without_analysis_output(
    mock_exists, mock_open, mock_Metadata, mock_context
):
    work_dir = Path("/tmp/workdir")
    bids_app_binary = "app"
    # No extra_info

    save_metadata(mock_context, work_dir, bids_app_binary)

    mock_open.assert_not_called()  # Open should not be called since the file doesn't exist
    mock_Metadata.assert_not_called()


@patch("flywheel_bids.flywheel_bids_app_toolkit.report.report_errors")
@patch("flywheel_bids.flywheel_bids_app_toolkit.report.zip_derivatives")
@patch("flywheel_bids.flywheel_bids_app_toolkit.report.zip_output")
@patch("flywheel_bids.flywheel_bids_app_toolkit.report.zip_htmls")
def test_package_output_zips_htmls_and_main_output(
    mock_zip_htmls, mock_zip_output, mock_zip_derivatives, mock_report, mock_app_context
):
    gear_name = "test_gear"
    errors = ["a useful error"]
    html_dir = (
        Path(mock_app_context.analysis_output_dir) / mock_app_context.bids_app_binary
    )
    html_dir.mkdir(parents=True, exist_ok=True)
    mock_app_context.post_processing_only = False
    mock_zip_htmls.return_value = None
    expected_output_calls = 1
    if mock_app_context.save_intermediate_files:
        expected_output_calls += 1
    if mock_app_context.save_intermediate_folders:
        expected_output_calls += 1

    package_output(mock_app_context, gear_name, errors)

    mock_zip_htmls.assert_any_call(
        str(mock_app_context.output_dir), mock_app_context.destination_id, html_dir
    )
    mock_zip_htmls.assert_any_call(
        str(mock_app_context.output_dir),
        mock_app_context.destination_id,
        mock_app_context.analysis_output_dir,
    )
    assert mock_zip_output.call_count == expected_output_calls
    mock_zip_derivatives.assert_called_once()
    mock_report.assert_called_once()


@pytest.fixture
def test_directory_structure(tmpdir):
    """Create a test directory structure for testing walk_tree_to_find_dirs function."""
    # Create directories and subdirectories
    dir1 = tmpdir.mkdir("dir1")
    dir1_subdir1 = dir1.mkdir("subdir1")
    dir1_subdir2 = dir1.mkdir("subdir2")
    dir2 = tmpdir.mkdir("dir2")
    dir2_subdir1 = dir2.mkdir("subdir1")

    return dir1, dir1_subdir1, dir1_subdir2, dir2, dir2_subdir1


@pytest.mark.parametrize(
    "patterns, expected_dirs",
    [
        (["dir*", "*subdir*"], 5),  # Match all directories and subdirectories
        (["dir*"], 2),  # Match only directories starting with "dir"
        (["*subdir*"], 3),  # Match only subdirectories containing "subdir"
    ],
)
def test_walk_tree_to_find_dirs(
    tmpdir, test_directory_structure, patterns, expected_dirs
):
    matching_dirs = walk_tree_to_find_dirs(tmpdir, patterns)

    assert len(matching_dirs) == expected_dirs

    # Check if the function returns the correct matching directories
    for dir_path in test_directory_structure:
        if any(Path(dir_path).match(pattern) for pattern in patterns):
            assert dir_path.strpath in matching_dirs
        else:
            assert dir_path.strpath not in matching_dirs
