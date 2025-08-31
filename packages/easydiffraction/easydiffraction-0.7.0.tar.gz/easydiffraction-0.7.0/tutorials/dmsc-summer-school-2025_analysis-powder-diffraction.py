# %% [markdown]
# # Fitting Powder Diffraction data
#
# This notebook guides you through the Rietveld refinement of crystal
# structures using simulated powder diffraction data. It consists of two parts:
# - Introduction: A simple reference fit using silicon (Si) crystal structure.
# - Exercise: A more complex fit using La₀.₅Ba₀.₅CoO₃ (LBCO) crystal structure.
#
# ## 🛠️ Import Library
#
# We start by importing the necessary library for the analysis. In this
# notebook, we use the EasyDiffraction library. As mentioned in the
# introduction to EasyScience, EasyDiffraction is built on that framework and
# offers a high-level interface focused specifically for diffraction analysis.
#
# This notebook is self-contained and designed for hands-on learning.
# However, if you're interested in exploring more advanced features or learning
# about additional capabilities of the EasyDiffraction library, please refer to
# the official documentation: https://docs.easydiffraction.org/lib
#
# Depending on your requirements, you may choose to import only specific
# classes. However, for the sake of simplicity in this notebook, we will import
# the entire library.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/first-steps/#importing-easydiffraction)
# for more details about importing the EasyDiffraction library and
# its components.

# %%
import easydiffraction as ed

# %% [markdown]
# ## 📘 Introduction: Simple Reference Fit – Si
#
# Before diving into the more complex fitting exercise with the La₀.₅Ba₀.₅CoO₃
# (LBCO) crystal structure, let's start with a simpler example using the
# silicon (Si) crystal structure. This will help us understand the basic
# concepts and steps involved in fitting a crystal structure using powder
# diffraction data.
#
# For this part of the notebook, we will use the powder diffraction data
# previously simulated using the Si crystal structure.
#
# ### 📦 Create a Project – 'reference'
#
# In EasyDiffraction, a project serves as a container for all information
# related to the analysis of a specific experiment or set of experiments. It
# enables you to organize your data, experiments, sample models, and fitting
# parameters in a structured manner. You can think of it as a folder containing
# all the essential details about your analysis. The project also allows
# us to visualize both the measured and calculated diffraction patterns, among
# other things.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/project/)
# for more details about creating a project and its purpose in the
# analysis workflow.

# %%
project_1 = ed.Project(name='reference')

# %% [markdown]
#
# You can set the title and description of the project to provide context
# and information about the analysis being performed. This is useful for
# documentation purposes and helps others (or yourself in the future)
# understand the purpose of the project at a glance.

# %%
project_1.info.title = 'Reference Silicon Fit'
project_1.info.description = 'Fitting simulated powder diffraction pattern of Si.'

# %% [markdown]
# ### 🔬 Create an Experiment
#
# An experiment
# represents a specific diffraction measurement performed on a specific sample
# using a particular instrument. It contains details about the measured data,
# instrument parameters, and other relevant information.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/experiment/)
# for more details about experiments and their purpose in the analysis workflow.

# %%
dir_path = 'data'
file_name = 'reduced_Si.xye'
si_xye_path = f'{dir_path}/{file_name}'

# %% [markdown]
# Uncomment the following cell if your data reduction failed and the reduced
# data file is missing. In this case, you can download our pre-generated
# reduced data file from the EasyDiffraction repository.
# The `download_from_repository` function will not overwrite an existing file
# unless you set `overwrite=True`, so it's safe to run even if the file is
# already present.

# %%
ed.download_from_repository(file_name, destination=dir_path)

# %% [markdown]
# Now we can create the experiment and load the measured data.
# In this case, the experiment is defined as a powder diffraction measurement
# using time-of-flight neutrons. The measured data is loaded from a file
# containing the reduced diffraction pattern of Si from the data reduction
# notebook.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/experiment/#defining-an-experiment-manually)
# for more details about different types of experiments.

# %%
project_1.experiments.add(
    name='sim_si',
    sample_form='powder',
    beam_mode='time-of-flight',
    radiation_probe='neutron',
    data_path=si_xye_path,
)

# %% [markdown]
# #### Inspect Measured Data
#
# After creating the experiment, we can examine the measured data. The measured
# data consists of a diffraction pattern having time-of-flight (TOF) values
# and corresponding intensities. The TOF values are given in microseconds (μs),
# and the intensities are in arbitrary units.
#
# The data is stored in XYE format, a simple text format containing three
# columns: TOF, intensity, and intensity error (if available).

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/experiment/#measured-data-category)
# for more details about the measured data and its format.

# To visualize the measured data, we can use the `plot_meas` method of the
# project. Before plotting, we need to set the plotting engine to 'plotly',
# which provides interactive visualizations.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://easyscience.github.io/diffraction-lib/user-guide/first-steps/#supported-plotters)
# for more details about setting the plotting engine.

# %%
project_1.plotter.engine = 'plotly'

# %%
project_1.plot_meas(expt_name='sim_si')

# %% [markdown]
# If you zoom in on the highest TOF peak (around 120,000 μs), you will notice
# that it has a broad and unusual shape. This distortion, along with additional
# effects on the low TOF peaks, is most likely an artifact related to the
# simplifications made during the simulation and/or reduction process and is
# currently under investigation. However, this is outside the scope of this
# school. Therefore, we will simply exclude both the low and high TOF regions
# from the analysis by adding an excluded regions to the experiment.
#
# In real experiments, it is often necessary to exclude certain regions from
# the measured data. For example, the direct beam can significantly increase
# the background at very low angles, making those parts of the diffractogram
# unreliable. Additionally, sample environment components may introduce
# unwanted peaks. In such cases, excluding specific regions is often simpler
# and more effective than modeling them with an additional sample phase.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/experiment/#excluded-regions-category)
# for more details about excluding regions from the measured data.

# %%
project_1.experiments['sim_si'].excluded_regions.add(start=0, end=55000)
project_1.experiments['sim_si'].excluded_regions.add(start=105500, end=200000)

