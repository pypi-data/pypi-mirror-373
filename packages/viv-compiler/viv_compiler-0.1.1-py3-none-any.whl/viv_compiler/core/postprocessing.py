"""Module that handles postprocessing of compiled ASTs for the Viv DSL.

This module takes in ASTs produced by the Viv parser (with imports honored) and
postprocesses them to produce compiled content bundles that are ready for validation.

The entrypoint function is `postprocess_combined_ast()`, and everything else is only
meant to be invoked internally, i.e., within this module.
"""

__all__ = ["postprocess_combined_ast"]

import copy
import viv_compiler.config
import viv_compiler.types
import viv_compiler.utils
from typing import Any, cast
from .validation import validate_join_directives, validate_preliminary_action_definitions
from .metadata import create_metadata


def postprocess_combined_ast(combined_ast: viv_compiler.types.CombinedAST) -> viv_compiler.types.CompiledContentBundle:
    """Postprocess the given combined AST by inserting higher-order metadata and performing other manipulations.

    Args:
        combined_ast: An abstract syntax tree produced by the Visitor class, integrating the
            respective ASTs of any included files.

    Returns:
        An AST containing postprocessed action definitions.
    """
    # Retrieve the raw action definitions to be postprocessed
    intermediate_action_definitions: list[viv_compiler.types.RawActionDefinition] = combined_ast["actions"]
    # Handle inheritance between action definitions
    validate_join_directives(raw_action_definitions=intermediate_action_definitions)
    _handle_action_definition_inheritance(raw_action_definitions=intermediate_action_definitions)
    # Add in default values for any optional fields elided in the definitions
    _add_optional_field_defaults(intermediate_action_definitions=intermediate_action_definitions)
    # Wrap preconditions, effects, and reactions with lists containing all roles referenced in the expressions
    intermediate_action_definitions: list[viv_compiler.types.IntermediateActionDefinition] = (
        _wrap_expressions_with_role_references(intermediate_action_definitions=intermediate_action_definitions)
    )
    # Duplicate initiator role definitions in dedicated 'initiator' fields
    _attribute_initiator_role(intermediate_action_definitions=intermediate_action_definitions)
    # Conduct preliminary validation of the intermediate action definitions. This will catch
    # potential major issues that cannot be outstanding by the time we get to the steps below.
    # If validation fails, an error will be thrown at this point.
    validate_preliminary_action_definitions(intermediate_action_definitions=intermediate_action_definitions)
    # Attribute to binding-pool directives whether they are cachable
    _attribute_binding_pool_cachability_values(intermediate_action_definitions=intermediate_action_definitions)
    # Construct a dependency tree that will structure role casting during action targeting. This will
    # be defined across 'parent' and 'children' role fields, which are modified in place by this method.
    for action_definition in intermediate_action_definitions:
        _build_role_casting_dependency_tree(action_definition=action_definition)
    # Convert the 'roles' field into a convenient mapping from role name to role definition
    for action_definition in intermediate_action_definitions:
        action_definition['roles'] = {role['name']: role for role in action_definition['roles']}
    # Convert the 'preconditions' field into a mapping from role name to (only) the preconditions
    # that must be evaluated to cast that role.
    finalized_action_definitions = _attribute_preconditions(
        intermediate_action_definitions=intermediate_action_definitions
    )
    # Isolate the trope definitions
    finalized_trope_definitions = combined_ast["tropes"]
    # Create metadata to be attached to the compiled content bundle
    content_bundle_metadata = create_metadata(
        action_definitions=finalized_action_definitions,
        trope_definitions=finalized_trope_definitions
    )
    # Package up and return the compiled content bundle
    compiled_content_bundle: viv_compiler.types.CompiledContentBundle = {
        "meta": content_bundle_metadata,
        "tropes": {trope["name"]: trope for trope in finalized_trope_definitions},
        "actions": {action["name"]: action for action in finalized_action_definitions}
    }
    return compiled_content_bundle


