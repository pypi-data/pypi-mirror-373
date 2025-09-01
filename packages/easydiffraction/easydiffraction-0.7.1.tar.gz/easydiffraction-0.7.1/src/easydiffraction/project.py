# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

import datetime
import os
import tempfile
from textwrap import wrap
from typing import List

from varname import varname

from easydiffraction.analysis.analysis import Analysis
from easydiffraction.experiments.experiments import Experiments
from easydiffraction.plotting.plotting import Plotter
from easydiffraction.sample_models.sample_models import SampleModels
from easydiffraction.summary import Summary
from easydiffraction.utils.formatting import error
from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.utils import render_cif
from easydiffraction.utils.utils import tof_to_d
from easydiffraction.utils.utils import twotheta_to_d


class ProjectInfo:
    """
    Stores metadata about the project, such as name, title, description,
    and file paths.
    """

    def __init__(self) -> None:
        self._name: str = 'untitled_project'
        self._title: str = 'Untitled Project'
        self._description: str = ''
        self._path: str = os.getcwd()
        self._created: datetime.datetime = datetime.datetime.now()
        self._last_modified: datetime.datetime = datetime.datetime.now()

    @property
    def name(self) -> str:
        """Return the project name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def title(self) -> str:
        """Return the project title."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def description(self) -> str:
        """Return sanitized description with single spaces."""
        return ' '.join(self._description.split())

    @description.setter
    def description(self, value: str) -> None:
        self._description = ' '.join(value.split())

    @property
    def path(self) -> str:
        """Return the project path."""
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    @property
    def created(self) -> datetime.datetime:
        """Return the creation timestamp."""
        return self._created

    @property
    def last_modified(self) -> datetime.datetime:
        """Return the last modified timestamp."""
        return self._last_modified

    def update_last_modified(self) -> None:
        """Update the last modified timestamp."""
        self._last_modified = datetime.datetime.now()

    def as_cif(self) -> str:
        """Export project metadata to CIF."""
        wrapped_title: List[str] = wrap(self.title, width=46)
        wrapped_description: List[str] = wrap(self.description, width=46)

        title_str: str = f"_project.title            '{wrapped_title[0]}'"
        for line in wrapped_title[1:]:
            title_str += f"\n{' ' * 27}'{line}'"

        if wrapped_description:
            base_indent: str = '_project.description      '
            indent_spaces: str = ' ' * len(base_indent)
            formatted_description: str = f"{base_indent}'{wrapped_description[0]}"
            for line in wrapped_description[1:]:
                formatted_description += f'\n{indent_spaces}{line}'
            formatted_description += "'"
        else:
            formatted_description: str = "_project.description      ''"

        return (
            f'_project.id               {self.name}\n'
            f'{title_str}\n'
            f'{formatted_description}\n'
            f"_project.created          '{self._created.strftime('%d %b %Y %H:%M:%S')}'\n"
            f"_project.last_modified    '{self._last_modified.strftime('%d %b %Y %H:%M:%S')}'\n"
        )

    def show_as_cif(self) -> None:
        cif_text: str = self.as_cif()
        paragraph_title: str = paragraph(f"Project 📦 '{self.name}' info as cif")
        render_cif(cif_text, paragraph_title)


