---
icon: material/school
---

# :material-school: Tutorials

This section presents a collection of **Jupyter Notebook** tutorials that
demonstrate how to use EasyDiffraction for various tasks. These tutorials serve
as self-contained, step-by-step **guides** to help users grasp the workflow of
diffraction data analysis using EasyDiffraction.

Instructions on how to run the tutorials are provided in the
[:material-cog-box: Installation & Setup](../installation-and-setup/index.md#how-to-run-tutorials)
section of the documentation.

The tutorials are organized into the following categories.

## Getting Started

- [LBCO `quick`](quick_single-fit_pd-neut-cwl_LBCO-HRPT.ipynb) – A minimal
  example intended as a quick reference for users already familiar with the
  EasyDiffraction API or who want to see an example refinement in code. This
  tutorial covers a Rietveld refinement of the La0.5Ba0.5CoO3 crystal structure
  using constant wavelength neutron powder diffraction data from HRPT at PSI.
- [LBCO `basic`](basic_single-fit_pd-neut-cwl_LBCO-HRPT.ipynb) – Demonstrates
  the use of the EasyDiffraction API in a simplified, user-friendly manner that
  closely follows the GUI workflow for a Rietveld refinement of the
  La0.5Ba0.5CoO3 crystal structure using constant wavelength neutron powder
  diffraction data from HRPT at PSI. This tutorial provides a full explanation
  of the workflow with detailed comments and descriptions of every step, making
  it suitable for users who are new to EasyDiffraction or those who prefer a
  more guided approach.
- [PbSO4 `advanced`](advanced_joint-fit_pd-neut-xray-cwl_PbSO4.ipynb) –
  Demonstrates a more flexible and advanced approach to using the
  EasyDiffraction library, intended for users who are more comfortable with
  Python programming. This tutorial covers a Rietveld refinement of the PbSO4
  crystal structure based on the joint fit of both X-ray and neutron diffraction
  data.

## Standard Diffraction

- [HS `pd-neut-cwl`](cryst-struct_pd-neut-cwl_HS-HRPT.ipynb) – Demonstrates a
  Rietveld refinement of the HS crystal structure using constant wavelength
  neutron powder diffraction data from HRPT at PSI.
- [Si `pd-neut-tof`](cryst-struct_pd-neut-tof_Si-SEPD.ipynb) – Demonstrates a
  Rietveld refinement of the Si crystal structure using time-of-flight neutron
  powder diffraction data from SEPD at Argonne.
- [NCAF `pd-neut-tof`](cryst-struct_pd-neut-tof_multidata_NCAF-WISH.ipynb) –
  Demonstrates a Rietveld refinement of the Na2Ca3Al2F14 crystal structure using
  two time-of-flight neutron powder diffraction datasets (from two detector
  banks) of the WISH instrument at ISIS.
- [LBCO+Si McStas](cryst-struct_pd-neut-tof_multiphase-LBCO-Si_McStas.ipynb) –
  Demonstrates a Rietveld refinement of the La0.5Ba0.5CoO3 crystal structure
  with a small amount of Si impurity as a secondary phase using time-of-flight
  neutron powder diffraction data simulated with McStas.

## Pair Distribution Function (PDF)

- [Ni `pd-neut-cwl`](pdf_pd-neut-cwl_Ni.ipynb) – Demonstrates a PDF analysis of
  Ni using data collected from a constant wavelength neutron powder diffraction
  experiment.
- [Si `pd-neut-tof`](pdf_pd-neut-tof_Si-NOMAD.ipynb) – Demonstrates a PDF
  analysis of Si using data collected from a time-of-flight neutron powder
  diffraction experiment at NOMAD at SNS.
- [NaCl `pd-xray`](pdf_pd-xray_NaCl.ipynb) – Demonstrates a PDF analysis of NaCl
  using data collected from an X-ray powder diffraction experiment.

## Workshops & Schools

- [2025 DMSC](dmsc-summer-school-2025_analysis-powder-diffraction.ipynb) – A
  workshop tutorial that demonstrates a Rietveld refinement of the
  La0.5Ba0.5CoO3 crystal structure using time-of-flight neutron powder
  diffraction data simulated with McStas. This tutorial is designed for the ESS
  DMSC Summer School 2025.
