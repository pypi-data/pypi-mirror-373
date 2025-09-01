# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import TYPE_CHECKING

# This is needed for static type checkers like mypy and IDEs to recognize the imports
# without actually importing them at runtime, which helps avoid circular dependencies
# and reduces initial load time.
if TYPE_CHECKING:
    # Analysis
    from easydiffraction.analysis.analysis import Analysis

    # Experiments
    from easydiffraction.experiments.experiment import Experiment
    from easydiffraction.experiments.experiments import Experiments

    # Project management
    from easydiffraction.project import Project
    from easydiffraction.project import ProjectInfo

    # Sample model
    from easydiffraction.sample_models.sample_model import SampleModel
    from easydiffraction.sample_models.sample_models import SampleModels

    # Summary
    from easydiffraction.summary import Summary

    # Utils
    from easydiffraction.utils.formatting import chapter
    from easydiffraction.utils.formatting import paragraph
    from easydiffraction.utils.formatting import section
    from easydiffraction.utils.utils import download_from_repository
    from easydiffraction.utils.utils import fetch_tutorials
    from easydiffraction.utils.utils import get_value_from_xye_header
    from easydiffraction.utils.utils import list_tutorials
    from easydiffraction.utils.utils import show_version


# Lazy loading of submodules and classes
# This improves initial import time and reduces memory usage
# when only a subset of functionality is needed.
def __getattr__(name):
    if name == 'Analysis':
        from easydiffraction.analysis.analysis import Analysis

        return Analysis
    elif name == 'Experiment':
        from easydiffraction.experiments.experiment import Experiment

        return Experiment
    elif name == 'Experiments':
        from easydiffraction.experiments.experiments import Experiments

        return Experiments
    elif name == 'Project':
        from easydiffraction.project import Project

        return Project
    elif name == 'ProjectInfo':
        from easydiffraction.project import ProjectInfo

        return ProjectInfo
    elif name == 'SampleModel':
        from easydiffraction.sample_models.sample_model import SampleModel

        return SampleModel
    elif name == 'SampleModels':
        from easydiffraction.sample_models.sample_models import SampleModels

        return SampleModels
    elif name == 'Summary':
        from easydiffraction.summary import Summary

        return Summary
    elif name == 'chapter':
        from easydiffraction.utils.formatting import chapter

        return chapter
    elif name == 'section':
        from easydiffraction.utils.formatting import section

        return section
    elif name == 'paragraph':
        from easydiffraction.utils.formatting import paragraph

        return paragraph
    elif name == 'download_from_repository':
        from easydiffraction.utils.utils import download_from_repository

        return download_from_repository
    elif name == 'fetch_tutorials':
        from easydiffraction.utils.utils import fetch_tutorials

        return fetch_tutorials
    elif name == 'list_tutorials':
        from easydiffraction.utils.utils import list_tutorials

        return list_tutorials
    elif name == 'get_value_from_xye_header':
        from easydiffraction.utils.utils import get_value_from_xye_header

        return get_value_from_xye_header
    elif name == 'show_version':
        from easydiffraction.utils.utils import show_version

        return show_version
    raise AttributeError(f"module 'easydiffraction' has no attribute {name}")


# Expose the public API
__all__ = [
    'Project',
    'ProjectInfo',
    'SampleModel',
    'SampleModels',
    'Experiment',
    'Experiments',
    'Analysis',
    'Summary',
    'chapter',
    'section',
    'paragraph',
    'download_from_repository',
    'fetch_tutorials',
    'list_tutorials',
    'get_value_from_xye_header',
    'show_version',
]