# %% [markdown]
# To visualize the effect of excluding the high TOF region, we can plot
# the measured data again. The excluded region will be omitted from the plot
# and is not used in the fitting process.

# %%
project_1.plot_meas(expt_name='sim_si')

# %% [markdown]
# #### Set Instrument Parameters
#
# After the experiment is created and measured data is loaded, we need
# to set the instrument parameters.
#
# In this type of experiment, the instrument parameters define how the
# measured data is converted between d-spacing and time-of-flight (TOF)
# during the data reduction process as well as the angular position of the
# detector. So, we put values based on those from the reduction. These
# values can be found in the header of the corresponding .XYE file. Their
# names are `two_theta` and `DIFC`, which stand for the two-theta angle
# and the linear conversion factor from d-spacing to TOF, respectively.
#
# You can set them manually, but it is more convenient to use the
# `get_value_from_xye_header` function from the EasyDiffraction library.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/experiment/#instrument-category)
# for more details about the instrument parameters.

# %%
project_1.experiments['sim_si'].instrument.setup_twotheta_bank = ed.get_value_from_xye_header(si_xye_path, 'two_theta')
project_1.experiments['sim_si'].instrument.calib_d_to_tof_linear = ed.get_value_from_xye_header(si_xye_path, 'DIFC')

# %% [markdown]
# Before proceeding, let's take a quick look at the concept of parameters in
# EasyDiffraction, which is similar to the parameter concept in EasyScience.
# The current version of EasyDiffraction is transitioning to reuse the
# parameter system from EasyScience.
#
# That is, every parameter is an object, which has different attributes,
# such as `value`, `units`, etc. To display the parameter of interest, you can
# simply print the parameter object.
#
# For example, to display the linear conversion factor from d-spacing to TOF,
# which is the `calib_d_to_tof_linear` parameter, you can do the following:

# %%
project_1.experiments['sim_si'].instrument.calib_d_to_tof_linear

# %% [markdown]
# The `value` attribute represents the current value of the parameter as a
# float. You can access it directly by using the `value` attribute of the
# parameter. This is useful when you want to use the parameter value in
# calculations or when you want to assign it to another parameter. For example,
# to get only the value of the same parameter as floating point number, but not
# the whole object, you can do the following:

# %%
project_1.experiments['sim_si'].instrument.calib_d_to_tof_linear.value

# %% [markdown]
# Note that to set the value of the parameter, you can simply assign a new
# value to the parameter object without using the `value` attribute, as we did
# above.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/parameters/)
# for more details about parameters in EasyDiffraction and their attributes.

# %% [markdown]
# #### Set Peak Profile Parameters
#
# The next set of parameters is needed to define the peak profile used in the
# fitting process. The peak profile describes the shape of the diffraction
# peaks. They include parameters for the broadening and asymmetry of the peaks.
#
# There are several commonly used peak profile functions:
# - **Gaussian**: Describes peaks with a symmetric bell-shaped curve, often
#   used when instrumental broadening dominates.
#   [Click for more details.](https://mantidproject.github.io/docs-versioned/v6.1.0/fitting/fitfunctions/Gaussian.html)
# - **Lorentzian**: Produces narrower central peaks with longer tails,
#   frequently used to model size broadening effects.
#   [Click for more details.](https://mantidproject.github.io/docs-versioned/v6.1.0/fitting/fitfunctions/Lorentzian.html)
# - **Pseudo-Voigt**: A linear combination of Gaussian and Lorentzian
#   components, providing flexibility to represent real diffraction peaks.
#   [Click for more details.](https://mantidproject.github.io/docs-versioned/v6.1.0/fitting/fitfunctions/PseudoVoigt.html)
# - **Pseudo-Voigt convoluted with Ikeda-Carpenter**: Incorporates the
#   asymmetry introduced by the neutron pulse shape in time-of-flight
#   instruments. This is a common choice for TOF neutron powder diffraction
#   data.
#   [Click for more details.](https://docs.mantidproject.org/v6.1.0/fitting/fitfunctions/IkedaCarpenterPV.html)
#
# Here, we use a pseudo-Voigt peak profile function with Ikeda-Carpenter
# asymmetry.
#
# The parameter values are typically determined experimentally on the same
# instrument and under the same configuration as the data being analyzed,
# using measurements of a standard sample. In our case, the Si sample serves
# as this standard reference. We will refine the peak profile parameters here,
# and these refined values will be used as starting points for the more
# complex fit in the next part of the notebook. For this initial fit, we will
# provide reasonable physical guesses as starting values.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/experiment/#peak-category)
# for more details about the peak profile types.

# %%
project_1.experiments['sim_si'].peak_profile_type = 'pseudo-voigt * ikeda-carpenter'
project_1.experiments['sim_si'].peak.broad_gauss_sigma_0 = 69498
project_1.experiments['sim_si'].peak.broad_gauss_sigma_1 = -55578
project_1.experiments['sim_si'].peak.broad_gauss_sigma_2 = 14560
project_1.experiments['sim_si'].peak.broad_mix_beta_0 = 0.0019
project_1.experiments['sim_si'].peak.broad_mix_beta_1 = 0.0137
project_1.experiments['sim_si'].peak.asym_alpha_0 = -0.0055
project_1.experiments['sim_si'].peak.asym_alpha_1 = 0.0147

# %% [markdown]
# #### Set Background
#
# The background of the diffraction pattern represents the portion of the
# pattern that is not related to the crystal structure of the sample. It's
# rather represents noise and other sources of scattering that can affect
# the measured intensities. This includes contributions from the instrument,
# the sample holder, the sample environment, and other sources of incoherent
# scattering.
#
# The background can be modeled in various ways. In this example, we will use
# a simple line segment background, which is a common approach for powder
# diffraction data. The background intensity at any point is defined by linear
# interpolation between neighboring points. The background points are selected
# to span the range of the diffraction pattern while avoiding the peaks.
#
# We will add several background points at specific TOF values (in μs) and
# corresponding intensity values. These points are chosen to represent the
# background level in the diffraction pattern free from any peaks.
#
# The background points are added using the `add` method of the `background`
# object. The `x` parameter represents the TOF value, and the `y` parameter
# represents the intensity value at that TOF.
#
# Let's set all the background points at a constant value of 0.01, which can be
# roughly estimated by the eye, and we will refine them later during the
# fitting process.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/experiment/#background-category)
# for more details about the background and its types.

