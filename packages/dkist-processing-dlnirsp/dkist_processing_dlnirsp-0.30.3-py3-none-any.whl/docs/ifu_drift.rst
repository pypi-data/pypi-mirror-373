IFU Drift
=========

Background
----------

The DLNIRSP pipeline uses four pre-computed "metrology" arrays during science data reduction; one that identifies IFU groups,
one that contains the spectral dispersion for each pixel, and two that identify the X/Y locations of each pixel in the
remapped IFU image.
These metrology arrays are only updated when the instrument is physically changed and are therefore considered static on
an observation-to-observation time scale.
The location of the IFU image in the detector FOV does slowly change with time, however, and this "IFU drift" can cause
an offset between the static metrology arrays and observations taken much later than when the metrology arrays were computed.
The `~dkist_processing_dlnirsp.tasks.ifu_drift` task corrects for this drift and ensures that the metrology arrays are
aligned with the current dataset.

Algorithm
---------

The algorithm consists of measuring any drift between the metrology arrays and the current data and then removing the
drift by shifting all metrology arrays by the measured amount. These shifted metrology arrays are then used in the rest
of the pipeline.
The steps are:

#. Compute binary versions of representative arrays from the current dataset and the metrology arrays. The binary images
   are 1 where the detector is illuminated and 0 elsewhere; they essentially capture the illumination of the IFU on the detector.
   An averaged solar gain image is used for the current dataset, and the IFU group array is used to represent the metrology arrays.

#. Compute the pixel shift between the two binary images.

#. Apply the inverse of the measured shift to all four metrology arrays and save these shifted arrays for use in the rest
   of the pipeline. We currently only shift by whole pixel amounts to avoid any interpolation artifacts in the
   metrology arrays, which would severely impact their utility. Subpixel shifts would affect the pointing accuracy at the
   < 0.015" level, which is small.
