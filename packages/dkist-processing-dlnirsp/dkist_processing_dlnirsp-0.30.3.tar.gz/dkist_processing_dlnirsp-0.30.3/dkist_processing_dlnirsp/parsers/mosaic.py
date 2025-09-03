"""Bud to parse the number of subloops making up a mosaic."""

from collections import defaultdict
from datetime import datetime
from functools import cache
from functools import cached_property
from typing import Literal
from typing import Type

import numpy as np
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.task_name import TaskName
from dkist_service_configuration.logging import logger
from pydantic import BaseModel
from pydantic import ValidationInfo
from pydantic import field_validator

from dkist_processing_dlnirsp.models.constants import DlnirspBudName
from dkist_processing_dlnirsp.models.tags import DlnirspStemName
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspL0FitsAccess
from dkist_processing_dlnirsp.parsers.wcs_corrections import correct_crpix_values

cached_info_logger = cache(logger.info)
CRPIX_CORRECTION_TYPE_HINT = Literal["flip_crpix1", "swap_then_flip_crpix2"]
CRPIX_LABEL_TYPE_HINT = Literal["crpix_1", "crpix_2"]
SPATIAL_STEP_LABEL_TYPE_HINT = Literal["spatial_step_x", "spatial_step_y"]


class locking_cached_property(cached_property):
    """
    Version of `cached_property` that sets `_state_locked` to `True` when the property is accessed.

    This is useful for cases where we want to ensure the state of the class containing this property doesn't change
    after the property is computed once.
    """

    def __get__(self, instance, owner=None):
        """Set `instance._state_locked = True` while getting the cached value."""
        if instance is None:
            raise ValueError(f"{self.__class__.__name__} doesn't work outside a class instance")

        instance._state_locked = True

        return super().__get__(instance, owner)


class MosaicPiece(BaseModel):
    """Container and validator for storing header values used to assign mosaic location."""

    bin_crpix_to_multiple_of: int
    dither_step: int
    mosaic_num: int
    spatial_step_x: int
    spatial_step_y: int
    crpix_1: float
    crpix_2: float
    timestamp: float

    @field_validator("crpix_1", "crpix_2")
    @classmethod
    def round_float(cls, value: float, info: ValidationInfo) -> float:
        """Round CRPIX values so numeric jitter doesn't give the impression of more steps than actually exist."""
        # Note for future dev:
        # This method is currently the simplest way to deal with slightly different CRPIX values for the same mosaic tile.
        # It is possible that in the future DL will start taking very small mosaic steps that cause the idea of "a single
        # pipeline parameter to capture all DL mosaic steps"  to no longer be valid.
        # First, I'm sorry; this is frustrating.
        # Second, there are two more complicated methods that were considered at the time of this writing that you
        # might find useful:
        # 1. Organize the CRPIX values by their spatial step label and compute an average CRPIX for each spatial step.
        #    This seems very simple at first, but is made complicated by snakiness in the step pattern (i.e., a single
        #    spatial step label can have *two* CRPIX values). It would still require some idea of "the smallest
        #    difference allowed for two CRPIX values to be considered the same", but in this case the number might be
        #    easier to set in stone because it would be based on the mosaic size, not the mosaic *step* size.
        # 2. Look at using the DLSTP[XY] header keys, which describe the actual step size. This is essentially the
        #    "bin" amount we are trying to approximate here. This is made complicated by the fact that the header values
        #    have units of "urad", not px. To convert to px would require hard-coding instrument information (focal length,
        #    pixel pitch) that is not in the headers.
        target_multiple = info.data["bin_crpix_to_multiple_of"]
        return round(value / target_multiple) * target_multiple


