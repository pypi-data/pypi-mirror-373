import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from flywheel_bids.flywheel_bids_app_toolkit.hpc_utils import (
    check_and_link_dirs,
    check_container_type,
    create_symlink_for_singularity,
    is_directory_writable,
    reset_FS_subj_paths,
    search_environ,
)


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("SUBJECTS_DIR", "/opt/freesurfer/subjects")


@pytest.fixture
def source_dir_and_link_name(tmp_path):
    """
    Pytest fixture that returns a tuple of source_dir and link_name using tmp_path.
    """
    source_dir = tmp_path / "source_dir"
    link_name = tmp_path / "link_name"
    return source_dir, link_name


def test_singularity_environment():
    with patch.dict(os.environ, {"SINGULARITY_ENVIRONMENT": ""}):
        assert check_container_type() == "Singularity"


def test_docker_host():
    with patch.dict(os.environ, {"DOCKER_HOST": ""}):
        assert check_container_type() == "Docker"


def test_no_container():
    with patch.dict(os.environ, {}):
        assert check_container_type() == "Not a container"


def test_reset_FS_subj_paths_updates_env(mock_env, tmp_path):
    gear_context = MagicMock(writable_dir=tmp_path)
    reset_FS_subj_paths(gear_context)
    assert os.environ["SUBJECTS_DIR"] == str(tmp_path) + "/freesurfer/subjects"


def test_reset_FS_subj_paths_creates_directories_and_symlinks(mock_env, tmp_path):
    gear_context = MagicMock(writable_dir=tmp_path)
    reset_FS_subj_paths(gear_context)
    subjects_dir = Path(tmp_path) / "freesurfer/subjects"
    assert subjects_dir.exists()
    assert (subjects_dir / "fsaverage").is_symlink()
    assert (subjects_dir / "fsaverage5").is_symlink()
    assert (subjects_dir / "fsaverage6").is_symlink()


@pytest.mark.parametrize(
    "work_dir_writable, subjects_dir, expected_tmp_dir, expected_reset_fs",
    [
        (True, None, None, False),
        (False, None, "/tmp/workspace", False),
        (True, "/freesurfer/subjects", None, True),
        (False, "/freesurfer/subjects", "/tmp/workspace", True),
    ],
)
def test_check_and_link_dirs(
    work_dir_writable,
    subjects_dir,
    expected_tmp_dir,
    expected_reset_fs,
    mock_context,
    tmp_path,
):
    mock_context.work_dir = tmp_path
    mock_context.tmp_dir = None
    with patch(
        "flywheel_bids.flywheel_bids_app_toolkit.hpc_utils.is_directory_writable",
        return_value=work_dir_writable,
    ):
        with patch(
            "flywheel_bids.flywheel_bids_app_toolkit.hpc_utils.create_temp_workspace",
            return_value="/tmp/workspace",
        ):
            with patch(
                "flywheel_bids.flywheel_bids_app_toolkit.hpc_utils.reset_FS_subj_paths"
            ) as mock_reset_fs:
                if subjects_dir:
                    os.environ["SUBJECTS_DIR"] = subjects_dir
                else:
                    os.environ.pop("SUBJECTS_DIR", None)

                check_and_link_dirs(mock_context)

                if expected_tmp_dir:
                    assert mock_context.writable_dir == expected_tmp_dir
                else:
                    assert "writable_dir" not in mock_context

                if expected_reset_fs:
                    mock_reset_fs.assert_called_once_with(mock_context)
                else:
                    mock_reset_fs.assert_not_called()


@patch("flywheel_bids.flywheel_bids_app_toolkit.hpc_utils.os.symlink")
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.hpc_utils.os.path.islink",
    return_value=False,
)
def test_create_symlink_for_singularity_runs(
    mock_ispath, mock_symlink, source_dir_and_link_name
):
    source_dir, link_name = source_dir_and_link_name
    source_dir.mkdir(parents=True)
    link_name.mkdir(parents=True)
    expected_link_path = str(link_name)

    mock_symlink.side_effect = lambda *args, **kwargs: None

    create_symlink_for_singularity(source_dir, link_name)

    mock_symlink.assert_called_once_with(source_dir, expected_link_path)


def test_create_symlink_for_singularity_raisesError(source_dir_and_link_name):
    source_dir, link_name = source_dir_and_link_name

    mock_symlink = MagicMock()

    with pytest.raises(FileNotFoundError):
        with patch(
            "flywheel_bids.flywheel_bids_app_toolkit.hpc_utils.os.symlink",
            new=mock_symlink,
        ):
            create_symlink_for_singularity(source_dir, link_name)


