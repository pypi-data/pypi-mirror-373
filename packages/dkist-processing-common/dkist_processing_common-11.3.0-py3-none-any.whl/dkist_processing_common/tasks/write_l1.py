"""Task(s) for writing level 1 data as 214 compliant fits files."""

import importlib
import logging
import uuid
from abc import ABC
from abc import abstractmethod
from functools import cached_property
from pathlib import Path
from string import ascii_uppercase
from typing import Literal

import astropy.units as u
import numpy as np
from astropy.io import fits
from astropy.time import Time
from dkist_fits_specifications import __version__ as spec_version
from dkist_fits_specifications.utils.formatter import reformat_spec214_header
from dkist_header_validator import spec214_validator
from dkist_header_validator.translator import remove_extra_axis_keys
from dkist_header_validator.translator import remove_spec_122_keys_and_spec_214_l0_keys
from dkist_spectral_lines.search import get_closest_spectral_line
from dkist_spectral_lines.search import get_spectral_lines
from scipy.stats import kurtosis
from scipy.stats import skew
from sqids import Sqids
from sunpy.coordinates import HeliocentricInertial
from sunpy.coordinates import Helioprojective

from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.dkist_location import location_of_dkist
from dkist_processing_common.models.fried_parameter import r0_valid
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.models.wavelength import WavelengthRange
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.tasks import WorkflowTaskBase

logger = logging.getLogger(__name__)

__all__ = ["WriteL1Frame"]

from dkist_processing_common.tasks.mixin.metadata_store import MetadataStoreMixin


