"""Types associated with the higher-level concerns represented in Viv compiled content bundles.

This module and `dsl_public_schemas.py` together define the public, stable schema for Viv compiled
content bundles. The schemas capture the compiler's emitted JSON shapes, which are mirrored in the
corresponding runtime type definitions, assuming the same version number for the compiler and runtime.
As such, the schemas constitute a reliable contract between the compiler and any Viv runtime.
"""

from __future__ import annotations

from typing import Union, Literal, TYPE_CHECKING
from typing_extensions import TypedDict, NotRequired

if TYPE_CHECKING:
    from .dsl_public_schemas import (
        Enum,
        EnumName,
        Expression,
        ExpressionDiscriminator,
        FloatField,
        IntField,
        ListField,
        ObjectField,
        StringField,
        TemplateStringField,
        VariableName,
    )


class CompiledContentBundle(TypedDict):
    """A content bundle in the format produced by the Viv compiler."""
    # Metadata for the content bundle, which is currently used for validation purposes
    meta: CompiledContentBundleMetadata
    # Trope definitions, keyed by name
    tropes: dict[TropeName, TropeDefinition]
    # Action definitions, keyed by name
    actions: dict[ActionName, ActionDefinition]


class CompiledContentBundleMetadata(TypedDict):
    """Metadata on the content bundle.

    This metadata attaches a Viv version number to the content bundle, which guarantees
    compatibility with any Viv runtime with the same version number.

    The metadata here is also used to support validation during initialization of a target application's
    Viv adapter by, e.g., confirming that any referenced enums and adapter functions actually exist.
    """
    # The Viv compiler version at the time of compiling this content bundle. If this
    # version number corresponds to the version number for a Viv runtime, the content
    # bundle is guaranteed to be compatible with that runtime.
    vivVersion: str
    # An array containing the names of all enums referenced in the content bundle. This is
    # used for validation during the initialization of a target application's Viv adapter.
    referencedEnums: list[EnumName]
    # An array containing the names of all adapter functions referenced in the
    # content bundle. This is used for validation during the initialization of
    # a target application's Viv adapter.
    referencedFunctionNames: list[AdapterFunctionName]
    # An array specifying all role definitions carrying the `item` label. This is used
    # for validation during the initialization of a target application's Viv adapter.
    itemRoles: list[CompiledContentBundleMetadataRoleEntry]
    # An array specifying all role definitions carrying the `build` label. This is used
    # for validation during the initialization of a target application's Viv adapter.
    buildRoles: list[CompiledContentBundleMetadataRoleEntry]
    # An array specifying all reactions that are constrained by the time of day. This is used
    # for validation during the initialization of a target application's Viv adapter.
    timeOfDayConstrainedReactions: list[CompiledContentBundleMetadataTimeOfDayConstrainedReaction]


class CompiledContentBundleMetadataRoleEntry(TypedDict):
    """A simple record of a case of a role carrying a `build` label, used for validation purposes."""
    # The name of the action containing a role carrying the `build` label
    action: ActionName
    # The name of the role carrying the `build` label
    role: RoleName


class CompiledContentBundleMetadataTimeOfDayConstrainedReaction(TypedDict):
    """A simple record of a case of reaction that is constrained by the time of day, used for validation purposes."""
    # The name of the action containing a reaction that is constrained by the time of day
    action: ActionName
    # The name of the target action of the reaction that is constrained by the time of day
    reaction: ActionName


# Unique name for an arbitrary function exposed in a target application's Viv adapter
AdapterFunctionName = str


class TropeDefinition(TypedDict):
    """A definition for a Viv trope (reusable bundle of conditions)."""
    # The (unique) name of the trope
    name: TropeName
    # The parameters for the trope. These take entity references as arguments,
    # allowing the conditions to refer to those entities.
    params: list[TropeParamName]
    # The ordered set of conditions composing the trope
    conditions: list[Expression]


# A unique name for a trope
TropeName = str

# A unique trope parameter name
TropeParamName = str


