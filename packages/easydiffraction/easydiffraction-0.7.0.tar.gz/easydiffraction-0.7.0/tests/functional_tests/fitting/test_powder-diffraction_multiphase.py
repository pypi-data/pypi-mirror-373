import os
import tempfile

from numpy.testing import assert_almost_equal

from easydiffraction import Experiment
from easydiffraction import Project
from easydiffraction import SampleModel
from easydiffraction import download_from_repository

TEMP_DIR = tempfile.gettempdir()


def test_single_fit_neutron_pd_tof_mcstas_lbco_si() -> None:
    # Set sample models
    model_1 = SampleModel('lbco')
    model_1.space_group.name_h_m = 'P m -3 m'
    model_1.space_group.it_coordinate_system_code = '1'
    model_1.cell.length_a = 3.8909
    model_1.atom_sites.add('La', 'La', 0, 0, 0, wyckoff_letter='a', b_iso=0.2, occupancy=0.5)
    model_1.atom_sites.add('Ba', 'Ba', 0, 0, 0, wyckoff_letter='a', b_iso=0.2, occupancy=0.5)
    model_1.atom_sites.add('Co', 'Co', 0.5, 0.5, 0.5, wyckoff_letter='b', b_iso=0.2567)
    model_1.atom_sites.add('O', 'O', 0, 0.5, 0.5, wyckoff_letter='c', b_iso=1.4041)

    model_2 = SampleModel('si')
    model_2.space_group.name_h_m = 'F d -3 m'
    model_2.space_group.it_coordinate_system_code = '2'
    model_2.cell.length_a = 5.43146
    model_2.atom_sites.add('Si', 'Si', 0.0, 0.0, 0.0, wyckoff_letter='a', b_iso=0.0)

    # Set experiment
    data_file = 'mcstas_lbco-si.xys'
    download_from_repository(data_file, destination=TEMP_DIR)
    expt = Experiment('mcstas', beam_mode='time-of-flight', data_path=os.path.join(TEMP_DIR, data_file))
    expt.instrument.setup_twotheta_bank = 94.90931761529106
    expt.instrument.calib_d_to_tof_offset = 0.0
    expt.instrument.calib_d_to_tof_linear = 58724.76869981215
    expt.instrument.calib_d_to_tof_quad = -0.00001
    expt.peak_profile_type = 'pseudo-voigt * ikeda-carpenter'
    expt.peak.broad_gauss_sigma_0 = 45137
    expt.peak.broad_gauss_sigma_1 = -52394
    expt.peak.broad_gauss_sigma_2 = 22998
    expt.peak.broad_mix_beta_0 = 0.0055
    expt.peak.broad_mix_beta_1 = 0.0041
    expt.peak.asym_alpha_0 = 0.0
    expt.peak.asym_alpha_1 = 0.0097
    expt.linked_phases.add('lbco', scale=4.0)
    expt.linked_phases.add('si', scale=0.2)
    for x in range(45000, 115000, 5000):
        expt.background.add(x=x, y=0.2)

    # Create project
    project = Project()
    project.sample_models.add(model_1)
    project.sample_models.add(model_2)
    project.experiments.add(expt)

    # Exclude regions from fitting
    project.experiments['mcstas'].excluded_regions.add(start=108000, end=200000)

    # Prepare for fitting
    project.analysis.current_calculator = 'cryspy'
    project.analysis.current_minimizer = 'lmfit (leastsq)'

    # Select fitting parameters
    model_1.cell.length_a.free = True
    model_1.atom_sites['La'].b_iso.free = True
    model_1.atom_sites['Ba'].b_iso.free = True
    model_1.atom_sites['Co'].b_iso.free = True
    model_1.atom_sites['O'].b_iso.free = True
    model_2.cell.length_a.free = True
    model_2.atom_sites['Si'].b_iso.free = True
    expt.linked_phases['lbco'].scale.free = True
    expt.linked_phases['si'].scale.free = True
    expt.peak.broad_gauss_sigma_0.free = True
    expt.peak.broad_gauss_sigma_1.free = True
    expt.peak.broad_gauss_sigma_2.free = True
    expt.peak.asym_alpha_1.free = True
    expt.peak.broad_mix_beta_0.free = True
    expt.peak.broad_mix_beta_1.free = True
    for point in expt.background:
        point.y.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=2.87, decimal=1)


if __name__ == '__main__':
    test_single_fit_neutron_pd_tof_mcstas_lbco_si()
