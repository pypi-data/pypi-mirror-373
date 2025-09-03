"""Types associated with the lower-level concerns represented in the Viv DSL's abstract syntax trees.

This module and `content_public_schemas.py` together define the public, stable schema for Viv compiled
content bundles. The schemas capture the compiler's emitted JSON shapes, which are mirrored in the
corresponding runtime type definitions, assuming the same version number for the compiler and runtime.
As such, the schemas constitute a reliable contract between the compiler and any Viv runtime.
"""

from __future__ import annotations

from typing import Union, Annotated, TypeAlias, Literal, TYPE_CHECKING
from typing_extensions import TypedDict
from pydantic import Field
from viv_compiler.backports import StrEnum


if TYPE_CHECKING:
    # Imported for static checking only; referenced by string at runtime to avoid cycles
    from .content_public_schemas import Reaction, RoleName, TropeName

# Union specifying all the Viv expression types
Expression: TypeAlias = Annotated[
    Union[
        "AdapterFunctionCall",
        "ArithmeticExpression",
        "Assignment",
        "BoolField",
        "ChanceExpression",
        "Comparison",
        "Conditional",
        "Conjunction",
        "Disjunction",
        "EntityReference",
        "Enum",
        "EvalFailSafeField",
        "FloatField",
        "IntField",
        "ListField",
        "LocalVariableReference",
        "Loop",
        "MembershipTest",
        "NullField",
        "ObjectField",
        "Reaction",
        "RoleUnpacking",
        "StringField",
        "TemplateStringField",
        "TropeFitExpression",
    ],
    Field(discriminator="type"),
]


# Enum containing discriminators for each Viv expression type
class ExpressionDiscriminator(StrEnum):
    ADAPTER_FUNCTION_CALL = "adapterFunctionCall"
    ASSIGNMENT = "assignment"
    ARITHMETIC_EXPRESSION = "arithmeticExpression"
    BINDING = "binding"
    BOOL = "bool"
    CHANCE_EXPRESSION = "chanceExpression"
    COMPARISON = "comparison"
    CONDITIONAL = "conditional"
    CONJUNCTION = "conjunction"
    DISJUNCTION = "disjunction"
    ENTITY_REFERENCE = "entityReference"
    ENUM = "enum"
    EVAL_FAIL_SAFE = "evalFailSafe"
    FLOAT = "float"
    INT = "int"
    LIST = "list"
    LOCAL_VARIABLE_REFERENCE = "localVariableReference"
    LOOP = "loop"
    MEMBERSHIP_TEST = "membershipTest"
    NULL_TYPE = "nullType"
    OBJECT = "object"
    REACTION = "reaction"
    ROLE_UNPACKING = "roleUnpacking"
    STRING = "string"
    TEMPLATE_STRING = "templateString"
    TROPE_FIT_EXPRESSION = "tropeFitExpression"


# Mixin for expression types that may be negated
class NegatableExpression(TypedDict, total=False):
    """Mixin for expression types that may be negated."""
    # Whether to negate the result of the expression. Only present when `True`.
    negated: Literal[True]


class AdapterFunctionCall(NegatableExpression):
    """A Viv adapter function call, which parameterizes a call to some function that must be exposed in the target
    application's Viv adapter.

    For instance, a Viv author might specify a function call in an action such as
    `~transport(@person.id, @destination.id)`, in which case there must be a function
    `transport()` exposed in the adapter. The Viv runtime confirms the existence of all
    referenced function names during adapter initialization.
    """
    # Discriminant for a Viv adapter function call
    type: Literal[ExpressionDiscriminator.ADAPTER_FUNCTION_CALL]
    # The actual expression value
    value: AdapterFunctionCallValue


class AdapterFunctionCallValue(TypedDict, total=False):
    """The actual expression value for a Viv function call."""
    # The name of the target function. There must be a function stored in the target
    # application's Viv adapter, via a key by this same name.
    name: AdapterFunctionName
    # An ordered list of Viv expressions whose evaluations will be passed as
    # arguments to the function, in that same order.
    args: list[Expression]
    # Whether the function call should fail safely (i.e., evaluate to a falsy value) if the
    # result of the function call is nullish. This field is only present when `True`.
    resultFailSafe: Literal[True]