class Project:
    """
    Central API for managing a diffraction data analysis project.
    Provides access to sample models, experiments, analysis, and summary.
    """

    def __init__(
        self,
        name: str = 'untitled_project',
        title: str = 'Untitled Project',
        description: str = '',
    ) -> None:
        self.info: ProjectInfo = ProjectInfo()
        self.info.name = name
        self.info.title = title
        self.info.description = description
        self.sample_models = SampleModels()
        self.experiments = Experiments()
        self.plotter = Plotter()
        self.analysis = Analysis(self)
        self.summary = Summary(self)
        self._saved = False
        self._varname = varname()

    @property
    def name(self) -> str:
        """Convenience property to access the project's name directly."""
        return self.info.name

    # ------------------------------------------
    #  Project File I/O
    # ------------------------------------------

    def load(self, dir_path: str) -> None:
        """
        Load a project from a given directory.
        Loads project info, sample models, experiments, etc.
        """
        print(paragraph(f'Loading project 📦 from {dir_path}'))
        print(dir_path)
        self.info.path = dir_path
        # TODO: load project components from files inside dir_path
        print('Loading project is not implemented yet.')
        self._saved = True

    def save_as(
        self,
        dir_path: str,
        temporary: bool = False,
    ) -> None:
        """
        Save the project into a new directory.
        """
        if temporary:
            tmp: str = tempfile.gettempdir()
            dir_path = os.path.join(tmp, dir_path)
        self.info.path = dir_path
        self.save()

    def save(self) -> None:
        """
        Save the project into the existing project directory.
        """
        if not self.info.path:
            print(error('Project path not specified. Use save_as() to define the path first.'))
            return

        print(paragraph(f"Saving project 📦 '{self.name}' to"))
        print(os.path.abspath(self.info.path))

        os.makedirs(self.info.path, exist_ok=True)

        # Save project info
        with open(os.path.join(self.info.path, 'project.cif'), 'w') as f:
            f.write(self.info.as_cif())
            print('✅ project.cif')

        # Save sample models
        sm_dir: str = os.path.join(self.info.path, 'sample_models')
        os.makedirs(sm_dir, exist_ok=True)
        for model in self.sample_models:
            file_name: str = f'{model.name}.cif'
            file_path: str = os.path.join(sm_dir, file_name)
            with open(file_path, 'w') as f:
                f.write(model.as_cif())
                print(f'✅ sample_models/{file_name}')

        # Save experiments
        expt_dir: str = os.path.join(self.info.path, 'experiments')
        os.makedirs(expt_dir, exist_ok=True)
        for experiment in self.experiments:
            file_name: str = f'{experiment.name}.cif'
            file_path: str = os.path.join(expt_dir, file_name)
            with open(file_path, 'w') as f:
                f.write(experiment.as_cif())
                print(f'✅ experiments/{file_name}')

        # Save analysis
        with open(os.path.join(self.info.path, 'analysis.cif'), 'w') as f:
            f.write(self.analysis.as_cif())
            print('✅ analysis.cif')

        # Save summary
        with open(os.path.join(self.info.path, 'summary.cif'), 'w') as f:
            f.write(self.summary.as_cif())
            print('✅ summary.cif')

        self.info.update_last_modified()
        self._saved = True

    # ------------------------------------------
    #  Sample Models API Convenience Methods
    # ------------------------------------------

    def set_sample_models(self, sample_models: SampleModels) -> None:
        """Attach a collection of sample models to the project."""
        self.sample_models = sample_models

    def set_experiments(self, experiments: Experiments) -> None:
        """Attach a collection of experiments to the project."""
        self.experiments = experiments

    # ------------------------------------------
    # Plotting
    # ------------------------------------------

    def plot_meas(
        self,
        expt_name,
        x_min=None,
        x_max=None,
        d_spacing=False,
    ):
        experiment = self.experiments[expt_name]
        pattern = experiment.datastore.pattern
        expt_type = experiment.type

        # Update d-spacing if necessary
        # TODO: This is done before every plot, and not when parameters
        #  needed for d-spacing conversion are changed. The reason is
        #  to minimize the performance impact during the fitting process.
        #  Need to find a better way to handle this.
        if d_spacing:
            self.update_pattern_d_spacing(expt_name)

        # Plot measured pattern
        self.plotter.plot_meas(
            pattern,
            expt_name,
            expt_type,
            x_min=x_min,
            x_max=x_max,
            d_spacing=d_spacing,
        )

    def plot_calc(
        self,
        expt_name,
        x_min=None,
        x_max=None,
        d_spacing=False,
    ):
        self.analysis.calculate_pattern(expt_name)  # Recalculate pattern
        experiment = self.experiments[expt_name]
        pattern = experiment.datastore.pattern
        expt_type = experiment.type

        # Update d-spacing if necessary
        # TODO: This is done before every plot, and not when parameters
        #  needed for d-spacing conversion are changed. The reason is
        #  to minimize the performance impact during the fitting process.
        #  Need to find a better way to handle this.
        if d_spacing:
            self.update_pattern_d_spacing(expt_name)

        # Plot calculated pattern
        self.plotter.plot_calc(
            pattern,
            expt_name,
            expt_type,
            x_min=x_min,
            x_max=x_max,
            d_spacing=d_spacing,
        )

    def plot_meas_vs_calc(
        self,
        expt_name,
        x_min=None,
        x_max=None,
        show_residual=False,
        d_spacing=False,
    ):
        self.analysis.calculate_pattern(expt_name)  # Recalculate pattern
        experiment = self.experiments[expt_name]
        pattern = experiment.datastore.pattern
        expt_type = experiment.type

        # Update d-spacing if necessary
        # TODO: This is done before every plot, and not when parameters
        #  needed for d-spacing conversion are changed. The reason is
        #  to minimize the performance impact during the fitting process.
        #  Need to find a better way to handle this.
        if d_spacing:
            self.update_pattern_d_spacing(expt_name)

        # Plot measured vs calculated
        self.plotter.plot_meas_vs_calc(
            pattern,
            expt_name,
            expt_type,
            x_min=x_min,
            x_max=x_max,
            show_residual=show_residual,
            d_spacing=d_spacing,
        )

    def update_pattern_d_spacing(self, expt_name: str) -> None:
        """
        Update the pattern's d-spacing based on the experiment's beam mode.
        """
        experiment = self.experiments[expt_name]
        pattern = experiment.datastore.pattern
        expt_type = experiment.type
        beam_mode = expt_type.beam_mode.value

        if beam_mode == 'time-of-flight':
            pattern.d = tof_to_d(
                pattern.x,
                experiment.instrument.calib_d_to_tof_offset.value,
                experiment.instrument.calib_d_to_tof_linear.value,
                experiment.instrument.calib_d_to_tof_quad.value,
            )
        elif beam_mode == 'constant wavelength':
            pattern.d = twotheta_to_d(pattern.x, experiment.instrument.setup_wavelength.value)
        else:
            print(error(f'Unsupported beam mode: {beam_mode} for d-spacing update.'))
