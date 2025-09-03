"""Subclass of AssembleQualityData that causes the correct polcal metrics to build."""

from dkist_processing_common.tasks import AssembleQualityData

__all__ = ["DlnirspAssembleQualityData"]


class DlnirspAssembleQualityData(AssembleQualityData):
    """Subclass just so that the polcal_label_list can be populated."""

    @property
    def polcal_label_list(self) -> list[str]:
        """Return labels for beams 1 and 2."""
        return ["Beam 1", "Beam 2"]
