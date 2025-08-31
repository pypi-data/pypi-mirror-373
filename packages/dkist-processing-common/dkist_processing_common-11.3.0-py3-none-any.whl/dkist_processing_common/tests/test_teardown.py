import json
from typing import Type

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.str import str_encoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.teardown import Teardown
from dkist_processing_common.tests.mock_metadata_store import RecipeRunResponseMapping
from dkist_processing_common.tests.mock_metadata_store import fake_gql_client_factory
from dkist_processing_common.tests.mock_metadata_store import make_default_recipe_run_response


class TeardownTest(Teardown):
    def metadata_store_change_recipe_run_to_completed_successfully(self):
        pass


@pytest.fixture()
def make_mock_GQL_with_configuration():
    def class_generator(teardown_option: bool | None):
        recipe_run_response = make_default_recipe_run_response()
        config = recipe_run_response.configuration
        if isinstance(teardown_option, bool):
            config.teardown_enabled = teardown_option
        else:
            config_dict = config.model_dump(exclude="teardown_enabled")
            config = json.dumps(config_dict)
        response_mapping_override = RecipeRunResponseMapping(response=recipe_run_response)
        TeardownFakeGQLClient = fake_gql_client_factory(
            response_mapping_override=response_mapping_override
        )
        return TeardownFakeGQLClient

    return class_generator


@pytest.fixture(scope="session")
def teardown_enabled() -> bool:
    return True


@pytest.fixture(scope="session")
def teardown_disabled() -> bool:
    return False


@pytest.fixture(scope="session")
def teardown_default() -> None:
    return None


@pytest.fixture(scope="function")
def teardown_task_factory(tmp_path, recipe_run_id):
    def factory(teardown_task_cls: Type[Teardown]):
        number_of_files = 10
        tag_object = Tag.output()
        filenames = []
        with teardown_task_cls(
            recipe_run_id=recipe_run_id,
            workflow_name="workflow_name",
            workflow_version="workflow_version",
        ) as task:
            task.scratch = WorkflowFileSystem(
                recipe_run_id=recipe_run_id,
                scratch_base_path=tmp_path,
            )
            task.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
            for file_num in range(number_of_files):
                file_path = task.write(f"file_{file_num}", tag_object, encoder=str_encoder)
                filenames.append(file_path.name)

            task.constants._update({"teardown_constant": 1234})

            return task, filenames, tag_object

    yield factory


def test_purge_data(
    teardown_task_factory, make_mock_GQL_with_configuration, teardown_enabled, mocker
):
    """
    :Given: A Teardown task with files and tags linked to it and teardown enabled
    :When: Running the task
    :Then: All the files are deleted and the tags are removed
    """
    FakeGQLClass = make_mock_GQL_with_configuration(teardown_enabled)
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClass
    )
    task, filenames, tag_object = teardown_task_factory(TeardownTest)
    tagged_data = list(task.read(tags=tag_object))
    for filepath in tagged_data:
        assert filepath.exists()
    task()
    for filepath in tagged_data:
        assert not filepath.exists()
    post_purge_tagged_data = list(task.read(tags=tag_object))
    assert len(post_purge_tagged_data) == 0
    # audit data removed
    assert not task.scratch._audit_db.tags
    assert not task.constants._db_dict._audit_db.tags
    assert not task.filename_counter.tags


def test_purge_data_disabled(
    teardown_task_factory, make_mock_GQL_with_configuration, teardown_disabled, mocker
):
    """
    :Given: A Teardown task with files and tags linked to it and teardown disabled
    :When: Running the task
    :Then: All the files are not deleted and the tags remain
    """
    FakeGQLClass = make_mock_GQL_with_configuration(teardown_disabled)
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClass
    )
    task, filenames, tag_object = teardown_task_factory(TeardownTest)
    tagged_data = list(task.read(tags=tag_object))
    for filepath in tagged_data:
        assert filepath.exists()
    task()
    for filepath in tagged_data:
        assert filepath.exists()  # still exists
    post_purge_tagged_data = list(task.read(tags=tag_object))
    assert len(post_purge_tagged_data) == len(tagged_data)
    # audit data still present
    assert task.scratch._audit_db.tags
    assert task.constants._db_dict._audit_db.tags
    assert task.filename_counter.tags


def test_purge_data_no_config(
    teardown_task_factory, make_mock_GQL_with_configuration, teardown_default, mocker
):
    """
    :Given: A Teardown task with files and tags linked and default teardown configuration
    :When: Running the task
    :Then: All the files are deleted and the tags are removed
    """
    FakeGQLClass = make_mock_GQL_with_configuration(teardown_default)
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClass
    )
    task, filenames, tag_object = teardown_task_factory(TeardownTest)
    tagged_data = list(task.read(tags=tag_object))
    for filepath in tagged_data:
        assert filepath.exists()
    task()
    for filepath in tagged_data:
        assert not filepath.exists()
    post_purge_tagged_data = list(task.read(tags=tag_object))
    assert len(post_purge_tagged_data) == 0
