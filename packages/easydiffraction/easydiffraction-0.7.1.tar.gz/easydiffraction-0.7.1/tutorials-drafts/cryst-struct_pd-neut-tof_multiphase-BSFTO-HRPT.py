# %% [markdown]
# # Structure Refinement: BSFTO, HRPT
#
# This example demonstrates a Rietveld refinement of Bi1−xSmxFe0.94Ti0.06O3
# crystal and magnetic structure...

# %% [markdown]
# ## Import Library

# %%
from easydiffraction import Experiment
from easydiffraction import Project
from easydiffraction import SampleModel

# %% [markdown]
# ## Define Sample Models
#
# This section shows how to add sample models and modify their parameters.
#
# ### Create Sample Model 1: Orthorhombic phase

# %%
model_1 = SampleModel('ort')

# %% [markdown]
# #### Set Space Group

# %%
model_1.space_group.name_h_m = 'P b a m'
model_1.space_group.it_coordinate_system_code = 'abc'

# %% [markdown]
# #### Set Unit Cell

# %%
model_1.cell.length_a = 5.588
model_1.cell.length_b = 11.125
model_1.cell.length_c = 7.876

# %% [markdown]
# #### Set Atom Sites

# %%
model_1.atom_sites.add('Bi1', 'Bi', 0.702, 0.114, 0,     wyckoff_letter='g', b_iso=0.0, occupancy=0.88)
model_1.atom_sites.add('Sm1', 'Sm', 0.702, 0.114, 0,     wyckoff_letter='g', b_iso=0.0, occupancy=0.12)
model_1.atom_sites.add('Bi2', 'Bi', 0.751, 0.132, 0.5,   wyckoff_letter='h', b_iso=0.0, occupancy=0.88)
model_1.atom_sites.add('Sm2', 'Sm', 0.751, 0.132, 0.5,   wyckoff_letter='h', b_iso=0.0, occupancy=0.12)
model_1.atom_sites.add('Fe',  'Fe', 0.236, 0.121, 0.259, wyckoff_letter='i', b_iso=0.0, occupancy=0.94)
model_1.atom_sites.add('Ti',  'Ti', 0.236, 0.121, 0.259, wyckoff_letter='i', b_iso=0.0, occupancy=0.06)
model_1.atom_sites.add('O1',  'O',  0.258, 0.151, 0,     wyckoff_letter='g', b_iso=0.0, occupancy=1.0)
model_1.atom_sites.add('O2',  'O',  0.316, 0.093, 0.5,   wyckoff_letter='h', b_iso=0.0, occupancy=1.0)
model_1.atom_sites.add('O3',  'O',  0.002, 0.258, 0.299, wyckoff_letter='i', b_iso=0.0, occupancy=1.0)
model_1.atom_sites.add('O4',  'O',  0,     0.5,   0.264, wyckoff_letter='f', b_iso=0.0, occupancy=1.0)
model_1.atom_sites.add('O5',  'O',  0,     0,     0.198, wyckoff_letter='e', b_iso=0.0, occupancy=1.0)

# %% [markdown]
# ### Create Sample Model 2: Rhombohedral phase

# %%
model_2 = SampleModel('rho')

# %% [markdown]
# #### Set Space Group

# %%
model_2.space_group.name_h_m = 'R 3 c'
model_2.space_group.it_coordinate_system_code = 'h'

# %% [markdown]
# #### Set Unit Cell

# %%
model_2.cell.length_a = 5.568
model_2.cell.length_c = 13.758

# %% [markdown]
# #### Set Atom Sites

# %%
model_2.atom_sites.add('Bi',  'Bi', 0,     0,     0,     wyckoff_letter='a', b_iso=0.0, occupancy=0.88)
model_2.atom_sites.add('Sm',  'Sm', 0,     0,     0,     wyckoff_letter='a', b_iso=0.0, occupancy=0.12)
model_2.atom_sites.add('Fe',  'Fe', 0,     0,     0.223, wyckoff_letter='a', b_iso=0.0, occupancy=0.94)
model_2.atom_sites.add('Ti',  'Ti', 0,     0,     0.223, wyckoff_letter='a', b_iso=0.0, occupancy=0.06)
model_2.atom_sites.add('O',   'O',  0.436, 0.022, 0.958, wyckoff_letter='b', b_iso=0.0, occupancy=1.0)

