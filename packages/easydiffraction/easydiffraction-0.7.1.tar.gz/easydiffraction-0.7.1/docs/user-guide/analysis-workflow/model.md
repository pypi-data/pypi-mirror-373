---
icon: material/puzzle
---

# :material-puzzle: Sample Model

The **Sample Model** in EasyDiffraction represents the **crystallographic
structure** used to calculate the diffraction pattern, which is then fitted to
the **experimentally measured data** to refine the structural parameters.

EasyDiffraction allows you to:

- **Load an existing model** from a file (**CIF** format).
- **Manually define** a new sample model by specifying crystallographic
  parameters.

Below, you will find instructions on how to define and manage crystallographic
models in EasyDiffraction. It is assumed that you have already created a
`project` object, as described in the [Project](project.md) section.

## Adding a Model from CIF

This is the most straightforward way to define a sample model in
EasyDiffraction. If you have a crystallographic information file (CIF) for your
sample model, you can add it to your project using the `add_phase_from_file`
method of the `project` instance. In this case, the name of the model will be
taken from CIF.

```python
# Load a phase from a CIF file
project.add_phase_from_file('data/lbco.cif')
```

Accessing the model after loading it will be done through the `sample_models`
object of the `project` instance. The name of the model will be the same as the
data block id in the CIF file. For example, if the CIF file contains a data
block with the id `lbco`,

<!-- prettier-ignore-start -->

<div class="cif">
<pre>
data_<span class="red"><b>lbco</b></span>

<span class="blue"><b>_space_group</b>.name_H-M_alt</span>  "P m -3 m"
...
</pre>
</div>

<!-- prettier-ignore-end -->

you can access it in the code as follows:

```python
# Access the sample model by its name
project.sample_models['lbco']
```

## Defining a Model Manually

If you do not have a CIF file or prefer to define the model manually, you can
use the `add` method of the `sample_models` object of the `project` instance. In
this case, you will need to specify the name of the model, which will be used to
reference it later.

```python
# Add a sample model with default parameters
# The sample model name is used to reference it later.
project.sample_models.add(name='nacl')
```

The `add` method creates a new sample model with default parameters. You can
then modify its parameters to match your specific crystallographic structure.
All parameters are grouped into the following categories, which makes it easier
to manage the model:

1. **Space Group Category**: Defines the symmetry of the crystal structure.
2. **Cell Category**: Specifies the dimensions and angles of the unit cell.
3. **Atom Sites Category**: Describes the positions and properties of atoms
   within the unit cell.

### 1. Space Group Category { #space-group-category }

```python
# Set space group
project.sample_models['nacl'].space_group.name_h_m = 'F m -3 m'
```

### 2. Cell Category { #cell-category }

```python
# Define unit cell parameters
project.sample_models['nacl'].cell.length_a = 5.691694
```

### 3. Atom Sites Category { #atom-sites-category }

```python
# Add atomic sites
project.sample_models['nacl'].atom_sites.append(
    label='Na',
    type_symbol='Na',
    fract_x=0,
    fract_y=0,
    fract_z=0,
    occupancy=1,
    b_iso_or_equiv=0.5
)
project.sample_models['nacl'].atom_sites.append(
    label='Cl',
    type_symbol='Cl',
    fract_x=0,
    fract_y=0,
    fract_z=0.5,
    occupancy=1,
    b_iso_or_equiv=0.5
)
```

## Listing Defined Models

To check which sample models have been added to the `project`, use:

```python
# Show defined sample models
project.sample_models.show_names()
```

Expected output:

```
Defined sample models 🧩
['lbco', 'nacl']
```

## Viewing a Model as CIF

To inspect a sample model in CIF format, use:

```python
# Show sample model as CIF
project.sample_models['lbco'].show_as_cif()
```

Example output:

```
Sample model 🧩 'lbco' as cif
╒═══════════════════════════════════════════╕
│ data_lbco                                 │
│                                           │
│ _space_group.IT_coordinate_system_code  1 │
│ _space_group.name_H-M_alt  "P m -3 m"     │
│                                           │
│ _cell.angle_alpha  90                     │
│ _cell.angle_beta  90                      │
│ _cell.angle_gamma  90                     │
│ _cell.length_a  3.88                      │
│ _cell.length_b  3.88                      │
│ _cell.length_c  3.88                      │
│                                           │
│ loop_                                     │
│ _atom_site.ADP_type                       │
│ _atom_site.B_iso_or_equiv                 │
│ _atom_site.fract_x                        │
│ _atom_site.fract_y                        │
│ _atom_site.fract_z                        │
│ _atom_site.label                          │
│ _atom_site.occupancy                      │
│ _atom_site.type_symbol                    │
│ _atom_site.Wyckoff_letter                 │
│ Biso 0.5 0.0 0.0 0.0 La 0.5 La a          │
│ Biso 0.5 0.0 0.0 0.0 Ba 0.5 Ba a          │
│ Biso 0.5 0.5 0.5 0.5 Co 1.0 Co b          │
│ Biso 0.5 0.0 0.5 0.5 O 1.0 O c            │
╘═══════════════════════════════════════════╛
```

## Saving a Model

Saving the project, as described in the [Project](project.md) section, will also
save the model. Each model is saved as a separate CIF file in the
`sample_models` subdirectory of the project directory. The project file contains
references to these files.

Below is an example of the saved CIF file for the `lbco` model:

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
Ba Ba   0   0   0     a   0.5  Biso 0.4943
Co Co   0.5 0.5 0.5   b   1    Biso 0.2567
O  O    0   0.5 0.5   c   1    Biso 1.4041
</pre>
</div>

<!-- prettier-ignore-end -->

<br>

---

Now that the crystallographic model has been defined and added to the project,
you can proceed to the next step: [Experiment](experiment.md).
