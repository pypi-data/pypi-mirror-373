"""List of intermediate task names."""

from enum import StrEnum


class DlnirspTaskName(StrEnum):
    """Controlled list of DLNIRSP task tag names."""

    drifted_ifu_group_id = "DRIFTED_IFU_GROUP_ID"
    drifted_dispersion = "DRIFTED_DISPERSION"
    drifted_ifu_x_pos = "DRIFTED_IFU_XPOS"
    drifted_ifu_y_pos = "DRIFTED_IFU_YPOS"
    bad_pixel_map = "BAD_PIXEL_MAP"
    avg_unrectified_solar_gain = "AVG_UNRECT_SOLAR_GAIN"
    dispersion = "DISPERSION"
    wavelength_solution = "WAVELENGTH_SOLUTION"
