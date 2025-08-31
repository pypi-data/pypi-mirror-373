"""Helper methods to handle fried parameter / r0 validity."""


def r0_valid(
    r0: float | None = None,
    ao_lock: bool | None = None,
    num_out_of_bounds_ao_values: int | None = None,
) -> bool:
    """
    Determine if the r0 value should be considered valid based on the following conditions.

        * ATMOS_R0 does not exist in the header.
        * the value of ATMOS_R0 is greater than 0.3m
        * the AO is not locked
        * the value of OOBSHIFT is greater than 100

    When the adaptive optics system is not locked, the ATMOS_R0 keyword is still filled with the output of the
    Fried parameter calculation. The inputs are not valid in this instance and the value should be removed.

    Sometimes, due to timing differences between the calculation of the Fried parameter and the AO lock status being
    updated, non-physical values can be recorded for ATMOS_R0 right on the edge of an AO_LOCK state change. To
    combat this, any remaining R0 values greater than 30cm (which is beyond the realm of physical possibility for
    solar observations) are also removed.

    In addition, the number of AO out-of-bound values is given in the keyword OOBSHIFT and the AO team advises
    that values under 100 are when the r0 value is considered reliable. If the OOBSHIFT key doesn't exist, this check
    should be ignored.
    """
    if r0 is None:
        return False

    if r0 > 0.3:
        return False

    if ao_lock is not True:
        return False

    if num_out_of_bounds_ao_values is not None and num_out_of_bounds_ao_values > 100:
        return False

    return True
