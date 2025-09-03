"""System configuration for the Viv DSL compiler.

Defines a set of constants constituting the configuration parameters necessary for the function
of the compiler. These are only meant to be modified in the course of system development, i.e.,
not by users. That said, user-supplied default values for the `saliences` and `associations`
fields will be used programmatically to update the dictionary below containing default values
for optional fields in action definitions.
"""

from viv_compiler.types import ExpressionDiscriminator, ReferencePathComponentDiscriminator


# Name of the root symbol in the Viv DSL grammar
GRAMMAR_ROOT_SYMBOL = "file"

# Name of the symbol associated with comments in the Viv DSL grammar
GRAMMAR_COMMENT_SYMBOL = "comment"

# Viv expression types that support negation. While the grammar (and therefore the parser)
# will allow for negation in other expression types, the validator will use this config
# parameter to enforce this policy.
NEGATABLE_EXPRESSION_TYPES = {
    ExpressionDiscriminator.ADAPTER_FUNCTION_CALL,
    ExpressionDiscriminator.COMPARISON,
    ExpressionDiscriminator.CONJUNCTION,
    ExpressionDiscriminator.DISJUNCTION,
    ExpressionDiscriminator.ENTITY_REFERENCE,
    ExpressionDiscriminator.LOCAL_VARIABLE_REFERENCE,
    ExpressionDiscriminator.LOOP,
    ExpressionDiscriminator.MEMBERSHIP_TEST,
    ExpressionDiscriminator.TROPE_FIT_EXPRESSION,
}

# Default values for various optional fields in an action definition
ACTION_DEFINITION_OPTIONAL_FIELD_DEFAULT_VALUES = {
    "gloss": None,
    "report": None,
    "control": {},
    "tags": {"type": "list", "value": []},  # This is an expression that produces a list, not a list itself
    "preconditions": [],
    "scratch": [],
    "effects": [],
    "reactions": [],
    "saliences": None,  # Set by user via CLI, which uses a default value if none is provided
    "associations": None,  # Set by user via CLI, which uses a default value if none is provided
    "embargoes": [],
}

# Default values for the options in an action definition's reaction field
REACTION_FIELD_DEFAULT_OPTIONS = {
    "urgent": {"type": "bool", "value": False},
    "priority": None,  # Set by user via CLI, which uses a default value if none is provided
    "killCode": None,
    "where": None,
    "when": None,
    "abandonmentConditions": [],
}

# The path to which the global-variable sigil `$` expands. This sigil is really just syntactic sugar for
# the path `@this.scratch`, which stores a blackboard local to a performed action. For instance, the scratch
# operation `$foo.bar = 99` is syntactic sugar for the expression `@this.scratch.foo.bar = 99`.
GLOBAL_VARIABLE_REFERENCE_ANCHOR = "this"
GLOBAL_VARIABLE_REFERENCE_PATH_PREFIX = [{
    "type": ReferencePathComponentDiscriminator.REFERENCE_PATH_COMPONENT_PROPERTY_NAME,
    "name": "scratch",
}]

# The path to which the local-variable sigil `$$` expands. This sigil is really just a property lookup in
# the special `__locals__` field of an evaluation context, which is a temporary store for scoped local
# variables. For instance, the local-variable reference `$$c` defines an attempt to access `__locals__.c`
# in an evaluation context. Unlike the `$` sigil, this is not syntactic sugar, since the Viv author has
# no other way to reference local variables.
LOCAL_VARIABLE_REFERENCE_PATH = ["__locals__"]

# Name for the variable to which each character is set when computing their salience for an action
SALIENCES_VARIABLE_NAME = "c"

# Name for the variable to which each character is set when computing their associations for an action
ASSOCIATIONS_VARIABLE_NAME = "c"

# A default salience value, to be used when the API caller does not provide one
DEFAULT_SALIENCE_VALUE = 1.0

# A default associations value, to be used when the API caller does not provide one
DEFAULT_ASSOCIATIONS_VALUE = []

# A default reaction priority value, to be used when the API caller does not provide one
DEFAULT_REACTION_PRIORITY_VALUE = 1.0
