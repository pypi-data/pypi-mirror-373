from typing import Literal, get_type_hints

from linq.schema.workflow_api import Comparison, Conditional

# NOTE: Define these statically s.t. SDK gets nice type hints
ComparisonOperator = Literal["==", "!=", "<", "<=", ">", ">=", "in", "not in"]
ElseComparison = Literal["Else"]

# Check that these types match the types in the API Schema

assert set(ComparisonOperator.__args__) == set(
    get_type_hints(Comparison)["operator"].__args__
), "ComparisonOperator has changed in the API schema! Update the static type to match"  # pragma: no cover
assert any(
    (
        hasattr(arg, "__args__") and arg.__args__ == ElseComparison.__args__  # type: ignore
        for arg in get_type_hints(Conditional)["comparison"].__args__
    )
), "ElseComparison has changed in the API schema! Update the static type to match"  # pragma: no cover
