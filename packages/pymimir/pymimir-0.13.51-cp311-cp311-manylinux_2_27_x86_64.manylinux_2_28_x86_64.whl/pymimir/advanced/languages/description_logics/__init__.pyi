from collections.abc import Iterable, Iterator
import enum
from typing import overload

import pymimir.advanced.datasets
import pymimir.advanced.formalism
import pymimir.advanced.search


class GrammarSpecificationEnum(enum.Enum):
    FRANCES_ET_AL_AAAI2021 = 1

class Concept:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Concept, /) -> bool: ...

    def __ne__(self, arg: Concept, /) -> bool: ...

    def __hash__(self) -> int: ...

    def evaluate(self, evaluation_context: EvaluationContext) -> ConceptDenotation: ...

    def accept(self, visitor: "mimir::languages::dl::IVisitor") -> None: ...

    def get_complexity(self) -> int: ...

    def get_index(self) -> int: ...

class ConceptList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ConceptList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Concept], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Concept]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Concept: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ConceptList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Concept, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Concept, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Concept:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ConceptList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Concept, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ConceptList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Concept, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Concept, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Concept, /) -> None:
        """Remove first occurrence of `arg`."""

class Role:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Role, /) -> bool: ...

    def __ne__(self, arg: Role, /) -> bool: ...

    def __hash__(self) -> int: ...

    def evaluate(self, evaluation_context: EvaluationContext) -> RoleDenotation: ...

    def accept(self, visitor: "mimir::languages::dl::IVisitor") -> None: ...

    def get_complexity(self) -> int: ...

    def get_index(self) -> int: ...

class RoleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: RoleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Role], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Role]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Role: ...

    @overload
    def __getitem__(self, arg: slice, /) -> RoleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Role, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Role, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Role:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: RoleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Role, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: RoleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Role, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Role, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Role, /) -> None:
        """Remove first occurrence of `arg`."""

class Boolean:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Boolean, /) -> bool: ...

    def __ne__(self, arg: Boolean, /) -> bool: ...

    def __hash__(self) -> int: ...

    def evaluate(self, evaluation_context: EvaluationContext) -> BooleanDenotation: ...

    def accept(self, visitor: "mimir::languages::dl::IVisitor") -> None: ...

    def get_complexity(self) -> int: ...

    def get_index(self) -> int: ...

class BooleanList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: BooleanList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Boolean], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Boolean]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Boolean: ...

    @overload
    def __getitem__(self, arg: slice, /) -> BooleanList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Boolean, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Boolean, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Boolean:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: BooleanList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Boolean, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: BooleanList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Boolean, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Boolean, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Boolean, /) -> None:
        """Remove first occurrence of `arg`."""

class Numerical:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Numerical, /) -> bool: ...

    def __ne__(self, arg: Numerical, /) -> bool: ...

    def __hash__(self) -> int: ...

    def evaluate(self, evaluation_context: EvaluationContext) -> NumericalDenotation: ...

    def accept(self, visitor: "mimir::languages::dl::IVisitor") -> None: ...

    def get_complexity(self) -> int: ...

    def get_index(self) -> int: ...

class NumericalList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: NumericalList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Numerical], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Numerical]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Numerical: ...

    @overload
    def __getitem__(self, arg: slice, /) -> NumericalList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Numerical, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Numerical, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Numerical:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: NumericalList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Numerical, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: NumericalList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Numerical, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Numerical, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Numerical, /) -> None:
        """Remove first occurrence of `arg`."""

class ConceptBot(Concept):
    pass

class ConceptTop(Concept):
    pass

class ConceptStaticAtomicState(Concept):
    def get_predicate(self) -> pymimir.advanced.formalism.StaticPredicate: ...

class ConceptFluentAtomicState(Concept):
    def get_predicate(self) -> pymimir.advanced.formalism.FluentPredicate: ...

class ConceptDerivedAtomicState(Concept):
    def get_predicate(self) -> pymimir.advanced.formalism.DerivedPredicate: ...

class ConceptStaticAtomicGoal(Concept):
    def get_predicate(self) -> pymimir.advanced.formalism.StaticPredicate: ...

    def get_polarity(self) -> bool: ...

class ConceptFluentAtomicGoal(Concept):
    def get_predicate(self) -> pymimir.advanced.formalism.FluentPredicate: ...

    def get_polarity(self) -> bool: ...

class ConceptDerivedAtomicGoal(Concept):
    def get_predicate(self) -> pymimir.advanced.formalism.DerivedPredicate: ...

    def get_polarity(self) -> bool: ...

class ConceptIntersection(Concept):
    def get_left_concept(self) -> Concept: ...

    def get_right_concept(self) -> Concept: ...

class ConceptUnion(Concept):
    def get_left_concept(self) -> Concept: ...

    def get_right_concept(self) -> Concept: ...

class ConceptNegation(Concept):
    def get_concept(self) -> Concept: ...

class ConceptValueRestriction(Concept):
    def get_role(self) -> Role: ...

    def get_concept(self) -> Concept: ...

class ConceptExistentialQuantification(Concept):
    def get_role(self) -> Role: ...

    def get_concept(self) -> Concept: ...

class ConceptRoleValueMapContainment(Concept):
    def get_left_role(self) -> Role: ...

    def get_right_role(self) -> Role: ...

