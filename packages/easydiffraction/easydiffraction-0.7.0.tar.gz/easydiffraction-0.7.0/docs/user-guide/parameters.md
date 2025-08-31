# Parameters

The data analysis process, introduced in the [Concept](concept.md) section,
assumes that you mainly work with different parameters. The parameters are used
to describe the sample model and the experiment and are required to set up the
analysis.

Each parameter in EasyDiffraction has a specific name used for code reference,
and it belongs to a specific category.

- In many cases, the EasyDiffraction name is the same as the CIF name.
- In some cases, the EasyDiffraction name is a slightly modified version of the
  CIF name to comply with Python naming conventions. For example, `name_H-M_alt`
  becomes `name_h_m`, replacing hyphens with underscores and using lowercase
  letters.
- In rare cases, the EasyDiffraction name is a bit shorter, like `b_iso` instead
  of CIF `B_iso_or_equiv`, to make the code a bit more user-friendly.
- When there is no defined CIF name for a parameter, EasyDiffraction introduces
  its own name, which is used in the code as well as an equivalent CIF name to
  be placed in the custom CIF dictionary `easydiffractionCIF`.

EasyDiffraction names are used in code, while CIF names are used to store and
retrieve the full state of a data analysis project in CIF format. You can find
more about the project in the [Project](analysis-workflow/project.md) section.

## Parameter Attributes

Parameters in EasyDiffraction are more than just variables. They are objects
that, in addition to the name and value, also include attributes such as the
description, unit, uncertainty, minimum and maximum values, etc. All these
attributes are described in the [API Reference](../api-reference/index.md)
section. Examples of how to use these parameters in code are provided in the
[Analysis Workflow](analysis-workflow/index.md) and
[Tutorials](../tutorials/index.md) sections.

The most important attribute, besides `name` and `value`, is `free`, which is
used to define whether the parameter is free or fixed for optimization during
the fitting process. The `free` attribute is set to `False` by default, which
means the parameter is fixed. To optimize a parameter, set `free` to `True`.

Although parameters are central, EasyDiffraction hides their creation and
attribute handling from the user. The user only accesses the required parameters
through the top-level objects, such as `project`, `sample_models`,
`experiments`, etc. The parameters are created and initialized automatically
when a new project is created or an existing one is loaded.

In the following sections, you can see a list of the parameters used in
EasyDiffraction. Use the tabs to switch between how to access a parameter in
code and its CIF name for serialization.

!!! warning "Important"

    Remember that parameters are accessed in code through their parent objects,
    such as `project`, `sample_models`, or `experiments`. For example, if you
    have a sample model with the ID `nacl`, you can access the space group name
    using the following syntax:

    ```python
    project.sample_models['nacl'].space_group.name_h_m
    ```

In the example above, `space_group` is a sample model category, and `name_h_m`
is the parameter. For simplicity, only the last part (`category.parameter`) of
the full access name will be shown in the tables below.

In addition, the CIF names are also provided for each parameter, which are used
to serialize the parameters in the CIF format.

Tags defining the corresponding experiment type are also given before the table.

## Sample model parameters

Below is a list of parameters used to describe the sample model in
EasyDiffraction.

### Crystall structure parameters

[pd-neut-cwl][3]{:.label-experiment} [pd-neut-tof][3]{:.label-experiment}
[pd-xray][3]{:.label-experiment} [sc-neut-cwl][3]{:.label-experiment}

