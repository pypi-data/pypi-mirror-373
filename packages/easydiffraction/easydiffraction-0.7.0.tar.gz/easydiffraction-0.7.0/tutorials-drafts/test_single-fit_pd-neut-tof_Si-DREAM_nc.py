# %% [markdown]
# # Structure Refinement: Si (NCrystal sim), DREAM

# %%
import easydiffraction as ed

# %% [markdown]
# ## Step 1: Project

# %%
project = ed.Project()

# %%
project.plotter.engine = 'plotly'

# %% [markdown]
# ## Step 2: Sample Model

# %%
project.sample_models.add(name='si')
sample_model = project.sample_models['si']

# %%
sample_model.space_group.name_h_m.value = 'F d -3 m'
sample_model.space_group.it_coordinate_system_code = '1'

# %%
sample_model.cell.length_a = 5.46872800 # 5.43146

# %%
sample_model.atom_sites.add(label='Si',
                            type_symbol='Si',
                            fract_x=0.,
                            fract_y=0.,
                            fract_z=0.5,
                            wyckoff_letter='b',
                            b_iso=0.5)

# %% [markdown]
# ## Step 3: Experiment

# %%
#ed.download_from_repository('NOM_9999_Si_640g_PAC_50_ff_ftfrgr_up-to-50.gr',
#                            branch='d-spacing',
#                            destination='data')

# %%
project.experiments.add(name='dream',
                        sample_form='powder',
                        beam_mode='time-of-flight',
                        radiation_probe='neutron',
                        scattering_type='bragg',
                        data_path='tutorials/data/DREAM_mantle_bc240_nist_cif_2.xye')
                        #data_path='tutorials/data/DREAM_mantle_bc240_nist_nc_2.xye')
experiment = project.experiments['dream']

# %%
experiment.instrument.setup_twotheta_bank = 90.20761742567521 # 144.845 # 90.20761742567521
experiment.instrument.calib_d_to_tof_offset = 0.0
experiment.instrument.calib_d_to_tof_linear = 27896.388403762866 # 7476.91 # 278963884037.62866
experiment.instrument.calib_d_to_tof_linear = 26935.57560870018
experiment.instrument.calib_d_to_tof_quad = -0.00001 # -1.54 # -1.0

# %%
experiment.peak_profile_type = 'pseudo-voigt * ikeda-carpenter'
experiment.peak.broad_gauss_sigma_0 = 3.0
experiment.peak.broad_gauss_sigma_1 = 40.0
experiment.peak.broad_gauss_sigma_2 = 0.0
experiment.peak.broad_mix_beta_0 = 0.024 # 0.04221
experiment.peak.broad_mix_beta_1 = 0 # 0.00946
experiment.peak.asym_alpha_0 = 0.14
experiment.peak.asym_alpha_1 = 0.0 # 0.5971

# %%
experiment.background_type = 'line-segment'
for x in range(10000, 70000, 5000):
    experiment.background.add(x=x, y=0.2)

# %%
experiment.linked_phases.add('si', scale=1)

# %% [markdown]
# ## Step 4: Analysis

# %%
project.plot_meas_vs_calc(expt_name='dream',
                          show_residual=True)
#exit()

# %%
#sample_model.cell.length_a.free = True

experiment.linked_phases['si'].scale.free = True
#experiment.instrument.calib_d_to_tof_offset.free = True

experiment.peak.broad_gauss_sigma_0.free = True
experiment.peak.broad_gauss_sigma_1.free = True
#experiment.peak.broad_gauss_sigma_2.free = True
experiment.peak.broad_mix_beta_0.free = True
#experiment.peak.broad_mix_beta_1.free = True
experiment.peak.asym_alpha_0.free = True
#experiment.peak.asym_alpha_1.free = True



project.analysis.fit()
project.plot_meas_vs_calc(expt_name='dream', show_residual=True)

exit()



project.sample_models['lbco'].atom_sites['La'].b_iso.free = True
project.sample_models['lbco'].atom_sites['Ba'].b_iso.free = True
project.sample_models['lbco'].atom_sites['Co'].b_iso.free = True
project.sample_models['lbco'].atom_sites['O'].b_iso.free = True

# %%
project.experiments['hrpt'].linked_phases['lbco'].scale.free = True

project.experiments['hrpt'].instrument.calib_twotheta_offset.free = True

project.experiments['hrpt'].background['10'].y.free = True
project.experiments['hrpt'].background['30'].y.free = True
project.experiments['hrpt'].background['50'].y.free = True
project.experiments['hrpt'].background['110'].y.free = True
project.experiments['hrpt'].background['165'].y.free = True

project.experiments['hrpt'].peak.broad_gauss_u.free = True
project.experiments['hrpt'].peak.broad_gauss_v.free = True
project.experiments['hrpt'].peak.broad_gauss_w.free = True
project.experiments['hrpt'].peak.broad_lorentz_y.free = True

# %%
project.analysis.fit()

# %%
project.plot_meas_vs_calc(expt_name='hrpt', show_residual=True)
