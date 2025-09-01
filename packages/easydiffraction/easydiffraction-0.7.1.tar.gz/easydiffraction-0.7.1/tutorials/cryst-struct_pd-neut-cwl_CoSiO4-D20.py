# %% [markdown]
# # Structure Refinement: Co2SiO4, D20
#
# This example demonstrates a Rietveld refinement of Co2SiO4 crystal structure
# using constant wavelength neutron powder diffraction data from D20 at ILL.

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
model = SampleModel('cosio')

# %% [markdown]
# #### Set Space Group

# %%
model.space_group.name_h_m = 'P n m a'
model.space_group.it_coordinate_system_code = 'abc'

# %% [markdown]
# #### Set Unit Cell

# %%
model.cell.length_a = 10.3
model.cell.length_b = 6.0
model.cell.length_c = 4.8

# %% [markdown]
# #### Set Atom Sites

# %%
model.atom_sites.add('Co1', 'Co', 0, 0, 0, wyckoff_letter='a', b_iso=0.5)
model.atom_sites.add('Co2', 'Co', 0.279, 0.25, 0.985, wyckoff_letter='c', b_iso=0.5)
model.atom_sites.add('Si', 'Si', 0.094, 0.25, 0.429, wyckoff_letter='c', b_iso=0.5)
model.atom_sites.add('O1', 'O', 0.091, 0.25, 0.771, wyckoff_letter='c', b_iso=0.5)
model.atom_sites.add('O2', 'O', 0.448, 0.25, 0.217, wyckoff_letter='c', b_iso=0.5)
model.atom_sites.add('O3', 'O', 0.164, 0.032, 0.28, wyckoff_letter='d', b_iso=0.5)

# %% [markdown]
# #### Symmetry Constraints
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
download_from_repository('co2sio4_d20.xye', destination='data')

# %% [markdown]
# #### Create Experiment

# %%
expt = Experiment('d20', data_path='data/co2sio4_d20.xye')

# %% [markdown]
# #### Set Instrument

# %%
expt.instrument.setup_wavelength = 1.87
expt.instrument.calib_twotheta_offset = 0.1

# %% [markdown]
# #### Set Peak Profile

# %%
expt.peak.broad_gauss_u = 0.3
expt.peak.broad_gauss_v = -0.5
expt.peak.broad_gauss_w = 0.4

# %% [markdown]
# #### Set Background

# %%
expt.background.add(x=8, y=500)
expt.background.add(x=9, y=500)
expt.background.add(x=10, y=500)
expt.background.add(x=11, y=500)
expt.background.add(x=12, y=500)
expt.background.add(x=15, y=500)
expt.background.add(x=25, y=500)
expt.background.add(x=30, y=500)
expt.background.add(x=50, y=500)
expt.background.add(x=70, y=500)
expt.background.add(x=90, y=500)
expt.background.add(x=110, y=500)
expt.background.add(x=130, y=500)
expt.background.add(x=150, y=500)

# %% [markdown]
# #### Set Linked Phases

# %%
expt.linked_phases.add('cosio', scale=1.0)

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
project.plot_meas_vs_calc(expt_name='d20', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='d20', x_min=41, x_max=54, show_residual=True)

# %% [markdown]
# #### Set Free Parameters

# %%
model.cell.length_a.free = True
model.cell.length_b.free = True
model.cell.length_c.free = True

model.atom_sites['Co2'].fract_x.free = True
model.atom_sites['Co2'].fract_z.free = True
model.atom_sites['Si'].fract_x.free = True
model.atom_sites['Si'].fract_z.free = True
model.atom_sites['O1'].fract_x.free = True
model.atom_sites['O1'].fract_z.free = True
model.atom_sites['O2'].fract_x.free = True
model.atom_sites['O2'].fract_z.free = True
model.atom_sites['O3'].fract_x.free = True
model.atom_sites['O3'].fract_y.free = True
model.atom_sites['O3'].fract_z.free = True

model.atom_sites['Co1'].b_iso.free = True
model.atom_sites['Co2'].b_iso.free = True
model.atom_sites['Si'].b_iso.free = True
model.atom_sites['O1'].b_iso.free = True
model.atom_sites['O2'].b_iso.free = True
model.atom_sites['O3'].b_iso.free = True

# %%
expt.linked_phases['cosio'].scale.free = True

expt.instrument.calib_twotheta_offset.free = True

expt.peak.broad_gauss_u.free = True
expt.peak.broad_gauss_v.free = True
expt.peak.broad_gauss_w.free = True
expt.peak.broad_lorentz_y.free = True

for point in expt.background:
    point.y.free = True

# %% [markdown]
# #### Set Constraints
#
# Set aliases for parameters.

# %%
project.analysis.aliases.add(
    label='biso_Co1',
    param_uid=project.sample_models['cosio'].atom_sites['Co1'].b_iso.uid,
)
project.analysis.aliases.add(
    label='biso_Co2',
    param_uid=project.sample_models['cosio'].atom_sites['Co2'].b_iso.uid,
)

# %% [markdown]
# Set constraints.

# %%
project.analysis.constraints.add(
    lhs_alias='biso_Co2',
    rhs_expr='biso_Co1',
)

# %% [markdown]
# Apply constraints.

# %%
project.analysis.apply_constraints()

# %% [markdown]
# #### Run Fitting

# %%
project.analysis.fit()

# %% [markdown]
# #### Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='d20', show_residual=True)

# %%
project.plot_meas_vs_calc(expt_name='d20', x_min=41, x_max=54, show_residual=True)

# %% [markdown]
# ## Summary
#
# This final section shows how to review the results of the analysis.

# %% [markdown]
# #### Show Project Summary

# %%
project.summary.show_report()
