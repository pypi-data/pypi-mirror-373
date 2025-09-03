"""
Helpers for identifying and/or extracting sub-arrays corresponding to specific 'groups' of the IFU.

A group is a single mirror slice of MISI. A group corresponds to a single beam (i.e., each beam is a separate group).
"""

from collections import defaultdict
from functools import cached_property

import numpy as np
from dkist_processing_common.codecs.asdf import asdf_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder

from dkist_processing_dlnirsp.models.tags import DlnirspTag


class GroupIdMixin:
    """
    Mixin for methods that identify and/or extract sub-arrays corresponding to specific IFU groups.

    Each group is a single mirror slice of MISI. A group corresponds to a single beam (i.e., each beam is a separate group).
    """

    @cached_property
    def group_id_drifted_id_array(self) -> np.ndarray:
        """Return the group ID array with IFU drift applied."""
        try:
            drifted_group_array = next(
                self.read(
                    tags=[
                        DlnirspTag.intermediate_frame(),
                        DlnirspTag.task_drifted_ifu_groups(),
                    ],
                    decoder=fits_array_decoder,
                )
            )
        except StopIteration:
            raise ValueError(
                "Could not find the drifted group ID array. Has IfuDriftCalibration been run?"
            )

        return drifted_group_array

    def group_id_get_idx(
        self, *, group_id: int, rectified: bool = False
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Get the indices that locate a single group in the full-frame array.

        Parameters
        ----------
        rectified
          If True then return indices that locate a single group in a rectified array (i.e., geometric correction
          applied so all spectra are on an identical wavelength grid). This kwarg is usually set automatically by
          helper functions; it's unlikely you'll ever need to use this.
        """
        group_id_array = (
            self.group_id_drifted_id_array if not rectified else self.rectified_group_id_array
        )
        idx = np.where(group_id_array == group_id)
        return idx

    def group_id_get_data_and_idx(
        self,
        *,
        data: np.ndarray,
        group_id: int,
    ) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray]]:
        """
        Return data associated with a single group and the indices of those data's location in the full-frame array.

        NOTE: The indices returned do NOT produce the shape of the returned data. In other words:

            >>> group_data, group_idx = self.group_id_get_data_and_idx(data, group_id)
            >>> group_data.shape == data[group_idx].shape
            False

        To convert the returned indices to a slice that will produce a 2D group array use
        `self.group_id_convert_idx_to_2d_slice`.

        Parameters
        ----------
        data
            Array from which to extract the given group

        group_id
            ID of the desired group
        """
        # Because we only slice along the first 2 axis (spatial, spectral) we only need to check that the first
        # two axis have the correct shape. This allows higher-dimensional array (like demodulation matrices) to
        # be processed correctly.
        data_shape = data.shape[:2]
        if data_shape == self.unrectified_array_shape:
            rectified = False
        elif data_shape == self.rectified_array_shape:
            rectified = True
        else:
            raise ValueError(
                f"Input data shape ({data_shape}) doesn't match either the un-rectified "
                f"({self.unrectified_array_shape}) or rectified ({self.rectified_array_shape}) group-id array shape"
            )

        idx = self.group_id_get_idx(group_id=group_id, rectified=rectified)
        slices = self.group_id_convert_idx_to_2d_slice(idx)
        group_data = data[slices]
        return group_data, idx

    def group_id_get_data(
        self,
        *,
        data: np.ndarray,
        group_id: int,
    ) -> np.ndarray:
        """
        Get the data for a single group.

        Parameters
        ----------
        data
            Array from which to extract the given group

        group_id
            ID of the desired group
        """
        return self.group_id_get_data_and_idx(
            data=data,
            group_id=group_id,
        )[0]

    def group_id_convert_idx_to_2d_slice(
        self,
        indices: tuple[np.ndarray, np.ndarray],
    ) -> tuple[slice, slice]:
        """
        Convert a tuple of arrays corresponding to group_id indices into a tuple of slices that produce 2D output.

        This is needed because a ND numpy array sliced with a tuple of index arrays will always be 1D. For DL, we know
        that the groups are contiguous regions in a 2D array so we can use the index arrays to compute slices that
        return these regions.

        This is done by simply grabbing pixels that fall in the (min, max) range of the index array for each dimension.

        Parameters
        ----------
        indices
            A tuple containing the spatial and spectral index arrays, in that order.
        """
        if len(indices) != 2:
            raise ValueError(
                f"Expected indices to be 2 dimensional. These have length {len(indices)}."
            )

        spatial_index, spectral_index = indices
        spatial_slice = slice(spatial_index.min(), spatial_index.max() + 1)

        spectral_min, spectral_max = self.ensure_uniform_spectral_size(
            spatial_index, spectral_index
        )
        spectral_slice = slice(spectral_min, spectral_max + 1)

        return spatial_slice, spectral_slice

    def ensure_uniform_spectral_size(
        self, spatial_idx: np.ndarray, spectral_idx: np.ndarray
    ) -> tuple[int, int]:
        """
        Make sure we're returning rectangular regions. I.e., a uniform spectral size for all spatial pixels.

        We do this by truncating the data to the smallest complete rectangle.
        """
        get_spectral_minmax = lambda idx: (spectral_idx[np.min(idx)], spectral_idx[np.max(idx)])
        unique_spatial_px = np.unique(spatial_idx)
        minmax_per_spatial_pix = [
            get_spectral_minmax(np.where(spatial_idx == spatial_px))
            for spatial_px in unique_spatial_px
        ]

        maximum_min_value = max(v[0] for v in minmax_per_spatial_pix)
        minimum_max_value = min(v[1] for v in minmax_per_spatial_pix)

        return maximum_min_value, minimum_max_value

    @cached_property
    def group_id_slitbeam_group_dict(self) -> dict[int, list[int]]:
        """Return a dictionary containing the group id's associated with each slitbeam."""
        num_groups = self.group_id_num_groups
        slit_separation = self.parameters.group_id_rough_slit_separation_px

        slitbeam_group_dict = defaultdict(list)
        current_slitbeam = 0
        current_spectral_center = self.get_spectral_center_of_both_beams(even_group_id=0)
        for group_id in range(0, num_groups, 2):
            spectral_center = self.get_spectral_center_of_both_beams(even_group_id=group_id)
            if abs(spectral_center - current_spectral_center) > slit_separation:
                current_slitbeam += 2
                current_spectral_center = spectral_center

            slitbeam_group_dict[current_slitbeam].append(group_id)  # Even beam
            slitbeam_group_dict[current_slitbeam + 1].append(group_id + 1)  # Odd beam

        # cast as `dict` so downstream users don't add extra keys with the default value
        return dict(slitbeam_group_dict)

    @cached_property
    def rectified_group_id_array(self) -> np.ndarray:
        """
        Return a rectified version of the group_id array.

        This is different than applying the geometric correction (rectification) to the group ID array because here we
        want the entire spectral range of the larger groups to contain the group ID. Thus, this array can be used to
        identify whole rectified groups, not just the portion that contained data in the raw frame.
        """
        try:
            geometric_correction = next(
                self.read(
                    tags=[DlnirspTag.intermediate(), DlnirspTag.task_geometric()],
                    decoder=asdf_decoder,
                )
            )
            reference_wave_axis = geometric_correction["reference_wavelength_axis"]
        except:
            raise FileNotFoundError(
                "Could not find the reference wavelength array. Has GeometricCalibration been run?"
            )

        output_stack = []
        for slitbeam, group_ids in self.group_id_slitbeam_group_dict.items():
            slitbeam_array = (
                np.zeros((self.group_id_drifted_id_array.shape[0], reference_wave_axis.size))
                * np.nan
            )
            for group_id in group_ids:
                group_idx = self.group_id_get_idx(group_id=group_id)
                spatial_slice = self.group_id_convert_idx_to_2d_slice(group_idx)[0]
                slitbeam_array[spatial_slice, :] = group_id

            output_stack.append(slitbeam_array)

        rectified_group_id_array = np.hstack(output_stack)

        return rectified_group_id_array

    @property
    def unrectified_array_shape(self) -> tuple[int, int]:
        """Return the shape of un-rectified data."""
        return self.group_id_drifted_id_array.shape

    @property
    def rectified_array_shape(self) -> tuple[int, int]:
        """Return the shape of rectified data."""
        return self.rectified_group_id_array.shape

    def get_spectral_center_of_both_beams(self, even_group_id: int) -> float:
        """Get the spectral pixel at the midpoint between the two beams of a single mirror slice."""
        if even_group_id % 2 != 0:
            raise ValueError("Only even groups are supported")

        odd_beam_group_id = even_group_id + 1
        even_beam_spectral_range = self.group_id_get_idx(group_id=even_group_id)[1]
        odd_beam_spectral_range = self.group_id_get_idx(group_id=odd_beam_group_id)[1]

        spectral_center = float(np.median(np.r_[even_beam_spectral_range, odd_beam_spectral_range]))
        return spectral_center

    @property
    def group_id_illuminated_idx(self) -> np.ndarray:
        """Return indices for all portions of the array that are part of any group."""
        return ~np.isnan(self.group_id_drifted_id_array)

    @property
    def group_id_rectified_illuminated_idx(self) -> np.ndarray:
        """Return indices for all portions of the rectified array that are part of any group."""
        return ~np.isnan(self.rectified_group_id_array)

    # TODO: This probably should be in Constants, but it's not obvious how to do that in a good way.
    @property
    def group_id_num_groups(self) -> int:
        """Return the total number of groups present in the full array."""
        return int(np.nanmax(self.group_id_drifted_id_array) + 1)
