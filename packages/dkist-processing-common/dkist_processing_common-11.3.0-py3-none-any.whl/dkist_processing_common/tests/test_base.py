from random import shuffle
from uuid import uuid4

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import WorkflowTaskBase


class Task(WorkflowTaskBase):
    def run(self) -> None:
        pass


@pytest.fixture
def base_task(tmp_path, recipe_run_id):
    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            scratch_base_path=tmp_path,
            recipe_run_id=recipe_run_id,
            task_name=task.__class__.__name__,
        )
        yield task
    task._purge()


@pytest.fixture
def tags_and_expected_generic_name() -> (list[str], str):
    random_seed = f"ZZ:Z{uuid4().hex[:6]}"
    tags = [
        Tag.input(),
        Tag.output(),
        Tag.intermediate(),
        Tag.frame(),
        Tag.calibrated(),
        Tag.debug(),
        Tag.task("FOO"),
        Tag.dsps_repeat(2),
        Tag.cs_step(4),
        Tag.modstate(5),
        Tag.workflow_task("BAR"),
        Tag.movie(),
        random_seed,
    ]
    shuffle(tags)
    expected_base_name = (
        f"{StemName.debug.value}_"
        f"{StemName.input.value}_"
        f"{StemName.intermediate.value}_"
        f"{StemName.calibrated.value}_"
        f"{StemName.output.value}_"
        f"{StemName.workflow_task.value.replace('_', '-')}-BAR_"
        f"{StemName.task.value}-FOO_"
        f"{StemName.dsps_repeat.value.replace('_', '-')}-2_"
        f"{StemName.cs_step.value.replace('_', '-')}-4_"
        f"{StemName.modstate.value}-5_"
        f"{StemName.movie.value}_"
        f"{random_seed.replace(':', '-')}"
    )
    return tags, expected_base_name


def test_apm_spans(base_task):
    """
    Given: A WorkflowTaskBase task
    When: Calling the task-specific apm_steps with weird inputs
    Then: Errors happen when they're supposed to and not when they're not supposed to
    """
    with pytest.raises(RuntimeError):
        with base_task.apm_processing_step("foo", span_type="bar"):
            pass

    with base_task.apm_task_step("foo", labels={"foo": "bar"}):
        pass


def test_tags(base_task):
    """
    Given: A WorkflowTaskBase task
    When: Creating, querying, and removing tags
    Then: The correct action is performed
    """
    path = base_task.scratch.workflow_base_path / "foo"
    path.touch()

    # Test assignment
    base_task.tag(path, ["tag1", "tag2"])
    assert list(base_task.read(["tag1", "tag2"])) == [path]

    # Test query
    assert sorted(base_task.tags(path)) == sorted(["tag1", "tag2"])

    # Test removal
    base_task.remove_tags(path, "tag1")
    assert base_task.tags(path) == ["tag2"]


def test_build_generic_tag_filename(base_task, tags_and_expected_generic_name):
    """
    Given: A WorkflowTaskBase task
    When: Constructing a default filename from a set of tags
    Then: The correct filename is returned
    """
    tags, expected_name = tags_and_expected_generic_name
    first_expected_name = f"{expected_name}_1.dat"
    first_built_name = base_task.build_generic_tag_filename(tags)
    assert first_built_name == first_expected_name

    second_expected_name = f"{expected_name}_2.dat"
    second_built_name = base_task.build_generic_tag_filename(tags)
    assert second_built_name == second_expected_name


@pytest.mark.parametrize(
    "other_tags",
    [
        pytest.param("A", id="single"),
        pytest.param(["A", "B"], id="list"),
        pytest.param(["A", ["B", "C"]], id="nested list"),
    ],
)
def test_write_workflow_task_tag(base_task, other_tags: str | list[str]):
    """
    :Given: A WorkflowTaskBase task and tags to write with
    :When: Writing a file with given tags
    :Then: Written file is tagged with a workflow task class tag in addition to given tags
    """
    # When
    path = base_task.write(
        data=b"123",
        tags=other_tags,
    )
    path = base_task.scratch.workflow_base_path / path
    # Then
    tags = base_task.tags(path)
    assert Tag.workflow_task(base_task.__class__.__name__) in tags


@pytest.fixture
def rollback_task_setup(tmp_path, recipe_run_id, base_task, mocker, fake_gql_client) -> dict:
    """Return setup data for a task that has data in scratch/constants written by 2 task names (The one from base_task and the RollbackTask)."""
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # add data that should remain
    keep_tag = "test_keep_tag"
    base_task.write(b"keep data", tags=keep_tag)
    keep_constant = {"keep": 1}
    base_task.constants._update(keep_constant)

    class RollbackTask(Task):
        pass

    # add data that can be rolled back
    with RollbackTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            scratch_base_path=tmp_path,
            recipe_run_id=recipe_run_id,
            task_name=task.__class__.__name__,
        )
        rollback_tag = "test_rollback_tag"
        task.write(b"rollback data", tags=rollback_tag)
        rollback_constant = {"remove": 0}
        task.constants._update(rollback_constant)

    # collate info for test case
    setup_config = {
        "rollback_task": RollbackTask,
        "keep_tag": keep_tag,
        "rollback_tag": rollback_tag,
        "keep_constant": keep_constant,
        "rollback_constant": rollback_constant,
    }

    return setup_config


def test_task_rollback(recipe_run_id, tmp_path, rollback_task_setup):
    """
    Given: A recipe run id and task name for a workflow that had data added in multiple tasks
    When: Rolling back the task with the given task name
    Then: Scratch data written by that task is removed but scratch data written by the other task
      remains.
    """
    # Given
    RollbackTask = rollback_task_setup["rollback_task"]
    keep_tag = rollback_task_setup["keep_tag"]
    rollback_tag = rollback_task_setup["rollback_tag"]
    keep_constant = rollback_task_setup["keep_constant"]
    rollback_constant = rollback_task_setup["rollback_constant"]

    task = RollbackTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    )
    task.scratch = WorkflowFileSystem(
        scratch_base_path=tmp_path, recipe_run_id=recipe_run_id, task_name=task.__class__.__name__
    )
    expected_keep_files = list(task.read(tags=keep_tag))
    # rollback data exists before
    assert task.count(tags=rollback_tag)
    assert task.constants._db_dict == keep_constant | rollback_constant

    # When
    task.rollback()
    # Then
    assert not list(task.read(tags=rollback_tag))
    assert sorted(list(task.read(tags=keep_tag))) == sorted(expected_keep_files)
    assert task.constants._db_dict == keep_constant
