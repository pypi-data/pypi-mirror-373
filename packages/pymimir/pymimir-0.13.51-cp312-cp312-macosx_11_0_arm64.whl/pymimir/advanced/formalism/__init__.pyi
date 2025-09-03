from collections.abc import Iterable, Iterator, Sequence
import enum
import os
import pathlib
from typing import overload

import pymimir.advanced.common


class RequirementEnum(enum.Enum):
    STRIPS = 0

    TYPING = 1

    NEGATIVE_PRECONDITIONS = 2

    DISJUNCTIVE_PRECONDITIONS = 3

    EQUALITY = 4

    EXISTENTIAL_PRECONDITIONS = 5

    UNIVERSAL_PRECONDITIONS = 6

    QUANTIFIED_PRECONDITIONS = 7

    CONDITIONAL_EFFECTS = 8

    FLUENTS = 9

    OBJECT_FLUENTS = 10

    NUMERIC_FLUENTS = 11

    ADL = 12

    DURATIVE_ACTIONS = 13

    DERIVED_PREDICATES = 14

    TIMED_INITIAL_LITERALS = 15

    PREFERENCES = 16

    CONSTRAINTS = 17

    ACTION_COSTS = 18

STRIPS: RequirementEnum = RequirementEnum.STRIPS

TYPING: RequirementEnum = RequirementEnum.TYPING

NEGATIVE_PRECONDITIONS: RequirementEnum = RequirementEnum.NEGATIVE_PRECONDITIONS

DISJUNCTIVE_PRECONDITIONS: RequirementEnum = RequirementEnum.DISJUNCTIVE_PRECONDITIONS

EQUALITY: RequirementEnum = RequirementEnum.EQUALITY

EXISTENTIAL_PRECONDITIONS: RequirementEnum = RequirementEnum.EXISTENTIAL_PRECONDITIONS

UNIVERSAL_PRECONDITIONS: RequirementEnum = RequirementEnum.UNIVERSAL_PRECONDITIONS

QUANTIFIED_PRECONDITIONS: RequirementEnum = RequirementEnum.QUANTIFIED_PRECONDITIONS

CONDITIONAL_EFFECTS: RequirementEnum = RequirementEnum.CONDITIONAL_EFFECTS

FLUENTS: RequirementEnum = RequirementEnum.FLUENTS

OBJECT_FLUENTS: RequirementEnum = RequirementEnum.OBJECT_FLUENTS

NUMERIC_FLUENTS: RequirementEnum = RequirementEnum.NUMERIC_FLUENTS

ADL: RequirementEnum = RequirementEnum.ADL

DURATIVE_ACTIONS: RequirementEnum = RequirementEnum.DURATIVE_ACTIONS

DERIVED_PREDICATES: RequirementEnum = RequirementEnum.DERIVED_PREDICATES

TIMED_INITIAL_LITERALS: RequirementEnum = RequirementEnum.TIMED_INITIAL_LITERALS

PREFERENCES: RequirementEnum = RequirementEnum.PREFERENCES

CONSTRAINTS: RequirementEnum = RequirementEnum.CONSTRAINTS

ACTION_COSTS: RequirementEnum = RequirementEnum.ACTION_COSTS

class AssignOperatorEnum(enum.Enum):
    ASSIGN = 0

    SCALE_UP = 1

    SCALE_DOWN = 2

    INCREASE = 3

    DECREASE = 4

ASSIGN: AssignOperatorEnum = AssignOperatorEnum.ASSIGN

SCALE_UP: AssignOperatorEnum = AssignOperatorEnum.SCALE_UP

SCALE_DOWN: AssignOperatorEnum = AssignOperatorEnum.SCALE_DOWN

INCREASE: AssignOperatorEnum = AssignOperatorEnum.INCREASE

DECREASE: AssignOperatorEnum = AssignOperatorEnum.DECREASE

class BinaryOperatorEnum(enum.Enum):
    MUL = 0

    PLUS = 1

    MINUS = 2

    DIV = 3

MUL: MultiOperatorEnum = MultiOperatorEnum.MUL

PLUS: MultiOperatorEnum = MultiOperatorEnum.PLUS

MINUS: BinaryOperatorEnum = BinaryOperatorEnum.MINUS

DIV: BinaryOperatorEnum = BinaryOperatorEnum.DIV

class MultiOperatorEnum(enum.Enum):
    MUL = 0

    PLUS = 1

class BinaryComparatorEnum(enum.Enum):
    EQUAL = 2

    GREATER = 0

    GREATER_EQUAL = 3

    LESS = 1

    LESS_EQUAL = 4

EQUAL: BinaryComparatorEnum = BinaryComparatorEnum.EQUAL

GREATER: BinaryComparatorEnum = BinaryComparatorEnum.GREATER

GREATER_EQUAL: BinaryComparatorEnum = BinaryComparatorEnum.GREATER_EQUAL

LESS: BinaryComparatorEnum = BinaryComparatorEnum.LESS

LESS_EQUAL: BinaryComparatorEnum = BinaryComparatorEnum.LESS_EQUAL

class OptimizationMetricEnum(enum.Enum):
    MINIMIZE = 0

    MAXIMIZE = 1

MINIMIZE: OptimizationMetricEnum = OptimizationMetricEnum.MINIMIZE

MAXIMIZE: OptimizationMetricEnum = OptimizationMetricEnum.MAXIMIZE

class ParserOptions:
    def __init__(self) -> None: ...

    @property
    def strict(self) -> bool:
        """Enable strict mode"""

    @strict.setter
    def strict(self, arg: bool, /) -> None: ...

    @property
    def quiet(self) -> bool:
        """Suppress output"""

    @quiet.setter
    def quiet(self, arg: bool, /) -> None: ...

class Requirements:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Requirements, /) -> bool: ...

    def __ne__(self, arg: Requirements, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_requirements(self) -> set[RequirementEnum]: ...

class Object:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Object, /) -> bool: ...

    def __ne__(self, arg: Object, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

class ObjectList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ObjectList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Object], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Object]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Object: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ObjectList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Object, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Object, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Object:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ObjectList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Object, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ObjectList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Object, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Object, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Object, /) -> None:
        """Remove first occurrence of `arg`."""

class Variable:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Variable, /) -> bool: ...

    def __ne__(self, arg: Variable, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

class VariableList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: VariableList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Variable], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Variable]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Variable: ...

    @overload
    def __getitem__(self, arg: slice, /) -> VariableList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Variable, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Variable, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Variable:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: VariableList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Variable, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: VariableList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Variable, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Variable, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Variable, /) -> None:
        """Remove first occurrence of `arg`."""

class Term:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Term, /) -> bool: ...

    def __ne__(self, arg: Term, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get(self) -> object: ...

class TermList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: TermList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Term], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Term]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Term: ...

    @overload
    def __getitem__(self, arg: slice, /) -> TermList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Term, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Term, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Term:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: TermList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Term, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: TermList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Term, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Term, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Term, /) -> None:
        """Remove first occurrence of `arg`."""

class StaticPredicate:
    def __str__(self) -> str: ...

    def __eq__(self, arg: StaticPredicate, /) -> bool: ...

    def __ne__(self, arg: StaticPredicate, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_parameters(self) -> VariableList: ...

    def get_arity(self) -> int: ...

class StaticPredicateList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: StaticPredicateList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[StaticPredicate], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[StaticPredicate]: ...

    @overload
    def __getitem__(self, arg: int, /) -> StaticPredicate: ...

    @overload
    def __getitem__(self, arg: slice, /) -> StaticPredicateList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: StaticPredicate, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: StaticPredicate, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> StaticPredicate:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: StaticPredicateList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: StaticPredicate, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: StaticPredicateList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: StaticPredicate, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: StaticPredicate, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: StaticPredicate, /) -> None:
        """Remove first occurrence of `arg`."""

