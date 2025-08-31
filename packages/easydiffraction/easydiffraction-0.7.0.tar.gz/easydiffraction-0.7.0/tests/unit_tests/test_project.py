import datetime
import os
import time
from unittest.mock import MagicMock
from unittest.mock import patch

from easydiffraction.analysis.analysis import Analysis
from easydiffraction.experiments.experiments import Experiments
from easydiffraction.project import Project
from easydiffraction.project import ProjectInfo
from easydiffraction.sample_models.sample_models import SampleModels
from easydiffraction.summary import Summary

# ------------------------------------------
# Tests for ProjectInfo
# ------------------------------------------


def test_project_info_initialization():
    project_info = ProjectInfo()

    # Assertions
    assert project_info.name == 'untitled_project'
    assert project_info.title == 'Untitled Project'
    assert project_info.description == ''
    assert project_info.path == os.getcwd()
    assert isinstance(project_info.created, datetime.datetime)
    assert isinstance(project_info.last_modified, datetime.datetime)


def test_project_info_setters():
    project_info = ProjectInfo()

    # Set values
    project_info.name = 'test_project'
    project_info.title = 'Test Project'
    project_info.description = 'This is a test project.'
    project_info.path = '/test/path'

    # Assertions
    assert project_info.name == 'test_project'
    assert project_info.title == 'Test Project'
    assert project_info.description == 'This is a test project.'
    assert project_info.path == '/test/path'


def test_project_info_update_last_modified():
    project_info = ProjectInfo()
    initial_last_modified = project_info.last_modified

    # Add a small delay to ensure the timestamps differ
    time.sleep(0.001)
    project_info.update_last_modified()

    # Assertions
    assert project_info.last_modified > initial_last_modified


def test_project_info_as_cif():
    project_info = ProjectInfo()
    project_info.name = 'test_project'
    project_info.title = 'Test Project'
    project_info.description = 'This is a test project.'

    cif = project_info.as_cif()

    # Assertions
    assert '_project.id               test_project' in cif
    assert "_project.title            'Test Project'" in cif
    assert "_project.description      'This is a test project.'" in cif


@patch('builtins.print')
def test_project_info_show_as_cif(mock_print):
    project_info = ProjectInfo()
    project_info.name = 'test_project'
    project_info.title = 'Test Project'
    project_info.description = 'This is a test project.'

    project_info.show_as_cif()

    # Assertions
    mock_print.assert_called()


# ------------------------------------------
# Tests for Project
# ------------------------------------------


def test_project_initialization():
    with (
        patch('easydiffraction.sample_models.sample_models.SampleModels'),
        patch('easydiffraction.experiments.experiments.Experiments'),
        patch('easydiffraction.analysis.analysis.Analysis'),
        patch('easydiffraction.summary.Summary'),
    ):
        project = Project()  # Directly assign the instance to a variable

    # Assertions
    assert project.name == 'untitled_project'
    assert isinstance(project.sample_models, SampleModels)
    assert isinstance(project.experiments, Experiments)
    assert isinstance(project.analysis, Analysis)
    assert isinstance(project.summary, Summary)


@patch('builtins.print')
def test_project_load(mock_print):
    with (
        patch('easydiffraction.sample_models.sample_models.SampleModels'),
        patch('easydiffraction.experiments.experiments.Experiments'),
        patch('easydiffraction.analysis.analysis.Analysis'),
        patch('easydiffraction.summary.Summary'),
    ):
        project = Project()  # Directly assign the instance to a variable

    project.load('/test/path')

    # Assertions
    assert project.info.path == '/test/path'
    assert 'Loading project 📦 from /test/path' in mock_print.call_args_list[0][0][0]


@patch('builtins.print')
@patch('os.makedirs')
@patch('builtins.open', new_callable=MagicMock)
def test_project_save(mock_open, mock_makedirs, mock_print):
    with (
        patch('easydiffraction.sample_models.sample_models.SampleModels'),
        patch('easydiffraction.experiments.experiments.Experiments'),
        patch('easydiffraction.analysis.analysis.Analysis'),
        patch('easydiffraction.summary.Summary'),
    ):
        project = Project()  # Directly assign the instance to a variable

    project.info.path = '/test/path'
    project.save()

    # Assertions
    mock_makedirs.assert_any_call('/test/path', exist_ok=True)
    # mock_open.assert_any_call("/test/path\\summary.cif", "w")


@patch('builtins.print')
@patch('os.makedirs')
@patch('builtins.open', new_callable=MagicMock)
def test_project_save_as(mock_open, mock_makedirs, mock_print):
    with (
        patch('easydiffraction.sample_models.sample_models.SampleModels'),
        patch('easydiffraction.experiments.experiments.Experiments'),
        patch('easydiffraction.analysis.analysis.Analysis'),
        patch('easydiffraction.summary.Summary'),
    ):
        project = Project()  # Directly assign the instance to a variable

    project.save_as('new_project_path')

    # Assertions
    assert project.info.path.endswith('new_project_path')
    mock_makedirs.assert_any_call(project.info.path, exist_ok=True)
    mock_open.assert_any_call(os.path.join(project.info.path, 'project.cif'), 'w')


def test_project_set_sample_models():
    with (
        patch('easydiffraction.sample_models.sample_models.SampleModels'),
        patch('easydiffraction.experiments.experiments.Experiments'),
        patch('easydiffraction.analysis.analysis.Analysis'),
        patch('easydiffraction.summary.Summary'),
    ):
        project = Project()  # Directly assign the instance to a variable

    sample_models = MagicMock()
    project.set_sample_models(sample_models)

    # Assertions
    assert project.sample_models == sample_models


def test_project_set_experiments():
    with (
        patch('easydiffraction.sample_models.sample_models.SampleModels'),
        patch('easydiffraction.experiments.experiments.Experiments'),
        patch('easydiffraction.analysis.analysis.Analysis'),
        patch('easydiffraction.summary.Summary'),
    ):
        project = Project()  # Directly assign the instance to a variable

    experiments = MagicMock()
    project.set_experiments(experiments)

    # Assertions
    assert project.experiments == experiments
