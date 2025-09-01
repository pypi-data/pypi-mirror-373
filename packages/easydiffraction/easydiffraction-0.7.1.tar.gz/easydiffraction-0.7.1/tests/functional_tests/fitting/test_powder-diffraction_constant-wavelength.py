import os
import tempfile

from numpy.testing import assert_almost_equal

from easydiffraction import Experiment
from easydiffraction import Project
from easydiffraction import SampleModel
from easydiffraction import download_from_repository

TEMP_DIR = tempfile.gettempdir()


def test_single_fit_neutron_pd_cwl_lbco() -> None:
    # Set sample model
    model = SampleModel('lbco')
    model.space_group.name_h_m = 'P m -3 m'
    model.cell.length_a = 3.88
    model.atom_sites.add('La', 'La', 0, 0, 0, occupancy=0.5, b_iso=0.1)
    model.atom_sites.add('Ba', 'Ba', 0, 0, 0, occupancy=0.5, b_iso=0.1)
    model.atom_sites.add('Co', 'Co', 0.5, 0.5, 0.5, b_iso=0.1)
    model.atom_sites.add('O', 'O', 0, 0.5, 0.5, b_iso=0.1)

    # Set experiment
    data_file = 'hrpt_lbco.xye'
    download_from_repository(data_file, destination=TEMP_DIR)
    expt = Experiment('hrpt', data_path=os.path.join(TEMP_DIR, data_file))
    expt.instrument.setup_wavelength = 1.494
    expt.instrument.calib_twotheta_offset = 0
    expt.peak.broad_gauss_u = 0.1
    expt.peak.broad_gauss_v = -0.1
    expt.peak.broad_gauss_w = 0.2
    expt.peak.broad_lorentz_x = 0
    expt.peak.broad_lorentz_y = 0
    expt.linked_phases.add('lbco', scale=5.0)
    expt.background.add(x=10, y=170)
    expt.background.add(x=165, y=170)

    # Create project
    project = Project()
    project.sample_models.add(model)
    project.experiments.add(expt)

    # Prepare for fitting
    project.analysis.current_calculator = 'cryspy'
    project.analysis.current_minimizer = 'lmfit (leastsq)'

    # ------------ 1st fitting ------------

    # Select fitting parameters
    model.cell.length_a.free = True
    expt.linked_phases['lbco'].scale.free = True
    expt.instrument.calib_twotheta_offset.free = True
    expt.background['10'].y.free = True
    expt.background['165'].y.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=5.79, decimal=1)

    # ------------ 2nd fitting ------------

    # Select fitting parameters
    expt.peak.broad_gauss_u.free = True
    expt.peak.broad_gauss_v.free = True
    expt.peak.broad_gauss_w.free = True
    expt.peak.broad_lorentz_y.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=4.41, decimal=1)

    # ------------ 3rd fitting ------------

    # Select fitting parameters
    model.atom_sites['La'].b_iso.free = True
    model.atom_sites['Ba'].b_iso.free = True
    model.atom_sites['Co'].b_iso.free = True
    model.atom_sites['O'].b_iso.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=1.3, decimal=1)