class StaticPredicateMap:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: StaticPredicateMap) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: dict[str, StaticPredicate], /) -> None:
        """Construct from a dictionary"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the map is nonempty"""

    def __repr__(self) -> str: ...

    @overload
    def __contains__(self, arg: str, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def __getitem__(self, arg: str, /) -> StaticPredicate: ...

    def __delitem__(self, arg: str, /) -> None: ...

    def clear(self) -> None:
        """Remove all items"""

    def __setitem__(self, arg0: str, arg1: StaticPredicate, /) -> None: ...

    def update(self, arg: StaticPredicateMap, /) -> None:
        """Update the map with element from `arg`"""

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    class ItemView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[tuple[str, StaticPredicate]]: ...

    class KeyView:
        @overload
        def __contains__(self, arg: str, /) -> bool: ...

        @overload
        def __contains__(self, arg: object, /) -> bool: ...

        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[str]: ...

    class ValueView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[StaticPredicate]: ...

    def keys(self) -> StaticPredicateMap.KeyView:
        """Returns an iterable view of the map's keys."""

    def values(self) -> StaticPredicateMap.ValueView:
        """Returns an iterable view of the map's values."""

    def items(self) -> StaticPredicateMap.ItemView:
        """Returns an iterable view of the map's items."""

class FluentPredicate:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentPredicate, /) -> bool: ...

    def __ne__(self, arg: FluentPredicate, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_parameters(self) -> VariableList: ...

    def get_arity(self) -> int: ...

class FluentPredicateList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FluentPredicateList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[FluentPredicate], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[FluentPredicate]: ...

    @overload
    def __getitem__(self, arg: int, /) -> FluentPredicate: ...

    @overload
    def __getitem__(self, arg: slice, /) -> FluentPredicateList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: FluentPredicate, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: FluentPredicate, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> FluentPredicate:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: FluentPredicateList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: FluentPredicate, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: FluentPredicateList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: FluentPredicate, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: FluentPredicate, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: FluentPredicate, /) -> None:
        """Remove first occurrence of `arg`."""

class FluentPredicateMap:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FluentPredicateMap) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: dict[str, FluentPredicate], /) -> None:
        """Construct from a dictionary"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the map is nonempty"""

    def __repr__(self) -> str: ...

    @overload
    def __contains__(self, arg: str, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def __getitem__(self, arg: str, /) -> FluentPredicate: ...

    def __delitem__(self, arg: str, /) -> None: ...

    def clear(self) -> None:
        """Remove all items"""

    def __setitem__(self, arg0: str, arg1: FluentPredicate, /) -> None: ...

    def update(self, arg: FluentPredicateMap, /) -> None:
        """Update the map with element from `arg`"""

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    class ItemView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[tuple[str, FluentPredicate]]: ...

    class KeyView:
        @overload
        def __contains__(self, arg: str, /) -> bool: ...

        @overload
        def __contains__(self, arg: object, /) -> bool: ...

        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[str]: ...

    class ValueView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[FluentPredicate]: ...

    def keys(self) -> FluentPredicateMap.KeyView:
        """Returns an iterable view of the map's keys."""

    def values(self) -> FluentPredicateMap.ValueView:
        """Returns an iterable view of the map's values."""

    def items(self) -> FluentPredicateMap.ItemView:
        """Returns an iterable view of the map's items."""

class DerivedPredicate:
    def __str__(self) -> str: ...

    def __eq__(self, arg: DerivedPredicate, /) -> bool: ...

    def __ne__(self, arg: DerivedPredicate, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_parameters(self) -> VariableList: ...

    def get_arity(self) -> int: ...

class DerivedPredicateList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: DerivedPredicateList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[DerivedPredicate], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[DerivedPredicate]: ...

    @overload
    def __getitem__(self, arg: int, /) -> DerivedPredicate: ...

    @overload
    def __getitem__(self, arg: slice, /) -> DerivedPredicateList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: DerivedPredicate, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: DerivedPredicate, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> DerivedPredicate:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: DerivedPredicateList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: DerivedPredicate, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: DerivedPredicateList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: DerivedPredicate, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: DerivedPredicate, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: DerivedPredicate, /) -> None:
        """Remove first occurrence of `arg`."""

class DerivedPredicateMap:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: DerivedPredicateMap) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: dict[str, DerivedPredicate], /) -> None:
        """Construct from a dictionary"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the map is nonempty"""

    def __repr__(self) -> str: ...

    @overload
    def __contains__(self, arg: str, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def __getitem__(self, arg: str, /) -> DerivedPredicate: ...

    def __delitem__(self, arg: str, /) -> None: ...

    def clear(self) -> None:
        """Remove all items"""

    def __setitem__(self, arg0: str, arg1: DerivedPredicate, /) -> None: ...

    def update(self, arg: DerivedPredicateMap, /) -> None:
        """Update the map with element from `arg`"""

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    class ItemView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[tuple[str, DerivedPredicate]]: ...

    class KeyView:
        @overload
        def __contains__(self, arg: str, /) -> bool: ...

        @overload
        def __contains__(self, arg: object, /) -> bool: ...

        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[str]: ...

    class ValueView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[DerivedPredicate]: ...

    def keys(self) -> DerivedPredicateMap.KeyView:
        """Returns an iterable view of the map's keys."""

    def values(self) -> DerivedPredicateMap.ValueView:
        """Returns an iterable view of the map's values."""

    def items(self) -> DerivedPredicateMap.ItemView:
        """Returns an iterable view of the map's items."""

class StaticAtom:
    def __str__(self) -> str: ...

    def __eq__(self, arg: StaticAtom, /) -> bool: ...

    def __ne__(self, arg: StaticAtom, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_predicate(self) -> StaticPredicate: ...

    def get_terms(self) -> TermList: ...

    def get_variables(self) -> VariableList: ...

class StaticAtomList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: StaticAtomList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[StaticAtom], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[StaticAtom]: ...

    @overload
    def __getitem__(self, arg: int, /) -> StaticAtom: ...

    @overload
    def __getitem__(self, arg: slice, /) -> StaticAtomList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: StaticAtom, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: StaticAtom, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> StaticAtom:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: StaticAtomList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: StaticAtom, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: StaticAtomList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: StaticAtom, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: StaticAtom, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: StaticAtom, /) -> None:
        """Remove first occurrence of `arg`."""

class FluentAtom:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentAtom, /) -> bool: ...

    def __ne__(self, arg: FluentAtom, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_predicate(self) -> FluentPredicate: ...

    def get_terms(self) -> TermList: ...

    def get_variables(self) -> VariableList: ...

class FluentAtomList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FluentAtomList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[FluentAtom], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[FluentAtom]: ...

    @overload
    def __getitem__(self, arg: int, /) -> FluentAtom: ...

    @overload
    def __getitem__(self, arg: slice, /) -> FluentAtomList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: FluentAtom, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: FluentAtom, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> FluentAtom:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: FluentAtomList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: FluentAtom, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: FluentAtomList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: FluentAtom, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: FluentAtom, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: FluentAtom, /) -> None:
        """Remove first occurrence of `arg`."""

class DerivedAtom:
    def __str__(self) -> str: ...

    def __eq__(self, arg: DerivedAtom, /) -> bool: ...

    def __ne__(self, arg: DerivedAtom, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_predicate(self) -> DerivedPredicate: ...

    def get_terms(self) -> TermList: ...

    def get_variables(self) -> VariableList: ...

class DerivedAtomList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: DerivedAtomList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[DerivedAtom], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[DerivedAtom]: ...

    @overload
    def __getitem__(self, arg: int, /) -> DerivedAtom: ...

    @overload
    def __getitem__(self, arg: slice, /) -> DerivedAtomList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: DerivedAtom, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: DerivedAtom, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> DerivedAtom:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: DerivedAtomList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: DerivedAtom, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: DerivedAtomList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: DerivedAtom, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: DerivedAtom, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: DerivedAtom, /) -> None:
        """Remove first occurrence of `arg`."""

class StaticFunctionSkeleton:
    def __str__(self) -> str: ...

    def __eq__(self, arg: StaticFunctionSkeleton, /) -> bool: ...

    def __ne__(self, arg: StaticFunctionSkeleton, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_parameters(self) -> VariableList: ...

class StaticFunctionSkeletonList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: StaticFunctionSkeletonList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[StaticFunctionSkeleton], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[StaticFunctionSkeleton]: ...

    @overload
    def __getitem__(self, arg: int, /) -> StaticFunctionSkeleton: ...

    @overload
    def __getitem__(self, arg: slice, /) -> StaticFunctionSkeletonList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: StaticFunctionSkeleton, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: StaticFunctionSkeleton, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> StaticFunctionSkeleton:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: StaticFunctionSkeletonList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: StaticFunctionSkeleton, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: StaticFunctionSkeletonList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: StaticFunctionSkeleton, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: StaticFunctionSkeleton, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: StaticFunctionSkeleton, /) -> None:
        """Remove first occurrence of `arg`."""

