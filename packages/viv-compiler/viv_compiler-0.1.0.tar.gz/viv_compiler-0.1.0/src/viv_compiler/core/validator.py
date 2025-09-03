"""A library of functions to validate preliminary action definitions and compiled content bundles.

The entrypoint functions are as follows:
    * `validate_join_directives()`: Invoked prior to handling of action inheritance.
    * `validate_preliminary_action_definitions()`: Invoked in the middle of postprocessing.
    * `validate_content_bundle()`: Invoked when the final compiled content bundle has been prepared.

Everything else is only meant to be invoked internally, i.e., within this module.
"""

__all__ = ["validate_join_directives", "validate_preliminary_action_definitions", "validate_content_bundle"]

import viv_compiler.config
import viv_compiler.types
import viv_compiler.utils
from viv_compiler.types import ExpressionDiscriminator, TropeDefinition
from viv_compiler.utils import get_all_referenced_roles
from importlib import import_module
from pydantic import TypeAdapter


# todo do we already ensure all references are anchored in a (valid) role name?
# todo warn or error if precondition references scaled enum?
# todo validate time of day to ensure 0-23 and 0-59
# todo technically you could inject major side effects (e.g. reaction queueing) into trope-fit expressions
# todo ensure closing time period is always later than opening time period
# todo ensure embargo is either permanent or has a declared time period
# todo don't allow reaction to precast same entity multiple times
# todo build roles:
#  - they can cast exactly one entity, with no chance and no mean
#  - no pool declarations
#  - can never be precast
#  - preconditions cannot reference build roles
#  - don't allow them in embargoes (embargo would not be violable)
# todo apparently the grammar allows e.g. multiple roles fields in an action definition
#  - test what happens (presumably last in wins)
# todo make sure times like 88:76 aren't allowed (grammar allows them)
# todo role renaming (make sure new name being duplicate of existing one is already caught)
#   - just detect duplicate role names right away post-visitor
# todo prohibit entity references anchored in symbol roles
#   - not ideal, but interpreter enforces this at runtime currently
# todo assignments only allowed in scratch and effects


def validate_join_directives(raw_action_definitions: list[viv_compiler.types.RawActionDefinition]) -> None:
    """Ensure that the given action definition makes proper use of `join` directives.

    If this validation check passes, the given action definitions are ready for inheritance to be handled.

    Args:
        raw_action_definitions: A list of raw action definitions for which inheritance is about to be handled.

    Returns:
        None.

    Raises:
        Exception: The given raw action definitions did not pass validation.
    """
    for action_definition in raw_action_definitions:
        if not action_definition["parent"]:
            for key, _ in list(action_definition.items()):
                if key.startswith("_join_"):
                    raise ValueError(
                        f"Action '{action_definition['name']}' uses 'join' operator but declares no parent"
                    )
        for role_definition in action_definition["roles"]:
            if "_role_renaming" in role_definition:
                if "_join_roles" not in action_definition:
                    raise ValueError(
                        f"Action '{action_definition['name']}' uses role renaming but does not 'join roles'"
                    )


def validate_preliminary_action_definitions(
    intermediate_action_definitions: list[viv_compiler.types.IntermediateActionDefinition]
) -> None:
    """Validate the given preliminary action definitions, to catch potential major issues that
    must be rectified prior to the final postprocessing steps.

    Args:
        intermediate_action_definitions: A list of action definitions for which includes have been honored,
            elided optional fields have been filled in, and the 'initiator' field has been set.

    Returns:
        Args

    Raises:
        Exception: At least one action definition did not pass validation.
    """
    for action_definition in intermediate_action_definitions:
        # Ensure that a 'roles' field is present
        if "roles" not in action_definition:
            raise KeyError(f"Action '{action_definition['name']}' is missing a 'roles' field, which is required")
        # Ensure that there is a single initiator role. Note that during initial validation,
        # the 'roles' field is still a list.
        _detect_wrong_number_of_initiators(action_definition=action_definition)
        # Detect duplicated role names
        _detect_duplicate_role(action_definition=action_definition)
        # Detect any reference to an undefined role. This validation *must* occur prior to
        # precondition attribution and construction of the role-dependency tree.
        _detect_reference_to_undefined_role(action_definition=action_definition)