class ConceptRoleValueMapEquality(Concept):
    def get_left_role(self) -> Role: ...

    def get_right_role(self) -> Role: ...

class ConceptNominal(Concept):
    def get_object(self) -> pymimir.advanced.formalism.Object: ...

class RoleUniversal(Role):
    pass

class RoleStaticAtomicState(Role):
    def get_predicate(self) -> pymimir.advanced.formalism.StaticPredicate: ...

class RoleFluentAtomicState(Role):
    def get_predicate(self) -> pymimir.advanced.formalism.FluentPredicate: ...

class RoleDerivedAtomicState(Role):
    def get_predicate(self) -> pymimir.advanced.formalism.DerivedPredicate: ...

class RoleStaticAtomicGoal(Role):
    def get_predicate(self) -> pymimir.advanced.formalism.StaticPredicate: ...

    def get_polarity(self) -> bool: ...

class RoleFluentAtomicGoal(Role):
    def get_predicate(self) -> pymimir.advanced.formalism.FluentPredicate: ...

    def get_polarity(self) -> bool: ...

class RoleDerivedAtomicGoal(Role):
    def get_predicate(self) -> pymimir.advanced.formalism.DerivedPredicate: ...

    def get_polarity(self) -> bool: ...

class RoleIntersection(Role):
    def get_left_role(self) -> Role: ...

    def get_right_role(self) -> Role: ...

class RoleUnion(Role):
    def get_left_role(self) -> Role: ...

    def get_right_role(self) -> Role: ...

class RoleComplement(Role):
    def get_role(self) -> Role: ...

class RoleInverse(Role):
    def get_role(self) -> Role: ...

class RoleComposition(Role):
    def get_left_role(self) -> Role: ...

    def get_right_role(self) -> Role: ...

class RoleTransitiveClosure(Role):
    def get_role(self) -> Role: ...

class RoleReflexiveTransitiveClosure(Role):
    def get_role(self) -> Role: ...

class RoleRestriction(Role):
    def get_role(self) -> Role: ...

    def get_concept(self) -> Concept: ...

class RoleIdentity(Role):
    def get_concept(self) -> Concept: ...

class BooleanStaticAtomicState(Boolean):
    def get_predicate(self) -> pymimir.advanced.formalism.StaticPredicate: ...

class BooleanFluentAtomicState(Boolean):
    def get_predicate(self) -> pymimir.advanced.formalism.FluentPredicate: ...

class BooleanDerivedAtomicState(Boolean):
    def get_predicate(self) -> pymimir.advanced.formalism.DerivedPredicate: ...

class BooleanConceptNonempty(Boolean):
    def get_constructor(self) -> Concept: ...

class BooleanRoleNonempty(Boolean):
    def get_constructor(self) -> Role: ...

class NumericalConceptCount(Numerical):
    def get_constructor(self) -> Concept: ...

class NumericalRoleCount(Numerical):
    def get_constructor(self) -> Role: ...

class NumericalDistance(Numerical):
    def get_left_concept(self) -> Concept: ...

    def get_role(self) -> Role: ...

    def get_right_concept(self) -> Concept: ...

