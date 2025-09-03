from collections.abc import Iterable, Iterator, Sequence
import enum
from typing import overload

import pymimir.advanced.datasets
import pymimir.advanced.formalism
import pymimir.advanced.languages.description_logics
import pymimir.advanced.search


class SolvabilityStatus(enum.Enum):
    SOLVED = 0

    CYCLIC = 1

    UNSOLVABLE = 2

class GeneralPoliciesPruningFunction(pymimir.advanced.languages.description_logics.IRefinementPruningFunction):
    @overload
    def __init__(self, generalized_state_space: pymimir.advanced.datasets.GeneralizedStateSpace, ref_denotation_repositories: pymimir.advanced.languages.description_logics.DenotationRepositories) -> None: ...

    @overload
    def __init__(self, generalized_state_space: pymimir.advanced.datasets.GeneralizedStateSpace, class_graph: pymimir.advanced.datasets.BidirectionalStaticClassGraph, ref_denotation_repositories: pymimir.advanced.languages.description_logics.DenotationRepositories) -> None: ...

    @overload
    def __init__(self, states: pymimir.advanced.search.StateList, transitions: Sequence[tuple[pymimir.advanced.search.State, pymimir.advanced.search.State]], ref_denotation_repositories: pymimir.advanced.languages.description_logics.DenotationRepositories) -> None: ...

class NamedConcept:
    def __str__(self) -> str: ...

    def __eq__(self, arg: NamedConcept, /) -> bool: ...

    def __ne__(self, arg: NamedConcept, /) -> bool: ...

    def __hash__(self) -> NamedConcept: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_feature(self) -> pymimir.advanced.languages.description_logics.Concept: ...

class NamedConceptList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: NamedConceptList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[NamedConcept], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[NamedConcept]: ...

    @overload
    def __getitem__(self, arg: int, /) -> NamedConcept: ...

    @overload
    def __getitem__(self, arg: slice, /) -> NamedConceptList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: NamedConcept, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: NamedConcept, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> NamedConcept:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: NamedConceptList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: NamedConcept, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: NamedConceptList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: NamedConcept, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: NamedConcept, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: NamedConcept, /) -> None:
        """Remove first occurrence of `arg`."""

class NamedRole:
    def __str__(self) -> str: ...

    def __eq__(self, arg: NamedRole, /) -> bool: ...

    def __ne__(self, arg: NamedRole, /) -> bool: ...

    def __hash__(self) -> NamedRole: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_feature(self) -> pymimir.advanced.languages.description_logics.Role: ...

class NamedRoleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: NamedRoleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[NamedRole], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[NamedRole]: ...

    @overload
    def __getitem__(self, arg: int, /) -> NamedRole: ...

    @overload
    def __getitem__(self, arg: slice, /) -> NamedRoleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: NamedRole, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: NamedRole, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> NamedRole:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: NamedRoleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: NamedRole, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: NamedRoleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: NamedRole, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: NamedRole, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: NamedRole, /) -> None:
        """Remove first occurrence of `arg`."""

class NamedBoolean:
    def __str__(self) -> str: ...

    def __eq__(self, arg: NamedBoolean, /) -> bool: ...

    def __ne__(self, arg: NamedBoolean, /) -> bool: ...

    def __hash__(self) -> NamedBoolean: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_feature(self) -> pymimir.advanced.languages.description_logics.Boolean: ...

class NamedBooleanList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: NamedBooleanList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[NamedBoolean], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[NamedBoolean]: ...

    @overload
    def __getitem__(self, arg: int, /) -> NamedBoolean: ...

    @overload
    def __getitem__(self, arg: slice, /) -> NamedBooleanList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: NamedBoolean, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: NamedBoolean, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> NamedBoolean:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: NamedBooleanList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: NamedBoolean, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: NamedBooleanList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: NamedBoolean, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: NamedBoolean, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: NamedBoolean, /) -> None:
        """Remove first occurrence of `arg`."""

class NamedNumerical:
    def __str__(self) -> str: ...

    def __eq__(self, arg: NamedNumerical, /) -> bool: ...

    def __ne__(self, arg: NamedNumerical, /) -> bool: ...

    def __hash__(self) -> NamedNumerical: ...

    def get_index(self) -> int: ...

    def get_name(self) -> str: ...

    def get_feature(self) -> pymimir.advanced.languages.description_logics.Numerical: ...

class NamedNumericalList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: NamedNumericalList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[NamedNumerical], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[NamedNumerical]: ...

    @overload
    def __getitem__(self, arg: int, /) -> NamedNumerical: ...

    @overload
    def __getitem__(self, arg: slice, /) -> NamedNumericalList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: NamedNumerical, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: NamedNumerical, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> NamedNumerical:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: NamedNumericalList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: NamedNumerical, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: NamedNumericalList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: NamedNumerical, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: NamedNumerical, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: NamedNumerical, /) -> None:
        """Remove first occurrence of `arg`."""

