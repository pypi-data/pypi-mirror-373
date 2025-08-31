# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from easydiffraction.core.constants import DEFAULT_BEAM_MODE
from easydiffraction.core.constants import DEFAULT_PEAK_PROFILE_TYPE
from easydiffraction.core.constants import DEFAULT_SCATTERING_TYPE
from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Parameter


# --- Mixins ---
class ConstantWavelengthBroadeningMixin:
    def _add_constant_wavelength_broadening(self) -> None:
        self.broad_gauss_u: Parameter = Parameter(
            value=0.01,
            name='broad_gauss_u',
            cif_name='broad_gauss_u',
            units='deg²',
            description='Gaussian broadening coefficient (dependent on sample size and instrument resolution)',
        )
        self.broad_gauss_v: Parameter = Parameter(
            value=-0.01,
            name='broad_gauss_v',
            cif_name='broad_gauss_v',
            units='deg²',
            description='Gaussian broadening coefficient (instrumental broadening contribution)',
        )
        self.broad_gauss_w: Parameter = Parameter(
            value=0.02,
            name='broad_gauss_w',
            cif_name='broad_gauss_w',
            units='deg²',
            description='Gaussian broadening coefficient (instrumental broadening contribution)',
        )
        self.broad_lorentz_x: Parameter = Parameter(
            value=0.0,
            name='broad_lorentz_x',
            cif_name='broad_lorentz_x',
            units='deg',
            description='Lorentzian broadening coefficient (dependent on sample strain effects)',
        )
        self.broad_lorentz_y: Parameter = Parameter(
            value=0.0,
            name='broad_lorentz_y',
            cif_name='broad_lorentz_y',
            units='deg',
            description='Lorentzian broadening coefficient (dependent on microstructural defects and strain)',
        )


class TimeOfFlightBroadeningMixin:
    def _add_time_of_flight_broadening(self) -> None:
        self.broad_gauss_sigma_0: Parameter = Parameter(
            value=0.0,
            name='gauss_sigma_0',
            cif_name='gauss_sigma_0',
            units='µs²',
            description='Gaussian broadening coefficient (instrumental resolution)',
        )
        self.broad_gauss_sigma_1: Parameter = Parameter(
            value=0.0,
            name='gauss_sigma_1',
            cif_name='gauss_sigma_1',
            units='µs/Å',
            description='Gaussian broadening coefficient (dependent on d-spacing)',
        )
        self.broad_gauss_sigma_2: Parameter = Parameter(
            value=0.0,
            name='gauss_sigma_2',
            cif_name='gauss_sigma_2',
            units='µs²/Å²',
            description='Gaussian broadening coefficient (instrument-dependent term)',
        )
        self.broad_lorentz_gamma_0: Parameter = Parameter(
            value=0.0,
            name='lorentz_gamma_0',
            cif_name='lorentz_gamma_0',
            units='µs',
            description='Lorentzian broadening coefficient (dependent on microstrain effects)',
        )
        self.broad_lorentz_gamma_1: Parameter = Parameter(
            value=0.0,
            name='lorentz_gamma_1',
            cif_name='lorentz_gamma_1',
            units='µs/Å',
            description='Lorentzian broadening coefficient (dependent on d-spacing)',
        )
        self.broad_lorentz_gamma_2: Parameter = Parameter(
            value=0.0,
            name='lorentz_gamma_2',
            cif_name='lorentz_gamma_2',
            units='µs²/Å²',
            description='Lorentzian broadening coefficient (instrumental-dependent term)',
        )
        self.broad_mix_beta_0: Parameter = Parameter(
            value=0.0,
            name='mix_beta_0',
            cif_name='mix_beta_0',
            units='deg',
            description='Mixing parameter. Defines the ratio of Gaussian to Lorentzian contributions in TOF profiles',
        )
        self.broad_mix_beta_1: Parameter = Parameter(
            value=0.0,
            name='mix_beta_1',
            cif_name='mix_beta_1',
            units='deg',
            description='Mixing parameter. Defines the ratio of Gaussian to Lorentzian contributions in TOF profiles',
        )