class FluentFunctionSkeleton:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentFunctionSkeleton, /) -> bool: ...

    def __ne__(self, arg: FluentFunctionSkeleton, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_parameters(self) -> VariableList: ...

class FluentFunctionSkeletonList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FluentFunctionSkeletonList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[FluentFunctionSkeleton], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[FluentFunctionSkeleton]: ...

    @overload
    def __getitem__(self, arg: int, /) -> FluentFunctionSkeleton: ...

    @overload
    def __getitem__(self, arg: slice, /) -> FluentFunctionSkeletonList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: FluentFunctionSkeleton, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: FluentFunctionSkeleton, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> FluentFunctionSkeleton:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: FluentFunctionSkeletonList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: FluentFunctionSkeleton, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: FluentFunctionSkeletonList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: FluentFunctionSkeleton, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: FluentFunctionSkeleton, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: FluentFunctionSkeleton, /) -> None:
        """Remove first occurrence of `arg`."""

class AuxiliaryFunctionSkeleton:
    def __str__(self) -> str: ...

    def __eq__(self, arg: AuxiliaryFunctionSkeleton, /) -> bool: ...

    def __ne__(self, arg: AuxiliaryFunctionSkeleton, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_parameters(self) -> VariableList: ...

class AuxiliaryFunctionSkeletonList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: AuxiliaryFunctionSkeletonList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[AuxiliaryFunctionSkeleton], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[AuxiliaryFunctionSkeleton]: ...

    @overload
    def __getitem__(self, arg: int, /) -> AuxiliaryFunctionSkeleton: ...

    @overload
    def __getitem__(self, arg: slice, /) -> AuxiliaryFunctionSkeletonList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: AuxiliaryFunctionSkeleton, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: AuxiliaryFunctionSkeleton, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> AuxiliaryFunctionSkeleton:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: AuxiliaryFunctionSkeletonList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: AuxiliaryFunctionSkeleton, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: AuxiliaryFunctionSkeletonList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: AuxiliaryFunctionSkeleton, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: AuxiliaryFunctionSkeleton, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: AuxiliaryFunctionSkeleton, /) -> None:
        """Remove first occurrence of `arg`."""

class StaticFunction:
    def __str__(self) -> str: ...

    def __eq__(self, arg: StaticFunction, /) -> bool: ...

    def __ne__(self, arg: StaticFunction, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function_skeleton(self) -> StaticFunctionSkeleton: ...

    def get_terms(self) -> TermList: ...

class StaticFunctionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: StaticFunctionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[StaticFunction], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[StaticFunction]: ...

    @overload
    def __getitem__(self, arg: int, /) -> StaticFunction: ...

    @overload
    def __getitem__(self, arg: slice, /) -> StaticFunctionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: StaticFunction, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: StaticFunction, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> StaticFunction:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: StaticFunctionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: StaticFunction, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: StaticFunctionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: StaticFunction, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: StaticFunction, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: StaticFunction, /) -> None:
        """Remove first occurrence of `arg`."""

class FluentFunction:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentFunction, /) -> bool: ...

    def __ne__(self, arg: FluentFunction, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function_skeleton(self) -> FluentFunctionSkeleton: ...

    def get_terms(self) -> TermList: ...

class FluentFunctionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FluentFunctionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[FluentFunction], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[FluentFunction]: ...

    @overload
    def __getitem__(self, arg: int, /) -> FluentFunction: ...

    @overload
    def __getitem__(self, arg: slice, /) -> FluentFunctionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: FluentFunction, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: FluentFunction, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> FluentFunction:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: FluentFunctionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: FluentFunction, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: FluentFunctionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: FluentFunction, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: FluentFunction, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: FluentFunction, /) -> None:
        """Remove first occurrence of `arg`."""

class AuxiliaryFunction:
    def __str__(self) -> str: ...

    def __eq__(self, arg: AuxiliaryFunction, /) -> bool: ...

    def __ne__(self, arg: AuxiliaryFunction, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function_skeleton(self) -> AuxiliaryFunctionSkeleton: ...

    def get_terms(self) -> TermList: ...

class AuxiliaryFunctionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: AuxiliaryFunctionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[AuxiliaryFunction], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[AuxiliaryFunction]: ...

    @overload
    def __getitem__(self, arg: int, /) -> AuxiliaryFunction: ...

    @overload
    def __getitem__(self, arg: slice, /) -> AuxiliaryFunctionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: AuxiliaryFunction, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: AuxiliaryFunction, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> AuxiliaryFunction:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: AuxiliaryFunctionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: AuxiliaryFunction, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: AuxiliaryFunctionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: AuxiliaryFunction, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: AuxiliaryFunction, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: AuxiliaryFunction, /) -> None:
        """Remove first occurrence of `arg`."""

class StaticGroundFunction:
    def __hash__(self) -> int: ...

    def __eq__(self, arg: StaticGroundFunction, /) -> bool: ...

    def __ne__(self, arg: StaticGroundFunction, /) -> bool: ...

    def __str__(self) -> str: ...

    def get_index(self) -> int: ...

    def get_function_skeleton(self) -> StaticFunctionSkeleton: ...

    def get_objects(self) -> ObjectList: ...

class StaticGroundFunctionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: StaticGroundFunctionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[StaticGroundFunction], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[StaticGroundFunction]: ...

    @overload
    def __getitem__(self, arg: int, /) -> StaticGroundFunction: ...

    @overload
    def __getitem__(self, arg: slice, /) -> StaticGroundFunctionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: StaticGroundFunction, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: StaticGroundFunction, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> StaticGroundFunction:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: StaticGroundFunctionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: StaticGroundFunction, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: StaticGroundFunctionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: StaticGroundFunction, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: StaticGroundFunction, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: StaticGroundFunction, /) -> None:
        """Remove first occurrence of `arg`."""

class FluentGroundFunction:
    def __hash__(self) -> int: ...

    def __eq__(self, arg: FluentGroundFunction, /) -> bool: ...

    def __ne__(self, arg: FluentGroundFunction, /) -> bool: ...

    def __str__(self) -> str: ...

    def get_index(self) -> int: ...

    def get_function_skeleton(self) -> FluentFunctionSkeleton: ...

    def get_objects(self) -> ObjectList: ...

class FluentGroundFunctionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FluentGroundFunctionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[FluentGroundFunction], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[FluentGroundFunction]: ...

    @overload
    def __getitem__(self, arg: int, /) -> FluentGroundFunction: ...

    @overload
    def __getitem__(self, arg: slice, /) -> FluentGroundFunctionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: FluentGroundFunction, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: FluentGroundFunction, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> FluentGroundFunction:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: FluentGroundFunctionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: FluentGroundFunction, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: FluentGroundFunctionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: FluentGroundFunction, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: FluentGroundFunction, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: FluentGroundFunction, /) -> None:
        """Remove first occurrence of `arg`."""

class AuxiliaryGroundFunction:
    def __hash__(self) -> int: ...

    def __eq__(self, arg: AuxiliaryGroundFunction, /) -> bool: ...

    def __ne__(self, arg: AuxiliaryGroundFunction, /) -> bool: ...

    def __str__(self) -> str: ...

    def get_index(self) -> int: ...

    def get_function_skeleton(self) -> AuxiliaryFunctionSkeleton: ...

    def get_objects(self) -> ObjectList: ...

class AuxiliaryGroundFunctionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: AuxiliaryGroundFunctionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[AuxiliaryGroundFunction], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[AuxiliaryGroundFunction]: ...

    @overload
    def __getitem__(self, arg: int, /) -> AuxiliaryGroundFunction: ...

    @overload
    def __getitem__(self, arg: slice, /) -> AuxiliaryGroundFunctionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: AuxiliaryGroundFunction, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: AuxiliaryGroundFunction, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> AuxiliaryGroundFunction:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: AuxiliaryGroundFunctionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: AuxiliaryGroundFunction, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: AuxiliaryGroundFunctionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: AuxiliaryGroundFunction, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: AuxiliaryGroundFunction, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: AuxiliaryGroundFunction, /) -> None:
        """Remove first occurrence of `arg`."""

