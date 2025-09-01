from unittest.mock import MagicMock

import pytest

from easydiffraction.core.objects import Parameter
from easydiffraction.core.singletons import BaseSingleton
from easydiffraction.core.singletons import ConstraintsHandler
from easydiffraction.core.singletons import UidMapHandler


@pytest.fixture
def params():
    param1 = Parameter(value=1.0, name='param1', cif_name='param1_cif')
    param2 = Parameter(value=2.0, name='param2', cif_name='param2_cif')
    return param1, param2


@pytest.fixture
def mock_aliases(params):
    param1, param2 = params
    mock = MagicMock()
    mock._items = {
        'alias1': MagicMock(label=MagicMock(value='alias1'), param_uid=MagicMock(value=param1.uid)),
        'alias2': MagicMock(label=MagicMock(value='alias2'), param_uid=MagicMock(value=param2.uid)),
    }
    return mock


@pytest.fixture
def mock_constraints():
    mock = MagicMock()
    mock._items = {
        'expr1': MagicMock(lhs_alias=MagicMock(value='alias1'), rhs_expr=MagicMock(value='alias2 + 1')),
        'expr2': MagicMock(lhs_alias=MagicMock(value='alias2'), rhs_expr=MagicMock(value='alias1 * 2')),
    }
    return mock


def test_base_singleton():
    class TestSingleton(BaseSingleton):
        pass

    instance1 = TestSingleton.get()
    instance2 = TestSingleton.get()

    assert instance1 is instance2  # Ensure only one instance is created


def test_uid_map_handler(params):
    param1, param2 = params
    handler = UidMapHandler.get()
    uid_map = handler.get_uid_map()

    assert uid_map[param1.uid] is param1
    assert uid_map[param2.uid] is param2
    assert uid_map[param1.uid].uid == 'None.param1_cif'
    assert uid_map[param2.uid].uid == 'None.param2_cif'


def test_constraints_handler_set_aliases(mock_aliases, params):
    param1, param2 = params
    handler = ConstraintsHandler.get()
    handler.set_aliases(mock_aliases)

    assert handler._alias_to_param['alias1'].param_uid.value is param1.uid
    assert handler._alias_to_param['alias2'].param_uid.value is param2.uid


def test_constraints_handler_set_constraints(mock_constraints):
    handler = ConstraintsHandler.get()
    handler.set_constraints(mock_constraints)

    assert len(handler._parsed_constraints) == 2
    assert handler._parsed_constraints[0] == ('alias1', 'alias2 + 1')
    assert handler._parsed_constraints[1] == ('alias2', 'alias1 * 2')


def test_constraints_handler_apply(mock_aliases, mock_constraints, params):
    param1, _ = params
    handler = ConstraintsHandler.get()
    handler.set_aliases(mock_aliases)
    handler.set_constraints(mock_constraints)

    handler.apply()

    assert param1.value == 3.0
    assert param1.constrained is True
