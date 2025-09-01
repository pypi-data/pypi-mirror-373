# %% [markdown]
# # Structure Refinement: LBCO, HRPT
#
# This example demonstrates how to use the EasyDiffraction API in a
# simplified, user-friendly manner that closely follows the GUI workflow for a
# Rietveld refinement of La0.5Ba0.5CoO3 crystal structure using constant
# wavelength neutron powder diffraction data from HRPT at PSI.
#
# It is intended for users with minimal programming experience who want to
# learn how to perform standard crystal structure fitting using diffraction
# data. This script covers creating a project, adding sample models and
# experiments, performing analysis, and refining parameters.
#
# Only a single import of `easydiffraction` is required, and all operations are
# performed through high-level components of the `project` object, such as
# `project.sample_models`, `project.experiments`, and `project.analysis`.
# The `project` object is the main container for all information.

# %% [markdown]
# ## Import Library

# %%
import easydiffraction as ed

# %% [markdown]
# ## Step 1: Create a Project
#
# This section explains how to create a project and define its metadata.

# %% [markdown]
# #### Create Project

# %%
project = ed.Project(name='lbco_hrpt')

# %% [markdown]
# #### Set Project Metadata

# %%
project.info.title = 'La0.5Ba0.5CoO3 at HRPT@PSI'
project.info.description = """This project demonstrates a standard
refinement of La0.5Ba0.5CoO3, which crystallizes in a perovskite-type
structure, using neutron powder diffraction data collected in constant
wavelength mode at the HRPT diffractometer (PSI)."""

# %% [markdown]
# #### Show Project Metadata as CIF

# %%
project.info.show_as_cif()

# %% [markdown]
# #### Save Project
#
# When saving the project for the first time, you need to specify the
# directory path. In the example below, the project is saved to a
# temporary location defined by the system.

# %%
project.save_as(dir_path='lbco_hrpt', temporary=True)

# %% [markdown]
# #### Set Up Data Plotter

# %% [markdown]
# Show supported plotting engines.

# %%
project.plotter.show_supported_engines()

# %% [markdown]
# Show current plotting configuration.

# %%
project.plotter.show_config()

# %% [markdown]
# Set plotting engine.

# %%
project.plotter.engine = 'plotly'

# %% [markdown]
# ## Step 2: Define Sample Model
#
# This section shows how to add sample models and modify their parameters.

# %% [markdown]
# #### Add Sample Model

# %%
project.sample_models.add(name='lbco')

# %% [markdown]
# #### Show Defined Sample Models
#
# Show the names of the models added. These names are used to access the
# model using the syntax: `project.sample_models['model_name']`. All model
# parameters can be accessed via the `project` object.

# %%
project.sample_models.show_names()

# %% [markdown]
# #### Set Space Group
#
# Modify the default space group parameters.

# %%
project.sample_models['lbco'].space_group.name_h_m = 'P m -3 m'
project.sample_models['lbco'].space_group.it_coordinate_system_code = '1'

# %% [markdown]
# #### Set Unit Cell
#
# Modify the default unit cell parameters.

# %%
project.sample_models['lbco'].cell.length_a = 3.88

# %% [markdown]
# #### Set Atom Sites
#
# Add atom sites to the sample model.

# %%
project.sample_models['lbco'].atom_sites.add(
    label='La',
    type_symbol='La',
    fract_x=0,
    fract_y=0,
    fract_z=0,
    wyckoff_letter='a',
    b_iso=0.5,
    occupancy=0.5,
)
project.sample_models['lbco'].atom_sites.add(
    label='Ba',
    type_symbol='Ba',
    fract_x=0,
    fract_y=0,
    fract_z=0,
    wyckoff_letter='a',
    b_iso=0.5,
    occupancy=0.5,
)
project.sample_models['lbco'].atom_sites.add(
    label='Co',
    type_symbol='Co',
    fract_x=0.5,
    fract_y=0.5,
    fract_z=0.5,
    wyckoff_letter='b',
    b_iso=0.5,
)
project.sample_models['lbco'].atom_sites.add(
    label='O',
    type_symbol='O',
    fract_x=0,
    fract_y=0.5,
    fract_z=0.5,
    wyckoff_letter='c',
    b_iso=0.5,
)

# %% [markdown]
# #### Apply Symmetry Constraints

# %%
project.sample_models['lbco'].apply_symmetry_constraints()

# %% [markdown]
# #### Show Sample Model as CIF

# %%
project.sample_models['lbco'].show_as_cif()

# %% [markdown]
# #### Show Sample Model Structure

# %%
project.sample_models['lbco'].show_structure()

# %% [markdown]
# #### Save Project State
#
# Save the project state after adding the sample model. This ensures
# that all changes are stored and can be accessed later. The project
# state is saved in the directory specified during project creation.

# %%
project.save()

# %% [markdown]
# ## Step 3: Define Experiment
#
# This section shows how to add experiments, configure their parameters, and
# link the sample models defined in the previous step.

# %% [markdown]
# #### Download Measured Data
#
# Download the data file from the EasyDiffraction repository on GitHub.

# %%
ed.download_from_repository('hrpt_lbco.xye', destination='data')