# %%
project_1.experiments['sim_si'].background_type = 'line-segment'
project_1.experiments['sim_si'].background.add(x=50000, y=0.01)
project_1.experiments['sim_si'].background.add(x=60000, y=0.01)
project_1.experiments['sim_si'].background.add(x=70000, y=0.01)
project_1.experiments['sim_si'].background.add(x=80000, y=0.01)
project_1.experiments['sim_si'].background.add(x=90000, y=0.01)
project_1.experiments['sim_si'].background.add(x=100000, y=0.01)
project_1.experiments['sim_si'].background.add(x=110000, y=0.01)

# %% [markdown]
# ### 🧩 Create a Sample Model – Si
#
# After setting up the experiment, we need to create a sample model that
# describes the crystal structure of the sample being analyzed.
#
# In this case, we will create a sample model for silicon (Si) with a
# cubic crystal structure. The sample model contains information about the
# space group, lattice parameters, atomic positions of the atoms in the
# unit cell, atom types, occupancies and atomic displacement parameters.
# The sample model is essential for the fitting process, as it
# is used to calculate the expected diffraction pattern.
#
# EasyDiffraction refines the crystal structure of the sample,
# but does not solve it. Therefore, we need a good starting point with
# reasonable structural parameters.
#
# Here, we define the Si structure as a
# cubic structure. As this is a cubic structure, we only need to define
# the single lattice parameter, which
# is the length of the unit cell edge. The Si crystal structure has a
# single atom in the unit cell, which is located at the origin (0, 0, 0) of
# the unit cell. The symmetry of this site is defined by the Wyckoff letter
# 'a'. The atomic displacement parameter defines the thermal vibrations of the
# atoms in the unit cell and is presented as an isotropic parameter (B_iso).
#
# Sometimes, the initial crystal structure parameters can be obtained
# from one of the crystallographic databases, like for example
# the Crystallography Open Database (COD). In this case, we use the COD
# entry for silicon as a reference for the initial crystal structure model:
# https://www.crystallography.net/cod/4507226.html
#
# Usually, the crystal structure parameters are provided in a CIF file
# format, which is a standard format for crystallographic data. An example
# of a CIF file for silicon is shown below. The CIF file contains the
# space group information, unit cell parameters, and atomic positions.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/data-format/)
# for more details about the CIF format and its use in
# EasyDiffraction.

# %% [markdown]
# ```
# data_si
#
# _space_group.name_H-M_alt  "F d -3 m"
# _space_group.IT_coordinate_system_code  2
#
# _cell.length_a      5.43
# _cell.length_b      5.43
# _cell.length_c      5.43
# _cell.angle_alpha  90.0
# _cell.angle_beta   90.0
# _cell.angle_gamma  90.0
#
# loop_
# _atom_site.label
# _atom_site.type_symbol
# _atom_site.fract_x
# _atom_site.fract_y
# _atom_site.fract_z
# _atom_site.wyckoff_letter
# _atom_site.occupancy
# _atom_site.ADP_type
# _atom_site.B_iso_or_equiv
# Si Si   0 0 0   a  1.0   Biso 0.89
# ```

# %% [markdown]
#
# As with adding the experiment in the
# previous step, we will create a default sample model
# and then modify its parameters to match the Si structure.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/model/)
# for more details about sample models and their purpose in the data
# analysis workflow.

# %% [markdown]
# #### Add Sample Model

# %%
project_1.sample_models.add(name='si')

# %% [markdown]
# #### Set Space Group

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/model/#space-group-category)
# for more details about the space group.

# %%
project_1.sample_models['si'].space_group.name_h_m = 'F d -3 m'
project_1.sample_models['si'].space_group.it_coordinate_system_code = '2'

# %% [markdown]
# #### Set Lattice Parameters

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/model/#cell-category)
# for more details about the unit cell parameters.

# %%
project_1.sample_models['si'].cell.length_a = 5.43

# %% [markdown]
# #### Set Atom Sites

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/model/#atom-sites-category)
# for more details about the atom sites category.

# %%
project_1.sample_models['si'].atom_sites.add(
    label='Si',
    type_symbol='Si',
    fract_x=0,
    fract_y=0,
    fract_z=0,
    wyckoff_letter='a',
    b_iso=0.89,
)

# %% [markdown]
# ### 🔗 Assign Sample Model to Experiment
#
# Now we need to assign, or link, this sample model to the experiment created
# above. This linked crystallographic phase will be used to calculate the
# expected diffraction pattern based on the crystal structure defined in the
# sample model.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/experiment/#linked-phases-category)
# for more details about linking a sample model to an experiment.

# %%
project_1.experiments['sim_si'].linked_phases.add(id='si', scale=1.0)

# %% [markdown]
# ### 🚀 Analyze and Fit the Data
#
# After setting up the experiment and sample model, we can now analyze the
# measured diffraction pattern and perform the fit. Building on the analogies
# from the EasyScience library and the previous notebooks, we can say that all
# the parameters we introduced earlier — those defining the sample model (crystal
# structure parameters) and the experiment (instrument, background, and peak
# profile parameters) — together form the complete set of parameters that can be
# refined during the fitting process.
#
# Unlike in the previous analysis notebooks, we will not create a **math_model**
# object here. The mathematical model used to calculate the expected diffraction
# pattern is already defined in the library and will be applied automatically
# during the fitting process.

# %% [markdown]
# **Reminder:**
#
# The fitting process involves comparing the measured diffraction pattern with
# the calculated diffraction pattern based on the sample model and instrument
# parameters. The goal is to adjust the parameters of the sample model and
# the experiment to minimize the difference between the measured and calculated
# diffraction patterns. This is done by refining the parameters of the sample
# model and the instrument settings to achieve a better fit.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/analysis/#minimization-optimization)
# for more details about the fitting process in EasyDiffraction.

