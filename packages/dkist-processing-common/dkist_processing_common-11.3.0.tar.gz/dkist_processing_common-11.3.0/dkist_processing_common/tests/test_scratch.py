"""
Tests for the workflow file system wrapper
"""

from pathlib import Path
from typing import Callable
from uuid import uuid4

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common._util.scratch import _flatten_list


@pytest.fixture(
    params=[pytest.param(["A", "B", "C"], id="1D"), pytest.param(["A", ["B", "C"]], id="2D")]
)
def tagged_workflow_fs_data(workflow_file_system, request):
    wkflow_fs, _, _ = workflow_file_system
    file_obj = b"file contents"
    tags = request.param
    intersection = Path("Intersect/f.txt")
    union = [Path(f"Union{t}/f.txt") for t in tags]
    union.append(intersection)
    wkflow_fs.write(file_obj, intersection, tags=tags)
    for t, p in zip(tags, union):
        wkflow_fs.write(file_obj, p, tags=t)

    # prepend base path
    intersection = wkflow_fs.workflow_base_path / intersection
    union = [wkflow_fs.workflow_base_path / u for u in union]

    return tags, intersection, union, file_obj


def test_workflow_file_system(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem
    When: Accessing attributes
    Then: has attr workflow_base_path which is namespace(d) to recipe run id that exists
    """
    wkflow_fs, rrun_id, custom_base_path = workflow_file_system
    assert wkflow_fs.workflow_base_path.stem == str(rrun_id)
    assert wkflow_fs.workflow_base_path.exists()


@pytest.mark.parametrize(
    "folder_path",
    [
        pytest.param(Path("test_write_path"), id="Path"),
        pytest.param("test_write_str", id="str"),
    ],
)
@pytest.mark.parametrize(
    "tags",
    [
        pytest.param(None, id="0"),
        pytest.param("foo", id="1"),
        pytest.param(["foo", "baz"], id="2"),
        pytest.param(["foo", ["bar", "baz"]], id="nested"),
    ],
)
def test_workflow_file_system_write(workflow_file_system, tags, folder_path):
    """
    Given: An instance of WorkflowFileSystem and a file to write
    When: writing to a relative path with/without tags
    Then: file is written to the path relative to the workflow fs configuration
      tags are added to the tag db if they exist
    """
    wkflow_fs, _, _ = workflow_file_system
    file_obj = uuid4().hex.encode("utf8")
    file_path = Path(f"{uuid4().hex[:6]}.bin")
    rel_path = folder_path / file_path
    # When
    wkflow_fs.write(file_obj, rel_path, tags=tags)
    # Then
    full_file_path = wkflow_fs.workflow_base_path / rel_path
    assert full_file_path.exists()
    with full_file_path.open(mode="rb") as f:
        assert file_obj == f.read()
    if tags:
        assert next(wkflow_fs.find_all(tags=tags)) == full_file_path


def test_workflow_file_system_write_invalid(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem
    When: writing to an absolute path
    Then: ValueError is raised
    """
    wkflow_fs, _, _ = workflow_file_system
    with pytest.raises(ValueError):
        wkflow_fs.write(b"1234", Path.cwd())


@pytest.mark.parametrize(
    "tags",
    [
        pytest.param("foo", id="1"),
        pytest.param(["foo", "baz"], id="2"),
        pytest.param(["foo", ["bar", "baz"]], id="nested"),
    ],
)
def test_workflow_file_system_tag(workflow_file_system, tags):
    """
    Given: An instance of WorkflowFileSystem and a file already in a path
      relative to WorkflowFileSystem base path
    When: Tagging the path
    Then: Tag is added
    """
    wkflow_fs, _, _ = workflow_file_system
    path = wkflow_fs.workflow_base_path / Path("tag_test.txt")
    path.touch()
    # When
    wkflow_fs.tag(path, tags=tags)
    wkflow_fs.tag(str(path), tags=tags)

    # Then
    assert next(wkflow_fs.find_any(tags=tags)) == path


def test_workflow_file_system_remove_tags(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem and a tagged path
    When: Removing tags from the path
    Then: The tags are removed
    """
    wkflow_fs, _, _ = workflow_file_system
    path = wkflow_fs.workflow_base_path / Path("tag_test.txt")
    path.touch()

    wkflow_fs.tag(path, tags=[f"tag{i}" for i in range(1, 7)])

    # Test removal of a single tag
    wkflow_fs.remove_tags(path, "tag1")
    assert sorted(wkflow_fs.tags(path)) == sorted([f"tag{i}" for i in range(2, 7)])

    # Test removal of multiple tags
    wkflow_fs.remove_tags(path, ["tag2", "tag3"])
    assert sorted(wkflow_fs.tags(path)) == sorted([f"tag{i}" for i in range(4, 7)])

    # Test removal of nested tags
    wkflow_fs.remove_tags(
        path,
        ["tag4", ["tag5"]],
    )

    assert wkflow_fs.tags(path) == ["tag6"]


def test_workflow_file_system_tag_invalid_base_path(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem
    When: tagging a path that isn't relative to the WorkflowFileSystem Base path
    Then: get a value error
    """
    wkflow_fs, _, _ = workflow_file_system
    bad_path = Path.cwd()
    with pytest.raises(ValueError):
        wkflow_fs.tag(bad_path, tags="bad_base")


def test_workflow_file_system_tag_invalid_path_not_exists(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem
    When: tagging a path that is relative to the WorkflowFileSystem base path
       doesn't exist
    Then: get a FileNotFoundError error
    """
    wkflow_fs, _, _ = workflow_file_system
    bad_path = wkflow_fs.workflow_base_path / Path("foo/bar.txt")
    assert not bad_path.exists()
    with pytest.raises(FileNotFoundError):
        wkflow_fs.tag(bad_path, tags="bad_base")


def test_workflow_file_system_find_any(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: Calling find any
    Then: Receive the union of the tagged data as Path objects to the data
    """
    tags, _, union, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system

    # When
    result = list(wkflow_fs.find_any(tags))
    # Then
    assert len(result) == len(union)
    for path in result:
        assert path.exists()
        assert path in union
        with path.open(mode="rb") as f:
            assert f.read() == file_obj


def test_workflow_file_system_find_all(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: Calling find all
    Then: Receive the intersection of the tagged data as Path objects to the data
    """
    tags, intersection, _, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system

    # When
    result = list(wkflow_fs.find_all(tags))
    # Then
    assert len(result) == 1
    path = result[0]
    assert path.exists()
    assert path == intersection
    with path.open(mode="rb") as f:
        assert f.read() == file_obj


def test_workflow_file_system_count_any(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: Calling count any
    Then: Receive the number of objects in the union of the tagged data
    """
    tags, _, union, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system

    # When
    result = wkflow_fs.count_any(tags)
    # Then
    assert result == len(union)


def test_workflow_file_system_count_all(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: Calling count all
    Then: Receive the number of objects in the intersection of the tagged data
    """
    tags, intersection, _, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system
    # When
    result = wkflow_fs.count_all(tags)
    # Then
    assert result == 1


def test_workflow_file_system_downstream_task(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: closing that instance and creating a new one
    Then: Receive the intersection of the tagged data as Path objects that were added
        to the original instance
    """
    wkflow_fs, rrun_id, custom_base_path = workflow_file_system
    tags, intersection, _, file_obj = tagged_workflow_fs_data
    # wkflow_fs.close()
    wkflow_fs2 = WorkflowFileSystem(
        recipe_run_id=rrun_id,
        task_name="wkflow_fs_test",
        scratch_base_path=custom_base_path,
    )
    # When
    try:
        result = list(wkflow_fs2.find_all(tags))
        # Then
        assert len(result) == 1
        path = result[0]
        assert path.exists()
        assert path == intersection
        with path.open(mode="rb") as f:
            assert f.read() == file_obj
    finally:
        # Teardown
        wkflow_fs2.purge()


def test_workflow_file_system_purge(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: calling purge
    Then: There is no more tagged data or paths in the base_path
    """
    tags, intersection, _, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system

    # When
    wkflow_fs.purge()
    # Then
    result = list(wkflow_fs.find_any(tags))
    assert not result
    assert not wkflow_fs.workflow_base_path.exists()


@pytest.mark.parametrize(
    "func, attr",
    [
        pytest.param(repr, "__repr__", id="repr"),
        pytest.param(str, "__str__", id="str"),
    ],
)
def test_workflow_file_system_dunder(workflow_file_system, func: Callable, attr):
    """
    Given: Connection to a tag database
    When: retrieving dunder method that should be implemented
    Then: It is implemented
    """
    wkflow_fs, _, _ = workflow_file_system

    assert getattr(wkflow_fs, attr, None)
    assert func(wkflow_fs)


def test_workflow_file_system_delete(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: Deleting a specific file
    Then: The file is removed from disk and all references to it are gone from tags
    """
    tags, _, union, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system
    assert union[0].exists()
    assert str(union[0]) in wkflow_fs._tag_db.any(tags=tags)
    wkflow_fs.delete(path=union[0])
    assert not union[0].exists()
    assert not str(union[0]) in wkflow_fs._tag_db.any(tags=tags)


def test_workflow_file_system_duplicate_do_not_overwrite(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem and a file to write
    When: writing the same file twice with the overwrite flag set to False
    Then: a FileExistsError is raised
    """
    wkflow_fs, _, _ = workflow_file_system
    file_obj = uuid4().hex.encode("utf8")
    file_path = Path(f"{uuid4().hex[:6]}.bin")
    rel_path = Path("test_write_path") / file_path
    # When / Then
    wkflow_fs.write(file_obj, rel_path, tags=None, overwrite=False)
    with pytest.raises(FileExistsError):
        wkflow_fs.write(file_obj, rel_path, tags=None, overwrite=False)


def test_workflow_file_system_duplicate_do_overwrite(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem and a file to write
    When: writing the same file twice with the overwrite flag set to True
    Then: the file is overwritten and only exists once
    """
    wkflow_fs, _, _ = workflow_file_system
    file_obj = uuid4().hex.encode("utf8")
    file_path = Path(f"{uuid4().hex[:6]}.bin")
    rel_path = Path("test_write_path") / file_path
    tags = "TEST_OVERWRITE"
    # When / Then
    wkflow_fs.write(file_obj, rel_path, tags=tags, overwrite=True)
    wkflow_fs.write(file_obj, rel_path, tags=tags, overwrite=True)
    # Then
    full_file_path = wkflow_fs.workflow_base_path / rel_path
    assert full_file_path.exists()
    with full_file_path.open(mode="rb") as f:
        assert file_obj == f.read()
    assert len(list(wkflow_fs.find_any(tags=tags))) == 1


@pytest.mark.parametrize(
    "given, expected",
    [
        pytest.param([], [], id="empty"),
        pytest.param(["a", "b", "c"], ["a", "b", "c"], id="1D"),
        pytest.param(
            ["a", ["b", ["c", "d"], "e"], ["f"], "g", ["h", "i"]],
            ["a", "b", "c", "d", "e", "f", "g", "h", "i"],
            id="Nested",
        ),
    ],
)
def test_flatten_list(given, expected):
    """
    Given: A list to flatten
    When: Flattening the list
    Then: The new list matches the expected 1D result
    """
    # When
    actual = _flatten_list(given)
    assert actual == expected


@pytest.fixture()
def rollback_workflow_fs_setup(recipe_run_id):
    """Return setup data for a workflow file system that has data written and tagged by 2 task names."""
    # Keep task simulates a task that completed successfully
    keep_task_name = "keep_task_name"
    keep_workflow_fs = WorkflowFileSystem(
        recipe_run_id=recipe_run_id,
        task_name=keep_task_name,
    )
    keep_write_tag = "keep_write_tag"
    keep_tag_tag = "keep_tag_tag"
    keep_file = b"keep file"
    keep_file_name = Path(f"{uuid4().hex[:6]}.bin")
    keep_workflow_fs.write(file_obj=keep_file, relative_path=keep_file_name, tags=keep_write_tag)
    keep_file_full_path = list(keep_workflow_fs.find_all(tags=keep_write_tag))[0]
    keep_workflow_fs.tag(path=keep_file_full_path, tags=keep_tag_tag)
    # Rollback task simulates a task that we want to rollback
    rollback_task_name = "rollback_task_name"
    rollback_workflow_fs = WorkflowFileSystem(
        recipe_run_id=recipe_run_id,
        task_name=rollback_task_name,
    )
    rollback_write_tag = "rollback_write_tag"
    rollback_tag_tag = "rollback_tag_tag"
    rollback_file = b"rollback file"
    rollback_file_name = Path(f"{uuid4().hex[:6]}.bin")
    rollback_workflow_fs.write(
        file_obj=rollback_file, relative_path=rollback_file_name, tags=rollback_write_tag
    )
    rollback_file_full_path = list(rollback_workflow_fs.find_all(tags=rollback_write_tag))[0]
    # tagging the file written by the keep task means that just the tag should be removed not the file
    rollback_workflow_fs.tag(path=keep_file_full_path, tags=rollback_tag_tag)

    setup_config = {
        "keep_write_tag": keep_write_tag,
        "keep_tag_tag": keep_tag_tag,
        "keep_file": keep_file,
        "keep_file_full_path": keep_file_full_path,
        "rollback_task_name": rollback_task_name,
        "rollback_write_tag": rollback_write_tag,
        "rollback_tag_tag": rollback_tag_tag,
        "rollback_file": rollback_file,
        "rollback_file_full_path": rollback_file_full_path,
    }
    yield setup_config
    keep_workflow_fs.purge(ignore_errors=True)
    keep_workflow_fs.close()
    rollback_workflow_fs.purge(ignore_errors=True)
    rollback_workflow_fs.close()


def test_workflow_filesystem_rollback(rollback_workflow_fs_setup, recipe_run_id):
    """
    Given: A workflow file system (scratch) setup with data written/tagged by 2 task names
    When: Rolling back with an instance with 1 of the task names
    Then: The files written by the rollback task are removed and the other(s) remain while only the
      tag assigned by the rollback task is removed but the file written by the keep task remains.
    """
    # Given
    keep_write_tag = rollback_workflow_fs_setup["keep_write_tag"]
    keep_tag_tag = rollback_workflow_fs_setup["keep_tag_tag"]
    keep_file_full_path = rollback_workflow_fs_setup["keep_file_full_path"]
    rollback_write_tag = rollback_workflow_fs_setup["rollback_write_tag"]
    rollback_tag_tag = rollback_workflow_fs_setup["rollback_tag_tag"]
    rollback_file_full_path = rollback_workflow_fs_setup["rollback_file_full_path"]
    rollback_task_name = rollback_workflow_fs_setup["rollback_task_name"]
    with WorkflowFileSystem(
        recipe_run_id=recipe_run_id,
        task_name=rollback_task_name,
    ) as rollback_workflow_fs:
        # rollback files are tagged before rollback
        assert rollback_workflow_fs.count_all(tags=rollback_write_tag)
        assert list(rollback_workflow_fs.find_all(tags=rollback_tag_tag))
        # When
        rollback_workflow_fs.rollback()
        # Then
        assert not list(rollback_workflow_fs.find_all(tags=rollback_write_tag))
        assert not list(rollback_workflow_fs.find_all(tags=rollback_tag_tag))
        assert not rollback_file_full_path.exists()
        assert keep_file_full_path.exists()
        assert rollback_workflow_fs.count_all(tags=keep_write_tag)
        assert rollback_workflow_fs.count_all(tags=keep_tag_tag)