class ActionDefinition(TypedDict):
    """A compiled definition for a Viv action."""
    # The (unique) name of the action
    name: ActionName
    # Whether this action may only be targeted as a queued reaction (True if so)
    special: bool
    # Name of the parent action from which this one inherited, if any. This field is
    # not currently used by the runtimes, but it can sometimes be useful for debugging.
    parent: ActionName | None
    # Tags on the action, whose purposes will depend on the target application
    tags: ListField
    # Mapping from the names of the roles associated with this action to their respective role definitions
    roles: dict[RoleName, RoleDefinition]
    # Definition for a simple templated string describing this action in a sentence or so
    gloss: StringField | TemplateStringField | None
    # Definition for a more detailed templated string describing this action in a paragraph or so
    report: TemplateStringField | None
    # Preconditions for the action, grouped by role name. A precondition is an expression that
    # must hold (i.e., evaluate to a truthy value) in order for an action to be performed with
    # a prospective cast.
    preconditions: dict[RoleName, list[WrappedExpression]]
    # An ordered set of expressions that prepare a set of temporary variables that may be referenced
    # downstream in the action definition. These temporary variables can be referenced by an author
    # using the `$` sigil, but this is syntactic sugar for `@this.scratch` — e.g., `$foo` is equivalent
    # to `@this.scratch.foo`.
    scratch: list[Expression]
    # An ordered set of expressions that, when executed, cause updates to the target application state
    effects: list[WrappedExpression]
    # A set of expressions that each produce a reaction when evaluated. A reaction specifies an action that
    # may be queued up for some time in the future, should an instance of the one at hand be performed.
    reactions: list[WrappedExpression]
    # Specifications for yielding numeric salience values for the action
    saliences: Saliences
    # Specifications for yielding subjective associations for the action
    associations: Associations
    # Embargo directives, which are authorial levers for controlling the frequency
    # with which an action will be performed in the target application.
    embargoes: list[EmbargoDeclaration]
    # Definition for this role's initiator, copied from the `roles` field,
    # where it also lives, into this top-level property as an optimization.
    initiator: RoleDefinition


# A unique name for an action
ActionName = str


class RoleDefinition(TypedDict, total=False):
    """A definition for a role in a Viv action definition."""
    # A name for this role, unique only within the associated action definition
    name: RoleName
    # The minimum number of entities to be cast into this role
    min: int
    # The maximum number of entities to be cast into this role
    max: int
    # If specified, the chance that a qualifying entity will be cast into the role. This field was
    # first implemented to support a pattern of specifying how likely it is that a given nearby
    # character will witness an action, which can be accomplished by defining a `bystander` role
    # with a high `max` and a specified `chance` value. Chance values are always guaranteed to
    # fall between `0.0` and `1.0`.
    chance: float | None
    # A mean on which to anchor a distribution from which will be sampled the number of entities
    # to cast into the role. This distribution must also be parameterized by a `sd` value.
    mean: float | None
    # Standard deviation for a distribution from which will be sampled the number of entities
    # to cast into the role. This distribution must also be parameterized by a `mean` value.
    sd: float | None
    # If specified, a directive specifying the pool of entities who may be cast into this role
    # at a given point in time, given an initiator and possibly other prospective role bindings.
    pool: BindingPool | None
    # The name of this role's parent, if any, in the dependency tree that is used
    # during role casting. This dependency tree is used to optimize this process.
    parent: RoleName | None
    # The names of this role's children, if any, in the dependency tree that is
    # used during casting. This dependency tree is used to optimize this process.
    children: list[RoleName]
    # Whether a character must be cast in this role
    character: bool
    # Whether an item must be cast in this role
    item: bool
    # Whether another action must be cast in this role
    action: bool
    # Whether a location must be cast in this role
    location: bool
    # Whether a symbol (some kind of literal value) must be cast in this role
    symbol: bool
    # Whether an entity cast in this role is initiator of the associated action
    initiator: bool
    # Whether an entity cast in this role is a co-initiator of the associated action
    partner: bool
    # Whether an entity cast in this role is a recipient of the associated action
    recipient: bool
    # Whether an entity cast in this role is an uninvolved witness to the associated action
    bystander: bool
    # Whether an entity cast in this role is a character who is not physically present for the associated action
    absent: bool
    # Whether this role must be precast via reaction bindings. See Reaction docs for details
    precast: bool
    # Whether the entity cast in this role is to be constructed as a result of the
    # associated action. Build roles are always accompanied by an entity recipe.
    build: bool
    # For `build` roles only, an expression that evaluates to the recipe for constructing an entity
    # to be cast into the role. The format used here is completely dependent on the target application,
    # but Viv allows authors to specify an arbitrary Viv object. When it's time to build a new entity,
    # the entity recipe will be passed to the `buildEntity()` adapter function, which is tasked with
    # actually constructing the entity.
    entityRecipe: NotRequired[ObjectField]


# A name for an action role (unique only within its action definition)
RoleName = str


class BindingPool(TypedDict):
    """A directive specifying the pool of entities who may be cast into a role at a given
    point in time, given an initiator and possibly other prospective role bindings.
    """
    # The Viv expression that should evaluate to a binding pool
    body: Expression
    # Whether the binding pool is uncachable. A binding pool is cachable so long as the associated
    # pool declaration does not reference a non-initiator role, in which case the role pool would
    # have to be re-computed if the parent role[s] are re-cast (which never happens with an
    # initiator role). When a binding pool is cached, it is not recomputed even as other
    # non-initiator roles are re-cast.
    uncachable: bool


