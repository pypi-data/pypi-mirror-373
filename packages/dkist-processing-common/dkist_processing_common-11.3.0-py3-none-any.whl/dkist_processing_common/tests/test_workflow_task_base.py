import json
import logging
import re
import tomllib
from importlib.metadata import version
from pathlib import Path
from string import ascii_uppercase

import pytest
from sqids import Sqids

import dkist_processing_common
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.str import str_encoder
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.constants import ConstantsBase
from dkist_processing_common.models.graphql import RecipeRunProvenanceMutation
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.base import WorkflowTaskBase

logger = logging.getLogger(__name__)


class NewConstants(ConstantsBase):
    @property
    def instrument_twice(self) -> str:
        return self.instrument * 2


class WorkflowTaskBaseTask(WorkflowTaskBase):
    record_provenance = False

    @property
    def constants_model_class(self):
        return NewConstants

    def run(self):
        pass


@pytest.fixture(scope="function")
def workflow_data_task(tmp_path, recipe_run_id):
    number_of_files = 10
    tag_string = "WORKFLOW_DATA_TASK"
    tag_object = Tag.input()
    filenames = []
    with WorkflowTaskBaseTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.constants._update({BudName.instrument.value: "foo"})
        task.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
        for file_num in range(number_of_files):
            file_path = task.write(
                f"file_{file_num}", tags=[tag_object, tag_string], encoder=str_encoder
            )
            filenames.append(file_path.name)

        yield task, number_of_files, filenames, tag_string, tag_object
        task._purge()


def test_valid_read_with_strings(workflow_data_task):
    """
    Given: a WorkflowDataTask with tagged data
    When: reading tagged files using a string
    Then: the correct number of files are returned and they have the correct names
    """
    task, number_of_files, filenames, tag_string, _ = workflow_data_task
    task()
    tagged_filepaths = list(task.read(tags=tag_string))
    assert len(tagged_filepaths) == number_of_files
    for tagged_filepath in tagged_filepaths:
        assert tagged_filepath.name in filenames
        assert tagged_filepath.exists()


def test_valid_read_with_tag_object(workflow_data_task):
    """
    Given: a WorkflowDataTask with tagged data
    When: reading tagged files using a string
    Then: the correct number of files are returned and they have the correct names
    """
    task, number_of_files, filenames, _, tag_object = workflow_data_task
    tagged_filepaths = list(task.read(tags=tag_object))
    assert len(tagged_filepaths) == number_of_files
    for tagged_filepath in tagged_filepaths:
        assert tagged_filepath.name in filenames
        assert tagged_filepath.exists()


