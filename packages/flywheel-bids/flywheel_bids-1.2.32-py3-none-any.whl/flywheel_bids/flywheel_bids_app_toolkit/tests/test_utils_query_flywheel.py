import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from flywheel import ApiException
from importlib_resources import files

from flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel import (
    copy_bidsignore_file,
    download_bids_data_for_run_level,
    get_fw_details,
    list_existing_dirs,
    list_reqd_folders,
    orchestrate_download_bids,
)
from flywheel_bids.supporting_files.errors import BIDSExportError

BIDS_PATH = files("tests.assets").joinpath("dataset")

hierarchy = {
    "run_level": "a_hierarchy_value",
    "run_label": "unknown",
    "group": None,
    "project_label": None,
    "subject_label": None,
    "session_label": None,
    "acquisition_label": None,
}


@pytest.mark.parametrize(
    "bidsignore_condition, copied_file",
    [("use", ".bidsignore"), ("skip", "found.bidsignore")],
)
def test_copy_bidsignore_file(bidsignore_condition, copied_file, tmp_path):
    # Set up dummy file
    input_dir = Path(tmp_path) / "input"
    input_dir.mkdir(parents=True)
    bidsignore = None
    if bidsignore_condition == "use":
        bidsignore = input_dir / copied_file
        bidsignore.touch()
    else:
        tmp_file = input_dir / copied_file
        tmp_file.touch()

    copy_bidsignore_file(BIDS_PATH, input_dir, bidsignore)
    expected_result = Path(BIDS_PATH) / ".bidsignore"

    assert expected_result.exists()

    # Clean-up
    os.remove(expected_result)


class TestDownloadBidsDataForRunLevel:
    @patch(
        "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.list_existing_dirs"
    )
    def test_project_subject_session(self, mock_list_existing_dirs, mock_context):
        mock_hierarchy = {
            "run_level": "project",
            "run_label": "proj1",
            "subject": "sub1",
            "session": "ses1",
        }
        mock_folders = ["folder1", "folder2"]
        mock_src_data = MagicMock()
        mock_context.download_project_bids.return_value = Path(
            "/whatever/BIDS/dir/should/be/here/bids"
        )
        mock_list_existing_dirs.return_value = (["folder1"], mock_folders)

        result, err_code = download_bids_data_for_run_level(
            mock_context, "project", mock_hierarchy, mock_folders, mock_src_data, False
        )

        assert isinstance(result, Path)
        assert result.name == "bids"
        assert err_code is None

    @patch(
        "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.download_bids_dir"
    )
    def test_acquisition(self, mock_download_bids_dir, mock_context):
        mock_hierarchy = {"run_level": "acquisition", "acquisition_label": "acq1"}
        mock_folders = ["folder1", "folder2"]
        mock_src_data = MagicMock()

        result, err_code = download_bids_data_for_run_level(
            mock_context,
            "acquisition",
            mock_hierarchy,
            mock_folders,
            mock_src_data,
            False,
        )

        assert isinstance(result, Path)
        assert result.name == "bids"
        assert err_code is None

    def test_invalid_run_level(self, mock_context):
        mock_hierarchy = {"run_level": "invalid"}

        result, err_code = download_bids_data_for_run_level(
            mock_context, "invalid", mock_hierarchy, [], None, False
        )

        assert result is None
        assert err_code == 20


def test_get_fw_details(extended_gear_context):
    extended_gear_context.manifest.get.side_effect = lambda key: {
        "custom": {"gear-builder": {"image": "flywheel/bids-qsiprep:0.0.1_0.15.1"}}
    }.get(key)
    extended_gear_context.client.get.side_effect = MagicMock()
    destination, gear_builder_info, container = get_fw_details(extended_gear_context)
    assert isinstance(destination, MagicMock)
    assert isinstance(gear_builder_info, dict)
    assert isinstance(container, str)