def _handle_action_definition_inheritance(
    raw_action_definitions: list[viv_compiler.types.RawActionDefinition]
) -> None:
    """Modify the given action definitions in place to honor all inheritance declarations.

    Args:
        raw_action_definitions: Action definitions for which the inheritance postprocessing
            step has not yet been conducted.

    Returns:
        None (modifies the input definitions are modified in place).
    """
    outstanding_child_action_names = [action['name'] for action in raw_action_definitions if action['parent']]
    while outstanding_child_action_names:
        for i in range(len(raw_action_definitions)):
            child_action_definition = raw_action_definitions[i]
            if child_action_definition['name'] not in outstanding_child_action_names:
                continue
            if child_action_definition['parent'] in outstanding_child_action_names:
                # This action's parent itself has a parent, and so we need to wait for the parent
                # to inherit its material first (and so on if there's further dependencies).
                continue
            try:
                parent_action_definition = next(
                    action for action in raw_action_definitions if action['name'] == child_action_definition['parent']
                )
            except StopIteration:
                raise KeyError(
                    f"Action '{child_action_definition['name']}' declares undefined parent action "
                    f"'{child_action_definition['parent']}'"
                )
            # Handle any 'join' flags
            merged_action_definition = _merge_action_definitions(
                child_action_definition=child_action_definition,
                parent_action_definition=parent_action_definition
            )
            # Handle any role-renaming declarations
            _handle_role_renaming_declarations(merged_action_definition=merged_action_definition)
            # Save the finalized child action
            raw_action_definitions[i] = merged_action_definition
            outstanding_child_action_names.remove(child_action_definition['name'])


def _merge_action_definitions(
    child_action_definition: viv_compiler.types.RawActionDefinition,
    parent_action_definition: viv_compiler.types.RawActionDefinition
) -> viv_compiler.types.RawActionDefinition:
    """Clone the given action definitions and return a merged one that honors the author's inheritance declarations.

    Args:
        child_action_definition: The child action definition that will inherit from the given parent definition.
        parent_action_definition: The parent action definition from which the given child definition will inherit.

    Returns:
        A merged action definition that honors the author's inheritance declarations.
    """
    new_merged_action_definition = copy.deepcopy(parent_action_definition)
    child_action_definition = cast(dict[str, Any], child_action_definition)
    parent_action_definition = cast(dict[str, Any], parent_action_definition)
    new_merged_action_definition = cast(dict[str, Any], new_merged_action_definition)
    field_name_to_join_flag = {
        "tags": "_join_tags",
        "roles": "_join_roles",
        "preconditions": "_join_preconditions",
        "scratch": "_join_scratch",
        "effects": "_join_effects",
        "reactions": "_join_reactions",
        "saliences": "_join_saliences",
        "associations": "_join_associations",
        "embargoes": "_join_embargoes",
    }
    for key in list(child_action_definition):
        if key.startswith("_join"):
            continue
        if key in field_name_to_join_flag and field_name_to_join_flag[key] in child_action_definition:
            both_dicts = (
                    isinstance(new_merged_action_definition[key], dict)
                    and isinstance(child_action_definition[key], dict)
            )
            both_lists = (
                    isinstance(new_merged_action_definition[key], list) and
                    isinstance(child_action_definition[key], list)
            )
            if key not in parent_action_definition:  # We can just use the child's value
                new_merged_action_definition[key] = child_action_definition[key]
            elif both_dicts:
                new_merged_action_definition[key].update(child_action_definition[key])
            elif both_lists:
                new_merged_action_definition[key] += child_action_definition[key]
            else:
                raise TypeError(
                    f"Cannot join field '{key}' in action '{child_action_definition['name']}': "
                    f"expected dict/list, got {type(new_merged_action_definition[key]).__name__} "
                    f"and {type(child_action_definition[key]).__name__}"
                )
            del child_action_definition[field_name_to_join_flag[key]]
        else:
            new_merged_action_definition[key] = child_action_definition[key]
    return new_merged_action_definition


