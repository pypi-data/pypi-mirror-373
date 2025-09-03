"""Parsing Stems for answering time-related questions."""

from typing import Hashable

from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.unique_bud import TaskUniqueBud

from dkist_processing_dlnirsp.models.constants import DlnirspBudName
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspRampFitsAccess
from dkist_processing_dlnirsp.parsers.task import parse_header_ip_task


class DLnirspSolarGainIpStartTimeBud(TaskUniqueBud):
    """Bud for finding the start time of the solar gain IP."""

    def __init__(self):
        super().__init__(
            constant_name=DlnirspBudName.solar_gain_ip_start_time.value,
            metadata_key="ip_start_time",
            ip_task_types=TaskName.solar_gain.value,
            task_type_parsing_function=parse_header_ip_task,
        )


class DlnirspTimeObsBud(Stem):
    """
    Produce a tuple of all time_obs values present in the dataset.

    The time_obs is a unique identifier for all raw frames in a single ramp. Hence, this list identifies all
    the ramps that must be processed in a data set.
    """

    def __init__(self):
        super().__init__(stem_name=DlnirspBudName.time_obs_list.value)

    def setter(self, fits_obj: DlnirspRampFitsAccess):
        """
        Set the time_obs for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The time_obs value associated with this fits object
        """
        return fits_obj.time_obs

    def getter(self, key: Hashable) -> Hashable:
        """
        Get the list of time_obs values.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        A tuple of exposure times
        """
        time_obs_tup = tuple(sorted(set(self.key_to_petal_dict.values())))
        return time_obs_tup