class Reaction(TypedDict):
    """A Viv reaction expression.

    A reaction specifies an action that may be queued up for some time in the future,
    should an instance of the one at hand be performed.
    """
    # Discriminator for Viv reaction expressions
    type: Literal[ExpressionDiscriminator.REACTION]
    # The actual expression value
    value: ReactionValue


class ReactionValue(TypedDict):
    """A specification of the parameters defining a reaction."""
    # The name of the target action, i.e., the one queued up by this reaction
    actionName: ActionName
    # Specification for how to precast entities in (a subset of) the roles of the target action
    bindings: list[ReactionBinding]
    # Parameterization of the reaction along various options
    options: ReactionOptions


class ReactionBinding(TypedDict):
    """An expression specifying how to precast a particular role in a reaction's target action."""
    # Discriminator for Viv binding expressions
    type: Literal[ExpressionDiscriminator.BINDING]
    # The actual expression value
    value: ReactionBindingValue


class ReactionBindingValue(TypedDict):
    """Value of a binding expression."""
    # The name of the role in the target action that will be precast via this binding
    role: RoleName
    # An expression that should evaluate to the entity to precast in the role associated with this binding
    entity: Expression


class ReactionOptions(TypedDict, total=False):
    """A set of options parameterizing a reaction."""
    # An expression that should evaluate to a boolean value indicating whether the reaction will queue its
    # target action urgently. (The evaluated value will be cast to a boolean, so authors should be careful
    # here.) Urgent actions receive the highest priority in action queueing.
    urgent: Expression
    # An expression that should evaluate to a numeric value specifying the priority of the queued
    # action. Within a given queue group (urgent or non-urgent), queued actions are targeted in
    # descending order of priority.
    priority: Expression
    # An expression that should evaluate to a string or number constituting a *kill code*. (If a number is
    # produced, it will be coerced into a string, for use as an object key.) When a queued action is performed,
    # its kill code (if any) is asserted, which causes all other queued actions with the same kill code to be
    # dequeued. This supports an authoring pattern where multiple competing reaction alternatives are queued
    # at the same time, each with the same kill code, where only the first one to be targeted successfully
    # will actually be performed. As a concrete example, imagine a character who is punched by someone and
    # whose personality is such that fighting back and running away would each be believable in their own
    # right. Instead of selecting one exclusively, an author can queue both and let it play out by chance,
    # with the winner dequeueing the others. Or they can queue multiple alternatives whose reaction options
    # conditionalize the prospects, such that the evolving state of the storyworld will ultimately decide
    # the winner. In each case, a kill code marks incompatibility between the alternatives, and in turn
    # guarantees that at most one of them will ever be performed. See pp. 618--619 of my PhD thesis for an
    # example of advanced usage of kill codes to coordinate and manage complex potential action sequences.
    killCode: Expression | None
    # An expression that should evaluate to a location, that being the specific location
    # at which the queued action must be performed.
    where: Expression | None
    # A time expression constraining when exactly the queued action may be performed.
    when: TemporalConstraints | None
    # A set of expressions such that, if all of them hold (i.e., evaluate to a truthy value),
    # the queued action will be dequeued.
    abandonmentConditions: list[Expression]


class Saliences(TypedDict):
    """Specifications for determining a numeric salience score for the action that will be held
    by a given character who experiences, observes, or otherwise learns about the action.
    """
    # A specification for a default value to be used as a fallback for any character for
    # which no `body` expressions hold. This will always be structured as a Viv enum,
    # int, or float, where even the enum should resolve to a numeric value.
    default: Union[Enum, IntField, FloatField]
    # The name of the variable to which a character will be bound when computing a salience for
    # them. This allows for evaluation of the body expressions, which may refer to this variable
    # in order to do things like conditionalize salience based on the character at hand.
    variable: VariableName
    # An ordered array of Viv expressions that will each evaluate to a numeric value, as in the
    # `default` property. These will be evaluated in turn, with the first numeric evaluated value
    # being assigned as the character's salience. If no body expression evaluates to a numeric
    # value, the default value will be used.
    body: list[Expression]


class Associations(TypedDict):
    """Specifications for determining the subjective associations for the action that will be held
    by a given character who experiences, observes, or otherwise learns about the action.
    """
    # A specification for a default value to be used as a fallback for any character for which no
    # `body` expressions hold. This will always be structured as a Viv list whose elements will be
    # simple Viv string expressions.
    default: ListField
    # The name of the variable to which a character will be bound when computing associations for
    # them. This allows for evaluation of the body expressions, which may refer to this variable
    # in order to do things like conditionalize associations based on the character at hand.
    variable: VariableName
    # An ordered array of Viv expressions that will each evaluate to Viv lists containing simple
    # Viv string expressions, as in the `default` property. These will be evaluated in turn, with
    # all the results being concatenated together to compose the associations for the character
    # at hand. If no body expression evaluates to a list value, the default value will be used.
    body: list[Expression]


