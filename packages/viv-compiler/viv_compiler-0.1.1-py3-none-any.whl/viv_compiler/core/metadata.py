"""Module that handles the creation of metadata to attach to a compiled content bundle.

The entrypoint function is `create_metadata()`.
"""

__all__ = ["create_metadata"]

import viv_compiler.types
import viv_compiler.utils
from viv_compiler import __version__
from viv_compiler.types import ExpressionDiscriminator
from viv_compiler.utils import get_all_expressions_of_type


def create_metadata(
    action_definitions: list[viv_compiler.types.ActionDefinition],
    trope_definitions: list[viv_compiler.types.TropeDefinition],
) -> viv_compiler.types.CompiledContentBundleMetadata:
    """Return a package containing metadata for the given compiled content bundle.

    Args:
        action_definitions: List containing all actions in the content bundle.
        trope_definitions: List containing all tropes in the content bundle.

    Returns:
        A metadata package for the given content bundle.
    """
    metadata = {
        "vivVersion": __version__,
        "referencedEnums": [],
        "referencedFunctionNames": [],
        "itemRoles": [],
        "buildRoles": [],
        "timeOfDayConstrainedReactions": []
    }
    for ast_chunk in action_definitions + trope_definitions:
        # Compile all referenced enums
        all_referenced_enum_names = set(viv_compiler.utils.get_all_referenced_enum_names(ast_chunk=ast_chunk))
        metadata["referencedEnums"].extend(all_referenced_enum_names)
        # Compile all referenced adapter functions
        all_referenced_function_names = set(
            viv_compiler.utils.get_all_referenced_adapter_function_names(ast_chunk=ast_chunk)
        )
        metadata["referencedFunctionNames"].extend(all_referenced_function_names)
    for action_definition in action_definitions:
        # Compile all roles carrying 'item' and 'build' labels
        for role_definition in action_definition["roles"].values():
            if role_definition["item"]:
                metadata["itemRoles"].append({
                    "action": action_definition["name"],
                    "role": role_definition["name"]
                })
            if role_definition["build"]:
                metadata["buildRoles"].append({
                    "action": action_definition["name"],
                    "role": role_definition["name"]
                })
        # Compile all reactions referencing time of day
        all_nested_reactions = get_all_expressions_of_type(
            expression_type=ExpressionDiscriminator.REACTION,
            ast_chunk=action_definition
        )
        for reaction in all_nested_reactions:
            if reaction["options"]["when"] and reaction["options"]["when"]["timeOfDay"]:
                metadata["timeOfDayConstrainedReactions"].append({
                    "action": action_definition["name"],
                    "reaction": reaction["actionName"]
                })
    return metadata
