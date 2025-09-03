Linearization
=============

Introduction
------------

Two of the DLNIRSP cameras (arms 2 and 3) use infrared (IR) H2RG detectors, which have non-linear response to light with increasing exposure time.
Because of this non-linear response, the count values at the final exposure do not accurately represent the light falling on the chip and therefore need to be corrected.
This correction is performed very early in the pipeline by the `~dkist_processing_dlnirsp.tasks.linearity_correction` task.

IR cameras make multiple readouts over the course of a single exposure and these readouts do not clear charge from the detector.
Because these reads are non-destructive they are referred to as Non-Destructive Readouts (NDRs).
The set of NDRs from the same exposure is called a ramp and typically the NDRs are evenly spaced over the full exposure time.
The linearization task uses all NDRs associated with a single ramp to compute what the final count values at the desired exposure time would be if the response of the detector was linear.
Thus, a single ramp (i.e., set of NDRs) is processed to produce a single "linearized" frame.

A ramp consists of 1 or more "bias" or "line" NDRs followed by a sequence of "read" NDRs.
The line NDRs serve to reset the camera and the read NDRs are used to acquire data.
A single set of line-then-read NDRs is called a "coadd" and a single ramp may contain multiple coadds to achieve higher signal-to-noise while keeping the exposure time of a single coadd low enough to avoid saturation.


Linearization Algorithms
------------------------

The IR cameras on DLNIRSP can operate in two different camera readout modes: "UpTheRamp" and "SubFrame", and each mode has a separate linearization strategy.
Furthermore, the "UpTheRamp" mode can be combined with either a "continuous" or "discrete" modulator spin mode.
The linearization algorithms for each combination of camera readout and modulator spin modes are described below.

**NOTE:** Before being sent to one of the algorithms described below, all ramp NDRs have a correction polynomial applied.
See `~dkist_processing_dlnirsp.tasks.linearity_correction.LinearityCorrection.apply_correction_polynomial` for more information.

UpTheRamp
^^^^^^^^^

Continuous Modulator Spin Mode
++++++++++++++++++++++++++++++

See `~dkist_processing_dlnirsp.tasks.linearity_correction.LinearityCorrection.linearize_uptheramp_continuous_coadd` for a more detailed description.

In this mode the modulator continues to spin while the ramp is being exposed and thus each NDR samples a slightly different modulator angle.
For this reason we cannot consider the ramp as a whole because each NDR is observing a slightly different input signal.
Each coadd is linearized by subtracting the last line NDR from the last read NDR; i.e., we only consider the most-exposed read NDR.
If a ramp contains multiple coadds then they are averaged together to produce the linearized frame.

Discrete Modulator Spin Mode
++++++++++++++++++++++++++++

See `~dkist_processing_dlnirsp.tasks.linearity_correction.LinearityCorrection.linearize_uptheramp_discrete_coadd` for a more detailed description.

In this mode the modulator is held at a fixed angle for the duration of the ramp, so each NDR samples the same input signal and thus the whole ramp can be considered during linearization.
Each coadd is linearized by first subtracting the last line NDR from all read NDRs.
The the slope of counts as a function of NDR is then computed separately as a function of each pixel.
The linearized value is this slope times the total number of reads in the coadd.
If a ramp contains multiple coadds then they are averaged together to produce the linearized frame.


SubFrame
^^^^^^^^

See `~dkist_processing_dlnirsp.tasks.linearity_correction.LinearityCorrection.linearize_subframe_coadd` for a more detailed description.

In this mode no bias subtraction is performed. The linearized value is simply the value of the last read NDR.
If a ramp contains multiple coadds then they are averaged together to produce the linearized frame.
