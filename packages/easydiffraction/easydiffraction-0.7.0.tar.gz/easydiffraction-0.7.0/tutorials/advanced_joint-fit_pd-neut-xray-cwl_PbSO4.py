# %% [markdown]
# # Structure Refinement: PbSO4, NPD + XRD
#
# This example demonstrates a more advanced use of the EasyDiffraction library
# by explicitly creating and configuring sample models and experiments
# before adding them to a project. It could be more suitable for users who are
# interested in creating custom workflows. This tutorial provides minimal
# explanation and is intended for users already familiar with EasyDiffraction.
#
# The tutorial covers a Rietveld refinement of PbSO4 crystal structure based
# on the joint fit of both X-ray and neutron diffraction data.

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
model = SampleModel('pbso4')

# %% [markdown]
# #### Set Space Group

# %%
model.space_group.name_h_m = 'P n m a'

# %% [markdown]
# #### Set Unit Cell

# %%
model.cell.length_a = 8.47
model.cell.length_b = 5.39
model.cell.length_c = 6.95

# %% [markdown]
# #### Set Atom Sites

# %%
model.atom_sites.add('Pb', 'Pb', 0.1876, 0.25, 0.167, b_iso=1.37)
model.atom_sites.add('S', 'S', 0.0654, 0.25, 0.684, b_iso=0.3777)
model.atom_sites.add('O1', 'O', 0.9082, 0.25, 0.5954, b_iso=1.9764)
model.atom_sites.add('O2', 'O', 0.1935, 0.25, 0.5432, b_iso=1.4456)
model.atom_sites.add('O3', 'O', 0.0811, 0.0272, 0.8086, b_iso=1.2822)


# %% [markdown]
# ## Define Experiments
#
# This section shows how to add experiments, configure their parameters, and
# link the sample models defined in the previous step.
#
# ### Experiment 1: npd
#
# #### Download Data

# %%
download_from_repository('d1a_pbso4.dat', destination='data')

# %% [markdown]
# #### Create Experiment

# %%
expt1 = Experiment('npd', radiation_probe='neutron', data_path='data/d1a_pbso4.dat')

# %% [markdown]
# #### Set Instrument

# %%
expt1.instrument.setup_wavelength = 1.91
expt1.instrument.calib_twotheta_offset = -0.1406

# %% [markdown]
# #### Set Peak Profile

# %%
expt1.peak.broad_gauss_u = 0.139
expt1.peak.broad_gauss_v = -0.412
expt1.peak.broad_gauss_w = 0.386
expt1.peak.broad_lorentz_x = 0
expt1.peak.broad_lorentz_y = 0.088

# %% [markdown]
# #### Set Background

# %% [markdown]
# Select the background type.

# %%
expt1.background_type = 'line-segment'

# %% [markdown]
# Add background points.

# %%
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

# %% [markdown]
# #### Set Linked Phases

# %%
expt1.linked_phases.add('pbso4', scale=1.5)

# %% [markdown]
# ### Experiment 2: xrd
#
# #### Download Data

# %%
download_from_repository('lab_pbso4.dat', destination='data')

# %% [markdown]
# #### Create Experiment

# %%
expt2 = Experiment('xrd', radiation_probe='xray', data_path='data/lab_pbso4.dat')

# %% [markdown]
# #### Set Instrument

# %%
expt2.instrument.setup_wavelength = 1.540567
expt2.instrument.calib_twotheta_offset = -0.05181

# %% [markdown]
# #### Set Peak Profile

# %%
expt2.peak.broad_gauss_u = 0.304138
expt2.peak.broad_gauss_v = -0.112622
expt2.peak.broad_gauss_w = 0.021272
expt2.peak.broad_lorentz_x = 0
expt2.peak.broad_lorentz_y = 0.057691

# %% [markdown]
# #### Set Background

# %% [markdown]
# Select background type.

# %%
expt2.background_type = 'chebyshev polynomial'

# %% [markdown]
# Add background points.

# %%
for x, y in [
    (0, 119.195),
    (1, 6.221),
    (2, -45.725),
    (3, 8.119),
    (4, 54.552),
    (5, -20.661),
]:
    expt2.background.add(x, y)

# %% [markdown]
# #### Set Linked Phases

# %%
expt2.linked_phases.add('pbso4', scale=0.001)

# %% [markdown]
# ## Define Project
#
# The project object is used to manage sample models, experiments, and analysis.
#
# #### Create Project

# %%
project = Project()

# %% [markdown]
# #### Add Sample Model

# %%
project.sample_models.add(model)

# %% [markdown]
# #### Add Experiments

# %%
project.experiments.add(expt1)
project.experiments.add(expt2)

# %% [markdown]
# ## Perform Analysis
#
# This section outlines the analysis process, including how to configure calculation and fitting engines.
#
# #### Set Calculator

# %%
project.analysis.current_calculator = 'cryspy'

# %% [markdown]
# #### Set Fit Mode

# %%
project.analysis.fit_mode = 'joint'

# %% [markdown]
# #### Set Minimizer

# %%
project.analysis.current_minimizer = 'lmfit (leastsq)'

# %% [markdown]
# #### Set Fitting Parameters
#
# Set sample model parameters to be optimized.

# %%
model.cell.length_a.free = True
model.cell.length_b.free = True
model.cell.length_c.free = True

# %% [markdown]
# Set experiment parameters to be optimized.

# %%
expt1.linked_phases['pbso4'].scale.free = True

expt1.instrument.calib_twotheta_offset.free = True

expt1.peak.broad_gauss_u.free = True
expt1.peak.broad_gauss_v.free = True
expt1.peak.broad_gauss_w.free = True
expt1.peak.broad_lorentz_y.free = True

# %%
expt2.linked_phases['pbso4'].scale.free = True

expt2.instrument.calib_twotheta_offset.free = True

expt2.peak.broad_gauss_u.free = True
expt2.peak.broad_gauss_v.free = True
expt2.peak.broad_gauss_w.free = True
expt2.peak.broad_lorentz_y.free = True

for term in expt2.background:
    term.coef.free = True

# %% [markdown]
# #### Perform Fit

# %%
project.analysis.fit()

# %% [markdown]
# #### Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='npd', x_min=35.5, x_max=38.3, show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='xrd', x_min=29.0, x_max=30.4, show_residual=True)