=== "How to access in the code"

    | Category                                            | Parameter                                                    | How to access in the code          |
    |-----------------------------------------------------|--------------------------------------------------------------|------------------------------------|
    | :material-space-station: [space_group][space_group] | :material-tag: [name_hm][space_group]                        | space_group.name_hm                |
    |                                                     | :material-numeric: [system_code][space_group]                | space_group.system_code            |
    | :material-cube-outline: [cell][cell]                | :material-ruler: [length_a][cell]                            | cell.length_a                      |
    |                                                     | :material-ruler: [length_b][cell]                            | cell.length_b                      |
    |                                                     | :material-ruler: [length_c][cell]                            | cell.length_c                      |
    |                                                     | :material-angle-acute: [angle_alpha][cell]                   | cell.angle_alpha                   |
    |                                                     | :material-angle-acute: [angle_beta][cell]                    | cell.angle_beta                    |
    |                                                     | :material-angle-acute: [angle_gamma][cell]                   | cell.angle_gamma                   |
    | :material-atom: [atom_site][atom_site]              | :material-tag: [label][atom_site]                            | atom_sites['ID'].label             |
    |                                                     | :material-periodic-table: [type_symbol][atom_site]           | atom_sites['ID'].type_symbol       |
    |                                                     | :material-map-marker: [fract_x][atom_site]                   | atom_sites['ID'].fract_x           |
    |                                                     | :material-map-marker: [fract_y][atom_site]                   | atom_sites['ID'].fract_y           |
    |                                                     | :material-map-marker: [fract_z][atom_site]                   | atom_sites['ID'].fract_z           |
    |                                                     | :material-format-color-fill: [occupancy][atom_site]          | atom_sites['ID'].occupancy         |
    |                                                     | :material-cursor-move: [adp_type][atom_site]                 | atom_sites['ID'].adp_type          |
    |                                                     | :material-cursor-move: [b_iso][atom_site]                    | atom_sites['ID'].b_iso             |
    |                                                     | :material-reflect-horizontal: [multiplicity][atom_site]      | atom_sites['ID'].multiplicity      |
    |                                                     | :material-reflect-horizontal: [wyckoff_letter][atom_site]    | atom_sites['ID'].wyckoff_letter    |

=== "CIF name for serialization"

    | Category                                            | Parameter                                                    | CIF name for serialization              | CIF dictionary            |
    |-----------------------------------------------------|--------------------------------------------------------------|-----------------------------------------|---------------------------|
    | :material-space-station: [space_group][space_group] | :material-tag: [name_hm][space_group]                        | \_space_group.name_H-M_alt              | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-numeric: [system_code][space_group]                | \_space_group.IT_coordinate_system_code | [coreCIF][1]{:.label-cif} |
    | :material-cube-outline: [cell][cell]                | :material-ruler: [length_a][cell]                            | \_cell.length_a                         | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-ruler: [length_b][cell]                            | \_cell.length_b                         | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-ruler: [length_c][cell]                            | \_cell.length_c                         | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-angle-acute: [angle_alpha][cell]                   | \_cell.angle_alpha                      | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-angle-acute: [angle_beta][cell]                    | \_cell.angle_beta                       | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-angle-acute: [angle_gamma][cell]                   | \_cell.angle_gamma                      | [coreCIF][1]{:.label-cif} |
    | :material-atom: [atom_site][atom_site]              | :material-tag: [label][atom_site]                            | \_atom_site.label                       | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-periodic-table: [type_symbol][atom_site]           | \_atom_site.type_symbol                 | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-map-marker: [fract_x][atom_site]                   | \_atom_site.fract_x                     | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-map-marker: [fract_y][atom_site]                   | \_atom_site.fract_y                     | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-map-marker: [fract_z][atom_site]                   | \_atom_site.fract_z                     | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-format-color-fill: [occupancy][atom_site]          | \_atom_site.occupancy                   | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-cursor-move: [adp_type][atom_site]                 | \_atom_site.ADP_type                    | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-cursor-move: [b_iso][atom_site]                    | \_atom_site.B_iso_or_equiv              | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-reflect-horizontal: [multiplicity][atom_site]      | \_atom_site.site_symmetry_multiplicity  | [coreCIF][1]{:.label-cif} |
    |                                                     | :material-reflect-horizontal: [wyckoff_letter][atom_site]    | \_atom_site.Wyckoff_symbol              | [coreCIF][1]{:.label-cif} |

## Experiment parameters

Below is a list of parameters used to describe the experiment in
EasyDiffraction.

### Common parameters

[pd-neut-cwl][3]{:.label-experiment} [pd-neut-tof][3]{:.label-experiment}
[pd-xray][3]{:.label-experiment} [sc-neut-cwl][3]{:.label-experiment}

