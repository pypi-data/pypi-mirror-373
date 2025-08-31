import numpy as np
import pytest

from easydiffraction.crystallography.space_group_lookup_table import SPACE_GROUP_LOOKUP_DICT


def test_lookup_table_consistency():
    # Ensure that the space group numbers and system codes in the
    # key are the same as in the actual entries.
    for (it_number, it_code), entry in SPACE_GROUP_LOOKUP_DICT.items():
        assert entry['IT_number'] == it_number
        assert entry['IT_coordinate_system_code'] == it_code


@pytest.mark.parametrize(
    'key, expected',
    [
        (
            (62, 'cab'),
            {
                'IT_number': 62,
                'setting': 2,
                'IT_coordinate_system_code': 'cab',
                'name_H-M_alt': 'P b n m',
                'crystal_system': 'orthorhombic',
                'Wyckoff_positions': {
                    'd': {
                        'multiplicity': 8,
                        'site_symmetry': '1',
                        'coords_xyz': [
                            '(x,y,z)',
                            '(x+1/2,-y+1/2,-z)',
                            '(-x,-y,z+1/2)',
                            '(-x+1/2,y+1/2,-z+1/2)',
                            '(-x,-y,-z)',
                            '(-x+1/2,y+1/2,z)',
                            '(x,y,-z+1/2)',
                            '(x+1/2,-y+1/2,z+1/2)',
                        ],
                    },
                    'c': {
                        'multiplicity': 4,
                        'site_symmetry': '.m.',
                        'coords_xyz': ['(x,y,1/4)', '(x+1/2,-y+1/2,3/4)', '(-x,-y,3/4)', '(-x+1/2,y+1/2,1/4)'],
                    },
                    'b': {
                        'multiplicity': 4,
                        'site_symmetry': '-1',
                        'coords_xyz': ['(1/2,0,0)', '(0,1/2,0)', '(1/2,0,1/2)', '(0,1/2,1/2)'],
                    },
                    'a': {
                        'multiplicity': 4,
                        'site_symmetry': '-1',
                        'coords_xyz': ['(0,0,0)', '(1/2,1/2,0)', '(0,0,1/2)', '(1/2,1/2,1/2)'],
                    },
                },
            },
        ),
        (
            (199, '1'),
            {
                'IT_number': 199,
                'setting': 0,
                'IT_coordinate_system_code': '1',
                'name_H-M_alt': 'I 21 3',
                'crystal_system': 'cubic',
                'Wyckoff_positions': {
                    'c': {
                        'multiplicity': 24,
                        'site_symmetry': '1',
                        'coords_xyz': [
                            '(x,y,z)',
                            '(-x+1/2,-y,z+1/2)',
                            '(-x,y+1/2,-z+1/2)',
                            '(x+1/2,-y+1/2,-z)',
                            '(z,x,y)',
                            '(z+1/2,-x+1/2,-y)',
                            '(-z+1/2,-x,y+1/2)',
                            '(-z,x+1/2,-y+1/2)',
                            '(y,z,x)',
                            '(-y,z+1/2,-x+1/2)',
                            '(y+1/2,-z+1/2,-x)',
                            '(-y+1/2,-z,x+1/2)',
                        ],
                    },
                    'b': {
                        'multiplicity': 12,
                        'site_symmetry': '2..',
                        'coords_xyz': [
                            '(x,0,1/4)',
                            '(-x+1/2,0,3/4)',
                            '(1/4,x,0)',
                            '(3/4,-x+1/2,0)',
                            '(0,1/4,x)',
                            '(0,3/4,-x+1/2)',
                        ],
                    },
                    'a': {
                        'multiplicity': 8,
                        'site_symmetry': '.3.',
                        'coords_xyz': ['(x,x,x)', '(-x+1/2,-x,x+1/2)', '(-x,x+1/2,-x+1/2)', '(x+1/2,-x+1/2,-x)'],
                    },
                },
            },
        ),
    ],
)
def test_space_group_lookup_table_yields_expected(key, expected):
    """Check the lookup table for a few keys and check that the output matches the expected"""
    entry = SPACE_GROUP_LOOKUP_DICT[key]

    # Check that the keys are the same
    assert set(entry.keys()) == set(expected.keys())

    # Check the non-nested fields first
    for sub_key in expected.keys():
        if sub_key == 'Wyckoff_positions':
            continue
        assert expected[sub_key] == entry[sub_key]

    # Then check Wyckoff
    wyckoff_entry = entry['Wyckoff_positions']
    wyckoff_expected = expected['Wyckoff_positions']
    for site in wyckoff_expected.keys():
        assert site in wyckoff_expected.keys()
        assert wyckoff_entry[site]['multiplicity'] == wyckoff_expected[site]['multiplicity']
        assert wyckoff_entry[site]['site_symmetry'] == wyckoff_expected[site]['site_symmetry']
        assert np.all(wyckoff_entry[site]['coords_xyz'] == wyckoff_expected[site]['coords_xyz'])
