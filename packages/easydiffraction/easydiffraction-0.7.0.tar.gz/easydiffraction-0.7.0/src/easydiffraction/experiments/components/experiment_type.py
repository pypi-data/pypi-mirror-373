# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Descriptor


class ExperimentType(Component):
    @property
    def cif_category_key(self) -> str:
        return 'expt_type'

    @property
    def category_key(self) -> str:
        return 'expt_type'

    def __init__(
        self,
        sample_form: str,
        beam_mode: str,
        radiation_probe: str,
        scattering_type: str,
    ):
        super().__init__()

        self.sample_form: Descriptor = Descriptor(
            value=sample_form,
            name='sample_form',
            cif_name='sample_form',
            description='Specifies whether the diffraction data corresponds to powder diffraction or single crystal '
            'diffraction',
        )
        self.beam_mode: Descriptor = Descriptor(
            value=beam_mode,
            name='beam_mode',
            cif_name='beam_mode',
            description='Defines whether the measurement is performed with a constant wavelength (CW) or time-of-flight ('
            'TOF) method',
        )
        self.radiation_probe: Descriptor = Descriptor(
            value=radiation_probe,
            name='radiation_probe',
            cif_name='radiation_probe',
            description='Specifies whether the measurement uses neutrons or X-rays',
        )
        self.scattering_type: Descriptor = Descriptor(
            value=scattering_type,
            name='scattering_type',
            cif_name='scattering_type',
            description='Specifies whether the experiment uses Bragg scattering (for conventional structure refinement) or '
            'total scattering (for pair distribution function analysis - PDF)',
        )

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked: bool = True
