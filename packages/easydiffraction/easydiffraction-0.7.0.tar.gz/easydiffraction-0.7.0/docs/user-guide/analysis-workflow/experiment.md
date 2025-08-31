---
icon: material/microscope
---

# :material-microscope: Experiment

The **Experiment** in EasyDiffraction includes both the measured diffraction
data and all the other relevant parameters that describe the experimental setup
and related conditions. This can include information about the instrumental
resolution, peak shape, background, etc.

EasyDiffraction allows you to:

- **Load an existing experiment** from a file (**CIF** format). Both the
  metadata and measured data are expected to be in CIF format.
- **Manually define** a new experiment by specifying its type, other necessary
  experimental parameters, as well as load measured data. This is useful when
  you want to create an experiment from scratch or when you have a measured data
  file in a non-CIF format (e.g., `.xye`, `.xy`).

Below, you will find instructions on how to define and manage experiments in
EasyDiffraction. It is assumed that you have already created a `project` object,
as described in the [Project](project.md) section as well as defined its
`sample_models`, as described in the [Sample Model](model.md) section.

### Adding an Experiment from CIF

This is the most straightforward way to define an experiment in EasyDiffraction.
If you have a crystallographic information file (CIF) for your experiment, that
contains both the necessary information (metadata) about the experiment as well
as the measured data, you can add it to your project using the
`add_experiment_from_cif` method of the `project` instance. In this case, the
name of the experiment will be taken from CIF.

```python
# Load an experiment from a CIF file
project.add_experiment_from_cif('data/hrpt_300K.cif')
```

Accessing the experiment after loading it will be done through the `experiments`
object of the `project` instance. The name of the model will be the same as the
data block id in the CIF file. For example, if the CIF file contains a data
block with the id `hrpt`,

<!-- prettier-ignore-start -->

<div class="cif">
<pre>
data_<span class="red"><b>hrpt</b></span>

<span class="blue"><b>_expt_type</b>.beam_mode</span>  "constant wavelength"
...
</pre>
</div>

<!-- prettier-ignore-end -->

you can access it in the code as follows:

```python
# Access the experient by its name
project.experiments['hrpt']
```

## Defining an Experiment Manually

If you do not have a CIF file or prefer to define the experiment manually, you
can use the `add` method of the `experiments` object of the `project` instance.
In this case, you will need to specify the name of the experiment, which will be
used to reference it later. Along with the name, you need to provide the
following parameters, essential for defining the experiment, which define the
**type of experiment**:

- **sample_form**: The form of the sample (powder, single crystal).
- **beam_mode**: The mode of the beam (constant wavelength, time-of-flight).
- **radiation_probe**: The type of radiation used (neutron, X-ray).
- **scattering_type**: The type of scattering (bragg, total).

!!! warning "Important"

    It is important to mention that once an experiment is added, you cannot change
    these parameters. If you need to change them, you must create a new experiment
    or redefine the existing one.

If you have a measured data file, you can also specify:

