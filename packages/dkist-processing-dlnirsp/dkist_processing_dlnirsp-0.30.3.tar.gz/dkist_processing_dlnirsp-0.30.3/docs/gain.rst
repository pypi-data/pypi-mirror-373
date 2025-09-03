Gain Calibration
================

Introduction
------------

NOTE: The usage of the term "gain" throughout this document refers to total system response of the DKIST/DLNIRSP optical
train; it does NOT refer to the detector gain that has units of ADU / electron. Sometimes the term "flat" is used in
a way that is interchangeable with the usage of "gain" in this document.

NOTE pt 2: The DLNIRSP IFU creates 4 slits on the detector and each of these slits is further split into two orthogonally
polarized beams. We call a single beam from a single slit a "slitbeam"; there are 8 slitbeams in the DLNIRSP FOV.

DLNIRSP gain calibration is performed by the `~dkist_processing_dlnirsp.tasks.solar` task using the following procedure.
The important steps are described in more detail below.

#. Apply dark, lamp, and geometric corrections to all solar gain frames and average them together.

#. Compute a single characteristic solar spectrum across all slitbeams and place it into the full array.

#. Re-apply the geometric calibration (spectral shifts and scales) to the characteristic spectra.

#. Remove the redistorted characteristic solar spectra from the dark-corrected (but NOT lamp corrected) solar gain image.

The result is a single array that characterizes the system response of the full optical train upstream of the detectors.

Important Features
------------------

The final gain image is *not* normalized; it has be scaled so that each slitbeam retains its original input values.
As a result, pixel values in the L1 data will be normalized to the average solar signal at disk center on the day calibrations
were acquired (usually the same day as science acquisition). Note that this is **NOT** intended to be an accurate photometric calibration.

Algorithm Detail
----------------

Apply Dark, Lamp, and Geometric Corrections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step is mostly how it sounds. Importantly, all solar gain images are divided by the average lamp gain image, which
ensures that system illumination differences are not misidentified as true solar signal in the following steps. After
applying the :doc:`geometric correction </geometric>` all spectra will be on the reference wavelength grid.

Compute Characteristic Solar Spectrum
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A single characteristic spectrum is computed by taking the median over *all* spatial pixels across *all* slitbeams.
Earlier versions of the pipeline computed a characteristic spectrum for each of the 8 slitbeams, but some slitbeams were
found to have strong spectrally varying response that was more-or-less constant across the spatial extent of the slitbeam.
This response was then erroneously considered part of the characteristic "solar" spectrum of that slitbeam.
By considering *all* spatial pixels these spurious signals are averaged out.

Re-Distort Characteristic Spectra
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The single characteristic spectrum is placed at every spatial pixel and then re-distorted by applying the inverse of the
geometric corrections. The result is a "raw" array that contains only the solar spectrum.

Remove Characteristic Solar Spectra from Raw Solar Gain Frames
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The re-distorted solar spectra are divided from the dark-corrected solar gain frames. Because we don't use solar gains
with a lamp correction applied, the resulting gain image includes the full optical response of the system and can be
applied directly to the science data.

Right before this step the characteristic spectra is normalized by the median of its continuum level. This means that
the overall signal present in the dark-corrected solar gain frames is preserved and is how we ensure that L1 science data
are in units of signal relative to disk center.

Rescale Gain Image to Capture Slitbeam Differences
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When we computed a single characteristic solar spectrum across all slitbeams we lost information about any relative
overall scaling between the slitbeams. In this step we rescale each slitbeam in the gain image so that it has the
same average counts as the corresponding slitbeam in the average dark-corrected solar gain image. Thus, when this scaled
gain is applied to science data the different slitbeam response will be corrected.

A side-effect of this step is that the final gain image has units of counts. This means that L1 output arrays will have
units of average signal at solar disk center (where the solar gains are observed).