class Repositories:
    def __init__(self) -> None: ...

    def get_or_create_concept(self, sentence: str, domain: pymimir.advanced.formalism.Domain) -> Concept: ...

    def get_or_create_role(self, sentence: str, domain: pymimir.advanced.formalism.Domain) -> Role: ...

    def get_or_create_boolean(self, sentence: str, domain: pymimir.advanced.formalism.Domain) -> Boolean: ...

    def get_or_create_numerical(self, sentence: str, domain: pymimir.advanced.formalism.Domain) -> Numerical: ...

    def get_or_create_concept_bot(self) -> Concept: ...

    def get_or_create_concept_top(self) -> Concept: ...

    def get_or_create_concept_intersection(self, left_concept: Concept, right_concept: Concept) -> Concept: ...

    def get_or_create_concept_union(self, left_concept: Concept, right_concept: Concept) -> Concept: ...

    def get_or_create_concept_negation(self, concept_: Concept) -> Concept: ...

    def get_or_create_concept_value_restriction(self, role: Role, concept_: Concept) -> Concept: ...

    def get_or_create_concept_existential_quantification(self, role: Role, concept_: Concept) -> Concept: ...

    def get_or_create_concept_role_value_map_containment(self, left_role: Role, right_role: Role) -> Concept: ...

    def get_or_create_concept_role_value_map_equality(self, left_role: Role, right_role: Role) -> Concept: ...

    def get_or_create_concept_nominal(self, object: pymimir.advanced.formalism.Object) -> Concept: ...

    def get_or_create_role_universal(self) -> Role: ...

    def get_or_create_role_intersection(self, left_role: Role, right_role: Role) -> Role: ...

    def get_or_create_role_union(self, left_role: Role, right_role: Role) -> Role: ...

    def get_or_create_role_complement(self, role: Role) -> Role: ...

    def get_or_create_role_inverse(self, role: Role) -> Role: ...

    def get_or_create_role_composition(self, left_role: Role, right_role: Role) -> Role: ...

    def get_or_create_role_transitive_closure(self, role: Role) -> Role: ...

    def get_or_create_role_reflexive_transitive_closure(self, role: Role) -> Role: ...

    def get_or_create_role_restriction(self, role: Role, concept_: Concept) -> Role: ...

    def get_or_create_role_identity(self, concept_: Concept) -> Role: ...

    def get_or_create_concept_atomic_state_static(self, predicate: pymimir.advanced.formalism.StaticPredicate) -> Concept: ...

    def get_or_create_concept_atomic_state_fluent(self, predicate: pymimir.advanced.formalism.FluentPredicate) -> Concept: ...

    def get_or_create_concept_atomic_state_derived(self, predicate: pymimir.advanced.formalism.DerivedPredicate) -> Concept: ...

    def get_or_create_concept_atomic_goal_static(self, predicate: pymimir.advanced.formalism.StaticPredicate, polarity: bool) -> Concept: ...

    def get_or_create_concept_atomic_goal_fluent(self, predicate: pymimir.advanced.formalism.FluentPredicate, polarity: bool) -> Concept: ...

    def get_or_create_concept_atomic_goal_derived(self, predicate: pymimir.advanced.formalism.DerivedPredicate, polarity: bool) -> Concept: ...

    def get_or_create_role_atomic_state_static(self, predicate: pymimir.advanced.formalism.StaticPredicate) -> Role: ...

    def get_or_create_role_atomic_state_fluent(self, predicate: pymimir.advanced.formalism.FluentPredicate) -> Role: ...

    def get_or_create_role_atomic_state_derived(self, predicate: pymimir.advanced.formalism.DerivedPredicate) -> Role: ...

    def get_or_create_role_atomic_goal_static(self, predicate: pymimir.advanced.formalism.StaticPredicate, polarity: bool) -> Role: ...

    def get_or_create_role_atomic_goal_fluent(self, predicate: pymimir.advanced.formalism.FluentPredicate, polarity: bool) -> Role: ...

    def get_or_create_role_atomic_goal_derived(self, predicate: pymimir.advanced.formalism.DerivedPredicate, polarity: bool) -> Role: ...

    def get_or_create_boolean_atomic_state_static(self, predicate: pymimir.advanced.formalism.StaticPredicate) -> Boolean: ...

    def get_or_create_boolean_atomic_state_fluent(self, predicate: pymimir.advanced.formalism.FluentPredicate) -> Boolean: ...

    def get_or_create_boolean_atomic_state_derived(self, predicate: pymimir.advanced.formalism.DerivedPredicate) -> Boolean: ...

    def get_or_create_boolean_nonempty_concept(self, constructor: Concept) -> Boolean: ...

    def get_or_create_boolean_nonempty_role(self, constructor: Role) -> Boolean: ...

    def get_or_create_numerical_count_concept(self, constructor: Concept) -> Numerical: ...

    def get_or_create_numerical_count_role(self, constructor: Role) -> Numerical: ...

    def get_or_create_numerical_distance(self, left_concept: Concept, role: Role, right_concept: Concept) -> Numerical: ...

class ConceptDenotation:
    pass

class RoleDenotation:
    pass

class BooleanDenotation:
    def get_data(self) -> bool: ...

class NumericalDenotation:
    def get_data(self) -> int: ...

class DenotationRepositories:
    def __init__(self) -> None: ...

    def clear(self) -> None: ...

class EvaluationContext:
    def __init__(self, state: pymimir.advanced.search.State, denotation_repositories: DenotationRepositories) -> None: ...