class StaticGroundAtom:
    def __str__(self) -> str: ...

    def __eq__(self, arg: StaticGroundAtom, /) -> bool: ...

    def __ne__(self, arg: StaticGroundAtom, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_arity(self) -> int: ...

    def get_predicate(self) -> StaticPredicate: ...

    def get_objects(self) -> ObjectList: ...

class StaticGroundAtomList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: StaticGroundAtomList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[StaticGroundAtom], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[StaticGroundAtom]: ...

    @overload
    def __getitem__(self, arg: int, /) -> StaticGroundAtom: ...

    @overload
    def __getitem__(self, arg: slice, /) -> StaticGroundAtomList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: StaticGroundAtom, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: StaticGroundAtom, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> StaticGroundAtom:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: StaticGroundAtomList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: StaticGroundAtom, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: StaticGroundAtomList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: StaticGroundAtom, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: StaticGroundAtom, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: StaticGroundAtom, /) -> None:
        """Remove first occurrence of `arg`."""

class FluentGroundAtom:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentGroundAtom, /) -> bool: ...

    def __ne__(self, arg: FluentGroundAtom, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_arity(self) -> int: ...

    def get_predicate(self) -> FluentPredicate: ...

    def get_objects(self) -> ObjectList: ...

class FluentGroundAtomList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FluentGroundAtomList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[FluentGroundAtom], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[FluentGroundAtom]: ...

    @overload
    def __getitem__(self, arg: int, /) -> FluentGroundAtom: ...

    @overload
    def __getitem__(self, arg: slice, /) -> FluentGroundAtomList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: FluentGroundAtom, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: FluentGroundAtom, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> FluentGroundAtom:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: FluentGroundAtomList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: FluentGroundAtom, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: FluentGroundAtomList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: FluentGroundAtom, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: FluentGroundAtom, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: FluentGroundAtom, /) -> None:
        """Remove first occurrence of `arg`."""

class DerivedGroundAtom:
    def __str__(self) -> str: ...

    def __eq__(self, arg: DerivedGroundAtom, /) -> bool: ...

    def __ne__(self, arg: DerivedGroundAtom, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_arity(self) -> int: ...

    def get_predicate(self) -> DerivedPredicate: ...

    def get_objects(self) -> ObjectList: ...

class DerivedGroundAtomList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: DerivedGroundAtomList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[DerivedGroundAtom], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[DerivedGroundAtom]: ...

    @overload
    def __getitem__(self, arg: int, /) -> DerivedGroundAtom: ...

    @overload
    def __getitem__(self, arg: slice, /) -> DerivedGroundAtomList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: DerivedGroundAtom, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: DerivedGroundAtom, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> DerivedGroundAtom:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: DerivedGroundAtomList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: DerivedGroundAtom, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: DerivedGroundAtomList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: DerivedGroundAtom, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: DerivedGroundAtom, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: DerivedGroundAtom, /) -> None:
        """Remove first occurrence of `arg`."""

class StaticGroundLiteral:
    def __str__(self) -> str: ...

    def __eq__(self, arg: StaticGroundLiteral, /) -> bool: ...

    def __ne__(self, arg: StaticGroundLiteral, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_atom(self) -> StaticGroundAtom: ...

    def get_polarity(self) -> bool: ...

class StaticGroundLiteralList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: StaticGroundLiteralList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[StaticGroundLiteral], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[StaticGroundLiteral]: ...

    @overload
    def __getitem__(self, arg: int, /) -> StaticGroundLiteral: ...

    @overload
    def __getitem__(self, arg: slice, /) -> StaticGroundLiteralList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: StaticGroundLiteral, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: StaticGroundLiteral, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> StaticGroundLiteral:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: StaticGroundLiteralList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: StaticGroundLiteral, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: StaticGroundLiteralList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: StaticGroundLiteral, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: StaticGroundLiteral, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: StaticGroundLiteral, /) -> None:
        """Remove first occurrence of `arg`."""

class FluentGroundLiteral:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentGroundLiteral, /) -> bool: ...

    def __ne__(self, arg: FluentGroundLiteral, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_atom(self) -> FluentGroundAtom: ...

    def get_polarity(self) -> bool: ...

class FluentGroundLiteralList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FluentGroundLiteralList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[FluentGroundLiteral], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[FluentGroundLiteral]: ...

    @overload
    def __getitem__(self, arg: int, /) -> FluentGroundLiteral: ...

    @overload
    def __getitem__(self, arg: slice, /) -> FluentGroundLiteralList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: FluentGroundLiteral, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: FluentGroundLiteral, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> FluentGroundLiteral:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: FluentGroundLiteralList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: FluentGroundLiteral, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: FluentGroundLiteralList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: FluentGroundLiteral, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: FluentGroundLiteral, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: FluentGroundLiteral, /) -> None:
        """Remove first occurrence of `arg`."""

class DerivedGroundLiteral:
    def __str__(self) -> str: ...

    def __eq__(self, arg: DerivedGroundLiteral, /) -> bool: ...

    def __ne__(self, arg: DerivedGroundLiteral, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_atom(self) -> DerivedGroundAtom: ...

    def get_polarity(self) -> bool: ...

class DerivedGroundLiteralList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: DerivedGroundLiteralList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[DerivedGroundLiteral], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[DerivedGroundLiteral]: ...

    @overload
    def __getitem__(self, arg: int, /) -> DerivedGroundLiteral: ...

    @overload
    def __getitem__(self, arg: slice, /) -> DerivedGroundLiteralList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: DerivedGroundLiteral, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: DerivedGroundLiteral, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> DerivedGroundLiteral:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: DerivedGroundLiteralList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: DerivedGroundLiteral, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: DerivedGroundLiteralList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: DerivedGroundLiteral, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: DerivedGroundLiteral, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: DerivedGroundLiteral, /) -> None:
        """Remove first occurrence of `arg`."""

class StaticLiteral:
    def __str__(self) -> str: ...

    def __eq__(self, arg: StaticLiteral, /) -> bool: ...

    def __ne__(self, arg: StaticLiteral, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_atom(self) -> StaticAtom: ...

    def get_polarity(self) -> bool: ...

class StaticLiteralList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: StaticLiteralList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[StaticLiteral], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[StaticLiteral]: ...

    @overload
    def __getitem__(self, arg: int, /) -> StaticLiteral: ...

    @overload
    def __getitem__(self, arg: slice, /) -> StaticLiteralList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: StaticLiteral, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: StaticLiteral, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> StaticLiteral:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: StaticLiteralList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: StaticLiteral, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: StaticLiteralList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: StaticLiteral, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: StaticLiteral, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: StaticLiteral, /) -> None:
        """Remove first occurrence of `arg`."""

class FluentLiteral:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentLiteral, /) -> bool: ...

    def __ne__(self, arg: FluentLiteral, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_atom(self) -> FluentAtom: ...

    def get_polarity(self) -> bool: ...

class FluentLiteralList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FluentLiteralList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[FluentLiteral], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[FluentLiteral]: ...

    @overload
    def __getitem__(self, arg: int, /) -> FluentLiteral: ...

    @overload
    def __getitem__(self, arg: slice, /) -> FluentLiteralList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: FluentLiteral, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: FluentLiteral, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> FluentLiteral:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: FluentLiteralList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: FluentLiteral, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: FluentLiteralList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: FluentLiteral, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: FluentLiteral, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: FluentLiteral, /) -> None:
        """Remove first occurrence of `arg`."""

class DerivedLiteral:
    def __str__(self) -> str: ...

    def __eq__(self, arg: DerivedLiteral, /) -> bool: ...

    def __ne__(self, arg: DerivedLiteral, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_atom(self) -> DerivedAtom: ...

    def get_polarity(self) -> bool: ...

class DerivedLiteralList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: DerivedLiteralList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[DerivedLiteral], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[DerivedLiteral]: ...

    @overload
    def __getitem__(self, arg: int, /) -> DerivedLiteral: ...

    @overload
    def __getitem__(self, arg: slice, /) -> DerivedLiteralList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: DerivedLiteral, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: DerivedLiteral, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> DerivedLiteral:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: DerivedLiteralList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: DerivedLiteral, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: DerivedLiteralList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: DerivedLiteral, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: DerivedLiteral, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: DerivedLiteral, /) -> None:
        """Remove first occurrence of `arg`."""

