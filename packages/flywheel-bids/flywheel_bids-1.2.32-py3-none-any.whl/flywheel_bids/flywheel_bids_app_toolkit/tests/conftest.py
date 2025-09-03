from pathlib import Path
from unittest.mock import MagicMock

import flywheel
import pytest
from flywheel_gear_toolkit.testing.sdk import job

from flywheel_bids.flywheel_bids_app_toolkit.context import BIDSAppContext
from flywheel_bids.supporting_files.templates import Rule


@pytest.fixture
def mock_context(mocker):
    mocker.patch("flywheel_gear_toolkit.GearToolkitContext")
    gtk_context = MagicMock(autospec=True)
    return gtk_context


@pytest.fixture
def mock_template(mocker):
    mocker.patch("flywheel_bids.supporting_files.templates.Template")
    template = MagicMock(autospec=True)

    return template


@pytest.fixture
def mock_rule(mock_template):
    rule = Rule(
        {
            "id": "passport",
            "template": "test_curation_template",
            "where": {"file.info.ImageType": "P"},
            "initialize": {"Acq": {"$value": "abcdefg"}},
        }
    )
    return rule


@pytest.fixture
def mock_client(mocker):
    mocker.patch("flywheel.Client")
    fw = flywheel.Client(autospec=True)
    return fw


@pytest.fixture
def mock_job(mocker):
    return job(mocker)


@pytest.fixture
def extended_gear_context(mock_context, tmpdir):
    """Extend the basic GTK context for the BIDSApp context.

    To return the desired side effects for mock_context.config.get.side_effect,
    use `lambda key: (mock_dict}.get(key) in the test method. Implementing the
    lambda function at the test level will allow us to combine this test fixture
    with parametrize and change various values on the fly.
    """
    mock_context.get.side_effect = lambda key: {"parent_container_type": "project"}.get(
        key
    )
    mock_context.get_input.return_value = None
    mock_context.output_dir = Path(tmpdir)
    mock_context.work_dir = Path(tmpdir) / "work_dir"
    mock_context.destination = {"id": "output_destination_id"}
    mock_context.config.get.side_effect_dict = {
        "bids_app_command": "something_bids_related /path/1 /path/2 participant --extra_option extra_opt",
        "app-dry-run": True,
        "gear-save-intermediate-output": True,
        "gear-intermediate-files": "a b",
        "gear-intermediate-folders": "A_dir B_dir",
        "gear-dry-run": False,
        "gear-expose-all-outputs": True,
        "n_cpus": 1,
        "mem_mb": 1024,
    }
    mock_context.config.get.side_effect = (
        lambda key: mock_context.config.get.side_effect_dict.get(key, None)
    )
    mock_context.manifest.get.side_effect = lambda key: {
        "custom": {
            "bids-app-binary": "something_bids_related",
            "bids-app-data-types": ["modality1", "modality2"],
        }
    }.get(key)

    return mock_context


@pytest.fixture
def mock_app_context(extended_gear_context):
    return BIDSAppContext(extended_gear_context)