class CNFConcept:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFConcept, /) -> bool: ...

    def __ne__(self, arg: CNFConcept, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Concept, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

class CNFConceptList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFConceptList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFConcept], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFConcept]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFConcept: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFConceptList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFConcept, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFConcept, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFConcept:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFConceptList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFConcept, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFConceptList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFConcept, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFConcept, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFConcept, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFRole:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFRole, /) -> bool: ...

    def __ne__(self, arg: CNFRole, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Role, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

class CNFRoleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFRoleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFRole], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFRole]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFRole: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFRoleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFRole, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFRole, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFRole:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFRoleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFRole, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFRoleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFRole, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFRole, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFRole, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFBoolean:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFBoolean, /) -> bool: ...

    def __ne__(self, arg: CNFBoolean, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Boolean, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

class CNFBooleanList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFBooleanList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFBoolean], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFBoolean]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFBoolean: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFBooleanList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFBoolean, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFBoolean, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFBoolean:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFBooleanList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFBoolean, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFBooleanList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFBoolean, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFBoolean, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFBoolean, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFNumerical:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFNumerical, /) -> bool: ...

    def __ne__(self, arg: CNFNumerical, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Numerical, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

class CNFNumericalList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFNumericalList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFNumerical], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFNumerical]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFNumerical: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFNumericalList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFNumerical, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFNumerical, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFNumerical:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFNumericalList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFNumerical, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFNumericalList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFNumerical, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFNumerical, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFNumerical, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFConceptNonTerminal:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFConceptNonTerminal, /) -> bool: ...

    def __ne__(self, arg: CNFConceptNonTerminal, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Concept, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

class CNFConceptNonTerminalList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFConceptNonTerminalList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFConceptNonTerminal], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFConceptNonTerminal]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFConceptNonTerminal: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFConceptNonTerminalList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFConceptNonTerminal, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFConceptNonTerminal, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFConceptNonTerminal:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFConceptNonTerminalList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFConceptNonTerminal, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFConceptNonTerminalList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFConceptNonTerminal, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFConceptNonTerminal, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFConceptNonTerminal, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFRoleNonTerminal:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFRoleNonTerminal, /) -> bool: ...

    def __ne__(self, arg: CNFRoleNonTerminal, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Role, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

class CNFRoleNonTerminalList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFRoleNonTerminalList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFRoleNonTerminal], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFRoleNonTerminal]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFRoleNonTerminal: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFRoleNonTerminalList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFRoleNonTerminal, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFRoleNonTerminal, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFRoleNonTerminal:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFRoleNonTerminalList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFRoleNonTerminal, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFRoleNonTerminalList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFRoleNonTerminal, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFRoleNonTerminal, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFRoleNonTerminal, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFBooleanNonTerminal:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFBooleanNonTerminal, /) -> bool: ...

    def __ne__(self, arg: CNFBooleanNonTerminal, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Boolean, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

class CNFBooleanNonTerminalList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFBooleanNonTerminalList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFBooleanNonTerminal], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFBooleanNonTerminal]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFBooleanNonTerminal: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFBooleanNonTerminalList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFBooleanNonTerminal, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFBooleanNonTerminal, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFBooleanNonTerminal:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFBooleanNonTerminalList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFBooleanNonTerminal, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFBooleanNonTerminalList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFBooleanNonTerminal, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFBooleanNonTerminal, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFBooleanNonTerminal, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFNumericalNonTerminal:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFNumericalNonTerminal, /) -> bool: ...

    def __ne__(self, arg: CNFNumericalNonTerminal, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Numerical, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

class CNFNumericalNonTerminalList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFNumericalNonTerminalList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFNumericalNonTerminal], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFNumericalNonTerminal]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFNumericalNonTerminal: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFNumericalNonTerminalList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFNumericalNonTerminal, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFNumericalNonTerminal, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFNumericalNonTerminal:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFNumericalNonTerminalList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFNumericalNonTerminal, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFNumericalNonTerminalList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFNumericalNonTerminal, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFNumericalNonTerminal, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFNumericalNonTerminal, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFConceptDerivationRule:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFConceptDerivationRule, /) -> bool: ...

    def __ne__(self, arg: CNFConceptDerivationRule, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Concept, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_head(self) -> CNFConceptNonTerminal: ...

    def get_body(self) -> CNFConcept: ...

class CNFConceptDerivationRuleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFConceptDerivationRuleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFConceptDerivationRule], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFConceptDerivationRule]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFConceptDerivationRule: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFConceptDerivationRuleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFConceptDerivationRule, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFConceptDerivationRule, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFConceptDerivationRule:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFConceptDerivationRuleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFConceptDerivationRule, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFConceptDerivationRuleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFConceptDerivationRule, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFConceptDerivationRule, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFConceptDerivationRule, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFRoleDerivationRule:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFRoleDerivationRule, /) -> bool: ...

    def __ne__(self, arg: CNFRoleDerivationRule, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Role, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_head(self) -> CNFRoleNonTerminal: ...

    def get_body(self) -> CNFRole: ...

class CNFRoleDerivationRuleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFRoleDerivationRuleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFRoleDerivationRule], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFRoleDerivationRule]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFRoleDerivationRule: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFRoleDerivationRuleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFRoleDerivationRule, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFRoleDerivationRule, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFRoleDerivationRule:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFRoleDerivationRuleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFRoleDerivationRule, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFRoleDerivationRuleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFRoleDerivationRule, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFRoleDerivationRule, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFRoleDerivationRule, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFBooleanDerivationRule:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFBooleanDerivationRule, /) -> bool: ...

    def __ne__(self, arg: CNFBooleanDerivationRule, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Boolean, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_head(self) -> CNFBooleanNonTerminal: ...

    def get_body(self) -> CNFBoolean: ...

class CNFBooleanDerivationRuleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFBooleanDerivationRuleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFBooleanDerivationRule], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFBooleanDerivationRule]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFBooleanDerivationRule: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFBooleanDerivationRuleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFBooleanDerivationRule, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFBooleanDerivationRule, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFBooleanDerivationRule:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFBooleanDerivationRuleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFBooleanDerivationRule, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFBooleanDerivationRuleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFBooleanDerivationRule, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFBooleanDerivationRule, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFBooleanDerivationRule, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFNumericalDerivationRule:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFNumericalDerivationRule, /) -> bool: ...

    def __ne__(self, arg: CNFNumericalDerivationRule, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Numerical, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_head(self) -> CNFNumericalNonTerminal: ...

    def get_body(self) -> CNFNumerical: ...

class CNFNumericalDerivationRuleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFNumericalDerivationRuleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFNumericalDerivationRule], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFNumericalDerivationRule]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFNumericalDerivationRule: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFNumericalDerivationRuleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFNumericalDerivationRule, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFNumericalDerivationRule, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFNumericalDerivationRule:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFNumericalDerivationRuleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFNumericalDerivationRule, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFNumericalDerivationRuleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFNumericalDerivationRule, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFNumericalDerivationRule, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFNumericalDerivationRule, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFConceptSubstitutionRule:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFConceptSubstitutionRule, /) -> bool: ...

    def __ne__(self, arg: CNFConceptSubstitutionRule, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Concept, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_head(self) -> CNFConceptNonTerminal: ...

    def get_body(self) -> CNFConceptNonTerminal: ...

class CNFConceptSubstitutionRuleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFConceptSubstitutionRuleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFConceptSubstitutionRule], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFConceptSubstitutionRule]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFConceptSubstitutionRule: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFConceptSubstitutionRuleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFConceptSubstitutionRule, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFConceptSubstitutionRule, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFConceptSubstitutionRule:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFConceptSubstitutionRuleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFConceptSubstitutionRule, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFConceptSubstitutionRuleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFConceptSubstitutionRule, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFConceptSubstitutionRule, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFConceptSubstitutionRule, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFRoleSubstitutionRule:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFRoleSubstitutionRule, /) -> bool: ...

    def __ne__(self, arg: CNFRoleSubstitutionRule, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Role, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_head(self) -> CNFRoleNonTerminal: ...

    def get_body(self) -> CNFRoleNonTerminal: ...

class CNFRoleSubstitutionRuleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFRoleSubstitutionRuleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFRoleSubstitutionRule], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFRoleSubstitutionRule]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFRoleSubstitutionRule: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFRoleSubstitutionRuleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFRoleSubstitutionRule, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFRoleSubstitutionRule, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFRoleSubstitutionRule:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFRoleSubstitutionRuleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFRoleSubstitutionRule, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFRoleSubstitutionRuleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFRoleSubstitutionRule, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFRoleSubstitutionRule, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFRoleSubstitutionRule, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFBooleanSubstitutionRule:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFBooleanSubstitutionRule, /) -> bool: ...

    def __ne__(self, arg: CNFBooleanSubstitutionRule, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Boolean, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_head(self) -> CNFBooleanNonTerminal: ...

    def get_body(self) -> CNFBooleanNonTerminal: ...

class CNFBooleanSubstitutionRuleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFBooleanSubstitutionRuleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFBooleanSubstitutionRule], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFBooleanSubstitutionRule]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFBooleanSubstitutionRule: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFBooleanSubstitutionRuleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFBooleanSubstitutionRule, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFBooleanSubstitutionRule, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFBooleanSubstitutionRule:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFBooleanSubstitutionRuleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFBooleanSubstitutionRule, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFBooleanSubstitutionRuleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFBooleanSubstitutionRule, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFBooleanSubstitutionRule, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFBooleanSubstitutionRule, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFNumericalSubstitutionRule:
    def __str__(self) -> str: ...

    def __eq__(self, arg: CNFNumericalSubstitutionRule, /) -> bool: ...

    def __ne__(self, arg: CNFNumericalSubstitutionRule, /) -> bool: ...

    def __hash__(self) -> int: ...

    def test_match(self, constructor: Numerical, grammar: CNFGrammar) -> bool: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_head(self) -> CNFNumericalNonTerminal: ...

    def get_body(self) -> CNFNumericalNonTerminal: ...

class CNFNumericalSubstitutionRuleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CNFNumericalSubstitutionRuleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[CNFNumericalSubstitutionRule], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[CNFNumericalSubstitutionRule]: ...

    @overload
    def __getitem__(self, arg: int, /) -> CNFNumericalSubstitutionRule: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CNFNumericalSubstitutionRuleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: CNFNumericalSubstitutionRule, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: CNFNumericalSubstitutionRule, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> CNFNumericalSubstitutionRule:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CNFNumericalSubstitutionRuleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: CNFNumericalSubstitutionRule, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CNFNumericalSubstitutionRuleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: CNFNumericalSubstitutionRule, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: CNFNumericalSubstitutionRule, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: CNFNumericalSubstitutionRule, /) -> None:
        """Remove first occurrence of `arg`."""

class CNFConceptBot(CNFConcept):
    pass

class CNFConceptTop(CNFConcept):
    pass

class CNFConceptStaticAtomicState(CNFConcept):
    def get_predicate(self) -> pymimir.advanced.formalism.StaticPredicate: ...

class CNFConceptFluentAtomicState(CNFConcept):
    def get_predicate(self) -> pymimir.advanced.formalism.FluentPredicate: ...

class CNFConceptDerivedAtomicState(CNFConcept):
    def get_predicate(self) -> pymimir.advanced.formalism.DerivedPredicate: ...

class CNFConceptStaticAtomicGoal(CNFConcept):
    def get_predicate(self) -> pymimir.advanced.formalism.StaticPredicate: ...

    def get_polarity(self) -> bool: ...

class CNFConceptFluentAtomicGoal(CNFConcept):
    def get_predicate(self) -> pymimir.advanced.formalism.FluentPredicate: ...

    def get_polarity(self) -> bool: ...

class CNFConceptDerivedAtomicGoal(CNFConcept):
    def get_predicate(self) -> pymimir.advanced.formalism.DerivedPredicate: ...

    def get_polarity(self) -> bool: ...

class CNFConceptIntersection(CNFConcept):
    def get_left_concept(self) -> CNFConceptNonTerminal: ...

    def get_right_concept(self) -> CNFConceptNonTerminal: ...

class CNFConceptUnion(CNFConcept):
    def get_left_concept(self) -> CNFConceptNonTerminal: ...

    def get_right_concept(self) -> CNFConceptNonTerminal: ...

class CNFConceptNegation(CNFConcept):
    def get_concept(self) -> CNFConceptNonTerminal: ...

