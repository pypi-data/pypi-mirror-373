"""
Common task to populate pipeline Constants and group files with tags by scanning headers.

The problems that parsing solves are:
* We need to sort and group data
* We need to ask questions of the set of data as a whole

In the Parse task, the pipeline has access to every single input file.

In the task we can ask two types of questions of the data:
* Something about a specific frame - becomes a flower and results in a tag on a frame
* Something about the data as a whole - becomes a bud and results in a pipeline constant

Either type of question can involve getting information about any number of frames, and to ask a new
question of the data we just add a new Flower or Bud to the parsing task. The goal is that at the
end of the Parse task the file tags are applied and the constants are populated so that we know
everything we need to know about the dataset as a whole and our data are organized in such a way
that makes the rest of the pipeline easy to write.

In other words, we can find exactly the frame we need (tags) and, once we have it, we never need to look
at a different frame to get information (constants).
"""

import logging
from abc import ABC
from abc import abstractmethod
from typing import TypeVar

from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import FlowerPot
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.flower_pot import Thorn
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.parsers.experiment_id_bud import ContributingExperimentIdsBud
from dkist_processing_common.parsers.experiment_id_bud import ExperimentIdBud
from dkist_processing_common.parsers.proposal_id_bud import ContributingProposalIdsBud
from dkist_processing_common.parsers.proposal_id_bud import ProposalIdBud
from dkist_processing_common.parsers.time import AverageCadenceBud
from dkist_processing_common.parsers.time import MaximumCadenceBud
from dkist_processing_common.parsers.time import MinimumCadenceBud
from dkist_processing_common.parsers.time import TaskExposureTimesBud
from dkist_processing_common.parsers.time import TaskReadoutExpTimesBud
from dkist_processing_common.parsers.time import VarianceCadenceBud
from dkist_processing_common.parsers.unique_bud import UniqueBud
from dkist_processing_common.tasks.base import WorkflowTaskBase

__all__ = [
    "ParseL0InputDataBase",
    "ParseDataBase",
    "default_constant_bud_factory",
    "default_tag_flower_factory",
]


logger = logging.getLogger(__name__)
S = TypeVar("S", bound=Stem)


def default_constant_bud_factory() -> list[S]:
    """Provide default constant buds for use in common parsing tasks."""
    return [
        UniqueBud(constant_name=BudName.instrument.value, metadata_key="instrument"),
        ProposalIdBud(),
        ContributingProposalIdsBud(),
        ExperimentIdBud(),
        ContributingExperimentIdsBud(),
        AverageCadenceBud(),
        MaximumCadenceBud(),
        MinimumCadenceBud(),
        VarianceCadenceBud(),
        TaskExposureTimesBud(stem_name=BudName.dark_exposure_times.value, ip_task_types="dark"),
        TaskReadoutExpTimesBud(
            stem_name=BudName.dark_readout_exp_times.value, ip_task_types="dark"
        ),
    ]


def default_tag_flower_factory() -> list[S]:
    """Provide default tag flowers for use in common parsing tasks."""
    return []


class ParseDataBase(WorkflowTaskBase, ABC):
    """Base class for tasks which need to parse some already tagged data and set constants and/or add additional tags to them."""

    @property
    @abstractmethod
    def constant_buds(self) -> list[S]:
        """Define the constants used."""

    @property
    @abstractmethod
    def tag_flowers(self) -> list[S]:
        """Define the Tags to apply."""

    @property
    @abstractmethod
    def fits_parsing_class(self):
        """Class used to parse the input data."""

    @property
    @abstractmethod
    def tags_for_input_frames(self) -> list[Tag]:
        """Define the tags for the data that will be parsed."""

    def run(self) -> None:
        """Run method for this task."""
        with self.apm_task_step("Check that input frames exist"):
            self.check_input_frames()

        with self.apm_task_step("Ingest all input files"):
            tag_pot, constant_pot = self.make_flower_pots()

        with self.apm_task_step("Update constants"):
            self.update_constants(constant_pot)

        with self.apm_task_step("Tag files"):
            self.tag_petals(tag_pot)

    def make_flower_pots(self) -> tuple[FlowerPot, FlowerPot]:
        """Ingest all headers."""
        tag_pot = FlowerPot()
        constant_pot = FlowerPot()
        tag_pot.stems += self.tag_flowers
        constant_pot.stems += self.constant_buds

        for fits_obj in self.input_frames:
            filepath = fits_obj.name
            tag_pot.add_dirt(filepath, fits_obj)
            constant_pot.add_dirt(filepath, fits_obj)

        return tag_pot, constant_pot

    @property
    def input_frames(self):
        """Return a fits access generator containing the input fits objects."""
        return self.read(
            tags=self.tags_for_input_frames,
            decoder=fits_access_decoder,
            fits_access_class=self.fits_parsing_class,
        )

    def check_input_frames(self):
        """Make sure that at least one tagged frame exists before doing anything else."""
        if self.scratch.count_all(tags=self.tags_for_input_frames) == 0:
            raise ValueError(f"No frames were tagged with {self.tags_for_input_frames}")

    def update_constants(self, constant_pot: FlowerPot):
        """
        Update pipeline Constants.

        Parameters
        ----------
        constant_pot
            The flower pot to be updated
        Returns
        -------
        None
        """
        for stem in constant_pot:
            with self.apm_processing_step(f"Setting value of constant {stem.stem_name}"):
                if len(stem.petals) == 0:
                    # There are no petals so nothing to do
                    continue
                if stem.bud.value is Thorn:
                    # Must've been a picky bud that passed. We don't want to pick it because it has no value
                    continue

                value = stem.bud.value
                self.constants._update({stem.stem_name: value})
                logger.info(f"Value of {stem.stem_name} set to {value}")

    def tag_petals(self, tag_pot: FlowerPot):
        """
        Apply tags to file paths.

        Parameters
        ----------
        tag_pot
            The flower pot to be tagged
        Returns
        -------
        None
        """
        for stem in tag_pot:
            with self.apm_processing_step(f"Applying {stem.stem_name} tag to files"):
                for petal in stem.petals:
                    tag = Tag.format_tag(stem.stem_name, petal.value)
                    for path in petal.keys:
                        self.tag(path, tag)


class ParseL0InputDataBase(ParseDataBase, ABC):
    """
    Common task to populate pipeline Constants and group files with tags by scanning headers.

    A minimum of configuration is needed to define the fits_parsing_class. e.g.
    >>> class ParseL0VispInputData(ParseL0InputDataBase):
    >>>     @property
    >>>     def fits_parsing_class(self):
    >>>         return VispL0FitsAccess
    """

    @property
    def constant_buds(self) -> list[S]:
        """Define the constants used."""
        return default_constant_bud_factory()

    @property
    def tag_flowers(self) -> list[S]:
        """Define the Tags to apply."""
        return default_tag_flower_factory()

    @property
    def tags_for_input_frames(self) -> list[Tag]:
        """Define the tags for the data that will be parsed."""
        return [Tag.input(), Tag.frame()]
