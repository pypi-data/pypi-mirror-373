from easydiffraction.sample_models.components.cell import Cell


def test_cell_initialization():
    cell = Cell(length_a=5.0, length_b=6.0, length_c=7.0, angle_alpha=80.0, angle_beta=85.0, angle_gamma=95.0)

    # Assertions
    assert cell.length_a.value == 5.0
    assert cell.length_b.value == 6.0
    assert cell.length_c.value == 7.0
    assert cell.angle_alpha.value == 80.0
    assert cell.angle_beta.value == 85.0
    assert cell.angle_gamma.value == 95.0

    assert cell.length_a.units == 'Å'
    assert cell.angle_alpha.units == 'deg'


def test_cell_default_initialization():
    cell = Cell()

    # Assertions
    assert cell.length_a.value == 10.0
    assert cell.length_b.value == 10.0
    assert cell.length_c.value == 10.0
    assert cell.angle_alpha.value == 90.0
    assert cell.angle_beta.value == 90.0
    assert cell.angle_gamma.value == 90.0


def test_cell_properties():
    cell = Cell()

    # Assertions
    assert cell.cif_category_key == 'cell'
    assert cell.category_key == 'cell'
    assert cell._entry_id is None
