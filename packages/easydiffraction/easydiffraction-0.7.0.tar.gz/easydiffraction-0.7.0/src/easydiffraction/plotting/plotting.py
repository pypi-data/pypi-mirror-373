# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from easydiffraction.core.constants import DEFAULT_AXES_LABELS
from easydiffraction.plotting.plotters.plotter_ascii import AsciiPlotter
from easydiffraction.plotting.plotters.plotter_base import DEFAULT_ENGINE
from easydiffraction.plotting.plotters.plotter_base import DEFAULT_HEIGHT
from easydiffraction.plotting.plotters.plotter_base import DEFAULT_MAX
from easydiffraction.plotting.plotters.plotter_base import DEFAULT_MIN
from easydiffraction.plotting.plotters.plotter_plotly import PlotlyPlotter
from easydiffraction.utils.formatting import error
from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.utils import render_table


class Plotter:
    def __init__(self):
        # Plotting engine
        self._engine = DEFAULT_ENGINE

        # X-axis limits
        self._x_min = DEFAULT_MIN
        self._x_max = DEFAULT_MAX

        # Chart height
        self.height = DEFAULT_HEIGHT

        # Plotter instance
        self._plotter = PlotterFactory.create_plotter(self._engine)

    @property
    def engine(self):
        """Returns the current plotting engine name."""
        return self._engine

    @engine.setter
    def engine(self, new_engine):
        """Sets the current plotting engine name and updates the plotter instance."""
        new_plotter = PlotterFactory.create_plotter(new_engine)
        if new_plotter is None:
            return
        self._engine = new_engine
        self._plotter = new_plotter
        print(paragraph('Current plotter changed to'))
        print(self._engine)

    @property
    def x_min(self):
        """Returns the minimum x-axis limit."""
        return self._x_min

    @x_min.setter
    def x_min(self, value):
        """Sets the minimum x-axis limit."""
        if value is not None:
            self._x_min = value
        else:
            self._x_min = DEFAULT_MIN

    @property
    def x_max(self):
        """Returns the maximum x-axis limit."""
        return self._x_max

    @x_max.setter
    def x_max(self, value):
        """Sets the maximum x-axis limit."""
        if value is not None:
            self._x_max = value
        else:
            self._x_max = DEFAULT_MAX

    @property
    def height(self):
        """Returns the chart height."""
        return self._height

    @height.setter
    def height(self, value):
        """Sets the chart height."""
        if value is not None:
            self._height = value
        else:
            self._height = DEFAULT_HEIGHT

    def show_config(self):
        """
        Displays the current configuration settings.
        """
        columns_headers = ['Parameter', 'Value']
        columns_alignment = ['left', 'left']
        columns_data = [
            ['Plotting engine', self.engine],
            ['x-axis limits', f'[{self.x_min}, {self.x_max}]'],
            ['Chart height', self.height],
        ]

        print(paragraph('Current plotter configuration'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=columns_data,
        )

    def show_supported_engines(self):
        """
        Displays the supported plotting engines.
        """
        columns_headers = ['Engine', 'Description']
        columns_alignment = ['left', 'left']
        columns_data = []
        for name, config in PlotterFactory._SUPPORTED_ENGINES_DICT.items():
            description = config.get('description', 'No description provided.')
            columns_data.append([name, description])

        print(paragraph('Supported plotter engines'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=columns_data,
        )

    def plot_meas(self, pattern, expt_name, expt_type, x_min=None, x_max=None, d_spacing=False):
        if pattern.x is None:
            error(f'No data available for experiment {expt_name}')
            return
        if pattern.meas is None:
            error(f'No measured data available for experiment {expt_name}')
            return

        if d_spacing:
            x_array = pattern.d
        else:
            x_array = pattern.x
        x = self._filtered_y_array(
            y_array=x_array,
            x_array=x_array,
            x_min=x_min,
            x_max=x_max,
        )
        y_meas = self._filtered_y_array(
            y_array=pattern.meas,
            x_array=x_array,
            x_min=x_min,
            x_max=x_max,
        )

        y_series = [y_meas]
        y_labels = ['meas']

        if d_spacing:
            axes_labels = DEFAULT_AXES_LABELS[expt_type.scattering_type.value]['d-spacing']
        else:
            axes_labels = DEFAULT_AXES_LABELS[expt_type.scattering_type.value][expt_type.beam_mode.value]

        self._plotter.plot(
            x=x,
            y_series=y_series,
            labels=y_labels,
            axes_labels=axes_labels,
            title=f"Measured data for experiment 🔬 '{expt_name}'",
            height=self.height,
        )

    def plot_calc(
        self,
        pattern,
        expt_name,
        expt_type,
        x_min=None,
        x_max=None,
        d_spacing=False,
    ):
        if pattern.x is None:
            error(f'No data available for experiment {expt_name}')
            return
        if pattern.calc is None:
            print(f'No calculated data available for experiment {expt_name}')
            return

        if d_spacing:
            x_array = pattern.d
        else:
            x_array = pattern.x
        x = self._filtered_y_array(
            y_array=x_array,
            x_array=x_array,
            x_min=x_min,
            x_max=x_max,
        )
        y_calc = self._filtered_y_array(
            y_array=pattern.calc,
            x_array=x_array,
            x_min=x_min,
            x_max=x_max,
        )

        y_series = [y_calc]
        y_labels = ['calc']

        if d_spacing:
            axes_labels = DEFAULT_AXES_LABELS[expt_type.scattering_type.value]['d-spacing']
        else:
            axes_labels = DEFAULT_AXES_LABELS[expt_type.scattering_type.value][expt_type.beam_mode.value]

        self._plotter.plot(
            x=x,
            y_series=y_series,
            labels=y_labels,
            axes_labels=axes_labels,
            title=f"Calculated data for experiment 🔬 '{expt_name}'",
            height=self.height,
        )

    def plot_meas_vs_calc(
        self,
        pattern,
        expt_name,
        expt_type,
        x_min=None,
        x_max=None,
        show_residual=False,
        d_spacing=False,
    ):
        if pattern.x is None:
            print(error(f'No data available for experiment {expt_name}'))
            return
        if pattern.meas is None:
            print(error(f'No measured data available for experiment {expt_name}'))
            return
        if pattern.calc is None:
            print(error(f'No calculated data available for experiment {expt_name}'))
            return

        if d_spacing:
            x_array = pattern.d
        else:
            x_array = pattern.x
        x = self._filtered_y_array(
            y_array=x_array,
            x_array=x_array,
            x_min=x_min,
            x_max=x_max,
        )
        y_meas = self._filtered_y_array(
            y_array=pattern.meas,
            x_array=x_array,
            x_min=x_min,
            x_max=x_max,
        )
        y_calc = self._filtered_y_array(
            y_array=pattern.calc,
            x_array=x_array,
            x_min=x_min,
            x_max=x_max,
        )

        y_series = [y_meas, y_calc]
        y_labels = ['meas', 'calc']

        if d_spacing:
            axes_labels = DEFAULT_AXES_LABELS[expt_type.scattering_type.value]['d-spacing']
        else:
            axes_labels = DEFAULT_AXES_LABELS[expt_type.scattering_type.value][expt_type.beam_mode.value]

        if show_residual:
            y_resid = y_meas - y_calc
            y_series.append(y_resid)
            y_labels.append('resid')

        self._plotter.plot(
            x=x,
            y_series=y_series,
            labels=y_labels,
            axes_labels=axes_labels,
            title=f"Measured vs Calculated data for experiment 🔬 '{expt_name}'",
            height=self.height,
        )

    def _filtered_y_array(
        self,
        y_array,
        x_array,
        x_min,
        x_max,
    ):
        if x_min is None:
            x_min = self.x_min
        if x_max is None:
            x_max = self.x_max

        mask = (x_array >= x_min) & (x_array <= x_max)
        filtered_y_array = y_array[mask]

        return filtered_y_array


class PlotterFactory:
    _SUPPORTED_ENGINES_DICT = {
        'asciichartpy': {
            'description': 'Console ASCII line charts',
            'class': AsciiPlotter,
        },
        'plotly': {
            'description': 'Interactive browser-based graphing library',
            'class': PlotlyPlotter,
        },
    }

    @classmethod
    def supported_engines(cls):
        keys = cls._SUPPORTED_ENGINES_DICT.keys()
        engines = list(keys)
        return engines

    @classmethod
    def create_plotter(cls, engine_name):
        config = cls._SUPPORTED_ENGINES_DICT.get(engine_name)
        if not config:
            supported_engines = cls.supported_engines()
            print(error(f"Unsupported plotting engine '{engine_name}'"))
            print(f'Supported engines: {supported_engines}')
            return None
        plotter_class = config['class']
        plotter_obj = plotter_class()
        return plotter_obj
