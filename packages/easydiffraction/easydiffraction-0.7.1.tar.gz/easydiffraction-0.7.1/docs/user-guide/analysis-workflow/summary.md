---
icon: material/clipboard-text
---

# :material-clipboard-text: Summary

The **Summary** section represents the final step in the data processing
workflow. It involves generating a **summary report** that consolidates the
results of the diffraction data analysis, providing a comprehensive overview of
the model refinement process and its outcomes.

## Contents of the Summary Report

The summary report includes key details such as:

- Final refined model parameters – Optimized crystallographic and instrumental
  parameters.
- Goodness-of-fit indicators – Metrics such as R-factors, chi-square (χ²), and
  residuals.
- Graphical representation – Visualization of experimental vs. calculated
  diffraction patterns.

## Viewing the Summary Report

Users can print the summary report using:

```python
# Generate and print the summary report
project.summary.show_report()
```

<!--
This command will display a structured summary of the analysis results,
including model parameters, fit statistics, and data visualizations.
-->

## Saving a Summary

Saving the project, as described in the [Project](project.md) section, will also
save the summary report to the `summary.cif` inside the project directory.

<!--
## Exporting the Summary Report

EasyDiffraction allows exporting the summary report in various formats for
further analysis and documentation:

- Human-readable text format (.txt)
- CIF format (.cif) for integration with crystallographic databases
- PDF format (.pdf) for easy sharing and publication
-->

---

Now that the initial user guide is complete, you can explore the
[EasyDiffraction API](../../api-reference/index.md) for detailed information on
the available classes and methods. Additionally, you can find practical examples
and step-by-step guides in the [Tutorials](../../tutorials/index.md).
