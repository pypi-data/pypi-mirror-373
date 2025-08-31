# %% [markdown]
# # Structure Refinement: HS, HRPT
#
# This example demonstrates a Rietveld refinement of HS crystal structure
# using constant wavelength neutron powder diffraction data from HRPT at PSI.

# %% [markdown]
# ## Import Library

# %%
from easydiffraction import Experiment
from easydiffraction import Project
from easydiffraction import SampleModel
from easydiffraction import download_from_repository

# %% [markdown]
# ## Define Sample Model
#
# This section shows how to add sample models and modify their parameters.
#
# #### Create Sample Model

# %%
model = SampleModel('hs')

# %% [markdown]
# #### Set Space Group

# %%
model.space_group.name_h_m = 'R -3 m'
model.space_group.it_coordinate_system_code = 'h'

# %% [markdown]
# #### Set Unit Cell

# %%
model.cell.length_a = 6.9
model.cell.length_c = 14.1

# %% [markdown]
# #### Set Atom Sites

# %%
model.atom_sites.add('Zn', 'Zn', 0, 0, 0.5, wyckoff_letter='b', b_iso=0.5)
model.atom_sites.add('Cu', 'Cu', 0.5, 0, 0, wyckoff_letter='e', b_iso=0.5)
model.atom_sites.add('O', 'O', 0.21, -0.21, 0.06, wyckoff_letter='h', b_iso=0.5)
model.atom_sites.add('Cl', 'Cl', 0, 0, 0.197, wyckoff_letter='c', b_iso=0.5)
model.atom_sites.add('H', '2H', 0.13, -0.13, 0.08, wyckoff_letter='h', b_iso=0.5)

# %% [markdown]
# #### Symmetry constraints
#
# Show CIF output before applying symmetry constraints.

# %%
model.show_as_cif()

# %% [markdown]
# Apply symmetry constraints.

# %%
model.apply_symmetry_constraints()

# %% [markdown]
# Show CIF output after applying symmetry constraints.

# %%
model.show_as_cif()

# %% [markdown]
# ## Define Experiment
#
# This section shows how to add experiments, configure their parameters, and
# link the sample models defined in the previous step.
#
# #### Download Measured Data

# %%
download_from_repository('hrpt_hs.xye', destination='data')

# %% [markdown]
# #### Create Experiment

# %%
expt = Experiment(name='hrpt', data_path='data/hrpt_hs.xye')

# %% [markdown]
# #### Set Instrument

# %%
expt.instrument.setup_wavelength = 1.89
expt.instrument.calib_twotheta_offset = 0.0

# %% [markdown]
# #### Set Peak Profile

# %%
expt.peak.broad_gauss_u = 0.1
expt.peak.broad_gauss_v = -0.2
expt.peak.broad_gauss_w = 0.2
expt.peak.broad_lorentz_x = 0.0
expt.peak.broad_lorentz_y = 0

# %% [markdown]
# #### Set Background

# %%
expt.background.add(x=4.4196, y=500)
expt.background.add(x=6.6207, y=500)
expt.background.add(x=10.4918, y=500)
expt.background.add(x=15.4634, y=500)
expt.background.add(x=45.6041, y=500)
expt.background.add(x=74.6844, y=500)
expt.background.add(x=103.4187, y=500)
expt.background.add(x=121.6311, y=500)
expt.background.add(x=159.4116, y=500)

# %% [markdown]
# #### Set Linked Phases

# %%
expt.linked_phases.add('hs', scale=0.5)

# %% [markdown]
# ## Define Project
#
# The project object is used to manage the sample model, experiment, and
# analysis.
#
# #### Create Project

# %%
project = Project()

# %% [markdown]
# #### Set Plotting Engine

# %%
project.plotter.engine = 'plotly'

# %% [markdown]
# #### Add Sample Model

# %%
project.sample_models.add(model)

# %% [markdown]
# #### Add Experiment

# %%
project.experiments.add(expt)

# %% [markdown]
# ## Perform Analysis
#
# This section shows the analysis process, including how to set up
# calculation and fitting engines.
#
# #### Set Calculator

# %%
project.analysis.current_calculator = 'cryspy'

# %% [markdown]
# #### Set Minimizer

# %%
project.analysis.current_minimizer = 'lmfit (leastsq)'

# %% [markdown]
# #### Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='hrpt', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='hrpt', x_min=48, x_max=51, show_residual=True)

# %% [markdown]
# ### Perform Fit 1/5
#
# Set parameters to be refined.

# %%
model.cell.length_a.free = True
model.cell.length_c.free = True

expt.linked_phases['hs'].scale.free = True
expt.instrument.calib_twotheta_offset.free = True

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
project.plot_meas_vs_calc(expt_name='hrpt', x_min=48, x_max=51, show_residual=True)

# %% [markdown]
# ### Perform Fit 2/5
#
# Set more parameters to be refined.

# %%
expt.peak.broad_gauss_u.free = True
expt.peak.broad_gauss_v.free = True
expt.peak.broad_gauss_w.free = True
expt.peak.broad_lorentz_x.free = True

for point in expt.background:
    point.y.free = True

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
project.plot_meas_vs_calc(expt_name='hrpt', x_min=48, x_max=51, show_residual=True)

# %% [markdown]
# ### Perform Fit 3/5
#
# Set more parameters to be refined.

# %%
model.atom_sites['O'].fract_x.free = True
model.atom_sites['O'].fract_z.free = True
model.atom_sites['Cl'].fract_z.free = True
model.atom_sites['H'].fract_x.free = True
model.atom_sites['H'].fract_z.free = True

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
project.plot_meas_vs_calc(expt_name='hrpt', x_min=48, x_max=51, show_residual=True)

# %% [markdown]
# ### Perform Fit 4/5
#
# Set more parameters to be refined.

# %%
model.atom_sites['Zn'].b_iso.free = True
model.atom_sites['Cu'].b_iso.free = True
model.atom_sites['O'].b_iso.free = True
model.atom_sites['Cl'].b_iso.free = True
model.atom_sites['H'].b_iso.free = True

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
project.plot_meas_vs_calc(expt_name='hrpt', x_min=48, x_max=51, show_residual=True)

# %% [markdown]
# ## Summary
#
# This final section shows how to review the results of the analysis.

# %% [markdown]
# #### Show Project Summary

# %%
project.summary.show_report()
