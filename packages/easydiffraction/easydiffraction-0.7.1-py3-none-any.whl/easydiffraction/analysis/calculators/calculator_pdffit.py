# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

import os
import re

import numpy as np

from easydiffraction.experiments.experiment import Experiment
from easydiffraction.sample_models.sample_model import SampleModel

from .calculator_base import CalculatorBase

try:
    from diffpy.pdffit2 import PdfFit as pdffit
    from diffpy.pdffit2 import redirect_stdout
    from diffpy.structure.parsers.p_cif import P_cif as pdffit_cif_parser

    redirect_stdout(open(os.path.devnull, 'w'))  # silence the C++ engine output
    # TODO: Add the following print to debug mode
    # print("✅ 'pdffit' calculation engine is successfully imported.")
except ImportError:
    # TODO: Add the following print to debug mode
    # print("⚠️ 'pdffit' module not found. This calculation engine will not be available.")
    pdffit = None


class PdffitCalculator(CalculatorBase):
    """
    Wrapper for Pdffit library.
    """

    engine_imported: bool = pdffit is not None

    @property
    def name(self):
        return 'pdffit'

    def calculate_structure_factors(self, sample_models, experiments):
        # PDF doesn't compute HKL but we keep interface consistent
        print('[pdffit] Calculating HKLs (not applicable)...')
        return []

    def _calculate_single_model_pattern(
        self,
        sample_model: SampleModel,
        experiment: Experiment,
        called_by_minimizer: bool = False,
    ):
        # Create PDF calculator object
        calculator = pdffit()

        # ---------------------------
        # Set sample model parameters
        # ---------------------------

        # TODO: move CIF v2 -> CIF v1 conversion to a separate module
        # Convert the sample model to CIF supported by PDFfit
        cif_string_v2 = sample_model.as_cif()
        # convert to version 1 of CIF format
        # this means: replace all dots with underscores for
        # cases where the dot is surrounded by letters on both sides.
        pattern = r'(?<=[a-zA-Z])\.(?=[a-zA-Z])'
        cif_string_v1 = re.sub(pattern, '_', cif_string_v2)

        # Create the PDFit structure
        structure = pdffit_cif_parser().parse(cif_string_v1)

        # Set all model parameters:
        # space group, cell parameters, and atom sites (including ADPs)
        calculator.add_structure(structure)

        # -------------------------
        # Set experiment parameters
        # -------------------------

        # Set some peak-related parameters
        calculator.setvar('pscale', experiment.linked_phases[sample_model.name].scale.value)
        calculator.setvar('delta1', experiment.peak.sharp_delta_1.value)
        calculator.setvar('delta2', experiment.peak.sharp_delta_2.value)
        calculator.setvar('spdiameter', experiment.peak.damp_particle_diameter.value)

        # Data
        pattern = experiment.datastore.pattern
        x = list(pattern.x)
        y_noise = list(np.zeros_like(pattern.x))

        # Assign the data to the PDFfit calculator
        calculator.read_data_lists(
            stype=experiment.type.radiation_probe.value[0].upper(),
            qmax=experiment.peak.cutoff_q.value,
            qdamp=experiment.peak.damp_q.value,
            r_data=x,
            Gr_data=y_noise,
        )

        # qbroad must be set after read_data_lists
        calculator.setvar('qbroad', experiment.peak.broad_q.value)

        # -----------------
        # Calculate pattern
        # -----------------

        # Calculate the PDF pattern
        calculator.calc()

        # Get the calculated PDF pattern
        pattern = calculator.getpdf_fit()
        pattern = np.array(pattern)

        return pattern