# %% [markdown]
# ## Define Experiment
#
# This section shows how to add experiments, configure their parameters, and
# link the sample models defined in the previous step.
#
# #### Download Data

# %%
#download_from_repository('hrpt_n_Bi0p88Sm0p12Fe0p94Ti0p06O3_DW_V_9x8x52_1p49_HI.xye',
#                         branch='develop',
#                         destination='data')

# %% [markdown]
# #### Create Experiment

# %%
experiment = Experiment('hrpt',
                        data_path='data/hrpt_n_Bi0p88Sm0p12Fe0p94Ti0p06O3_DW_V_9x8x52_1p49_HI.xye')

# %% [markdown]
# #### Set Instrument

# %%
experiment.instrument.setup_wavelength = 1.494
experiment.instrument.calib_twotheta_offset = 0.14

# %% [markdown]
# #### Set Peak Profile

# %%
experiment.peak.broad_gauss_u = 0.7
experiment.peak.broad_gauss_v = -0.41
experiment.peak.broad_gauss_w = 0.18
experiment.peak.broad_lorentz_x = 0
experiment.peak.broad_lorentz_y = 0.21

# %% [markdown]
# #### Set Background

# %% [markdown]
# Select the background type.

# %%
experiment.background_type = 'line-segment'

# %% [markdown]
# Add background points.

# %%
experiment.background.add(x=10, y=865)
experiment.background.add(x=30, y=888)
experiment.background.add(x=50, y=893)
experiment.background.add(x=110, y=874)
experiment.background.add(x=165, y=702)

# %% [markdown]
# #### Set Linked Phases

# %%
experiment.linked_phases.add('ort', scale=0.07)
experiment.linked_phases.add('rho', scale=0.21)

# %% [markdown]
# ## Define Project
#
# The project object is used to manage sample models, experiments, and analysis.
#
# #### Create Project

# %%
project = Project()

# %% [markdown]
# #### Set Plotting Engine

# %%
project.plotter.engine = 'plotly'

# %% [markdown]
# #### Add Sample Models

# %%
project.sample_models.add(model_1)
project.sample_models.add(model_2)

# %% [markdown]
# #### Show Sample Models

# %%
project.sample_models.show_names()

# %% [markdown]
# #### Add Experiments

# %%
project.experiments.add(experiment)

# %% [markdown]
# #### Set Excluded Regions
#
# Show measured data as loaded from the file.

# %%
project.plot_meas(expt_name='hrpt')

# %% [markdown]
# Add excluded regions.

# %%
experiment.excluded_regions.add(start=0, end=10)
experiment.excluded_regions.add(start=160, end=180)

# %% [markdown]
# Show excluded regions.

# %%
experiment.excluded_regions.show()

# %% [markdown]
# Show measured data after adding excluded regions.

# %%
project.plot_meas(expt_name='hrpt')

# %% [markdown]
# Show experiment as CIF.

# %%
project.experiments['hrpt'].show_as_cif()

# %% [markdown]
# ## Perform Analysis
#
# This section outlines the analysis process, including how to configure
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
# #### Set Fitting Parameters
#
# Set sample model parameters to be optimized.

# %%
#model_1.cell.length_a.free = True
#model_1.atom_sites['Co'].b_iso.free = True
#model_1.atom_sites['O'].b_iso.free = True

#model_2.cell.length_a.free = True

# %% [markdown]
# Set experiment parameters to be optimized.

# %%
experiment.instrument.calib_twotheta_offset.free = True

# %%
experiment.peak.broad_gauss_u.free = True
experiment.peak.broad_gauss_v.free = True
experiment.peak.broad_gauss_w.free = True
experiment.peak.broad_lorentz_y.free = True

# %%
experiment.linked_phases['ort'].scale.free = True
experiment.linked_phases['rho'].scale.free = True

for point in experiment.background:
    point.y.free = True

# %% [markdown]
# #### Perform Fit

# %%
project.analysis.fit()

# %% [markdown]
# #### Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='hrpt')