def test_valid_write(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: writing a bytes object to disk
    Then: the file is on disk and correctly tagged
    """
    task, _, _, _, _ = workflow_data_task
    relative_path = "bytes_path"
    task.write(data=bytes("abcdefg", "utf-8"), tags="BYTES_OBJECT", relative_path=relative_path)
    assert (task.scratch.workflow_base_path / relative_path).exists()
    assert len(list(task.read(tags="BYTES_OBJECT"))) == 1


def test_write_tags_is_none(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: writing a file to disk with tags=None
    Then: a ValueError is raised
    """
    task, _, _, _, _ = workflow_data_task
    relative_path = "bytesio_path"
    with pytest.raises(TypeError):
        task.write(data=bytes("abcdefg", "utf-8"), tags=None, relative_path=relative_path)


def test_read_nonexistent_tag(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: reading from a tag that doesn't exist
    Then: an empty generator is returned
    """
    task, _, _, _, _ = workflow_data_task
    filepaths = task.read(tags="DOES_NOT_EXIST")
    with pytest.raises(StopIteration):
        next(filepaths)


def test_tag_nonexistent_file(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: trying to tag a file that doesn't exist
    Then: a FileNotFoundError is raised
    """
    task, _, _, _, _ = workflow_data_task
    with pytest.raises(FileNotFoundError):
        task.tag(path=task.scratch.workflow_base_path / "abc.ext", tags="NONEXISTENT_FILE")


def test_tag_not_on_base_path(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: trying to tag a file that isn't on the workflow base path
    Then: a ValueError is raised
    """
    task, _, _, _, _ = workflow_data_task
    with pytest.raises(ValueError):
        task.tag(path="abc.ext", tags="NOT_ON_BASE_PATH")


def test_count(workflow_data_task):
    """
    Given: a WorkflowDataTask with tagged data
    When: counting tagged files
    Then: the correct number of files are returned
    """
    task, number_of_files, filenames, tag_string, _ = workflow_data_task
    task()
    assert task.count(tags=tag_string) == number_of_files


def test_constants(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: accessing a value on that task's constants object
    Then: the correct value is returned
    """
    task = workflow_data_task[0]
    assert task.constants.instrument == "foo"
    assert task.constants.instrument_twice == "foofoo"


def test_dataset_id(workflow_data_task):
    """
    Given: a ParsedL0InputTaskBase task
    When: getting the dataset id
    Then: the dataset id hashed from the recipe run id is returned
    """
    task = workflow_data_task[0]
    expected_dataset_id = Sqids(min_length=6, alphabet=ascii_uppercase).encode([task.recipe_run_id])
    assert len(expected_dataset_id) >= 6
    assert task.constants.dataset_id == expected_dataset_id


class ProvenanceTask(WorkflowTaskBase):
    record_provenance = True

    def run(self): ...

    # Because I couldn't figure out how to mock the mixin
    def metadata_store_record_provenance(self, is_task_manual: bool, library_versions: str):
        params = RecipeRunProvenanceMutation(
            inputDatasetId=1234,
            isTaskManual=is_task_manual,
            recipeRunId=self.recipe_run_id,
            taskName=self.task_name,
            libraryVersions=library_versions,
            workflowVersion=self.workflow_version,
        )
        self.write(data=bytes(params.model_dump_json(), "utf-8"), tags=["TEST_PROVENANCE"])


@pytest.fixture(scope="function")
def provenance_task(tmp_path, recipe_run_id):
    with ProvenanceTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        yield task


@pytest.fixture()
def no_provenance_task(tmp_path, recipe_run_id):
    with ProvenanceTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.record_provenance = False
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        yield task


@pytest.fixture()
def package_dependencies() -> set:
    """
    Extract dependencies from pyproject.toml and format into a set of package names
    """
    module_path = Path(dkist_processing_common.__path__[0])
    pyproject_toml = module_path.parent / "pyproject.toml"
    logger.info(pyproject_toml)
    with open(pyproject_toml, "rb") as f:
        pyproject_toml_data = tomllib.load(f)
    install_requires = pyproject_toml_data["project"]["dependencies"]
    requirements = install_requires + ["dkist-processing-common"]
    dependencies_without_optionals = {re.split(r"[!<=> []", pkg)[0] for pkg in requirements}
    return dependencies_without_optionals


def test_library_versions(provenance_task, package_dependencies):
    """
    Given: An instance of a TaskBase subclass
    When: accessing library_versions attr
    Then: Result contains package names and version numbers for:
        - all installed packages whose names start with 'dkist'
        - all packages required by these 'dkist' packages
      Result does not contain any other packages
      Result structure is Dict[str,str] where the key is library name and value is the version
      Result version values match the versions of the currently installed packages
    """
    libraries = json.loads(provenance_task.library_versions)
    # NB: The list in package_dependencies is a subset of libraries.keys(), as it contains only
    #   dkist-processing-common and its required packages. On the other hand, libraries contains
    #   all packages whose names start with "dkist" along with all their required packages.
    #   Hence, this test verifies only that the entries in package_dependencies are present
    #   in libraries, and that the versions listed for these packages match those of the
    #   installed packages.
    for package in package_dependencies:
        assert package in libraries
        assert libraries[package] == version(package)


def test_record_provenance(provenance_task):
    """
    Given: A WorkflowTaskBase subclass with provenance recording turned on
    When: Running the task
    Then: The library versions are correctly recorded to a provenance record
    """
    provenance_task()
    provenance_record = list(provenance_task.read(tags="TEST_PROVENANCE"))
    assert len(provenance_record) == 1
    expected = json.loads(provenance_task.library_versions)
    with open(provenance_record[0], "r") as f:
        found = json.loads(json.loads(f.read())["libraryVersions"])
    assert found == expected


def test_dont_record_provenance(no_provenance_task):
    """
    Given: A WorkflowTaskBase subclass with provenance recording turned off
    When: Running the task
    Then: No provenance record is created
    """
    no_provenance_task()
    provenance_record = list(no_provenance_task.read(tags="TEST_PROVENANCE"))
    assert len(provenance_record) == 0