# The name for a function targeted by a Viv function call
AdapterFunctionName = str


class ArithmeticExpression(TypedDict):
    """A Viv arithmetic expression, which accepts two numeric operands and evaluates to a number."""
    # Discriminant for a Viv arithmetic expression
    type: Literal[ExpressionDiscriminator.ARITHMETIC_EXPRESSION]
    # The actual expression value
    value: ArithmeticExpressionValue


class ArithmeticExpressionValue(TypedDict):
    """The actual expression value for a Viv arithmetic expression."""
    # An expression whose evaluation will be used as the left operand in the arithmetic expression
    left: Expression
    # The arithmetic operator
    operator: ArithmeticOperator
    # An expression whose evaluation will be used as the right operand in the arithmetic expression
    right: Expression


# Enum of arithmetic operators supported by Viv
ArithmeticOperator = Literal["+", "-", "*", "/"]


class Assignment(TypedDict):
    """A Viv assignment (or update)."""
    # Discriminant for a Viv assignment
    type: Literal[ExpressionDiscriminator.ASSIGNMENT]
    # The actual expression value
    value: AssignmentValue


class AssignmentValue(TypedDict):
    """The actual expression value for a Viv assignment."""
    # An expression whose evaluation will be used as the left operand in the assignment/update
    left: Expression
    # The assignment/update operator
    operator: AssignmentOperator
    # An expression whose evaluation will be used as the right operand in the assignment/update
    right: Expression


# Enum containing the Viv assignment (and update) operators
AssignmentOperator = Literal["=", "+=", "-=", "*=", "/=", "append", "remove"]


class BoolField(TypedDict):
    """A Viv boolean."""
    # Discriminant for a Viv boolean
    type: Literal[ExpressionDiscriminator.BOOL]
    # The boolean literal to which this expression will evaluate
    value: bool


class ChanceExpression(TypedDict):
    """A Viv chance expression.

    This is a kind of condition that evaluates to True if the specified probability value (a number
    between 0.0 and 1.0) exceeds a pseudorandom number generated by the Viv interpreter.
    """
    # Discriminant for a Viv chance expression
    type: Literal[ExpressionDiscriminator.CHANCE_EXPRESSION]
    # The specified probability, which the compiler guarantees to be a number in the range [0, 1]
    value: float


class Comparison(NegatableExpression):
    """A Viv comparison, whereby two values are compared using a comparator."""
    # Discriminant for a Viv comparison
    type: Literal[ExpressionDiscriminator.COMPARISON]
    # The actual expression value
    value: ComparisonValue


class ComparisonValue(TypedDict):
    """The actual expression value for a Viv comparison."""
    # An expression whose evaluation will serve as the left operand in the comparison
    left: Expression
    # The comparison operator
    operator: Comparator
    # An expression whose evaluation will serve as the right operand in the comparison
    right: Expression


# Enum containing the Viv comparison operators
Comparator = Literal["==", ">", ">=", "<", "<=", "!="]


class Conditional(TypedDict):
    """A Viv conditional expression, allowing for branching based on the value of a test."""
    # Discriminant for a Viv conditional
    type: Literal[ExpressionDiscriminator.CONDITIONAL]
    # The actual expression value
    value: ConditionalValue


class ConditionalValue(TypedDict, total=False):
    """The actual expression value for a Viv conditional."""
    # The condition that will be tested, which holds if its evaluation is truthy
    condition: Expression
    # A list of expressions that will be evaluated/executed should the condition hold
    consequent: list[Expression]
    # If an author has provided an alternative body (via an `else` clause), a list
    # of expressions that will be evaluated/executed should the condition not hold.
    alternative: list[Expression]


class Conjunction(NegatableExpression):
    """A Viv conjunction.

    This kind of expression takes multiple expressions as operands and evaluates to
    `True` if and only if all the respective expressions evaluate to truthy values.
    """
    # Discriminant for a Viv conjunction
    type: Literal[ExpressionDiscriminator.CONJUNCTION]
    # The actual expression value
    value: ConjunctionValue


