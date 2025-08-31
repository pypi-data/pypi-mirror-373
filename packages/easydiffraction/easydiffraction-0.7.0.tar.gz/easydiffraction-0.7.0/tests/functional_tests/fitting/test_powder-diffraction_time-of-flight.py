import os
import tempfile

from numpy.testing import assert_almost_equal

from easydiffraction import Experiment
from easydiffraction import Project
from easydiffraction import SampleModel
from easydiffraction import download_from_repository

TEMP_DIR = tempfile.gettempdir()


def test_single_fit_neutron_pd_tof_si() -> None:
    # Set sample model
    model = SampleModel('si')
    model.space_group.name_h_m = 'F d -3 m'
    model.space_group.it_coordinate_system_code = '2'
    model.cell.length_a = 5.4315
    model.atom_sites.add('Si', 'Si', 0.125, 0.125, 0.125, b_iso=0.529)

    # Set experiment
    data_file = 'sepd_si.xye'
    download_from_repository(data_file, destination=TEMP_DIR)
    expt = Experiment('sepd', beam_mode='time-of-flight', data_path=os.path.join(TEMP_DIR, data_file))
    expt.instrument.setup_twotheta_bank = 144.845
    expt.instrument.calib_d_to_tof_offset = -9.29
    expt.instrument.calib_d_to_tof_linear = 7476.91
    expt.instrument.calib_d_to_tof_quad = -1.54
    expt.peak_profile_type = 'pseudo-voigt * ikeda-carpenter'
    expt.peak.broad_gauss_sigma_0 = 4.2
    expt.peak.broad_gauss_sigma_1 = 45.8
    expt.peak.broad_gauss_sigma_2 = 1.1
    expt.peak.broad_mix_beta_0 = 0.04221
    expt.peak.broad_mix_beta_1 = 0.00946
    expt.peak.asym_alpha_0 = 0.0
    expt.peak.asym_alpha_1 = 0.5971
    expt.linked_phases.add('si', scale=14.92)
    for x in range(0, 35000, 5000):
        expt.background.add(x=x, y=200)
    expt.show_as_cif()

    # Create project
    project = Project()
    project.sample_models.add(model)
    project.experiments.add(expt)

    # Prepare for fitting
    project.analysis.current_calculator = 'cryspy'
    project.analysis.current_minimizer = 'lmfit (leastsq)'

    # Select fitting parameters
    model.cell.length_a.free = True
    model.atom_sites['Si'].b_iso.free = True
    expt.linked_phases['si'].scale.free = True
    expt.instrument.calib_d_to_tof_offset.free = True
    for point in expt.background:
        point.y.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=3.19, decimal=1)


def test_single_fit_neutron_pd_tof_ncaf() -> None:
    # Set sample model
    model = SampleModel('ncaf')
    model.space_group.name_h_m = 'I 21 3'
    model.space_group.it_coordinate_system_code = '1'
    model.cell.length_a = 10.250256
    model.atom_sites.add('Ca', 'Ca', 0.4661, 0.0, 0.25, wyckoff_letter='b', b_iso=0.9)
    model.atom_sites.add('Al', 'Al', 0.25171, 0.25171, 0.25171, wyckoff_letter='a', b_iso=0.66)
    model.atom_sites.add('Na', 'Na', 0.08481, 0.08481, 0.08481, wyckoff_letter='a', b_iso=1.9)
    model.atom_sites.add('F1', 'F', 0.1375, 0.3053, 0.1195, wyckoff_letter='c', b_iso=0.9)
    model.atom_sites.add('F2', 'F', 0.3626, 0.3634, 0.1867, wyckoff_letter='c', b_iso=1.28)
    model.atom_sites.add('F3', 'F', 0.4612, 0.4612, 0.4612, wyckoff_letter='a', b_iso=0.79)

    # Set experiment
    data_file = 'wish_ncaf.xye'
    download_from_repository(data_file, destination=TEMP_DIR)
    expt = Experiment('wish', beam_mode='time-of-flight', data_path=os.path.join(TEMP_DIR, data_file))
    expt.instrument.setup_twotheta_bank = 152.827
    expt.instrument.calib_d_to_tof_offset = -13.7123
    expt.instrument.calib_d_to_tof_linear = 20773.1
    expt.instrument.calib_d_to_tof_quad = -1.08308
    expt.peak_profile_type = 'pseudo-voigt * ikeda-carpenter'
    expt.peak.broad_gauss_sigma_0 = 0.0
    expt.peak.broad_gauss_sigma_1 = 0.0
    expt.peak.broad_gauss_sigma_2 = 15.7
    expt.peak.broad_mix_beta_0 = 0.00670
    expt.peak.broad_mix_beta_1 = 0.0099
    expt.peak.asym_alpha_0 = -0.009
    expt.peak.asym_alpha_1 = 0.1085
    expt.linked_phases.add('ncaf', scale=1.0928)
    for x, y in [
        (9162, 465),
        (11136, 593),
        (13313, 497),
        (14906, 546),
        (16454, 533),
        (17352, 496),
        (18743, 428),
        (20179, 452),
        (21368, 397),
        (22176, 468),
        (22827, 477),
        (24644, 380),
        (26439, 381),
        (28257, 378),
        (31196, 343),
        (34034, 328),
        (37265, 310),
        (41214, 323),
        (44827, 283),
        (49830, 273),
        (52905, 257),
        (58204, 260),
        (62916, 261),
        (70186, 262),
        (74204, 262),
        (82103, 268),
        (91958, 268),
        (102712, 262),
    ]:
        expt.background.add(x, y)

    # Create project
    project = Project()
    project.sample_models.add(model)
    project.experiments.add(expt)

    # Prepare for fitting
    project.analysis.current_calculator = 'cryspy'
    project.analysis.current_minimizer = 'lmfit (leastsq)'

    # Select fitting parameters
    expt.linked_phases['ncaf'].scale.free = True
    expt.instrument.calib_d_to_tof_offset.free = True
    expt.peak.broad_gauss_sigma_2.free = True
    expt.peak.broad_mix_beta_1.free = True
    expt.peak.asym_alpha_1.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=15.25, decimal=1)


if __name__ == '__main__':
    test_single_fit_neutron_pd_tof_si()
    test_single_fit_neutron_pd_tof_ncaf()
