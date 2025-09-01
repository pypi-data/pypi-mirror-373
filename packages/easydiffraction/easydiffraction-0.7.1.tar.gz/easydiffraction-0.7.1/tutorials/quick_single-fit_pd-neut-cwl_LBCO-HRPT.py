# %% [markdown]
# # Structure Refinement: LBCO, HRPT
#
# This minimalistic example is designed to be as compact as possible for a
# Rietveld refinement of a crystal structure using constant-wavelength neutron
# powder diffraction data for La0.5Ba0.5CoO3 from HRPT at PSI.
#
# It does not contain any advanced features or options, and includes no
# comments or explanations—these can be found in the other tutorials.
# Default values are used for all parameters if not specified. Only essential
# and self-explanatory code is provided.
#
# The example is intended for users who are already familiar with the
# EasyDiffraction library and want to quickly get started with a simple
# refinement. It is also useful for those who want to see what a refinement
# might look like in code. For a more detailed explanation of the code, please
# refer to the other tutorials.

# %% [markdown]
# ## Import Library

# %%
import easydiffraction as ed

# %% [markdown]
# ## Step 1: Define Project

# %%
project = ed.Project()

# %% [markdown]
# ## Step 2: Define Sample Model

# %%
project.sample_models.add(name='lbco')

# %%
sample_model = project.sample_models['lbco']

# %%
sample_model.space_group.name_h_m = 'P m -3 m'
sample_model.space_group.it_coordinate_system_code = '1'

# %%
sample_model.cell.length_a = 3.88

# %%
sample_model.atom_sites.add('La', 'La', 0, 0, 0, b_iso=0.5, occupancy=0.5)
sample_model.atom_sites.add('Ba', 'Ba', 0, 0, 0, b_iso=0.5, occupancy=0.5)
sample_model.atom_sites.add('Co', 'Co', 0.5, 0.5, 0.5, b_iso=0.5)
sample_model.atom_sites.add('O', 'O', 0, 0.5, 0.5, b_iso=0.5)

# %% [markdown]
# ## Step 3: Define Experiment

# %%
ed.download_from_repository('hrpt_lbco.xye', destination='data')

# %%
project.experiments.add(
    name='hrpt',
    sample_form='powder',
    beam_mode='constant wavelength',
    radiation_probe='neutron',
    data_path='data/hrpt_lbco.xye',
)

# %%
experiment = project.experiments['hrpt']

# %%
experiment.instrument.setup_wavelength = 1.494
experiment.instrument.calib_twotheta_offset = 0.6

# %%
experiment.peak.broad_gauss_u = 0.1
experiment.peak.broad_gauss_v = -0.1
experiment.peak.broad_gauss_w = 0.1
experiment.peak.broad_lorentz_y = 0.1

# %%
experiment.background.add(x=10, y=170)
experiment.background.add(x=30, y=170)
experiment.background.add(x=50, y=170)
experiment.background.add(x=110, y=170)
experiment.background.add(x=165, y=170)

# %%
experiment.excluded_regions.add(start=0, end=5)
experiment.excluded_regions.add(start=165, end=180)

# %%
experiment.linked_phases.add(id='lbco', scale=10.0)

# %% [markdown]
# ## Step 4: Perform Analysis

# %%
sample_model.cell.length_a.free = True

sample_model.atom_sites['La'].b_iso.free = True
sample_model.atom_sites['Ba'].b_iso.free = True
sample_model.atom_sites['Co'].b_iso.free = True
sample_model.atom_sites['O'].b_iso.free = True

# %%
experiment.instrument.calib_twotheta_offset.free = True

experiment.peak.broad_gauss_u.free = True
experiment.peak.broad_gauss_v.free = True
experiment.peak.broad_gauss_w.free = True
experiment.peak.broad_lorentz_y.free = True

experiment.background['10'].y.free = True
experiment.background['30'].y.free = True
experiment.background['50'].y.free = True
experiment.background['110'].y.free = True
experiment.background['165'].y.free = True

experiment.linked_phases['lbco'].scale.free = True

# %%
project.analysis.fit()

# %%
project.plot_meas_vs_calc(expt_name='hrpt', show_residual=True)