def test_single_fit_neutron_pd_cwl_lbco_with_constraints() -> None:
    # Set sample model
    model = SampleModel('lbco')

    space_group = model.space_group
    space_group.name_h_m = 'P m -3 m'

    cell = model.cell
    cell.length_a = 3.8909

    atom_sites = model.atom_sites
    atom_sites.add('La', 'La', 0, 0, 0, b_iso=1.0, occupancy=0.5)
    atom_sites.add('Ba', 'Ba', 0, 0, 0, b_iso=1.0, occupancy=0.5)
    atom_sites.add('Co', 'Co', 0.5, 0.5, 0.5, b_iso=1.0)
    atom_sites.add('O', 'O', 0, 0.5, 0.5, b_iso=1.0)

    # Set experiment
    data_file = 'hrpt_lbco.xye'
    download_from_repository(data_file, destination=TEMP_DIR)

    expt = Experiment('hrpt', data_path=os.path.join(TEMP_DIR, data_file))

    instrument = expt.instrument
    instrument.setup_wavelength = 1.494
    instrument.calib_twotheta_offset = 0.6225

    peak = expt.peak
    peak.broad_gauss_u = 0.0834
    peak.broad_gauss_v = -0.1168
    peak.broad_gauss_w = 0.123
    peak.broad_lorentz_x = 0
    peak.broad_lorentz_y = 0.0797

    background = expt.background
    background.add(x=10, y=174.3)
    background.add(x=20, y=159.8)
    background.add(x=30, y=167.9)
    background.add(x=50, y=166.1)
    background.add(x=70, y=172.3)
    background.add(x=90, y=171.1)
    background.add(x=110, y=172.4)
    background.add(x=130, y=182.5)
    background.add(x=150, y=173.0)
    background.add(x=165, y=171.1)

    expt.linked_phases.add('lbco', scale=9.0976)

    # Create project
    project = Project()
    project.sample_models.add(model)
    project.experiments.add(expt)

    # Prepare for fitting
    project.analysis.current_calculator = 'cryspy'
    project.analysis.current_minimizer = 'lmfit (leastsq)'

    # ------------ 1st fitting ------------

    # Select fitting parameters
    atom_sites['La'].occupancy.free = True
    atom_sites['Ba'].occupancy.free = True
    atom_sites['La'].b_iso.free = True
    atom_sites['Ba'].b_iso.free = True
    atom_sites['Co'].b_iso.free = True
    atom_sites['O'].b_iso.free = True

    # Compare parameter values before fit
    assert_almost_equal(atom_sites['La'].b_iso.value, 1.0, decimal=2)
    assert_almost_equal(atom_sites['Ba'].b_iso.value, 1.0, decimal=2)
    assert_almost_equal(atom_sites['Co'].b_iso.value, 1.0, decimal=2)
    assert_almost_equal(atom_sites['O'].b_iso.value, 1.0, decimal=2)
    assert_almost_equal(atom_sites['La'].occupancy.value, 0.5, decimal=2)
    assert_almost_equal(atom_sites['Ba'].occupancy.value, 0.5, decimal=2)

    # Perform fit
    project.analysis.fit()

    # Compare parameter values after fit
    assert_almost_equal(atom_sites['La'].b_iso.value, desired=15.0945, decimal=2)
    assert_almost_equal(atom_sites['Ba'].b_iso.value, desired=0.5226, decimal=2)
    assert_almost_equal(atom_sites['Co'].b_iso.value, desired=0.2398, decimal=2)
    assert_almost_equal(atom_sites['O'].b_iso.value, desired=1.4049, decimal=2)
    assert_almost_equal(atom_sites['La'].occupancy.value, desired=0.011, decimal=2)
    assert_almost_equal(atom_sites['Ba'].occupancy.value, desired=1.3206, decimal=2)

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=1.24, decimal=1)

    # ------------ 2nd fitting ------------

    # Set aliases for parameters
    project.analysis.aliases.add(label='biso_La', param_uid=atom_sites['La'].b_iso.uid)
    project.analysis.aliases.add(label='biso_Ba', param_uid=atom_sites['Ba'].b_iso.uid)
    project.analysis.aliases.add(label='occ_La', param_uid=atom_sites['La'].occupancy.uid)
    project.analysis.aliases.add(label='occ_Ba', param_uid=atom_sites['Ba'].occupancy.uid)

    # Set constraints
    project.analysis.constraints.add(lhs_alias='biso_Ba', rhs_expr='biso_La')
    project.analysis.constraints.add(lhs_alias='occ_Ba', rhs_expr='1 - occ_La')

    # Apply constraints
    project.analysis.apply_constraints()

    # Perform fit
    project.analysis.fit()

    # Compare parameter values after fit
    assert_almost_equal(atom_sites['La'].b_iso.value, desired=0.5443, decimal=2)
    assert_almost_equal(atom_sites['Ba'].b_iso.value, desired=0.5443, decimal=2)
    assert_almost_equal(atom_sites['Co'].b_iso.value, desired=0.2335, decimal=2)
    assert_almost_equal(atom_sites['O'].b_iso.value, desired=1.4056, decimal=2)
    assert_almost_equal(atom_sites['La'].occupancy.value, desired=0.5274, decimal=2)
    assert_almost_equal(atom_sites['Ba'].occupancy.value, desired=0.4726, decimal=2)

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=1.24, decimal=1)