class ConjunctionValue(TypedDict):
    """The actual expression value for a Viv conjunction."""
    # A list of expressions that will be evaluated in turn to determine the result
    # of the conjunction. Note that the interpreter stops evaluating as soon as a
    # falsy evaluation is encountered.
    operands: list[Expression]


class Disjunction(NegatableExpression):
    """A Viv disjunction.

    This kind which takes multiple expressions and evaluates to `True` if and only
    if at least one of the respective expressions evaluate to a truthy value.
    """
    # Discriminant for a Viv disjunction
    type: Literal[ExpressionDiscriminator.DISJUNCTION]
    # The actual expression value
    value: DisjunctionValue


class DisjunctionValue(TypedDict):
    """The actual expression value for a Viv disjunction."""
    # A list of expressions that will be evaluated in turn to determine the result
    # of the disjunction. Note that the interpreter stops evaluating as soon as a
    # truthy evaluation is encountered.
    operands: list[Expression]


class EntityReference(NegatableExpression):
    """A Viv entity reference, structured as an anchor role and a path to a specific property value.

    Usually, the property is on the entity cast into the anchor role, but this is not the case if
    the reference contains a pointer. For instance, `@person.boss->boss->traits.cruel` would return
    the value stored at the path `traits.cruel` on the boss of the boss of the entity cast in the
    anchor role `@person`.

    Note that the compiler currently prevents an author from anchoring an entity reference in a
    symbol role, which allows the interpreter to assume that the anchor role binds an entity.

    Also note that references anchored in global variables, e.g. `$foo.bar.baz`, are compiled
    to entities anchored in role references -- this is because `$` is really just syntactic
    sugar for `@this.scratch.`.
    """
    # Discriminant for a Viv reference
    type: Literal[ExpressionDiscriminator.ENTITY_REFERENCE]
    # The actual expression value
    value: EntityReferenceValue


class EntityReferenceValue(TypedDict):
    """The actual expression value for a Viv entity reference."""
    # The name of the role that anchors this reference
    anchor: RoleName
    # If applicable, the path to a specified property value. If the reference is just to
    # the entity itself, this will be an empty list. Otherwise, it will specify a path
    # to a specific property value, either on that entity or another one (via a pointer).
    path: list[ReferencePathComponent]


class ReferencePathComponentPropertyName(TypedDict, total=False):
    """A component of a Viv reference path specifying a property to access."""
    # Discriminant for a property-name reference path component
    type: Literal[ReferencePathComponentDiscriminator.REFERENCE_PATH_COMPONENT_PROPERTY_NAME]
    # The name of the property to access
    name: str
    # Whether this step should use the eval fail-safe. If the property is missing/null,
    # the interpreter should return the eval fail-safe signal. Present only when `True`.
    failSafe: Literal[True]


class ReferencePathComponentPointer(TypedDict, total=False):
    """A component of a Viv reference path specifying a pointer to dereference."""
    # Discriminant for a pointer reference path component
    type: Literal[ReferencePathComponentDiscriminator.REFERENCE_PATH_COMPONENT_POINTER]
    # The name of the property to access in the entity data of the entity targeted by the pointer
    propertyName: str
    # Whether this pointer step should use the eval fail-safe. If the target isn't an entity or the
    # pointed property is missing/null, the interpreter should return the eval fail-safe signal.
    # Present only when `True`.
    failSafe: Literal[True]


class ReferencePathComponentLookup(TypedDict, total=False):
    """A component of a Viv reference path specifying a property lookup or an array access.

    The key/index can be specified by an arbitrary Viv expression.
    """
    # Discriminant for a lookup reference path component
    type: Literal[ReferencePathComponentDiscriminator.REFERENCE_PATH_COMPONENT_LOOKUP]
    # An expression that should evaluate to a valid property key (string or integer)
    key: Expression
    # Whether this lookup should use the eval fail-safe. If the key/index yields a missing/null value,
    # the interpreter should return the eval fail-safe signal. Present only when `True`.
    failSafe: Literal[True]


