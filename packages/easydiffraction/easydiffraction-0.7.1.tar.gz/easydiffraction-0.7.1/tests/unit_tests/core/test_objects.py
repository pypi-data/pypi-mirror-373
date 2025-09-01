from easydiffraction.core.objects import Collection
from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Datablock
from easydiffraction.core.objects import Descriptor
from easydiffraction.core.objects import Parameter

# filepath: src/easydiffraction/core/test_objects.py


def test_descriptor_initialization():
    desc = Descriptor(value=10, name='test', cif_name='test_cif', editable=True)
    assert desc.value == 10
    assert desc.name == 'test'
    assert desc.cif_name == 'test_cif'
    assert desc.editable is True


def test_descriptor_value_setter():
    desc = Descriptor(value=10, name='test', cif_name='test_cif', editable=True)
    desc.value = 20
    assert desc.value == 20

    desc_non_editable = Descriptor(value=10, name='test', cif_name='test_cif', editable=False)
    desc_non_editable.value = 30
    assert desc_non_editable.value == 10  # Value should not change


def test_parameter_initialization():
    param = Parameter(
        value=5.0,
        name='param',
        cif_name='param_cif',
        uncertainty=0.1,
        free=True,
        constrained=False,
        min_value=0.0,
        max_value=10.0,
    )
    assert param.value == 5.0
    assert param.uncertainty == 0.1
    assert param.free is True
    assert param.constrained is False
    assert param.min == 0.0
    assert param.max == 10.0


def test_component_abstract_methods():
    class TestComponent(Component):
        @property
        def category_key(self):
            return 'test_category'

        @property
        def cif_category_key(self):
            return 'test_cif_category'

    comp = TestComponent()
    assert comp.category_key == 'test_category'
    assert comp.cif_category_key == 'test_cif_category'


def test_component_attribute_handling():
    class TestComponent(Component):
        @property
        def category_key(self):
            return 'test_category'

        @property
        def cif_category_key(self):
            return 'test_cif_category'

    comp = TestComponent()
    desc = Descriptor(value=10, name='test', cif_name='test_cif')
    comp.test_attr = desc
    assert comp.test_attr.value == 10  # Access Descriptor value directly


def test_collection_add_and_retrieve():
    class TestCollection(Collection):
        @property
        def _child_class(self):
            return str

    collection = TestCollection()

    collection._items['item1'] = 'value1'
    collection._items['item2'] = 'value2'

    assert collection['item1'] == 'value1'
    assert collection['item2'] == 'value2'


def test_collection_iteration():
    class TestCollection(Collection):
        @property
        def _child_class(self):
            return str

    collection = TestCollection()

    collection._items['item1'] = 'value1'
    collection._items['item2'] = 'value2'

    items = list(collection)
    assert items == ['value1', 'value2']


def test_datablock_components():
    class TestComponent(Component):
        @property
        def category_key(self):
            return 'test_category'

        @property
        def cif_category_key(self):
            return 'test_cif_category'

    class TestDatablock(Datablock):
        def __init__(self):
            super().__init__()
            self.component1 = TestComponent()
            self.component2 = TestComponent()

    datablock = TestDatablock()
    items = datablock.items()
    assert len(items) == 2
    assert isinstance(items[0], TestComponent)
    assert isinstance(items[1], TestComponent)
