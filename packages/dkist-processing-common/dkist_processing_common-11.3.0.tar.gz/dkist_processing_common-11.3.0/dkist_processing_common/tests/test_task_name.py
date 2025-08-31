from dkist_processing_common.models.tags import Tag
from dkist_processing_common.models.task_name import TaskName


def test_task_name_tags():
    """
    Given: A Tag class
    When: Access the task-specific task-type tags
    Then: The correct values are returned
    """
    assert Tag.task_observe() == f"TASK_{TaskName.observe.value}"
    assert Tag.task_polcal() == f"TASK_{TaskName.polcal.value}"
    assert Tag.task_polcal_dark() == f"TASK_{TaskName.polcal_dark.value}"
    assert Tag.task_polcal_gain() == f"TASK_{TaskName.polcal_gain.value}"
    assert Tag.task_dark() == f"TASK_{TaskName.dark.value}"
    assert Tag.task_gain() == f"TASK_{TaskName.gain.value}"
    assert Tag.task_lamp_gain() == f"TASK_{TaskName.lamp_gain.value}"
    assert Tag.task_solar_gain() == f"TASK_{TaskName.solar_gain.value}"
    assert Tag.task_geometric() == f"TASK_{TaskName.geometric.value}"
    assert Tag.task_geometric_angle() == f"TASK_{TaskName.geometric_angle.value}"
    assert (
        Tag.task_geometric_spectral_shifts() == f"TASK_{TaskName.geometric_spectral_shifts.value}"
    )
    assert Tag.task_geometric_offset() == f"TASK_{TaskName.geometric_offsets.value}"
    assert Tag.task_polcal() == f"TASK_{TaskName.polcal.value}"
