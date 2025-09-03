v0.28.0 (2025-07-03)
====================




- L1 data now have a correct wavelength solution encoded in their headers. See :doc:`here </wavelength_calibration>`
  for more information. (`#94 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/94>`__)


v0.27.0 (2025-06-26)
====================




- The :py:meth:`spatial fit <dkist_processing_dlnirsp.tasks.instrument_polarization.InstrumentPolarizationCalibration.fit_demodulation_matrices_by_group>`
  of demodulation entries can now be turned off with a pipeline parameter ("dlnirsp_polcal_demodulation_spatial_poly_fit_order").
  If the fit is turned off the resulting demodulation matrices will have more fine structure in the spatial dimension, which
  will change the L1 science data. It is expected that the spatial fit *will* be turned off by default. (`#95 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/95>`__)


v0.26.0 (2025-06-23)
====================




- Bad pixels in the input science data are now masked during the science task. We use Astropy's
  `interpolate_replace_nans <https://docs.astropy.org/en/stable/api/astropy.convolution.interpolate_replace_nans.html>`_
  to replace bad pixels with a local mean. The bad pixel locations are still preserved in the bad pixel map dataset extra. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/92>`__)


v0.25.0 (2025-06-03)
====================




- Add the ability to process IR data taken with "SubFrame" camera readout mode and the "UpTheRamp" readout mode combined
  with the "Discrete" modulator spin mode. Additionally, all linearization algorithms now apply a correction polynomial,
  so even data taken in "UpTheRamp" "Continuous" mode will have different linearized pixel values after this change.
  (`#71 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/71>`__)


v0.21.0 (2025-02-06)
====================




- L1 mosaic index header keys are now correctly populated based on an absolute orientation determined from the CRPIX[12] WCS values.
  In the past these header keys were straight copies of the DLNIRSP spatial step X/Y header keys, but this is wrong for a few reasons.
  First, the spatial step keys describe *relative* mosaic positions that need knowledge of the spatial step pattern to convert to an absolute orientation.
  The spatial step pattern is not encoded into L0 headers and would thus require out-of-channel communications to convert to an absolute orientation (bad).
  Second, in some cases the CRPIX values are swapped (see `#54 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/54>`__) and
  in these cases the "spatial X" direction will not be not be aligned with a consistent "X" direction as defined in the WCS (i.e., CRPIX1).
  This update sidesteps both issues by ignoring the spatial step X/Y keys and computing an absolute mosaic orientation based on the (potentially corrected)
  CRPIX[12] values. (`#57 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/57>`__)
- Mosaiced datasets will always have MAXIS = 2 in L1 headers, even if the mosaic only moved in one direction.
  This is so user interaction via `DKIST user tools <https://docs.dkist.nso.edu/projects/python-tools/en/latest/>`__ is consistent, regardless of how the mosaic was constructed. (`#57 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/57>`__)


v0.20.0 (2025-01-03)
====================




- Add a task that discovers bad pixels. Both IR and VIS cameras have static bad pixel maps provided by the DL team, and
  the IR cameras take an additional step of computing dynamic bad pixels from a combination of lamp gain data and the
  standard deviation over a stack of dark arrays. Pixels in the computed bad pixel map have their values set to NaN in two
  places: during binning when computing demodulation matrices, and during Science Calibration. Thus, bad pixels are NaN in
  L1 science data. (`#52 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/52>`__)


v0.19.0 (2024-12-20)
====================




- Apply corrections to the L1 WCS header values.
  The original WCS orientation was computed for the BIFOS-36 IFU, which is fiber-fed, and is flipped w.r.t to MISI-36, which uses mirrors to slice the image.
  Until a new WCS orientation is implemented, all MISI-36 data (i.e., *all* data) need to be corrected for this flip.
  Additionally, and update to the software of the field steering mirror temporarily introduced a flip in two WCS axes before it was fixed.
  Any data taken during this epoch need an additional correction. (`#54 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/54>`__)


v0.18.0 (2024-12-04)
====================




- Improvement to correcting relative scaling difference between the different slitbeams.
  Previously we had scaled the final gain image (which doesn't contain the solar spectrum) based on the relative scalings
  of raw solar gain images (which DO contain the solar spectrum). This approach worked reasonably well for spectral regions
  that were mostly continuum because any spectral lines didn't affect the overall median of the spectra. For regions with
  very little continuum, however, the large spectral signal could skew the overall scaling at the few percent level. This
  was most prevalent in the VIS arm. The updated algorithm uses two images with solar spectrum so the scaling is comparing
  apples to apples. (`#50 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/50>`__)


v0.15.0 (2024-10-15)
====================




- Spatial variations in the demodulation matrices are now fit on a per-IFU-group basis.
  First, a demodulation matrix is fit for every illuminated spatial pixel and these results are fit as a function of spatial pixel within each IFU group.
  These polynomial fits (order is a pipeline parameter) mitigate noise in the individual demodulation matrices.
  We still average all wavelengths in each spatial pixel because the demodulation matrices have been shown to be constant with wavelength. (`#39 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/39>`__)


v0.13.0 (2024-10-01)
====================




- Data taken in dither mode are now treated correctly. In this mode a second full mosaic is performed with a small offset
  for each mosaic repeat; the second set is the "dithered" step. Previously, the dithered step was considered to be part
  of the same (mosaic repeat, X tile, Y tile) step and thus averaged with the non-dithered step, but now the
  dither/non-dither steps are processed separately. If multiple dither steps exist in a dataset then a "dither step"
  dataset axis is added to the L1 inventory file. (`#31 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/31>`__)


v0.9.0 (2024-09-09)
===================




- Polcal fits are now done on a per-beam basis. Previously, a single fit to the Calibration Unit (CU) optics was performed
  for the entire DLNIRSP array. This essentially caused the two orthogonally polarized beams to cancel each other out for
  the CU fits. We now fit the CU optics separately for each beam and then use those results to also fit the demodulation
  matrices on a per-beam basis. (`#30 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/30>`__)


v0.8.0 (2024-09-04)
===================




- Linearization task now correctly handles multiple coadds. Previously we only processed the last coadd, but now all
  coadds are processed separately and then averaged together, which improves signal-to-noise. (`#28 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/28>`__)


v0.7.0 (2024-08-19)
===================




- Update linearity correction to average initial bias frames if more than one is found. Uses the last read NDR as opposed to the last NDR, which may be a bias NDR. (`#22 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/22>`__)


v0.6.0 (2024-07-30)
===================




- Two relatively minor changes to the solar gain algorithm have resulted in much improved science output. The biggest
  improvement is that the relative throughput differences between the slits are now correctly accounted for, which results
  in the same scaling across slit borders. The second change improves the separation of solar absorption lines from real gain
  differences and results in better gain correction overall. (`#25 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/25>`__)


v0.5.0 (2024-07-15)
===================




- L1 output files are now remapped, 3D IFU cubes with coordinates (LAT, LON, WAVE). The WCS information for the two spatial axes
  comes directly from the raw L0 frames and pre-computed IFU remapping files. (`#8 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/8>`__)


v0.1.0 (2024-06-06)
===================

- Initial release. Pipeline supports both BIFOS and MISI data and produces valid L1 frames. IFU-remapping is not yet implemented
  so the L1 files are presented as a single slit. WCS header values not guaranteed.
