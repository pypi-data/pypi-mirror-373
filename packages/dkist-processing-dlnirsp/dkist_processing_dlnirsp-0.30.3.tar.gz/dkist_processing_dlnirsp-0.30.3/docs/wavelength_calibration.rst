Absolute Wavelength Calibration
===============================

Introduction
------------

Once all spectra are on the same :doc:`relative wavelength axis </geometric>` an absolute wavelength solution is computed
with the `~dkist_processing_dlnirsp.tasks.wavelength_calibration` task and encoded in the L1 headers.
The solution is computed with the
`solar-wavelength-calibration <https://docs.dkist.nso.edu/projects/solar-wavelength-calibration/en/latest/>`_ library
and the details of the fitting algorithm can be found at that link. Generally, the steps the DL-NIRSP pipeline runs through
are:

#. Compute a representative spectrum by taking a spatial average near the center of the FOV of an average of all solar gain images.

#. Use the L0 headers to construct a decent first-guess for the wavelength solution.

#. Feed both the representative spectrum and initial guess into the `solar-wavelength-calibration <https://docs.dkist.nso.edu/projects/solar-wavelength-calibration/en/latest/>`_ library.

#. Save the fit result as a set of header values that parameterize the solution (see below).

Important Features
------------------

Encoding the Wavelength Solution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The computed wavelength solution is not used to interpolate data onto a linear grid. Instead we simply update the header
values of L1 data during the `~dkist_processing_dlnirsp.tasks.write_l1` task.

The final wavelength solution uses the parameterization of `Greisen et al (2006) <https://ui.adsabs.harvard.edu/abs/2006A%26A...446..747G/abstract>`_
for non-linear wavelength vectors from reflection gratings. The full parameterization is (see Section 5 and Table 6 of
the linked paper for more information)

+---------+--------------------------+----------------+
| Keyword | Description              | Units          |
+=========+==========================+================+
| `CTYPE3`| Type of spectral         |                |
|         | coordinate.              |                |
|         | Aways "AWAV-GRA"         |                |
+---------+--------------------------+----------------+
| `CUNIT3`| Unit for CRVALn and      |                |
|         | CDELTn. Always "nm"      |                |
+---------+--------------------------+----------------+
| `CRPIX3`| Reference pixel          |                |
+---------+--------------------------+----------------+
| `CRVAL3`| Reference wavelength     | nm             |
+---------+--------------------------+----------------+
| `CDELT3`| Linear dispersion        | nm / px        |
+---------+--------------------------+----------------+
| `PV3_0` | Grating constant         | 1 / m          |
+---------+--------------------------+----------------+
| `PV3_1` | Spectral order           |                |
+---------+--------------------------+----------------+
| `PV3_2` | Incident light angle     | deg            |
+---------+--------------------------+----------------+

Note that the units of `PV3_0` are always 1 / m, regardless of the value of `CUNIT3`.

Free Fit Parameters
^^^^^^^^^^^^^^^^^^^

The `solar-wavelength-calibration <https://docs.dkist.nso.edu/projects/solar-wavelength-calibration/en/latest/>`_ library
allows for a wide range of parameters to be free when computing an optimal wavelength solution. DL-NIRSP only fits the
following parameters:

crval
   The overall wavelength zero-point.

dispersion
   Although the instrument dispersion is known *a priori* via parameter files, we still allow the dispersion to be fit
   within a few percent of the measured value. This accounts for any shifts in instrument performance in the time since
   the dispersion was measured.

opacity_factor
   This parameter accounts for the overall effect of absorption in the atmosphere and affects the strength of Telluric
   lines in the model spectrum. We fit it to match the observing conditions as closely as possible.

continuum_level
   This parameter is simply an overall scaling of the input spectrum and is needed to account for any scale offsets between
   our average solar spectrum and the atlas spectra.
