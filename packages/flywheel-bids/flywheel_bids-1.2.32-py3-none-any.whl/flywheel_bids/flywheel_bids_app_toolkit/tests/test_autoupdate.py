import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flywheel_bids.flywheel_bids_app_toolkit.autoupdate import (
    extract_repo_from_dockerfile,
    find_file,
    find_gear_details,
    generate_updates_dictionary,
    get_latest_tag,
    is_numeric_version,
    update_json_file,
    update_nested,
    update_tag_in_dockerfile,
)


@pytest.fixture
def create_dockerfile():
    def _create_dockerfile(content):
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".dockerfile"
        ) as temp:
            temp.write(content)
        return temp.name

    yield _create_dockerfile
    # Cleanup: remove all temporary files after tests
    for file in Path(tempfile.gettempdir()).glob("*.dockerfile"):
        os.unlink(file)


@pytest.fixture
def mock_json_file(tmp_path):
    def _mock_json_file(data):
        file = tmp_path / "test.json"
        file.write_text(json.dumps(data))
        return file

    yield _mock_json_file


@pytest.mark.parametrize(
    "dockerfile_content, expected_result",
    [
        (
            """FROM third_party/ubuntu:20.04 \nRUN apt-get update \n""",
            ("third_party", "ubuntu", "20.04"),
        ),
        (
            """FROM myusername/myrepo:1.2.3 \nRUN echo "Hello, World!" \n""",
            ("myusername", "myrepo", "1.2.3"),
        ),
        (
            """FROM ubuntu:18.04 AS build \nRUN apt-get update \nFROM python:3.9-slim \nCOPY --from=build /app /app\n""",
            (None, "python", "3.9-slim"),
        ),
    ],
)
def test_extract_repo_valid(create_dockerfile, dockerfile_content, expected_result):
    dockerfile_path = create_dockerfile(dockerfile_content)
    assert extract_repo_from_dockerfile(dockerfile_path) == expected_result


def test_extract_repo_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        extract_repo_from_dockerfile("nonexistent_file.dockerfile")


### find_file
@pytest.fixture
def setup_file_structure(tmp_path):
    # Create a nested directory structure
    (tmp_path / "dir1" / "subdir").mkdir(parents=True)
    (tmp_path / "dir2").mkdir()

    # Create some files
    (tmp_path / "file1.txt").touch()
    (tmp_path / "dir1" / "file2.txt").touch()
    (tmp_path / "dir1" / "subdir" / "FILE3.TXT").touch()
    (tmp_path / "dir2" / "file4.doc").touch()

    return tmp_path


@pytest.mark.parametrize(
    "filename, search_subdirs, expected_result",
    [
        ("file1.txt", False, "file1.txt"),
        ("file2.txt", True, "dir1/file2.txt"),
        ("FILE3.TXT", True, "dir1/subdir/FILE3.TXT"),
        ("file4.doc", True, "dir2/file4.doc"),
        ("file", True, "file1.txt"),
    ],
)
def test_find_file(setup_file_structure, filename, search_subdirs, expected_result):
    original_cwd = Path.cwd()
    try:
        os.chdir(setup_file_structure)
        result = find_file(filename, search_subdirs)
        assert result.relative_to(setup_file_structure).as_posix() == expected_result
    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize(
    "filename, search_subdirs",
    [
        ("nonexistent.txt", True),
        ("FILE1.TXT", False),
        ("file4.doc", False),  # Won't find because it's not in the current directory
    ],
)
def test_find_file_not_found(setup_file_structure, filename, search_subdirs):
    original_cwd = Path.cwd()
    try:
        os.chdir(setup_file_structure)
        with pytest.raises(FileNotFoundError):
            find_file(filename, search_subdirs)
    finally:
        os.chdir(original_cwd)


### find_gear_details
@pytest.mark.parametrize(
    "json_data, expected_result",
    [
        (
            {"name": "my_bids_algo", "version": "my_bids_algo:1.2.3_4.5.6"},
            ["my_bids_algo", "my_bids_algo:1.2.3"],
        )
    ],
)
def test_find_gear_details(json_data, expected_result, mock_json_file):
    json = mock_json_file(json_data)

    result_name, result_version = find_gear_details(json)

    assert result_name, result_version == expected_result


### generate_updates
@pytest.mark.parametrize(
    "mock_gear_name, mock_gear_version, mock_algo_version, expected_custom, expected_version",
    [
        (
            "fw/gear1",
            "9.8",
            "1.2",
            {"gear-builder": {"image": "fw_gear1:9.8_1.2"}},
            "9.8_1.2",
        ),
    ],
)
def test_generate_update_dictionary(
    mock_gear_name,
    mock_gear_version,
    mock_algo_version,
    expected_custom,
    expected_version,
):
    result = generate_updates_dictionary(
        mock_gear_name, mock_gear_version, mock_algo_version
    )

    assert result["custom"] == expected_custom
    assert result["version"] == expected_version


# get_latest
@pytest.mark.parametrize(
    "username, repo_name, mock_response, expected_result",
    [
        (
            "user1",
            "repo1",
            Mock(
                status_code=200,
                json=lambda: {
                    "results": [
                        {"name": "1.0.0"},
                        {"name": "1.1.0"},
                        {"name": "0.9.0"},
                        {"name": "latest"},
                    ]
                },
            ),
            "1.1.0",
        ),
        (
            None,
            "official_repo",
            Mock(
                status_code=200,
                json=lambda: {
                    "results": [
                        {"name": "3.7"},
                        {"name": "3.8"},
                        {"name": "3.9"},
                        {"name": "latest"},
                    ]
                },
            ),
            "3.9",
        ),
        (
            "user2",
            "empty_repo",
            Mock(status_code=200, json=lambda: {"results": []}),
            None,
        ),
        ("user3", "error_repo", Mock(status_code=404), None),
    ],
)
def test_get_latest_tag(username, repo_name, mock_response, expected_result):
    with patch("requests.get", return_value=mock_response):
        result = get_latest_tag(username, repo_name)
        assert result == expected_result


