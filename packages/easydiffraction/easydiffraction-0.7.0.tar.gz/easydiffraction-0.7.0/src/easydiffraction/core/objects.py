# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

import secrets
import string
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import TypeVar
from typing import Union

from easydiffraction.core.singletons import UidMapHandler
from easydiffraction.utils.formatting import error
from easydiffraction.utils.formatting import warning

T = TypeVar('T')


class Descriptor:
    """
    Base class for descriptors (non-refinable attributes).
    """

    def __init__(
        self,
        value: Any,  # Value of the parameter
        name: str,  # ED parameter name (to access it in the code)
        cif_name: str,  # CIF parameter name (to show it in the CIF)
        pretty_name: Optional[str] = None,  # Pretty name (to show it in the table)
        datablock_id: Optional[str] = None,  # Parent datablock name
        category_key: Optional[str] = None,  # ED parent category name
        cif_category_key: Optional[str] = None,  # CIF parent category name
        collection_entry_id: Optional[str] = None,  # Parent collection entry id
        units: Optional[str] = None,  # Units of the parameter
        description: Optional[str] = None,  # Description of the parameter
        editable: bool = True,  # If false, the parameter can never be edited. It is calculated automatically
    ) -> None:
        self._value = value
        self.name: str = name
        self.cif_name: str = cif_name
        self.pretty_name: Optional[str] = pretty_name
        self._datablock_id: Optional[str] = datablock_id
        self.category_key: Optional[str] = category_key
        self.cif_category_key: Optional[str] = cif_category_key
        self._collection_entry_id: Optional[str] = collection_entry_id
        self.units: Optional[str] = units
        self._description: Optional[str] = description
        self._editable: bool = editable

        self._human_uid = self._generate_human_readable_unique_id()

        UidMapHandler.get().add_to_uid_map(self)

    def __str__(self):
        # Base value string
        value_str = f'{self.__class__.__name__}: {self.uid} = {self.value}'

        # Append ± uncertainty if it exists and is nonzero
        if hasattr(self, 'uncertainty') and getattr(self, 'uncertainty') != 0.0:
            value_str += f' ± {self.uncertainty}'

        # Append units if available
        if self.units:
            value_str += f' {self.units}'

        return value_str

    def __repr__(self):
        return self.__str__()

    def _generate_random_unique_id(self) -> str:
        # Derived class Parameter will use this unique id for the
        # minimization process to identify the parameter. It will also be
        # used to create the alias for the parameter in the constraint
        # expression.
        length = 16
        letters = [secrets.choice(string.ascii_lowercase) for _ in range(length)]
        uid = ''.join(letters)
        return uid

    def _generate_human_readable_unique_id(self):
        # Instead of generating a random string, we can use the
        # name of the parameter and the block name to create a unique id.
        #  E.g.:
        #  - "block-id.category-name.parameter-name": "lbco.cell.length_a"
        #  - "block-id.category-name.entry-id.parameter-name": "lbco.atom_site.Ba.fract_x"
        # For the analysis, we can use the same format, but without the
        # datablock id. E.g.:
        #  - "category-name.entry-id.parameter-name": "alias.occ_Ba.label"
        # This need to be called after the parameter is created and all its
        # attributes are set.
        if self.datablock_id:
            uid = f'{self.datablock_id}.{self.cif_category_key}'
        else:
            uid = f'{self.cif_category_key}'
        if self.collection_entry_id:
            uid += f'.{self.collection_entry_id}'
        uid += f'.{self.cif_name}'
        return uid

    @property
    def datablock_id(self):
        return self._datablock_id

    @datablock_id.setter
    def datablock_id(self, new_id):
        self._datablock_id = new_id
        # Update the unique id, when datablock_id attribute is of
        # the parameter is changed
        self.uid = self._generate_human_readable_unique_id()

    @property
    def collection_entry_id(self):
        return self._collection_entry_id

    @collection_entry_id.setter
    def collection_entry_id(self, new_id):
        self._collection_entry_id = new_id
        # Update the unique id, when datablock_id attribute is of
        # the parameter is changed
        self.uid = self._generate_human_readable_unique_id()

    @property
    def uid(self):
        return self._human_uid

    @uid.setter
    def uid(self, new_uid):
        # Update the unique id in the global uid map
        old_uid = self._human_uid
        self._human_uid = new_uid
        UidMapHandler.get().replace_uid(old_uid, new_uid)

    @property
    def minimizer_uid(self):
        return self.uid.replace('.', '__')

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any) -> None:
        if self._editable:
            self._value = new_value
        else:
            print(warning(f"The parameter '{self.cif_name}' it is calculated automatically and cannot be changed manually."))

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def editable(self) -> bool:
        return self._editable