class MosaicPieceBase(Stem):
    """
    Base class for identifying the organization of dither steps, mosaic repeats, X tiles, and Y tiles in a dataset.

    Header keys exist for all of these loop levels; this class exists to handle the logic of datasets that are aborted
    at different levels of the instrument loops.

    Each "piece" of the mosaic loop (dither, mosaic repeats, X tiles, Y tiles) is recorded for all OBSERVE frames so
    that derived classes can use this information to figure out how many pieces there are.
    """

    observe_task_name = TaskName.observe.value.casefold()

    # This only here so type-hinting of this complex dictionary will work.
    key_to_petal_dict: dict[str, MosaicPiece]

    def __init__(
        self,
        stem_name: str,
        crpix_correction_method: CRPIX_CORRECTION_TYPE_HINT,
        bin_crpix_to_multiple_of: int,
    ):
        super().__init__(stem_name=stem_name)
        self.crpix_correction_method = crpix_correction_method
        self.bin_crpix_to_multiple_of = bin_crpix_to_multiple_of

    def setter(self, fits_obj: DlnirspL0FitsAccess) -> Type[SpilledDirt] | MosaicPiece:
        """
        Extract the mosaic piece information from each frame and package in a tuple.

        Only OBSERVE frames are considered.
        """
        if fits_obj.ip_task_type.casefold() != TaskName.observe.value.casefold():
            return SpilledDirt

        dither_step = fits_obj.dither_step
        mosaic_num = fits_obj.mosaic_num
        spatial_step_x = fits_obj.X_tile_num
        spatial_step_y = fits_obj.Y_tile_num
        raw_crpix_1 = fits_obj.crpix_1
        raw_crpix_2 = fits_obj.crpix_2
        timestamp = datetime.fromisoformat(fits_obj.time_obs).timestamp()

        corrected_crpix_1, corrected_crpix_2 = correct_crpix_values(
            raw_crpix_1, raw_crpix_2, self.crpix_correction_method
        )

        return MosaicPiece(
            bin_crpix_to_multiple_of=self.bin_crpix_to_multiple_of,
            dither_step=dither_step,
            mosaic_num=mosaic_num,
            spatial_step_x=spatial_step_x,
            spatial_step_y=spatial_step_y,
            crpix_1=corrected_crpix_1,
            crpix_2=corrected_crpix_2,
            timestamp=timestamp,
        )

    def multiple_pieces_attempted_and_at_least_one_completed(
        self, piece_name: Literal["dither_step", "mosaic_num", "spatial_step_x", "spatial_step_y"]
    ) -> bool:
        """Return `True` if more than one of the requested pieces was attempted and at least one completed."""
        num_files_per_piece = self.num_files_per_mosaic_piece(piece_name)
        complete_piece_nums = self.complete_piece_list(num_files_per_piece)
        num_attempted_pieces = len(num_files_per_piece.keys())
        num_completed_pieces = len(complete_piece_nums)

        return num_attempted_pieces > 1 and num_completed_pieces > 0

    def num_files_per_mosaic_piece(
        self, piece_name: Literal["dither_step", "mosaic_num", "spatial_step_x", "spatial_step_y"]
    ) -> dict[int, int]:
        """
        Compute the number of files per each unique mosaic piece.

        For example, if each mosaic num usually has 4 files, but an abort resulted in the last one only having 2 then
        the output of this method would be `{0: 4, 1: 4, 2: 4, 3: 2}`.
        """
        num_files_per_piece = defaultdict(int)
        for mosaic_piece in self.key_to_petal_dict.values():
            num_files_per_piece[getattr(mosaic_piece, piece_name)] += 1

        return num_files_per_piece

    def complete_piece_list(self, num_files_per_piece_dict: dict[int, int]) -> list[int]:
        """
        Identify the identifiers of all complete mosaic pieces.

        "Completed" pieces are assumed to be those that have a number of files equal to the maximum number of files
        in any mosaic piece. This is a good assumption for now.
        """
        complete_piece_size = max(num_files_per_piece_dict.values())
        return [
            piece_num
            for piece_num, piece_size in num_files_per_piece_dict.items()
            if piece_size == complete_piece_size
        ]