# %% [markdown]
# #### Set Fit Parameters
#
# To perform the fit, we need to specify the refinement parameters. These
# are the parameters that will be adjusted during the fitting process to
# minimize the difference between the measured and calculated diffraction
# patterns. This is done by setting the `free` attribute of the
# corresponding parameters to `True`.
#
# Note: setting `param.free = True` is equivalent to using
# `param.fixed = False` in the EasyScience library.
#
# We will refine the scale factor of the Si phase, the intensities of the
# background points as well as the peak profile parameters. The structure
# parameters of the Si phase will not be refined, as this sample is
# considered a reference sample with known parameters.

# %%
project_1.experiments['sim_si'].linked_phases['si'].scale.free = True

for line_segment in project_1.experiments['sim_si'].background:
    line_segment.y.free = True

project_1.experiments['sim_si'].peak.broad_gauss_sigma_0.free = True
project_1.experiments['sim_si'].peak.broad_gauss_sigma_1.free = True
project_1.experiments['sim_si'].peak.broad_gauss_sigma_2.free = True
project_1.experiments['sim_si'].peak.broad_mix_beta_0.free = True
project_1.experiments['sim_si'].peak.broad_mix_beta_1.free = True
project_1.experiments['sim_si'].peak.asym_alpha_0.free = True
project_1.experiments['sim_si'].peak.asym_alpha_1.free = True

# %% [markdown]
# #### Show Free Parameters
#
# We can check which parameters are free to be refined by calling the
# `show_free_params` method of the `analysis` object of the project.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://easyscience.github.io/diffraction-lib/user-guide/first-steps/#available-parameters)
# for more details on how to
# - show all parameters of the project,
# - show all fittable parameters, and
# - show only free parameters of the project.

# %%
project_1.analysis.show_free_params()

# %% [markdown]
# #### Visualize Diffraction Patterns
#
# Before performing the fit, we can visually compare the measured
# diffraction pattern with the calculated diffraction pattern based on the
# initial parameters of the sample model and the instrument.
# This provides an indication of how well the initial parameters
# match the measured data. The `plot_meas_vs_calc` method of the project
# allows this comparison.

# %%
project_1.plot_meas_vs_calc(expt_name='sim_si')

# %% [markdown]
# #### Run Fitting
#
# We can now perform the fit using the `fit` method of the `analysis`
# object of the project.

# %% [markdown] tags=["doc-link"]
# 📖 See [documentation](https://docs.easydiffraction.org/lib/user-guide/analysis-workflow/analysis/#perform-fit)
# for more details about the fitting process.

# %%
project_1.analysis.fit()

# %% [markdown]
# #### Check Fit Results
# You can
# see that the agreement between the measured and calculated diffraction
# patterns is now much improved and that the intensities of the
# calculated peaks align much better with the measured peaks. To check the
# quality of the fit numerically, we can look at the goodness-of-fit
# χ² value and the reliability R-factors. The χ² value is a measure of how well
# the calculated diffraction pattern matches the measured pattern, and it is
# calculated as the sum of the squared differences between the measured and
# calculated intensities, divided by the number of data points. Ideally, the
# χ² value should be close to 1, indicating a good fit.

# %% [markdown]
# #### Visualize Fit Results
#
# After the fit is completed, we can plot the comparison between the
# measured and calculated diffraction patterns again to see how well the fit
# improved the agreement between the two. The calculated diffraction pattern
# is now based on the refined parameters.

# %%
project_1.plot_meas_vs_calc(expt_name='sim_si')

# %% [markdown]
# #### TOF vs d-spacing
#
# The diffraction pattern is typically analyzed and plotted in the
# time-of-flight (TOF) axis, which represents the time it takes for neutrons
# to travel from the sample to the detector. However, it is sometimes more
# convenient to visualize the diffraction pattern in the d-spacing axis,
# which represents the distance between planes in the crystal lattice.
#
# The conversion from d-spacing to TOF was already introduced in the data
# reduction notebook. As a reminder, the two are related through the
# instrument calibration parameters according to the equation:
#
# $$
# \text{TOF} = \text{offset} + \text{linear} \cdot d + \text{quad} \cdot d^{2},
# $$
#
# where `offset`, `linear`, and `quad` are calibration parameters.
#
# In our case, only the `linear` term is used (the `calib_d_to_tof_linear`
# parameter we set earlier). The `offset` and `quad` terms were not part of
# the data reduction and are therefore set to 0 by default.
#
# The `plot_meas_vs_calc` method of the project allows us to
# plot the measured and calculated diffraction patterns in the d-spacing axis
# by setting the `d_spacing` parameter to `True`.

# %%
project_1.plot_meas_vs_calc(expt_name='sim_si', d_spacing=True)

# %% [markdown]
# As you can see, the calculated diffraction pattern now matches the measured
# pattern much more closely. Typically, additional experimental parameters are included in
# the refinement process to further improve the fit. In this example, the structural
# parameters are not refined because the Si crystal structure is a well-known
# standard reference used to calibrate both the instrument and the experimental
# setup. The refined experimental parameters obtained here will then be applied
# when fitting the crystal structures of other materials.
#
# In the next part of the notebook, we will move to a more advanced case and
# fit a more complex crystal structure: La₀.₅Ba₀.₅CoO₃ (LBCO).
#
# %% [markdown]
# #### Save Project
#
# Before moving on, we can save the project to disk for later use. This will
# preserve the entire project structure, including experiments, sample models,
# and fitting results. The project is saved into a directory specified by the
# `dir_path` attribute of the project object.

# %%
project_1.save_as(dir_path='powder_diffraction_Si')

