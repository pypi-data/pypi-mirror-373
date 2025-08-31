# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd

from easydiffraction.core.objects import Descriptor
from easydiffraction.core.objects import Parameter
from easydiffraction.core.singletons import ConstraintsHandler
from easydiffraction.experiments.experiments import Experiments
from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.formatting import warning
from easydiffraction.utils.utils import render_cif
from easydiffraction.utils.utils import render_table

from .calculators.calculator_factory import CalculatorFactory
from .collections.aliases import Aliases
from .collections.constraints import Constraints
from .collections.joint_fit_experiments import JointFitExperiments
from .minimization import DiffractionMinimizer
from .minimizers.minimizer_factory import MinimizerFactory


class Analysis:
    _calculator = CalculatorFactory.create_calculator('cryspy')

    def __init__(self, project) -> None:
        self.project = project
        self.aliases = Aliases()
        self.constraints = Constraints()
        self.constraints_handler = ConstraintsHandler.get()
        self.calculator = Analysis._calculator  # Default calculator shared by project
        self._calculator_key: str = 'cryspy'  # Added to track the current calculator
        self._fit_mode: str = 'single'
        self.fitter = DiffractionMinimizer('lmfit (leastsq)')

    def _get_params_as_dataframe(
        self,
        params: List[Union[Descriptor, Parameter]],
    ) -> pd.DataFrame:
        """
        Convert a list of parameters to a DataFrame.

        Args:
            params: List of Descriptor or Parameter objects.

        Returns:
            A pandas DataFrame containing parameter information.
        """
        rows = []
        for param in params:
            common_attrs = {}
            if isinstance(param, (Descriptor, Parameter)):
                common_attrs = {
                    'datablock': param.datablock_id,
                    'category': param.category_key,
                    'entry': param.collection_entry_id,
                    'parameter': param.name,
                    'value': param.value,
                    'units': param.units,
                    'fittable': False,
                }
            param_attrs = {}
            if isinstance(param, Parameter):
                param_attrs = {
                    'fittable': True,
                    'free': param.free,
                    'min': param.min,
                    'max': param.max,
                    'uncertainty': f'{param.uncertainty:.4f}' if param.uncertainty else '',
                    'value': f'{param.value:.4f}',
                    'units': param.units,
                }
            row = common_attrs | param_attrs
            rows.append(row)

        dataframe = pd.DataFrame(rows)
        return dataframe

    def show_all_params(self) -> None:
        sample_models_params = self.project.sample_models.get_all_params()
        experiments_params = self.project.experiments.get_all_params()

        if not sample_models_params and not experiments_params:
            print(warning('No parameters found.'))
            return

        columns_headers = [
            'datablock',
            'category',
            'entry',
            'parameter',
            'value',
            'fittable',
        ]
        columns_alignment = [
            'left',
            'left',
            'left',
            'left',
            'right',
            'left',
        ]

        sample_models_dataframe = self._get_params_as_dataframe(sample_models_params)
        sample_models_dataframe = sample_models_dataframe[columns_headers]

        print(paragraph('All parameters for all sample models (🧩 data blocks)'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=sample_models_dataframe,
            show_index=True,
        )

        experiments_dataframe = self._get_params_as_dataframe(experiments_params)
        experiments_dataframe = experiments_dataframe[columns_headers]

        print(paragraph('All parameters for all experiments (🔬 data blocks)'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=experiments_dataframe,
            show_index=True,
        )

    def show_fittable_params(self) -> None:
        sample_models_params = self.project.sample_models.get_fittable_params()
        experiments_params = self.project.experiments.get_fittable_params()

        if not sample_models_params and not experiments_params:
            print(warning('No fittable parameters found.'))
            return

        columns_headers = [
            'datablock',
            'category',
            'entry',
            'parameter',
            'value',
            'uncertainty',
            'units',
            'free',
        ]
        columns_alignment = [
            'left',
            'left',
            'left',
            'left',
            'right',
            'right',
            'left',
            'left',
        ]

        sample_models_dataframe = self._get_params_as_dataframe(sample_models_params)
        sample_models_dataframe = sample_models_dataframe[columns_headers]

        print(paragraph('Fittable parameters for all sample models (🧩 data blocks)'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=sample_models_dataframe,
            show_index=True,
        )

        experiments_dataframe = self._get_params_as_dataframe(experiments_params)
        experiments_dataframe = experiments_dataframe[columns_headers]

        print(paragraph('Fittable parameters for all experiments (🔬 data blocks)'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=experiments_dataframe,
            show_index=True,
        )

    def show_free_params(self) -> None:
        sample_models_params = self.project.sample_models.get_free_params()
        experiments_params = self.project.experiments.get_free_params()
        free_params = sample_models_params + experiments_params

        if not free_params:
            print(warning('No free parameters found.'))
            return

        columns_headers = [
            'datablock',
            'category',
            'entry',
            'parameter',
            'value',
            'uncertainty',
            'min',
            'max',
            'units',
        ]
        columns_alignment = [
            'left',
            'left',
            'left',
            'left',
            'right',
            'right',
            'right',
            'right',
            'left',
        ]

        dataframe = self._get_params_as_dataframe(free_params)
        dataframe = dataframe[columns_headers]

        print(paragraph('Free parameters for both sample models (🧩 data blocks) and experiments (🔬 data blocks)'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=dataframe,
            show_index=True,
        )

    def how_to_access_parameters(self) -> None:
        sample_models_params = self.project.sample_models.get_all_params()
        experiments_params = self.project.experiments.get_all_params()
        params = {'sample_models': sample_models_params, 'experiments': experiments_params}

        if not params:
            print(warning('No parameters found.'))
            return

        columns_headers = [
            'datablock',
            'category',
            'entry',
            'parameter',
            'How to Access in Python Code',
            'Unique Identifier for CIF Constraints',
        ]

        columns_alignment = [
            'left',
            'left',
            'left',
            'left',
            'left',
            'left',
        ]

        columns_data = []
        project_varname = self.project._varname
        for datablock_type, params in params.items():
            for param in params:
                if isinstance(param, (Descriptor, Parameter)):
                    datablock_id = param.datablock_id
                    category_key = param.category_key
                    entry_id = param.collection_entry_id
                    param_key = param.name
                    code_variable = f"{project_varname}.{datablock_type}['{datablock_id}'].{category_key}"
                    if entry_id:
                        code_variable += f"['{entry_id}']"
                    code_variable += f'.{param_key}'
                    cif_uid = param._generate_human_readable_unique_id()
                    columns_data.append([datablock_id, category_key, entry_id, param_key, code_variable, cif_uid])

        print(paragraph('How to access parameters'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=columns_data,
            show_index=True,
        )

    def show_current_calculator(self) -> None:
        print(paragraph('Current calculator'))
        print(self.current_calculator)

    @staticmethod
    def show_supported_calculators() -> None:
        CalculatorFactory.show_supported_calculators()

    @property
    def current_calculator(self) -> str:
        return self._calculator_key

    @current_calculator.setter
    def current_calculator(self, calculator_name: str) -> None:
        calculator = CalculatorFactory.create_calculator(calculator_name)
        if calculator is None:
            return
        self.calculator = calculator
        self._calculator_key = calculator_name
        print(paragraph('Current calculator changed to'))
        print(self.current_calculator)

    def show_current_minimizer(self) -> None:
        print(paragraph('Current minimizer'))
        print(self.current_minimizer)

    @staticmethod
    def show_available_minimizers() -> None:
        MinimizerFactory.show_available_minimizers()

    @property
    def current_minimizer(self) -> Optional[str]:
        return self.fitter.selection if self.fitter else None

    @current_minimizer.setter
    def current_minimizer(self, selection: str) -> None:
        self.fitter = DiffractionMinimizer(selection)
        print(paragraph('Current minimizer changed to'))
        print(self.current_minimizer)

    @property
    def fit_mode(self) -> str:
        return self._fit_mode

    @fit_mode.setter
    def fit_mode(self, strategy: str) -> None:
        if strategy not in ['single', 'joint']:
            raise ValueError("Fit mode must be either 'single' or 'joint'")
        self._fit_mode = strategy
        if strategy == 'joint':
            if not hasattr(self, 'joint_fit_experiments'):
                # Pre-populate all experiments with weight 0.5
                self.joint_fit_experiments = JointFitExperiments()
                for id in self.project.experiments.ids:
                    self.joint_fit_experiments.add(id, weight=0.5)
        print(paragraph('Current fit mode changed to'))
        print(self._fit_mode)

    def show_available_fit_modes(self) -> None:
        strategies = [
            {
                'Strategy': 'single',
                'Description': 'Independent fitting of each experiment; no shared parameters',
            },
            {
                'Strategy': 'joint',
                'Description': 'Simultaneous fitting of all experiments; some parameters are shared',
            },
        ]

        columns_headers = ['Strategy', 'Description']
        columns_alignment = ['left', 'left']
        columns_data = []
        for item in strategies:
            strategy = item['Strategy']
            description = item['Description']
            columns_data.append([strategy, description])

        print(paragraph('Available fit modes'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=columns_data,
        )

    def show_current_fit_mode(self) -> None:
        print(paragraph('Current fit mode'))
        print(self.fit_mode)

    def calculate_pattern(self, expt_name: str) -> Optional[np.ndarray]:
        """
        Calculate the diffraction pattern for a given experiment.

        Args:
            expt_name: The name of the experiment.

        Returns:
            The calculated pattern as a pandas DataFrame.
        """
        experiment = self.project.experiments[expt_name]
        sample_models = self.project.sample_models
        calculated_pattern = self.calculator.calculate_pattern(sample_models, experiment)
        return calculated_pattern

    def show_constraints(self) -> None:
        constraints_dict = self.constraints._items

        if not self.constraints._items:
            print(warning('No constraints defined.'))
            return

        rows = []
        for constraint in constraints_dict.values():
            row = {
                'lhs_alias': constraint.lhs_alias.value,
                'rhs_expr': constraint.rhs_expr.value,
                'full expression': f'{constraint.lhs_alias.value} = {constraint.rhs_expr.value}',
            }
            rows.append(row)

        headers = ['lhs_alias', 'rhs_expr', 'full expression']
        alignments = ['left', 'left', 'left']
        rows = [[row[header] for header in headers] for row in rows]

        print(paragraph('User defined constraints'))
        render_table(
            columns_headers=headers,
            columns_alignment=alignments,
            columns_data=rows,
        )

    def apply_constraints(self):
        if not self.constraints._items:
            print(warning('No constraints defined.'))
            return

        self.constraints_handler.set_aliases(self.aliases)
        self.constraints_handler.set_constraints(self.constraints)
        self.constraints_handler.apply()

    def fit(self):
        sample_models = self.project.sample_models
        if not sample_models:
            print('No sample models found in the project. Cannot run fit.')
            return

        experiments = self.project.experiments
        if not experiments:
            print('No experiments found in the project. Cannot run fit.')
            return

        calculator = self.calculator
        if not calculator:
            print('No calculator is set. Cannot run fit.')
            return

        # Run the fitting process
        experiment_ids = experiments.ids

        if self.fit_mode == 'joint':
            print(paragraph(f"Using all experiments 🔬 {experiment_ids} for '{self.fit_mode}' fitting"))
            self.fitter.fit(sample_models, experiments, calculator, weights=self.joint_fit_experiments)
        elif self.fit_mode == 'single':
            for expt_name in experiments.ids:
                print(paragraph(f"Using experiment 🔬 '{expt_name}' for '{self.fit_mode}' fitting"))
                experiment = experiments[expt_name]
                dummy_experiments = Experiments()  # TODO: Find a better name
                dummy_experiments.add(experiment)
                self.fitter.fit(sample_models, dummy_experiments, calculator)
        else:
            raise NotImplementedError(f'Fit mode {self.fit_mode} not implemented yet.')

        # After fitting, get the results
        self.fit_results = self.fitter.results

    def as_cif(self):
        current_minimizer = self.current_minimizer
        if ' ' in current_minimizer:
            current_minimizer = f'"{current_minimizer}"'

        lines = []
        lines.append(f'_analysis.calculator_engine  {self.current_calculator}')
        lines.append(f'_analysis.fitting_engine  {current_minimizer}')
        lines.append(f'_analysis.fit_mode  {self.fit_mode}')

        lines.append('')
        lines.append(self.aliases.as_cif())

        lines.append('')
        lines.append(self.constraints.as_cif())

        return '\n'.join(lines)

    def show_as_cif(self) -> None:
        cif_text: str = self.as_cif()
        paragraph_title: str = paragraph('Analysis 🧮 info as cif')
        render_cif(cif_text, paragraph_title)