class NumMosaicRepeatsBud(MosaicPieceBase):
    """
    Bud for determining the number of mosaic repeats.

    Only completed mosaics are considered.
    """

    def __init__(
        self, crpix_correction_method: CRPIX_CORRECTION_TYPE_HINT, bin_crpix_to_multiple_of: int
    ):
        super().__init__(
            stem_name=DlnirspBudName.num_mosaic_repeats.value,
            crpix_correction_method=crpix_correction_method,
            bin_crpix_to_multiple_of=bin_crpix_to_multiple_of,
        )

    def getter(self, key: str) -> int:
        """
        Return the number of *completed* mosaic repeats.

        A check is also made that the list of completed repeats is continuous from 0 to the number of completed repeats.
        """
        num_files_per_mosaic = self.num_files_per_mosaic_piece("mosaic_num")
        complete_mosaic_nums = self.complete_piece_list(num_files_per_mosaic)

        num_mosaics = len(complete_mosaic_nums)
        sorted_complete_mosaic_nums = sorted(complete_mosaic_nums)
        if sorted_complete_mosaic_nums != list(range(num_mosaics)):
            raise ValueError(
                f"Not all sequential mosaic repeats could be found. Found {sorted_complete_mosaic_nums}"
            )

        return num_mosaics


class NumDitherStepsBud(MosaicPieceBase):
    """
    Bud for determining the number of dither steps.

    If there are multiple mosaic repeats and any of them are complete then *all* dither steps are expected to exist.
    Otherwise the number of completed dither steps is returned.
    """

    def __init__(
        self, crpix_correction_method: CRPIX_CORRECTION_TYPE_HINT, bin_crpix_to_multiple_of: int
    ):
        super().__init__(
            stem_name=DlnirspBudName.num_dither_steps.value,
            crpix_correction_method=crpix_correction_method,
            bin_crpix_to_multiple_of=bin_crpix_to_multiple_of,
        )

    def getter(self, key: str) -> int:
        """
        Return the number of *completed* dither steps.

        Also check that the set of completed dither steps is either `{0}` or `{0, 1}` (because the max number of dither
        steps is 2).
        """
        num_files_per_dither = self.num_files_per_mosaic_piece("dither_step")
        if self.multiple_pieces_attempted_and_at_least_one_completed("mosaic_num"):
            # Only consider complete dither steps
            all_dither_steps = sorted(list(num_files_per_dither.keys()))
            num_dither_steps = len(all_dither_steps)
            if all_dither_steps != list(range(num_dither_steps)):
                raise ValueError(
                    f"Whole dither steps are missing. This is extremely strange. Found {all_dither_steps}"
                )
            return num_dither_steps

        complete_dither_nums = self.complete_piece_list(num_files_per_dither)

        num_dither = len(complete_dither_nums)

        if sorted(complete_dither_nums) != list(range(num_dither)):
            raise ValueError(
                f"Not all sequential dither steps could be found. Found {set(complete_dither_nums)}."
            )

        return num_dither


