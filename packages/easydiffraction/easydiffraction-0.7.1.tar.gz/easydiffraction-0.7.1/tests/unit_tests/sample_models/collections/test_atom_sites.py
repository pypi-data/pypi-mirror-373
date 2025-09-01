import pytest

from easydiffraction.sample_models.collections.atom_sites import AtomSite
from easydiffraction.sample_models.collections.atom_sites import AtomSites


def test_atom_site_initialization():
    atom_site = AtomSite(
        label='O1',
        type_symbol='O',
        fract_x=0.1,
        fract_y=0.2,
        fract_z=0.3,
        wyckoff_letter='a',
        occupancy=0.8,
        b_iso=1.2,
        adp_type='Biso',
    )

    # Assertions
    assert atom_site.label.value == 'O1'
    assert atom_site.type_symbol.value == 'O'
    assert atom_site.fract_x.value == 0.1
    assert atom_site.fract_y.value == 0.2
    assert atom_site.fract_z.value == 0.3
    assert atom_site.wyckoff_letter.value == 'a'
    assert atom_site.occupancy.value == 0.8
    assert atom_site.b_iso.value == 1.2
    assert atom_site.adp_type.value == 'Biso'


def test_atom_site_properties():
    atom_site = AtomSite(label='O1', type_symbol='O', fract_x=0.1, fract_y=0.2, fract_z=0.3)

    # Assertions
    assert atom_site.cif_category_key == 'atom_site'
    assert atom_site.category_key == 'atom_sites'
    assert atom_site._entry_id == 'O1'


@pytest.fixture
def atom_sites_collection():
    return AtomSites()


def test_atom_sites_add(atom_sites_collection):
    atom_sites_collection.add(
        label='O1',
        type_symbol='O',
        fract_x=0.1,
        fract_y=0.2,
        fract_z=0.3,
        wyckoff_letter='a',
        occupancy=0.8,
        b_iso=1.2,
        adp_type='Biso',
    )

    # Assertions
    assert 'O1' in atom_sites_collection._items
    atom_site = atom_sites_collection._items['O1']
    assert isinstance(atom_site, AtomSite)
    assert atom_site.label.value == 'O1'
    assert atom_site.type_symbol.value == 'O'
    assert atom_site.fract_x.value == 0.1
    assert atom_site.fract_y.value == 0.2
    assert atom_site.fract_z.value == 0.3
    assert atom_site.wyckoff_letter.value == 'a'
    assert atom_site.occupancy.value == 0.8
    assert atom_site.b_iso.value == 1.2
    assert atom_site.adp_type.value == 'Biso'


def test_atom_sites_add_multiple(atom_sites_collection):
    atom_sites_collection.add(label='O1', type_symbol='O', fract_x=0.1, fract_y=0.2, fract_z=0.3)
    atom_sites_collection.add(label='C1', type_symbol='C', fract_x=0.4, fract_y=0.5, fract_z=0.6)

    # Assertions
    assert 'O1' in atom_sites_collection._items
    assert 'C1' in atom_sites_collection._items
    assert len(atom_sites_collection._items) == 2


def test_atom_sites_type(atom_sites_collection):
    # Assertions
    assert atom_sites_collection._type == 'category'