class EmpiricalAsymmetryMixin:
    def _add_empirical_asymmetry(self) -> None:
        self.asym_empir_1: Parameter = Parameter(
            value=0.1,
            name='asym_empir_1',
            cif_name='asym_empir_1',
            units='',
            description='Empirical asymmetry coefficient p1',
        )
        self.asym_empir_2: Parameter = Parameter(
            value=0.2,
            name='asym_empir_2',
            cif_name='asym_empir_2',
            units='',
            description='Empirical asymmetry coefficient p2',
        )
        self.asym_empir_3: Parameter = Parameter(
            value=0.3,
            name='asym_empir_3',
            cif_name='asym_empir_3',
            units='',
            description='Empirical asymmetry coefficient p3',
        )
        self.asym_empir_4: Parameter = Parameter(
            value=0.4,
            name='asym_empir_4',
            cif_name='asym_empir_4',
            units='',
            description='Empirical asymmetry coefficient p4',
        )


class FcjAsymmetryMixin:
    def _add_fcj_asymmetry(self) -> None:
        self.asym_fcj_1: Parameter = Parameter(
            value=0.01,
            name='asym_fcj_1',
            cif_name='asym_fcj_1',
            units='',
            description='FCJ asymmetry coefficient 1',
        )
        self.asym_fcj_2: Parameter = Parameter(
            value=0.02,
            name='asym_fcj_2',
            cif_name='asym_fcj_2',
            units='',
            description='FCJ asymmetry coefficient 2',
        )


class IkedaCarpenterAsymmetryMixin:
    def _add_ikeda_carpenter_asymmetry(self) -> None:
        self.asym_alpha_0: Parameter = Parameter(
            value=0.01,
            name='asym_alpha_0',
            cif_name='asym_alpha_0',
            units='',
            description='Ikeda-Carpenter asymmetry parameter α₀',
        )
        self.asym_alpha_1: Parameter = Parameter(
            value=0.02,
            name='asym_alpha_1',
            cif_name='asym_alpha_1',
            units='',
            description='Ikeda-Carpenter asymmetry parameter α₁',
        )


class PairDistributionFunctionBroadeningMixin:
    def _add_pair_distribution_function_broadening(self):
        self.damp_q = Parameter(
            value=0.05,
            name='damp_q',
            cif_name='damp_q',
            units='Å⁻¹',
            description='Instrumental Q-resolution damping factor (affects high-r PDF peak amplitude)',
        )
        self.broad_q = Parameter(
            value=0.0,
            name='broad_q',
            cif_name='broad_q',
            units='Å⁻²',
            description='Quadratic PDF peak broadening coefficient (thermal and model uncertainty contribution)',
        )
        self.cutoff_q = Parameter(
            value=25.0,
            name='cutoff_q',
            cif_name='cutoff_q',
            units='Å⁻¹',
            description='Q-value cutoff applied to model PDF for Fourier transform (controls real-space resolution)',
        )
        self.sharp_delta_1 = Parameter(
            value=0.0,
            name='sharp_delta_1',
            cif_name='sharp_delta_1',
            units='Å',
            description='PDF peak sharpening coefficient (1/r dependence)',
        )
        self.sharp_delta_2 = Parameter(
            value=0.0,
            name='sharp_delta_2',
            cif_name='sharp_delta_2',
            units='Å²',
            description='PDF peak sharpening coefficient (1/r² dependence)',
        )
        self.damp_particle_diameter = Parameter(
            value=0.0,
            name='damp_particle_diameter',
            cif_name='damp_particle_diameter',
            units='Å',
            description='Particle diameter for spherical envelope damping correction in PDF',
        )


# --- Base peak class ---
class PeakBase(Component):
    @property
    def category_key(self) -> str:
        return 'peak'

    @property
    def cif_category_key(self) -> str:
        return 'peak'


# --- Derived peak classes ---
class ConstantWavelengthPseudoVoigt(
    PeakBase,
    ConstantWavelengthBroadeningMixin,
):
    _description: str = 'Pseudo-Voigt profile'

    def __init__(self) -> None:
        super().__init__()

        self._add_constant_wavelength_broadening()

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked: bool = True


class ConstantWavelengthSplitPseudoVoigt(
    PeakBase,
    ConstantWavelengthBroadeningMixin,
    EmpiricalAsymmetryMixin,
):
    _description: str = 'Split pseudo-Voigt profile'

    def __init__(self) -> None:
        super().__init__()

        self._add_constant_wavelength_broadening()
        self._add_empirical_asymmetry()

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked: bool = True


