from easydiffraction.sample_models.components.space_group import SpaceGroup


def test_space_group_initialization():
    space_group = SpaceGroup(name_h_m='P 2/m', it_coordinate_system_code=1)

    # Assertions
    assert space_group.name_h_m.value == 'P 2/m'
    assert space_group.name_h_m.name == 'name_h_m'
    assert space_group.name_h_m.cif_name == 'name_H-M_alt'

    assert space_group.it_coordinate_system_code.value == 1
    assert space_group.it_coordinate_system_code.name == 'it_coordinate_system_code'
    assert space_group.it_coordinate_system_code.cif_name == 'IT_coordinate_system_code'


def test_space_group_default_initialization():
    space_group = SpaceGroup()

    # Assertions
    assert space_group.name_h_m.value == 'P 1'
    assert space_group.it_coordinate_system_code.value is None


def test_space_group_properties():
    space_group = SpaceGroup()

    # Assertions
    assert space_group.cif_category_key == 'space_group'
    assert space_group.category_key == 'space_group'
    assert space_group._entry_id is None
