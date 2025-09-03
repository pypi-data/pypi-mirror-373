"""Dataset-level constants for a pipeline run."""

from enum import Enum

import astropy.units as u
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.constants import ConstantsBase


class DlnirspBudName(Enum):
    """Names to be used for DLNIRSP buds."""

    arm_id = "ARM_ID"
    num_beams = "NUM_BEAMS"
    num_dsps_repeats = "NUM_DSPS_REPEATS"  # TODO: Maybe we don't need this?
    num_dither_steps = "NUM_DITHER_STEPS"
    num_mosaic_repeats = "NUM_MOSAIC_REPEATS"
    num_mosaic_tiles_x = "NUM_MOSAIC_TILES_X"
    num_mosaic_tiles_y = "NUM_MOSAIC_TILES_Y"
    num_modstates = "NUM_MODSTATES"
    wavelength = "WAVELENGTH"
    polarimeter_mode = "POLARIMETER_MODE"
    time_obs_list = "TIME_OBS_LIST"
    lamp_gain_exposure_times = "LAMP_GAIN_EXPOSURE_TIMES"
    solar_gain_exposure_times = "SOLAR_GAIN_EXPOSURE_TIMES"
    polcal_exposure_times = "POLCAL_EXPOSURE_TIMES"
    observe_exposure_times = "OBSERVE_EXPOSURE_TIMES"
    non_dark_task_exposure_times = "NON_DARK_TASK_EXPOSURE_TIMES"
    arm_position_mm = "ARM_POSITION_MM"
    grating_constant_inverse_mm = "GRATING_CONSTANT_INVERSE_MM"
    grating_position_deg = "GRATING_POSITION_DEG"
    solar_gain_ip_start_time = "SOLAR_GAIN_IP_START_TIME"


VIS_ARM_NAMES = ["VIS".casefold()]
IR_ARM_NAMES = ["JBand".casefold(), "HBand".casefold()]


class DlnirspConstants(ConstantsBase):
    """DLNIRSP specific constants to add to the common constants."""

    @property
    def arm_id(self) -> str:
        """Arm used to record the data, either VIS or one of 2 IR bands."""
        return self._db_dict[DlnirspBudName.arm_id]

    @property
    def is_ir_data(self) -> bool:
        """Return True if the data are from an IR camera and need to be linearized."""
        if self.arm_id.casefold() in VIS_ARM_NAMES:
            return False
        if self.arm_id.casefold() in IR_ARM_NAMES:
            return True
        raise ValueError(f"Unable to determine the camera type of Arm ID {self.arm_id}")

    @property
    def num_beams(self) -> int:
        """Determine the number of beams present in the data."""
        return 2

    @property
    def num_slits(self) -> int:
        """Return the number of slits on a single detector readout."""
        return 4

    @property
    def num_dither_steps(self) -> int:
        """Return the number of dither steps."""
        return self._db_dict[DlnirspBudName.num_dither_steps]

    @property
    def num_mosaic_repeats(self) -> int:
        """
        Return the number of mosaic repeats.

        I.e., the number of times the mosaic pattern was observed.
        """
        return self._db_dict[DlnirspBudName.num_mosaic_repeats]

    @property
    def num_mosaic_tiles_x(self) -> int:
        """Return the number of tiles in the X direction in the mosaic grid."""
        return self._db_dict[DlnirspBudName.num_mosaic_tiles_x]

    @property
    def num_mosaic_tiles_y(self) -> int:
        """Return the number of tiles in the Y direction in the mosaic grid."""
        return self._db_dict[DlnirspBudName.num_mosaic_tiles_y]

    @property
    def num_mosaic_tiles(self) -> int:
        """Return the total number of tiles that make up the full mosaic."""
        return self.num_mosaic_tiles_x * self.num_mosaic_tiles_y

    @property
    def num_cs_steps(self):
        """Find the number of calibration sequence steps."""
        return self._db_dict[BudName.num_cs_steps]

    @property
    def time_obs_list(self) -> list[str]:
        """Construct a list of all the dateobs for this dataset."""
        return self._db_dict[DlnirspBudName.time_obs_list]

    @property
    def wavelength(self) -> float:
        """Wavelength."""
        return self._db_dict[DlnirspBudName.wavelength]

    @property
    def correct_for_polarization(self) -> bool:
        """Return True if dataset is polarimetric."""
        # TODO: Check what the option "Other" for DLPOLMD means
        return self._db_dict[DlnirspBudName.polarimeter_mode] == "Full Stokes"

    @property
    def pac_init_set(self):
        """Return the label for the initial set of parameter values used when fitting demodulation matrices."""
        retarder_name = self._db_dict[BudName.retarder_name.value]
        match retarder_name:
            case "SiO2 OC":
                return "OCCal_VIS"
            case _:
                raise ValueError(f"No init set known for {retarder_name = }")

    @property
    def lamp_gain_exposure_times(self) -> list[float]:
        """Construct a list of lamp gain FPA exposure times for the dataset."""
        return self._db_dict[DlnirspBudName.lamp_gain_exposure_times]

    @property
    def solar_gain_exposure_times(self) -> list[float]:
        """Construct a list of solar gain FPA exposure times for the dataset."""
        return self._db_dict[DlnirspBudName.solar_gain_exposure_times]

    @property
    def polcal_exposure_times(self) -> list[float]:
        """Construct a list of polcal FPA exposure times for the dataset."""
        if self.correct_for_polarization:
            return self._db_dict[DlnirspBudName.polcal_exposure_times]
        else:
            return []

    @property
    def observe_exposure_times(self) -> list[float]:
        """Construct a list of observe FPA exposure times."""
        return self._db_dict[DlnirspBudName.observe_exposure_times]

    @property
    def non_dark_task_exposure_times(self) -> list[float]:
        """Return a list of all exposure times required for all tasks other than dark."""
        exposure_times = list()
        exposure_times.extend(self.lamp_gain_exposure_times)
        exposure_times.extend(self.solar_gain_exposure_times)
        exposure_times.extend(self.observe_exposure_times)
        exposure_times = list(set(exposure_times))
        return exposure_times

    @property
    def num_modstates(self) -> int:
        """Return the number of modulator states."""
        return self._db_dict[DlnirspBudName.num_modstates]

    @property
    def solar_gain_ip_start_time(self) -> str:
        """Solar gain IP start time."""
        return self._db_dict[DlnirspBudName.solar_gain_ip_start_time.value]

    @property
    def arm_position_mm(self) -> u.Quantity:
        """Arm linear state position (mm)."""
        return self._db_dict[DlnirspBudName.arm_position_mm] * u.mm

    @property
    def grating_constant_inverse_mm(self) -> u.Quantity:
        """Grating constant (1/mm)."""
        return self._db_dict[DlnirspBudName.grating_constant_inverse_mm.value] / u.mm

    @property
    def grating_position_deg(self) -> u.Quantity:
        """Grating position angle (deg)."""
        return self._db_dict[DlnirspBudName.grating_position_deg.value] * u.deg