# is_numeric
@pytest.mark.parametrize(
    "version, expected",
    [
        ("1.0.0", True),
        ("v1.0.0", False),
        ("latest", False),
        ("3.7", True),
        ("alpha", False),
    ],
)
def test_is_numeric_version(version, expected):
    assert is_numeric_version(version) == expected


### update_json
@pytest.mark.parametrize(
    "initial_data, updates, expected_result",
    [
        (
            {"key1": "value1", "key2": {"nested_key": "nested_value"}},
            {"key1": "new_value1", "key2": {"nested_key": "new_nested_value"}},
            {"key1": "new_value1", "key2": {"nested_key": "new_nested_value"}},
        ),
        (
            {"list_key": [1, 2, 3], "dict_key": {"a": 1, "b": 2}},
            {"list_key": [4, 5, 6], "dict_key": {"c": 3}},
            {"list_key": [4, 5, 6], "dict_key": {"a": 1, "b": 2, "c": 3}},
        ),
        (
            {"unchanged": "stay_same", "change_me": "old_value"},
            {"change_me": "new_value", "new_key": "brand_new"},
            {
                "unchanged": "stay_same",
                "change_me": "new_value",
                "new_key": "brand_new",
            },
        ),
        (
            {"deep": {"nested": {"structure": "old"}}},
            {"deep": {"nested": {"structure": "new"}}},
            {"deep": {"nested": {"structure": "new"}}},
        ),
    ],
)
def test_update_json_file(tmp_path, initial_data, updates, expected_result):
    # Create a temporary JSON file
    json_file = tmp_path / "test.json"
    with open(json_file, "w") as f:
        json.dump(initial_data, f)

    # Call the function to update the JSON file
    update_json_file(json_file, updates)

    # Read the updated file
    with open(json_file, "r") as f:
        updated_data = json.load(f)

    # Assert that the file was updated correctly
    assert updated_data == expected_result


# Test for file not found error
def test_update_json_file_not_found(tmp_path):
    non_existent_file = tmp_path / "non_existent.json"
    with pytest.raises(FileNotFoundError):
        update_json_file(non_existent_file, {"key": "value"})


# Test for invalid JSON
def test_update_json_file_invalid_json(tmp_path):
    invalid_json_file = tmp_path / "invalid.json"
    with open(invalid_json_file, "w") as f:
        f.write("This is not valid JSON")

    with pytest.raises(json.JSONDecodeError):
        update_json_file(invalid_json_file, {"key": "value"})


### update_nested
@pytest.mark.parametrize(
    "mock_data, mock_updates, expected_data",
    [
        ({"key": "simple_value"}, {"key": "simple_value2"}, {"key": "simple_value2"}),
        (
            {"key2": {"complicated_key": "my_value"}},
            {"key2": {"complicated_key": "it_changed"}},
            {"key2": {"complicated_key": "it_changed"}},
        ),
    ],
)
def test_update_nested(mock_data, mock_updates, expected_data):
    update_nested(mock_data, mock_updates)
    assert mock_data == expected_data


### update_repo
@pytest.mark.parametrize(
    "initial_content, new_tag, expected_content, expected_result",
    [
        (
            "FROM ignore/this_one:old_tag\nRUN echo'Ignore me'\nFROM user/repo:old_tag\nRUN echo 'Hello'",
            "new_tag",
            "FROM ignore/this_one:old_tag\nRUN echo'Ignore me'\nFROM user/repo:new_tag\nRUN echo 'Hello'",
            ("user", "repo", "new_tag"),
        ),
        (
            "FROM another/image:v1\nCOPY . /app",
            "v2",
            "FROM another/image:v2\nCOPY . /app",
            ("another", "image", "v2"),
        ),
        (
            "FROM python:3.8\nWORKDIR /app",
            "3.9",
            "FROM python:3.9\nWORKDIR /app",
            (None, "python", "3.9"),
        ),
        (
            "FROM my_repo/neat_gear:1.1.8_3.6.0 AS final_stage\nRUN echo 'Building...'",
            "2.0.0",
            "FROM my_repo/neat_gear:2.0.0 AS final_stage\nRUN echo 'Building...'",
            ("my_repo", "neat_gear", "2.0.0"),
        ),
    ],
)
def test_update_tag_in_dockerfile(
    initial_content, new_tag, expected_content, expected_result
):
    with tempfile.TemporaryDirectory() as tmpdirname:
        dockerfile_path = Path(tmpdirname) / "Dockerfile"

        with open(dockerfile_path, "w") as f:
            f.write(initial_content)

        result = update_tag_in_dockerfile(dockerfile_path, new_tag)

        assert result == expected_result

        with open(dockerfile_path, "r") as f:
            updated_content = f.read()

        assert updated_content == expected_content


def test_update_tag_in_dockerfile_error():
    with tempfile.TemporaryDirectory() as tmpdirname:
        dockerfile_path = Path(tmpdirname) / "Dockerfile"

        # Write a Dockerfile without a FROM instruction
        with open(dockerfile_path, "w") as f:
            f.write("RUN echo 'Hello'")

        # Check that the function raises a ValueError
        with pytest.raises(ValueError):
            update_tag_in_dockerfile(dockerfile_path, "new_tag")
