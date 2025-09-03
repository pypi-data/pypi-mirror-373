Wavelength Calibration
============================

Overview
--------

The `~dkist_processing_cryonirsp.tasks.sp_wavelength_calibration` task provides an absolute wavelength calibration of
Cryo-NIRSP solar spectra by using the routines provided by the
`solar-wavelength-calibration <https://docs.dkist.nso.edu/projects/solar-wavelength-calibration/en/latest/>`_ library.

Workflow
--------

#. **Input Spectrum**: Compute a spatially averaged input spectrum from solar gain images.
#. **Initial Guess**: Use Level 0 headers to generate a first-guess wavelength solution.
#. **Fitting**: Fit the representative spectrum using the `solar-wavelength-calibration <https://docs.dkist.nso.edu/projects/solar-wavelength-calibration/en/latest/>`_  library, refining the wavelength solution.
#. **Header Encoding**: Save the fit results as FITS header keywords, parameterizing the solution for downstream use.

Wavelength Solution Encoding
----------------------------

The wavelength solution is stored in FITS headers using the following keywords (see `Greisen et al (2006) <https://ui.adsabs.harvard.edu/abs/2006A%26A...446..747G/abstract>`_, Section 5 and Table 6):

+---------+--------------------------+----------------+
| Keyword | Description              | Units          |
+=========+==========================+================+
| `CTYPE1`| Spectral coordinate type | "AWAV-GRA"     |
+---------+--------------------------+----------------+
| `CUNIT1`| Wavelength unit          | "nm"           |
+---------+--------------------------+----------------+
| `CRPIX1`| Reference pixel          |                |
+---------+--------------------------+----------------+
| `CRVAL1`| Reference wavelength     | nm             |
+---------+--------------------------+----------------+
| `CDELT1`| Linear dispersion        | nm / px        |
+---------+--------------------------+----------------+
| `PV1_0` | Grating constant         | 1 / m          |
+---------+--------------------------+----------------+
| `PV1_1` | Spectral order           |                |
+---------+--------------------------+----------------+
| `PV1_1` | Incident light angle     | deg            |
+---------+--------------------------+----------------+

Note: The units of `PV1_0` are always 1 / m.

Fitted Parameters
-----------------

The fitting process can optimize several parameters. The parameters that are free in Cryo-NIRSP fits are:

- **crval**: Wavelength zero-point.
- **dispersion**: Linear dispersion, allowed to vary within a few percent of the nominal value.
- **opacity_factor**: Atmospheric absorption scaling, to match telluric line strengths.
- **continuum_level**: Overall spectrum scaling, to match the observed continuum.
- **straylight_fraction**: Fraction of stray or scattered light added to the observed spectrum, affecting line depths and continuum.
- **resolving_power**: Spectral resolving power (:math:`R = \frac{\lambda}{\Delta\lambda}`), characterizing the instrument's ability to distinguish close spectral features.
- **incident_light_angle**: Angle at which light enters the grating, influencing the wavelength solution through the grating equation.


For more details on the fitting algorithms and parameterization, see the
`solar-wavelength-calibration documentation <https://docs.dkist.nso.edu/projects/solar-wavelength-calibration/en/latest/>`_
and `Greisen et al. (2006) <https://ui.adsabs.harvard.edu/abs/2006A%26A...446..747G/abstract>`_.
