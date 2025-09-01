# Data Format

Before starting the data analysis workflow, it is important to define the **data
formats** used in EasyDiffraction.

## Crystallographic Information File

Each software package typically uses its own **data format** and **parameter
names** for storing and sharing data. In EasyDiffraction, we use the
**Crystallographic Information File (CIF)** format, which is widely used in
crystallography and materials science. It provides both a human-readable syntax
and a set of dictionaries that define the meaning of each parameter.

These dictionaries are maintained by the
[International Union of Crystallography (IUCr)](https://www.iucr.org).  
The base dictionary, **coreCIF**, contains the most common parameters in
crystallography. The **pdCIF** dictionary covers parameters specific to powder
diffraction, **magCIF** is used for magnetic structure analysis.

As most parameters needed for diffraction data analysis are already covered by
IUCr dictionaries, EasyDiffraction uses the strict **CIF format** and follows
these dictionaries as closely as possible — for both input and output —
throughout the workflow described in the
[Analysis Workflow](analysis-workflow/index.md) section.

The key advantage of CIF is the standardized naming of parameters and
categories, which promotes interoperability and familiarity among researchers.

If a required parameter is not defined in the standard dictionaries,
EasyDiffraction introduces **custom CIF keywords**, documented in the
[Parameters](parameters.md) section under the **CIF name for serialization**
columns.

## Format Comparison

Below, we compare **CIF** with another common data format in programming:
**JSON**.

### Scientific Journals

Let's assume the following structural data for La₀.₅Ba₀.₅CoO₃ (LBCO), as
reported in a scientific publication. These parameters are to be refined during
diffraction data analysis:

Table 1. Crystallographic data. Space group: _Pm3̅m_.

| Parameter | Value  |
| --------- | ------ |
| a         | 3.8909 |
| b         | 3.8909 |
| c         | 3.8909 |
| alpha     | 90.0   |
| beta      | 90.0   |
| gamma     | 90.0   |

Table 2. Atomic coordinates (_x_, _y_, _z_), occupancies (occ) and isotropic
displacement parameters (_Biso_)

| Label | Type | x   | y   | z   | occ | Biso   |
| ----- | ---- | --- | --- | --- | --- | ------ |
| La    | La   | 0   | 0   | 0   | 0.5 | 0.4958 |
| Ba    | Ba   | 0   | 0   | 0   | 0.5 | 0.4958 |
| Co    | Co   | 0.5 | 0.5 | 0.5 | 1.0 | 0.2567 |
| O     | O    | 0   | 0.5 | 0.5 | 1.0 | 1.4041 |

### CIF

The data above would be represented in CIF as follows:

<!-- prettier-ignore-start -->

<div class="cif">
<pre>
data_<span class="red"><b>lbco</b></span>

<span class="blue"><b>_space_group</b>.name_H-M_alt</span>              "P m -3 m"
<span class="blue"><b>_space_group</b>.IT_coordinate_system_code</span> 1

<span class="blue"><b>_cell</b>.length_a</span>      3.8909
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
Ba Ba   0   0   0     a   0.5  Biso 0.4958
Co Co   0.5 0.5 0.5   b   1    Biso 0.2567
O  O    0   0.5 0.5   c   1    Biso 1.4041
</pre>
</div>

<!-- prettier-ignore-end -->

Here, unit cell parameters are grouped under the `_cell` category, and atomic
positions under the `_atom_site` category. The `loop_` keyword indicates that
multiple rows follow for the listed parameters. Each atom is identified using
`_atom_site.label`.

### JSON

Representing the same data in **JSON** results in a format that is more verbose
and less human-readable, especially for large datasets. JSON is ideal for
structured data in programming environments, whereas CIF is better suited for
human-readable crystallographic data.

```json
{
  "lbco": {
    "space_group": {
      "name_H-M_alt": "P m -3 m",
      "IT_coordinate_system_code": 1
    },
    "cell": {
      "length_a": 3.8909,
      "length_b": 3.8909,
      "length_c": 3.8909,
      "angle_alpha": 90,
      "angle_beta": 90,
      "angle_gamma": 90
    },
    "atom_site": [
      {
        "label": "La",
        "type_symbol": "La",
        "fract_x": 0,
        "fract_y": 0,
        "fract_z": 0,
        "occupancy": 0.5,
        "B_iso_or_equiv": 0.4958
      },
      {
        "label": "Ba",
        "type_symbol": "Ba",
        "fract_x": 0,
        "fract_y": 0,
        "fract_z": 0,
        "occupancy": 0.5,
        "B_iso_or_equiv": 0.4943
      },
      {
        "label": "Co",
        "type_symbol": "Co",
        "fract_x": 0.5,
        "fract_y": 0.5,
        "fract_z": 0.5,
        "occupancy": 1.0,
        "B_iso_or_equiv": 0.2567
      },
      {
        "label": "O",
        "type_symbol": "O",
        "fract_x": 0,
        "fract_y": 0.5,
        "fract_z": 0.5,
        "occupancy": 1.0,
        "B_iso_or_equiv": 1.4041
      }
    ]
  }
}
```

## Experiment Definition

The previous example described the **sample model** (crystallographic model),
but how is the **experiment** itself represented?

The experiment is also saved as a CIF file. For example, background intensity in
a powder diffraction experiment might be represented as:

<!-- prettier-ignore-start -->

<div class="cif">
<pre>
loop_
<span class="green"><b>_pd_background</b>.line_segment_X</span>
<span class="green"><b>_pd_background</b>.line_segment_intensity</span>
<span class="green"><b>_pd_background</b>.X_coordinate</span>

 10.0  174.3  2theta
 20.0  159.8  2theta
 30.0  167.9  2theta
 ...
</pre>
</div>

<!-- prettier-ignore-end -->

More details on how to define the experiment in CIF format are provided in the
[Experiment](analysis-workflow/experiment.md) section.

## Other Input/Output Blocks

EasyDiffraction uses CIF consistently throughout its workflow, including in the
following blocks:

- **project**: contains the project information
- **sample model**: defines the sample model
- **experiment**: contains the experiment setup and measured data
- **analysis**: stores fitting and analysis parameters
- **summary**: captures analysis results

Example CIF files for each block are provided in the
[Analysis Workflow](analysis-workflow/index.md) and
[Tutorials](../tutorials/index.md).

## Other Data Formats

While CIF is the primary format in EasyDiffraction, we also support other
formats for importing measured data. These include plain text files with
multiple columns. The meaning of the columns depends on the experiment type.

For example, in a standard constant-wavelength powder diffraction experiment:

- Column 1: 2θ angle
- Column 2: intensity
- Column 3: standard uncertainty of the intensity

More details on supported input formats are provided in the
[Experiment](analysis-workflow/experiment.md) section.