def _handle_role_renaming_declarations(
    merged_action_definition: viv_compiler.types.RawActionDefinition
) -> None:
    """Modify the given action definition in place to honor all role-renaming declarations.

    A role-renaming declaration (e.g. `new_name<<old_name`) allows an author to rename a role that
    is inherited from a parent action. This entails not just updating the role's name in the child
    action, but also updating any references to the role in material inherited from the parent.

    Args:
        merged_action_definition: A merged action definition, meaning one that was produced by merging
            parent content into the definition of a child that inherits from the parent.

    Returns:
        None (modifies the input definitions are modified in place).
    """
    # Build a mapping from old names to new name
    old_name_to_new_name: dict[viv_compiler.types.RoleName, viv_compiler.types.RoleName] = {}
    for role_renaming_declaration in merged_action_definition["roles"]:
        if "_role_renaming" in role_renaming_declaration:
            source_role_is_defined = any(
                r for r in merged_action_definition["roles"] if r['name'] == role_renaming_declaration["_source_name"]
            )
            if not source_role_is_defined:
                raise ValueError(
                    f"Action '{merged_action_definition['name']}' attempts to rename role "
                    f"'{role_renaming_declaration['_source_name']}', but no such role is defined "
                    f"in the parent action '{merged_action_definition['parent']}'"
                )
            old_name_to_new_name[role_renaming_declaration["_source_name"]] = role_renaming_declaration["_target_name"]
    # If the dictionary is empty, there's no role-renaming declarations to handle and we can return now
    if not old_name_to_new_name:
        return
    # Otherwise, let's proceed. First, filter out the role-renaming directives.
    merged_action_definition["roles"] = [
        role for role in merged_action_definition["roles"] if "_role_renaming" not in role
    ]
    # Next, update the corresponding role definitions
    for role in merged_action_definition["roles"]:
        if role["name"] in old_name_to_new_name:
            role["name"] = old_name_to_new_name[role["name"]]
    # Update any embargo `roles` fields, which contain bare role names (not references or role unpackings)
    for embargo in merged_action_definition["embargoes"]:
        if not embargo["roles"]:
            continue
        updated_roles_field = []
        for role_name in embargo["roles"]:
            updated_role_name = old_name_to_new_name[role_name] if role_name in old_name_to_new_name else role_name
            updated_roles_field.append(updated_role_name)
        embargo["roles"] = updated_roles_field
    # Recursively walk the action definition to update all applicable references and role unpackings
    _rewrite_role_references(ast_chunk=merged_action_definition, old_name_to_new_name=old_name_to_new_name)


def _rewrite_role_references(
    ast_chunk: Any,
    old_name_to_new_name: dict[viv_compiler.types.RoleName, viv_compiler.types.RoleName]
) -> Any:
    """Recurse over the given AST chunk to honor any role-renaming declarations captured in the given mapping.

    This function only updates entity-reference and role-unpacking AST nodes, which it reaches by
    recursively visiting all dictionary values and list elements.

    Args:
        ast_chunk: The AST chunk to search.
        old_name_to_new_name: A mapping from old role names to new role names, as specified in all the
            role-renaming declarations contained in a given action definition that uses inheritance.

    Returns:
        The updated AST chunk, which will also be mutated in place. (Note: its shape will never change.)
    """
    # Recurse over a list value
    if isinstance(ast_chunk, list):
        for i in range(len(ast_chunk)):
            ast_chunk[i] = _rewrite_role_references(ast_chunk=ast_chunk[i], old_name_to_new_name=old_name_to_new_name)
        return ast_chunk
    # If it's a dictionary, we may just have a reference or a role unpacking...
    if isinstance(ast_chunk, dict):
        node_type = ast_chunk.get("type")
        # Rename an entity-reference anchor, if applicable, and recurse over its value
        if node_type == viv_compiler.types.ExpressionDiscriminator.ENTITY_REFERENCE:
            value = ast_chunk.get("value")
            name_of_reference_anchor_role = value["anchor"]
            if name_of_reference_anchor_role in old_name_to_new_name:
                value["anchor"] = old_name_to_new_name[name_of_reference_anchor_role]
            for i in range(len(value["path"])):
                value["path"][i] = _rewrite_role_references(
                    ast_chunk=value["path"][i],
                    old_name_to_new_name=old_name_to_new_name
                )
            return ast_chunk
        # Rename a role-unpacking target, if applicable (no need to recurse)
        if node_type == viv_compiler.types.ExpressionDiscriminator.ROLE_UNPACKING:
            name_of_role_to_unpack = ast_chunk.get("value")
            if name_of_role_to_unpack in old_name_to_new_name:
                ast_chunk["value"] = old_name_to_new_name[name_of_role_to_unpack]
            return ast_chunk
        # Recurse over any other dictionary value
        for key, value in ast_chunk.items():
            ast_chunk[key] = _rewrite_role_references(ast_chunk=value, old_name_to_new_name=old_name_to_new_name)
        return ast_chunk
    # For any other kind of value, there's no need to recurse
    return ast_chunk


