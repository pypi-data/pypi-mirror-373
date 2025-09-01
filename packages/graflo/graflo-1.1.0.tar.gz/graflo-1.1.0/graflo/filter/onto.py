"""Filter expression system for database queries.

This module provides a flexible system for creating and evaluating filter expressions
that can be translated into different database query languages (AQL, Cypher, Python).
It includes classes for logical operators, comparison operators, and filter clauses.

Key Components:
    - LogicalOperator: Enum for logical operations (AND, OR, NOT, IMPLICATION)
    - ComparisonOperator: Enum for comparison operations (==, !=, >, <, etc.)
    - AbsClause: Abstract base class for filter clauses
    - LeafClause: Concrete clause for field comparisons
    - Clause: Composite clause combining multiple sub-clauses
    - Expression: Factory class for creating filter expressions from dictionaries

Example:
    >>> expr = Expression.from_dict({
    ...     "AND": [
    ...         {"field": "age", "cmp_operator": ">=", "value": 18},
    ...         {"field": "status", "cmp_operator": "==", "value": "active"}
    ...     ]
    ... })
    >>> # Converts to: "age >= 18 AND status == 'active'"
"""

import dataclasses
import logging
from abc import ABCMeta, abstractmethod
from types import MappingProxyType

from graflo.onto import BaseDataclass, BaseEnum, ExpressionFlavor

logger = logging.getLogger(__name__)


class LogicalOperator(BaseEnum):
    """Logical operators for combining filter conditions.

    Attributes:
        AND: Logical AND operation
        OR: Logical OR operation
        NOT: Logical NOT operation
        IMPLICATION: Logical IF-THEN operation
    """

    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IMPLICATION = "IF_THEN"


def implication(ops):
    """Evaluate logical implication (IF-THEN).

    Args:
        ops: Tuple of (antecedent, consequent)

    Returns:
        bool: True if antecedent is False or consequent is True
    """
    a, b = ops
    return b if a else True


OperatorMapping = MappingProxyType(
    {
        LogicalOperator.AND: all,
        LogicalOperator.OR: any,
        LogicalOperator.IMPLICATION: implication,
    }
)


class ComparisonOperator(BaseEnum):
    """Comparison operators for field comparisons.

    Attributes:
        NEQ: Not equal (!=)
        EQ: Equal (==)
        GE: Greater than or equal (>=)
        LE: Less than or equal (<=)
        GT: Greater than (>)
        LT: Less than (<)
        IN: Membership test (IN)
    """

    NEQ = "!="
    EQ = "=="
    GE = ">="
    LE = "<="
    GT = ">"
    LT = "<"
    IN = "IN"


@dataclasses.dataclass
class AbsClause(BaseDataclass, metaclass=ABCMeta):
    """Abstract base class for filter clauses.

    This class defines the interface for all filter clauses, requiring
    implementation of the __call__ method to evaluate or render the clause.
    """

    @abstractmethod
    def __call__(
        self,
        doc_name,
        kind: ExpressionFlavor = ExpressionFlavor.ARANGO,
        **kwargs,
    ):
        """Evaluate or render the clause.

        Args:
            doc_name: Name of the document variable in the query
            kind: Target expression flavor (ARANGO, NEO4J, PYTHON)
            **kwargs: Additional arguments for evaluation

        Returns:
            str: Rendered clause in the target language
        """
        pass


@dataclasses.dataclass
class LeafClause(AbsClause):
    """Concrete clause for field comparisons.

    This class represents a single field comparison operation, such as
    "field >= value" or "field IN [values]".

    Attributes:
        cmp_operator: Comparison operator to use
        value: Value(s) to compare against
        field: Field name to compare
        operator: Optional operator to apply before comparison
    """

    cmp_operator: ComparisonOperator | None = None
    value: list = dataclasses.field(default_factory=list)
    field: str | None = None
    operator: str | None = None

    def __post_init__(self):
        """Convert single value to list if necessary."""
        if not isinstance(self.value, list):
            self.value = [self.value]

    def __call__(
        self,
        doc_name="doc",
        kind: ExpressionFlavor = ExpressionFlavor.ARANGO,
        **kwargs,
    ):
        """Render the leaf clause in the target language.

        Args:
            doc_name: Name of the document variable
            kind: Target expression flavor
            **kwargs: Additional arguments

        Returns:
            str: Rendered clause

        Raises:
            ValueError: If kind is not implemented
        """
        if not self.value:
            logger.warning(f"for {self} value is not set : {self.value}")
        if kind == ExpressionFlavor.ARANGO:
            assert self.cmp_operator is not None
            return self._cast_arango(doc_name)
        elif kind == ExpressionFlavor.NEO4J:
            assert self.cmp_operator is not None
            return self._cast_cypher(doc_name)
        elif kind == ExpressionFlavor.PYTHON:
            return self._cast_python(**kwargs)
        else:
            raise ValueError(f"kind {kind} not implemented")

    def _cast_value(self):
        """Format the comparison value for query rendering.

        Returns:
            str: Formatted value string
        """
        value = f"{self.value[0]}" if len(self.value) == 1 else f"{self.value}"
        if len(self.value) == 1:
            if isinstance(self.value[0], str):
                value = f'"{self.value[0]}"'
            elif self.value[0] is None:
                value = "null"
            else:
                value = f"{self.value[0]}"
        return value

    def _cast_arango(self, doc_name):
        """Render the clause in AQL format.

        Args:
            doc_name: Document variable name

        Returns:
            str: AQL clause
        """
        const = self._cast_value()

        lemma = f"{self.cmp_operator} {const}"
        if self.operator is not None:
            lemma = f"{self.operator} {lemma}"

        if self.field is not None:
            lemma = f'{doc_name}["{self.field}"] {lemma}'
        return lemma

    def _cast_cypher(self, doc_name):
        """Render the clause in Cypher format.

        Args:
            doc_name: Document variable name

        Returns:
            str: Cypher clause
        """
        const = self._cast_value()
        if self.cmp_operator == ComparisonOperator.EQ:
            cmp_operator = "="
        else:
            cmp_operator = self.cmp_operator
        lemma = f"{cmp_operator} {const}"
        if self.operator is not None:
            lemma = f"{self.operator} {lemma}"

        if self.field is not None:
            lemma = f"{doc_name}.{self.field} {lemma}"
        return lemma

    def _cast_python(self, **kwargs):
        """Evaluate the clause in Python.

        Args:
            **kwargs: Additional arguments

        Returns:
            bool: Evaluation result
        """
        field = kwargs.pop(self.field, None)
        if field is not None:
            foo = getattr(field, self.operator)
            return foo(self.value[0])
        else:
            return False