class CNFConceptValueRestriction(CNFConcept):
    def get_role(self) -> CNFRoleNonTerminal: ...

    def get_concept(self) -> CNFConceptNonTerminal: ...

class CNFConceptExistentialQuantification(CNFConcept):
    def get_role(self) -> CNFRoleNonTerminal: ...

    def get_concept(self) -> CNFConceptNonTerminal: ...

class CNFConceptRoleValueMapContainment(CNFConcept):
    def get_left_role(self) -> CNFRoleNonTerminal: ...

    def get_right_role(self) -> CNFRoleNonTerminal: ...

class CNFConceptRoleValueMapEquality(CNFConcept):
    def get_left_role(self) -> CNFRoleNonTerminal: ...

    def get_right_role(self) -> CNFRoleNonTerminal: ...

class CNFConceptNominal(CNFConcept):
    def get_object(self) -> pymimir.advanced.formalism.Object: ...

class CNFRoleUniversal(CNFRole):
    pass

class CNFRoleStaticAtomicState(CNFRole):
    def get_predicate(self) -> pymimir.advanced.formalism.StaticPredicate: ...

class CNFRoleFluentAtomicState(CNFRole):
    def get_predicate(self) -> pymimir.advanced.formalism.FluentPredicate: ...

class CNFRoleDerivedAtomicState(CNFRole):
    def get_predicate(self) -> pymimir.advanced.formalism.DerivedPredicate: ...

class CNFRoleStaticAtomicGoal(CNFRole):
    def get_predicate(self) -> pymimir.advanced.formalism.StaticPredicate: ...

    def get_polarity(self) -> bool: ...

class CNFRoleFluentAtomicGoal(CNFRole):
    def get_predicate(self) -> pymimir.advanced.formalism.FluentPredicate: ...

    def get_polarity(self) -> bool: ...

class CNFRoleDerivedAtomicGoal(CNFRole):
    def get_predicate(self) -> pymimir.advanced.formalism.DerivedPredicate: ...

    def get_polarity(self) -> bool: ...

class CNFRoleIntersection(CNFRole):
    def get_left_role(self) -> CNFRoleNonTerminal: ...

    def get_right_role(self) -> CNFRoleNonTerminal: ...

class CNFRoleUnion(CNFRole):
    def get_left_role(self) -> CNFRoleNonTerminal: ...

    def get_right_role(self) -> CNFRoleNonTerminal: ...

class CNFRoleComplement(CNFRole):
    def get_role(self) -> CNFRoleNonTerminal: ...

class CNFRoleInverse(CNFRole):
    def get_role(self) -> CNFRoleNonTerminal: ...

class CNFRoleComposition(CNFRole):
    def get_left_role(self) -> CNFRoleNonTerminal: ...

    def get_right_role(self) -> CNFRoleNonTerminal: ...

class CNFRoleTransitiveClosure(CNFRole):
    def get_role(self) -> CNFRoleNonTerminal: ...

class CNFRoleReflexiveTransitiveClosure(CNFRole):
    def get_role(self) -> CNFRoleNonTerminal: ...

class CNFRoleRestriction(CNFRole):
    def get_role(self) -> CNFRoleNonTerminal: ...

    def get_concept(self) -> CNFConceptNonTerminal: ...

class CNFRoleIdentity(CNFRole):
    def get_concept(self) -> CNFConceptNonTerminal: ...

class CNFBooleanStaticAtomicState(CNFBoolean):
    def get_predicate(self) -> pymimir.advanced.formalism.StaticPredicate: ...

class CNFBooleanFluentAtomicState(CNFBoolean):
    def get_predicate(self) -> pymimir.advanced.formalism.FluentPredicate: ...

class CNFBooleanDerivedAtomicState(CNFBoolean):
    def get_predicate(self) -> pymimir.advanced.formalism.DerivedPredicate: ...

class CNFBooleanConceptNonempty(CNFBoolean):
    def get_constructor(self) -> CNFConceptNonTerminal: ...

class CNFBooleanRoleNonempty(CNFBoolean):
    def get_constructor(self) -> CNFRoleNonTerminal: ...

class CNFNumericalConceptCount(CNFNumerical):
    def get_constructor(self) -> CNFConceptNonTerminal: ...

class CNFNumericalRoleCount(CNFNumerical):
    def get_constructor(self) -> CNFRoleNonTerminal: ...

class CNFNumericalDistance(CNFNumerical):
    def get_left_concept(self) -> CNFConceptNonTerminal: ...

    def get_role(self) -> CNFRoleNonTerminal: ...

    def get_right_concept(self) -> CNFConceptNonTerminal: ...

