import os
import tempfile

from numpy.testing import assert_almost_equal

from easydiffraction import Experiment
from easydiffraction import Project
from easydiffraction import SampleModel
from easydiffraction import download_from_repository

TEMP_DIR = tempfile.gettempdir()


def test_joint_fit_split_dataset_neutron_pd_cwl_pbso4() -> None:
    # Set sample model
    model = SampleModel('pbso4')
    model.space_group.name_h_m.value = 'P n m a'
    model.cell.length_a.value = 8.47
    model.cell.length_b.value = 5.39
    model.cell.length_c.value = 6.95
    model.atom_sites.add('Pb', 'Pb', 0.1876, 0.25, 0.167, b_iso=1.37)
    model.atom_sites.add('S', 'S', 0.0654, 0.25, 0.684, b_iso=0.3777)
    model.atom_sites.add('O1', 'O', 0.9082, 0.25, 0.5954, b_iso=1.9764)
    model.atom_sites.add('O2', 'O', 0.1935, 0.25, 0.5432, b_iso=1.4456)
    model.atom_sites.add('O3', 'O', 0.0811, 0.0272, 0.8086, b_iso=1.2822)

    # Set experiments
    data_file = 'd1a_pbso4_first-half.dat'
    download_from_repository(data_file, destination=TEMP_DIR)
    expt1 = Experiment('npd1', data_path=os.path.join(TEMP_DIR, data_file))
    expt1.instrument.setup_wavelength = 1.91
    expt1.instrument.calib_twotheta_offset = -0.1406
    expt1.peak.broad_gauss_u = 0.139
    expt1.peak.broad_gauss_v = -0.4124
    expt1.peak.broad_gauss_w = 0.386
    expt1.peak.broad_lorentz_x = 0
    expt1.peak.broad_lorentz_y = 0.0878
    expt1.linked_phases.add('pbso4', scale=1.46)
    expt1.background_type = 'line-segment'
    for x, y in [
        (11.0, 206.1624),
        (15.0, 194.75),
        (20.0, 194.505),
        (30.0, 188.4375),
        (50.0, 207.7633),
        (70.0, 201.7002),
        (120.0, 244.4525),
        (153.0, 226.0595),
    ]:
        expt1.background.add(x, y)

    data_file = 'd1a_pbso4_second-half.dat'
    download_from_repository(data_file, destination=TEMP_DIR)
    expt2 = Experiment('npd2', data_path=os.path.join(TEMP_DIR, data_file))
    expt2.instrument.setup_wavelength = 1.91
    expt2.instrument.calib_twotheta_offset = -0.1406
    expt2.peak.broad_gauss_u = 0.139
    expt2.peak.broad_gauss_v = -0.4124
    expt2.peak.broad_gauss_w = 0.386
    expt2.peak.broad_lorentz_x = 0
    expt2.peak.broad_lorentz_y = 0.0878
    expt2.linked_phases.add('pbso4', scale=1.46)
    expt2.background_type = 'line-segment'
    for x, y in [
        (11.0, 206.1624),
        (15.0, 194.75),
        (20.0, 194.505),
        (30.0, 188.4375),
        (50.0, 207.7633),
        (70.0, 201.7002),
        (120.0, 244.4525),
        (153.0, 226.0595),
    ]:
        expt2.background.add(x, y)

    # Create project
    project = Project()
    project.sample_models.add(model)
    project.experiments.add(expt1)
    project.experiments.add(expt2)

    # Prepare for fitting
    project.analysis.current_calculator = 'cryspy'
    project.analysis.current_minimizer = 'lmfit (leastsq)'
    project.analysis.fit_mode = 'joint'

    # Select fitting parameters
    model.cell.length_a.free = True
    model.cell.length_b.free = True
    model.cell.length_c.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=4.66, decimal=1)