# %% [markdown]
# ## 💪 Exercise: Complex Fit – LBCO
#
# Now that you have a basic understanding of the fitting process, we will
# undertake a more complex fit of the La₀.₅Ba₀.₅CoO₃ (LBCO) crystal structure
# using simulated powder diffraction data from the data reduction notebook.
#
# You can use the same approach as in the previous part of the notebook, but
# this time we will refine a more complex crystal structure LBCO with multiple
# atoms in the unit cell.
#
# ### 📦 Exercise 1: Create a Project
#
# Create a new project for the LBCO fit.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# You can use the same approach as in the previous part of the
# notebook, but this time we will create a new project for the LBCO fit.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2 = ed.Project(name='main')
project_2.info.title = 'La0.5Ba0.5CoO3 Fit'
project_2.info.description = 'Fitting simulated powder diffraction pattern of La0.5Ba0.5CoO3.'

# %% [markdown]
# ### 🔬 Exercise 2: Define an Experiment
#
# #### Exercise 2.1: Create an Experiment
#
# Create an experiment within the new project and load the reduced diffraction
# pattern for LBCO.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# You can use the same approach as in the previous part of the
# notebook, but this time you need to use the data file for LBCO.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
dir_path = 'data'
file_name = 'reduced_LBCO.xye'
lbco_xye_path = f'{dir_path}/{file_name}'

# Uncomment the following line if your data reduction failed and the reduced data file is missing.
ed.download_from_repository(file_name, destination=dir_path)

project_2.experiments.add(
    name='sim_lbco',
    sample_form='powder',
    beam_mode='time-of-flight',
    radiation_probe='neutron',
    data_path=lbco_xye_path,
)

# %% [markdown]
# #### Exercise 2.1: Inspect Measured Data
#
# Check the measured data of the LBCO experiment. Are there any
# peaks with the shape similar to those excluded in the Si fit?
# If so, exclude them from this analysis as well.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# You can use the `plot_meas` method of the project to visualize the
# measured diffraction pattern. You can also use the `excluded_regions`
# attribute of the experiment to exclude specific regions from the analysis
# as we did in the previous part of the notebook.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.plotter.engine = 'plotly'
project_2.plot_meas(expt_name='sim_lbco')

project_2.experiments['sim_lbco'].excluded_regions.add(start=0, end=55000)
project_2.experiments['sim_lbco'].excluded_regions.add(start=105500, end=200000)

project_2.plot_meas(expt_name='sim_lbco')

# %% [markdown]
# #### Exercise 2.2: Set Instrument Parameters
#
# Set the instrument parameters for the LBCO experiment.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Use the values from the data reduction process for the LBCO and
# follow the same approach as in the previous part of the notebook.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.experiments['sim_lbco'].instrument.setup_twotheta_bank = ed.get_value_from_xye_header(lbco_xye_path, 'two_theta')
project_2.experiments['sim_lbco'].instrument.calib_d_to_tof_linear = ed.get_value_from_xye_header(lbco_xye_path, 'DIFC')

# %% [markdown]
# #### Exercise 2.3: Set Peak Profile Parameters
#
# Set the peak profile parameters for the LBCO experiment.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Use the values from the previous part of the notebook. You can
# either manually copy the values from the Si fit or use the `value` attribute
# of the parameters from the Si experiment to set the initial values for the
# LBCO experiment. This will help us to have a good starting point for the fit.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.peak_profile_type = 'pseudo-voigt * ikeda-carpenter'
project_2.experiments['sim_lbco'].peak.broad_gauss_sigma_0 = project_1.experiments['sim_si'].peak.broad_gauss_sigma_0.value
project_2.experiments['sim_lbco'].peak.broad_gauss_sigma_1 = project_1.experiments['sim_si'].peak.broad_gauss_sigma_1.value
project_2.experiments['sim_lbco'].peak.broad_gauss_sigma_2 = project_1.experiments['sim_si'].peak.broad_gauss_sigma_2.value
project_2.experiments['sim_lbco'].peak.broad_mix_beta_0 = project_1.experiments['sim_si'].peak.broad_mix_beta_0.value
project_2.experiments['sim_lbco'].peak.broad_mix_beta_1 = project_1.experiments['sim_si'].peak.broad_mix_beta_1.value
project_2.experiments['sim_lbco'].peak.asym_alpha_0 = project_1.experiments['sim_si'].peak.asym_alpha_0.value
project_2.experiments['sim_lbco'].peak.asym_alpha_1 = project_1.experiments['sim_si'].peak.asym_alpha_1.value

# %% [markdown]
# #### Exercise 2.4: Set Background
#
# Set the background points for the LBCO experiment. What would you suggest as
# the initial intensity value for the background points?

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Use the same approach as in the previous part of the notebook, but
# this time you need to set the background points for the LBCO experiment. You
# can zoom in on the measured diffraction pattern to determine the approximate
# background level.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.experiments['sim_lbco'].background_type = 'line-segment'
project_2.experiments['sim_lbco'].background.add(x=50000, y=0.2)
project_2.experiments['sim_lbco'].background.add(x=60000, y=0.2)
project_2.experiments['sim_lbco'].background.add(x=70000, y=0.2)
project_2.experiments['sim_lbco'].background.add(x=80000, y=0.2)
project_2.experiments['sim_lbco'].background.add(x=90000, y=0.2)
project_2.experiments['sim_lbco'].background.add(x=100000, y=0.2)
project_2.experiments['sim_lbco'].background.add(x=110000, y=0.2)

# %% [markdown]
# ### 🧩 Exercise 3: Define a Sample Model – LBCO
#
# The LBSO structure is not as simple as the Si model, as it contains multiple
# atoms in the unit cell. It is not in COD, so we give you the structural
# parameters in CIF format to create the sample model.
#
# Note that those parameters are not necessarily the most accurate ones, but
# they are a good starting point for the fit. The aim of the study is to refine
# the LBCO lattice parameters.

