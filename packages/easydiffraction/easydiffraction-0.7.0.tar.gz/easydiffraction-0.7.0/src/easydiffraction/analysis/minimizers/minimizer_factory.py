# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.utils import render_table

from .minimizer_base import MinimizerBase
from .minimizer_dfols import DfolsMinimizer
from .minimizer_lmfit import LmfitMinimizer


class MinimizerFactory:
    _available_minimizers: Dict[str, Dict[str, Any]] = {
        'lmfit': {
            'engine': 'lmfit',
            'method': 'leastsq',
            'description': 'LMFIT library using the default Levenberg-Marquardt least squares method',
            'class': LmfitMinimizer,
        },
        'lmfit (leastsq)': {
            'engine': 'lmfit',
            'method': 'leastsq',
            'description': 'LMFIT library with Levenberg-Marquardt least squares method',
            'class': LmfitMinimizer,
        },
        'lmfit (least_squares)': {
            'engine': 'lmfit',
            'method': 'least_squares',
            'description': 'LMFIT library with SciPy’s trust region reflective algorithm',
            'class': LmfitMinimizer,
        },
        'dfols': {
            'engine': 'dfols',
            'method': None,
            'description': 'DFO-LS library for derivative-free least-squares optimization',
            'class': DfolsMinimizer,
        },
    }

    @classmethod
    def list_available_minimizers(cls) -> List[str]:
        """
        List all available minimizers.

        Returns:
            A list of minimizer names.
        """
        return list(cls._available_minimizers.keys())

    @classmethod
    def show_available_minimizers(cls) -> None:
        # TODO: Rename this method to `show_supported_minimizers` for
        #  consistency with other methods in the library. E.g.
        #  `show_supported_calculators`, etc.
        """
        Display a table of available minimizers and their descriptions.
        """
        columns_headers: List[str] = ['Minimizer', 'Description']
        columns_alignment = ['left', 'left']
        columns_data: List[List[str]] = []
        for name, config in cls._available_minimizers.items():
            description: str = config.get('description', 'No description provided.')
            columns_data.append([name, description])

        print(paragraph('Supported minimizers'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=columns_data,
        )

    @classmethod
    def create_minimizer(cls, selection: str) -> MinimizerBase:
        """
        Create a minimizer instance based on the selection.

        Args:
            selection: The name of the minimizer to create.

        Returns:
            An instance of the selected minimizer.

        Raises:
            ValueError: If the selection is not a valid minimizer.
        """
        config = cls._available_minimizers.get(selection)
        if not config:
            raise ValueError(f"Unknown minimizer '{selection}'. Use one of {cls.list_available_minimizers()}")

        minimizer_class: Type[MinimizerBase] = config.get('class')
        method: Optional[str] = config.get('method')

        kwargs: Dict[str, Any] = {}
        if method is not None:
            kwargs['method'] = method

        return minimizer_class(**kwargs)

    @classmethod
    def register_minimizer(
        cls,
        name: str,
        minimizer_cls: Type[MinimizerBase],
        method: Optional[str] = None,
        description: str = 'No description provided.',
    ) -> None:
        """
        Register a new minimizer.

        Args:
            name: The name of the minimizer.
            minimizer_cls: The class of the minimizer.
            method: The method used by the minimizer (optional).
            description: A description of the minimizer.
        """
        cls._available_minimizers[name] = {
            'engine': name,
            'method': method,
            'description': description,
            'class': minimizer_cls,
        }
