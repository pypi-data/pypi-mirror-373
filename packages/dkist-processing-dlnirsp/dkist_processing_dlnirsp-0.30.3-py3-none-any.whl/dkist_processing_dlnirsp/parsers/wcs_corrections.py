"""Module to contain functions that are used throughout the pipeline to correct incoming WCS header information."""

from typing import Literal

import numpy as np
from astropy.io import fits


def correct_crpix_values(
    crpix1: float, crpix2: float, correction_method: Literal["flip_crpix1", "swap_then_flip_crpix2"]
) -> tuple[float, float]:
    """
    Correct CRPIX[12] values based on a provided correction method.

    Returns
    -------
    (corrected crpix1, corrected crpix2)
    """
    match correction_method:
        case "flip_crpix1":
            crpix1 = -1 * crpix1

        case "swap_then_flip_crpix2":
            crpix1, crpix2 = crpix2, -crpix1

        case _:
            raise ValueError(f"No CRPIX correction method defined for '{correction_method}'")

    return crpix1, crpix2


def correct_header_PC_matrix(header: fits.Header, pc_correction_matrix: np.ndarray) -> fits.Header:
    """
    Apply a correction matrix to the PCi_j matrix encoded in a FITS header.

    Parameters
    ----------
    header
      A `fits.Header` object that contains PC[12]_[12] keys

    pc_correction_matrix
      A 2x2 numpy array containg the correction matrix

    Returns
    -------
    `fits.Header`
       The same header, but with updated PC[12]_[12] keys
    """
    PC_matrix = np.empty((2, 2))
    PC_matrix[0, 0] = header["PC1_1"]
    PC_matrix[0, 1] = header["PC1_2"]
    PC_matrix[1, 0] = header["PC2_1"]
    PC_matrix[1, 1] = header["PC2_2"]

    correction_matrix = pc_correction_matrix

    corrected_PC_matrix = PC_matrix @ correction_matrix
    header["PC1_1"] = corrected_PC_matrix[0, 0]
    header["PC1_2"] = corrected_PC_matrix[0, 1]
    header["PC2_1"] = corrected_PC_matrix[1, 0]
    header["PC2_2"] = corrected_PC_matrix[1, 1]

    return header