@dataclasses.dataclass
class Clause(AbsClause):
    """Composite clause combining multiple sub-clauses.

    This class represents a logical combination of multiple filter clauses,
    such as "clause1 AND clause2" or "NOT clause1".

    Attributes:
        operator: Logical operator to combine clauses
        deps: List of dependent clauses
    """

    operator: LogicalOperator
    deps: list[AbsClause]

    def __call__(
        self,
        doc_name="doc",
        kind: ExpressionFlavor = ExpressionFlavor.ARANGO,
        **kwargs,
    ):
        """Render the composite clause in the target language.

        Args:
            doc_name: Document variable name
            kind: Target expression flavor
            **kwargs: Additional arguments

        Returns:
            str: Rendered clause

        Raises:
            ValueError: If operator and dependencies don't match
        """
        if kind == ExpressionFlavor.ARANGO or kind == ExpressionFlavor.ARANGO:
            return self._cast_generic(doc_name=doc_name, kind=kind)
        elif kind == ExpressionFlavor.PYTHON:
            return self._cast_python(kind=kind, **kwargs)

    def _cast_generic(self, doc_name, kind):
        """Render the clause in a generic format.

        Args:
            doc_name: Document variable name
            kind: Target expression flavor

        Returns:
            str: Rendered clause

        Raises:
            ValueError: If operator and dependencies don't match
        """
        if len(self.deps) == 1:
            if self.operator == LogicalOperator.NOT:
                return f"{self.operator} {self.deps[0](kind=kind, doc_name=doc_name)}"
            else:
                raise ValueError(
                    f" length of deps = {len(self.deps)} but operator is not"
                    f" {LogicalOperator.NOT}"
                )
        else:
            return f" {self.operator} ".join(
                [item(kind=kind, doc_name=doc_name) for item in self.deps]
            )

    def _cast_python(self, kind, **kwargs):
        """Evaluate the clause in Python.

        Args:
            kind: Expression flavor
            **kwargs: Additional arguments

        Returns:
            bool: Evaluation result

        Raises:
            ValueError: If operator and dependencies don't match
        """
        if len(self.deps) == 1:
            if self.operator == LogicalOperator.NOT:
                return not self.deps[0](kind=kind, **kwargs)
            else:
                raise ValueError(
                    f" length of deps = {len(self.deps)} but operator is not"
                    f" {LogicalOperator.NOT}"
                )
        else:
            return OperatorMapping[self.operator](
                [item(kind=kind, **kwargs) for item in self.deps]
            )


@dataclasses.dataclass
class Expression(AbsClause):
    """Factory class for creating filter expressions.

    This class provides methods to create filter expressions from dictionaries
    and evaluate them in different languages.
    """

    @classmethod
    def from_dict(cls, current):
        """Create a filter expression from a dictionary.

        Args:
            current: Dictionary or list representing the filter expression

        Returns:
            AbsClause: Created filter expression

        Example:
            >>> expr = Expression.from_dict({
            ...     "AND": [
            ...         {"field": "age", "cmp_operator": ">=", "value": 18},
            ...         {"field": "status", "cmp_operator": "==", "value": "active"}
            ...     ]
            ... })
        """
        if isinstance(current, list):
            if current[0] in ComparisonOperator:
                return LeafClause(*current)
            elif current[0] in LogicalOperator:
                return Clause(*current)
        elif isinstance(current, dict):
            k = list(current.keys())[0]
            if k in LogicalOperator:
                clauses = [cls.from_dict(v) for v in current[k]]
                return Clause(operator=k, deps=clauses)
            else:
                return LeafClause(**current)

    def __call__(
        self,
        doc_name="doc",
        kind: ExpressionFlavor = ExpressionFlavor.ARANGO,
        **kwargs,
    ):
        """Evaluate the expression in the target language.

        Args:
            doc_name: Document variable name
            kind: Target expression flavor
            **kwargs: Additional arguments

        Returns:
            str: Rendered expression
        """
        pass