def _add_optional_field_defaults(
    intermediate_action_definitions: list[viv_compiler.types.RawActionDefinition],
) -> None:
    """Modify the given action definitions in place to add default values for any elided optional fields.

    Args:
        intermediate_action_definitions: Action definitions for which the inheritance postprocessing
            step has already been conducted.

    Returns:
        None (modifies the input definitions are modified in place).
    """
    for action_definition in intermediate_action_definitions:
        for key, default in viv_compiler.config.ACTION_DEFINITION_OPTIONAL_FIELD_DEFAULT_VALUES.items():
            action_definition.setdefault(key, copy.deepcopy(default))


def _wrap_expressions_with_role_references(
    intermediate_action_definitions: list[viv_compiler.types.RawActionDefinition],
) -> list[viv_compiler.types.IntermediateActionDefinition]:
    """Return modified action definitions in which all preconditions, effects, and reactions
    are wrapped with lists containing all roles referred to in those expressions.

    Args:
        intermediate_action_definitions: Raw action definitions honoring inheritance declarations and
            containing default values for any elided optional fields.

    Returns:
        Intermediate action definitions whose preconditions, effects, and reactions are wrapped in
        structures listing all roles referred to in those expressions.
    """
    modified_intermediate_action_definitions: list[viv_compiler.types.IntermediateActionDefinition] = []
    for action_definition in intermediate_action_definitions:
        precondition_wrappers = []
        for precondition in action_definition['preconditions']:
            wrapper = {
                "body": precondition,
                "references": viv_compiler.utils.get_all_referenced_roles(ast_chunk=precondition)
            }
            precondition_wrappers.append(wrapper)
        effect_wrappers = []
        for effect in action_definition['effects']:
            wrapper = {"body": effect, "references": viv_compiler.utils.get_all_referenced_roles(ast_chunk=effect)}
            effect_wrappers.append(wrapper)
        reaction_wrappers = []
        for reaction in action_definition['reactions']:
            wrapper = {
                "body": reaction,
                "references": viv_compiler.utils.get_all_referenced_roles(ast_chunk=reaction)
            }
            reaction_wrappers.append(wrapper)
        modified_intermediate_action_definition: viv_compiler.types.IntermediateActionDefinition = (
            action_definition
            | {
                "preconditions": precondition_wrappers,
                "effects": effect_wrappers,
                "reactions": reaction_wrappers
            }
        )
        modified_intermediate_action_definitions.append(modified_intermediate_action_definition)
    return modified_intermediate_action_definitions


def _attribute_initiator_role(
    intermediate_action_definitions: list[viv_compiler.types.IntermediateActionDefinition],
) -> None:
    """Modify the given action definitions in place to attribute an initiator role.

    Args:
        intermediate_action_definitions: Action definitions that do not yet have the 'initiator' field added in.

    Returns:
        None (modifies the input definitions in place).
    """
    for action_definition in intermediate_action_definitions:
        if 'roles' not in action_definition:
            raise KeyError(f"Action '{action_definition['name']}' has no 'roles' field (this is required)")
        try:
            initiator_role = next(role for role in action_definition['roles'] if role['initiator'])
        except (StopIteration, KeyError):
            raise KeyError(f"Action '{action_definition['name']}' has no initiator role")
        action_definition['initiator'] = initiator_role