=== "How to access in the code"

    | Category                                     | Parameter                                                     | How to access in the code  |
    |----------------------------------------------|---------------------------------------------------------------|----------------------------|
    | :material-flask: [expt_type][expt_type]      | :material-sawtooth-wave: [beam_mode][expt_type]               | expt_type.beam_mode        |
    |                                              | :material-radiology-box-outline: [radiation_probe][expt_type] | expt_type.radiation_probe  |
    |                                              | :material-diamond-stone: [sample_form][expt_type]             | expt_type.sample_form      |
    |                                              | :material-chart-bell-curve: [scattering_type][expt_type]      | expt_type.scattering_type  |

=== "CIF name for serialization"

    | Category                                     | Parameter                                                     | CIF name for serialization   | CIF dictionary                       |
    |----------------------------------------------|---------------------------------------------------------------|------------------------------|--------------------------------------|
    | :material-flask: [expt_type][expt_type]      | :material-sawtooth-wave: [beam_mode][expt_type]               | \_expt_type.beam_mode        | [easydiffractionCIF][0]{:.label-cif} |
    |                                              | :material-radiology-box-outline: [radiation_probe][expt_type] | \_expt_type.radiation_probe  | [easydiffractionCIF][0]{:.label-cif} |
    |                                              | :material-diamond-stone: [sample_form][expt_type]             | \_expt_type.sample_form      | [easydiffractionCIF][0]{:.label-cif} |
    |                                              | :material-chart-bell-curve: [scattering_type][expt_type]      | \_expt_type.scattering_type  | [easydiffractionCIF][0]{:.label-cif} |

### Standard powder diffraction

[pd-neut-cwl][3]{:.label-experiment} [pd-neut-tof][3]{:.label-experiment}
[pd-xray][3]{:.label-experiment}

=== "How to access in the code"

    | Category                                         | Parameter                                                  | How to access in the code        |
    |--------------------------------------------------|------------------------------------------------------------|----------------------------------|
    | :material-waveform: [background][background]     | :material-arrow-collapse-right: [x][background]            | background.x                     |
    |                                                  | :material-arrow-collapse-up: [y][background]               | background.y                     |
    |                                                  | :material-format-superscript: [order][background]          | background.order                 |
    |                                                  | :material-arrow-collapse-up: [coef][background]            | background.coef                  |
    | :material-puzzle: [linked_phases][linked_phases] | :material-scale: [scale][linked_phases]                    | linked_phases['ID'].scale        |

=== "CIF name for serialization"

    | Category                                         | Parameter                                                  | CIF name for serialization             | CIF dictionary          |
    |--------------------------------------------------|------------------------------------------------------------|----------------------------------------|-------------------------|
    | :material-waveform: [background][background]     | :material-arrow-collapse-right: [x][background]            | \_pd_background.line_segment_X         | [pdCIF][0]{:.label-cif} |
    |                                                  | :material-arrow-collapse-up: [y][background]               | \_pd_background.line_segment_intensity | [pdCIF][0]{:.label-cif} |
    |                                                  | :material-format-superscript: [order][background]          | \_pd_background.chebyshev_order        | [pdCIF][0]{:.label-cif} |
    |                                                  | :material-arrow-collapse-up: [coef][background]            | \_pd_background.chebyshev_coef         | [pdCIF][0]{:.label-cif} |
    | :material-puzzle: [linked_phases][linked_phases] | :material-scale: [scale][linked_phases]                    | \_pd_phase_block.scale                 | [pdCIF][0]{:.label-cif} |

[pd-neut-cwl][3]{:.label-experiment} [pd-xray][3]{:.label-experiment}

=== "How to access in the code"

    | Category                                       | Parameter                                                  | How to access in the code        |
    |------------------------------------------------|------------------------------------------------------------|----------------------------------|
    | :material-microscope: [instrument][instrument] | :material-wrench: [setup_wavelength][instrument]           | instrument.setup_wavelength      |
    |                                                | :material-tune: [calib_twotheta_offset][instrument]        | instrument.calib_twotheta_offset |
    | :material-shape: [peak][peak]                  | :material-arrow-expand-horizontal: [broad_gauss_u][peak]   | peak.broad_gauss_u               |
    |                                                | :material-arrow-expand-horizontal: [broad_gauss_v][peak]   | peak.broad_gauss_v               |
    |                                                | :material-arrow-expand-horizontal: [broad_gauss_w][peak]   | peak.broad_gauss_w               |
    |                                                | :material-arrow-expand-horizontal: [broad_lorentz_x][peak] | peak.broad_lorentz_x             |
    |                                                | :material-arrow-expand-horizontal: [broad_lorentz_y][peak] | peak.broad_lorentz_y             |