class StaticGroundFunctionValue:
    def __str__(self) -> str: ...

    def __eq__(self, arg: StaticGroundFunctionValue, /) -> bool: ...

    def __ne__(self, arg: StaticGroundFunctionValue, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function(self) -> StaticGroundFunction: ...

    def get_number(self) -> float: ...

class StaticGroundFunctionValueList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: StaticGroundFunctionValueList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[StaticGroundFunctionValue], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[StaticGroundFunctionValue]: ...

    @overload
    def __getitem__(self, arg: int, /) -> StaticGroundFunctionValue: ...

    @overload
    def __getitem__(self, arg: slice, /) -> StaticGroundFunctionValueList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: StaticGroundFunctionValue, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: StaticGroundFunctionValue, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> StaticGroundFunctionValue:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: StaticGroundFunctionValueList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: StaticGroundFunctionValue, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: StaticGroundFunctionValueList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: StaticGroundFunctionValue, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: StaticGroundFunctionValue, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: StaticGroundFunctionValue, /) -> None:
        """Remove first occurrence of `arg`."""

class FluentGroundFunctionValue:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentGroundFunctionValue, /) -> bool: ...

    def __ne__(self, arg: FluentGroundFunctionValue, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function(self) -> FluentGroundFunction: ...

    def get_number(self) -> float: ...

class FluentGroundFunctionValueList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FluentGroundFunctionValueList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[FluentGroundFunctionValue], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[FluentGroundFunctionValue]: ...

    @overload
    def __getitem__(self, arg: int, /) -> FluentGroundFunctionValue: ...

    @overload
    def __getitem__(self, arg: slice, /) -> FluentGroundFunctionValueList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: FluentGroundFunctionValue, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: FluentGroundFunctionValue, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> FluentGroundFunctionValue:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: FluentGroundFunctionValueList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: FluentGroundFunctionValue, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: FluentGroundFunctionValueList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: FluentGroundFunctionValue, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: FluentGroundFunctionValue, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: FluentGroundFunctionValue, /) -> None:
        """Remove first occurrence of `arg`."""

class AuxiliaryGroundFunctionValue:
    def __str__(self) -> str: ...

    def __eq__(self, arg: AuxiliaryGroundFunctionValue, /) -> bool: ...

    def __ne__(self, arg: AuxiliaryGroundFunctionValue, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function(self) -> AuxiliaryGroundFunction: ...

    def get_number(self) -> float: ...

class AuxiliaryGroundFunctionValueList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: AuxiliaryGroundFunctionValueList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[AuxiliaryGroundFunctionValue], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[AuxiliaryGroundFunctionValue]: ...

    @overload
    def __getitem__(self, arg: int, /) -> AuxiliaryGroundFunctionValue: ...

    @overload
    def __getitem__(self, arg: slice, /) -> AuxiliaryGroundFunctionValueList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: AuxiliaryGroundFunctionValue, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: AuxiliaryGroundFunctionValue, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> AuxiliaryGroundFunctionValue:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: AuxiliaryGroundFunctionValueList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: AuxiliaryGroundFunctionValue, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: AuxiliaryGroundFunctionValueList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: AuxiliaryGroundFunctionValue, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: AuxiliaryGroundFunctionValue, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: AuxiliaryGroundFunctionValue, /) -> None:
        """Remove first occurrence of `arg`."""

class FunctionExpression:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FunctionExpression, /) -> bool: ...

    def __ne__(self, arg: FunctionExpression, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get(self) -> object: ...

class FunctionExpressionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: FunctionExpressionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[FunctionExpression], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[FunctionExpression]: ...

    @overload
    def __getitem__(self, arg: int, /) -> FunctionExpression: ...

    @overload
    def __getitem__(self, arg: slice, /) -> FunctionExpressionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: FunctionExpression, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: FunctionExpression, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> FunctionExpression:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: FunctionExpressionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: FunctionExpression, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: FunctionExpressionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: FunctionExpression, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: FunctionExpression, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: FunctionExpression, /) -> None:
        """Remove first occurrence of `arg`."""

class FunctionExpressionNumber:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FunctionExpressionNumber, /) -> bool: ...

    def __ne__(self, arg: FunctionExpressionNumber, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_number(self) -> float: ...

class FunctionExpressionBinaryOperator:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FunctionExpressionBinaryOperator, /) -> bool: ...

    def __ne__(self, arg: FunctionExpressionBinaryOperator, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_binary_operator(self) -> BinaryOperatorEnum: ...

    def get_left_function_expression(self) -> FunctionExpression: ...

    def get_right_function_expression(self) -> FunctionExpression: ...

class FunctionExpressionMultiOperator:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FunctionExpressionMultiOperator, /) -> bool: ...

    def __ne__(self, arg: FunctionExpressionMultiOperator, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_multi_operator(self) -> MultiOperatorEnum: ...

    def get_function_expressions(self) -> FunctionExpressionList: ...

class FunctionExpressionMinus:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FunctionExpressionMinus, /) -> bool: ...

    def __ne__(self, arg: FunctionExpressionMinus, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function_expression(self) -> FunctionExpression: ...

class StaticFunctionExpressionFunction:
    def __str__(self) -> str: ...

    def __eq__(self, arg: StaticFunctionExpressionFunction, /) -> bool: ...

    def __ne__(self, arg: StaticFunctionExpressionFunction, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function(self) -> StaticFunction: ...

class FluentFunctionExpressionFunction:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentFunctionExpressionFunction, /) -> bool: ...

    def __ne__(self, arg: FluentFunctionExpressionFunction, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function(self) -> FluentFunction: ...

class AuxiliaryFunctionExpressionFunction:
    def __str__(self) -> str: ...

    def __eq__(self, arg: AuxiliaryFunctionExpressionFunction, /) -> bool: ...

    def __ne__(self, arg: AuxiliaryFunctionExpressionFunction, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function(self) -> AuxiliaryFunction: ...

class FluentNumericEffect:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentNumericEffect, /) -> bool: ...

    def __ne__(self, arg: FluentNumericEffect, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_assign_operator(self) -> AssignOperatorEnum: ...

    def get_function(self) -> FluentFunction: ...

    def get_function_expression(self) -> FunctionExpression: ...

class AuxiliaryNumericEffect:
    def __str__(self) -> str: ...

    def __eq__(self, arg: AuxiliaryNumericEffect, /) -> bool: ...

    def __ne__(self, arg: AuxiliaryNumericEffect, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_assign_operator(self) -> AssignOperatorEnum: ...

    def get_function(self) -> AuxiliaryFunction: ...

    def get_function_expression(self) -> FunctionExpression: ...

class NumericConstraint:
    def __str__(self) -> str: ...

    def __eq__(self, arg: NumericConstraint, /) -> bool: ...

    def __ne__(self, arg: NumericConstraint, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_binary_comparator(self) -> BinaryComparatorEnum: ...

    def get_left_function_expression(self) -> FunctionExpression: ...

    def get_right_function_expression(self) -> FunctionExpression: ...

class NumericConstraintList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: NumericConstraintList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[NumericConstraint], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[NumericConstraint]: ...

    @overload
    def __getitem__(self, arg: int, /) -> NumericConstraint: ...

    @overload
    def __getitem__(self, arg: slice, /) -> NumericConstraintList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: NumericConstraint, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: NumericConstraint, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> NumericConstraint:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: NumericConstraintList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: NumericConstraint, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: NumericConstraintList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: NumericConstraint, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: NumericConstraint, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: NumericConstraint, /) -> None:
        """Remove first occurrence of `arg`."""

class ConjunctiveCondition:
    def __str__(self) -> str: ...

    def __eq__(self, arg: ConjunctiveCondition, /) -> bool: ...

    def __ne__(self, arg: ConjunctiveCondition, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_parameters(self) -> VariableList: ...

    def get_static_literals(self) -> StaticLiteralList: ...

    def get_fluent_literals(self) -> FluentLiteralList: ...

    def get_derived_literals(self) -> DerivedLiteralList: ...

    def get_nullary_ground_static_literals(self) -> StaticGroundLiteralList: ...

    def get_nullary_ground_fluent_literals(self) -> FluentGroundLiteralList: ...

    def get_nullary_ground_derived_literals(self) -> DerivedGroundLiteralList: ...

    def get_numeric_constraints(self) -> NumericConstraintList: ...

class ConjunctiveEffect:
    def __str__(self) -> str: ...

    def __eq__(self, arg: ConjunctiveEffect, /) -> bool: ...

    def __ne__(self, arg: ConjunctiveEffect, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_parameters(self) -> VariableList: ...

    def get_literals(self) -> FluentLiteralList: ...

    def get_fluent_numeric_effects(self) -> list[FluentNumericEffect]: ...

    def get_auxiliary_numeric_effect(self) -> AuxiliaryNumericEffect | None: ...

class ConditionalEffect:
    def __str__(self) -> str: ...

    def __eq__(self, arg: ConditionalEffect, /) -> bool: ...

    def __ne__(self, arg: ConditionalEffect, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_conjunctive_condition(self) -> ConjunctiveCondition: ...

    def get_conjunctive_effect(self) -> ConjunctiveEffect: ...

class ConditionalEffectList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ConditionalEffectList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[ConditionalEffect], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[ConditionalEffect]: ...

    @overload
    def __getitem__(self, arg: int, /) -> ConditionalEffect: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ConditionalEffectList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: ConditionalEffect, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: ConditionalEffect, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> ConditionalEffect:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ConditionalEffectList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: ConditionalEffect, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ConditionalEffectList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: ConditionalEffect, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: ConditionalEffect, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: ConditionalEffect, /) -> None:
        """Remove first occurrence of `arg`."""

class Action:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Action, /) -> bool: ...

    def __ne__(self, arg: Action, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_parameters(self) -> VariableList: ...

    def get_conjunctive_condition(self) -> ConjunctiveCondition: ...

    def get_conditional_effects(self) -> ConditionalEffectList: ...

    def get_arity(self) -> int: ...

class ActionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ActionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Action], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Action]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Action: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ActionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Action, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Action, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Action:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ActionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Action, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ActionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Action, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Action, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Action, /) -> None:
        """Remove first occurrence of `arg`."""

class Axiom:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Axiom, /) -> bool: ...

    def __ne__(self, arg: Axiom, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_conjunctive_condition(self) -> ConjunctiveCondition: ...

    def get_literal(self) -> DerivedLiteral: ...

    def get_arity(self) -> int: ...

class AxiomList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: AxiomList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Axiom], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Axiom]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Axiom: ...

    @overload
    def __getitem__(self, arg: slice, /) -> AxiomList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Axiom, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Axiom, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Axiom:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: AxiomList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Axiom, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: AxiomList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Axiom, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Axiom, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Axiom, /) -> None:
        """Remove first occurrence of `arg`."""