class CNFGrammar:
    def __init__(self, bnf_description: str, domain: pymimir.advanced.formalism.Domain) -> None: ...

    @staticmethod
    def create(type: GrammarSpecificationEnum, domain: pymimir.advanced.formalism.Domain) -> CNFGrammar: ...

    def __str__(self) -> str: ...

    def accept(self, visitor: "mimir::languages::dl::cnf_grammar::IVisitor") -> None: ...

    @overload
    def test_match(self, arg: Concept, /) -> bool: ...

    @overload
    def test_match(self, arg: Role, /) -> bool: ...

    @overload
    def test_match(self, arg: Boolean, /) -> bool: ...

    @overload
    def test_match(self, arg: Numerical, /) -> bool: ...

    def get_repositories(self) -> CNFRepositories: ...

    def get_domain(self) -> pymimir.advanced.formalism.Domain: ...

    def get_concept_start_symbol(self) -> CNFConceptNonTerminal | None: ...

    def get_role_start_symbol(self) -> CNFRoleNonTerminal | None: ...

    def get_boolean_start_symbol(self) -> CNFBooleanNonTerminal | None: ...

    def get_numerical_start_symbol(self) -> CNFNumericalNonTerminal | None: ...

    def get_concept_derivation_rules(self) -> CNFConceptDerivationRuleList: ...

    def get_role_derivation_rules(self) -> CNFRoleDerivationRuleList: ...

    def get_boolean_derivation_rules(self) -> CNFBooleanDerivationRuleList: ...

    def get_numerical_derivation_rules(self) -> CNFNumericalDerivationRuleList: ...

    def get_concept_substitution_rules(self) -> CNFConceptSubstitutionRuleList: ...

    def get_role_substitution_rules(self) -> CNFRoleSubstitutionRuleList: ...

    def get_boolean_substitution_rules(self) -> CNFBooleanSubstitutionRuleList: ...

    def get_numerical_substitution_rules(self) -> CNFNumericalSubstitutionRuleList: ...

class CNFRepositories:
    def __init__(self) -> None: ...

    def get_or_create_concept_bot(self) -> CNFConcept: ...

    def get_or_create_concept_top(self) -> CNFConcept: ...

    def get_or_create_concept_intersection(self, left_concept: CNFConceptNonTerminal, right_concept: CNFConceptNonTerminal) -> CNFConcept: ...

    def get_or_create_concept_union(self, left_concept: CNFConceptNonTerminal, right_concept: CNFConceptNonTerminal) -> CNFConcept: ...

    def get_or_create_concept_negation(self, concept_: CNFConceptNonTerminal) -> CNFConcept: ...

    def get_or_create_concept_value_restriction(self, role: CNFRoleNonTerminal, concept_: CNFConceptNonTerminal) -> CNFConcept: ...

    def get_or_create_concept_existential_quantification(self, role: CNFRoleNonTerminal, concept_: CNFConceptNonTerminal) -> CNFConcept: ...

    def get_or_create_concept_role_value_map_containment(self, left_role: CNFRoleNonTerminal, right_role: CNFRoleNonTerminal) -> CNFConcept: ...

    def get_or_create_concept_role_value_map_equality(self, left_role: CNFRoleNonTerminal, right_role: CNFRoleNonTerminal) -> CNFConcept: ...

    def get_or_create_concept_nominal(self, object: pymimir.advanced.formalism.Object) -> CNFConcept: ...

    def get_or_create_role_universal(self) -> CNFRole: ...

    def get_or_create_role_intersection(self, left_role: CNFRoleNonTerminal, right_role: CNFRoleNonTerminal) -> CNFRole: ...

    def get_or_create_role_union(self, left_role: CNFRoleNonTerminal, right_role: CNFRoleNonTerminal) -> CNFRole: ...

    def get_or_create_role_complement(self, role: CNFRoleNonTerminal) -> CNFRole: ...

    def get_or_create_role_inverse(self, role: CNFRoleNonTerminal) -> CNFRole: ...

    def get_or_create_role_composition(self, left_role: CNFRoleNonTerminal, right_role: CNFRoleNonTerminal) -> CNFRole: ...

    def get_or_create_role_transitive_closure(self, role: CNFRoleNonTerminal) -> CNFRole: ...

    def get_or_create_role_reflexive_transitive_closure(self, role: CNFRoleNonTerminal) -> CNFRole: ...

    def get_or_create_role_restriction(self, role: CNFRoleNonTerminal, concept_: CNFConceptNonTerminal) -> CNFRole: ...

    def get_or_create_role_identity(self, concept_: CNFConceptNonTerminal) -> CNFRole: ...

    def get_or_create_concept_atomic_state_static(self, predicate: pymimir.advanced.formalism.StaticPredicate) -> CNFConcept: ...

    def get_or_create_concept_atomic_state_fluent(self, predicate: pymimir.advanced.formalism.FluentPredicate) -> CNFConcept: ...

    def get_or_create_concept_atomic_state_derived(self, predicate: pymimir.advanced.formalism.DerivedPredicate) -> CNFConcept: ...

    def get_or_create_concept_atomic_goal_static(self, predicate: pymimir.advanced.formalism.StaticPredicate, polarity: bool) -> CNFConcept: ...

    def get_or_create_concept_atomic_goal_fluent(self, predicate: pymimir.advanced.formalism.FluentPredicate, polarity: bool) -> CNFConcept: ...

    def get_or_create_concept_atomic_goal_derived(self, predicate: pymimir.advanced.formalism.DerivedPredicate, polarity: bool) -> CNFConcept: ...

    def get_or_create_role_atomic_state_static(self, predicate: pymimir.advanced.formalism.StaticPredicate) -> CNFRole: ...

    def get_or_create_role_atomic_state_fluent(self, predicate: pymimir.advanced.formalism.FluentPredicate) -> CNFRole: ...

    def get_or_create_role_atomic_state_derived(self, predicate: pymimir.advanced.formalism.DerivedPredicate) -> CNFRole: ...

    def get_or_create_role_atomic_goal_static(self, predicate: pymimir.advanced.formalism.StaticPredicate, polarity: bool) -> CNFRole: ...

    def get_or_create_role_atomic_goal_fluent(self, predicate: pymimir.advanced.formalism.FluentPredicate, polarity: bool) -> CNFRole: ...

    def get_or_create_role_atomic_goal_derived(self, predicate: pymimir.advanced.formalism.DerivedPredicate, polarity: bool) -> CNFRole: ...

    def get_or_create_boolean_atomic_state_static(self, predicate: pymimir.advanced.formalism.StaticPredicate) -> CNFBoolean: ...

    def get_or_create_boolean_atomic_state_fluent(self, predicate: pymimir.advanced.formalism.FluentPredicate) -> CNFBoolean: ...

    def get_or_create_boolean_atomic_state_derived(self, predicate: pymimir.advanced.formalism.DerivedPredicate) -> CNFBoolean: ...

    def get_or_create_boolean_nonempty_concept(self, constructor: CNFConceptNonTerminal) -> CNFBoolean: ...

    def get_or_create_boolean_nonempty_role(self, constructor: CNFRoleNonTerminal) -> CNFBoolean: ...

    def get_or_create_numerical_count_concept(self, constructor: CNFConceptNonTerminal) -> CNFNumerical: ...

    def get_or_create_numerical_count_role(self, constructor: CNFRoleNonTerminal) -> CNFNumerical: ...

    def get_or_create_numerical_distance(self, left_concept: CNFConceptNonTerminal, role: CNFRoleNonTerminal, right_concept: CNFConceptNonTerminal) -> CNFNumerical: ...

    def get_or_create_concept_nonterminal(self, name: str) -> CNFConceptNonTerminal: ...

    def get_or_create_role_nontermina(self, name: str) -> CNFRoleNonTerminal: ...

    def get_or_create_boolean_nonterminal(self, name: str) -> CNFConceptNonTerminal: ...

    def get_or_create_numerical_nonterminal(self, name: str) -> CNFRoleNonTerminal: ...

    def get_or_create_concept_derivation_rule(self, nonterminal: CNFConceptNonTerminal, constructor: CNFConcept) -> CNFConceptDerivationRule: ...

    def get_or_create_role_derivation_rule(self, nonterminal: CNFRoleNonTerminal, constructor: CNFRole) -> CNFRoleDerivationRule: ...

    def get_or_create_boolean_derivation(self, nonterminal: CNFConceptNonTerminal, constructor: CNFConcept) -> CNFConceptDerivationRule: ...

    def get_or_create_numerical_derivation_rule(self, nonterminal: CNFRoleNonTerminal, constructor: CNFRole) -> CNFRoleDerivationRule: ...

    def get_or_create_concept_substitution_rule(self, nonterminal: CNFConceptNonTerminal, constructor: CNFConceptNonTerminal) -> CNFConceptSubstitutionRule: ...

    def get_or_create_role_substitution_rule(self, nonterminal: CNFRoleNonTerminal, constructor: CNFRoleNonTerminal) -> CNFRoleSubstitutionRule: ...

    def get_or_create_boolean_substitution_rule(self, nonterminal: CNFConceptNonTerminal, constructor: CNFConceptNonTerminal) -> CNFConceptSubstitutionRule: ...

    def get_or_create_numerical_substitution_rule(self, nonterminal: CNFRoleNonTerminal, constructor: CNFRoleNonTerminal) -> CNFRoleSubstitutionRule: ...