def _attribute_binding_pool_cachability_values(
    intermediate_action_definitions: list[viv_compiler.types.IntermediateActionDefinition],
) -> None:
    """Modify the given action definitions in place to mark binding-pool declarations as cachable/uncachable.

    A role has a cachable binding-pool declaration when it does not reference a non-initiator role.

    Args:
        intermediate_action_definitions: Action definitions that do have the 'initiator' field added in, but
            have not yet been processed for pool cachability.

    Returns:
        None (modifies the input definitions in place).
    """
    for action_definition in intermediate_action_definitions:
        for role_definition in action_definition['roles']:
            if not role_definition['pool']:
                continue
            role_definition['pool']['uncachable'] = False
            all_pool_references = viv_compiler.utils.get_all_referenced_roles(role_definition['pool'])
            if any(role for role in all_pool_references if role != action_definition['initiator']['name']):
                role_definition['pool']['uncachable'] = True


def _build_role_casting_dependency_tree(action_definition: viv_compiler.types.IntermediateActionDefinition) -> None:
    """Construct a dependency tree spanning required roles by modifying the given action definition in place.

    The dependency tree constructed by this method will be defined by setting 'parent' and 'children'
    fields in each of the given action definition's role definitions. This tree will be used at runtime
    to structure role casting during action targeting. Its edges represent dependency from two sources:
    1) the child role's pool directive being anchored in the parent role, or 2) the child role sharing
    one or more preconditions with the parent role and/or its ancestors in the tree (as constructed to
    that point). During action targeting, role casting will proceed down the dependency tree in a depth-
    first manner, with backtracking working in the inverse direction, upward along the dependency tree.
    This allows for sequential role casting and also greatly reduces the frequency of re-evaluating
    preconditions unnecessarily, since backtracking will not revisit roles without a dependency relation
    to the one for which casting failed. Note that the tree is technically a list of trees, where each
    one is rooted in a role that is either a) the initiator role, b) a role anchored in the initiator
    role, or c) a role with no anchor. Since the subtrees appear in order, we can conceive of it as a
    single tree rooted in an implied single root. Note also that this tree only contains required roles,
    since optional roles are always cast last, in a manner that does not require backtracking.

    Args:
        action_definition: An intermediate action definition for which the 'initiator' field has been set.

    Returns:
        None (modifies the given action definition in place).
    """
    # Set up some data that is needed by various helper functions below
    required_roles = [role for role in action_definition["roles"] if role['min'] > 0 and not role['initiator']]
    role_name_to_definition = {role_definition['name']: role_definition for role_definition in required_roles}
    # Record dependency relations that are rooted in binding-pool directives
    _record_binding_pool_dependencies(
        action_definition=action_definition,
        required_roles=required_roles,
        role_name_to_definition=role_name_to_definition
    )
    # Now we will record dependencies rooted in shared preconditions
    role_name_to_role_names_sharing_preconditions = _detect_precondition_dependencies(
        action_definition=action_definition,
        required_roles=required_roles,
        role_name_to_definition=role_name_to_definition
    )
    _record_precondition_dependencies(
        action_definition=action_definition,
        required_roles=required_roles,
        role_name_to_definition=role_name_to_definition,
        role_name_to_role_names_sharing_preconditions=role_name_to_role_names_sharing_preconditions
    )
    # Finally, let's organize the dependency relations into a single tree rooted in the initiator role
    _organize_dependency_tree(
        action_definition=action_definition,
        required_roles=required_roles,
        role_name_to_definition=role_name_to_definition,
    )