def test_fit_neutron_pd_cwl_hs() -> None:
    # Set sample model
    model = SampleModel('hs')
    model.space_group.name_h_m = 'R -3 m'
    model.space_group.it_coordinate_system_code = 'h'
    model.cell.length_a = 6.8615
    model.cell.length_c = 14.136
    model.atom_sites.add('Zn', 'Zn', 0, 0, 0.5, wyckoff_letter='b', b_iso=0.1)
    model.atom_sites.add('Cu', 'Cu', 0.5, 0, 0, wyckoff_letter='e', b_iso=1.2)
    model.atom_sites.add('O', 'O', 0.206, -0.206, 0.061, wyckoff_letter='h', b_iso=0.7)
    model.atom_sites.add('Cl', 'Cl', 0, 0, 0.197, wyckoff_letter='c', b_iso=1.1)
    model.atom_sites.add('H', '2H', 0.132, -0.132, 0.09, wyckoff_letter='h', b_iso=2.3)
    model.apply_symmetry_constraints()

    # Set experiment
    data_file = 'hrpt_hs.xye'
    download_from_repository(data_file, destination=TEMP_DIR)
    expt = Experiment('hrpt', data_path=os.path.join(TEMP_DIR, data_file))
    expt.instrument.setup_wavelength = 1.89
    expt.instrument.calib_twotheta_offset = 0.0
    expt.peak.broad_gauss_u = 0.1579
    expt.peak.broad_gauss_v = -0.3571
    expt.peak.broad_gauss_w = 0.3498
    expt.peak.broad_lorentz_x = 0.2927
    expt.peak.broad_lorentz_y = 0
    expt.background.add(x=4.4196, y=648.413)
    expt.background.add(x=6.6207, y=523.788)
    expt.background.add(x=10.4918, y=454.938)
    expt.background.add(x=15.4634, y=435.913)
    expt.background.add(x=45.6041, y=472.972)
    expt.background.add(x=74.6844, y=486.606)
    expt.background.add(x=103.4187, y=472.409)
    expt.background.add(x=121.6311, y=496.734)
    expt.background.add(x=159.4116, y=473.146)
    expt.linked_phases.add('hs', scale=0.492)

    # Create project
    project = Project()
    project.sample_models.add(model)
    project.experiments.add(expt)

    # Prepare for fitting
    project.analysis.current_calculator = 'cryspy'
    project.analysis.current_minimizer = 'lmfit (leastsq)'

    # ------------ 1st fitting ------------

    # Select fitting parameters
    model.cell.length_a.free = True
    model.cell.length_c.free = True
    expt.linked_phases['hs'].scale.free = True
    expt.instrument.calib_twotheta_offset.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=2.11, decimal=1)

    # ------------ 2nd fitting ------------

    # Select fitting parameters
    expt.peak.broad_gauss_u.free = True
    expt.peak.broad_gauss_v.free = True
    expt.peak.broad_gauss_w.free = True
    expt.peak.broad_lorentz_x.free = True
    for point in expt.background:
        point.y.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=2.11, decimal=1)

    # ------------ 3rd fitting ------------

    # Select fitting parameters
    model.atom_sites['O'].fract_x.free = True
    model.atom_sites['O'].fract_z.free = True
    model.atom_sites['Cl'].fract_z.free = True
    model.atom_sites['H'].fract_x.free = True
    model.atom_sites['H'].fract_z.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=2.11, decimal=1)

    # ------------ 3rd fitting ------------

    # Select fitting parameters
    model.atom_sites['Zn'].b_iso.free = True
    model.atom_sites['Cu'].b_iso.free = True
    model.atom_sites['O'].b_iso.free = True
    model.atom_sites['Cl'].b_iso.free = True
    model.atom_sites['H'].b_iso.free = True

    # Perform fit
    project.analysis.fit()

    # Compare fit quality
    assert_almost_equal(project.analysis.fit_results.reduced_chi_square, desired=2.11, decimal=1)


if __name__ == '__main__':
    test_fit_neutron_pd_cwl_hs()
    test_single_fit_neutron_pd_cwl_lbco()
    test_single_fit_neutron_pd_cwl_lbco_with_constraints()