# %% [markdown]
# #### Add Diffraction Experiment

# %%
project.experiments.add(
    name='hrpt',
    sample_form='powder',
    beam_mode='constant wavelength',
    radiation_probe='neutron',
    data_path='data/hrpt_lbco.xye',
)

# %% [markdown]
# #### Show Defined Experiments

# %%
project.experiments.show_names()

# %% [markdown]
# #### Show Measured Data

# %%
project.plot_meas(expt_name='hrpt')

# %% [markdown]
# #### Set Instrument
#
# Modify the default instrument parameters.

# %%
project.experiments['hrpt'].instrument.setup_wavelength = 1.494
project.experiments['hrpt'].instrument.calib_twotheta_offset = 0.6

# %% [markdown]
# #### Set Peak Profile
#
# Show supported peak profile types.

# %%
project.experiments['hrpt'].show_supported_peak_profile_types()

# %% [markdown]
# Show the current peak profile type.

# %%
project.experiments['hrpt'].show_current_peak_profile_type()

# %% [markdown]
# Select the desired peak profile type.

# %%
project.experiments['hrpt'].peak_profile_type = 'pseudo-voigt'

# %% [markdown]
# Modify default peak profile parameters.

# %%
project.experiments['hrpt'].peak.broad_gauss_u = 0.1
project.experiments['hrpt'].peak.broad_gauss_v = -0.1
project.experiments['hrpt'].peak.broad_gauss_w = 0.1
project.experiments['hrpt'].peak.broad_lorentz_x = 0
project.experiments['hrpt'].peak.broad_lorentz_y = 0.1

# %% [markdown]
# #### Set Background

# %% [markdown]
# Show supported background types.

# %%
project.experiments['hrpt'].show_supported_background_types()

# %% [markdown]
# Show current background type.

# %%
project.experiments['hrpt'].show_current_background_type()

# %% [markdown]
# Select the desired background type.

# %%
project.experiments['hrpt'].background_type = 'line-segment'

# %% [markdown]
# Add background points.

# %%
project.experiments['hrpt'].background.add(x=10, y=170)
project.experiments['hrpt'].background.add(x=30, y=170)
project.experiments['hrpt'].background.add(x=50, y=170)
project.experiments['hrpt'].background.add(x=110, y=170)
project.experiments['hrpt'].background.add(x=165, y=170)

# %% [markdown]
# Show current background points.

# %%
project.experiments['hrpt'].background.show()

# %% [markdown]
# #### Set Linked Phases
#
# Link the sample model defined in the previous step to the experiment.

# %%
project.experiments['hrpt'].linked_phases.add(id='lbco', scale=10.0)

# %% [markdown]
# #### Show Experiment as CIF

# %%
project.experiments['hrpt'].show_as_cif()

# %% [markdown]
# #### Save Project State

# %%
project.save()

# %% [markdown]
# ## Step 4: Perform Analysis
#
# This section explains the analysis process, including how to set up
# calculation and fitting engines.
#
# #### Set Calculator
#
# Show supported calculation engines.

# %%
project.analysis.show_supported_calculators()

# %% [markdown]
# Show current calculation engine.

# %%
project.analysis.show_current_calculator()

# %% [markdown]
# Select the desired calculation engine.

# %%
project.analysis.current_calculator = 'cryspy'

# %% [markdown]
# #### Show Calculated Data

# %%
project.plot_calc(expt_name='hrpt')

# %% [markdown]
# #### Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='hrpt', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='hrpt', x_min=38, x_max=41, show_residual=True)

# %% [markdown]
# #### Show Parameters
#
# Show all parameters of the project.

# %%
project.analysis.show_all_params()

# %% [markdown]
# Show all fittable parameters.

# %%
project.analysis.show_fittable_params()

# %% [markdown]
# Show only free parameters.

# %%
project.analysis.show_free_params()

# %% [markdown]
# Show how to access parameters in the code.

# %%
project.analysis.how_to_access_parameters()

# %% [markdown]
# #### Set Fit Mode
#
# Show supported fit modes.

# %%
project.analysis.show_available_fit_modes()

# %% [markdown]
# Show current fit mode.

# %%
project.analysis.show_current_fit_mode()

# %% [markdown]
# Select desired fit mode.

# %%
project.analysis.fit_mode = 'single'

# %% [markdown]
# #### Set Minimizer
#
# Show supported fitting engines.

# %%
project.analysis.show_available_minimizers()

# %% [markdown]
# Show current fitting engine.

# %%
project.analysis.show_current_minimizer()

# %% [markdown]
# Select desired fitting engine.

# %%
project.analysis.current_minimizer = 'lmfit (leastsq)'

# %% [markdown]
# ### Perform Fit 1/5
#
# Set sample model parameters to be refined.

# %%
project.sample_models['lbco'].cell.length_a.free = True

# %% [markdown]
# Set experiment parameters to be refined.