=== "CIF name for serialization"

    | Category                                       | Parameter                                                  | CIF name for serialization         | CIF dictionary                       |
    |------------------------------------------------|------------------------------------------------------------|------------------------------------|--------------------------------------|
    | :material-microscope: [instrument][instrument] | :material-wrench: [setup_wavelength][instrument]           | \_instrument.setup_wavelength      | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-tune: [calib_twotheta_offset][instrument]        | \_instrument.calib_twotheta_offset | [easydiffractionCIF][0]{:.label-cif} |
    | :material-shape: [peak][peak]                  | :material-arrow-expand-horizontal: [broad_gauss_u][peak]   | \_peak.broad_gauss_u               | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-arrow-expand-horizontal: [broad_gauss_v][peak]   | \_peak.broad_gauss_v               | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-arrow-expand-horizontal: [broad_gauss_w][peak]   | \_peak.broad_gauss_w               | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-arrow-expand-horizontal: [broad_lorentz_x][peak] | \_peak.broad_lorentz_x             | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-arrow-expand-horizontal: [broad_lorentz_y][peak] | \_peak.broad_lorentz_y             | [easydiffractionCIF][0]{:.label-cif} |

[pd-neut-tof][3]{:.label-experiment}

=== "How to access in the code"

    | Category                                       | Parameter                                                      | How to access in the code        |
    |------------------------------------------------|----------------------------------------------------------------|----------------------------------|
    | :material-microscope: [instrument][instrument] | :material-wrench: [setup_twotheta_bank][instrument]            | instrument.setup_twotheta_bank   |
    |                                                | :material-tune: [calib_d_to_tof_recip][instrument]             | instrument.calib_d_to_tof_recip  |
    |                                                | :material-tune: [calib_d_to_tof_offset][instrument]            | instrument.calib_d_to_tof_offset |
    |                                                | :material-tune: [calib_d_to_tof_linear][instrument]            | instrument.calib_d_to_tof_linear |
    |                                                | :material-tune: [calib_d_to_tof_quad][instrument]              | instrument.calib_d_to_tof_quad   |
    | :material-shape: [peak][peak]                  | :material-arrow-expand-horizontal: [broad_gauss_sigma_0][peak] | peak.broad_gauss_sigma_0         |
    |                                                | :material-arrow-expand-horizontal: [broad_gauss_sigma_1][peak] | peak.broad_gauss_sigma_1         |
    |                                                | :material-arrow-expand-horizontal: [broad_gauss_sigma_2][peak] | peak.broad_gauss_sigma_2         |
    |                                                | :material-arrow-expand-horizontal: [broad_mix_beta_0][peak]    | peak.broad_mix_beta_0            |
    |                                                | :material-arrow-expand-horizontal: [broad_mix_beta_1][peak]    | peak.broad_mix_beta_1            |
    |                                                | :material-scale-unbalanced: [asym_alpha_0][peak]               | peak.asym_alpha_0                |
    |                                                | :material-scale-unbalanced: [asym_alpha_1][peak]               | peak.asym_alpha_1                |

