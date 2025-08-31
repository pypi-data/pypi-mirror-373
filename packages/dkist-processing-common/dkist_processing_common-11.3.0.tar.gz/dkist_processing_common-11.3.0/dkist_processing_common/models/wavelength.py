"""Support classes for manipulating wavelengths."""

import astropy.units as u
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import ValidationInfo
from pydantic import field_validator
from pydantic import model_validator


class WavelengthRange(BaseModel):
    """Model for holding a range of wavelengths."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    min: u.Quantity
    max: u.Quantity

    @field_validator("min", "max")
    @classmethod
    def convert_to_nanometers(cls, v, info: ValidationInfo) -> u.Quantity:
        """Validate wavelength unit is for distance and convert to nanometers."""
        return v.to(u.nm)

    @model_validator(mode="after")
    def max_greater_than_min(self):
        """Validate that the max wavelength is greater than the min wavelength."""
        if self.min > self.max:
            raise ValueError("min is greater than max.  Values may be reversed.")
        return self