def _record_binding_pool_dependencies(
    action_definition: viv_compiler.types.IntermediateActionDefinition,
    required_roles: list[viv_compiler.types.RoleDefinition],
    role_name_to_definition: dict[str, viv_compiler.types.RoleDefinition],
) -> None:
    """Modify the given action definition in place to attribute dependency relations among
    its roles that are rooted in their respective binding-pool directives.

    If a given role R1 references another role R2 in its binding-pool directive, R1 will be
    specified as a child of R2 in the dependency tree.

    Args:
        action_definition: An intermediate action definition whose 'initiator' field has already been set.
        required_roles: A list containing all required roles in the given action definitions.
        role_name_to_definition: A mapping from role names to role definitions.

    Returns:
        None (modifies the action definition in place).
    """
    # First, add in any roles that are anchored in the initiator or that have no anchor
    already_included = set()  # A set containing role names already added to the tree
    for role in required_roles:
        if role["pool"]:
            all_roles_referenced_in_pools = viv_compiler.utils.get_all_referenced_roles(role['pool'])
            if all_roles_referenced_in_pools:
                parent_name = all_roles_referenced_in_pools[0]
                if parent_name != action_definition['initiator']['name']:
                    continue
        already_included.add(role["name"])
    # Next, for each role anchored in another role, attach the former as a child of the latter
    while True:
        try:
            child = next(role for role in required_roles if role['pool'] and role['name'] not in already_included)
        except StopIteration:
            break
        parent_name = viv_compiler.utils.get_all_referenced_roles(child['pool'])[0]
        if parent_name not in already_included:
            # The parent comes later in the 'roles' list. We'll come back around, so `pass` here and move on.
            pass
        child['parent'] = parent_name
        parent = role_name_to_definition[parent_name]
        parent['children'].append(child['name'])
        already_included.add(child['name'])


def _detect_precondition_dependencies(
    action_definition: viv_compiler.types.IntermediateActionDefinition,
    required_roles: list[viv_compiler.types.RoleDefinition],
    role_name_to_definition: dict[str, viv_compiler.types.RoleDefinition],
) -> dict[str, set[str]]:
    """Returns a mapping from role name to the names of all other roles that share preconditions.

    If two roles are referenced in the same precondition, one of them will depend on the other,
    with the direction of the relation depending on other factors. In this function, we merely
    detect such mutual relations, and later on we will make these unidirectional.

    Args:
        action_definition: An intermediate action definition.
        required_roles: A list containing all required roles in the given action definitions.
        role_name_to_definition: A mapping from role names to role definitions.

    Returns:
        A mapping from role name to the names of all other roles that share preconditions.
    """
    role_name_to_role_names_sharing_preconditions = {role['name']: set() for role in required_roles}
    for precondition in action_definition["preconditions"]:
        # Skip any precondition that references an optional role
        if any(role_name for role_name in precondition["references"] if role_name not in role_name_to_definition):
            continue
        for precondition_role_name in precondition["references"]:
            for other_precondition_role_name in precondition["references"]:
                if precondition_role_name == other_precondition_role_name:
                    continue
                role_name_to_role_names_sharing_preconditions[precondition_role_name].add(other_precondition_role_name)
    return role_name_to_role_names_sharing_preconditions