class Condition:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Condition, /) -> bool: ...

    def __ne__(self, arg: Condition, /) -> bool: ...

    def __hash__(self) -> int: ...

    def evaluate(self, evaluation_context: pymimir.advanced.languages.description_logics.EvaluationContext) -> bool: ...

    def accept(self, visitor: "mimir::languages::general_policies::IVisitor") -> None: ...

    def get_index(self) -> int: ...

class ConditionList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ConditionList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Condition], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Condition]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Condition: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ConditionList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Condition, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Condition, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Condition:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ConditionList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Condition, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ConditionList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Condition, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Condition, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Condition, /) -> None:
        """Remove first occurrence of `arg`."""

class PositiveBooleanCondition(Condition):
    def get_feature(self) -> NamedBoolean: ...

class NegativeBooleanCondition(Condition):
    def get_feature(self) -> NamedBoolean: ...

class GreaterNumericalCondition(Condition):
    def get_feature(self) -> NamedNumerical: ...

class EqualNumericalCondition(Condition):
    def get_feature(self) -> NamedNumerical: ...

class Effect:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Effect, /) -> bool: ...

    def __ne__(self, arg: Effect, /) -> bool: ...

    def __hash__(self) -> int: ...

    def evaluate(self, source_evaluation_context: pymimir.advanced.languages.description_logics.EvaluationContext, target_evaluation_context: pymimir.advanced.languages.description_logics.EvaluationContext) -> bool: ...

    def accept(self, visitor: "mimir::languages::general_policies::IVisitor") -> None: ...

    def get_index(self) -> int: ...

class EffectList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: EffectList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Effect], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Effect]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Effect: ...

    @overload
    def __getitem__(self, arg: slice, /) -> EffectList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Effect, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Effect, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Effect:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: EffectList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Effect, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: EffectList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Effect, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Effect, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Effect, /) -> None:
        """Remove first occurrence of `arg`."""

class PositiveBooleanEffect(Effect):
    def get_feature(self) -> NamedBoolean: ...

class NegativeBooleanEffect(Effect):
    def get_feature(self) -> NamedBoolean: ...

class UnchangedBooleanEffect(Effect):
    def get_feature(self) -> NamedBoolean: ...

class IncreaseNumericalEffect(Effect):
    def get_feature(self) -> NamedNumerical: ...

class DecreaseNumericalEffect(Effect):
    def get_feature(self) -> NamedNumerical: ...

class UnchangedNumericalEffect(Effect):
    def get_feature(self) -> NamedNumerical: ...

class Rule:
    def __str__(self) -> str: ...

    def __eq__(self, arg: Rule, /) -> bool: ...

    def __ne__(self, arg: Rule, /) -> bool: ...

    def __hash__(self) -> int: ...

    def evaluate(self, source_evaluation_context: pymimir.advanced.languages.description_logics.EvaluationContext, target_evaluation_context: pymimir.advanced.languages.description_logics.EvaluationContext) -> bool: ...

    def accept(self, visitor: "mimir::languages::general_policies::IVisitor") -> None: ...

    def get_index(self) -> int: ...

    def get_conditions(self) -> ConditionList: ...

    def get_effects(self) -> EffectList: ...

class RuleList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: RuleList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Rule], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Rule]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Rule: ...

    @overload
    def __getitem__(self, arg: slice, /) -> RuleList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Rule, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Rule, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Rule:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: RuleList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Rule, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: RuleList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: Rule, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: Rule, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: Rule, /) -> None:
        """Remove first occurrence of `arg`."""

