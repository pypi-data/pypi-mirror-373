---
icon: material/archive
---

# :material-archive: Project

The **Project** serves as a container for all data and metadata associated with
a particular data analysis task. It acts as the top-level entity in
EasyDiffraction, ensuring structured organization and easy access to relevant
information. Each project can contain multiple **experimental datasets**, with
each dataset containing contribution from multiple **sample models**.

EasyDiffraction allows you to:

- **Manually create** a new project by specifying its metadata.
- **Load an existing project** from a file (**CIF** format).

Below are instructions on how to set up a project in EasyDiffraction. It is
assumed that you have already imported the `easydiffraction` package, as
described in the [First Steps](../first-steps.md) section.

## Creating a Project Manually

You can manually create a new project and specify its short **name**, **title**
and **description**. All these parameters are optional.

```py
# Create a new project
project = ed.Project(name='lbco_hrpt')

# Define project info
project.info.title = 'La0.5Ba0.5CoO3 from neutron diffraction at HRPT@PSI'
project.info.description = '''This project demonstrates a standard refinement
of La0.5Ba0.5CoO3, which crystallizes in a perovskite-type structure, using
neutron powder diffraction data collected in constant wavelength mode at the
HRPT diffractometer (PSI).'''
```

## Saving a Project

Saving the initial project requires specifying the directory path:

```python
project.save_as(dir_path='lbco_hrpt')
```

If working in the interactive mode in a Jupyter notebook or similar environment,
you can also save the project after every significant change. This is useful for
keeping track of changes and ensuring that your work is not lost. If you already
saved the project with `save_as`, you can just call the `save`:

```python
project.save()
```

## Loading a Project from CIF

If you have an existing project, you can load it directly from a CIF file. This
is useful for reusing previously defined projects or sharing them with others.

```python
project.load('data/lbco_hrpt.cif')
```

## Project Structure

The example below illustrates a typical **project structure** for a
**constant-wavelength powder neutron diffraction** experiment:

<!-- prettier-ignore-start -->

<div class="cif">
<pre>
📁 <span class="red"><b>La0.5Ba0.5CoO3</b></span>     - Project directory.
├── 📄 <span class="orange"><b>project.cif</b></span>    - Main project description file.
├── 📁 sample_models  - Folder with sample models (crystallographic structures).
│   ├── 📄 <span class="orange"><b>lbco.cif</b></span>   - File with La0.5Ba0.5CoO3 structure parameters.
│   └── ...
├── 📁 experiments    - Folder with instrumental parameters and measured data.
│   ├── 📄 <span class="orange"><b>hrpt.cif</b></span>   - Instrumental parameters and measured data from HRPT@PSI.
│   └── ...
├── 📄 <span class="orange"><b>analysis.cif</b></span>   - Settings for data analysis (calculator, minimizer, etc.).
└── 📁 summary
    └── 📄 report.cif - Summary report after structure refinement.
</pre>
</div>

<!-- prettier-ignore-end -->

## Project Files

Below is a complete project example stored in the `La0.5Ba0.5CoO3` directory,
showing the contents of all files in the project.

!!! warning "Important"

    If you save the project right after creating it, the project directory will
    only contain the `project.cif` file. The other folders and files will be
    created as you add sample models, experiments, and set up the analysis. The
    summary folder will be created after the analysis is completed.

### 1. <span class="orange">project.cif</span>

This file provides an overview of the project, including file names of the
**sample models** and **experiments** associated with the project.

<!-- prettier-ignore-start -->

<div class="cif">
<pre>
data_<span class="red"><b>La0.5Ba0.5CoO3</b></span>

<span class="blue"><b>_project</b>.title</span>       "La0.5Ba0.5CoO3 from neutron diffraction at HRPT@PSI"
<span class="blue"><b>_project</b>.description</span> "neutrons, powder, constant wavelength, HRPT@PSI"

loop_
<span class="green"><b>_sample_model</b>.cif_file_name</span>
lbco.cif

loop_
<span class="green"><b>_experiment</b>.cif_file_name</span>
hrpt.cif
</pre>
</div>

<!-- prettier-ignore-end -->

### 2. sample_models / <span class="orange">lbco.cif</span>

This file contains crystallographic information associated with the sample
model, including **space group**, **unit cell parameters**, and **atomic
positions**.

<!-- prettier-ignore-start -->

<div class="cif">
<pre>
data_<span class="red"><b>lbco</b></span>

<span class="blue"><b>_space_group</b>.name_H-M_alt</span>              "P m -3 m"
<span class="blue"><b>_space_group</b>.IT_coordinate_system_code</span> 1

<span class="blue"><b>_cell</b>.length_a</span>      3.8909(1)
<span class="blue"><b>_cell</b>.length_b</span>      3.8909
<span class="blue"><b>_cell</b>.length_c</span>      3.8909
<span class="blue"><b>_cell</b>.angle_alpha</span>  90
<span class="blue"><b>_cell</b>.angle_beta</span>   90
<span class="blue"><b>_cell</b>.angle_gamma</span>  90