- **data_path**: The path to the measured data file (e.g., `.xye`, `.xy`).
  Supported formats are described in the
  [Measured Data Category](#5-measured-data-category) section.

Here is an example of how to add an experiment with all components needed to
define the experiment explicitly set:

```python
# Add an experiment with default parameters, based on the specified type.
# The experiment name is used to reference it later.
project.experiments.add(name='hrpt',
                        sample_form='powder',
                        beam_mode='constant wavelength',
                        radiation_probe='neutron',
                        scattering_type='bragg',
                        data_path='data/hrpt_lbco.xye')
```

To add an experiment of default type, you can simply do:

```python
# Add an experiment of default type
# The experiment name is used to reference it later.
project.experiments.add(name='hrpt',
                        data_path='data/hrpt_lbco.xye')
```

You can now change the default parameters of the experiment, categorized into
the groups based on the type of experiment.

The `add` method creates a new experiment of the specified type with default
parameters. You can then modify its parameters to match your specific
experimental setup. All parameters are grouped into the following categories,
which makes it easier to manage the experiment:

1. **Instrument Category**: Defines the instrument configuration, including
   wavelength, two-theta offset, and resolution parameters.
2. **Peak Category**: Specifies the peak profile type and its parameters, such
   as broadening and asymmetry.
3. **Background Category**: Defines the background type and allows you to add
   background points.
4. **Linked Phases Category**: Links the sample model defined in the previous
   step to the experiment, allowing you to specify the scale factor for the
   linked phase.
5. **Measured Data Category**: Contains the measured data. The expected format
   depends on the experiment type, but generally includes columns for 2θ angle
   or TOF and intensity.

### 1. Instrument Category { #instrument-category }

```python
# Modify the default instrument parameters
project.experiments['hrpt'].instrument.setup_wavelength = 1.494
project.experiments['hrpt'].instrument.calib_twotheta_offset = 0.6
```

### 2. Excluded Regions Category { #excluded-regions-category }

```python
# Add excluded regions to the experiment
project.experiments['hrpt'].excluded_regions.add(start=0, end=10)
project.experiments['hrpt'].excluded_regions.add(start=160, end=180)
```

### 3. Peak Category { #peak-category }

```python
# Select the desired peak profile type
project.experiments['hrpt'].peak_profile_type = 'pseudo-voigt'

# Modify default peak profile parameters
project.experiments['hrpt'].peak.broad_gauss_u = 0.1
project.experiments['hrpt'].peak.broad_gauss_v = -0.1
project.experiments['hrpt'].peak.broad_gauss_w = 0.1
project.experiments['hrpt'].peak.broad_lorentz_x = 0
project.experiments['hrpt'].peak.broad_lorentz_y = 0.1
```

### 4. Background Category { #background-category }

```python
# Select the desired background type
project.experiments['hrpt'].background_type = 'line-segment'

# Add background points
project.experiments['hrpt'].background.add(x=10, y=170)
project.experiments['hrpt'].background.add(x=30, y=170)
project.experiments['hrpt'].background.add(x=50, y=170)
project.experiments['hrpt'].background.add(x=110, y=170)
project.experiments['hrpt'].background.add(x=165, y=170)
```

### 5. Linked Phases Category { #linked-phases-category }

```python
# Link the sample model defined in the previous step to the experiment
project.experiments['hrpt'].linked_phases.add(id='lbco', scale=10.0)
```

### 6. Measured Data Category { #measured-data-category }

If you do not have a CIF file for your experiment, you can load measured data
from a file in a supported format. The measured data will be automatically
converted into CIF format and added to the experiment. The expected format
depends on the experiment type.

#### Supported data file formats:

- `.xye` or `.xys` (3 columns, including standard deviations)
  - [\_pd_meas.2theta_scan](../parameters/pd_meas.md)
  - [\_pd_meas.intensity_total](../parameters/pd_meas.md)
  - [\_pd_meas.intensity_total_su](../parameters/pd_meas.md)
- `.xy` (2 columns, no standard deviations):
  - [\_pd_meas.2theta_scan](../parameters/pd_meas.md)
  - [\_pd_meas.intensity_total](../parameters/pd_meas.md)

If no **standard deviations** are provided, they are automatically calculated as
the **square root** of measured intensities.

Optional comments with `#` are possible in data file headers.

Here are some examples:

#### example1.xye

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
<span class="grey"># 2theta  intensity    su</span>
   10.00     167      12.6
   10.05     157      12.5
   10.10     187      13.3
   10.15     197      14.0
   10.20     164      12.5
  ...
  164.65     173      30.1
  164.70     187      27.9
  164.75     175      38.2
  164.80     168      30.9
  164.85     109      41.2
</pre>
</div>
<!-- prettier-ignore-end -->

#### example2.xy

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
<span class="grey"># 2theta  intensity</span>
   10.00     167    
   10.05     157    
   10.10     187    
   10.15     197    
   10.20     164    
  ...
  164.65     173    
  164.70     187    
  164.75     175    
  164.80     168    
  164.85     109  
</pre>
</div>
<!-- prettier-ignore-end -->

#### example3.xy

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
10  167.3    
10.05  157.4    
10.1  187.1    
10.15  197.8    
10.2  164.9    
...
164.65  173.3    
164.7  187.5    
164.75  175.8    
164.8  168.1    
164.85  109     
</pre>
</div>
<!-- prettier-ignore-end -->

## Listing Defined Experiments

To check which experiments have been added to the `project`, use:

```python
# Show defined experiments
project.experiments.show_names()
```

Expected output:

```
Defined experiments 🔬
['hrpt']
```

## Viewing an Experiment as CIF

To inspect an experiment in CIF format, use:

```python
# Show experiment as CIF
project.experiments['hrpt'].show_as_cif()
```

Example output:

```
Experiment 🔬 'hrpt' as cif
╒═════════════════════════════════════════════╕
│ data_hrpt                                   │
│                                             │
│ _expt_type.beam_mode  "constant wavelength" │
│ _expt_type.radiation_probe  neutron         │
│ _expt_type.sample_form  powder              │
│ _expt_type.scattering_type  bragg           │
│                                             │
│ _instr.2theta_offset  0.6                   │
│ _instr.wavelength  1.494                    │
│                                             │
│ _peak.broad_gauss_u  0.1                    │
│ _peak.broad_gauss_v  -0.1                   │
│ _peak.broad_gauss_w  0.1                    │
│ _peak.broad_lorentz_x  0                    │
│ _peak.broad_lorentz_y  0.1                  │
│                                             │
│ loop_                                       │
│ _pd_phase_block.id                          │
│ _pd_phase_block.scale                       │
│ lbco 10.0                                   │
│                                             │
│ loop_                                       │
│ _pd_background.line_segment_X               │
│ _pd_background.line_segment_intensity       │
│ 10 170                                      │
│ 30 170                                      │
│ 50 170                                      │
│ 110 170                                     │
│ 165 170                                     │
│                                             │
│ loop_                                       │
│ _pd_meas.2theta_scan                        │
│ _pd_meas.intensity_total                    │
│ _pd_meas.intensity_total_su                 │
│ 10.0 167.0 12.6                             │
│ 10.05 157.0 12.5                            │
│ 10.1 187.0 13.3                             │
│ 10.15 197.0 14.0                            │
│ 10.2 164.0 12.5                             │
│ ...                                         │
│ 164.65 173.0 30.1                           │
│ 164.7 187.0 27.9                            │
│ 164.75 175.0 38.2                           │
│ 164.8 168.0 30.9                            │
│ 164.85 109.0 41.2                           │
╘═════════════════════════════════════════════╛
```

## Saving an Experiment

Saving the project, as described in the [Project](project.md) section, 
will also save the experiment. Each experiment is saved as a separate
CIF file in the `experiments` subdirectory of the project directory. The project file contains 
references to these files.

EasyDiffraction supports different types of experiments, and each experiment is saved in a 
dedicated CIF file with 
experiment-specific parameters. 

Below are examples of how different experiments are saved in CIF format.

### [pd-neut-cwl][3]{:.label-experiment}

This example represents a constant-wavelength neutron powder diffraction
experiment:

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

### [pd-neut-tof][3]{:.label-experiment}

This example demonstrates a time-of-flight neutron powder diffraction
experiment:

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
data_<span class="red"><b>wish</b></span>

<span class="blue"><b>_diffrn_radiation</b>.probe</span> neutron

<span class="blue"><b>_pd_instr</b>.2theta_bank</span> 152.827

<span class="blue"><b>_pd_instr</b>.dtt1</span> 20773.1(3)
<span class="blue"><b>_pd_instr</b>.dtt2</span>    -1.08308
<span class="blue"><b>_pd_instr</b>.zero</span>   -13.7(5)

<span class="blue"><b>_pd_instr</b>.alpha0</span> -0.009(1)
<span class="blue"><b>_pd_instr</b>.alpha1</span>  0.109(2)
<span class="blue"><b>_pd_instr</b>.beta0</span>   0.00670(3)
<span class="blue"><b>_pd_instr</b>.beta1</span>   0.0100(3)
<span class="blue"><b>_pd_instr</b>.sigma0</span>  0
<span class="blue"><b>_pd_instr</b>.sigma1</span>  0
<span class="blue"><b>_pd_instr</b>.sigma2</span> 15.7(8)

loop_
<span class="green"><b>_pd_phase_block</b>.id</span>
<span class="green"><b>_pd_phase_block</b>.scale</span>
ncaf 1.093(5)

loop_
<span class="green"><b>_pd_background</b>.line_segment_X</span>
<span class="green"><b>_pd_background</b>.line_segment_intensity</span>
<span class="green"><b>_pd_background</b>.X_coordinate</span>
  9162.3  465(38) time-of-flight
 11136.8  593(30) time-of-flight
 14906.5  546(18) time-of-flight
 17352.2  496(14) time-of-flight
 20179.5  452(10) time-of-flight
 22176.0  468(12) time-of-flight
 24644.7  380(6)  time-of-flight
 28257.2  378(4)  time-of-flight
 34034.4  328(4)  time-of-flight
 41214.6  323(3)  time-of-flight
 49830.9  273(3)  time-of-flight
 58204.9  260(4)  time-of-flight
 70186.9  262(5)  time-of-flight
 82103.2  268(5)  time-of-flight
102712.0  262(15) time-of-flight

loop_
<span class="green"><b>_pd_meas</b>.time_of_flight</span>
<span class="green"><b>_pd_meas</b>.intensity_total</span>
<span class="green"><b>_pd_meas</b>.intensity_total_su</span>
  9001.0  616.523  124.564
  9006.8  578.769  123.141
  9012.6  574.184  120.507
  9018.5  507.739  111.300
  9024.3  404.672  101.616
  9030.1  469.244  107.991
...
103085.0  275.072   60.978
103151.4  214.187   55.675
103217.9  256.211   62.825
103284.4  323.872   73.082
103351.0  242.382   65.736
103417.6  277.666   73.837
</pre>
</div>
<!-- prettier-ignore-end -->

### [sc-neut-cwl][3]{:.label-experiment}

This example represents a single-crystal neutron diffraction experiment:

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
data_<span class="red"><b>heidi</b></span>

<span class="blue"><b>_diffrn_radiation</b>.probe</span>                 neutron
<span class="blue"><b>_diffrn_radiation_wavelength</b>.wavelength</span> 0.793

<span class="blue"><b>_pd_calib</b>.2theta_offset</span> 0.6225(4)

<span class="blue"><b>_pd_instr</b>.resolution_u</span>  0.0834
<span class="blue"><b>_pd_instr</b>.resolution_v</span> -0.1168
<span class="blue"><b>_pd_instr</b>.resolution_w</span>  0.123
<span class="blue"><b>_pd_instr</b>.resolution_x</span>  0
<span class="blue"><b>_pd_instr</b>.resolution_y</span>  0.0797

<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p1</span> 0
<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p2</span> 0
<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p3</span> 0
<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p4</span> 0

loop_
<span class="green"><b>_exptl_crystal</b>.id</span>
<span class="green"><b>_exptl_crystal</b>.scale</span>
tbti 2.92(6)

loop_
<span class="green"><b>_refln</b>.index_h</span>
<span class="green"><b>_refln</b>.index_k</span>
<span class="green"><b>_refln</b>.index_l</span>
<span class="green"><b>_refln</b>.intensity_meas</span>
<span class="green"><b>_refln</b>.intensity_meas_su</span>
 1  1  1   194.5677    2.3253
 2  2  0    22.6319    1.1233
 3  1  1    99.2917    2.5620
 2  2  2   219.2877    3.2522
...
16  8  8    29.3063   12.6552
17  7  7  1601.5154  628.8915
13 13  7  1176.0896  414.6018
19  5  1     0.8334   20.4207
15  9  9    10.9864    8.0650
12 12 10    14.4074   11.3800
</pre>
</div>
<!-- prettier-ignore-end -->

<!-- prettier-ignore-start -->
[3]: ../glossary.md#experiment-type-labels
<!-- prettier-ignore-end -->

<br>

---

Now that the experiment has been defined, you can proceed to the next step:
[Analysis](analysis.md).
