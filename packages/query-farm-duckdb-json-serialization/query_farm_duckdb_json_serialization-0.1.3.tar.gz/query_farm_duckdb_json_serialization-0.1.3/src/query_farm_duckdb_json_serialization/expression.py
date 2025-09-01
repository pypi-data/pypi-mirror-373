from typing import Annotated, Literal, Union

from pydantic import BaseModel, Discriminator, Field, Tag

from .value import AnyValueType, Value, ValueType_struct


class Context(BaseModel):
    """
    Context for parsing expressions, containing information about bound columnns,
    and storing information about the types bound.
    """

    bound_column_names: list[str]
    bound_column_types: dict[str, str]


class BaseWithContext(BaseModel):
    """
    Base class for objects that can have a parse context injected.
    """

    parse_context_: Context | None = Field(default=None, exclude=True)


def inject_context(obj: BaseWithContext, context: Context) -> None:
    """
    Inject the context into the object and its nested BaseWithContext objects,
    this is needed for table and column references to be properly resolved.
    """
    if isinstance(obj, BaseWithContext):
        obj.parse_context_ = context
        for _field_name, field_value in obj.__dict__.items():
            if isinstance(field_value, BaseWithContext):
                inject_context(field_value, context)
            elif isinstance(field_value, list):
                for item in field_value:
                    inject_context(item, context)
            elif isinstance(field_value, dict):
                for item in field_value.values():
                    inject_context(item, context)


class Base(BaseWithContext):
    """
    Base class for all expressions
    """

    alias: str | None = None

    # The location of the expression in the query, used for error reporting.
    query_location: int | None = None


class BoundConstant(Base):
    """
    Represents a constant value in an expression.
    """

    expression_class: Literal["BOUND_CONSTANT"] = "BOUND_CONSTANT"
    type: Literal["VALUE_CONSTANT"] = "VALUE_CONSTANT"
    value: Value

    def sql(self) -> str:
        return self.value.sql()


class BoundColumnRefBinding(BaseModel):
    table_index: int
    column_index: int


class BoundColumnRef(Base, BaseWithContext):
    expression_class: Literal["BOUND_COLUMN_REF"] = "BOUND_COLUMN_REF"
    binding: BoundColumnRefBinding
    return_type: AnyValueType

    def sql(self) -> str:
        assert self.parse_context_
        column_name = self.parse_context_.bound_column_names[self.binding.column_index]
        self.parse_context_.bound_column_types[column_name] = self.return_type.sql()
        return f'"{column_name}"'


comparison_type_to_sql_operator: dict[str, str] = {
    "COMPARE_EQUAL": "=",
    "COMPARE_NOTEQUAL": "!=",
    "COMPARE_LESSTHAN": "<",
    "COMPARE_GREATERTHAN": ">",
    "COMPARE_LESSTHANOREQUALTO": "<=",
    "COMPARE_GREATERTHANOREQUALTO": ">=",
    "COMPARE_DISTINCT_FROM": "IS DISTINCT FROM",
    "COMPARE_NOT_DISTINCT_FROM": "IS NOT DISTINCT FROM",
}

Any = Union[
    BoundConstant,
    BoundColumnRef,
    "BoundComparison",
    "BoundCast",
    "BoundFunction",
    "BoundOperator",
    "BoundCase",
    "BoundBetween",
    "BoundConjunction",
]


class BoundConjunction(Base):
    """
    Represents a conjunction (AND/OR) of multiple expressions.
    """

    expression_class: Literal["BOUND_CONJUNCTION"] = "BOUND_CONJUNCTION"
    type: Literal["CONJUNCTION_AND", "CONJUNCTION_OR"]
    children: list[Any]

    def sql(self) -> str:
        operator = "AND" if self.type == "CONJUNCTION_AND" else "OR"
        return "(" + f" {operator} ".join([child.sql() for child in self.children]) + ")"


class BoundBetween(Base):
    """
    Represents a BETWEEN expression, which checks if a value is within a range.
    """

    expression_class: Literal["BOUND_BETWEEN"] = "BOUND_BETWEEN"
    input: Any
    lower: Any
    upper: Any

    def sql(self) -> str:
        return f"{self.input.sql()} BETWEEN {self.lower.sql()} AND {self.upper.sql()}"


class BoundCast(Base):
    """
    Represents a CAST expression, which converts a value from one type to another.
    """

    expression_class: Literal["BOUND_CAST"] = "BOUND_CAST"
    child: Any
    return_type: AnyValueType

    def sql(self) -> str:
        return f"CAST({self.child.sql()} AS {self.return_type.sql()})"


class BoundCaseCaseCheck(BaseModel):
    when_expr: Any
    then_expr: Any


class BoundCase(Base):
    """
    Represents a CASE expression, which evaluates a series of conditions and returns
    a corresponding value based on the first true condition.
    """

    expression_class: Literal["BOUND_CASE"] = "BOUND_CASE"
    case_checks: list[BoundCaseCaseCheck]
    else_expr: Any | None = None

    def sql(self) -> str:
        case_checks = [
            f"WHEN {case_check.when_expr.sql()} THEN {case_check.then_expr.sql()}"
            for case_check in self.case_checks
        ]
        if self.else_expr:
            case_checks.append(f"ELSE {self.else_expr.sql()}")

        return "CASE " + " ".join(case_checks) + " END"


