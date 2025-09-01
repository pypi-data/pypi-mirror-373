import pytest

from easydiffraction.core.objects import Parameter
from easydiffraction.experiments.components.peak import ConstantWavelengthBroadeningMixin
from easydiffraction.experiments.components.peak import ConstantWavelengthPseudoVoigt
from easydiffraction.experiments.components.peak import ConstantWavelengthSplitPseudoVoigt
from easydiffraction.experiments.components.peak import ConstantWavelengthThompsonCoxHastings
from easydiffraction.experiments.components.peak import EmpiricalAsymmetryMixin
from easydiffraction.experiments.components.peak import FcjAsymmetryMixin
from easydiffraction.experiments.components.peak import IkedaCarpenterAsymmetryMixin
from easydiffraction.experiments.components.peak import PeakBase
from easydiffraction.experiments.components.peak import PeakFactory
from easydiffraction.experiments.components.peak import TimeOfFlightBroadeningMixin
from easydiffraction.experiments.components.peak import TimeOfFlightPseudoVoigt
from easydiffraction.experiments.components.peak import TimeOfFlightPseudoVoigtBackToBackExponential
from easydiffraction.experiments.components.peak import TimeOfFlightPseudoVoigtIkedaCarpenter


# --- Tests for Mixins ---
def test_constant_wavelength_broadening_mixin():
    class TestClass(ConstantWavelengthBroadeningMixin):
        def __init__(self):
            self._add_constant_wavelength_broadening()

    obj = TestClass()
    assert isinstance(obj.broad_gauss_u, Parameter)
    assert obj.broad_gauss_u.value == 0.01
    assert obj.broad_gauss_v.value == -0.01
    assert obj.broad_gauss_w.value == 0.02
    assert obj.broad_lorentz_x.value == 0.0
    assert obj.broad_lorentz_y.value == 0.0


def test_time_of_flight_broadening_mixin():
    class TestClass(TimeOfFlightBroadeningMixin):
        def __init__(self):
            self._add_time_of_flight_broadening()

    obj = TestClass()
    assert isinstance(obj.broad_gauss_sigma_0, Parameter)
    assert obj.broad_gauss_sigma_0.value == 0.0
    assert obj.broad_gauss_sigma_1.value == 0.0
    assert obj.broad_gauss_sigma_2.value == 0.0
    assert obj.broad_lorentz_gamma_0.value == 0.0
    assert obj.broad_lorentz_gamma_1.value == 0.0
    assert obj.broad_lorentz_gamma_2.value == 0.0
    assert obj.broad_mix_beta_0.value == 0.0
    assert obj.broad_mix_beta_1.value == 0.0


def test_empirical_asymmetry_mixin():
    class TestClass(EmpiricalAsymmetryMixin):
        def __init__(self):
            self._add_empirical_asymmetry()

    obj = TestClass()
    assert isinstance(obj.asym_empir_1, Parameter)
    assert obj.asym_empir_1.value == 0.1
    assert obj.asym_empir_2.value == 0.2
    assert obj.asym_empir_3.value == 0.3
    assert obj.asym_empir_4.value == 0.4


def test_fcj_asymmetry_mixin():
    class TestClass(FcjAsymmetryMixin):
        def __init__(self):
            self._add_fcj_asymmetry()

    obj = TestClass()
    assert isinstance(obj.asym_fcj_1, Parameter)
    assert obj.asym_fcj_1.value == 0.01
    assert obj.asym_fcj_2.value == 0.02


def test_ikeda_carpenter_asymmetry_mixin():
    class TestClass(IkedaCarpenterAsymmetryMixin):
        def __init__(self):
            self._add_ikeda_carpenter_asymmetry()

    obj = TestClass()
    assert isinstance(obj.asym_alpha_0, Parameter)
    assert obj.asym_alpha_0.value == 0.01
    assert obj.asym_alpha_1.value == 0.02


# --- Tests for Base and Derived Peak Classes ---
def test_peak_base_properties():
    peak = PeakBase()
    assert peak.cif_category_key == 'peak'
    assert peak.category_key == 'peak'
    assert peak._entry_id is None


def test_constant_wavelength_pseudo_voigt_initialization():
    peak = ConstantWavelengthPseudoVoigt()
    assert isinstance(peak.broad_gauss_u, Parameter)
    assert peak.broad_gauss_u.value == 0.01


def test_constant_wavelength_split_pseudo_voigt_initialization():
    peak = ConstantWavelengthSplitPseudoVoigt()
    assert isinstance(peak.broad_gauss_u, Parameter)
    assert isinstance(peak.asym_empir_1, Parameter)
    assert peak.asym_empir_1.value == 0.1


def test_constant_wavelength_thompson_cox_hastings_initialization():
    peak = ConstantWavelengthThompsonCoxHastings()
    assert isinstance(peak.broad_gauss_u, Parameter)
    assert isinstance(peak.asym_fcj_1, Parameter)
    assert peak.asym_fcj_1.value == 0.01


def test_time_of_flight_pseudo_voigt_initialization():
    peak = TimeOfFlightPseudoVoigt()
    assert isinstance(peak.broad_gauss_sigma_0, Parameter)
    assert peak.broad_gauss_sigma_0.value == 0.0


def test_time_of_flight_pseudo_voigt_ikeda_carpenter_initialization():
    peak = TimeOfFlightPseudoVoigtIkedaCarpenter()
    assert isinstance(peak.broad_gauss_sigma_0, Parameter)
    assert isinstance(peak.asym_alpha_0, Parameter)


def test_time_of_flight_pseudo_voigt_back_to_back_exponential_initialization():
    peak = TimeOfFlightPseudoVoigtBackToBackExponential()
    assert isinstance(peak.broad_gauss_sigma_0, Parameter)
    assert isinstance(peak.asym_alpha_0, Parameter)


# --- Tests for PeakFactory ---
def test_peak_factory_create_constant_wavelength_pseudo_voigt():
    peak = PeakFactory.create(beam_mode='constant wavelength', profile_type='pseudo-voigt')
    assert isinstance(peak, ConstantWavelengthPseudoVoigt)


def test_peak_factory_create_invalid_beam_mode():
    with pytest.raises(ValueError, match="Unsupported beam mode: 'invalid'.*"):
        PeakFactory.create(beam_mode='invalid', profile_type='pseudo-voigt')


def test_peak_factory_create_invalid_profile_type():
    with pytest.raises(ValueError, match="Unsupported profile type 'invalid' for beam mode 'constant wavelength'.*"):
        PeakFactory.create(beam_mode='constant wavelength', profile_type='invalid')