def test_list_existing_dirs_finds_specific_dirs(tmpdir):
    bids_dir = tmpdir.mkdir("bids")
    # Add an extra folder that will be filtered out
    folders = ["anat", "fmap", "perf"]
    dirList = []
    for i, folder in enumerate(folders):
        vars()["dir%s" % i] = bids_dir.mkdir(folder)
        dirList.append(vars()["dir%s" % i])

    folders.append("extraneous")
    result_existing, result_reqd = list_existing_dirs(bids_dir, folders=folders)

    assert len(result_existing) == len(result_reqd)
    assert all([d.exists() for d in dirList])
    assert "extraneous" not in result_existing


def test_list_existing_dirs_reports_missing_dirs(tmpdir):
    bids_dir = tmpdir.mkdir("bids")
    # Add an extra folder that will be filtered out
    folders = ["anat", "fmap", "perf", "unknown_suffix"]
    for f in folders:
        bids_dir.mkdir(f)

    result_existing, result_reqd = list_existing_dirs(bids_dir)

    assert len(result_existing) == 3
    assert (
        len(result_reqd) == 5
    )  # Total number of suffixes available for curation in Flywheel


@pytest.mark.parametrize(
    "in_set, expected_set",
    [
        (["anat", "fmap", "perf", "unknown_suffix"], ["anat", "fmap", "perf"]),
        (None, ["anat", "func", "dwi", "fmap", "perf"]),
    ],
)
def test_list_reqd_folders(in_set, expected_set):
    if in_set:
        result = list_reqd_folders(folders=in_set)
    else:
        result = list_reqd_folders()

    assert sorted(result) == sorted(expected_set)


@patch("flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.tree_bids")
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.validate_bids",
    return_value=0,
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.copy_bidsignore_file"
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.download_bids_data_for_run_level"
)
def test_orchestrate_download_bids_succeeds(
    mock_download, mock_copybids, mock_validate, mock_tree, mock_context
):
    # Fake a download location
    bids_dir = mock_context.work_dir / "bids"
    Path(bids_dir).mkdir(parents=True, exist_ok=True)
    mock_download.return_value = (bids_dir, 0)
    err_code = orchestrate_download_bids(
        mock_context,
        hierarchy,
        tree=True,
        tree_title="Sycamore",
        skip_download=True,
        do_validate_bids=True,
    )
    assert err_code == 0
    mock_download.assert_called_once()
    mock_validate.assert_called_once()
    mock_tree.assert_called_once()


@patch("flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.tree_bids")
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.validate_bids",
    return_value=0,
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.copy_bidsignore_file"
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.download_bids_data_for_run_level"
)
def test_orchestrate_download_bids_no_validation(
    mock_download, mock_copybids, mock_validate, mock_tree, mock_context
):
    # Fake a download location
    bids_dir = mock_context.work_dir / "bids"
    Path(bids_dir).mkdir(parents=True, exist_ok=True)
    mock_download.return_value = (bids_dir, 0)
    err_code = orchestrate_download_bids(
        mock_context,
        hierarchy,
        tree=True,
        tree_title="Sycamore",
        skip_download=True,
        do_validate_bids=False,
    )
    assert err_code == 0
    mock_download.assert_called_once()
    assert mock_validate.call_count == 0
    mock_tree.assert_called_once()


@patch("flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.tree_bids")
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.validate_bids",
    side_effect=Exception,
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.copy_bidsignore_file"
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.download_bids_data_for_run_level"
)
def test_orchestrate_download_bids_validationException(
    mock_download, mock_copybids, mock_validate, mock_tree, mock_context
):
    # Fake a download location
    bids_dir = mock_context.work_dir / "bids"
    Path(bids_dir).mkdir(parents=True, exist_ok=True)
    mock_download.return_value = (bids_dir, 0)
    err_code = orchestrate_download_bids(
        mock_context,
        hierarchy,
        tree=True,
        tree_title="Sycamore",
        skip_download=True,
        do_validate_bids=True,
    )
    assert err_code == 22
    mock_download.assert_called_once()
    mock_validate.assert_called_once()
    mock_tree.assert_called_once()