def test_writable_directory():
    with tempfile.TemporaryDirectory() as tmp_dir:
        assert is_directory_writable(tmp_dir)


def test_unwritable_directory():
    # Use a path that doesn't exist or is known to be unwritable
    unwritable_path = "/nonexistent/path/to/test"
    assert not is_directory_writable(unwritable_path)


def test_exception_handling(caplog):
    dir_path = "/path/to/some/directory"
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        assert not is_directory_writable(dir_path)
    assert ("Failed to write to directory: Permission denied") in caplog.messages


@pytest.fixture
def mock_filesystem():
    filesystem = {
        "/path/to/source": True,
        "/path/to/target": False,
        "/path/to/existing_link": True,
        "/path/to/existing_dir": True,
        "/nonexistent/source": False,
    }
    return filesystem


@pytest.fixture
def mock_links():
    links = {
        "/path/to/existing_link": "/path/to/existing_link",
        "/path/to/existing_dir": "/path/to/existing_dir",
    }
    return links


@pytest.mark.parametrize(
    "source_dir,target_dir,expected_behavior",
    [
        ("/path/to/source", "/path/to/target", "create_symlink"),
        ("/path/to/source", "/path/to/existing_link", "log"),
        ("/nonexistent/source", "/path/to/target", "raise_error"),
        ("/path/to/error/source", "/path/to/target", "raise_error"),
        ("/path/to/source", "/path/to/existing_dir", "log"),
    ],
)
def test_create_symlink_for_singularity(
    source_dir, target_dir, expected_behavior, mock_filesystem, mock_links, caplog
):
    def mock_exists(path):
        return mock_filesystem.get(path, False)

    def mock_islink(path):
        return mock_links.get(path, None)

    def mock_symlink(src, dst):
        if "error" in src:
            raise OSError("Mock symlink error")
        mock_filesystem[dst] = True

    with (
        patch("os.path.exists", side_effect=mock_exists),
        patch("os.path.islink", side_effect=mock_islink),
        patch("os.symlink", side_effect=mock_symlink),
    ):
        if expected_behavior == "raise_error":
            with pytest.raises((FileNotFoundError, OSError)):
                create_symlink_for_singularity(source_dir, target_dir)
        elif expected_behavior == "create_symlink":
            create_symlink_for_singularity(source_dir, target_dir)
            assert mock_filesystem[target_dir]  # Check if symlink was created
        elif expected_behavior == "log":
            create_symlink_for_singularity(source_dir, target_dir)
            assert mock_islink(target_dir)  # Check if it's still a symlink
            assert "already exists" in caplog.records[0].message


def test_create_symlink_for_singularity_real_fs(tmp_path):
    source_dir = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_dir.mkdir()

    create_symlink_for_singularity(str(source_dir), str(target_dir))
    assert target_dir.is_symlink()
    assert target_dir.resolve() == source_dir.resolve()


def test_create_symlink_for_singularity_raisesFileNotFound():
    with pytest.raises(FileNotFoundError):
        create_symlink_for_singularity("/nonexistent/source", "/some/target")


def test_find_bids_related_dirs():
    pass


@pytest.fixture
def mock_environ(monkeypatch):
    mock_env = {
        "AFNI_DIR": "/opt/afni",
        "AFNI_IMSAVE_WARNINGS": "NO",
        "AFNI_MODELPATH": "/opt/afni/models",
        "PATH": "/usr/local/bin:/usr/bin",
        "HOME": "/home/user",
        "PYTHON_VERSION": "3.9.5",
    }
    monkeypatch.setattr("os.environ", mock_env)


@pytest.mark.parametrize(
    "substrings, expected_count, expected_keys",
    [
        (["AFNI"], 3, ["AFNI_DIR", "AFNI_IMSAVE_WARNINGS", "AFNI_MODELPATH"]),
        (
            ["AFNI", "PATH"],
            4,
            ["AFNI_DIR", "AFNI_IMSAVE_WARNINGS", "AFNI_MODELPATH", "PATH"],
        ),
        (["NONEXISTENT"], 0, []),
        (
            ["afni", "path"],
            4,
            ["AFNI_DIR", "AFNI_IMSAVE_WARNINGS", "AFNI_MODELPATH", "PATH"],
        ),
        ([], 0, []),
        (["PYTHON"], 1, ["PYTHON_VERSION"]),
    ],
)
def test_search_environ(mock_environ, substrings, expected_count, expected_keys):
    result = search_environ(substrings)
    assert len(result) == expected_count
    assert all(key in result for key in expected_keys)
