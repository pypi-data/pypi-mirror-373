# %% [markdown]
# # Pair Distribution Function: NaCl, XRD
#
# This example demonstrates a pair distribution function (PDF) analysis of
# NaCl, based on data collected from an X-ray powder diffraction experiment.
#
# The dataset is taken from:
# https://github.com/diffpy/add2019-diffpy-cmi/tree/master

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
project.plotter.x_min = 2.0
project.plotter.x_max = 30.0

# %% [markdown]
# ## Add Sample Model

# %%
project.sample_models.add(name='nacl')

# %%
project.sample_models['nacl'].space_group.name_h_m = 'F m -3 m'
project.sample_models['nacl'].space_group.it_coordinate_system_code = '1'
project.sample_models['nacl'].cell.length_a = 5.62
project.sample_models['nacl'].atom_sites.add(
    label='Na', type_symbol='Na', fract_x=0, fract_y=0, fract_z=0, wyckoff_letter='a', b_iso=1.0
)
project.sample_models['nacl'].atom_sites.add(
    label='Cl', type_symbol='Cl', fract_x=0.5, fract_y=0.5, fract_z=0.5, wyckoff_letter='b', b_iso=1.0
)

# %% [markdown]
# ## Add Experiment

# %%
ed.download_from_repository('NaCl.gr', destination='data')

# %%
project.experiments.add(
    name='xray_pdf',
    sample_form='powder',
    beam_mode='constant wavelength',
    radiation_probe='xray',
    scattering_type='total',
    data_path='data/NaCl.gr',
)

# %%
project.experiments['xray_pdf'].show_supported_peak_profile_types()

# %%
project.experiments['xray_pdf'].show_current_peak_profile_type()

# %%
project.experiments['xray_pdf'].peak_profile_type = 'gaussian-damped-sinc'

# %%
project.experiments['xray_pdf'].peak.damp_q = 0.03
project.experiments['xray_pdf'].peak.broad_q = 0
project.experiments['xray_pdf'].peak.cutoff_q = 21
project.experiments['xray_pdf'].peak.sharp_delta_1 = 0
project.experiments['xray_pdf'].peak.sharp_delta_2 = 5
project.experiments['xray_pdf'].peak.damp_particle_diameter = 0

# %%
project.experiments['xray_pdf'].linked_phases.add(id='nacl', scale=0.5)

# %% [markdown]
# ## Select Fitting Parameters

# %%
project.sample_models['nacl'].cell.length_a.free = True
project.sample_models['nacl'].atom_sites['Na'].b_iso.free = True
project.sample_models['nacl'].atom_sites['Cl'].b_iso.free = True

# %%
project.experiments['xray_pdf'].linked_phases['nacl'].scale.free = True
project.experiments['xray_pdf'].peak.damp_q.free = True
project.experiments['xray_pdf'].peak.sharp_delta_2.free = True

# %% [markdown]
# ## Run Fitting

# %%
project.analysis.current_calculator = 'pdffit'
project.analysis.fit()

# %% [markdown]
# ## Plot Measured vs Calculated

# %%
project.plot_meas_vs_calc(expt_name='xray_pdf')