loop_
<span class="green"><b>_atom_site</b>.label</span>
<span class="green"><b>_atom_site</b>.type_symbol</span>
<span class="green"><b>_atom_site</b>.fract_x</span>
<span class="green"><b>_atom_site</b>.fract_y</span>
<span class="green"><b>_atom_site</b>.fract_z</span>
<span class="green"><b>_atom_site</b>.Wyckoff_letter</span>
<span class="green"><b>_atom_site</b>.occupancy</span>
<span class="green"><b>_atom_site</b>.adp_type</span>
<span class="green"><b>_atom_site</b>.B_iso_or_equiv</span>
La La   0   0   0     a   0.5  Biso 0.4958
Ba Ba   0   0   0     a   0.5  Biso 0.4943
Co Co   0.5 0.5 0.5   b   1    Biso 0.2567
O  O    0   0.5 0.5   c   1    Biso 1.4041
</pre>
</div>

<!-- prettier-ignore-end -->

### 3. experiments / <span class="orange">hrpt.cif</span>

This file contains the **experiment type**, **instrumental parameters**, **peak
parameters**, **associated phases**, **background parameters** and **measured
diffraction data**.

<!-- prettier-ignore-start -->

<div class="cif">
<pre>
data_<span class="red"><b>hrpt</b></span>

<span class="blue"><b>_expt_type</b>.beam_mode</span>        "constant wavelength"
<span class="blue"><b>_expt_type</b>.radiation_probe</span>  neutron
<span class="blue"><b>_expt_type</b>.sample_form</span>      powder
<span class="blue"><b>_expt_type</b>.scattering_type</span>  bragg

<span class="blue"><b>_instr</b>.wavelength</span>    1.494
<span class="blue"><b>_instr</b>.2theta_offset</span> 0.6225(4)

<span class="blue"><b>_peak</b>.broad_gauss_u</span>    0.0834
<span class="blue"><b>_peak</b>.broad_gauss_v</span>   -0.1168
<span class="blue"><b>_peak</b>.broad_gauss_w</span>    0.123
<span class="blue"><b>_peak</b>.broad_lorentz_x</span>  0
<span class="blue"><b>_peak</b>.broad_lorentz_y</span>  0.0797

loop_
<span class="green"><b>_pd_phase_block</b>.id</span>
<span class="green"><b>_pd_phase_block</b>.scale</span>
lbco 9.0976(3)

loop_
<span class="green"><b>_pd_background</b>.line_segment_X</span>
<span class="green"><b>_pd_background</b>.line_segment_intensity</span>
<span class="green"><b>_pd_background</b>.X_coordinate</span>
 10  174.3  2theta
 20  159.8  2theta
 30  167.9  2theta
 50  166.1  2theta
 70  172.3  2theta
 90  171.1  2theta
110  172.4  2theta
130  182.5  2theta
150  173.0  2theta
165  171.1  2theta

loop_
<span class="green"><b>_pd_meas</b>.2theta_scan</span>
<span class="green"><b>_pd_meas</b>.intensity_total</span>
<span class="green"><b>_pd_meas</b>.intensity_total_su</span>
 10.00  167  12.6
 10.05  157  12.5
 10.10  187  13.3
 10.15  197  14.0
 10.20  164  12.5
 10.25  171  13.0
...
164.60  153  20.7
164.65  173  30.1
164.70  187  27.9
164.75  175  38.2
164.80  168  30.9
164.85  109  41.2
</pre>
</div>

<!-- prettier-ignore-end -->

### 4. <span class="orange">analysis.cif</span>

This file contains settings used for data analysis, including the choice of
**calculation** and **fitting** engines, as well as user defined
**constraints**.

<!-- prettier-ignore-start -->

<div class="cif">
<pre>
<span class="blue"><b>_analysis</b>.calculator_engine</span>  cryspy
<span class="blue"><b>_analysis</b>.fitting_engine</span>     "lmfit (leastsq)"
<span class="blue"><b>_analysis</b>.fit_mode</span>           single

loop_
<span class="green"><b>_alias</b>.label</span>
<span class="green"><b>_alias</b>.param_uid</span>
biso_La  lbco.atom_site.La.B_iso_or_equiv
biso_Ba  lbco.atom_site.Ba.B_iso_or_equiv
occ_La   lbco.atom_site.La.occupancy
occ_Ba   lbco.atom_site.Ba.occupancy

loop_
<span class="green"><b>_constraint</b>.lhs_alias</span>
<span class="green"><b>_constraint</b>.rhs_expr</span>
biso_Ba  biso_La
occ_Ba   "1 - occ_La"
</pre>
</div>

<!-- prettier-ignore-end -->

<br>

---

Now that the Project has been defined, you can proceed to the next step:
[Sample Model](model.md).