class BoundOperator(Base):
    """
    Represents an operator expression, which can be a unary or binary operation,
    or a comparison operation.
    """

    expression_class: Literal["BOUND_OPERATOR"] = "BOUND_OPERATOR"
    type: Literal[
        "OPERATOR_IS_NULL",
        "OPERATOR_IS_NOT_NULL",
        "COMPARE_IN",
        "COMPARE_NOT_IN",
        "OPERATOR_NOT",
    ]
    children: list[Any]

    def sql(self) -> str:
        if self.type in ("OPERATOR_IS_NULL", "OPERATOR_IS_NOT_NULL"):
            operation = "IS NULL" if self.type == "OPERATOR_IS_NULL" else "IS NOT NULL"
            return self.children[0].sql() + " " + operation
        elif self.type in ("COMPARE_IN", "COMPARE_NOT_IN"):
            first, *rest = self.children
            operation = "IN" if self.type == "COMPARE_IN" else "NOT IN"
            return f"{first.sql()} {operation} ({', '.join([child.sql() for child in rest])})"
        elif self.type == "OPERATOR_NOT":
            assert len(self.children) == 1
            return f"NOT {self.children[0].sql()}"
        else:
            raise ValueError(f"Unsupported operator type: {self.type}")


class BoundFunctionFunctionData(BaseModel):
    variable_return_type: AnyValueType


class BoundFunction(Base):
    """
    Represents a function call in an expression, which can include user-defined functions,
    built-in functions, and operators.
    """

    expression_class: Literal["BOUND_FUNCTION"] = "BOUND_FUNCTION"
    type: Literal["BOUND_FUNCTION"] = "BOUND_FUNCTION"
    name: str
    return_type: AnyValueType
    children: list[Any]
    arguments: list[AnyValueType] | None = None
    original_arguments: list[AnyValueType] | None = None
    has_serialize: bool
    is_operator: bool
    function_data: BoundFunctionFunctionData | None = None

    def sql(self) -> str:
        if self.name == "struct_pack":
            assert self.function_data is not None
            result_struct = self.function_data.variable_return_type
            assert isinstance(result_struct, ValueType_struct)

            return (
                self.name
                + "("
                + ", ".join(
                    [
                        f"{child_type.first} := {child.sql()}"
                        for child, child_type in zip(
                            self.children,
                            result_struct.type_info.child_types,
                            strict=True,
                        )
                    ]
                )
                + ")"
            )
        elif self.is_operator:
            return self.name.join([child.sql() for child in self.children])
        else:
            return f"{self.name}({', '.join([child.sql() for child in self.children])})"


class BoundComparison(Base):
    """
    Represents a comparison expression, which compares two expressions using
    various comparison operators.
    """

    left: Any
    right: Any

    type: Literal[
        "COMPARE_EQUAL",
        "COMPARE_NOTEQUAL",
        "COMPARE_LESSTHAN",
        "COMPARE_GREATERTHAN",
        "COMPARE_LESSTHANOREQUALTO",
        "COMPARE_GREATERTHANOREQUALTO",
        "COMPARE_DISTINCT_FROM",
        "COMPARE_NOT_DISTINCT_FROM",
    ]

    def sql(self) -> str:
        operator = comparison_type_to_sql_operator.get(self.type)
        if operator is None:
            raise ValueError(f"Unsupported comparison type: {self.type}")

        return f"{self.left.sql()} {operator} {self.right.sql()}"


Contents = Annotated[
    Annotated[BoundConstant, Tag("BOUND_CONSTANT")]
    | Annotated[BoundColumnRef, Tag("BOUND_COLUMN_REF")]
    | Annotated[BoundComparison, Tag("BOUND_COMPARISON")]
    | Annotated[BoundCast, Tag("BOUND_CAST")]
    | Annotated[BoundFunction, Tag("BOUND_FUNCTION")]
    | Annotated[BoundOperator, Tag("BOUND_OPERATOR")]
    | Annotated[BoundCase, Tag("BOUND_CASE")]
    | Annotated[BoundBetween, Tag("BOUND_BETWEEN")]
    | Annotated[BoundConjunction, Tag("BOUND_CONJUNCTION")],
    Discriminator(lambda v: v.get("expression_class")),
]


class Expression(BaseWithContext):
    """
    Represents a serialized expression, which can be used to store and transfer
    expressions in a structured format.
    """

    # The parsed contents of the serialized expression.
    contents: Contents


def expression_to_sql(
    *,
    expression: dict[str, Any],
    bound_column_names: list[str],
    bound_column_types: dict[str, str],
) -> str:
    """
    Convert a DuckDB serialized expression back into SQL, with the types of the
    columns tracked.
    """

    context = Context.model_construct(
        bound_column_names=bound_column_names,
        bound_column_types=bound_column_types,
    )

    base = Expression.model_validate({"contents": expression})
    inject_context(base, context)
    return base.contents.sql()


def convert_to_sql(
    source: list[dict[str, Any]], bound_column_names: list[str]
) -> tuple[str, dict[str, str]]:
    bound_column_types: dict[str, str] = {}
    sql = " AND ".join(
        [
            expression_to_sql(
                expression=filter,
                bound_column_names=bound_column_names,
                bound_column_types=bound_column_types,
            )
            for filter in source
        ]
    )
    return sql, bound_column_types