def _detect_wrong_number_of_initiators(action_definition: viv_compiler.types.IntermediateActionDefinition) -> None:
    """Ensure that the given action definition has a single initiator role.

    Args:
        action_definition: An action definitions for which includes have been honored, elided
            optional fields have been filled in, and the 'initiator' field has been set.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    all_initiator_roles = [role for role in action_definition['roles'] if role['initiator']]
    if len(all_initiator_roles) == 0:
        raise ValueError(f"Action '{action_definition['name']}' has no initiator role (must have exactly one)")
    elif len(all_initiator_roles) > 1:
        raise ValueError(f"Action '{action_definition['name']}' has multiple initiator roles (must have exactly one)")


def _detect_duplicate_role(action_definition: viv_compiler.types.IntermediateActionDefinition) -> None:
    """Ensure that the given action definition has no duplicated role names.

    Args:
        action_definition: An action definitions for which includes have been honored, elided
            optional fields have been filled in, and the 'initiator' field has been set.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    for role_definition in action_definition["roles"]:
        n_roles_with_that_name = 0
        for other_role_definition in action_definition["roles"]:
            if other_role_definition['name'] == role_definition["name"]:
                n_roles_with_that_name += 1
                if n_roles_with_that_name > 1:
                    raise ValueError(
                        f"Action '{action_definition['name']}' has duplicate role: "
                        f"'{role_definition['name']}'"
                    )


