import os
import tempfile

from numpy.testing import assert_almost_equal

import easydiffraction as ed

TEMP_DIR = tempfile.gettempdir()


def test_single_fit_pdf_xray_pd_cw_nacl() -> None:
    project = ed.Project()

    # Set sample model
    project.sample_models.add(name='nacl')
    sample_model = project.sample_models['nacl']
    sample_model.space_group.name_h_m = 'F m -3 m'
    sample_model.space_group.it_coordinate_system_code = '1'
    sample_model.cell.length_a = 5.6018
    sample_model.atom_sites.add(
        label='Na', type_symbol='Na', fract_x=0, fract_y=0, fract_z=0, wyckoff_letter='a', b_iso=1.1053
    )
    sample_model.atom_sites.add(
        label='Cl', type_symbol='Cl', fract_x=0.5, fract_y=0.5, fract_z=0.5, wyckoff_letter='b', b_iso=0.5708
    )

    # Set experiment
    data_file = 'NaCl.gr'
    ed.download_from_repository(data_file, destination=TEMP_DIR)
    project.experiments.add(
        name='xray_pdf',
        sample_form='powder',
        beam_mode='constant wavelength',
        radiation_probe='xray',
        scattering_type='total',
        data_path=os.path.join(TEMP_DIR, data_file),
    )
    experiment = project.experiments['xray_pdf']
    experiment.peak_profile_type = 'gaussian-damped-sinc'
    experiment.peak.damp_q = 0.0606
    experiment.peak.broad_q = 0
    experiment.peak.cutoff_q = 21
    experiment.peak.sharp_delta_1 = 0
    experiment.peak.sharp_delta_2 = 3.5041
    experiment.peak.damp_particle_diameter = 0
    experiment.linked_phases.add(id='nacl', scale=0.4254)

    # Select fitting parameters
    sample_model.cell.length_a.free = True
    sample_model.atom_sites['Na'].b_iso.free = True
    sample_model.atom_sites['Cl'].b_iso.free = True
    experiment.linked_phases['nacl'].scale.free = True
    experiment.peak.damp_q.free = True
    experiment.peak.sharp_delta_2.free = True

    # Perform fit
    project.analysis.current_calculator = 'pdffit'
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=1.48, decimal=2)


def test_single_fit_pdf_neutron_pd_cw_ni():
    project = ed.Project()

    # Set sample model
    project.sample_models.add(name='ni')
    sample_model = project.sample_models['ni']
    sample_model.space_group.name_h_m.value = 'F m -3 m'
    sample_model.space_group.it_coordinate_system_code = '1'
    sample_model.cell.length_a = 3.526
    sample_model.atom_sites.add(
        label='Ni', type_symbol='Ni', fract_x=0, fract_y=0, fract_z=0, wyckoff_letter='a', b_iso=0.4281
    )

    # Set experiment
    data_file = 'ni-q27r100-neutron_from-2.gr'
    ed.download_from_repository(data_file, destination=TEMP_DIR)
    project.experiments.add(
        name='pdf',
        sample_form='powder',
        beam_mode='constant wavelength',
        radiation_probe='neutron',
        scattering_type='total',
        data_path=os.path.join(TEMP_DIR, data_file),
    )
    experiment = project.experiments['pdf']
    experiment.peak.damp_q = 0
    experiment.peak.broad_q = 0.022
    experiment.peak.cutoff_q = 27.0
    experiment.peak.sharp_delta_1 = 0
    experiment.peak.sharp_delta_2 = 2.5587
    experiment.peak.damp_particle_diameter = 0
    experiment.linked_phases.add(id='ni', scale=0.9892)

    # Select fitting parameters
    sample_model.cell.length_a.free = True
    sample_model.atom_sites['Ni'].b_iso.free = True
    experiment.linked_phases['ni'].scale.free = True
    experiment.peak.broad_q.free = True
    experiment.peak.sharp_delta_2.free = True

    # Perform fit
    project.analysis.current_calculator = 'pdffit'
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=207.1, decimal=1)


def test_single_fit_pdf_neutron_pd_tof_si():
    project = ed.Project()

    # Set sample model
    project.sample_models.add(name='si')
    sample_model = project.sample_models['si']
    sample_model.space_group.name_h_m.value = 'F d -3 m'
    sample_model.space_group.it_coordinate_system_code = '1'
    sample_model.cell.length_a = 5.4306
    sample_model.atom_sites.add(label='Si', type_symbol='Si', fract_x=0, fract_y=0, fract_z=0, wyckoff_letter='a', b_iso=0.717)

    # Set experiment
    data_file = 'NOM_9999_Si_640g_PAC_50_ff_ftfrgr_up-to-50.gr'
    ed.download_from_repository(data_file, destination=TEMP_DIR)
    project.experiments.add(
        name='nomad',
        sample_form='powder',
        beam_mode='time-of-flight',
        radiation_probe='neutron',
        scattering_type='total',
        data_path=os.path.join(TEMP_DIR, data_file),
    )
    experiment = project.experiments['nomad']
    experiment.peak.damp_q = 0.0251
    experiment.peak.broad_q = 0.0183
    experiment.peak.cutoff_q = 35.0
    experiment.peak.sharp_delta_1 = 2.54
    experiment.peak.sharp_delta_2 = -1.7525
    experiment.peak.damp_particle_diameter = 0
    experiment.linked_phases.add(id='si', scale=1.2728)

    # Select fitting parameters
    project.sample_models['si'].cell.length_a.free = True
    project.sample_models['si'].atom_sites['Si'].b_iso.free = True
    experiment.linked_phases['si'].scale.free = True
    experiment.peak.damp_q.free = True
    experiment.peak.broad_q.free = True
    experiment.peak.sharp_delta_1.free = True
    experiment.peak.sharp_delta_2.free = True

    # Perform fit
    project.analysis.current_calculator = 'pdffit'
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=170.54, decimal=1)


if __name__ == '__main__':
    test_single_fit_pdf_xray_pd_cw_nacl()
    test_single_fit_pdf_neutron_pd_cw_ni()
    test_single_fit_pdf_neutron_pd_tof_si()
