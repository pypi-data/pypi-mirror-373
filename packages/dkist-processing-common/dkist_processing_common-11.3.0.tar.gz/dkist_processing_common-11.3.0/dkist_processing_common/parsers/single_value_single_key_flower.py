"""Pre-made flower that produces tag based on a single header key."""

from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess


class SingleValueSingleKeyFlower(Stem):
    """
    Flower that just passes through a single header value.

    Parameters
    ----------
    tag_stem_name
        The tag stem name
    metadata_key
        The metadata key
    """

    def __init__(self, tag_stem_name: str, metadata_key: str):
        super().__init__(stem_name=tag_stem_name)
        self.metadata_key = metadata_key

    def setter(self, fits_obj: L0FitsAccess):
        """
        Set the value.

        Parameters
        ----------
        fits_obj
            The input fits object

        Returns
        -------
        The value associated with the metadata key for this object
        """
        return getattr(fits_obj, self.metadata_key)

    def getter(self, key):
        """
        Get the value.

        Parameters
        ----------
        key
            The input metadata key

        Returns
        -------
        The value associated with the metadata key for this object
        """
        return self.key_to_petal_dict[key]