# %%
project.experiments['hrpt'].linked_phases['lbco'].scale.free = True
project.experiments['hrpt'].instrument.calib_twotheta_offset.free = True
project.experiments['hrpt'].background['10'].y.free = True
project.experiments['hrpt'].background['30'].y.free = True
project.experiments['hrpt'].background['50'].y.free = True
project.experiments['hrpt'].background['110'].y.free = True
project.experiments['hrpt'].background['165'].y.free = True

# %% [markdown]
# Show free parameters after selection.

# %%
project.analysis.show_free_params()

# %% [markdown]
# #### Run Fitting

# %%
project.analysis.fit()

# %% [markdown]
# #### Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='hrpt', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='hrpt', x_min=38, x_max=41, show_residual=True)

# %% [markdown]
# #### Save Project State

# %%
project.save_as(dir_path='lbco_hrpt', temporary=True)

# %% [markdown]
# ### Perform Fit 2/5
#
# Set more parameters to be refined.

# %%
project.experiments['hrpt'].peak.broad_gauss_u.free = True
project.experiments['hrpt'].peak.broad_gauss_v.free = True
project.experiments['hrpt'].peak.broad_gauss_w.free = True
project.experiments['hrpt'].peak.broad_lorentz_y.free = True

# %% [markdown]
# Show free parameters after selection.

# %%
project.analysis.show_free_params()

# %% [markdown]
# #### Run Fitting

# %%
project.analysis.fit()

# %% [markdown]
# #### Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='hrpt', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='hrpt', x_min=38, x_max=41, show_residual=True)

# %% [markdown]
# #### Save Project State

# %%
project.save_as(dir_path='lbco_hrpt', temporary=True)

# %% [markdown]
# ### Perform Fit 3/5
#
# Set more parameters to be refined.

# %%
project.sample_models['lbco'].atom_sites['La'].b_iso.free = True
project.sample_models['lbco'].atom_sites['Ba'].b_iso.free = True
project.sample_models['lbco'].atom_sites['Co'].b_iso.free = True
project.sample_models['lbco'].atom_sites['O'].b_iso.free = True

# %% [markdown]
# Show free parameters after selection.

# %%
project.analysis.show_free_params()

# %% [markdown]
# #### Run Fitting

# %%
project.analysis.fit()

# %% [markdown]
# #### Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='hrpt', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='hrpt', x_min=38, x_max=41, show_residual=True)

# %% [markdown]
# #### Save Project State

# %%
project.save_as(dir_path='lbco_hrpt', temporary=True)

# %% [markdown]
# ### Perform Fit 4/5
#
# #### Set Constraints
#
# Set aliases for parameters.

# %%
project.analysis.aliases.add(label='biso_La', param_uid=project.sample_models['lbco'].atom_sites['La'].b_iso.uid)
project.analysis.aliases.add(label='biso_Ba', param_uid=project.sample_models['lbco'].atom_sites['Ba'].b_iso.uid)

# %% [markdown]
# Set constraints.

# %%
project.analysis.constraints.add(lhs_alias='biso_Ba', rhs_expr='biso_La')

# %% [markdown]
# Show defined constraints.

# %%
project.analysis.show_constraints()

# %% [markdown]
# Show free parameters before applying constraints.

# %%
project.analysis.show_free_params()

# %% [markdown]
# Apply constraints.

# %%
project.analysis.apply_constraints()

# %% [markdown]
# Show free parameters after applying constraints.

# %%
project.analysis.show_free_params()

# %% [markdown]
# #### Run Fitting

# %%
project.analysis.fit()

# %% [markdown]
# #### Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='hrpt', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='hrpt', x_min=38, x_max=41, show_residual=True)

# %% [markdown]
# #### Save Project State

# %%
project.save_as(dir_path='lbco_hrpt', temporary=True)

# %% [markdown]
# ### Perform Fit 5/5
#
# #### Set Constraints
#
# Set more aliases for parameters.

# %%
project.analysis.aliases.add(
    label='occ_La',
    param_uid=project.sample_models['lbco'].atom_sites['La'].occupancy.uid,
)
project.analysis.aliases.add(
    label='occ_Ba',
    param_uid=project.sample_models['lbco'].atom_sites['Ba'].occupancy.uid,
)

# %% [markdown]
# Set more constraints.

# %%
project.analysis.constraints.add(
    lhs_alias='occ_Ba',
    rhs_expr='1 - occ_La',
)

# %% [markdown]
# Show defined constraints.

# %%
project.analysis.show_constraints()

# %% [markdown]
# Apply constraints.

# %%
project.analysis.apply_constraints()

# %% [markdown]
# Set sample model parameters to be refined.

# %%
project.sample_models['lbco'].atom_sites['La'].occupancy.free = True

# %% [markdown]
# Show free parameters after selection.

# %%
project.analysis.show_free_params()

# %% [markdown]
# #### Run Fitting

# %%
project.analysis.fit()

# %% [markdown]
# #### Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='hrpt', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='hrpt', x_min=38, x_max=41, show_residual=True)

# %% [markdown]
# #### Save Project State

# %%
project.save_as(dir_path='lbco_hrpt', temporary=True)

# %% [markdown]
# ## Step 5: Summary
#
# This final section shows how to review the results of the analysis.

# %% [markdown]
# #### Show Project Summary

# %%
project.summary.show_report()
