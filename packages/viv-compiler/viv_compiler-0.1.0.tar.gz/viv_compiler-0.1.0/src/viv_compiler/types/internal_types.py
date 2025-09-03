"""Internal types that are used by the compiler only.

The types defined here describe shapes whose life cycles begin and expire during
compilation. As such, they are not part of the public API for the compiler.
"""

from __future__ import annotations

from typing import Literal
from typing_extensions import TypedDict, NotRequired
from .dsl_public_schemas import (
    Expression,
    TemplateStringField,
    ListField,
)
from .content_public_schemas import (
    ActionName,
    Associations,
    EmbargoDeclaration,
    Reaction,
    RoleDefinition,
    RoleName,
    Saliences,
    TropeDefinition,
    WrappedExpression
)


class AST(TypedDict):
    """Visitor output for a single source file."""
    # A list of relative import paths, exactly as authored in the source file (using the
    # `include` operator). This transient field is deleted once inheritance has been handled.
    _includes: list[str]
    # All raw trope definitions in the source file
    tropes: list[TropeDefinition]
    # All raw action definitions in the source file
    actions: list["RawActionDefinition"]


class CombinedAST(TypedDict):
    """The merged AST after import resolution.

    Notes:
        * The `includes` field has been handled and is no longer present here.
    """
    # All trope definitions across the entry file and its resolved imports
    tropes: list[TropeDefinition]
    # All raw actions across the entry file and its resolved imports
    actions: list["RawActionDefinition"]


class RawActionDefinition(TypedDict, total=False):
    """An action definition as emitted directly by the visitor.

    Notes:
        * Default values are not yet filled in.
        * No expressions have been converted into wrapped expressions.
        * The `initiator` field is not present.
        # The transient "join" flags are still present.
        * The `roles` and `preconditions` fields are still lists (converted into dictionaries later on).
        * Role-renaming declarations may be included in the `roles` field.
    """
    # Unique action name (public-schema shape)
    name: ActionName
    # Whether this action can only be targeted via a reaction (public-schema shape)
    special: bool
    # Optional parent action from which this action inherits fields
    parent: ActionName | None
    # Author-specified tags as a literal list of strings (public-schema shape)
    tags: ListField
    # All roles defined for this action, including role-renaming declarations (later converted into a dictionary)
    roles: list[RoleDefinition | RoleRenaming]
    # If present, a definition for a simple templated string describing this action
    # in a sentence or so (public-schema shape).
    gloss: TemplateStringField | None
    # If present, a definition for a more detailed templated string describing this
    # action in a paragraph or so (public-schema shape).
    report: TemplateStringField | None
    # A list of preconditions on this action (pre-wrapping)
    preconditions: list[Expression]
    # Scratch expressions for preparing an arbitrary action blackboard state (public-schema shape)
    scratch: list[Expression]
    # A list of effects on this action (pre-wrapping)
    effects: list[Expression]
    # A list of reactions on this action (pre-wrapping)
    reactions: list[Reaction]
    # Salience-computation block (public-schema shape)
    saliences: "Saliences"
    # Association-computation block (public-schema shape)
    associations: "Associations"
    # Embargo declarations constraining future performance of the action (public-schema shape)
    embargoes: list["EmbargoDeclaration"]
    # Whether to combine the `tags` field here with those of a parent (`True` if present)
    _join_tags: NotRequired[Literal[True]]
    # Whether to combine the `roles` field here with those of a parent (`True` if present)
    _join_roles: NotRequired[Literal[True]]
    # Whether to combine the `preconditions` field here with those of a parent (`True` if present)
    _join_preconditions: NotRequired[Literal[True]]
    # Whether to combine the `scratch` field here with those of a parent (`True` if present)
    _join_scratch: NotRequired[Literal[True]]
    # Whether to combine the `effects` field here with those of a parent (`True` if present)
    _join_effects: NotRequired[Literal[True]]
    # Whether to combine the `reactions` field here with those of a parent (`True` if present)
    _join_reactions: NotRequired[Literal[True]]
    # Whether to combine the `saliences` field here with those of a parent (`True` if present)
    _join_saliences: NotRequired[Literal[True]]
    # Whether to combine the `associations` field here with those of a parent (`True` if present)
    _join_associations: NotRequired[Literal[True]]
    # Whether to combine the `embargoes` field here with those of a parent (`True` if present)
    _join_embargoes: NotRequired[Literal[True]]


class RoleRenaming(TypedDict):
    """A declaration to rename a role inherited from a parent definition."""
    # Flag indicating that a `roles` entry is a role-renaming declaration
    _role_renaming: Literal[True]
    # The name of source role, from the parent action, that is to be renamed
    _source_name: RoleName
    # The new name to be used for the source role, from the parent action, whose definition will be retained
    _target_name: RoleName


class IntermediateActionDefinition(TypedDict, total=False):
    """An intermediate action definition.

    Notes:
        * Default values are now filled in.
        * Expressions have been converted into wrapped expressions, as applicable.
        * The `initiator` field is now present.
        * All "join" flags have been honored and deleted.
        * The `roles` field may either be a list or a dictionary. We collapse both variants
          of the intermediate action-definition shape here for convenience.
        * The `preconditions` fields is still a list (converted into dictionary later on).
        * Role-renaming declarations have been handled and are no longer present in the `roles` field.
    """
    # Unique action name (public-schema shape)
    name: ActionName
    # Whether this action can only be targeted via a reaction (public-schema shape)
    special: bool
    # Optional parent action from which this action inherits fields
    parent: ActionName | None
    # Author-specified tags as a literal list of strings (public-schema shape)
    tags: ListField
    # All roles defined for this action (may already be converted into a dictionary)
    roles: list[RoleDefinition] | dict[RoleName, RoleDefinition]
    # The initiator role definition duplicated for convenience during post-processing
    initiator: RoleDefinition
    # If present, a definition for a simple templated string describing this action
    # in a sentence or so (public-schema shape).
    gloss: TemplateStringField | None
    # If present, a definition for a more detailed templated string describing this
    # action in a paragraph or so (public-schema shape).
    report: TemplateStringField | None
    # A list of preconditions on this action (post-wrapping, but not yet a dictionary)
    preconditions: list[WrappedExpression]
    # Scratch expressions for preparing an arbitrary action blackboard state (public-schema shape)
    scratch: list[Expression]
    # A list of effects on this action (public-schema shape)
    effects: list[WrappedExpression]
    # A list of reactions on this action (public-schema shape)
    reactions: list[WrappedExpression]
    # Salience computation block (public-schema shape)
    saliences: "Saliences"
    # Association computation block (public-schema shape)
    associations: "Associations"
    # Embargo declarations constraining future performance of the action (public-schema shape)
    embargoes: list["EmbargoDeclaration"]
