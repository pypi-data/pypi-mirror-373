import pytest

from dkist_processing_common.models.fried_parameter import r0_valid


@pytest.mark.parametrize(
    "r0, ao_lock, oob_shift, should_r0_exist",
    [
        pytest.param(0.2, True, 17, True, id="AO_LOCK_True_good_R0_good_oob"),
        pytest.param(1, True, 17, False, id="AO_LOCK_True_bad_R0_good_oob"),
        pytest.param(0.2, False, 17, False, id="AO_LOCK_False_good_R0_good_oob"),
        pytest.param(1, False, 17, False, id="AO_LOCK_False_bad_R0_good_oob"),
        pytest.param(0.2, True, 150, False, id="AO_LOCK_True_good_R0_bad_oob"),
        pytest.param(1, True, 150, False, id="AO_LOCK_True_bad_R0_bad_oob"),
        pytest.param(0.2, False, 150, False, id="AO_LOCK_False_good_R0_bad_oob"),
        pytest.param(1, False, 150, False, id="AO_LOCK_False_bad_R0_bad_oob"),
        pytest.param(0.2, None, 17, False, id="AO_LOCK_missing"),
        pytest.param(0.2, True, None, True, id="OOBSHIFT_missing"),
    ],
)
def test_check_r0_valid(r0, ao_lock, oob_shift, should_r0_exist):
    """
    :Given: values for r0, the ao_lock status, and the ao out of bound shift value
    :When: checking for a valid state to use r0
    :Then: valid conditions are marked True, invalid conditions marked False
    """
    assert r0_valid(r0, ao_lock, oob_shift) == should_r0_exist