def _detect_reference_to_undefined_role(action_definition: viv_compiler.types.IntermediateActionDefinition) -> None:
    """Ensure that the given action definition has no references to any undefined role.

    Args:
        action_definition: An action definitions for which includes have been honored, elided
            optional fields have been filled in, and the 'initiator' field has been set.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    # Retrieve the names of all defined roles ('roles' is still a list at this point in postprocessing)
    all_defined_role_names = {role['name'] for role in action_definition['roles']} | {'hearer', 'this', 'default'}
    # Validate report references
    if action_definition["report"]:
        for reference in viv_compiler.utils.get_all_referenced_roles(action_definition["report"]):
            if reference not in all_defined_role_names:
                raise KeyError(
                    f"Action '{action_definition['name']}' has report that references "
                    f"undefined role '{reference}'"
                )
    # Validation pool-directive references
    for role_definition in action_definition["roles"]:
        if not role_definition['pool']:
            continue
        for reference in viv_compiler.utils.get_all_referenced_roles(role_definition['pool']):
            if reference not in all_defined_role_names:
                raise KeyError(
                    f"Pool directive for role '{role_definition['name']}' in action "
                    f"'{action_definition['name']}' references undefined role: '{reference}'"
                )
    # Validation precondition references
    for precondition in action_definition["preconditions"]:
        for reference in precondition['references']:
            if reference not in all_defined_role_names:
                raise KeyError(
                    f"Action '{action_definition['name']}' has precondition that references "
                    f"undefined role: '{reference}'"
                )
    # Validation effect references
    for effect in action_definition["effects"]:
        for reference in effect['references']:
            if reference not in all_defined_role_names:
                raise KeyError(
                    f"Action '{action_definition['name']}' has effect that references "
                    f"undefined role '{reference}'"
                )
    # Validate reaction references
    for reaction_declaration in action_definition['reactions']:
        for reference in reaction_declaration['references']:
            if reference not in all_defined_role_names:
                raise KeyError(
                    f"Action '{action_definition['name']}' has reaction that references "
                    f"undefined role '{reference}'"
                )
    # Validate salience references
    for role_name in get_all_referenced_roles(ast_chunk=action_definition['saliences']):
        if role_name not in all_defined_role_names:
            raise KeyError(
                f"Action '{action_definition['name']}' has salience expression that "
                f"references undefined role: '{role_name}'"
            )
    # Validate association references
    for role_name in get_all_referenced_roles(ast_chunk=action_definition['associations']):
        if role_name not in all_defined_role_names:
            raise KeyError(
                f"Action '{action_definition['name']}' has association declaration that "
                f"references undefined role: '{role_name}'"
            )
    # Validate embargo references
    for embargo in action_definition['embargoes']:
        for role_name in embargo['roles'] or []:
            if role_name not in all_defined_role_names:
                raise KeyError(
                    f"Action '{action_definition['name']}' has embargo that "
                    f"references undefined role: '{role_name}'"
                )


def validate_content_bundle(content_bundle: viv_compiler.types.CompiledContentBundle) -> None:
    """Validate the given compiled content bundle.

    Args:
        content_bundle: A compiled content bundle.

    Returns:
        None: If no issue was detected.

    Raises:
        Exception: If an issue was detected.
    """
    # Carry out semantic validation on the trope definitions
    _validate_trope_definitions(trope_definitions=content_bundle["tropes"])
    # Carry out semantic validation on the action definitions
    _validate_action_definitions(
        action_definitions=content_bundle["actions"],
        trope_definitions=content_bundle["tropes"],
    )
    # Finally, carry out structural validation by comparing the entire content bundle against our schema
    _validate_compiled_content_bundle_against_schema(content_bundle=content_bundle)


def _validate_trope_definitions(trope_definitions: dict[str, viv_compiler.types.TropeDefinition]) -> None:
    """Validate the given trope definitions.

    Args:
        trope_definitions: Map from trope name to trope definition, for all definitions in the compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The trope definitions did not pass validation.
    """
    for trope_definition in trope_definitions.values():
        # Detect any reference to an undefined param
        all_referenced_params = viv_compiler.utils.get_all_referenced_roles(ast_chunk=trope_definition)
        for referenced_param in all_referenced_params:
            if referenced_param not in trope_definition["params"]:
                raise KeyError(
                    f"Trope '{trope_definition['name']}' references undefined parameter: "
                    f"'{referenced_param}'"
                )


def _validate_action_definitions(
    action_definitions: dict[str, viv_compiler.types.ActionDefinition],
    trope_definitions: dict[str, viv_compiler.types.TropeDefinition],
) -> None:
    """Validate the given action definitions.

    Args:
        action_definitions: Map from action name to action definition, for all action
            definitions in the compiled content bundle.
        trope_definitions: Map from trope name to trope definition, for all definitions in the compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definitions did not pass validation.
    """
    # First, let's operate over the set of definitions to detect any duplicated action names
    _detect_duplicate_action_names(action_definitions=action_definitions)
    # Now let's validate each action in turn
    for action_definition in action_definitions.values():
        # Validate role definitions
        _validate_action_roles(action_definition=action_definition)
        # Validate preconditions
        _validate_action_preconditions(action_definition=action_definition)
        # Validate effects
        _validate_action_effects(action_definition=action_definition)
        # Validate reactions
        _validate_action_reactions(action_definition=action_definition, all_action_definitions=action_definitions)
        # Validate associations
        # Validate trope-fit expressions
        _validate_action_trope_fit_expressions(
            action_definition=action_definition,
            trope_definitions=trope_definitions
        )
        # Validate role unpackings
        _validate_action_role_unpackings(action_definition=action_definition)
        # Validate loops
        _validate_action_loops(action_definition=action_definition)
        # Validate assignments
        _validate_action_assignments(action_definition=action_definition)
        # Validate negated expressions
        _validate_negated_expressions(action_definition=action_definition)
        # Validate chance expressions
        _validate_chance_expressions(action_definition=action_definition)


def _detect_duplicate_action_names(action_definitions: dict[str, viv_compiler.types.ActionDefinition]) -> None:
    """Ensure that there are no duplicate names in use among the given action definitions.

    Args:
        action_definitions: Map from action name to action definition, for all action
            definitions in the compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definitions did not pass validation.
    """
    action_names = [action_definition['name'] for action_definition in action_definitions.values()]
    for action_name in action_names:
        if action_names.count(action_name) > 1:
            raise ValueError(f"Duplicate action name: '{action_name}'")


def _validate_action_roles(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Validate the 'roles' field of the given action definition.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    # Validate the initiator role
    _validate_action_initiator_role(action_definition=action_definition)
    # Ensure all roles have proper 'min' and 'max' values
    _validate_action_role_min_and_max_values(action_definition=action_definition)
    # Ensure all roles have proper 'chance' and 'mean' values
    _validate_action_role_chance_and_mean_values(action_definition=action_definition)
    # Ensure all roles with binding pools have proper ones
    _validate_action_role_pool_directives(action_definition=action_definition)
    # Ensure that the 'precast' label is only used if this is a special action
    _validate_action_role_precast_label_usages(action_definition=action_definition)


def _validate_action_initiator_role(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Ensure that the given action definition has a valid initiator role definition.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    # Retrieve the definition for the action's initiator role
    initiator_role_definition = action_definition['initiator']
    # Ensure that the initiator role has no pool directive
    if initiator_role_definition["pool"]:
        raise ValueError(
            f"Action '{action_definition['name']}' has initiator role '{initiator_role_definition['name']}' "
            f"with a pool directive, which is not allowed for initiator roles"
        )
    # Ensure that the initiator role casts exactly one entity
    if initiator_role_definition['min'] != 1:
        raise ValueError(
            f"Action '{action_definition['name']}' has initiator role '{initiator_role_definition['name']}' "
            f"with min other than 1 (there must be a single initiator)"
        )
    if initiator_role_definition['max'] != 1:
        raise ValueError(
            f"Action '{action_definition['name']}' has initiator role '{initiator_role_definition['name']}' "
            f"with max other than 1 (there must be a single initiator)"
        )
    # Ensure that the initiator role has no specified binding mean
    if initiator_role_definition['mean'] is not None:
        raise ValueError(
            f"Action '{action_definition['name']}' has initiator role '{initiator_role_definition['name']}' "
            f"with declared casting mean (there must be a single initiator)"
        )
    # Ensure that the initiator role has no specified binding chance
    if initiator_role_definition['chance'] is not None:
        raise ValueError(
            f"Action '{action_definition['name']}' has initiator role '{initiator_role_definition['name']}' "
            f"with declared casting chance (there must be a single initiator)"
        )


def _validate_action_role_min_and_max_values(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Ensure that the given action definition has no role definition with invalid 'min' or 'max' value.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    for role_definition in action_definition["roles"].values():
        # Detect minimums less than 0
        if role_definition['min'] < 0:
            raise ValueError(
                f"Action '{action_definition['name']}' has role '{role_definition['name']}' "
                f"with negative min (must be 0 or greater)"
            )
        # Detect maximums of 0 or less
        if role_definition['max'] < 1:
            raise ValueError(
                f"Action '{action_definition['name']}' has role '{role_definition['name']}' "
                f"with max less than 1 (to turn off role, comment it out or use chance of [0%])"
            )
        # Detect role-count minimums that are greater than role-count maximums
        if role_definition['min'] > role_definition['max']:
            raise ValueError(
                f"Action '{action_definition['name']}' has role '{role_definition['name']}' with min > max"
            )


def _validate_action_role_chance_and_mean_values(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Ensure that the given action definition has no role definition with invalid 'chance' or 'mean' value.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    for role_definition in action_definition["roles"].values():
        # Confirm that 'chance', if present, is between 0.0 and 1.0
        if role_definition['chance'] is not None:
            if role_definition['chance'] < 0.0 or role_definition['chance'] > 1.0:
                raise ValueError(
                    f"Action '{action_definition['name']}' has role '{role_definition['name']}' "
                    f"with invalid chance (must be between 0-100%)"
                )
        # Confirm that 'mean', if present, is between min and max
        if role_definition['mean'] is not None:
            role_min, role_max = role_definition['min'], role_definition['max']
            if role_definition['mean'] < role_min or role_definition['mean'] > role_max:
                raise ValueError(
                    f"Action '{action_definition['name']}' has role '{role_definition['name']}' "
                    f"with invalid mean (must be between min and max)"
                )


def _validate_action_role_pool_directives(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Ensure that the given action definition does not have an invalid pool directive.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    for role_definition in action_definition["roles"].values():
        # Force pool directives for all roles except present characters and items. One exception here is
        # that an absent item can be built by an action, in which case its location should be specified.
        requires_pool_directive = False
        if role_definition['absent']:
            if not role_definition['build']:
                requires_pool_directive = True
        elif role_definition['action']:
            requires_pool_directive = True
        elif role_definition['location']:
            requires_pool_directive = True
        elif role_definition['symbol']:
            requires_pool_directive = True
        if role_definition['precast']:
            requires_pool_directive = False
        if requires_pool_directive and not role_definition["pool"]:
            raise KeyError(
                f"Action '{action_definition['name']}' has role '{role_definition['name']}' "
                f"that requires a pool declaration but does not have one"
            )
        # Ensure that all pool directives reference at most one other (valid) role
        if role_definition["pool"]:
            all_pool_references = viv_compiler.utils.get_all_referenced_roles(role_definition["pool"])
            if len(all_pool_references) > 1:
                non_initiator_pool_references = (
                    [role for role in all_pool_references if role != action_definition['initiator']['name']]
                )
                if len(non_initiator_pool_references) > 1:
                    raise ValueError(
                        f"Pool directive for role '{role_definition['name']}' in action '{action_definition['name']}' "
                        f"references multiple other non-initiator roles ({', '.join(non_initiator_pool_references)}), "
                        f"but pool directives may only reference a single other non-initiator role"
                    )
            # Force "is" pool directives to correspond to a max of exactly 1, since this is the "is" semantics.
            # Note that we don't actually retain any data marking that the 'is' operator was used, but rather we
            # create a binding-pool expression that is a list containing a single element, that being the reference
            # for the entity associated with the 'is' usage. We could end up with this same shape if the author uses
            # 'from' with a literal singleton array -- e.g. "hat from ["hat"]: symbol" -- so the error message will
            # refer to both potential causes.
            if role_definition["pool"]["body"]["type"] == ExpressionDiscriminator.LIST:
                if len(role_definition["pool"]["body"]["value"]) == 1:
                    # If we're in here, this is either an 'is' usage or a case of 'from' with a literal singleton array
                    if role_definition['max'] != 1:
                        raise ValueError(
                            f"Action '{action_definition['name']}' has role '{role_definition['name']}'that uses "
                            f"'is' pool directive (or 'from' with a singleton array) with a max other than 1"
                        )


def _validate_action_role_precast_label_usages(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Ensure that the given action definition only uses the 'precast' role label if it's special.

    The 'precast' role label allows an author to specify that a role can only be cast using
    the bindings asserted by a reaction. A 'special' action is one that can only be targeted
    as a reaction, which is necessary for usage of the 'precast' label, because otherwise there
    would be no way to cast the role.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    if action_definition['special']:
        return
    for role_definition in action_definition["roles"].values():
        if role_definition['precast']:
            raise ValueError(
                f"Action '{action_definition['name']}' has precast role '{role_definition['name']}', "
                f"but is not marked special (only special actions can have precast roles)"
            )


def _validate_action_preconditions(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Validate the given action definition's 'preconditions' field.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    # Collect all preconditions
    all_preconditions = []
    for precondition_group in action_definition['preconditions'].values():  # Grouped by role
        all_preconditions += precondition_group
    # Validate each one
    for precondition in all_preconditions:
        # Currently, it's not possible to evaluate a precondition referencing two optional roles
        optional_role_references = []
        for reference in precondition['references']:
            if action_definition['roles'][reference]['min'] < 1:
                optional_role_references.append(reference)
            if len(optional_role_references) > 1:
                raise ValueError(
                    f"Action '{action_definition['name']}' has precondition that references multiple optional "
                    f"roles ({', '.join(optional_role_references)}), but currently a precondition may only "
                    f"reference at most one optional role"
                )


def _validate_action_effects(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Validate the given action definition's 'effects' field.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    for effect in action_definition['effects']:
        # Confirm that the effect contains no eval fail-safe operator
        if viv_compiler.utils.contains_eval_fail_safe_operator(ast_chunk=effect):
            raise ValueError(
                f"Action '{action_definition['name']}' has effect that uses the eval fail-safe "
                f"operator (?), which is not allowed in effects"
            )


def _validate_action_reactions(
    action_definition: viv_compiler.types.ActionDefinition,
    all_action_definitions: dict[str, viv_compiler.types.ActionDefinition]
) -> None:
    """Validate the given action definition's 'reactions' field.

    Args:
        action_definition: An action definition from a compiled content bundle.
        all_action_definitions: Map from action name to action definition, for all action
            definitions in the compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    # Ensure that all reactions are housed in the proper fields
    fields_to_check = (
        ("preconditions", action_definition["preconditions"]),
        ("scratch", action_definition["scratch"]),
        ("effects", action_definition["effects"]),
    )
    for field_name, field_value in fields_to_check:
        reactions_in_this_field = viv_compiler.utils.get_all_expressions_of_type(
            expression_type="reaction",
            ast_chunk=field_value
        )
        if reactions_in_this_field:
            raise ValueError(
                f"Action '{action_definition['name']}' has reaction in '{field_name}' field "
                f"(only allowed in 'reactions' field)"
            )
    # Collect all reactions
    all_reactions = viv_compiler.utils.get_all_expressions_of_type(
        expression_type="reaction",
        ast_chunk=action_definition['reactions']
    )
    # Validate each reaction in turn
    for reaction in all_reactions:
        # Make sure the reaction references a valid action
        action_names = [action_definition['name'] for action_definition in all_action_definitions.values()]
        queued_action_name = reaction['actionName']
        if queued_action_name not in action_names:
            raise KeyError(
                f"Action '{action_definition['name']}' has reaction that queues "
                f"undefined action '{queued_action_name}'"
            )
        # Make sure the reaction binds an initiator role
        queued_action_definition = all_action_definitions[queued_action_name]
        queued_action_initiator_role_name = queued_action_definition['initiator']['name']
        initiator_is_bound = False
        for binding in reaction['bindings']:
            if binding['value']['role'] == queued_action_initiator_role_name:
                initiator_is_bound = True
                break
        if not initiator_is_bound:
            raise ValueError(
                f"Action '{action_definition['name']}' has '{queued_action_name}' reaction that "
                f"fails to precast its initiator role '{queued_action_initiator_role_name}'"
            )
        # Make sure the reaction references only roles defined in the queued actions
        all_queued_action_role_names = queued_action_definition['roles'].keys()
        for binding in reaction['bindings']:
            bound_role_name = binding['value']['role']
            if bound_role_name not in all_queued_action_role_names:
                raise KeyError(
                    f"Action '{action_definition['name']}' has '{queued_action_name}' reaction that "
                    f"references a role that is undefined for '{queued_action_name}': '{bound_role_name}'"
                )
        # Make sure the reaction precasts all 'precast' roles
        for role_object in queued_action_definition['roles'].values():
            if not role_object['precast']:
                continue
            precast_role_name = role_object['name']
            role_is_precast = False
            for binding in reaction['bindings']:
                bound_role_name = binding['value']['role']
                if bound_role_name == precast_role_name:
                    role_is_precast = True
                    break
            if not role_is_precast:
                raise KeyError(
                    f"Action '{action_definition['name']}' has '{queued_action_name}' reaction "
                    f"that fails to precast one of its 'precast' roles: '{precast_role_name}'"
                )


