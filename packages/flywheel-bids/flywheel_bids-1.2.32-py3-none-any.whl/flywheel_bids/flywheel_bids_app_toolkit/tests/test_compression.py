import datetime
import fnmatch
import shutil
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import pytest

from flywheel_bids.flywheel_bids_app_toolkit.compression import (
    change_to_relative_dir,
    parse_BIDS_suffix,
    prepend_index_filename,
    search_for_html_report_files,
    unzip_archive_files,
    walk_tree_to_exclude,
    zip_derivatives,
    zip_html_and_svg_files,
    zip_htmls,
)
from flywheel_bids.flywheel_bids_app_toolkit.utils.helpers import make_dirs_and_files


def test_change_to_relative_dir(tmpdir):
    html_filename = "test.html"
    html_path = Path(tmpdir) / html_filename
    html_path.touch()

    result_dir, result_html_name = change_to_relative_dir(tmpdir, html_path)

    assert result_dir == "."
    assert result_html_name == html_path


@pytest.mark.parametrize(
    "file_name, expected_suffix",
    [
        ("sub-01_task-rest_bold.nii.gz", "_bold"),
        ("sub-01_T1w.nii.gz", "_T1w"),
        ("sub-01_task-task_run-1_bold.nii.gz", "_bold"),
        ("sub-01-incorrect-format.nii.gz", None),
        ("sub-01_T2w.nii.gz", "_T2w"),
    ],
)
def test_parse_BIDS_suffix(file_name, expected_suffix):
    assert parse_BIDS_suffix(file_name) == expected_suffix


def test_prepend_index_filename(tmp_path):
    test_file = tmp_path / "test_ix_file.txt"
    test_file.touch()

    updated_filename = prepend_index_filename(test_file)

    expected_filename = (
        f"{tmp_path}/{datetime.datetime.now().strftime('%Y-%m-%d_%H')}_test_ix_file.txt"
    )
    assert str(updated_filename) == expected_filename


def test_walk_tree_to_exclude(tmp_path):
    files = [
        Path("bids/gear/analysis/out.txt"),
        Path("bids/gear/analysis/chart.md"),
        Path("bids/gear/analysis/final.nii"),
        Path("bids/gear/analysis/buried/result.nii.gz"),
    ]
    paths = [str(tmp_path / file) for file in files]
    make_dirs_and_files(paths)
    root_dir = Path(tmp_path)

    # Test case 1: Excluding files that match patterns in the inclusion list
    inclusion_list = ["*.txt", "*.md"]
    excluded_items = walk_tree_to_exclude(root_dir, inclusion_list)
    for item in excluded_items:
        assert (
            any(fnmatch.fnmatch(item, pattern) for pattern in inclusion_list) is False
        )

    # Test case 2: Including files that do not match any pattern in the inclusion list
    inclusion_list = ["*.txt", "*.md"]
    excluded_items = walk_tree_to_exclude(root_dir, inclusion_list)
    for item in excluded_items:
        assert not any(fnmatch.fnmatch(item, pattern) for pattern in inclusion_list)

    # Test case 3: Empty inclusion list
    inclusion_list = []
    excluded_items = walk_tree_to_exclude(root_dir, inclusion_list)
    assert all(i in excluded_items for i in paths)


@pytest.fixture
def test_archive(tmp_path):
    # Create a temporary test directory
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Create a test zip file
    test_zip_path = test_dir / "test_archive.zip"
    with ZipFile(test_zip_path, "w") as zipf:
        zipf.writestr("file_1.txt", "Test file 1")
        zipf.writestr("file_2.txt", "Test file 2")

    yield test_dir, test_zip_path

    # Clean up after the test
    shutil.rmtree(test_dir)