@patch("flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.tree_bids")
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.validate_bids",
    return_value=0,
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.copy_bidsignore_file"
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.download_bids_data_for_run_level"
)
def test_orchestrate_download_bids_no_data(
    mock_download, mock_copybids, mock_validate, mock_tree, mock_context
):
    # Fake a download location
    bids_dir = mock_context.work_dir / "bids"
    # Don't make the location
    mock_download.return_value = (bids_dir, 0)
    err_code = orchestrate_download_bids(
        mock_context,
        hierarchy,
        tree=True,
        tree_title="Sycamore",
        skip_download=True,
        do_validate_bids=True,
    )
    assert err_code == 26
    mock_download.assert_called_once()
    mock_tree.assert_called_once()


@patch("flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.tree_bids")
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.validate_bids",
    return_value=0,
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.copy_bidsignore_file"
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.download_bids_data_for_run_level"
)
def test_orchestrate_download_bids_BIDSExportException(
    mock_download, mock_copybids, mock_validate, mock_tree, mock_context
):
    # Fake a download location
    bids_dir = mock_context.work_dir / "bids"
    Path(bids_dir).mkdir(parents=True, exist_ok=True)
    mock_download.side_effect = BIDSExportError
    err_code = orchestrate_download_bids(
        mock_context,
        hierarchy,
        tree=True,
        tree_title="Sycamore",
        skip_download=True,
        do_validate_bids=True,
    )
    assert err_code == 21
    mock_download.assert_called_once()


@patch("flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.tree_bids")
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.validate_bids",
    return_value=0,
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.copy_bidsignore_file"
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.download_bids_data_for_run_level"
)
def test_orchestrate_download_bids_api_exception(
    mock_download, mock_copybids, mock_validate, mock_tree, mock_context
):
    # Fake a download location
    bids_dir = mock_context.work_dir / "bids"
    Path(bids_dir).mkdir(parents=True, exist_ok=True)
    mock_download.side_effect = ApiException
    err_code = orchestrate_download_bids(
        mock_context,
        hierarchy,
        tree=True,
        tree_title="Sycamore",
        skip_download=True,
        do_validate_bids=True,
    )
    assert err_code == 25
    mock_download.assert_called_once()


@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.download_bids_data_for_run_level"
)
def test_orchestrate_download_bids_no_destination(mock_download, mock_context):
    test_hierarchy = hierarchy.copy()
    test_hierarchy["run_level"] = "no_destination"
    err_code = orchestrate_download_bids(mock_context, test_hierarchy)
    assert err_code == 24
    mock_download.assert_not_called()


# @patch("flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.Client")
# def test_find_associated_bids_acqs(mock_client_instance):
#     mock_api_key = {"key": "mock_api_key:part2"}
#     mock_destination = MagicMock()
#     mock_destination.id = "mock_destination_id"
#     mock_destination.parents = {"project":'1234'}
#     mock_destination.parent.type = "project"
#     mock_acquisition = MagicMock()
#     mock_files = [{"info": {"BIDS": True}}]
#     mock_acquisition.files.return_value = mock_files

#     mock_client_instance.return_value.get.return_value = mock_destination
#     mock_client_instance.acquisitions = Mock()
#     mock_client_instance.acquisitions.iter_find.side_effect = [mock_acquisition]

#     gear_context = MagicMock(get_input=lambda x: mock_api_key, destination=mock_destination)
#     result = find_associated_bids_acqs(gear_context)

#     assert len(result) == 1
#     assert isinstance(result[0], type(mock_acquisition))
#     mock_client_instance.assert_called_once_with(mock_api_key["key"])


# # Additional test case for when no BIDS acquisitions are found
# @patch("flywheel_bids.flywheel_bids_app_toolkit.utils.query_flywheel.Client")
# def test_find_associated_bids_acqs_no_bids(mock_client):
#     mock_files = [{"info": {}}]  # No BIDS info
#     fw_acquisition.files.return_value = mock_files

#     gear_context = MagicMock(get_input=lambda x: mock_api_key, destination=mock_destination)
#     result = find_associated_bids_acqs(gear_context)

#     assert len(result) == 0