=== "CIF name for serialization"

    | Category                                       | Parameter                                                      | CIF name for serialization         | CIF dictionary                       |
    |------------------------------------------------|----------------------------------------------------------------|------------------------------------|--------------------------------------|
    | :material-microscope: [instrument][instrument] | :material-wrench: [setup_twotheta_bank][instrument]            | \_instrument.setup_twotheta_bank   | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-tune: [calib_d_to_tof_recip][instrument]             | \_instrument.calib_d_to_tof_recip  | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-tune: [calib_d_to_tof_offset][instrument]            | \_instrument.calib_d_to_tof_offset | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-tune: [calib_d_to_tof_linear][instrument]            | \_instrument.calib_d_to_tof_linear | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-tune: [calib_d_to_tof_quad][instrument]              | \_instrument.calib_d_to_tof_quad   | [easydiffractionCIF][0]{:.label-cif} |
    | :material-shape: [peak][peak]                  | :material-arrow-expand-horizontal: [broad_gauss_sigma_0][peak] | \_peak.broad_gauss_sigma_0         | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-arrow-expand-horizontal: [broad_gauss_sigma_1][peak] | \_peak.broad_gauss_sigma_1         | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-arrow-expand-horizontal: [broad_gauss_sigma_2][peak] | \_peak.broad_gauss_sigma_2         | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-arrow-expand-horizontal: [broad_mix_beta_0][peak]    | \_peak.broad_mix_beta_0            | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-arrow-expand-horizontal: [broad_mix_beta_1][peak]    | \_peak.broad_mix_beta_1            | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-scale-unbalanced: [asym_alpha_0][peak]               | \_peak.asym_alpha_0                | [easydiffractionCIF][0]{:.label-cif} |
    |                                                | :material-scale-unbalanced: [asym_alpha_1][peak]               | \_peak.asym_alpha_1                | [easydiffractionCIF][0]{:.label-cif} |

### Total scattering

[pd-neut-total][3]{:.label-experiment} [pd-xray-total][3]{:.label-experiment}

=== "How to access in the code"

    | Category                                       | Parameter                                                    | How to access in the code        |
    |------------------------------------------------|--------------------------------------------------------------|----------------------------------|
    | :material-shape: [peak][peak]                  | :material-content-cut: [cutoff_q][peak]                      | peak.cutoff_q                    |
    |                                                | :material-arrow-expand-horizontal: [broad_q][peak]           | peak.broad_q                     |
    |                                                | :material-knife: [sharp_delta_1][peak]                       | peak.sharp_delta_1               |
    |                                                | :material-knife: [sharp_delta_2][peak]                       | peak.sharp_delta_2               |
    |                                                | :material-arrow-bottom-right: [damp_q][peak]                 | peak.damp_q                      |
    |                                                | :material-arrow-bottom-right: [damp_particle_diameter][peak] | peak.damp_particle_diameter      |

=== "CIF name for serialization"

     | Category                                       | Parameter                                                    | CIF name for serialization    | CIF dictionary                       |
     |------------------------------------------------|--------------------------------------------------------------|-------------------------------|--------------------------------------|
     | :material-shape: [peak][peak]                  | :material-content-cut: [cutoff_q][peak]                      | \_peak.cutoff_q               | [easydiffractionCIF][0]{:.label-cif} |
     |                                                | :material-arrow-expand-horizontal: [broad_q][peak]           | \_peak.broad_q                | [easydiffractionCIF][0]{:.label-cif} |
     |                                                | :material-knife: [sharp_delta_1][peak]                       | \_peak.sharp_delta_1          | [easydiffractionCIF][0]{:.label-cif} |
     |                                                | :material-knife: [sharp_delta_2][peak]                       | \_peak.sharp_delta_2          | [easydiffractionCIF][0]{:.label-cif} |
     |                                                | :material-arrow-bottom-right: [damp_q][peak]                 | \_peak.damp_q                 | [easydiffractionCIF][0]{:.label-cif} |
     |                                                | :material-arrow-bottom-right: [damp_particle_diameter][peak] | \_peak.damp_particle_diameter | [easydiffractionCIF][0]{:.label-cif} |

<!-- prettier-ignore-start -->
[0]: #
[1]: https://www.iucr.org/resources/cif/dictionaries/browse/cif_core
[2]: https://www.iucr.org/resources/cif/dictionaries/browse/cif_pd
[3]: glossary.md#experiment-type-labels
[space_group]: parameters/space_group.md
[cell]: parameters/cell.md
[atom_site]: parameters/atom_site.md
[expt_type]: parameters/expt_type.md
[instrument]: parameters/instrument.md
[peak]: parameters/peak.md
[background]: parameters/background.md
[linked_phases]: parameters/linked_phases.md
<!-- prettier-ignore-end -->