class IRefinementPruningFunction:
    def __init__(self) -> None: ...

    @overload
    def should_prune(self, concept: Concept) -> bool: ...

    @overload
    def should_prune(self, role: Role) -> bool: ...

    @overload
    def should_prune(self, boolean: Boolean) -> bool: ...

    @overload
    def should_prune(self, numerical: Numerical) -> bool: ...

class StateListRefinementPruningFunction(IRefinementPruningFunction):
    @overload
    def __init__(self, generalized_state_space: pymimir.advanced.datasets.GeneralizedStateSpace, ref_denotation_repositories: DenotationRepositories) -> None: ...

    @overload
    def __init__(self, generalized_state_space: pymimir.advanced.datasets.GeneralizedStateSpace, class_graph: pymimir.advanced.datasets.BidirectionalStaticClassGraph, ref_denotation_repositories: DenotationRepositories) -> None: ...

    @overload
    def __init__(self, states: pymimir.advanced.search.StateList, ref_denotation_repositories: DenotationRepositories) -> None: ...

class GeneratedSentencesContainer:
    def __init__(self) -> None: ...

    def get_concepts(self) -> dict[CNFConceptNonTerminal, list[ConceptList]]: ...

    def get_roles(self) -> dict[CNFRoleNonTerminal, list[RoleList]]: ...

    def get_booleans(self) -> dict[CNFBooleanNonTerminal, list[BooleanList]]: ...

    def get_numericals(self) -> dict[CNFNumericalNonTerminal, list[NumericalList]]: ...

class GeneratorVisitor:
    def __init__(self, refinement_pruning_function: IRefinementPruningFunction, generated_sentences_container: GeneratedSentencesContainer, repositories: Repositories, max_complexity: int) -> None: ...

    def visit(self, arg: CNFGrammar, /) -> None: ...
