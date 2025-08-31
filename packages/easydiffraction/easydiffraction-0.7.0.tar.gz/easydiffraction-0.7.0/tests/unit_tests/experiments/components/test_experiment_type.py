from easydiffraction.core.objects import Descriptor
from easydiffraction.experiments.components.experiment_type import ExperimentType


def test_experiment_type_initialization():
    experiment_type = ExperimentType(sample_form='powder', beam_mode='CW', radiation_probe='neutron', scattering_type='bragg')

    assert isinstance(experiment_type.sample_form, Descriptor)
    assert experiment_type.sample_form.value == 'powder'
    assert experiment_type.sample_form.name == 'sample_form'
    assert experiment_type.sample_form.cif_name == 'sample_form'

    assert isinstance(experiment_type.beam_mode, Descriptor)
    assert experiment_type.beam_mode.value == 'CW'
    assert experiment_type.beam_mode.name == 'beam_mode'
    assert experiment_type.beam_mode.cif_name == 'beam_mode'

    assert isinstance(experiment_type.radiation_probe, Descriptor)
    assert experiment_type.radiation_probe.value == 'neutron'
    assert experiment_type.radiation_probe.name == 'radiation_probe'
    assert experiment_type.radiation_probe.cif_name == 'radiation_probe'


def test_experiment_type_properties():
    experiment_type = ExperimentType(
        sample_form='single_crystal', beam_mode='TOF', radiation_probe='x-ray', scattering_type='bragg'
    )

    assert experiment_type.category_key == 'expt_type'
    assert experiment_type.cif_category_key == 'expt_type'
    assert experiment_type.datablock_id is None
    assert experiment_type.entry_id is None
    assert experiment_type._locked is True


def no_test_experiment_type_locking_attributes():
    # TODO: hmm this doesn't work as expected.
    experiment_type = ExperimentType(sample_form='powder', beam_mode='CW', radiation_probe='neutron', scattering_type='bragg')
    experiment_type._locked = True  # Disallow adding new attributes
    experiment_type.new_attribute = 'value'
    assert not hasattr(experiment_type, 'new_attribute')