class Parameter(Descriptor):
    """
    A parameter with a value, uncertainty, units, and CIF representation.
    """

    def __init__(
        self,
        value: Any,
        name: str,
        cif_name: str,
        pretty_name: Optional[str] = None,
        datablock_id: Optional[str] = None,  # Parent datablock name
        category_key: Optional[str] = None,
        cif_category_key: Optional[str] = None,
        collection_entry_id: Optional[str] = None,
        units: Optional[str] = None,
        description: Optional[str] = None,
        editable: bool = True,
        uncertainty: float = 0.0,
        free: bool = False,
        constrained: bool = False,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ) -> None:
        super().__init__(
            value,
            name,
            cif_name,
            pretty_name,
            datablock_id,
            category_key,
            cif_category_key,
            collection_entry_id,
            units,
            description,
            editable,
        )
        self.uncertainty: float = uncertainty  # Standard uncertainty or estimated standard deviation
        self.free: bool = free  # If the parameter is free to be fitted during the optimization
        self.constrained: bool = constrained  # If symmetry constrains the parameter during the optimization
        self.min: Optional[float] = min_value  # Minimum physical value of the parameter
        self.max: Optional[float] = max_value  # Maximum physical value of the parameter
        self.start_value: Optional[Any] = None  # Starting value for optimization


class Component(ABC):
    """
    Base class for standard components, like Cell, Peak, etc.
    """

    @property
    @abstractmethod
    def category_key(self):
        """
        Must be implemented in subclasses to return the ED category name.
        Can differ from cif_category_key.
        """
        pass

    @property
    @abstractmethod
    def cif_category_key(self):
        """
        Must be implemented in subclasses to return the CIF category name.
        """
        pass

    def __init__(self):
        self._locked = False  # If adding new attributes is locked

        self._datablock_id = None  # Parent datablock name to be set by the parent
        self._entry_id = None  # Parent collection entry id to be set by the parent

        # TODO: Currently, it is not used. Planned to be used for displaying
        #  the parameters in the specific order.
        self._ordered_attrs: List[str] = []

    def __getattr__(self, name: str) -> Any:
        """
        If the attribute is a Parameter or Descriptor, return its value by default
        """
        attr = self.__dict__.get(name, None)
        if isinstance(attr, (Descriptor, Parameter)):
            return attr.value
        raise AttributeError(f'{name} not found in {self}')

    def __setattr__(self, name: str, value: Any) -> None:
        """
        If an object is locked for adding new attributes, raise an error.
        If the attribute 'name' does not exist, add it.
        If the attribute 'name' exists and is a Parameter or Descriptor, set its value.
        """
        if hasattr(self, '_locked') and self._locked:
            if not hasattr(self, name):
                print(error(f"Cannot add new parameter '{name}'"))
                return

        # Try to get the attribute from the instance's dictionary
        attr = self.__dict__.get(name, None)

        # If the attribute is not set, and it is a Parameter or Descriptor,
        # set its category_key and cif_category_key to the current category_key
        # and cif_category_key and add it to the component.
        # Also add its name to the list of ordered attributes
        if attr is None:
            if isinstance(value, (Descriptor, Parameter)):
                value.category_key = self.category_key
                value.cif_category_key = self.cif_category_key
                self._ordered_attrs.append(name)
            super().__setattr__(name, value)
        # If the attribute is already set and is a Parameter or Descriptor,
        # update its value. Else, allow normal reassignment
        else:
            if isinstance(attr, (Descriptor, Parameter)):
                attr.value = value
            else:
                super().__setattr__(name, value)

    @property
    def datablock_id(self):
        return self._datablock_id

    @datablock_id.setter
    def datablock_id(self, new_id):
        self._datablock_id = new_id
        # For each parameter in this component, also update its datablock_id
        for param in self.get_all_params():
            param.datablock_id = new_id

    @property
    def entry_id(self):
        return self._entry_id

    @entry_id.setter
    def entry_id(self, new_id):
        self._entry_id = new_id
        # For each parameter in the component, set the entry_id
        for param in self.get_all_params():
            param.collection_entry_id = new_id

    def get_all_params(self):
        attr_objs = []
        for attr_name in dir(self):
            attr_obj = getattr(self, attr_name)
            if isinstance(attr_obj, (Descriptor, Parameter)):
                attr_objs.append(attr_obj)
        return attr_objs

    def as_dict(self) -> Dict[str, Any]:
        d = {}

        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue

            attr_obj = getattr(self, attr_name)
            if not isinstance(attr_obj, (Descriptor, Parameter)):
                continue

            key = attr_obj.cif_name
            value = attr_obj.value
            d[key] = value

        return d

    def as_cif(self) -> str:
        if not self.cif_category_key:
            raise ValueError('cif_category_key must be defined in the derived class.')

        lines = []

        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue

            attr_obj = getattr(self, attr_name)
            if not isinstance(attr_obj, (Descriptor, Parameter)):
                continue

            key = f'_{self.cif_category_key}.{attr_obj.cif_name}'
            value = attr_obj.value

            if value is None:
                continue

            if isinstance(value, str) and ' ' in value:
                value = f'"{value}"'

            line = f'{key}  {value}'
            lines.append(line)

        return '\n'.join(lines)


