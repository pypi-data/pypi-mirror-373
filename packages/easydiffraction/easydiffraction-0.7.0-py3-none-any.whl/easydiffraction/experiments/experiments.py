# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

import os.path
from typing import Dict
from typing import List

from easydiffraction.core.objects import Collection
from easydiffraction.experiments.experiment import BaseExperiment
from easydiffraction.experiments.experiment import ExperimentFactory
from easydiffraction.utils.decorators import enforce_type
from easydiffraction.utils.formatting import paragraph


class Experiments(Collection):
    """
    Collection manager for multiple Experiment instances.
    """

    @property
    def _child_class(self):
        return BaseExperiment

    def __init__(self) -> None:
        super().__init__()
        self._experiments: Dict[str, BaseExperiment] = self._items  # Alias for legacy support

    def add(
        self,
        experiment=None,
        name=None,
        sample_form=None,
        beam_mode=None,
        radiation_probe=None,
        scattering_type=None,
        cif_path=None,
        cif_str=None,
        data_path=None,
    ):
        """
        Add a new experiment to the collection.
        """
        if scattering_type is None:
            scattering_type = 'bragg'
        if experiment:
            self._add_prebuilt_experiment(experiment)
        elif cif_path:
            self._add_from_cif_path(cif_path)
        elif cif_str:
            self._add_from_cif_string(cif_str)
        elif all(
            [
                name,
                sample_form,
                beam_mode,
                radiation_probe,
                data_path,
            ]
        ):
            self._add_from_data_path(
                name=name,
                sample_form=sample_form,
                beam_mode=beam_mode,
                radiation_probe=radiation_probe,
                scattering_type=scattering_type,
                data_path=data_path,
            )
        else:
            raise ValueError('Provide either experiment, type parameters, cif_path, cif_str, or data_path')

    @enforce_type
    def _add_prebuilt_experiment(self, experiment: BaseExperiment):
        self._experiments[experiment.name] = experiment

    def _add_from_cif_path(self, cif_path: str) -> None:
        print('Loading Experiment from CIF path...')
        raise NotImplementedError('CIF loading not implemented.')

    def _add_from_cif_string(self, cif_str: str) -> None:
        print('Loading Experiment from CIF string...')
        raise NotImplementedError('CIF loading not implemented.')

    def _add_from_data_path(
        self,
        name,
        sample_form,
        beam_mode,
        radiation_probe,
        scattering_type,
        data_path,
    ):
        """
        Load an experiment from raw data ASCII file.
        """
        print(paragraph('Loading measured data from ASCII file'))
        print(os.path.abspath(data_path))
        experiment = ExperimentFactory.create(
            name=name,
            sample_form=sample_form,
            beam_mode=beam_mode,
            radiation_probe=radiation_probe,
            scattering_type=scattering_type,
        )
        experiment._load_ascii_data_to_experiment(data_path)
        self._experiments[experiment.name] = experiment

    def remove(self, experiment_id: str) -> None:
        if experiment_id in self._experiments:
            del self._experiments[experiment_id]

    def show_names(self) -> None:
        print(paragraph('Defined experiments' + ' 🔬'))
        print(self.ids)

    @property
    def ids(self) -> List[str]:
        return list(self._experiments.keys())

    def show_params(self) -> None:
        for exp in self._experiments.values():
            print(exp)

    def as_cif(self) -> str:
        return '\n\n'.join([exp.as_cif() for exp in self._experiments.values()])