class XYMosaicTilesBase(MosaicPieceBase):
    """
    Base class for determining things that depend on knowing the loop order of [XY] mosaic tiles.

    As a child of `MosaicPieceBase` this class adds the ability to determine which mosaic loop (X or Y) was the
    outer loop. The order of loops is needed to accurately identify the number of "completed" mosaic pieces.

    This class also provides the ability to link the "spatial step" header keys to either CPRIX1 or CRPIX2 so that
    an *absolute* reference for the mosaic orientation can be determined regardless of what the spatial step pattern was
    or how CRPIX values were mapped to the *relative* mosaic orientation.
    """

    def __init__(
        self,
        stem_name: str,
        crpix_label: CRPIX_LABEL_TYPE_HINT,
        crpix_correction_method: CRPIX_CORRECTION_TYPE_HINT,
        bin_crpix_to_multiple_of: int,
    ) -> None:
        super().__init__(
            stem_name=stem_name,
            crpix_correction_method=crpix_correction_method,
            bin_crpix_to_multiple_of=bin_crpix_to_multiple_of,
        )
        self._state_locked = False
        self.crpix_label = crpix_label
        match crpix_label:
            case "crpix_1":
                self.opposite_crpix_label = "crpix_2"
            case "crpix_2":
                self.opposite_crpix_label = "crpix_1"
            case _:
                raise ValueError(f"I don't know the opposite CRPIX axis of {crpix_label}")

    def setter(self, fits_obj: DlnirspL0FitsAccess) -> Type[SpilledDirt] | MosaicPiece:
        """
        Disallow setting if a `locking_cached_property` has already been accessed.

        Otherwise, set as in `MosaicPieceBase.setter`.
        """
        if self._state_locked:
            raise ValueError(
                f"State of {self.__class__.__name__} has been locked. No more setting allowed."
            )
        return super().setter(fits_obj)

    @locking_cached_property
    def spatial_step_label(self) -> SPATIAL_STEP_LABEL_TYPE_HINT:
        """
        Compute the spatial step label (X or Y) associated with the CRPIX axis defined in this class.

        This calculation is needed because there is no guarantee that CRPIX1 *always* corresponds to spatial step direction
        "X", for example.

        We need to know the spatial step label associated with this CRPIX axis because the spatial step keys provide
        a quick and easy way to deal with aborted mosaics.

        The spatial step label corresponding to this Stem's crpix label is found by comparing the set of CRPIX values
        associated with each spatial step label; the spatial step label that has fewer unique CRPIX values is the one
        that corresponds to this Stem's crpix label. In other words, the spatial step label that stays constant with
        constant CRPIX value is the one that corresponds to this Stem's crpix label.

        The snaking spatial step pattern often used by DLNIRSP means that there's no guarantee that each CRPIX value
        corresponds to only a single spatial step ID; a single CRPIX value in the snaking dimension will correspond
        to two spatial step IDs (and maybe more with other patterns). In the case where this snaking causes ambiguity
        in the spatial step assignment we can consider the spatial step assignment of the *other* CRPIX value. One
        CRPIX value *should* always correspond to only a single spatial step ID.

        In the case of a mosaic with a single step we default to CRPIX1 -> spatial_step_x and CRPIX2 -> spatial_step_y
        because it doesn't matter.
        """
        avg_num_step_x_per_crpix = self.compute_avg_num_step_per_crpix(
            crpix_label=self.crpix_label, spatial_step_label="spatial_step_x"
        )
        avg_num_step_y_per_crpix = self.compute_avg_num_step_per_crpix(
            crpix_label=self.crpix_label, spatial_step_label="spatial_step_y"
        )

        ################
        # Weird step patterns can cause more than 1 spatial step to be associated with its true corresponding CRPIX
        # value. This `if` statement catches the case where the number of true associations is equal to the number
        # of steps in the other dimension.
        # In this case we need to look at the opposite CRPIX label, which should not suffer from multiple true
        # associations caused by weird step patterns. We then take the opposite spatial step label from the opposite
        # CRPIX label.
        if avg_num_step_y_per_crpix == avg_num_step_x_per_crpix:
            cached_info_logger(f"Snakiness detected in {self.crpix_label}")
            avg_num_step_x_per_opposite_crpix = self.compute_avg_num_step_per_crpix(
                crpix_label=self.opposite_crpix_label, spatial_step_label="spatial_step_x"
            )
            avg_num_step_y_per_opposite_crpix = self.compute_avg_num_step_per_crpix(
                crpix_label=self.opposite_crpix_label, spatial_step_label="spatial_step_y"
            )

            if (
                avg_num_step_x_per_crpix
                == avg_num_step_y_per_crpix
                == avg_num_step_x_per_opposite_crpix
                == avg_num_step_y_per_opposite_crpix
                == 1
            ):
                # One last special case. If there is only a single associated spatial step label for ALL CRPIX and
                # spatial step combinations then we have a single-tile mosic.
                # In this case we just hard-code the mapping because it doesn't matter.
                cached_info_logger("Only a single mosiac step detected")
                if self.crpix_label == "crpix_1":
                    return "spatial_step_x"
                return "spatial_step_y"

            if avg_num_step_x_per_opposite_crpix == avg_num_step_y_per_opposite_crpix:
                raise ValueError(
                    f"Both {self.crpix_label} and {self.opposite_crpix_label} show snakiness. This is unknown territory."
                )

            # Here's the logic of "use the opposite spatial step label as the opposite CRPIX label"
            if avg_num_step_x_per_opposite_crpix < avg_num_step_y_per_opposite_crpix:
                return "spatial_step_y"

            return "spatial_step_x"
        ################

        # The "normal" case; this Stem's CRPIX label corresponds to the spatial step label associated with the fewest
        # unique values.
        if avg_num_step_x_per_crpix < avg_num_step_y_per_crpix:
            return "spatial_step_x"

        return "spatial_step_y"

    def compute_avg_num_step_per_crpix(
        self,
        crpix_label: CRPIX_LABEL_TYPE_HINT,
        spatial_step_label: SPATIAL_STEP_LABEL_TYPE_HINT,
    ) -> float:
        """Compute the average number of unique spatial step IDs corresponding to a given CPRIX label."""
        crpix_step_dict = defaultdict(set)
        for piece in self.key_to_petal_dict.values():
            crpix_step_dict[getattr(piece, crpix_label)].add(getattr(piece, spatial_step_label))

        unique_step_per_crpix = [len(s) for s in crpix_step_dict.values()]

        avg_num_step_per_crpix = sum(unique_step_per_crpix) / len(unique_step_per_crpix)

        return avg_num_step_per_crpix

    def get_avg_delta_time_for_piece(self, piece_name: SPATIAL_STEP_LABEL_TYPE_HINT) -> float:
        """
        Compute the median length of time it took to observe all frames of a single X/Y tile index.

        This is different than the time to observe a single tile. For example, if the loop order is::

          spatial_step_x:
            spatial_step_y:

        then spatial_step_y index 0 won't be finished observing until the last spatial_step_x, while spatial_step_x
        index 0 will be finished as soon as all spatial_step_ys are observed once.
        """
        times_per_piece = defaultdict(list)
        for mosaic_piece in self.key_to_petal_dict.values():
            times_per_piece[getattr(mosaic_piece, piece_name)].append(mosaic_piece.timestamp)

        length_per_piece = [max(times) - min(times) for times in times_per_piece.values()]

        # median because an abort could cause a weirdly short piece
        return float(np.median(length_per_piece))

    @locking_cached_property
    def outer_loop_identifier(self) -> str:
        """
        Return the identified of the outer X/Y mosaic loop.

        The loop with the smaller time to complete a single index is the outer loop. See `get_avg_delta_time_for_piece`
        for more info.
        """
        avg_x_step_length = self.get_avg_delta_time_for_piece("spatial_step_x")
        avg_y_step_length = self.get_avg_delta_time_for_piece("spatial_step_y")

        if avg_x_step_length > avg_y_step_length:
            return "spatial_step_y"

        return "spatial_step_x"

    @locking_cached_property
    def any_outer_loop_attempted_multiple_times_and_completed_at_least_once(self) -> bool:
        """
        Return True if any outer loop completed at least once.

        The dither and mosaic loops are always "outer", and we also check if the other X/Y loop was outer to the loop
        in question.
        """
        dither_or_mosaic_completed = (
            self.multiple_pieces_attempted_and_at_least_one_completed("mosaic_num")  # fmt: skip
            or self.multiple_pieces_attempted_and_at_least_one_completed("dither_step")
        )

        opposite_tile_identifier = (
            "spatial_step_x" if self.spatial_step_label == "spatial_step_y" else "spatial_step_y"
        )

        if self.outer_loop_identifier == opposite_tile_identifier:
            return (
                dither_or_mosaic_completed
                or self.multiple_pieces_attempted_and_at_least_one_completed(opposite_tile_identifier)  # fmt: skip
            )

        return dither_or_mosaic_completed