class EmbargoDeclaration(TypedDict):
    """An embargo declaration constraining the subsequent performance of an associated action."""
    # Names for all the roles constituting the bindings over which this embargo holds. For instance,
    # if two roles R1 and R2 were specified here, and if an action A was performed with bindings
    # R1=[E1] and R2=[E2, E3], then this embargo would hold over all cases of A with any prospective
    # bindings that cast E1 in R1 and *either* E2 and/or E3 in R2. Stated differently, the embargo
    # holds if for all roles specified here, some subset overlaps between the embargo role bindings
    # and the prospective role bindings. Often, an embargo will only specify an initiator.
    roles: list[RoleName] | None
    # Whether the embargo is permanent. If so, `period` will always be null, and exactly one of
    # the fields is guaranteed to be truthy.
    permanent: bool
    # For an embargo that is not permanent, a specification of the time period over which the embargo
    # will hold. If `period` is present, `permanent` will always be false, and exactly one of the fields
    # is guaranteed to be truthy.
    period: TimePeriod | None
    # Whether the embargo holds only over a certain location, that being the location
    # at which an instance of the associated action has just been performed.
    here: bool


class TemporalConstraints(TypedDict, total=False):
    """A set of one or more temporal constraints, which an author specifies (in a reaction declaration)
    to control the time at which a queued action may be performed.
    """
    # Whether to anchor the temporal constraints in the timestamp of the action that directly triggered  this
    # reaction -- meaning the action whose definition included the reaction declaration -- as opposed to the
    # current simulation timestamp. This distinction only matters for time-period constraints, and specifically
    # for cases where a reaction is triggered because a character has learned about an action after the fact.
    # In such cases, we need to know whether a time-period constraint like "between 1 year and 3 years" holds
    # relative to the timestamp of the original action or relative to the time at which the character learned
    # about the original action.
    useActionTimestamp: bool
    # If specified, a temporal constraint specifying an acceptable range between
    # two points in time, where one end of the range may be open-ended.
    timePeriod: TimePeriodRangeConstraint | None
    # If specified, a temporal constraint specifying an acceptable range between
    # two times of day, where one end of the range may be open-ended.
    timeOfDay: TimeOfDayRangeConstraint | None


class TimePeriodRangeConstraint(TypedDict, total=False):
    """A temporal constraint specifying an acceptable range between two points in time.
    """
    # The point in time at which the range opens. This is specified as a relative time period (e.g., `5 days`)
    # that the target application can resolve at runtime into a point in time (by anchoring it relative to a
    # given simulation timestamp). If no relative time period is specified here, the range is open on this end.
    open: TimePeriod | None
    # The point in time at which the range closes. This is specified as a relative time period (e.g., `5 days`)
    # that the target application can resolve at runtime into a point in time (by anchoring it relative to a
    # given simulation timestamp). If no relative time period is specified here, the range is open on this end.
    close: TimePeriod | None


class TimePeriod(TypedDict):
    """A relative time period (e.g., "2 weeks") that the target application can resolve
     at runtime into a point in time.
    """
    # The number of time units -- e.g., `2` in `2 weeks`
    amount: int
    # The unit of time -- e.g., `weeks` in `2 weeks`
    unit: TemporalConstraintTimeUnit


class TimeOfDayRangeConstraint(TypedDict, total=False):
    """A temporal constraint specifying an acceptable range between two times of day.
    """
    # The time of day that opens the range marked acceptable by the temporal constraint. If no
    # time of day is specified here, the range is open on this end. Note that the target
    # application is tasked with determining whether a given time of day has passed.
    open: TimeOfDay | None
    # The time of day that closes the range marked acceptable by the temporal constraint. If no
    # time of day is specified here, the range is open on this end. Note that the target
    # application is tasked with determining whether a given time of day has passed.
    close: TimeOfDay | None


class TimeOfDay(TypedDict):
    """A specified time of day."""
    # The hour of day
    hour: int
    # The minute of the hour of day
    minute: int


# Enum containing the valid temporal-constraint time units
TemporalConstraintTimeUnit = Literal["minutes", "hours", "days", "weeks", "months", "years"]


class WrappedExpression(TypedDict):
    """A Viv expression wrapped with an array containing the names of all roles that it references.

    These reference lists are used for various optimizations.
    """
    # The actual Viv expression that is being wrapped
    body: Expression
    # Names of the roles referenced in the Viv expression
    references: list[RoleName]
