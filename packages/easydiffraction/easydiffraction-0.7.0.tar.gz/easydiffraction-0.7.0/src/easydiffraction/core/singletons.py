# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Type
from typing import TypeVar

from asteval import Interpreter

T = TypeVar('T', bound='BaseSingleton')


class BaseSingleton:
    """Base class to implement Singleton pattern.

    Ensures only one shared instance of a class is ever created.
    Useful for managing shared state across the library.
    """

    _instance = None  # Class-level shared instance

    @classmethod
    def get(cls: Type[T]) -> T:
        """Returns the shared instance, creating it if needed."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class UidMapHandler(BaseSingleton):
    """Global handler to manage UID-to-Parameter object mapping."""

    def __init__(self) -> None:
        # Internal map: uid (str) → Parameter instance
        self._uid_map: Dict[str, Any] = {}

    def get_uid_map(self) -> Dict[str, Any]:
        """Returns the current UID-to-Parameter map."""
        return self._uid_map

    def add_to_uid_map(self, parameter):
        """Adds a single Parameter object to the UID map."""
        self._uid_map[parameter.uid] = parameter

    def replace_uid(self, old_uid, new_uid):
        """Replaces an existing UID key in the UID map with a new UID.

        Moves the associated parameter from old_uid to new_uid.
        Raises a KeyError if the old_uid doesn't exist.
        """
        if old_uid in self._uid_map:
            self._uid_map[new_uid] = self._uid_map.pop(old_uid)
        else:
            raise KeyError(f"UID '{old_uid}' not found in the UID map.")

    # TODO: Implement removing from the UID map


# TODO: Implement changing atrr '.constrained' back to False
#  when removing constraints
class ConstraintsHandler(BaseSingleton):
    """Manages user-defined parameter constraints using aliases and expressions.

    Uses the asteval interpreter for safe evaluation of mathematical expressions.
    Constraints are defined as: lhs_alias = expression(rhs_aliases).
    """

    def __init__(self) -> None:
        # Maps alias names (like 'biso_La') → ConstraintAlias(param=Parameter)
        self._alias_to_param: Dict[str, Any] = {}

        # Stores raw user-defined constraints indexed by lhs_alias
        # Each value should contain: lhs_alias, rhs_expr
        self._constraints = {}

        # Internally parsed constraints as (lhs_alias, rhs_expr) tuples
        self._parsed_constraints: List[Tuple[str, str]] = []

    def set_aliases(self, aliases):
        """
        Sets the alias map (name → parameter wrapper).
        Called when user registers parameter aliases like:
            alias='biso_La', param=model.atom_sites['La'].b_iso
        """
        self._alias_to_param = aliases._items

    def set_constraints(self, constraints):
        """
        Sets the constraints and triggers parsing into internal format.
        Called when user registers expressions like:
            lhs_alias='occ_Ba', rhs_expr='1 - occ_La'
        """
        self._constraints = constraints._items
        self._parse_constraints()

    def _parse_constraints(self) -> None:
        """
        Converts raw expression input into a normalized internal list of
        (lhs_alias, rhs_expr) pairs, stripping whitespace and skipping invalid entries.
        """
        self._parsed_constraints = []

        for expr_obj in self._constraints.values():
            lhs_alias = expr_obj.lhs_alias.value
            rhs_expr = expr_obj.rhs_expr.value

            if lhs_alias and rhs_expr:
                constraint = (lhs_alias.strip(), rhs_expr.strip())
                self._parsed_constraints.append(constraint)

    def apply(self) -> None:
        """Evaluates constraints and applies them to dependent parameters.

        For each constraint:
        - Evaluate RHS using current values of aliases
        - Locate the dependent parameter by alias → uid → param
        - Update its value and mark it as constrained
        """
        if not self._parsed_constraints:
            return  # Nothing to apply

        # Retrieve global UID → Parameter object map
        uid_map = UidMapHandler.get().get_uid_map()

        # Prepare a flat dict of {alias: value} for use in expressions
        param_values = {}
        for alias, alias_obj in self._alias_to_param.items():
            uid = alias_obj.param_uid.value
            param = uid_map[uid]
            value = param.value
            param_values[alias] = value

        # Create an asteval interpreter for safe expression evaluation
        ae = Interpreter()
        ae.symtable.update(param_values)

        for lhs_alias, rhs_expr in self._parsed_constraints:
            try:
                # Evaluate the RHS expression using the current values
                rhs_value = ae(rhs_expr)

                # Get the actual parameter object we want to update
                dependent_uid = self._alias_to_param[lhs_alias].param_uid.value
                param = uid_map[dependent_uid]

                # Update its value and mark it as constrained
                param.value = rhs_value
                param.constrained = True

            except Exception as error:
                print(f"Failed to apply constraint '{lhs_alias} = {rhs_expr}': {error}")