def _record_precondition_dependencies(
    action_definition: viv_compiler.types.IntermediateActionDefinition,
    required_roles: list[viv_compiler.types.RoleDefinition],
    role_name_to_definition: dict[str, viv_compiler.types.RoleDefinition],
    role_name_to_role_names_sharing_preconditions: dict[str, set[str]]
) -> None:
    """Modify the given action definition in place to attribute dependency relations among
    its roles that are rooted in shared preconditions.

    In the previous step, we detected cases of roles sharing preconditions. In this step,
    we will operate over these to record actual unidirectional dependencies.

    Args:
        action_definition: An intermediate action definition whose binding-pool dependencies have
            already been attributed.
        required_roles: A list containing all required roles in the given action definitions.
        role_name_to_definition: A mapping from role names to role definitions.
        role_name_to_role_names_sharing_preconditions: A mapping from role name to the names of
            all other roles that share preconditions.

    Returns:
        None (modifies the action definition in place).
    """
    # For each role, retrieve the role's ancestors and descendants. If a role R shares one or
    # more preconditions with a role S that is not a lineal relative of R, we will shift a subtree
    # containing S to be rooted in R. More on this below.
    for role in required_roles:
        # Search for a role with which this role shares one or more preconditions
        role_ancestors = _get_role_dependency_tree_ancestors(
            action_definition=action_definition, role_name=role['name']
        )
        role_descendants = _get_role_dependency_tree_descendants(
            action_definition=action_definition, role_name=role['name']
        )
        for role_sharing_preconditions in role_name_to_role_names_sharing_preconditions[role['name']]:
            if role_sharing_preconditions not in role_ancestors | role_descendants:
                # We now want to make the role at hand, R, an ancestor of this role with which it shares
                # preconditions, S. (Since sharing preconditions is a mutual dependency, we could just as
                # well work in the opposite direction. Due to our loop construction, R will have been defined
                # prior to S, however, and so we prefer for R to be the ancestor so that we can cast them in
                # the author-defined order -- this is likely a good heuristic for reducing backtracking.) In
                # shifting S to become a descendant of R, we must keep S's existing dependency structure
                # intact, since otherwise we could e.g. separate S from its pool anchor. Naively, we might
                # try to make its primogenitor, P, a child of R, but this will fail in the case where R
                # also descends from P, in particular the case where R's pool is anchored in P. (Since P would
                # then be a child of R, despite R requiring P to be cast first.) In other words, we need to take
                # special care when S is a collateral relative of R. To manage this correctly, we will retrieve
                # the highest-level ancestor of S that is not also an ancestor of R, call it A, and then make
                # A a child of R.
                ancestor_name = role_sharing_preconditions
                while role_name_to_definition[ancestor_name]['parent']:
                    if role_name_to_definition[ancestor_name]['parent'] in role_ancestors:
                        break
                    ancestor_name = role_name_to_definition[ancestor_name]['parent']
                # Leaving its descendant structure intact, make A a child of R
                original_parent = role_name_to_definition[ancestor_name]['parent']
                if original_parent:
                    role_name_to_definition[original_parent]['children'].remove(ancestor_name)
                role_name_to_definition[ancestor_name]['parent'] = role['name']
                role['children'].append(ancestor_name)
                role_ancestors.add(role_sharing_preconditions)


def _get_role_dependency_tree_ancestors(
    action_definition: viv_compiler.types.IntermediateActionDefinition,
    role_name: str
) -> set[str]:
    """Return all ancestors of the given role in the dependency tree for the given action definition.

    Args:
        action_definition: An AST postprocessed into an action definition.
        role_name: The role whose dependency-tree ancestors are to be retrieved.

    Returns:
        A set containing the names of all dependency-tree ancestors of the given role.
    """
    role_ancestors = set()
    if isinstance(action_definition['roles'], list):
        role_definitions = action_definition['roles']
    else:
        role_definitions = action_definition['roles'].values()
    role_definition = next(role for role in role_definitions if role['name'] == role_name)
    parent_name = role_definition['parent']
    if parent_name:
        role_ancestors.add(parent_name)
        role_ancestors |= _get_role_dependency_tree_ancestors(
            action_definition=action_definition, role_name=parent_name
        )
    return role_ancestors


def _get_role_dependency_tree_descendants(
    action_definition: viv_compiler.types.IntermediateActionDefinition,
    role_name: str
) -> set[str]:
    """Return all descendants of the given role in the dependency tree for the given action definition.

    Args:
        action_definition: An AST postprocessed into an action definition.
        role_name: The role whose dependency-tree descendants are to be retrieved.

    Returns:
        A set containing the names of all dependency-tree descendants of the given role.
    """
    role_descendants = set()
    if isinstance(action_definition['roles'], list):
        role_definitions = action_definition['roles']
    else:
        role_definitions = action_definition['roles'].values()
    role_definition = next(role for role in role_definitions if role['name'] == role_name)
    for child_name in role_definition['children']:
        role_descendants.add(child_name)
        role_descendants |= _get_role_dependency_tree_descendants(
            action_definition=action_definition, role_name=child_name
        )
    return role_descendants