class ReferencePathComponentDiscriminator(StrEnum):
    """Enum containing discriminators for the possible reference path components."""
    # Discriminant for a property-name reference path component
    REFERENCE_PATH_COMPONENT_PROPERTY_NAME = "referencePathComponentPropertyName"
    # Discriminant for a pointer reference path component
    REFERENCE_PATH_COMPONENT_POINTER = "referencePathComponentPointer"
    # Discriminant for a lookup reference path component
    REFERENCE_PATH_COMPONENT_LOOKUP = "referencePathComponentLookup"


# A component in a Viv reference path
ReferencePathComponent = Union[
    ReferencePathComponentPropertyName,
    ReferencePathComponentPointer,
    ReferencePathComponentLookup,
]


class Enum(TypedDict):
    """A Viv enum.

    Enums are resolved by the target application at runtime.
    """
    # Discriminant for a Viv enum
    type: Literal[ExpressionDiscriminator.ENUM]
    # The actual expression value
    value: EnumValue


class EnumValue(TypedDict):
    """The actual expression value for a Viv enum."""
    # The name of the enum. This must be resolvable by the target application at runtime.
    name: EnumName
    # Whether the enum value should be scaled. In Viv, an enum value will by default be scaled according to the
    # current size of the simulation timestep in the target application. (Technically, the target application
    # could scale according to some other principle.) This is achieved by using the `#ENUM_NAME` syntax, as
    # opposed to the unscaled `##ENUM_NAME` notation. This notation supports a pattern where effects will have
    # proportionally more weight when the simulation fidelity is coarser, i.e., when fewer actions are being
    # performed in general. That said, even in such cases, an author may not want their enum to scale -- e.g.,
    # in an effect for a "love at first sight" action or a traumatic incident -- and thus the `##ENUM_NAME`
    # notation remains available.
    scaled: bool
    # Whether to flip the sign of a numeric value associated with the enum.
    minus: bool


# A unique label for an enum value
EnumName = str


class EvalFailSafeField(TypedDict):
    """The Viv eval fail-safe operator.

    A Viv author may specify an attempt to access a property that may not exist, safely,
    via the eval fail-safe operator `?`, as in this example: `@foo.bar?.baz`.
    """
    # Discriminant for the Viv eval fail-safe operator
    type: Literal[ExpressionDiscriminator.EVAL_FAIL_SAFE]


class FloatField(TypedDict):
    """A Viv floating-point number."""
    # Discriminant for a Viv floating-point number
    type: Literal[ExpressionDiscriminator.FLOAT]
    # The float literal to which this expression will evaluate
    value: float


class IntField(TypedDict):
    """A Viv integer."""
    # Discriminant for a Viv integer
    type: Literal[ExpressionDiscriminator.INT]
    # The integer literal to which this expression will evaluate
    value: int


class ListField(TypedDict):
    """A Viv list, defined as an ordered list of Viv expressions.

    Once evaluated, the result will contain the respective evaluations of the expressions, in that same order.
    """
    # Discriminant for a Viv list
    type: Literal[ExpressionDiscriminator.LIST]
    # The actual expression value
    value: list[Expression]


class LocalVariableReference(NegatableExpression):
    """A Viv local-variable reference, meaning a reference anchored in a local variable.

    This kind of expression is structured as an anchor (the local variable name) with a subsequent path
    to a specific property value. If a local variable is bound to an entity, this works just like an
    entity reference — common when looping over role unpackings. Local variables may, however, hold
    arbitrary values to which authors can refer.
    """
    # Discriminant for a Viv local-variable reference
    type: Literal[ExpressionDiscriminator.LOCAL_VARIABLE_REFERENCE]
    # The actual expression value
    value: LocalVariableReferenceValue


class LocalVariableReferenceValue(TypedDict):
    """The actual expression value for a Viv local-variable reference."""
    # The name of the local variable that anchors this reference
    anchor: VariableName
    # If applicable, the path to a specified property value. If the reference is just to the
    # variable's value itself, this will be an empty list. Otherwise, it specifies the path.
    path: list[ReferencePathComponent]