def _validate_action_trope_fit_expressions(
    action_definition: viv_compiler.types.ActionDefinition,
    trope_definitions: dict[str, TropeDefinition]
) -> None:
    """Validate the given action definition's usage of trope-fit expressions.

    Args:
        action_definition: An action definition from a compiled content bundle.
        trope_definitions: Map from trope name to trope definition, for all definitions in the compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    all_trope_fit_expressions = viv_compiler.utils.get_all_expressions_of_type(
        expression_type="tropeFitExpression",
        ast_chunk=action_definition
    )
    for trope_fit_expression in all_trope_fit_expressions:
        # Retrieve the name of the trope referenced in the expression
        trope_name = trope_fit_expression['tropeName']
        # Detect reference to undefined trope
        if trope_name not in trope_definitions:
            raise KeyError(f"Action '{action_definition['name']}' references undefined trope: '{trope_name}'")
        # Detect cases of missing arguments or extra arguments
        trope_definition = trope_definitions[trope_name]
        if len(trope_fit_expression['args']) != len(trope_definition['params']):
            n_args = len(trope_fit_expression['args'])
            n_params = len(trope_definition['params'])
            relative_quantity = "too few" if n_args < n_params else "too many"
            raise ValueError(
                f"Action '{action_definition['name']}' invokes trope '{trope_name}' with "
                f"{relative_quantity} arguments (expected {n_params}, got {n_args})"
            )


def _validate_action_role_unpackings(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Validate the given action definition's usage of role unpackings.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    # Ensure all role unpackings unpack roles that can cast multiple entities
    all_unpacked_role_names = viv_compiler.utils.get_all_expressions_of_type(
        expression_type="roleUnpacking",
        ast_chunk=action_definition
    )
    for unpacked_role_name in all_unpacked_role_names:
        for role_definition in action_definition['roles'].values():
            if role_definition['name'] == unpacked_role_name:
                if role_definition['min'] == role_definition['max'] == 1:
                    raise ValueError(
                        f"Action '{action_definition['name']}' unpacks a singleton role (one that is "
                        f"always bound to a single entity): '{unpacked_role_name}'"
                    )
                break
    # Ensure that all other references to roles that can cast multiple entities use role unpackings
    single_entity_role_references = viv_compiler.utils.get_all_referenced_roles(  # I.e., using the '@role' notation
        ast_chunk=action_definition,
        ignore_role_unpackings=True
    )
    for referenced_role_name in single_entity_role_references:
        for role_definition in action_definition['roles'].values():
            if role_definition['name'] == referenced_role_name:
                if not (role_definition['min'] == role_definition['max'] == 1):
                    raise ValueError(
                        f"Action '{action_definition['name']}' fails to unpack group "
                        f"role: '{referenced_role_name}' (use * instead of @)"
                    )
                break


def _validate_action_loops(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Validate the given action definition's usage of loops.

    Note: the grammar already enforces that loop bodies may not be empty.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    all_loops = viv_compiler.utils.get_all_expressions_of_type(expression_type="loop", ast_chunk=action_definition)
    for loop in all_loops:
        # Detect attempts to loop over single-entity role references (i.e., ones using '@role' notation)
        if loop['iterable']['type'] == ExpressionDiscriminator.ENTITY_REFERENCE:
            if not loop['iterable']['value']['path']:
                role_name = loop['iterable']['value']['anchor']
                raise ValueError(
                    f"Action '{action_definition['name']}' attempts to loop over a non-unpacked "
                    f"role: '{role_name}' (perhaps use * instead of @)"
                )
        # Detect cases of a loop variable shadowing the name of a role from the same action
        if loop['variable'] in viv_compiler.utils.get_all_role_names(action_definition=action_definition):
            raise ValueError(
                f"Action '{action_definition['name']}' has loop with variable name that "
                f"shadows role name '{loop['variable']}' (this is not allowed)"
            )


def _validate_action_assignments(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Validate the given action definition's usage of assignments.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    all_assignments = viv_compiler.utils.get_all_expressions_of_type(
        expression_type="assignment",
        ast_chunk=action_definition
    )
    for assignment in all_assignments:
        anchor = assignment['left']['value']['anchor']
        path = assignment['left']['value']['path']
        if assignment['left']['type'] == ExpressionDiscriminator.ENTITY_REFERENCE:
            # Detect attempts to recast a role via assignment (not allowed)
            if not path:
                raise ValueError(
                    f"Assignment expression in action '{action_definition['name']}' recasts "
                    f"role '{anchor}' (this is prohibited)"
                )
            # Detect attempts to set data on the "entity" associated with a symbol role
            if anchor != "this":
                if action_definition['roles'][anchor]['symbol']:
                    raise ValueError(
                        f"Assignment expression in action '{action_definition['name']}' has "
                        f"symbol role on its left-hand side: '{anchor}'"
                    )
        # Detect a trailing eval fail-safe marker, which is bizarre and probably an authoring error
        if path and path[-1].get('failSafe'):
            raise ValueError(
                f"LHS of assignment expression in action '{action_definition['name']}' has "
                f"a trailing eval fail-safe marker '?' (only allowed within, and not following, the LHS)"
            )


def _validate_chance_expressions(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Validate the given action definition's usage of chance expressions.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    all_chance_expression_values = viv_compiler.utils.get_all_expressions_of_type(
        expression_type="chanceExpression",
        ast_chunk=action_definition
    )
    for chance_value in all_chance_expression_values:
        if chance_value < 0.0 or chance_value > 1.0:
            raise ValueError(
                f"Chance expression in action '{action_definition['name']}' has "
                f"chance value outside of the range [0, 1]: '{chance_value * 100}%'"
            )


def _validate_negated_expressions(action_definition: viv_compiler.types.ActionDefinition) -> None:
    """Validate the given action definition's usage of chance expressions.

    Args:
        action_definition: An action definition from a compiled content bundle.

    Returns:
        None.

    Raises:
        Exception: The action definition did not pass validation.
    """
    for negated_expression in viv_compiler.utils.get_all_negated_expressions(ast_chunk=action_definition):
        if negated_expression['type'] not in viv_compiler.config.NEGATABLE_EXPRESSION_TYPES:
            raise ValueError(
                f"Expression of type '{negated_expression['type']}' in action '{action_definition['name']}' is "
                f" negated, but this is not allowed (only the following expression types support negation: "
                f"{', '.join(viv_compiler.config.NEGATABLE_EXPRESSION_TYPES)}):\n\n{negated_expression}"
            )


def _validate_compiled_content_bundle_against_schema(content_bundle: viv_compiler.types.CompiledContentBundle) -> None:
    """Validate a compiled content bundle against its public schema.

    Uses Pydantic v2's TypeAdapter to validate the *shape* of the compiled bundle produced by the compiler
    against the public schema. This catches structural drift between the compiler output and runtime contracts.

    Args:
        content_bundle: The compiled content bundle to validate.

    Raises:
        pydantic.ValidationError: If validation fails, detailing schema mismatches.
    """
    content_schema = import_module("viv_compiler.types.content_public_schemas")
    dsl_schema = import_module("viv_compiler.types.dsl_public_schemas")
    type_adapter = TypeAdapter(content_schema.CompiledContentBundle)
    type_adapter.rebuild(_types_namespace={**content_schema.__dict__, **dsl_schema.__dict__})
    type_adapter.validate_python(content_bundle)
