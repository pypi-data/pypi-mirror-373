# %% [markdown]
# # Pair Distribution Function: Ni, NPD
#
# This example demonstrates a pair distribution function (PDF) analysis of Ni,
# based on data collected from a constant wavelength neutron powder diffraction
# experiment.
#
# The dataset is taken from:
# https://github.com/diffpy/cmi_exchange/tree/main/cmi_scripts/fitNiPDF

# %% [markdown]
# ## Import Library

# %%
import easydiffraction as ed

# %% [markdown]
# ## Create Project

# %%
project = ed.Project()

# %% [markdown]
# ## Set Plotting Engine

# %%
project.plotter.engine = 'plotly'

# %% [markdown]
# ## Add Sample Model

# %%
project.sample_models.add(name='ni')

# %%
project.sample_models['ni'].space_group.name_h_m = 'F m -3 m'
project.sample_models['ni'].space_group.it_coordinate_system_code = '1'
project.sample_models['ni'].cell.length_a = 3.52387
project.sample_models['ni'].atom_sites.add(
    label='Ni', type_symbol='Ni', fract_x=0.0, fract_y=0.0, fract_z=0.0, wyckoff_letter='a', b_iso=0.5
)

# %% [markdown]
# ## Add Experiment

# %%
ed.download_from_repository('ni-q27r100-neutron_from-2.gr', destination='data')

# %%
project.experiments.add(
    name='pdf',
    sample_form='powder',
    beam_mode='constant wavelength',
    radiation_probe='neutron',
    scattering_type='total',
    data_path='data/ni-q27r100-neutron_from-2.gr',
)

# %%
project.experiments['pdf'].linked_phases.add(id='ni', scale=1.0)
project.experiments['pdf'].peak.damp_q = 0
project.experiments['pdf'].peak.broad_q = 0.03
project.experiments['pdf'].peak.cutoff_q = 27.0
project.experiments['pdf'].peak.sharp_delta_1 = 0.0
project.experiments['pdf'].peak.sharp_delta_2 = 2.0
project.experiments['pdf'].peak.damp_particle_diameter = 0

# %% [markdown]
# ## Select Fitting Parameters

# %%
project.sample_models['ni'].cell.length_a.free = True
project.sample_models['ni'].atom_sites['Ni'].b_iso.free = True

# %%
project.experiments['pdf'].linked_phases['ni'].scale.free = True
project.experiments['pdf'].peak.broad_q.free = True
project.experiments['pdf'].peak.sharp_delta_2.free = True

# %% [markdown]
# ## Run Fitting

# %%
project.analysis.current_calculator = 'pdffit'
project.analysis.fit()

# %% [markdown]
# ## Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='pdf', show_residual=True)