class GroundFunctionExpression:
    def __str__(self) -> str: ...

    def __eq__(self, arg: GroundFunctionExpression, /) -> bool: ...

    def __ne__(self, arg: GroundFunctionExpression, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get(self) -> object: ...

class GroundFunctionExpressionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: GroundFunctionExpressionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[GroundFunctionExpression], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[GroundFunctionExpression]: ...

    @overload
    def __getitem__(self, arg: int, /) -> GroundFunctionExpression: ...

    @overload
    def __getitem__(self, arg: slice, /) -> GroundFunctionExpressionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: GroundFunctionExpression, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: GroundFunctionExpression, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> GroundFunctionExpression:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: GroundFunctionExpressionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: GroundFunctionExpression, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: GroundFunctionExpressionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: GroundFunctionExpression, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: GroundFunctionExpression, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: GroundFunctionExpression, /) -> None:
        """Remove first occurrence of `arg`."""

class GroundFunctionExpressionNumber:
    def __str__(self) -> str: ...

    def __eq__(self, arg: GroundFunctionExpressionNumber, /) -> bool: ...

    def __ne__(self, arg: GroundFunctionExpressionNumber, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_number(self) -> float: ...

class GroundFunctionExpressionBinaryOperator:
    def __str__(self) -> str: ...

    def __eq__(self, arg: GroundFunctionExpressionBinaryOperator, /) -> bool: ...

    def __ne__(self, arg: GroundFunctionExpressionBinaryOperator, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_binary_operator(self) -> BinaryOperatorEnum: ...

    def get_left_function_expression(self) -> GroundFunctionExpression: ...

    def get_right_function_expression(self) -> GroundFunctionExpression: ...

class GroundFunctionExpressionMultiOperator:
    def __str__(self) -> str: ...

    def __eq__(self, arg: GroundFunctionExpressionMultiOperator, /) -> bool: ...

    def __ne__(self, arg: GroundFunctionExpressionMultiOperator, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_multi_operator(self) -> MultiOperatorEnum: ...

    def get_function_expressions(self) -> GroundFunctionExpressionList: ...

class GroundFunctionExpressionMinus:
    def __str__(self) -> str: ...

    def __eq__(self, arg: GroundFunctionExpressionMinus, /) -> bool: ...

    def __ne__(self, arg: GroundFunctionExpressionMinus, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function_expression(self) -> GroundFunctionExpression: ...

class StaticGroundFunctionExpressionFunction:
    def __str__(self) -> str: ...

    def __eq__(self, arg: StaticGroundFunctionExpressionFunction, /) -> bool: ...

    def __ne__(self, arg: StaticGroundFunctionExpressionFunction, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function(self) -> StaticGroundFunction: ...

class FluentGroundFunctionExpressionFunction:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentGroundFunctionExpressionFunction, /) -> bool: ...

    def __ne__(self, arg: FluentGroundFunctionExpressionFunction, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function(self) -> FluentGroundFunction: ...

class AuxiliaryGroundFunctionExpressionFunction:
    def __str__(self) -> str: ...

    def __eq__(self, arg: AuxiliaryGroundFunctionExpressionFunction, /) -> bool: ...

    def __ne__(self, arg: AuxiliaryGroundFunctionExpressionFunction, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function(self) -> AuxiliaryGroundFunction: ...

class OptimizationMetric:
    def __str__(self) -> str: ...

    def __eq__(self, arg: OptimizationMetric, /) -> bool: ...

    def __ne__(self, arg: OptimizationMetric, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_function_expression(self) -> GroundFunctionExpression: ...

    def get_optimization_metric(self) -> OptimizationMetricEnum: ...

class FluentGroundNumericEffect:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FluentGroundNumericEffect, /) -> bool: ...

    def __ne__(self, arg: FluentGroundNumericEffect, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_assign_operator(self) -> AssignOperatorEnum: ...

    def get_function(self) -> FluentGroundFunction: ...

    def get_function_expression(self) -> GroundFunctionExpression: ...

class AuxiliaryGroundNumericEffect:
    def __str__(self) -> str: ...

    def __eq__(self, arg: AuxiliaryGroundNumericEffect, /) -> bool: ...

    def __ne__(self, arg: AuxiliaryGroundNumericEffect, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_assign_operator(self) -> AssignOperatorEnum: ...

    def get_function(self) -> AuxiliaryGroundFunction: ...

    def get_function_expression(self) -> GroundFunctionExpression: ...

class GroundNumericConstraint:
    def __str__(self) -> str: ...

    def __eq__(self, arg: GroundNumericConstraint, /) -> bool: ...

    def __ne__(self, arg: GroundNumericConstraint, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_binary_comparator(self) -> BinaryComparatorEnum: ...

    def get_left_function_expression(self) -> GroundFunctionExpression: ...

    def get_right_function_expression(self) -> GroundFunctionExpression: ...

class GroundNumericConstraintList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: GroundNumericConstraintList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[GroundNumericConstraint], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[GroundNumericConstraint]: ...

    @overload
    def __getitem__(self, arg: int, /) -> GroundNumericConstraint: ...

    @overload
    def __getitem__(self, arg: slice, /) -> GroundNumericConstraintList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: GroundNumericConstraint, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: GroundNumericConstraint, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> GroundNumericConstraint:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: GroundNumericConstraintList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: GroundNumericConstraint, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: GroundNumericConstraintList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: GroundNumericConstraint, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: GroundNumericConstraint, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: GroundNumericConstraint, /) -> None:
        """Remove first occurrence of `arg`."""

class GroundConjunctiveCondition:
    def to_string(self, arg: Problem, /) -> str: ...

    def __eq__(self, arg: GroundConjunctiveCondition, /) -> bool: ...

    def __ne__(self, arg: GroundConjunctiveCondition, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_static_positive_condition(self) -> Iterator[int]: ...

    def get_fluent_positive_condition(self) -> Iterator[int]: ...

    def get_derived_positive_condition(self) -> Iterator[int]: ...

    def get_static_negative_condition(self) -> Iterator[int]: ...

    def get_fluent_negative_condition(self) -> Iterator[int]: ...

    def get_derived_negative_condition(self) -> Iterator[int]: ...

class GroundConjunctiveEffect:
    def to_string(self, arg: Problem, /) -> str: ...

    def __eq__(self, arg: GroundConjunctiveEffect, /) -> bool: ...

    def __ne__(self, arg: GroundConjunctiveEffect, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_positive_effects(self) -> Iterator[int]: ...

    def get_negative_effects(self) -> Iterator[int]: ...

    def get_fluent_numeric_effects(self) -> list[FluentGroundNumericEffect]: ...

    def get_auxiliary_numeric_effect(self) -> AuxiliaryGroundNumericEffect | None: ...

class GroundConditionalEffect:
    def to_string(self, arg: Problem, /) -> str: ...

    def __eq__(self, arg: GroundConditionalEffect, /) -> bool: ...

    def __ne__(self, arg: GroundConditionalEffect, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_conjunctive_condition(self) -> GroundConjunctiveCondition: ...

    def get_conjunctive_effect(self) -> GroundConjunctiveEffect: ...

class GroundConditionalEffectList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: GroundConditionalEffectList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[GroundConditionalEffect], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[GroundConditionalEffect]: ...

    @overload
    def __getitem__(self, arg: int, /) -> GroundConditionalEffect: ...

    @overload
    def __getitem__(self, arg: slice, /) -> GroundConditionalEffectList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: GroundConditionalEffect, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: GroundConditionalEffect, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> GroundConditionalEffect:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: GroundConditionalEffectList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: GroundConditionalEffect, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: GroundConditionalEffectList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: GroundConditionalEffect, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: GroundConditionalEffect, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: GroundConditionalEffect, /) -> None:
        """Remove first occurrence of `arg`."""

class GroundAction:
    def to_string(self, arg: Problem, /) -> str: ...

    def __eq__(self, arg: GroundAction, /) -> bool: ...

    def __ne__(self, arg: GroundAction, /) -> bool: ...

    def __hash__(self) -> int: ...

    def to_string_for_plan(self, arg: Problem, /) -> str: ...

    def get_index(self) -> int: ...

    def get_action(self) -> Action: ...

    def get_objects(self) -> ObjectList: ...

    def get_conjunctive_condition(self) -> GroundConjunctiveCondition: ...

    def get_conditional_effects(self) -> GroundConditionalEffectList: ...

class GroundActionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: GroundActionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[GroundAction], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[GroundAction]: ...

    @overload
    def __getitem__(self, arg: int, /) -> GroundAction: ...

    @overload
    def __getitem__(self, arg: slice, /) -> GroundActionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: GroundAction, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: GroundAction, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> GroundAction:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: GroundActionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: GroundAction, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: GroundActionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: GroundAction, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: GroundAction, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: GroundAction, /) -> None:
        """Remove first occurrence of `arg`."""

class GroundAxiom:
    def to_string(self, arg: Problem, /) -> str: ...

    def __eq__(self, arg: GroundAxiom, /) -> bool: ...

    def __ne__(self, arg: GroundAxiom, /) -> bool: ...

    def __hash__(self) -> int: ...

    def get_index(self) -> int: ...

    def get_axiom(self) -> Axiom: ...

    def get_objects(self) -> ObjectList: ...

    def get_conjunctive_condition(self) -> GroundConjunctiveCondition: ...

    def get_literal(self) -> DerivedGroundLiteral: ...

class GroundAxiomList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: GroundAxiomList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[GroundAxiom], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[GroundAxiom]: ...

    @overload
    def __getitem__(self, arg: int, /) -> GroundAxiom: ...

    @overload
    def __getitem__(self, arg: slice, /) -> GroundAxiomList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: GroundAxiom, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: GroundAxiom, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> GroundAxiom:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: GroundAxiomList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: GroundAxiom, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: GroundAxiomList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: GroundAxiom, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: GroundAxiom, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: GroundAxiom, /) -> None:
        """Remove first occurrence of `arg`."""

class Repositories:
    def get_static_ground_atoms(self) -> StaticGroundAtomList: ...

    def get_static_ground_atom(self, arg: int, /) -> StaticGroundAtom: ...

    def get_fluent_ground_atoms(self) -> FluentGroundAtomList: ...

    def get_fluent_ground_atom(self, arg: int, /) -> FluentGroundAtom: ...

    def get_derived_ground_atoms(self) -> DerivedGroundAtomList: ...

    def get_derived_ground_atom(self, arg: int, /) -> DerivedGroundAtom: ...

    def get_static_ground_atoms_from_indices(self, arg: Sequence[int], /) -> StaticGroundAtomList: ...

    def get_fluent_ground_atoms_from_indices(self, arg: Sequence[int], /) -> FluentGroundAtomList: ...

    def get_derived_ground_atoms_from_indices(self, arg: Sequence[int], /) -> DerivedGroundAtomList: ...

    def get_object(self, arg: int, /) -> Object: ...

class StaticAssignmentSet:
    def __init__(self, num_objects: int, predicates: StaticPredicateList) -> None: ...

    def reset(self) -> None: ...

    def insert_ground_atoms(self, ground_atoms: StaticGroundAtomList) -> None: ...

    def insert_ground_atom(self, ground_atom: StaticGroundAtomList) -> None: ...

class FluentAssignmentSet:
    def __init__(self, num_objects: int, predicates: FluentPredicateList) -> None: ...

    def reset(self) -> None: ...

    def insert_ground_atoms(self, ground_atoms: FluentGroundAtomList) -> None: ...

    def insert_ground_atom(self, ground_atom: FluentGroundAtomList) -> None: ...

class DerivedAssignmentSet:
    def __init__(self, num_objects: int, predicates: DerivedPredicateList) -> None: ...

    def reset(self) -> None: ...

    def insert_ground_atoms(self, ground_atoms: DerivedGroundAtomList) -> None: ...

    def insert_ground_atom(self, ground_atom: DerivedGroundAtomList) -> None: ...

class StaticNumericAssignmentSet:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, num_objects: int, function_skeletons: StaticFunctionSkeletonList) -> None: ...

    def reset(self) -> None: ...

    def insert_ground_function_values(self, ground_functions: StaticGroundFunctionList, numeric_values: pymimir.advanced.common.FlatDoubleList) -> None: ...

class FluentNumericAssignmentSet:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, num_objects: int, function_skeletons: FluentFunctionSkeletonList) -> None: ...

    def reset(self) -> None: ...

    def insert_ground_function_values(self, ground_functions: FluentGroundFunctionList, numeric_values: pymimir.advanced.common.FlatDoubleList) -> None: ...

class Domain:
    def __str__(self) -> str: ...

    def get_repositories(self) -> Repositories: ...

    def get_filepath(self) -> pathlib.Path | None: ...

    def get_name(self) -> str: ...

    def get_constants(self) -> ObjectList: ...

    def get_static_predicates(self) -> StaticPredicateList: ...

    def get_fluent_predicates(self) -> FluentPredicateList: ...

    def get_derived_predicates(self) -> DerivedPredicateList: ...

    def get_static_functions(self) -> StaticFunctionSkeletonList: ...

    def get_fluent_functions(self) -> FluentFunctionSkeletonList: ...

    def get_auxiliary_function(self) -> AuxiliaryFunctionSkeleton | None: ...

    def get_actions(self) -> ActionList: ...

    def get_requirements(self) -> Requirements: ...

    def get_constant(self, arg: str, /) -> Object: ...

    def get_name_to_constant(self) -> dict[str, Object]: ...

    def get_static_predicate(self, arg: str, /) -> StaticPredicate: ...

    def get_fluent_predicate(self, arg: str, /) -> FluentPredicate: ...

    def get_derived_predicate(self, arg: str, /) -> DerivedPredicate: ...

    def get_name_to_static_predicate(self) -> StaticPredicateMap: ...

    def get_name_to_fluent_predicate(self) -> FluentPredicateMap: ...

    def get_name_to_derived_predicate(self) -> DerivedPredicateMap: ...

class Problem:
    @staticmethod
    def create(domain_filepath: str | os.PathLike, problem_filepath: str | os.PathLike, options: ParserOptions) -> Problem: ...

    def __str__(self) -> str: ...

    def get_index(self) -> int: ...

    def get_repositories(self) -> Repositories: ...

    def get_filepath(self) -> pathlib.Path | None: ...

    def get_name(self) -> str: ...

    def get_domain(self) -> Domain: ...

    def get_requirements(self) -> Requirements: ...

    def get_objects(self) -> ObjectList: ...

    def get_problem_and_domain_objects(self) -> ObjectList: ...

    def get_problem_and_domain_derived_predicates(self) -> DerivedPredicateList: ...

    def get_object(self, arg: str, /) -> Object: ...

    def get_problem_or_domain_object(self, arg: str, /) -> Object: ...

    @overload
    def get_name_to_object(self) -> dict[str, Object]: ...

    @overload
    def get_name_to_object(self) -> dict[str, Object]: ...

    def get_derived_predicate(self, arg: str, /) -> DerivedPredicate: ...

    def get_problem_or_domain_derived_predicate(self, arg: str, /) -> DerivedPredicate: ...

    def get_name_to_derived_predicate(self) -> DerivedPredicateMap: ...

    def get_name_to_problem_or_domain_derived_predicate(self) -> DerivedPredicateMap: ...

    def get_static_initial_literals(self) -> StaticGroundLiteralList: ...

    def get_fluent_initial_literals(self) -> FluentGroundLiteralList: ...

    def get_static_function_values(self) -> StaticGroundFunctionValueList: ...

    def get_fluent_function_values(self) -> FluentGroundFunctionValueList: ...

    def get_auxiliary_function_value(self) -> AuxiliaryGroundFunctionValue | None: ...

    def get_optimization_metric(self) -> OptimizationMetric | None: ...

    def get_static_goal_condition(self) -> StaticGroundLiteralList: ...

    def get_fluent_goal_condition(self) -> FluentGroundLiteralList: ...

    def get_derived_goal_condition(self) -> DerivedGroundLiteralList: ...

    def get_numeric_goal_condition(self) -> GroundNumericConstraintList: ...

    def get_static_initial_atoms(self) -> StaticGroundAtomList: ...

    def get_fluent_initial_atoms(self) -> FluentGroundAtomList: ...

    def get_static_assignment_set(self) -> StaticAssignmentSet: ...

    @overload
    def ground(self, action: Action, binding: ObjectList) -> GroundAction: ...

    @overload
    def ground(self, function_expression: FunctionExpression, binding: ObjectList) -> GroundFunctionExpression: ...

    @overload
    def ground(self, numeric_constraint: NumericConstraint, binding: ObjectList) -> GroundNumericConstraint: ...

    @overload
    def ground(self, literal: StaticLiteral, binding: ObjectList) -> StaticGroundLiteral: ...

    @overload
    def ground(self, literal: FluentLiteral, binding: ObjectList) -> FluentGroundLiteral: ...

    @overload
    def ground(self, literal: DerivedLiteral, binding: ObjectList) -> DerivedGroundLiteral: ...

    @overload
    def ground(self, numeric_effect: FluentNumericEffect, binding: ObjectList) -> FluentGroundNumericEffect: ...

    @overload
    def ground(self, numeric_effect: AuxiliaryNumericEffect, binding: ObjectList) -> AuxiliaryGroundNumericEffect: ...

    @overload
    def ground(self, function: StaticFunction, binding: ObjectList) -> StaticGroundFunction: ...

    @overload
    def ground(self, function: FluentFunction, binding: ObjectList) -> FluentGroundFunction: ...

    @overload
    def ground(self, function: AuxiliaryFunction, binding: ObjectList) -> AuxiliaryGroundFunction: ...

    @overload
    def get_or_create_ground_atom(self, predicate: StaticPredicate, binding: ObjectList) -> StaticGroundAtom: ...

    @overload
    def get_or_create_ground_atom(self, predicate: FluentPredicate, binding: ObjectList) -> FluentGroundAtom: ...

    @overload
    def get_or_create_ground_atom(self, predicate: DerivedPredicate, binding: ObjectList) -> DerivedGroundAtom: ...

    def get_or_create_variable(self, name: str, parameter_index: int) -> Variable: ...

    @overload
    def get_or_create_term(self, variable: Variable) -> Term: ...

    @overload
    def get_or_create_term(self, object: Object) -> Term: ...

    @overload
    def get_or_create_atom(self, predicate: StaticPredicate, terms: TermList) -> StaticAtom: ...

    @overload
    def get_or_create_atom(self, predicate: FluentPredicate, terms: TermList) -> FluentAtom: ...

    @overload
    def get_or_create_atom(self, predicate: DerivedPredicate, terms: TermList) -> DerivedAtom: ...

    @overload
    def get_or_create_literal(self, polarity: bool, atom: StaticAtom) -> StaticLiteral: ...

    @overload
    def get_or_create_literal(self, polarity: bool, atom: FluentAtom) -> FluentLiteral: ...

    @overload
    def get_or_create_literal(self, polarity: bool, atom: DerivedAtom) -> DerivedLiteral: ...

    @overload
    def get_or_create_function(self, function_skeleton: StaticFunctionSkeleton, terms: TermList, mapping: Sequence[int]) -> StaticFunction: ...

    @overload
    def get_or_create_function(self, function_skeleton: FluentFunctionSkeleton, terms: TermList, mapping: Sequence[int]) -> FluentFunction: ...

    @overload
    def get_or_create_function(self, function_skeleton: AuxiliaryFunctionSkeleton, terms: TermList, mapping: Sequence[int]) -> AuxiliaryFunction: ...

    def get_or_create_function_expression_number(self, number: float) -> FunctionExpressionNumber: ...

    def get_or_create_function_expression_binary_operator(self, binary_operator: BinaryOperatorEnum, left: FunctionExpression, right: FunctionExpression) -> FunctionExpressionBinaryOperator: ...

    def get_or_create_function_expression_multi_operator(self, multi_operator: MultiOperatorEnum, function_expressions: FunctionExpressionList) -> FunctionExpressionMultiOperator: ...

    def get_or_create_function_expression_minus(self, function_expression: FunctionExpression) -> FunctionExpressionMinus: ...

    @overload
    def get_or_create_function_expression_function(self, function: StaticFunction) -> StaticFunctionExpressionFunction: ...

    @overload
    def get_or_create_function_expression_function(self, function: FluentFunction) -> FluentFunctionExpressionFunction: ...

    @overload
    def get_or_create_function_expression(self, function_expression: FunctionExpressionNumber) -> FunctionExpression: ...

    @overload
    def get_or_create_function_expression(self, function_expression: FunctionExpressionBinaryOperator) -> FunctionExpression: ...

    @overload
    def get_or_create_function_expression(self, function_expression: FunctionExpressionMultiOperator) -> FunctionExpression: ...

    @overload
    def get_or_create_function_expression(self, function_expression: FunctionExpressionMinus) -> FunctionExpression: ...

    @overload
    def get_or_create_function_expression(self, function_expression: StaticFunctionExpressionFunction) -> FunctionExpression: ...

    @overload
    def get_or_create_function_expression(self, function_expression: FluentFunctionExpressionFunction) -> FunctionExpression: ...

    def get_or_create_numeric_constraint(self, comparator: BinaryComparatorEnum, left_expression: FunctionExpression, right_expression: FunctionExpression, terms: TermList) -> NumericConstraint: ...

    def get_or_create_conjunctive_condition(self, parameters: VariableList, static_literals: StaticLiteralList, fluent_literals: FluentLiteralList, derived_literals: DerivedLiteralList, numeric_constraints: NumericConstraintList) -> ConjunctiveCondition: ...

    def get_or_create_ground_conjunctive_condition(self, static_literals: StaticGroundLiteralList, fluent_literals: FluentGroundLiteralList, derived_literals: DerivedGroundLiteralList) -> GroundConjunctiveCondition: ...

class ProblemList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ProblemList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Problem], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Problem]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Problem: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ProblemList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Problem, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Problem, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Problem:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ProblemList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Problem, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ProblemList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Problem, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Problem, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Problem, /) -> None:
        """Remove first occurrence of `arg`."""

class GeneralizedProblem:
    @overload
    @staticmethod
    def create(domain_filepath: str | os.PathLike, problem_filepaths: Sequence[str | os.PathLike], options: ParserOptions) -> GeneralizedProblem: ...

    @overload
    @staticmethod
    def create(domain_filepath: str | os.PathLike, problems_directory: str | os.PathLike, options: ParserOptions) -> GeneralizedProblem: ...

    @overload
    @staticmethod
    def create(domain: Domain, problems: ProblemList) -> GeneralizedProblem: ...

    def get_domain(self) -> Domain: ...

    def get_problems(self) -> ProblemList: ...

class Parser:
    def __init__(self, domain_filepath: str | os.PathLike, options: ParserOptions) -> None: ...

    def parse_problem(self, problem_filepath: str | os.PathLike, options: ParserOptions) -> Problem: ...

    def get_domain(self) -> Domain: ...