def test_unzip_archive_files(test_archive, mock_context):
    test_dir, test_zip_path = test_archive
    mock_context.get_input_path.side_effect = lambda key: {
        "archive_key": Path(test_zip_path)
    }.get(key)

    result_dir = unzip_archive_files(mock_context, "archive_key")

    # Assert that the extracted files exist in the result directory
    assert (Path(result_dir) / "file_1.txt").is_file()
    assert (Path(result_dir) / "file_2.txt").is_file()

    # Assert that the archive key in app_options has been updated to the extracted directory
    expected_result_dir = test_dir / "test_archive"
    assert result_dir == expected_result_dir

    @pytest.fixture
    def test_htmls(tmp_path):
        # Create a temporary test directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Create test HTML files
        html_file1 = test_dir / "file_1.html"
        html_file1.touch()

        html_file2 = test_dir / "folder" / "file_2.html"
        html_file2.parent.mkdir()
        html_file2.touch()

        yield test_dir, html_file1, html_file2

        # Clean up
        shutil.rmtree(test_dir)

    # This test ends up testing the sub-methods, too...
    def test_zip_htmls(test_htmls, tmp_path):
        test_dir, html_file1, html_file2 = test_htmls

        output_dir = tmp_path
        destination_id = "test_destination_id"
        html_path = str(test_dir)

        zip_htmls(output_dir, destination_id, html_path)

        # Assert that the zip files are created in the output directory
        zip_index_file = tmp_path / f"{destination_id}_{Path(html_file1).name}.zip"
        assert zip_index_file.is_file()


@pytest.mark.parametrize(
    "mocked_search, expected_files",
    [
        (
            [Path("a_straight_forward.html"), Path("list.html")],
            [Path("a_straight_forward.html"), Path("list.html")],
        ),
        (
            [
                Path("NONfiltered_ses.html"),
                Path("filtered_CITATION.html"),
                Path("random.html"),
            ],
            [Path("NONfiltered_ses.html"), Path("random.html")],
        ),
        ([Path("/dir/figures/here_i_am.html")], []),
        (
            [
                Path("/buried/dir/figures/here_i_am2.html"),
                Path("/sub-001/summary.html"),
            ],
            [Path("/sub-001/summary.html")],
        ),
    ],
)
def test_search_for_html_report_files(mocked_search, expected_files, tmp_path):
    with patch.object(Path, "rglob", return_value=mocked_search) as mock_rglob:
        result_htmls = search_for_html_report_files(tmp_path)

    assert mock_rglob.assert_called_once
    assert sorted(result_htmls) == sorted(expected_files)


@patch("flywheel_bids.flywheel_bids_app_toolkit.compression.zip_htmls")
@patch("flywheel_bids.flywheel_bids_app_toolkit.compression.zip_output")
def test_zip_derivatives(mock_zip_output, mock_zip_htmls, mock_app_context):
    alt_derivatives = ["qsirecon"]

    # Mock the existence of derivative directories
    for derivative in [mock_app_context.bids_app_binary] + alt_derivatives:
        derivative_dir = Path(mock_app_context.analysis_output_dir) / derivative
        derivative_dir.mkdir(parents=True, exist_ok=True)

    zip_derivatives(mock_app_context, alt_derivatives)

    # Check if zip_output and zip_htmls are called with the correct arguments
    for derivative in [mock_app_context.bids_app_binary] + alt_derivatives:
        mock_zip_output.assert_any_call(
            str(mock_app_context.analysis_output_dir),
            derivative,
            str(
                mock_app_context.output_dir
                / f"{mock_app_context.bids_app_binary}_{mock_app_context.destination_id}_{derivative}.zip"
            ),
            dry_run=False,
            exclude_files=None,
        )
        mock_zip_htmls.assert_any_call(
            mock_app_context.output_dir,
            mock_app_context.destination_id,
            Path(mock_app_context.analysis_output_dir) / derivative,
        )


def test_zip_html_and_svg_files(tmpdir, extended_gear_context):
    extended_gear_context.output_dir = Path(tmpdir)
    extended_gear_context.analysis_output_dir = Path(tmpdir) / "analysis"
    extended_gear_context.analysis_output_dir.mkdir(parents=True, exist_ok=True)

    # Create a sample HTML file with an image
    html_content = """
    <html>
    <body>
    <img src="sub-test.html">
    </body>
    </html>
    """
    html_path = extended_gear_context.analysis_output_dir / "sub-test.html"
    with open(html_path, "w") as f:
        f.write(html_content)

    zip_html_and_svg_files(
        extended_gear_context.analysis_output_dir,
        html_path,
        "test_destination",
        extended_gear_context.output_dir,
    )

    zip_file_path = extended_gear_context.output_dir / "sub-test.html.zip"
    assert Path(zip_file_path).exists()

    with ZipFile(zip_file_path, "r") as zip_file:
        assert "index.html" in zip_file.namelist()
        with zip_file.open("index.html", "r") as index_file:
            index_content = index_file.read().decode("utf-8")
            assert '<img src="./sub-test.html"/>' in index_content