class NumXYMosaicTilesBud(XYMosaicTilesBase):
    """
    Bud Class for determining the number of X and Y mosaic tiles.

    This class is a little different than other Buds because we don't know a priori if we're recording the number of
    X or Y tiles. Instead, a single instance of this Bud is associated with either CRPIX1 or CRPIX2, which define the
    *absolute* orientation of the mosaic, and once all frames have been ingested we can determine which spatial step
    direction was associated with the given CRPIX value.

    Most of that machinery comes from `XYMosaicTilesBase`. What this class provides is a `getter` that brings together
    all of this information (along with loop order methods also provided by `XYMosaicTilesBase`) to compute the number
    of absolute mosaic X/Y steps.
    """

    def __init__(
        self,
        stem_name: str,
        crpix_label: CRPIX_LABEL_TYPE_HINT,
        crpix_correction_method: CRPIX_CORRECTION_TYPE_HINT,
        bin_crpix_to_multiple_of: int,
    ):
        super().__init__(
            stem_name=stem_name,
            crpix_label=crpix_label,
            crpix_correction_method=crpix_correction_method,
            bin_crpix_to_multiple_of=bin_crpix_to_multiple_of,
        )

    def getter(self, key: str) -> int:
        """
        Return the number of X or Y tiles.

        First, the order of X/Y loops is established. If any outer loops (mosaic, dither, and the outer X/Y loop) were
        attempted and at least one is completed then all tiles are required to be complete, but if all outer loops are
        singular then the total number of tiles is considered to be the number of *completed* tiles.

        We also check that the set of tiles is continuous from 0 to the number of tiles.
        """
        cached_info_logger(f"Outer mosaic loop is {self.outer_loop_identifier}")
        num_files_per_tile = self.num_files_per_mosaic_piece(self.spatial_step_label)

        if self.any_outer_loop_attempted_multiple_times_and_completed_at_least_once:
            # The logic of this conditional is pretty subtle so here's an explanation:
            # If ANY outer-level loop has more than one iteration then ALL inner-level loops will be required
            # to be complete. This is why this is `or` instead of `and`. For example if num_dithers=2 but the mosaic
            # loop was not used (num_mosaic = 1) we still need all X tiles.
            all_tiles = sorted(list(num_files_per_tile.keys()))
            num_tiles = len(all_tiles)
            if all_tiles != list(range(num_tiles)):
                raise ValueError(
                    f"Whole {self.spatial_step_label}'s are missing. This is extremely strange. Found {all_tiles}"
                )
            return num_tiles

        # Otherwise (i.e., there are no completed mosaics, or we only observed a single mosaic) all tiles are valid
        completed_tiles = self.complete_piece_list(num_files_per_tile)

        num_tiles = len(completed_tiles)
        sorted_complete_tiles = sorted(completed_tiles)
        if sorted_complete_tiles != list(range(num_tiles)):
            raise ValueError(
                f"Not all sequential {self.spatial_step_label}'s could be found. Found {sorted_complete_tiles}"
            )

        return num_tiles


