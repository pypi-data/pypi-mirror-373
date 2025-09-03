L1 Science Calibration
======================

Introduction
------------

The `~dkist_processing_dlnirsp.tasks.science` module takes L0 input science frames and fully calibrates them into L1 science
products. This page describes the basic steps in this processes as well as import features of the DLNIRSP algorithm that
may not be obvious.

Important Features
------------------

Pixel Units
^^^^^^^^^^^

The :doc:`gain arrays </gain>` used to correct science data are *not* normalized; they retain their original input values.
As a result, pixel values in the L1 data will be normalized to the average solar signal at disk center on the day calibrations
were acquired (usually the same day as science acquisition). Note that this is **NOT** intended to be an accurate photometric calibration.

Beam Combination
^^^^^^^^^^^^^^^^

Apart from the order in which the basic corrections are applied (described below), it is important to state how the two
polarimetric beams of DLNIRSP are combined to produce a single L1 data frame. After demodulation the 4 Stokes components of
the two beams are combined thusly:

.. math::

  I_{comb} &= (I_1 + I_2) / 2 \\
  Q_{comb} &= I_{comb} \left(\frac{Q_1}{I_1} + \frac{Q_2}{I_2}\right) / 2 \\
  U_{comb} &= I_{comb} \left(\frac{U_1}{I_1} + \frac{U_2}{I_2}\right) / 2 \\
  V_{comb} &= I_{comb} \left(\frac{V_1}{I_1} + \frac{V_2}{I_2}\right) / 2,

where numbered subscripts correspond to beam number. This combination scheme improves the signal-to-noise of the data
and mitigates residual polarization artifacts caused by temporal-based modulation (e.g., atmospheric seeing).

When DLNIRSP operates in non-polarimetric mode the beam combination is a simple average.

L1 Coordinate System
^^^^^^^^^^^^^^^^^^^^

The science pipeline places L1 data into a coordinate frame that matches the coordinates used by SDO/HMI and HINDOE-SP.
Namely, -Q and +Q will be aligned parallel and perpendicular to the central meridian of the Sun, respectively.

IFU Remapping
^^^^^^^^^^^^^

The image-slicing natures of the DLNIRSP IFUs mean that L0 data are essentially 8 "slit spectra" (2 polarimetric beams
times 4 slits) stacked next to each other. The final step of the science pipeline is to remap these slit spectra into a
3D IFU cube. Part of instrument commissioning and maintenance is to produce a set of arrays that map detector pixel
coordinates to X/Y IFU coordinates and these arrays are used to produce the final IFU cube. A linear interpolator is
used convert spatial "slit" position to IFU X/Y position, but the wavelength dimension remains un-interpolated.

The final result is 3D array with one spectral dimension and two spatial that are consistent with the World Coordinate
Information encoded in the L0 headers.

Algorithm
---------

Input science data is processed into L1 science data via the following steps:

#. Average dark signal is subtracted from input data.

#. :doc:`Gain calibration </gain>` frame is divided from the data.

#. :doc:`Bad pixels </bad_pixel_calibration>` are masked using Astropy's `interpolate_replace_nans <https://docs.astropy.org/en/stable/api/astropy.convolution.interpolate_replace_nans.html>`_

#. Polarimetric data are demodulated.

#. Geometric/optical distortions are removed so that all spectra are on the same reference wavelength grid.

#. The beams are combined as described above.

#. Remove the polarization effects of all DKIST mirrors upstream of DLNIRSP. This step also includes the rotation into the coordinate frame described above.

#. Data are remapped into a 3D IFU cube.

#. The :doc:`absolute wavelength solution </wavelength_calibration>` is written to the L1 headers.
