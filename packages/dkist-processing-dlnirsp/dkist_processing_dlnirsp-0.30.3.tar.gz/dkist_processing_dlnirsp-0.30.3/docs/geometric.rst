Relative Wavelength Calibration
===============================

Introduction
------------

The `~dkist_processing_dlnirsp.tasks.geometric` task defines a single reference wavelength axis and computes the parameters
needed to align the spectrum of every single spatial pixel to this reference wavelength axis.
Generally speaking the algorithm is much like many other relative wavelength calibration algorithms: a reference spectrum
is identified and then all target spectra are shifted to align with this reference spectrum. Specifics unique to DLNIRSP
are described below.

It is important to note that this pipeline step does NOT compute an *absolute* wavelength calibration; it only ensures
that all spectra are on the same *relative* wavelength scale. Information about absolute wavelength calibration can be
found :doc:`here </wavelength_calibration>`.

Algorithm Details
-----------------

Identification of Reference Spectrum and Dispersion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The way the DLNIRSP IFU is projected onto the detector means that the same relatively small spectral range is repeated
many times across both dimensions of the FOV. As a result, any optical effects across the FOV can reduce the
homogeneity of the set of all spectra. A prime example of this is that spectra near the side of the detector usually
cover a smaller wavelength range than those near the center.

The reference spectrum is derived from an IFU group near to the center of the FOV because it will qualitatively be the
"median" spectrum of the entire array. To improve the signal-to-noise the reference spectrum is an average of the entire
spatial extent (~60 pixels) of the chosen IFU group.

The spectral dispersion (in angstrom / px) varies across the FOV and this variation is captured in one of the four :doc:`metrology arrays <ifu_drift>`.
To compute the reference dispersion we first compute the median dispersion of each of the 4 slits.
The reference dispersion is then the maximum dispersion across all slits. We use the maximum dispersion to ensure that
when we place each spectrum on the reference wavelength axis we are not "creating" data by artificially increasing the
resolution of any spectra. In other words, we degrade all spectra to the worst resolution present in the array.

The reference spectrum used to match all other spectra is the median spectrum re-scaled to the reference dispersion.

Aligning Spectra with Reference Spectra
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A linear function (i.e., a shift and a scale) is sufficient to capture the mapping from each spectrum's raw wavelength
axis to the reference spectrum's wavelength axis. The scale is fixed to be the ratio of the known dispersion to the reference dispersion,
and the shift is computed via a cross-correlation algorithm.

Creation of Reference Wavelength Axis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the shifts and scales for all spectra have been computed we can compute the global reference wavelength axis. This
is different than the wavelength axis of the reference spectrum because the single reference spectrum likely does not
cover the full spectral range sampled by *all* spectra. By considering the full range of shifts used across all spectra we compute the full range spectral needed to capture
all data present in the array.

The final output of this pipeline step are the reference wavelength axis and arrays containing the shifts and scales needed
to map each spectrum to that reference wavelength axis.
