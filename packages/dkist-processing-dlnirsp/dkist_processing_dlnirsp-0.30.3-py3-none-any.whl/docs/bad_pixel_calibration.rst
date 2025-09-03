Bad Pixel Calibration
=====================

Introduction
------------

Both the Visible and IR cameras used by DLNIRSP contain a number of bad pixels and the `~dkist_processing_dlnirsp.tasks.bad_pixel_map`
task identifies these pixels so they can be treated properly in downstream tasks. Knowledge of the locations of bad
pixels (i.e., the bad pixel map) comes from two sources:

#. A "static" bad pixel map that is provided by the DLNIRSP team. These maps identify known defects in the cameras (e.g.
   bad columns) that are constant across time. They can be updated if instrument conditions change, but this happens
   infrequently.

#. A "dynamic" bad pixel map that is computed once per L1 dataset (i.e., pipeline run). These maps identify hot, cold, or
   otherwise deviant pixels that may not be constant with time. Only the IR cameras undergo this step.

Correcting Bad Pixels
---------------------

There are two places in the pipeline where a bad pixel value can negatively affect science results:

#. When computing demodulation matrices in the `~dkist_processing_dlnirsp.tasks.instrument_polarization` task
   raw POLCAL data are binned before being sent to `dkist-processing-pac <https://docs.dkist.nso.edu/projects/pac/en/stable>`_
   for analysis. Any bad pixel values would skew this binning and lead to inaccuracies in the computed demodulation matrices.
   We remove the effect of bad pixel values by simply setting all known bad pixels to NaN; all binning and analysis
   algorithms ignore NaN values by default.

#. Bad pixel values in the OBSERVE frames directly become erroneous values in L1 science data. Bad pixels in the input
   science data are interpolated over during the science task. We use Astropy's
   `interpolate_replace_nans <https://docs.astropy.org/en/stable/api/astropy.convolution.interpolate_replace_nans.html>`_
   for this step. This step is done prior to any other interpolation (e.g., to apply the
   :doc:`relative wavelength correction </geometric>`). The kernel size used by the bad pixel masking routine is a
   pipeline parameter.

Algorithm Detail
----------------

**NOTE:** These steps are used to find "dynamic" bad pixel locations in IR cameras. As mentioned above, the Visible
camera only uses the "static" bad pixel map provided by the DLNIRSP team.

Dynamic bad pixel locations in IR data are identified from two sources: an averaged, dark corrected lamp gain image, and
the per-pixel standard deviation of all DARK frames used to correct the lamp image. The lamp gain image is used to
identify pixels that are consistently bad, while the per-pixel standard deviation of the DARK frames finds pixels that
have highly unstable responses from exposure to exposure. For both sources the algorithm is the same:

#. Smooth the input image (either a dark corrected lamp gain, or the per-pixel standard deviation over DARK frames)
   with a median filter. The shape of the smoothing window is a pipeline parameter, but is different for each of the
   two input types.

#. Subtract the input image and smoothed image.

#. Identify pixels in the difference image that are more than a specific number of standard deviations (of the
   difference image) away from zero. These are the "dynamic" bad pixels.

The bad pixels from both input types are combined, along with the static bad pixel map, to produce the final bad pixel
map used during calibrations.
