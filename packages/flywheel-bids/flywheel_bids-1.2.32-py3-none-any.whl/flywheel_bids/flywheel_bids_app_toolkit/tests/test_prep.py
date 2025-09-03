from unittest.mock import patch

import pytest

from flywheel_bids.flywheel_bids_app_toolkit.prep import (
    get_bids_data,
    set_participant_info_for_command,
)


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("SUBJECTS_DIR", "/opt/freesurfer/subjects")


def test_set_participant_info_for_command(mock_app_context):
    participant_info = {
        "subject_label": "sub-01",
        "session_label": "ses-01",
        "run_label": "run-01",
        "valueless_key": None,
    }

    set_participant_info_for_command(mock_app_context, participant_info)

    assert mock_app_context.subject_label == "01"
    assert mock_app_context.session_label == "ses-01"
    assert mock_app_context.run_label == "run-01"
    assert not hasattr(mock_app_context, "valueless_key")


@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.prep.orchestrate_download_bids",
    return_value=0,
)
@patch(
    "flywheel_bids.flywheel_bids_app_toolkit.prep.get_analysis_run_level_and_hierarchy"
)
def test_get_bids_data(mock_hierarchy, mock_orchestrate, mock_context, mock_client):
    bids_suffixes = ["T1w", "T2w"]
    tree_title = "Test BIDS Tree"
    subject_label = "test_subject"
    session_label = "test_session"
    mock_hierarchy.return_value = {
        "run_level": "a_hierarchy_value",
        "run_label": "unknown",
        "group": None,
        "project_label": None,
        "subject_label": subject_label,
        "session_label": session_label,
        "acquisition_label": None,
    }
    result, errors = get_bids_data(
        mock_context, mock_hierarchy, bids_suffixes, tree_title
    )

    assert result["subject_label"] == subject_label
    assert result["session_label"] == session_label
    assert isinstance(result["run_label"], str)
    assert len(errors) == 0