class ConstantWavelengthThompsonCoxHastings(
    PeakBase,
    ConstantWavelengthBroadeningMixin,
    FcjAsymmetryMixin,
):
    _description: str = 'Thompson-Cox-Hastings profile'

    def __init__(self) -> None:
        super().__init__()

        self._add_constant_wavelength_broadening()
        self._add_fcj_asymmetry()

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked: bool = True


class TimeOfFlightPseudoVoigt(
    PeakBase,
    TimeOfFlightBroadeningMixin,
):
    _description: str = 'Pseudo-Voigt profile'

    def __init__(self) -> None:
        super().__init__()

        self._add_time_of_flight_broadening()

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked: bool = True


class TimeOfFlightPseudoVoigtIkedaCarpenter(
    PeakBase,
    TimeOfFlightBroadeningMixin,
    IkedaCarpenterAsymmetryMixin,
):
    _description: str = 'Pseudo-Voigt * Ikeda-Carpenter profile'

    def __init__(self) -> None:
        super().__init__()

        self._add_time_of_flight_broadening()
        self._add_ikeda_carpenter_asymmetry()

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked: bool = True


class TimeOfFlightPseudoVoigtBackToBackExponential(
    PeakBase,
    TimeOfFlightBroadeningMixin,
    IkedaCarpenterAsymmetryMixin,
):
    _description: str = 'Pseudo-Voigt * Back-to-Back Exponential profile'

    def __init__(self) -> None:
        super().__init__()

        self._add_time_of_flight_broadening()
        self._add_ikeda_carpenter_asymmetry()

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked: bool = True


class PairDistributionFunctionGaussianDampedSinc(
    PeakBase,
    PairDistributionFunctionBroadeningMixin,
):
    _description = 'Gaussian-damped sinc PDF profile'

    def __init__(self):
        super().__init__()
        self._add_pair_distribution_function_broadening()
        self._locked = True  # Lock further attribute additions


# --- Peak factory ---
class PeakFactory:
    _supported = {
        'bragg': {
            'constant wavelength': {
                'pseudo-voigt': ConstantWavelengthPseudoVoigt,
                'split pseudo-voigt': ConstantWavelengthSplitPseudoVoigt,
                'thompson-cox-hastings': ConstantWavelengthThompsonCoxHastings,
            },
            'time-of-flight': {
                'pseudo-voigt': TimeOfFlightPseudoVoigt,
                'pseudo-voigt * ikeda-carpenter': TimeOfFlightPseudoVoigtIkedaCarpenter,
                'pseudo-voigt * back-to-back': TimeOfFlightPseudoVoigtBackToBackExponential,
            },
        },
        'total': {
            'constant wavelength': {
                'gaussian-damped-sinc': PairDistributionFunctionGaussianDampedSinc,
            },
            'time-of-flight': {
                'gaussian-damped-sinc': PairDistributionFunctionGaussianDampedSinc,
            },
        },
    }

    @classmethod
    def create(
        cls,
        scattering_type=DEFAULT_SCATTERING_TYPE,
        beam_mode=DEFAULT_BEAM_MODE,
        profile_type=DEFAULT_PEAK_PROFILE_TYPE[DEFAULT_SCATTERING_TYPE][DEFAULT_BEAM_MODE],
    ):
        supported_scattering_types = list(cls._supported.keys())
        if scattering_type not in supported_scattering_types:
            raise ValueError(
                f"Unsupported scattering type: '{scattering_type}'.\n Supported scattering types: {supported_scattering_types}"
            )

        supported_beam_modes = list(cls._supported[scattering_type].keys())
        if beam_mode not in supported_beam_modes:
            raise ValueError(
                f"Unsupported beam mode: '{beam_mode}' for scattering type: '{scattering_type}'.\n "
                f'Supported beam modes: {supported_beam_modes}'
            )

        supported_profile_types = list(cls._supported[scattering_type][beam_mode].keys())
        if profile_type not in supported_profile_types:
            raise ValueError(
                f"Unsupported profile type '{profile_type}' for beam mode '{beam_mode}'.\n"
                f'Supported profile types: {supported_profile_types}'
            )

        peak_class = cls._supported[scattering_type][beam_mode][profile_type]
        peak_obj = peak_class()

        return peak_obj