class Collection(ABC):
    """
    Base class for collections like AtomSites, LinkedPhases, SampleModels,
    Experiments, etc.
    """

    @property
    @abstractmethod
    def _child_class(self):
        return None

    def __init__(self, parent=None):
        self._parent = parent  # Parent datablock
        self._datablock_id = None  # Parent datablock name to be set by the parent
        self._items = {}

    def __getitem__(self, key: str) -> Union[Component, 'Collection']:
        return self._items[key]

    def __iter__(self) -> Iterator[Union[Component, 'Collection']]:
        return iter(self._items.values())

    @property
    def datablock_id(self):
        return self._datablock_id

    @datablock_id.setter
    def datablock_id(self, new_id):
        self._datablock_id = new_id
        for param in self.get_all_params():
            param.datablock_id = new_id

    def add(self, *args, **kwargs):
        """
        Add a new item to the collection. The item must be a subclass of
        Component.
        """
        if self._child_class is None:
            raise ValueError('Child class is not defined.')
        child_obj = self._child_class(*args, **kwargs)
        child_obj.datablock_id = self.datablock_id  # Setting the datablock_id to update its child parameters
        child_obj.entry_id = child_obj.entry_id  # Forcing the entry_id to be reset to update its child parameters
        self._items[child_obj._entry_id] = child_obj

        # Call on_item_added if it exists, i.e. defined in the derived class
        if hasattr(self, 'on_item_added'):
            self.on_item_added(child_obj)

    def get_all_params(self):
        params = []
        for item in self._items.values():
            if isinstance(item, Datablock):
                datablock = item
                for datablock_item in datablock.items():
                    if isinstance(datablock_item, Component):
                        component = datablock_item
                        for param in component.get_all_params():
                            params.append(param)
                    elif isinstance(datablock_item, Collection):
                        collection = datablock_item
                        for component in collection:
                            for param in component.get_all_params():
                                params.append(param)
            elif isinstance(item, Component):
                component = item
                for param in component.get_all_params():
                    params.append(param)
            else:
                raise TypeError(f'Expected a Component or Datablock, got {type(item)}')
        return params

    def get_fittable_params(self) -> List[Parameter]:
        all_params = self.get_all_params()
        params = []
        for param in all_params:
            if hasattr(param, 'free') and not param.constrained:
                params.append(param)
        return params

    def get_free_params(self) -> List[Parameter]:
        fittable_params = self.get_fittable_params()
        params = []
        for param in fittable_params:
            if param.free:
                params.append(param)
        return params

    def as_cif(self) -> str:
        lines = []
        if self._type == 'category':
            for idx, item in enumerate(self._items.values()):
                params = item.as_dict()
                category_key = item.cif_category_key
                # Keys
                keys = [f'_{category_key}.{param_key}' for param_key in params.keys()]
                # Values. If the value is a string and contains spaces, add quotes
                values = []
                for value in params.values():
                    value = f'{value}'
                    if ' ' in value:
                        value = f'"{value}"'
                    values.append(value)
                # Header is added only for the first item
                if idx == 0:
                    lines.append('loop_')
                    header = '\n'.join(keys)
                    lines.append(header)
                line = ' '.join(values)
                lines.append(line)
        return '\n'.join(lines)


class Datablock(ABC):
    """
    Base class for Sample Model and Experiment data blocks.
    """

    # TODO: Consider unifying with class Component?

    def __init__(self):
        self._name = None

    def __setattr__(self, name, value):
        # TODO: compare with class Component
        # If the value is a Component or Collection:
        # - set its datablock_id to the current datablock name
        # - add it to the datablock
        if isinstance(value, (Component, Collection)):
            value.datablock_id = self._name
        super().__setattr__(name, value)

    def items(self):
        """
        Returns a list of both components and collections in the
        data block.
        """
        attr_objs = []
        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue
            attr_obj = getattr(self, attr_name)
            if isinstance(attr_obj, (Component, Collection)):
                attr_objs.append(attr_obj)
        return attr_objs

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        # For each component/collection in this datablock,
        # also update its datablock_id
        for item in self.items():
            item.datablock_id = new_name