def test_joint_fit_neutron_xray_pd_cwl_pbso4() -> None:
    # Set sample model
    model = SampleModel('pbso4')
    model.space_group.name_h_m = 'P n m a'
    model.cell.length_a = 8.47
    model.cell.length_b = 5.39
    model.cell.length_c = 6.95
    model.atom_sites.add('Pb', 'Pb', 0.1876, 0.25, 0.167, b_iso=1.37)
    model.atom_sites.add('S', 'S', 0.0654, 0.25, 0.684, b_iso=0.3777)
    model.atom_sites.add('O1', 'O', 0.9082, 0.25, 0.5954, b_iso=1.9764)
    model.atom_sites.add('O2', 'O', 0.1935, 0.25, 0.5432, b_iso=1.4456)
    model.atom_sites.add('O3', 'O', 0.0811, 0.0272, 0.8086, b_iso=1.2822)

    # Set experiments
    data_file = 'd1a_pbso4.dat'
    download_from_repository(data_file, destination=TEMP_DIR)
    expt1 = Experiment('npd', radiation_probe='neutron', data_path=os.path.join(TEMP_DIR, data_file))
    expt1.instrument.setup_wavelength = 1.91
    expt1.instrument.calib_twotheta_offset = -0.1406
    expt1.peak.broad_gauss_u = 0.139
    expt1.peak.broad_gauss_v = -0.412
    expt1.peak.broad_gauss_w = 0.386
    expt1.peak.broad_lorentz_x = 0
    expt1.peak.broad_lorentz_y = 0.088
    expt1.linked_phases.add('pbso4', scale=1.5)
    for x, y in [
        (11.0, 206.1624),
        (15.0, 194.75),
        (20.0, 194.505),
        (30.0, 188.4375),
        (50.0, 207.7633),
        (70.0, 201.7002),
        (120.0, 244.4525),
        (153.0, 226.0595),
    ]:
        expt1.background.add(x, y)

    data_file = 'lab_pbso4.dat'
    download_from_repository(data_file, destination=TEMP_DIR)
    expt2 = Experiment('xrd', radiation_probe='xray', data_path=os.path.join(TEMP_DIR, data_file))
    expt2.instrument.setup_wavelength = 1.540567
    expt2.instrument.calib_twotheta_offset = -0.05181
    expt2.peak.broad_gauss_u = 0.304138
    expt2.peak.broad_gauss_v = -0.112622
    expt2.peak.broad_gauss_w = 0.021272
    expt2.peak.broad_lorentz_x = 0
    expt2.peak.broad_lorentz_y = 0.057691
    expt2.linked_phases.add('pbso4', scale=0.001)
    for x, y in [
        (11.0, 141.8516),
        (13.0, 102.8838),
        (16.0, 78.0551),
        (20.0, 124.0121),
        (30.0, 123.7123),
        (50.0, 120.8266),
        (90.0, 113.7473),
        (110.0, 132.4643),
    ]:
        expt2.background.add(x, y)

    # Create project
    project = Project()
    project.sample_models.add(model)
    project.experiments.add(expt1)
    project.experiments.add(expt2)

    # Prepare for fitting
    project.analysis.current_calculator = 'cryspy'
    project.analysis.current_minimizer = 'lmfit (leastsq)'

    # Select fitting parameters
    model.cell.length_a.free = True
    model.cell.length_b.free = True
    model.cell.length_c.free = True
    expt1.linked_phases['pbso4'].scale.free = True
    expt2.linked_phases['pbso4'].scale.free = True

    # ------------ 1st fitting ------------

    # Perform fit
    project.analysis.fit_mode = 'single'  # Default
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=26.05, decimal=1)

    # ------------ 2nd fitting ------------

    # Perform fit
    project.analysis.fit_mode = 'joint'
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=21.09, decimal=1)

    # ------------ 3rd fitting ------------

    # Perform fit
    project.analysis.joint_fit_experiments['xrd'].weight = 0.5  # Default
    project.analysis.joint_fit_experiments['npd'].weight = 0.5  # Default
    project.analysis.fit_mode = 'joint'
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=21.09, decimal=1)

    # ------------ 4th fitting ------------

    # Perform fit
    project.analysis.joint_fit_experiments['xrd'].weight = 0.3
    project.analysis.joint_fit_experiments['npd'].weight = 0.7
    project.analysis.fit_mode = 'joint'
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=14.39, decimal=1)


if __name__ == '__main__':
    test_joint_fit_split_dataset_neutron_pd_cwl_pbso4()
    test_joint_fit_neutron_xray_pd_cwl_pbso4()