# %% [markdown]
# ```
# data_lbco
#
# _space_group.name_H-M_alt  "P m -3 m"
# _space_group.IT_coordinate_system_code  1
#
# _cell.length_a      3.89
# _cell.length_b      3.89
# _cell.length_c      3.89
# _cell.angle_alpha  90.0
# _cell.angle_beta   90.0
# _cell.angle_gamma  90.0
#
# loop_
# _atom_site.label
# _atom_site.type_symbol
# _atom_site.fract_x
# _atom_site.fract_y
# _atom_site.fract_z
# _atom_site.wyckoff_letter
# _atom_site.occupancy
# _atom_site.ADP_type
# _atom_site.B_iso_or_equiv
# La La   0.0 0.0 0.0   a   0.5   Biso 0.95
# Ba Ba   0.0 0.0 0.0   a   0.5   Biso 0.95
# Co Co   0.5 0.5 0.5   b   1.0   Biso 0.80
# O  O    0.0 0.5 0.5   c   1.0   Biso 1.66
# ```

# %% [markdown]
# Note that the `occupancy` of the La and Ba atoms is 0.5 and those atoms
# are located in the same position (0, 0, 0) in the unit cell. This means that
# an extra attribute `occupancy` needs to be set for those atoms later in the
# sample model.
#
# We model the La/Ba site using the virtual crystal approximation.
# In this approach, the scattering is taken as a weighted average of La and Ba.
# This reproduces the average diffraction pattern well but does not capture
# certain real-world effects.
#
# The edge cases are:
# - **Random distribution**.
#    La and Ba atoms are placed randomly. The Bragg peaks still match the
#    average structure, but the pattern also shows extra background
#    (diffuse scattering) between the peaks, but this is usually neglected
#    in the analysis.
# - **Perfect ordering**.
#    La and Ba arrange themselves in a regular pattern, creating a larger
#    repeating unit. This gives rise to extra peaks
#    ("superlattice reflections") and changes the intensity of some existing
#    peaks.
# - **Virtual crystal approximation (our model)**.
#    We replace the site with a single "virtual atom" that averages La and Ba.
#    This gives the correct average Bragg peaks but leaves out the extra
#    background of the random case and the extra peaks of the ordered case.

# %% [markdown]
# #### Exercise 3.1: Create Sample Model
#
# Add a sample model for LBCO to the project. The sample model parameters
# will be set in the next exercises.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# You can use the same approach as in the previous part of the
# notebook, but this time you need to use the model name corresponding to the
# LBCO structure, e.g. 'lbco'.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.sample_models.add(name='lbco')

# %% [markdown]
# #### Exercise 3.2: Set Space Group
#
# Set the space group for the LBCO sample model.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Use the space group name and IT coordinate system code from the CIF data.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.sample_models['lbco'].space_group.name_h_m = 'P m -3 m'
project_2.sample_models['lbco'].space_group.it_coordinate_system_code = '1'

# %% [markdown]
# #### Exercise 3.3: Set Lattice Parameters
#
# Set the lattice parameters for the LBCO sample model.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Use the lattice parameters from the CIF data.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.sample_models['lbco'].cell.length_a = 3.88

# %% [markdown]
# #### Exercise 3.4: Set Atom Sites
#
# Set the atom sites for the LBCO sample model.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Use the atom sites from the CIF data. You can use the `add` method of
# the `atom_sites` attribute of the sample model to add the atom sites.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.sample_models['lbco'].atom_sites.add(
    label='La',
    type_symbol='La',
    fract_x=0,
    fract_y=0,
    fract_z=0,
    wyckoff_letter='a',
    b_iso=0.95,
    occupancy=0.5,
)
project_2.sample_models['lbco'].atom_sites.add(
    label='Ba',
    type_symbol='Ba',
    fract_x=0,
    fract_y=0,
    fract_z=0,
    wyckoff_letter='a',
    b_iso=0.95,
    occupancy=0.5,
)
project_2.sample_models['lbco'].atom_sites.add(
    label='Co',
    type_symbol='Co',
    fract_x=0.5,
    fract_y=0.5,
    fract_z=0.5,
    wyckoff_letter='b',
    b_iso=0.80,
)
project_2.sample_models['lbco'].atom_sites.add(
    label='O',
    type_symbol='O',
    fract_x=0,
    fract_y=0.5,
    fract_z=0.5,
    wyckoff_letter='c',
    b_iso=1.66,
)

# %% [markdown]
# ### 🔗 Exercise 4: Assign Sample Model to Experiment
#
# Now assign the LBCO sample model to the experiment created above.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Use the `linked_phases` attribute of the experiment to link the sample model.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.experiments['sim_lbco'].linked_phases.add(id='lbco', scale=1.0)

# %% [markdown]
# ### 🚀 Exercise 5: Analyze and Fit the Data
#
# #### Exercise 5.1: Set Fit Parameters
#
# Select the initial set of parameters to be refined during the fitting
# process.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# You can start with the scale factor and the background
# points, as in the Si fit.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.experiments['sim_lbco'].linked_phases['lbco'].scale.free = True

for line_segment in project_2.experiments['sim_lbco'].background:
    line_segment.y.free = True

# %% [markdown]
# #### Exercise 5.2: Run Fitting
#
# Visualize the measured and calculated diffraction patterns before fitting and
# then run the fitting process.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Use the `plot_meas_vs_calc` method of the project to visualize the
# measured and calculated diffraction patterns before fitting. Then, use the
# `fit` method of the `analysis` object of the project to perform the fitting
# process.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.plot_meas_vs_calc(expt_name='sim_lbco')

project_2.analysis.fit()

# %% [markdown]
# #### Exercise 5.3: Find the Misfit in the Fit
#
# Visualize the measured and calculated diffraction patterns after the fit. As
# you can see, the fit shows noticeable discrepancies. If you zoom in on
# different regions of the pattern, you will observe that all the calculated
# peaks are shifted to the left.
#
# What could be the reason for the misfit?

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Consider the following options:
# 1. The conversion parameters from TOF to d-spacing are not correct.
# 2. The lattice parameters of the LBCO phase are not correct.
# 3. The peak profile parameters are not correct.
# 4. The background points are not correct.

# %% [markdown]
# **Solution:**

