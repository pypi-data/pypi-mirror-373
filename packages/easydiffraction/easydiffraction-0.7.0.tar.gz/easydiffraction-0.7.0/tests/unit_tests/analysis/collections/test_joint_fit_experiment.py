from easydiffraction.analysis.collections.joint_fit_experiments import JointFitExperiment

# filepath: src/easydiffraction/analysis/collections/test_joint_fit_experiments.py


def test_joint_fit_experiment_initialization():
    # Test initialization of JointFitExperiment
    expt = JointFitExperiment(id='exp1', weight=1.5)
    assert expt.id.value == 'exp1'
    assert expt.id.name == 'id'
    assert expt.id.cif_name == 'id'
    assert expt.weight.value == 1.5
    assert expt.weight.name == 'weight'
    assert expt.weight.cif_name == 'weight'


def test_joint_fit_experiment_properties():
    # Test properties of JointFitExperiment
    expt = JointFitExperiment(id='exp2', weight=2.0)
    assert expt.cif_category_key == 'joint_fit_experiment'
    assert expt.category_key == 'joint_fit_experiment'
    assert expt._entry_id == 'exp2'
