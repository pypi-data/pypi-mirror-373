# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

# TODO: Change to use enum for these constants
DEFAULT_SAMPLE_FORM = 'powder'
DEFAULT_BEAM_MODE = 'constant wavelength'
DEFAULT_RADIATION_PROBE = 'neutron'
DEFAULT_BACKGROUND_TYPE = 'line-segment'
DEFAULT_SCATTERING_TYPE = 'bragg'
DEFAULT_PEAK_PROFILE_TYPE = {
    'bragg': {
        'constant wavelength': 'pseudo-voigt',
        'time-of-flight': 'pseudo-voigt * ikeda-carpenter',
    },
    'total': {
        'constant wavelength': 'gaussian-damped-sinc',
        'time-of-flight': 'gaussian-damped-sinc',
    },
}
DEFAULT_AXES_LABELS = {
    'bragg': {
        'constant wavelength': ['2θ (degree)', 'Intensity (arb. units)'],
        'time-of-flight': ['TOF (µs)', 'Intensity (arb. units)'],
        'd-spacing': ['d (Å)', 'Intensity (arb. units)'],
    },
    'total': {
        'constant wavelength': ['r (Å)', 'G(r) (Å)'],
        'time-of-flight': ['r (Å)', 'G(r) (Å)'],
    },
}
