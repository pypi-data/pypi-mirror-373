Polarization Calibration
========================

Introduction
------------

The `~dkist_processing_dlnirsp.tasks.instrument_polarization` pipeline task produces demodulation matrices from input polcal
data. For a more detailed background on how DKIST approaches polarization calibration please see
`this page about dkist-processing-pac <https://docs.dkist.nso.edu/projects/pac/en/stable/background.html>`_. Much of
the language and information in that page will be referenced here.

This page explains the specifics of how DLNIRSP produces demodulation matrices and how its approach differs from the general,
default strategy mentioned in the link above.

Important Features
------------------

There are two options that DLNIRSP uses to make it deviate from the "standard" polarization calibration routine, both of
which have import implications for the accuracy of L1 science data.

#. The total system throughput, :math:`I_{sys}`, is freely fit for every single GOS input state (i.e., Calibration
   Unit configuration). This change mitigates any variations in the total incident intensity that occur during a minutes-long PolCal
   data collection sequence (e.g., from solar granulation, humidity, etc.) and results in more precise fits to the Calibration Unit (CU)
   parameters. Note that this change necessitates fixing the CU retarder and polarizer transmission fractions to database
   values.

#. All "global" parameters are also fit during the "local" fits (using initial guesses from the global fits).
   In other words, the CU retardances (in addition to modulation matrices) are fit separately for each bin in the
   polcal data. (In the default polcal scheme only the modulation matrices are fit for each input bin). This change was
   made to correct for the real variations in the retardance of the calibration optics over the DLNIRSP FOV.

The change in #2 above is required because DLNIRSP computes a separate demodulation matrix for *every single spatial pixel*
(as described below).

Algorithm Detail
----------------

The general algorithm is:

#. Generate polcal-specific dark and gain calibrations, and apply to all POLCAL data.

#. Bin "global" and "local" sets of polcal data.

#. Pass the binned data to `dkist-processing-pac <https://docs.dkist.nso.edu/projects/pac/en/stable/index.html>`_ for fitting.

#. Smooth the resulting demodulation matrices in the spatial dimension.

Calibrate Input POLCAL Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^

All input POLCAL data undergo dark and gain correction prior to specific polarimetric analysis, but instead of using the
main `~dkist_processing_dlnirsp.tasks.dark` or :doc:`gain </gain>` images used by the rest of the pipeline they are
corrected with polcal-specific dark and gain images. Every Calibration Sequence (CS) used by DKIST includes two each of
"dark" and "clear" steps so that a single CS can be processed independent of any other data, and the DLNIRSP pipeline adopts
this methodology when processing POLCAL data.

Both the dark and gain images used to calibrated POLCAL data are simply averages of the respective CS steps.
:doc:`Full removal </gain>` of the solar spectrum from the gain images is unnecessary because tests show the polarimetric
response to be constant across the narrow wavelength ranges sampled by DLNIRSP.

Bin POLCAL Data
^^^^^^^^^^^^^^^

The DKIST PA&C (Polarization Analysis and Calibration) library requires `two types of inputs data <https://docs.dkist.nso.edu/projects/pac/en/stable/background.html#important-note-about-bins-and-the-calibration-unit-matrix>`_;
"global" and "local" data. The global data are used to fit Calibration Unit (CU) parameters and generally cover a large
FOV, while the local data define how fine the sampling of demodulation matrices is across the FOV. DLNIRSP averages
all data from a single beam into the global data and fits a demodulation matrix for every single spatial pixel. All
spectral pixels are collapsed to a single point with a simple median.

Send Data to dkist-processing-pac
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The "global" and "local" data are sent to `dkist-processing-pac` for fitting and demodulation matrix computation. See
`here <https://docs.dkist.nso.edu/projects/pac/en/stable/layout.html>`_ for detailed info.

Spatial Smoothing of Demodulation Matrices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The output of `dkist-processing-pac` is a single demodulation matrix for every spatial pixel. To reduce noise and harden
this output against spurious inputs these matrices are fit as a function spatial location. The current scheme is to compute
a separate polynomial fit for all pixels (~60px) in each IFU group. The order of polynomial is set via the
``dlnirsp_polcal_demodulation_spatial_poly_fit_order`` pipeline parameter and the fit is performed with an
`iterative outlier rejection algorithm <https://docs.astropy.org/en/stable/api/astropy.modeling.fitting.FittingWithOutlierRemoval.html>`_.

After smoothing the demodulation matrix values are expanded to fill the spectral dimension so that a demodulation matrix
exists for every single illuminated pixel. These matrices are then used to demodulate science data.