# %% [markdown] tags=["dmsc-school-hint"]
# 1. ❌ The conversion parameters from TOF to d-spacing were set based on the
# data reduction step. While they are specific to each dataset and thus differ
# from those used for the Si data, the full reduction workflow has already been
# validated with the Si fit. Therefore, they are not the cause of the misfit in
# this case.
# 2. ✅ The lattice parameters of the LBCO phase were set based on the CIF
# data, which is a good starting point, but they are not necessarily as
# accurate as needed for the fit. The lattice parameters may need to be
# refined.
# 3. ❌ The peak profile parameters do not change the position of the peaks,
# but rather their shape.
# 4. ❌ The background points affect the background level, but not the peak
# positions.

# %% tags=["solution", "hide-input"]
project_2.plot_meas_vs_calc(expt_name='sim_lbco')

# %% [markdown]
# #### Exercise 5.4: Refine the LBCO Lattice Parameter
#
# To improve the fit, refine the lattice parameters of the LBCO phase.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# To achieve this, we will set the `free` attribute of the `length_a`
# parameter of the LBCO cell to `True`.
#
# LBCO has a cubic crystal structure (space group `P m -3 m`), which means
# that `length_b` and `length_c` are constrained to be equal to `length_a`.
# Therefore, only `length_a` needs to be refined; the other two will be
# updated automatically. All cell angles are fixed at 90°, so they do not
# require refinement.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.sample_models['lbco'].cell.length_a.free = True

project_2.analysis.fit()

project_2.plot_meas_vs_calc(expt_name='sim_lbco')

# %% [markdown]
# One of the main goals of this study was to refine the lattice parameter of
# the LBCO phase. As shown in the updated fit results, the overall fit has
# improved significantly, even though the change in cell length is less than
# 1% of the initial value. This demonstrates how even a small adjustment to the
# lattice parameter can have a substantial impact on the quality of the fit.

# %% [markdown]
# #### Exercise 5.5: Visualize the Fit Results in d-spacing
#
# Plot measured vs calculated diffraction patterns in d-spacing instead of TOF.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Use the `plot_meas_vs_calc` method of the project and set the
# `d_spacing` parameter to `True`.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.plot_meas_vs_calc(expt_name='sim_lbco', d_spacing=True)

# %% [markdown]
# #### Exercise 5.6: Refine the Peak Profile Parameters
#
# As you can see, the fit is now relatively good and the peak positions are
# much closer to the measured data.
#
# The peak profile parameters were not refined, and their starting values were
# set based on the previous fit of the Si standard sample. Although these
# starting values are reasonable and provide a good starting point for the fit,
# they are not necessarily optimal for the LBCO phase. This can be seen while
# inspecting the individual peaks in the diffraction pattern. For example, the
# calculated curve does not perfectly describe the peak at about 1.38 Å, as can
# be seen below:

# %%
project_2.plot_meas_vs_calc(expt_name='sim_lbco', d_spacing=True, x_min=1.35, x_max=1.40)

# %% [markdown]
# The peak profile parameters are determined based on both the instrument
# and the sample characteristics, so they can vary when analyzing different
# samples on the same instrument. Therefore, it is better to refine them as
# well.
#
# Select the peak profile parameters to be refined during the fitting process.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# You can set the `free` attribute of the peak profile parameters to `True`
# to allow the fitting process to adjust them. You can use the same approach as
# in the previous part of the notebook, but this time you will refine the peak
# profile parameters of the LBCO phase.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.experiments['sim_lbco'].peak.broad_gauss_sigma_0.free = True
project_2.experiments['sim_lbco'].peak.broad_gauss_sigma_1.free = True
project_2.experiments['sim_lbco'].peak.broad_gauss_sigma_2.free = True
project_2.experiments['sim_lbco'].peak.broad_mix_beta_0.free = True
project_2.experiments['sim_lbco'].peak.broad_mix_beta_1.free = True
project_2.experiments['sim_lbco'].peak.asym_alpha_0.free = True
project_2.experiments['sim_lbco'].peak.asym_alpha_1.free = True

project_2.analysis.fit()

project_2.plot_meas_vs_calc(expt_name='sim_lbco', d_spacing=True, x_min=1.35, x_max=1.40)

# %% [markdown]
# #### Exercise 5.7: Find Undefined Features
#
# After refining the lattice parameter and the peak profile parameters, the fit
# is significantly improved, but inspect the diffraction pattern again. Are you
# noticing anything undefined?

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# While the fit is now significantly better, there are still some
# unexplained peaks in the diffraction pattern. These peaks are not accounted
# for by the LBCO phase. For example, if you zoom in on the region around
# 1.6 Å (or 95,000 μs), you will notice that the rightmost peak is not
# explained by the LBCO phase at all.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
project_2.plot_meas_vs_calc(expt_name='sim_lbco', x_min=1.53, x_max=1.7, d_spacing=True)

# %% [markdown]
# #### Exercise 5.8: Identify the Cause of the Unexplained Peaks
#
# Analyze the residual peaks that remain after refining the LBCO phase and the
# peak-profile parameters. Based on their positions and characteristics, decide
# which potential cause best explains the misfit.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Consider the following options:
# 1. The LBCO phase is not correctly modeled.
# 2. The LBCO phase is not the only phase present in the sample.
# 3. The data reduction process introduced artifacts.
# 4. The studied sample is not LBCO, but rather a different phase.

# %% [markdown]
# **Solution:**

# %% [markdown] tags=["dmsc-school-hint"]
# 1. ❌ In principle, this could be the case, as sometimes the presence of
# extra peaks in the diffraction pattern can indicate lower symmetry
# than the one used in the model, or that the model is not complete. However,
# in this case, the LBCO phase is correctly modeled based on the CIF data.
# 2. ✅ The unexplained peaks are due to the presence of an impurity phase
# in the sample, which is not included in the current model.
# 3. ❌ The data reduction process is not likely to introduce such specific
# peaks, as it is tested and verified in the previous part of the notebook.
# 4. ❌ This could also be the case in real experiments, but in this case,
# we know that the sample is LBCO, as it was simulated based on the CIF data.

