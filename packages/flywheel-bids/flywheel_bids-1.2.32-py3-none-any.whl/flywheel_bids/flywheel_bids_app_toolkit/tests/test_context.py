from pathlib import Path
from unittest.mock import patch

import pytest

from flywheel_bids.flywheel_bids_app_toolkit import BIDSAppContext
from flywheel_bids.flywheel_bids_app_toolkit.context import parse_unknown_args


@pytest.mark.parametrize(
    "args,expected",
    [
        (
            [
                "--ignore",
                "slicetiming",
                "--output-spaces",
                "MNIPediatricAsym:cohort-1:cohort-2:res-native:res-1",
                "T1w",
                "fsnative",
                "--skip-bids-validation",
            ],
            {
                "ignore": "slicetiming",
                "output-spaces": "MNIPediatricAsym:cohort-1:cohort-2:res-native:res-1 T1w fsnative",
                "skip-bids-validation": True,
            },
        ),
        (
            ["--arg1", "value1", "--arg2", "value2"],
            {"arg1": "value1", "arg2": "value2"},
        ),
        (["--arg1", "value1", "arg2"], {"arg1": "value1 arg2"}),
        (["arg1", "--arg2", "value2"], {"arg2": "value2"}),
        (["--arg1", "value1", "-Z"], {"arg1": "value1", "Z": True}),
        (["d", "-a", "value1", "--b", "-c"], {"a": "value1", "b": True, "c": True}),
        ([], {}),
    ],
)
def test_parse_args(args, expected):
    result = parse_unknown_args(args)
    assert result == expected


@pytest.mark.parametrize(
    "archived_files, extra_args, expected_bids_dir, expected_unzip_count",
    [
        (None, None, "work_dir/bids", 0),
        ("/a/tar.zip", None, Path("/a/tar"), 1),
        ("/another/archive", None, Path("/another/archive"), 0),
        (None, {"n_cpus": 6}, "work_dir/bids", 0),
        (
            "/a/tar/for/post_processing.zip",
            {"gear-post-processing-only": True},
            Path("/a/tar/for/post_processing"),
            1,
        ),
    ],
)
def test_BIDSAppContext(
    archived_files,
    extra_args,
    expected_bids_dir,
    expected_unzip_count,
    extended_gear_context,
    tmpdir,
):
    extended_gear_context.get_input_path.return_value = archived_files
    if extra_args:
        extended_gear_context.get_input.side_effect = lambda key: extra_args.get(key)
        extended_gear_context.get_input.return_value = "value"
    extended_gear_context.config.get.side_effect = (
        lambda key: extended_gear_context.config.get.side_effect_dict.get(key)
    )
    if not archived_files:
        expected_bids_dir = Path(tmpdir) / expected_bids_dir

    with patch(
        "flywheel_bids.flywheel_bids_app_toolkit.context.unzip_archive_files",
        return_value=expected_bids_dir,
    ) as unzip:
        # Create an instance of the BIDSAppContext class
        bids_app_context = BIDSAppContext(extended_gear_context)

    # Test the initialization of the BIDSAppContext object
    assert bids_app_context.destination_id == "output_destination_id"
    assert bids_app_context.analysis_level == "participant"
    assert bids_app_context.bids_app_binary == "something_bids_related"
    assert bids_app_context.bids_app_data_types == ["modality1", "modality2"]
    assert bids_app_context.bids_app_dry_run is True
    assert bids_app_context.bids_app_options.get("extra_option")

    # Test the parsing of directory settings
    assert bids_app_context.output_dir == Path(tmpdir)
    assert bids_app_context.work_dir == Path(tmpdir) / "work_dir"
    assert bids_app_context.bids_dir == expected_bids_dir

    # Test the parsing of run settings
    assert bids_app_context.save_intermediate_output is True
    assert bids_app_context.gear_dry_run is False
    assert bids_app_context.keep_output is True

    # Test the log file output location
    assert bids_app_context.output_log_file == bids_app_context.output_dir / Path(
        str(bids_app_context.bids_app_binary) + "_log.txt"
    )

    # Test the analysis output dir
    assert bids_app_context.analysis_output_dir == Path(
        bids_app_context.output_dir
    ) / Path(bids_app_context.destination_id)

    assert unzip.call_count == expected_unzip_count


def test_BIDSAppContext_exits_for_no_archive(extended_gear_context):
    extended_gear_context.get_input_path.return_value = None
    extended_gear_context.config.get.side_effect = lambda key: {
        "gear-post-processing-only": True
    }
    with pytest.raises(SystemExit):
        BIDSAppContext(extended_gear_context)