class NumMosaicXTilesBud(NumXYMosaicTilesBud):
    """Class for finding the number of mosaic tiles in the X (CRPIX1) direction."""

    def __init__(
        self, crpix_correction_method: CRPIX_CORRECTION_TYPE_HINT, bin_crpix_to_multiple_of: int
    ):
        super().__init__(
            stem_name=DlnirspBudName.num_mosaic_tiles_x.value,
            crpix_label="crpix_1",
            crpix_correction_method=crpix_correction_method,
            bin_crpix_to_multiple_of=bin_crpix_to_multiple_of,
        )


class NumMosaicYTilesBud(NumXYMosaicTilesBud):
    """Class for finding the number of mosaic tiles in the Y (CRPIX2) direction."""

    def __init__(
        self, crpix_correction_method: CRPIX_CORRECTION_TYPE_HINT, bin_crpix_to_multiple_of: int
    ):
        super().__init__(
            stem_name=DlnirspBudName.num_mosaic_tiles_y.value,
            crpix_label="crpix_2",
            crpix_correction_method=crpix_correction_method,
            bin_crpix_to_multiple_of=bin_crpix_to_multiple_of,
        )


class MosaicStepFlowerBase(XYMosaicTilesBase):
    """
    Base class for assigning mosaic positions to individual frames.

    The Spatial Step [XY] keys require knowledge of an internal mapping to correctly convert them to the mosaic X/Y grid.
    Unfortunately, this mapping is not stored in headers and can change from observation to observation, which makes
    using the spatial step keys very challenging. Fortunately the relative WCS information of each tile can be used to
    map out the mosaic grid.

    Flowers based on this class are used to identify the mosaic index of a *single* mosaic axis, corresponding to one of
    the CRPIX[12] header keys. The full set of all CRPIX[12] values across the entire mosaic is sorted and an individual
    file's mosaic index is the same as its index in the sorted list.

    The mosaic indices are used to identify tiles during processing and are written to L1 headers in the MINDEX{12} keys,
    which are indexed starting at 1 (FITS convention).

    Each mosaic and dither step is treated as a separate full mosaic when assigning mosaic index keys.
    """

    def __init__(
        self,
        tag_name: str,
        crpix_label: CRPIX_LABEL_TYPE_HINT,
        crpix_correction_method: CRPIX_CORRECTION_TYPE_HINT,
        bin_crpix_to_multiple_of: int,
    ):
        """Define which CRPIX[12] value this Flower corresponds to."""
        super().__init__(
            stem_name=tag_name,
            crpix_label=crpix_label,
            crpix_correction_method=crpix_correction_method,
            bin_crpix_to_multiple_of=bin_crpix_to_multiple_of,
        )

    @locking_cached_property
    def sorted_crpix_dict(self) -> dict[int, dict[int, list[float]]]:
        """
        Sort CRPIX values of completed tiles.

        By "completed" tiles we mean either all X/Y tiles if any outer loop completed at least one cycle. If no outer
        loops exist or completed one cycle then all found X/Y tiles are considered "complete.

        Values are first grouped by mosaic number and dither step.
        """
        cached_info_logger(f"{self.crpix_label} corresponds to {self.spatial_step_label}")
        num_files_per_spatial_step = self.num_files_per_mosaic_piece(self.spatial_step_label)

        # See `XYMosaicTilesBase.getter` for more info on this logic. Basically, if any outer loop completed one
        # cycle then *all* X/Y tiles need to be considered (because they exist in all completed outer loops).
        # If no outer loops completed then any tiles we have are considered "complete".
        if self.any_outer_loop_attempted_multiple_times_and_completed_at_least_once:
            completed_spatial_step_indices = list(num_files_per_spatial_step.keys())
        else:
            completed_spatial_step_indices = self.complete_piece_list(num_files_per_spatial_step)

        # Organize crpix values by mosaic and dither so the index mapping can be different for each one.
        # This would probably never happen, but it's easy to be aware of it.
        crpix_dict = defaultdict(lambda: defaultdict(list))
        for piece in self.key_to_petal_dict.values():
            spatial_step_value = getattr(piece, self.spatial_step_label)
            crpix_value = getattr(piece, self.crpix_label)
            if spatial_step_value in completed_spatial_step_indices:
                crpix_dict[piece.mosaic_num][piece.dither_step].append(crpix_value)

        # Sort the crpix values. Here is where we decide that the mosaic index origin will be at the smallest
        # (crpix1, crpix2) values.
        for mosaic_num_dict in crpix_dict.values():
            for dither_step, crpix_list in mosaic_num_dict.items():
                mosaic_num_dict[dither_step] = sorted(list(set(crpix_list)))

        return crpix_dict

    def getter(self, key: str) -> int:
        """Find the current axis mosaic index for the given frame."""
        current_mosaic_piece = self.key_to_petal_dict[key]
        current_mosaic_num = current_mosaic_piece.mosaic_num
        current_dither_step = current_mosaic_piece.dither_step
        current_crpix_value = getattr(current_mosaic_piece, self.crpix_label)

        sorted_crpix_list = self.sorted_crpix_dict[current_mosaic_num][current_dither_step]

        if current_crpix_value in sorted_crpix_list:
            # +1 because MINDEX keys are 1-indexed
            return sorted_crpix_list.index(current_crpix_value) + 1

        # Tag any frames dropped due to an abort with mosaic index -1
        return -1


class MosaicStepXFlower(MosaicStepFlowerBase):
    """Flower for finding the X location of a file in the mosaic."""

    def __init__(
        self, crpix_correction_method: CRPIX_CORRECTION_TYPE_HINT, bin_crpix_to_multiple_of: int
    ):
        super().__init__(
            tag_name=DlnirspStemName.mosaic_tile_x.value,
            crpix_label="crpix_1",
            crpix_correction_method=crpix_correction_method,
            bin_crpix_to_multiple_of=bin_crpix_to_multiple_of,
        )


class MosaicStepYFlower(MosaicStepFlowerBase):
    """Flower for finding the Y location of a file in the mosaic."""

    def __init__(
        self, crpix_correction_method: CRPIX_CORRECTION_TYPE_HINT, bin_crpix_to_multiple_of: int
    ):
        super().__init__(
            tag_name=DlnirspStemName.mosaic_tile_y.value,
            crpix_label="crpix_2",
            crpix_correction_method=crpix_correction_method,
            bin_crpix_to_multiple_of=bin_crpix_to_multiple_of,
        )