class GeneralPolicy:
    def __str__(self) -> str: ...

    def __eq__(self, arg: GeneralPolicy, /) -> bool: ...

    def __ne__(self, arg: GeneralPolicy, /) -> bool: ...

    def __hash__(self) -> int: ...

    def evaluate(self, source_context: pymimir.advanced.languages.description_logics.EvaluationContext, target_contest: pymimir.advanced.languages.description_logics.EvaluationContext) -> bool: ...

    def accept(self, visitor: "mimir::languages::general_policies::IVisitor") -> None: ...

    def is_terminating(self, repositories: Repositories) -> bool: ...

    @overload
    def solves(self, state_space: pymimir.advanced.datasets.StateSpace, denotation_repositories: pymimir.advanced.languages.description_logics.DenotationRepositories) -> SolvabilityStatus: ...

    @overload
    def solves(self, state_space: pymimir.advanced.datasets.StateSpace, vertex_indices: Sequence[int], denotation_repositories: pymimir.advanced.languages.description_logics.DenotationRepositories) -> SolvabilityStatus: ...

    @overload
    def solves(self, state_space: pymimir.advanced.datasets.GeneralizedStateSpace, denotation_repositories: pymimir.advanced.languages.description_logics.DenotationRepositories) -> SolvabilityStatus: ...

    @overload
    def solves(self, state_space: pymimir.advanced.datasets.GeneralizedStateSpace, vertex_indices: Sequence[int], denotation_repositories: pymimir.advanced.languages.description_logics.DenotationRepositories) -> SolvabilityStatus: ...

    @overload
    def solves(self, search_context: pymimir.advanced.search.SearchContext, denotation_repositories: pymimir.advanced.languages.description_logics.DenotationRepositories) -> SolvabilityStatus: ...

    def find_solution(self, search_context: pymimir.advanced.search.SearchContext, denotation_repositories: pymimir.advanced.languages.description_logics.DenotationRepositories) -> pymimir.advanced.search.SearchResult: ...

    def get_index(self) -> int: ...

    def get_boolean_features(self) -> NamedBooleanList: ...

    def get_numerical_features(self) -> NamedNumericalList: ...

    def get_rules(self) -> RuleList: ...

class Repositories:
    def __init__(self) -> None: ...

    @overload
    def get_or_create_named_feature(self, name: str, concept: pymimir.advanced.languages.description_logics.Concept) -> NamedConcept: ...

    @overload
    def get_or_create_named_feature(self, name: str, role: pymimir.advanced.languages.description_logics.Role) -> NamedRole: ...

    @overload
    def get_or_create_named_feature(self, name: str, boolean: pymimir.advanced.languages.description_logics.Boolean) -> NamedBoolean: ...

    @overload
    def get_or_create_named_feature(self, name: str, numerical: pymimir.advanced.languages.description_logics.Numerical) -> NamedNumerical: ...

    def get_or_create_positive_boolean_condition(self, arg: NamedBoolean, /) -> Condition:
        """named_boolean"""

    def get_or_create_negative_boolean_condition(self, arg: NamedBoolean, /) -> Condition:
        """named_boolean"""

    def get_or_create_greater_numerical_condition(self, arg: NamedNumerical, /) -> Condition:
        """named_numerical"""

    def get_or_create_equal_numerical_condition(self, arg: NamedNumerical, /) -> Condition:
        """named_numerical"""

    def get_or_create_positive_boolean_effect(self, arg: NamedBoolean, /) -> Effect:
        """named_boolean"""

    def get_or_create_negative_boolean_effect(self, arg: NamedBoolean, /) -> Effect:
        """named_boolean"""

    def get_or_create_unchanged_boolean_effect(self, arg: NamedBoolean, /) -> Effect:
        """named_boolean"""

    def get_or_create_increase_numerical_effect(self, arg: NamedNumerical, /) -> Effect:
        """named_numerical"""

    def get_or_create_decrease_numerical_effect(self, arg: NamedNumerical, /) -> Effect:
        """named_numerical"""

    def get_or_create_unchanged_numerical_effect(self, arg: NamedNumerical, /) -> Effect:
        """named_numerical"""

    def get_or_create_rule(self, conditions: ConditionList, effects: EffectList) -> Rule: ...

    @overload
    def get_or_create_general_policy(self, boolean_features: NamedBooleanList, numerical_features: NamedNumericalList, rules: RuleList) -> GeneralPolicy: ...

    @overload
    def get_or_create_general_policy(self, description: str, domain: pymimir.advanced.formalism.Domain, dl_repositories: pymimir.advanced.languages.description_logics.Repositories) -> GeneralPolicy: ...

class GeneralPolicyFactory:
    @staticmethod
    def get_or_create_general_policy_gripper(domain: pymimir.advanced.formalism.Domain, repositories: Repositories, dl_repositories: pymimir.advanced.languages.description_logics.Repositories) -> GeneralPolicy: ...

    @staticmethod
    def get_or_create_general_policy_blocks3ops(domain: pymimir.advanced.formalism.Domain, repositories: Repositories, dl_repositories: pymimir.advanced.languages.description_logics.Repositories) -> GeneralPolicy: ...

    @staticmethod
    def get_or_create_general_policy_spanner(domain: pymimir.advanced.formalism.Domain, repositories: Repositories, dl_repositories: pymimir.advanced.languages.description_logics.Repositories) -> GeneralPolicy: ...

    @staticmethod
    def get_or_create_general_policy_delivery(domain: pymimir.advanced.formalism.Domain, repositories: Repositories, dl_repositories: pymimir.advanced.languages.description_logics.Repositories) -> GeneralPolicy: ...
