# %% [markdown]
# # Structure Refinement: Si, SEPD
#
# This example demonstrates a Rietveld refinement of Si crystal structure using
# time-of-flight neutron powder diffraction data from SEPD at Argonne.

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
model = SampleModel('si')

# %% [markdown]
# #### Set Space Group

# %%
model.space_group.name_h_m = 'F d -3 m'
model.space_group.it_coordinate_system_code = '2'

# %% [markdown]
# #### Set Unit Cell

# %%
model.cell.length_a = 5.431

# %% [markdown]
# #### Set Atom Sites

# %%
model.atom_sites.add('Si', 'Si', 0.125, 0.125, 0.125, b_iso=0.5)

# %% [markdown]
# ## Define Experiment
#
# This section shows how to add experiments, configure their parameters, and
# link the sample models defined in the previous step.
#
# #### Download Measured Data

# %%
download_from_repository('sepd_si.xye', destination='data')

# %% [markdown]
# #### Create Experiment

# %%
expt = Experiment('sepd', beam_mode='time-of-flight', data_path='data/sepd_si.xye')

# %% [markdown]
# #### Set Instrument

# %%
expt.instrument.setup_twotheta_bank = 144.845
expt.instrument.calib_d_to_tof_offset = 0.0
expt.instrument.calib_d_to_tof_linear = 7476.91
expt.instrument.calib_d_to_tof_quad = -1.54

# %% [markdown]
# #### Set Peak Profile

# %%
expt.peak_profile_type = 'pseudo-voigt * ikeda-carpenter'
expt.peak.broad_gauss_sigma_0 = 3.0
expt.peak.broad_gauss_sigma_1 = 40.0
expt.peak.broad_gauss_sigma_2 = 2.0
expt.peak.broad_mix_beta_0 = 0.04221
expt.peak.broad_mix_beta_1 = 0.00946

# %% [markdown]
# #### Set Peak Asymmetry

# %%
expt.peak.asym_alpha_0 = 0.0
expt.peak.asym_alpha_1 = 0.5971

# %% [markdown]
# #### Set Background

# %%
expt.background_type = 'line-segment'
for x in range(0, 35000, 5000):
    expt.background.add(x=x, y=200)

# %% [markdown]
# #### Set Linked Phases

# %%
expt.linked_phases.add('si', scale=10.0)

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
project.plot_meas_vs_calc(expt_name='sepd', show_residual=True)
project.plot_meas_vs_calc(expt_name='sepd', x_min=23200, x_max=23700, show_residual=True)

# %% [markdown]
# ### Perform Fit 1/5
#
# Set parameters to be refined.

# %%
model.cell.length_a.free = True

expt.linked_phases['si'].scale.free = True
expt.instrument.calib_d_to_tof_offset.free = True

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
project.plot_meas_vs_calc(expt_name='sepd', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='sepd', x_min=23200, x_max=23700, show_residual=True)

# %% [markdown]
# ### Perform Fit 2/5
#
# Set more parameters to be refined.

# %%
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
project.plot_meas_vs_calc(expt_name='sepd', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='sepd', x_min=23200, x_max=23700, show_residual=True)

# %% [markdown]
# ### Perform Fit 3/5
#
# Fix background points.

# %%
for point in expt.background:
    point.y.free = False

# %% [markdown]
# Set more parameters to be refined.

# %%
expt.peak.broad_gauss_sigma_0.free = True
expt.peak.broad_gauss_sigma_1.free = True
expt.peak.broad_gauss_sigma_2.free = True

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
project.plot_meas_vs_calc(expt_name='sepd', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='sepd', x_min=23200, x_max=23700, show_residual=True)

# %% [markdown]
# ### Perform Fit 4/5
#
# Set more parameters to be refined.

# %%
model.atom_sites['Si'].b_iso.free = True

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
project.plot_meas_vs_calc(expt_name='sepd', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='sepd', x_min=23200, x_max=23700, show_residual=True)
