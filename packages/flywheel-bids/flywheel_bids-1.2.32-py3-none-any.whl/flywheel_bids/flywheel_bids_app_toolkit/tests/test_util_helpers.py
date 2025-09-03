from pathlib import Path
from unittest.mock import patch

import pytest

from flywheel_bids.flywheel_bids_app_toolkit.utils.helpers import (
    create_analysis_output_dir,
    determine_dir_structure,
    find_BIDS_algo_results_dir,
    make_dirs_and_files,
    reconcile_existing_and_unzipped_files,
    split_extension,
)


def test_create_analysis_output_dir(tmp_path, extended_gear_context):
    test_path = Path(tmp_path) / "output"
    extended_gear_context.analysis_output_dir = test_path

    create_analysis_output_dir(extended_gear_context)

    assert test_path.exists()


def test_determine_dir_structure(caplog, tmp_path):
    # Create files and subdirectories
    (tmp_path / "subdir1").mkdir()
    (tmp_path / "subdir2").mkdir()
    (tmp_path / "file1.txt").write_text("This is file 1")
    (tmp_path / "subdir1" / "file2.txt").write_text("This is file 2")
    (tmp_path / "subdir2" / "file3.txt").write_text("This is file 3")
    caplog.set_level("DEBUG")
    determine_dir_structure(str(tmp_path))

    # Get the captured log output
    log_output = {record.getMessage() for record in caplog.records}

    # Assert the expected output
    assert log_output == {
        str(tmp_path / "file1.txt"),
        str(tmp_path / "subdir1" / "file2.txt"),
        str(tmp_path / "subdir2" / "file3.txt"),
    }


@pytest.mark.parametrize(
    "filename, expected_name, expected_ext",
    [
        ("a.nii", "a", ".nii"),
        ("/try/path/b.nii.gz", "b", ".nii.gz"),
        ("c.dicom.zip.extra.suffixes", "c", ".dicom.zip.extra.suffixes"),
    ],
)
def test_split_extension(filename, expected_name, expected_ext):
    result_name, result_ext = split_extension(filename)
    assert result_name == expected_name
    assert result_ext == expected_ext


def test_make_dirs_and_files(tmp_path):
    files = ["path/to/file1.txt", "path/to/file2.txt", "path/to/dir/file3.txt"]
    paths = [tmp_path / file for file in files]

    make_dirs_and_files(paths)

    for path in paths:
        assert path.exists()


def test_make_dirs_and_files_with_path_objects(tmp_path):
    files = [
        Path("../../tests/path/to/file1.txt"),
        Path("../../tests/path/to/file2.txt"),
        Path("../../tests/path/to/dir/file3.txt"),
    ]

    make_dirs_and_files(files)

    for file in files:
        assert file.exists()


def test_find_analysis_dir_single_directory(tmp_path):
    destination_id = "gobble_t_gook"
    test_dir = tmp_path / f"test_dir_{destination_id}"
    test_dir.mkdir(parents=True, exist_ok=True)

    result = find_BIDS_algo_results_dir(destination_id, tmp_path)

    assert result == test_dir


def test_find_analysis_dir_multiple_directories(tmp_path):
    destination_id = "here_be_the_test"
    test_dir1 = tmp_path / f"test_{destination_id}/dir1"
    test_dir2 = tmp_path / f"test_{destination_id}/dir2"
    test_dir1.mkdir(parents=True, exist_ok=True)
    test_dir2.mkdir(parents=True, exist_ok=True)

    result = find_BIDS_algo_results_dir(destination_id, tmp_path)
    assert result == tmp_path / f"test_{destination_id}"


def test_find_analysis_dir_no_match(tmp_path):
    destination_id = "mismatch"
    test_dir1 = tmp_path / "test_missing_dir1"
    test_dir2 = tmp_path / "test_missing_dir2"
    test_dir1.mkdir(parents=True, exist_ok=True)
    test_dir2.mkdir(parents=True, exist_ok=True)

    with pytest.raises(ValueError, match="Did not find a folder matching"):
        find_BIDS_algo_results_dir(destination_id, tmp_path)


@patch("flywheel_bids.flywheel_bids_app_toolkit.utils.helpers.log")
@patch("flywheel_bids.flywheel_bids_app_toolkit.utils.helpers.shutil")
@patch("flywheel_bids.flywheel_bids_app_toolkit.utils.helpers.Path")
def test_move_files(mock_path, mock_shutil, mock_log, tmpdir):
    target_dir = tmpdir
    unzip_dir = Path(tmpdir) / "unzip_dir"
    unzip_dir.mkdir(exist_ok=True)
    for i in range(1, 3):
        dummy_file = unzip_dir / f"dummy_file{i}.txt"
        # Create the dummy file
        dummy_file.touch()

    mock_path.return_value = target_dir

    reconcile_existing_and_unzipped_files(target_dir, unzip_dir)

    mock_shutil.move.assert_any_call(dummy_file, target_dir / dummy_file.name)

    mock_log.info.assert_not_called()
    for i in range(1, 3):
        filename = f"dummy_file{i}.txt"
        mock_log.debug.assert_any_call(
            "Moving %s to %s", filename, target_dir / filename
        )