def _organize_dependency_tree(
    action_definition: viv_compiler.types.IntermediateActionDefinition,
    required_roles: list[viv_compiler.types.RoleDefinition],
    role_name_to_definition: dict[str, viv_compiler.types.RoleDefinition],
) -> None:
    """Modify the given action definition in place to construct a single dependency tree rooted in its initiator role.

    Args:
        action_definition: An intermediate action definition whose dependency relations have already been attributed.
        required_roles: A list containing all required roles in the given action definitions.
        role_name_to_definition: A mapping from role names to role definitions.

    Returns:
        None (modifies the action definition in place).
    """
    # While we've attributed parents and children to all non-initiator required roles, we haven't stored
    # any listing of the subtrees formed thereby. We need this so that we can proceed through them one by
    # one during role casting. An easy solution here is to assign a list of all subtree-root (i.e., top-level)
    # roles as the 'children' value of the initiator role definition for this action. Let's do so now. We'll
    # also set the initiator as 'parent' for these roles, which is needed during precondition attribution.
    top_level_role_names = [role['name'] for role in required_roles if not role['parent']]
    action_definition['initiator']['children'] = top_level_role_names
    for role_name in top_level_role_names:
        role_name_to_definition[role_name]['parent'] = action_definition['initiator']['name']
    # Before we go, let's sort each listing of children such that larger subtrees come first. This heuristic
    # proceeds from an assumption that it's better to reach fail states as soon as possible, and fail states
    # are more likely to occur amid complex dependencies.
    for role_definition in action_definition['roles']:
        role_definition['children'].sort(
            key=lambda subtree_root_name: (
                len(_get_role_dependency_tree_descendants(action_definition, subtree_root_name)),
            ),
            reverse=True
        )


def _attribute_preconditions(
    intermediate_action_definitions: list[viv_compiler.types.IntermediateActionDefinition]
) -> list[viv_compiler.types.ActionDefinition]:
    """Modify the given action definitions in place such that the 'preconditions' field maps
    role names to (only) the preconditions that must be evaluated to cast that role.

    As a minor side effect, this method also sorts precondition references in dependency-stream order.

    Args:
        intermediate_action_definitions: Action definitions for which role-dependency trees have already been computed.

    Returns:
        Finalized action definitions, since this is the last postprocessing step.
    """
    final_action_definitions: list[viv_compiler.types.ActionDefinition] = []
    for action_definition in intermediate_action_definitions:
        role_name_to_preconditions = {role_name: [] for role_name in action_definition['roles'].keys()}
        for precondition in action_definition["preconditions"]:
            # If there is no reference, assign it to the initiator. Such preconditions (e.g., chance only)
            # can be evaluated at the beginning of action targeting, prior to casting any additional roles.
            if not precondition['references']:
                role_name_to_preconditions[action_definition['initiator']['name']].append(precondition)
                continue
            # If there's a single reference, assign it to that role
            if len(precondition['references']) == 1:
                role_name_to_preconditions[precondition['references'][0]].append(precondition)
                continue
            # If there's any optional role referenced, assign it to that role
            for role_name in precondition['references']:
                role_definition = next(
                    role for role in action_definition['roles'].values() if role['name'] == role_name
                )
                if role_definition['min'] == 0:
                    role_name_to_preconditions[role_name].append(precondition)
                    continue
            # Otherwise, assign it to the role furthest downstream in the dependency structure. Since all
            # roles sharing a precondition will be situated in a direct line in this structure, we can
            # easily identify the most downstream role as the one with the most ancestors. For clarity,
            # we'll sort the actual precondition 'references' value in upstream-to-downstream order.
            precondition['references'].sort(
                key=lambda role_name: len(_get_role_dependency_tree_ancestors(action_definition, role_name)),
            )
            role_name_to_preconditions[precondition['references'][-1]].append(precondition)
        final_action_definition: viv_compiler.types.ActionDefinition = (
            action_definition | {"preconditions": role_name_to_preconditions}
        )
        final_action_definitions.append(final_action_definition)
    return final_action_definitions