class Loop(TypedDict):
    """A Viv loop, allowing for iteration over some iterable value."""
    # Discriminant for a Viv loop
    type: Literal[ExpressionDiscriminator.LOOP]
    # The actual expression value
    value: LoopValue


class LoopValue(TypedDict):
    """The actual expression value for a Viv loop."""
    # An expression that should evaluate to a value that is iterable in the runtime at hand.
    iterable: Expression
    # Name of the variable to which each member of the iterable is assigned
    # on its respective iteration of the loop.
    variable: VariableName
    # The body of the loop, structured as a list of expressions that will each be interpreted,
    # in order, on each iteration. These body expressions can reference the loop variable,
    # allowing for Viv code that acts on each member of an iterable.
    body: list[Expression]


# The name for a variable used in an assignment or a loop
VariableName = str


class MembershipTest(NegatableExpression):
    """A Viv membership test.

    This kind of expression takes two expressions as operands and evaluates to `True` if the evaluation
    of the first expression is a member of the (iterable) evaluation of the second expression.
    """
    # Discriminant for a Viv membership test
    type: Literal[ExpressionDiscriminator.MEMBERSHIP_TEST]
    # The actual expression value
    value: MembershipTestValue


class MembershipTestValue(TypedDict):
    """The actual expression value for a Viv membership test."""
    # An expression whose evaluation will be used as the left operand in the membership test
    left: Expression
    # Always the membership-test operator `in`. This field isn't used by the interpreter, but it's
    # included here as a convenience for the compiler, where it's easier to maintain parity in the
    # shape of all relational expressions.
    operator: Literal["in"]
    # An expression whose evaluation will be used as the right operand in the membership test
    right: Expression


class NullField(TypedDict):
    """A Viv null value."""
    # Discriminant for a Viv null value
    type: Literal[ExpressionDiscriminator.NULL_TYPE]
    # Python's `None`, which serializes to JSON's `null`. In any Viv runtime, expressions of this
    # type evaluate to the null-like value in the language at hand.
    value: None


class ObjectField(TypedDict):
    """A Viv object literal.

    Expressions of this type maps keys (string literals) to Viv expressions. Once evaluated,
    the result will map those same keys to the respective evaluations of the Viv expressions.
    """
    # Discriminant for a Viv object literal
    type: Literal[ExpressionDiscriminator.OBJECT]
    # The actual expression value
    value: dict[str, "Expression"]


class RoleUnpacking(TypedDict):
    """A Viv "role unpacking" expression.

    This kind of expression expands a role into an array containing all the entities cast into
    that role. This allows for iterating over multiple entities cast into the same role, e.g.,
    to carry out effects on each.
    """
    # Discriminant for a Viv role-unpacking expression
    type: Literal[ExpressionDiscriminator.ROLE_UNPACKING]
    # The actual expression value
    value: RoleName


class StringField(TypedDict):
    """A Viv string literal."""
    # Discriminant for a Viv string literal
    type: Literal[ExpressionDiscriminator.STRING]
    # The string literal to which this expression will evaluate
    value: str


class TemplateStringField(TypedDict):
    """A Viv templated string.

    This kind of expression is structured as an ordered list of string literals and string-producing
    references, the evaluations of which are concatenated to form the rendered string.
    """
    # Discriminant for a Viv templated string
    type: Literal[ExpressionDiscriminator.TEMPLATE_STRING]
    # The actual expression value
    value: list[Union[str, EntityReference, RoleUnpacking, LocalVariableReference]]


class TropeFitExpression(NegatableExpression):
    """A Viv "trope fit" expression.

    This kind of expression evaluates to `True` if the trope holds with the given arguments.
    """
    # Discriminant for a Viv trope-fit expression
    type: Literal[ExpressionDiscriminator.TROPE_FIT_EXPRESSION]
    # The actual expression value
    value: TropeFitExpressionValue


class TropeFitExpressionValue(TypedDict):
    """The actual expression value for a Viv trope-fit expression."""
    # The name of the trope that will be used for the test
    tropeName: TropeName
    # An ordered list of expressions whose evaluations will be passed as the
    # arguments for the test. These must correspond to the trope's parameters.
    args: list[Expression]