class WriteL1Frame(WorkflowTaskBase, MetadataStoreMixin, ABC):
    """
    Task to convert final calibrated science frames into spec 214 compliant level 1 frames.

    It is intended to be subclassed as the dataset header table is instrument specific.
    """

    def run(self) -> None:
        """Run method for this task."""
        for stokes_param in self.constants.stokes_params:
            with self.apm_task_step(f"Get calibrated frames for stokes param {stokes_param}"):
                tags = [Tag.frame(), Tag.calibrated(), Tag.stokes(stokes_param)]
                calibrated_fits_objects = self.read(
                    tags=tags,
                    decoder=fits_access_decoder,
                    fits_access_class=L0FitsAccess,
                    auto_squeeze=False,
                )
                num_files = self.scratch.count_all(tags)

            for file_num, calibrated_fits_object in enumerate(calibrated_fits_objects, start=1):
                # Convert the headers to L1
                l1_header = self.convert_l0_to_l1(
                    header=calibrated_fits_object.header,
                    data=calibrated_fits_object.data,
                    hdu_size=calibrated_fits_object.size,
                    stokes_param=stokes_param,
                )

                data_array = calibrated_fits_object.data
                # Cast array to float32 if float64
                if np.issubdtype(data_array.dtype, np.float64):
                    # Cast to float32 with the conservative casting option
                    # just incase something weird has happened.
                    data_array = data_array.astype(np.float32, casting="same_kind")

                # Get the tile size to use for compression. None means use astropy defaults
                tile_size = self.compute_tile_size_for_array(data_array)
                # Write frame to disk - compressed
                hdu = fits.CompImageHDU(header=l1_header, data=data_array, tile_shape=tile_size)
                formatted_header = reformat_spec214_header(hdu.header)
                hdu = fits.CompImageHDU(
                    header=formatted_header, data=hdu.data, tile_shape=tile_size
                )
                relative_path = self.l1_filename(header=l1_header, stokes=stokes_param)
                temp_file_name = Path(calibrated_fits_object.name).name
                logger.debug(
                    f"{file_num} of {num_files}: Translate and write frame {temp_file_name} to {relative_path}"
                )
                tags = [Tag.output(), Tag.frame(), Tag.stokes(stokes_param)]
                self.write(
                    data=fits.HDUList([fits.PrimaryHDU(), hdu]),
                    tags=tags,
                    encoder=fits_hdulist_encoder,
                    relative_path=relative_path,
                )

                self.update_framevol(relative_path)

                # Check that the written file passes spec 214 validation if requested
                if self.validate_l1_on_write:
                    spec214_validator.validate(
                        self.scratch.absolute_path(relative_path), extra=False
                    )

    @cached_property
    def tile_size_param(self) -> int | None:
        """Get the tile size parameter for compression."""
        return self.metadata_store_recipe_run.configuration.tile_size

    @cached_property
    def validate_l1_on_write(self) -> bool:
        """Check for validate on write."""
        return self.metadata_store_recipe_run.configuration.validate_l1_on_write

    @cached_property
    def workflow_had_manual_intervention(self):
        """Indicate determining if any provenance capturing steps had manual intervention."""
        for provenance_record in self.metadata_store_recipe_run.recipeRunProvenances:
            if provenance_record.isTaskManual:
                return True
        return False

    def compute_tile_size_for_array(self, data: np.ndarray) -> list | None:
        """Determine the tile size to use for compression accounting for array shape minimums."""
        if self.tile_size_param is None:
            return None
        tile_size = []
        for dim_size in data.shape:
            if dim_size < self.tile_size_param:
                tile_size.append(dim_size)
            else:
                tile_size.append(self.tile_size_param)
        return tile_size

    def update_framevol(self, relative_path: str) -> None:
        """Update FRAMEVOL key to be exactly the size of the file on-disk."""
        full_path = self.scratch.workflow_base_path / relative_path
        compressed_size = full_path.stat().st_size / 1024 / 1024
        hdul = fits.open(full_path, mode="update")
        hdul[1].header["FRAMEVOL"] = compressed_size
        hdul.flush()
        del hdul

    def replace_header_values(self, header: fits.Header, data: np.ndarray) -> fits.Header:
        """Replace header values that should already exist with new values."""
        header["FILE_ID"] = uuid.uuid4().hex
        header["DATE"] = Time.now().fits
        # Remove BZERO and BSCALE as their value should be recalculated by astropy upon fits write
        header.pop("BZERO", None)
        header.pop("BSCALE", None)
        # Make sure that NAXIS is set to the shape of the data in case of squeezing
        header["NAXIS"] = len(data.shape)
        # The HLSVERS keyword was added after data was ingested into the data stores. This means
        # it isn't guaranteed to exist in all L0 data to be copied to the L1 data. This next line
        # ensures a copy will be made
        header["HLSVERS"] = header["ID___014"]
        header["DATE-END"] = self.calculate_date_end(header=header)
        return header

    @staticmethod
    def compute_product_id(ids_obs_id: int, proc_type: str) -> str:
        """Compute the productId from IDSOBSID and PROCTYPE."""
        sqid_factory = Sqids(alphabet=ascii_uppercase, min_length=5)
        sqid = sqid_factory.encode([ids_obs_id])
        return f"{proc_type}-{sqid}"

    @staticmethod
    def add_stats_headers(header: fits.Header, data: np.ndarray) -> fits.Header:
        """Fill out the spec 214 statistics header table."""
        data = data.flatten()
        percentiles = np.nanpercentile(data, [1, 2, 5, 10, 25, 75, 90, 95, 98, 99])
        header["DATAMIN"] = np.nanmin(data)
        header["DATAMAX"] = np.nanmax(data)
        header["DATAMEAN"] = np.nanmean(data)
        header["DATAMEDN"] = np.nanmedian(data)
        header["DATAP01"] = percentiles[0]
        header["DATAP02"] = percentiles[1]
        header["DATAP05"] = percentiles[2]
        header["DATAP10"] = percentiles[3]
        header["DATAP25"] = percentiles[4]
        header["DATAP75"] = percentiles[5]
        header["DATAP90"] = percentiles[6]
        header["DATAP95"] = percentiles[7]
        header["DATAP98"] = percentiles[8]
        header["DATAP99"] = percentiles[9]
        header["DATARMS"] = np.sqrt(np.nanmean(data**2))
        header["DATAKURT"] = kurtosis(data, nan_policy="omit")
        header["DATASKEW"] = skew(data, nan_policy="omit")
        return header

    def add_datacenter_headers(
        self,
        header: fits.Header,
        hdu_size: float,
        stokes: Literal["I", "Q", "U", "V"],
    ) -> fits.Header:
        """Fill out the spec 214 datacenter header table."""
        header["DSETID"] = self.constants.dataset_id
        header["POINT_ID"] = self.constants.dataset_id
        # This is just a placeholder value, but it's needed so FRAMEVOL gets properly commented and placed during header formatting
        header["FRAMEVOL"] = -1.0
        header["PROCTYPE"] = "L1"
        header["RRUNID"] = self.recipe_run_id
        header["RECIPEID"] = self.metadata_store_recipe_run.recipeInstance.recipeId
        header["RINSTID"] = self.metadata_store_recipe_run.recipeInstanceId
        header["EXTNAME"] = "observation"
        header["SOLARNET"] = 1
        header["OBS_HDU"] = 1
        header["FILENAME"] = self.l1_filename(header=header, stokes=stokes)
        header["STOKES"] = stokes
        # Keywords to support reprocessing
        if parameters := self.metadata_store_input_dataset_parameters:
            header["IDSPARID"] = parameters.inputDatasetPartId
        if observe_frames := self.metadata_store_input_dataset_observe_frames:
            header["IDSOBSID"] = observe_frames.inputDatasetPartId
        if calibration_frames := self.metadata_store_input_dataset_calibration_frames:
            header["IDSCALID"] = calibration_frames.inputDatasetPartId
        header["WKFLNAME"] = self.workflow_name
        header["WKFLVERS"] = self.workflow_version
        header = self.add_contributing_id_headers(header=header)
        header["MANPROCD"] = self.workflow_had_manual_intervention
        header["PRODUCT"] = self.compute_product_id(header["IDSOBSID"], header["PROCTYPE"])
        return header

    def add_timing_headers(self, header: fits.Header) -> fits.Header:
        """
        Add timing headers to the FITS header.

        This method adds or updates headers related to frame timings.
        """
        # Cadence keywords
        header["CADENCE"] = self.constants.average_cadence
        header["CADMIN"] = self.constants.minimum_cadence
        header["CADMAX"] = self.constants.maximum_cadence
        header["CADVAR"] = self.constants.variance_cadence
        return header

    def add_spectral_line_headers(
        self,
        header: fits.Header,
    ) -> fits.Header:
        """Add datacenter table keys relating to spectral lines."""
        wavelength_range = self.get_wavelength_range(header=header)
        spectral_lines = get_spectral_lines(
            wavelength_min=wavelength_range.min,
            wavelength_max=wavelength_range.max,
        )
        if spectral_lines:
            header["NSPECLNS"] = len(spectral_lines)
            for i, l in enumerate(spectral_lines):
                header[f"SPECLN{str(i + 1).zfill(2)}"] = l.name
        return header

    @abstractmethod
    def get_wavelength_range(self, header: fits.Header) -> WavelengthRange:
        """
        Determine the wavelength range covered by the data in this frame.

        For imagers, this is generally the wavelengths covered by the filter.
        For spectrographs, this is the wavelengths covered by the spectral axis of the data.
        """

    def add_solarnet_headers(self, header: fits.Header) -> fits.Header:
        """Add headers recommended by solarnet that haven't already been added."""
        header["DATE-AVG"] = self.calculate_date_avg(header=header)
        header["TELAPSE"] = self.calculate_telapse(header=header)
        header["DATEREF"] = header["DATE-BEG"]
        header["OBSGEO-X"] = location_of_dkist.x.to_value(unit=u.m)
        header["OBSGEO-Y"] = location_of_dkist.y.to_value(unit=u.m)
        header["OBSGEO-Z"] = location_of_dkist.z.to_value(unit=u.m)
        obstime = Time(header["DATE-AVG"])
        header["OBS_VR"] = (
            location_of_dkist.get_gcrs(obstime=obstime)
            .transform_to(HeliocentricInertial(obstime=obstime))
            .d_distance.to_value(unit=u.m / u.s)
        )  # relative velocity of observer with respect to the sun in m/s
        header["SOLARRAD"] = self.calculate_solar_angular_radius(obstime=obstime)
        header["SPECSYS"] = "TOPOCENT"  # no wavelength correction made due to doppler velocity
        header["VELOSYS"] = 0.0  # no wavelength correction made due to doppler velocity
        wavelength_range = self.get_wavelength_range(header=header)
        header["WAVEMIN"] = wavelength_range.min.to_value(u.nm)
        header["WAVEMAX"] = wavelength_range.max.to_value(u.nm)
        waveband: str | None = self.get_waveband(
            wavelength=header["LINEWAV"] * u.nm, wavelength_range=wavelength_range
        )
        if waveband:
            header["WAVEBAND"] = waveband
        return header

    def l1_filename(self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]):
        """
        Use a FITS header to derive its filename in the following format.

        instrument_datetime_wavelength__stokes_datasetid_L1.fits.

        Example
        -------
        "VISP_2020_03_13T00_00_00_000_01080000_Q_DATID_L1.fits"

        Parameters
        ----------
        header
            The input fits header
        stokes
            The stokes parameter

        Returns
        -------
        The L1 filename
        """
        instrument = header["INSTRUME"]
        wavelength = str(round(header["LINEWAV"] * 1000)).zfill(8)
        datetime = header["DATE-BEG"].replace("-", "_").replace(":", "_").replace(".", "_")
        return f"{instrument}_{datetime}_{wavelength}_{stokes}_{self.constants.dataset_id}_L1.fits"

    @staticmethod
    def calculate_date_avg(header: fits.Header) -> str:
        """Given the start and end datetimes of observations, return the datetime exactly between them."""
        start_time = Time(header["DATE-BEG"], format="isot", precision=6)
        end_time = Time(header["DATE-END"], format="isot", precision=6)
        time_diff = end_time - start_time
        return (start_time + (time_diff / 2)).to_value("isot")

    @staticmethod
    def calculate_telapse(header: fits.Header) -> float:
        """Given the start and end time of observation, calculate the time elapsed, in seconds."""
        start_time = Time(header["DATE-BEG"], format="isot", precision=6).to_value("mjd")
        end_time = Time(header["DATE-END"], format="isot", precision=6).to_value("mjd")
        return (end_time - start_time) * 86400  # seconds in a day

    def convert_l0_to_l1(
        self,
        header: fits.Header,
        data: np.ndarray,
        hdu_size: float,
        stokes_param: Literal["I", "Q", "U", "V"],
    ) -> fits.Header:
        """
        Run through the steps needed to convert a L0 header into a L1 header.

        Parameters
        ----------
        header
            The L0 header
        data
            The data array
        hdu_size
            The hdu size
        stokes_param
            The stokes parameter

        Returns
        -------
        A header translated to L1
        """
        # Replace header values in place
        header = self.replace_header_values(header=header, data=data)
        # Remove r0 value if r0 conditions are not met
        r0_is_valid = r0_valid(
            r0=header["ATMOS_R0"],
            ao_lock=header.get("AO_LOCK", None),
            num_out_of_bounds_ao_values=header.get("OOBSHIFT", None),
        )
        if not r0_is_valid:
            header.pop("ATMOS_R0", None)
        # Add the stats table
        header = self.add_stats_headers(header=header, data=data)
        # Add the datacenter table
        header = self.add_datacenter_headers(header=header, hdu_size=hdu_size, stokes=stokes_param)
        # Add extra headers recommended by solarnet (not all in a single table)
        header = self.add_solarnet_headers(header=header)
        # Add the documentation headers
        header = self.add_doc_headers(header=header)
        # Add the dataset headers (abstract - implement in instrument task)
        header = self.add_dataset_headers(header=header, stokes=stokes_param)
        # Add the timing headers
        header = self.add_timing_headers(header=header)
        # Add the spectral line headers
        header = self.add_spectral_line_headers(header=header)
        # Remove any headers not contained in spec 214
        header = remove_spec_122_keys_and_spec_214_l0_keys(input_headers=header)
        # Remove any keys referring to axes that don't exist
        header = remove_extra_axis_keys(input_headers=header)
        return header

    def add_doc_headers(self, header: fits.Header) -> fits.Header:
        """
        Add URLs to the headers that point to the correct versions of documents in our public documentation.

        Parameters
        ----------
        header
            The FITS header to which the doc headers is to be added
        Returns
        -------
        None

        Header values follow these rules:
            1. header['INFO_URL']:
                The main documentation site: docs.dkist.nso.edu
            2. header['HEADVERS']:
                The version of the DKIST FITS specs used for this calibration:
                dkist_fits_specifications.__version__
            3. header['HEAD_URL']:
                The URL for the documentation of this version of the DKIST fits specifications:
                docs.dkist.nso.edu/projects/data-products/en/v<version> where <version> is header['HEADVERS']
            4. header['CALVERS']:
                The version of the calibration codes used for this calibration
                dkist_processing_<instrument>.__version__
                <instrument> is available as self.constants.instrument
            5. header['CAL_URL']:
                The URL for the documentation of this version of the calibration codes for
                the current instrument and workflow being executed
                docs.dkist.nso.edu/projects/<instrument>/en/v<version>/<workflow_name>.html
        """
        header["INFO_URL"] = self.docs_base_url
        header["HEADVERS"] = spec_version
        header["HEAD_URL"] = f"{self.docs_base_url}/projects/data-products/en/v{spec_version}"
        inst_name = self.constants.instrument.lower()
        calvers = self.version_from_module_name()
        header["CALVERS"] = calvers
        header["CAL_URL"] = (
            f"{self.docs_base_url}/projects/{inst_name}/en/v{calvers}/{self.workflow_name}.html"
        )
        return header

    def version_from_module_name(self) -> str:
        """
        Get the value of __version__ from a module given its name.

        Returns
        -------
        The value of __version__
        """
        package = self.__module__.split(".")[0]
        module = importlib.import_module(package)
        return module.__version__

    @abstractmethod
    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        """
        Abstract method to be implemented in the instrument repos.

        Construction of the dataset object is instrument, or possibly instrument mode specific.

        Parameters
        ----------
        header
            The input fits header
        stokes
            The stokes parameter

        Returns
        -------
        The input header updated with the addition of the data set headers
        """

    @abstractmethod
    def calculate_date_end(self, header: fits.Header) -> str:
        """
        Calculate the instrument specific version of the "DATE-END" keyword.

        This abstract method forces each instrument pipeline to consider the implementation of the
        DATE-END calculation.

        Parameters
        ----------
        header
            The input fits header

        Returns
        -------
        The isot formatted string of the DATE-END keyword value
        """

    def add_contributing_id_headers(self, header: fits.Header) -> fits.Header:
        """Add headers for contributing proposal and experiment IDs."""
        # contributing proposal ID headers
        for i, contributing_proposal_id in enumerate(
            self.constants.contributing_proposal_ids, start=1
        ):
            header[f"PROPID{str(i).zfill(2)}"] = contributing_proposal_id
        header["NPROPOS"] = len(self.constants.contributing_proposal_ids)
        # contributing experiment ID headers
        for i, contributing_experiment_id in enumerate(
            self.constants.contributing_experiment_ids, start=1
        ):
            header[f"EXPRID{str(i).zfill(2)}"] = contributing_experiment_id
        header["NEXPERS"] = len(self.constants.contributing_experiment_ids)
        return header

    def calculate_solar_angular_radius(self, obstime: Time) -> float:
        """
        Calculate the angular radius of the Sun.

        Given a time of observation, return the angular radius of the Sun, in arcseconds,
        as seen by an observer located at the DKIST site at the given time of observation.
        """
        dummy_theta_coord = 0 * u.arcsec
        dkist_at_obstime = location_of_dkist.get_itrs(obstime=obstime)
        sun_coordinate = Helioprojective(
            Tx=dummy_theta_coord, Ty=dummy_theta_coord, observer=dkist_at_obstime
        )
        return round(sun_coordinate.angular_radius.value, 2)

    @staticmethod
    def remove_invalid_r0_values(header: fits.Header) -> fits.Header:
        """Remove the Fried parameter r0 from the header if the AO is not locked."""
        if header.get("AO_LOCK") is not True:
            header.pop("ATMOS_R0", None)
        return header

    @staticmethod
    def get_waveband(wavelength: u.Quantity, wavelength_range: WavelengthRange) -> str | None:
        """
        Get the spectral line information of the closest spectral line to the wavelength argument.

        If the spectral line rest wavelength in air does not fall in the wavelength range of the data,
        do not populate the keyword.
        """
        closest_line = get_closest_spectral_line(wavelength=wavelength)
        rest_wavelength = closest_line.rest_wavelength_in_air
        if rest_wavelength < wavelength_range.min or rest_wavelength > wavelength_range.max:
            return None
        return closest_line.name