# %% [markdown]
# #### Exercise 5.9: Identify the impurity phase
#
# Use the positions of the unexplained peaks to identify the most likely
# secondary phase present in the sample.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# Check the positions of the unexplained peaks in the diffraction pattern.
# Compare them with the known diffraction patterns in the previous part
# of the notebook.

# %% [markdown]
# **Solution:**

# %% [markdown] tags=["dmsc-school-hint"]
# The unexplained peaks are likely due to the presence of a small amount of
# Si in the LBCO sample. In real experiments, it might happen, e.g., because
# the sample holder was not cleaned properly after the Si experiment.
#
# You can visalize both the patterns of the Si and LBCO phases to confirm this
# hypothesis.

# %% tags=["solution", "hide-input"]
project_1.plot_meas_vs_calc(expt_name='sim_si', x_min=1, x_max=1.7, d_spacing=True)
project_2.plot_meas_vs_calc(expt_name='sim_lbco', x_min=1, x_max=1.7, d_spacing=True)

# %% [markdown]
# #### Exercise 5.10: Create a Second Sample Model – Si as Impurity
#
# Create a second sample model for the Si phase, which is the impurity phase
# identified in the previous step. Link this sample model to the LBCO
# experiment.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# You can use the same approach as in the previous part of the
# notebook, but this time you need to create a sample model for Si and link it
# to the LBCO experiment.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
# Set Space Group
project_2.sample_models.add(name='si')
project_2.sample_models['si'].space_group.name_h_m = 'F d -3 m'
project_2.sample_models['si'].space_group.it_coordinate_system_code = '2'

# Set Lattice Parameters
project_2.sample_models['si'].cell.length_a = 5.43

# Set Atom Sites
project_2.sample_models['si'].atom_sites.add(
    label='Si',
    type_symbol='Si',
    fract_x=0,
    fract_y=0,
    fract_z=0,
    wyckoff_letter='a',
    b_iso=0.89,
)

# Assign Sample Model to Experiment
project_2.experiments['sim_lbco'].linked_phases.add(id='si', scale=1.0)

# %% [markdown]
# #### Exercise 5.11: Refine the Scale of the Si Phase
#
# Visualize the measured diffraction pattern and the calculated diffraction
# pattern. Check if the Si phase is contributing to the calculated diffraction
# pattern. Refine the scale factor of the Si phase to improve the fit.

# %% [markdown]
# **Hint:**

# %% [markdown] tags=["dmsc-school-hint"]
# You can use the `plot_meas_vs_calc` method of the project to
# visualize the patterns. Then, set the `free` attribute of the `scale`
# parameter of the Si phase to `True` to allow the fitting process to adjust
# the scale factor.

# %% [markdown]
# **Solution:**

# %% tags=["solution", "hide-input"]
# Before optimizing the parameters, we can visualize the measured
# diffraction pattern and the calculated diffraction pattern based on the
# two phases: LBCO and Si.
project_2.plot_meas_vs_calc(expt_name='sim_lbco')

# As you can see, the calculated pattern is now the sum of both phases,
# and Si peaks are visible in the calculated pattern. However, their
# intensities are much too high. Therefore, we need to refine the scale factor
# of the Si phase.
project_2.experiments['sim_lbco'].linked_phases['si'].scale.free = True

# Now we can perform the fit with both phases included.
project_2.analysis.fit()

# Let's plot the measured diffraction pattern and the calculated diffraction
# pattern both for the full range and for a zoomed-in region around the
# previously unexplained peak near 95,000 μs. The calculated pattern will be
# the sum of the two phases.
project_2.plot_meas_vs_calc(expt_name='sim_lbco')
project_2.plot_meas_vs_calc(expt_name='sim_lbco', x_min=88000, x_max=101000)

# %% [markdown]
# All previously unexplained peaks are now accounted for in the pattern, and
# the fit is improved. Some discrepancies in the peak intensities remain, but
# further improvements would require more advanced data reduction and analysis,
# which are beyond the scope of this school.
#
# To review the analysis results, you can generate and print a summary
# report using the `show_report()` method, as demonstrated in the cell below.
# The report includes parameters related to the sample model and the
# experiment, such as the refined unit cell parameter `a` of LBCO.
#
# Information about the crystal or magnetic structure, along with experimental
# details, fitting quality, and other relevant data, is often submitted to
# crystallographic journals as part of a scientific publication.
# It can also be deposited in crystallographic databases when relevant.

# %%
project_2.summary.show_report()

# %% [markdown]
# Finally, we save the project to disk to preserve the current state of the analysis.

# %%
project_2.save_as(dir_path='powder_diffraction_LBCO_Si')

# %% [markdown]
# #### Final Remarks
#
# In this part of the notebook, you learned how to use EasyDiffraction
# to refine lattice parameters of a more complex crystal structure,
# La₀.₅Ba₀.₅CoO₃ (LBCO).
# In real experiments, you might also refine additional parameters,
# such as atomic positions, occupancies, and atomic displacement factors,
# to achieve an even better fit.
# For our purposes, we'll stop here, as the goal was to give you a
# starting point for analyzing more complex crystal structures
# with EasyDiffraction.

# %% [markdown]
# ## 🎁 Bonus
#
# Congratulations — you've now completed the diffraction data analysis part of
# the DMSC Summer School!
#
# If you'd like to keep exploring, the EasyDiffraction library offers many
# additional tutorials and examples on the official documentation site:
# 👉 https://docs.easydiffraction.org/lib/tutorials/
#
# Besides the Python package, EasyDiffraction also comes with a graphical
# user interface (GUI) that lets you perform similar analyses without writing
# code. To be fair, it's not *quite* feature-complete compared to the Python
# library yet — but we're working on it! 🚧
#
# If you prefer a point-and-click interface over coding, the GUI provides a
# user-friendly way to analyze diffraction data. You can download it as a
# standalone application here:
# 👉 https://easydiffraction.org
#
# We'd love to hear your feedback on EasyDiffraction — both the library and
# the GUI! 💬
