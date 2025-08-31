import pytest

from easydiffraction.core.objects import Parameter
from easydiffraction.experiments.components.instrument import ConstantWavelengthInstrument
from easydiffraction.experiments.components.instrument import InstrumentBase
from easydiffraction.experiments.components.instrument import InstrumentFactory
from easydiffraction.experiments.components.instrument import TimeOfFlightInstrument


def test_instrument_base_properties():
    instrument = InstrumentBase()
    assert instrument.category_key == 'instrument'
    assert instrument.cif_category_key == 'instr'
    assert instrument._entry_id is None


def test_constant_wavelength_instrument_initialization():
    instrument = ConstantWavelengthInstrument(setup_wavelength=1.5406, calib_twotheta_offset=0.1)

    assert isinstance(instrument.setup_wavelength, Parameter)
    assert instrument.setup_wavelength.value == 1.5406
    assert instrument.setup_wavelength.name == 'wavelength'
    assert instrument.setup_wavelength.cif_name == 'wavelength'
    assert instrument.setup_wavelength.units == 'Å'

    assert isinstance(instrument.calib_twotheta_offset, Parameter)
    assert instrument.calib_twotheta_offset.value == 0.1
    assert instrument.calib_twotheta_offset.name == 'twotheta_offset'
    assert instrument.calib_twotheta_offset.cif_name == '2theta_offset'
    assert instrument.calib_twotheta_offset.units == 'deg'


def test_time_of_flight_instrument_initialization():
    instrument = TimeOfFlightInstrument(
        setup_twotheta_bank=150.0,
        calib_d_to_tof_offset=0.5,
        calib_d_to_tof_linear=10000.0,
        calib_d_to_tof_quad=-1.0,
        calib_d_to_tof_recip=0.1,
    )

    assert isinstance(instrument.setup_twotheta_bank, Parameter)
    assert instrument.setup_twotheta_bank.value == 150.0
    assert instrument.setup_twotheta_bank.name == 'twotheta_bank'
    assert instrument.setup_twotheta_bank.cif_name == '2theta_bank'
    assert instrument.setup_twotheta_bank.units == 'deg'

    assert isinstance(instrument.calib_d_to_tof_offset, Parameter)
    assert instrument.calib_d_to_tof_offset.value == 0.5
    assert instrument.calib_d_to_tof_offset.name == 'd_to_tof_offset'
    assert instrument.calib_d_to_tof_offset.cif_name == 'd_to_tof_offset'
    assert instrument.calib_d_to_tof_offset.units == 'µs'

    assert isinstance(instrument.calib_d_to_tof_linear, Parameter)
    assert instrument.calib_d_to_tof_linear.value == 10000.0
    assert instrument.calib_d_to_tof_linear.name == 'd_to_tof_linear'
    assert instrument.calib_d_to_tof_linear.cif_name == 'd_to_tof_linear'
    assert instrument.calib_d_to_tof_linear.units == 'µs/Å'

    assert isinstance(instrument.calib_d_to_tof_quad, Parameter)
    assert instrument.calib_d_to_tof_quad.value == -1.0
    assert instrument.calib_d_to_tof_quad.name == 'd_to_tof_quad'
    assert instrument.calib_d_to_tof_quad.cif_name == 'd_to_tof_quad'
    assert instrument.calib_d_to_tof_quad.units == 'µs/Å²'

    assert isinstance(instrument.calib_d_to_tof_recip, Parameter)
    assert instrument.calib_d_to_tof_recip.value == 0.1
    assert instrument.calib_d_to_tof_recip.name == 'd_to_tof_recip'
    assert instrument.calib_d_to_tof_recip.cif_name == 'd_to_tof_recip'
    assert instrument.calib_d_to_tof_recip.units == 'µs·Å'


def test_instrument_factory_create_constant_wavelength():
    instrument = InstrumentFactory.create(beam_mode='constant wavelength')
    assert isinstance(instrument, ConstantWavelengthInstrument)


def test_instrument_factory_create_time_of_flight():
    instrument = InstrumentFactory.create(beam_mode='time-of-flight')
    assert isinstance(instrument, TimeOfFlightInstrument)


def test_instrument_factory_create_invalid_beam_mode():
    with pytest.raises(ValueError, match="Unsupported beam mode: 'invalid'.*"):
        InstrumentFactory.create(beam_mode='invalid')
