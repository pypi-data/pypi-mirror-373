"""Utility functions used by various components of the Viv DSL compiler."""

import viv_compiler.types
from viv_compiler.types import ExpressionDiscriminator
from typing import Any


def get_all_role_names(action_definition: viv_compiler.types.ActionDefinition) -> set[viv_compiler.types.RoleName]:
    """Return a set containing the names of all roles associated with the given action definition.

    Args:
        action_definition:

    Returns:
        A set containing the names of all roles associated with the given action definition.
    """
    return {'hearer', 'this', 'default'} | set(action_definition['roles'])


def get_all_referenced_roles(
    ast_chunk: Any,
    ignore_role_unpackings: bool = False,
    ignore: Any = None
) -> list[viv_compiler.types.RoleName]:
    """Return a list of all roles referenced in the given AST chunk.

    Args:
        ast_chunk: The full or partial AST to search for role references.
        ignore_role_unpackings: Whether to search for role references inside role unpackings.
        ignore: Only used internally, via recursive calls to this function.

    Returns:
        A list containing the names of all roles referenced in the given AST chunk.
    """
    ignore = ignore or ["this"]
    roles_referenced_so_far = []
    if isinstance(ast_chunk, list):
        for element in ast_chunk:
            roles_referenced_so_far.extend(get_all_referenced_roles(
                ast_chunk=element,
                ignore_role_unpackings=ignore_role_unpackings,
                ignore=ignore
            ))
    elif isinstance(ast_chunk, dict):
        if ast_chunk.get('type') == ExpressionDiscriminator.ENTITY_REFERENCE:
            referenced_role = ast_chunk['value']['anchor']
            roles_referenced_so_far.append(referenced_role)
        elif not ignore_role_unpackings and ast_chunk.get('type') == ExpressionDiscriminator.ROLE_UNPACKING:
            referenced_role = ast_chunk['value']
            roles_referenced_so_far.append(referenced_role)
        else:
            scoped_ignore = ignore
            if ast_chunk.get('type') == ExpressionDiscriminator.LOOP:
                scoped_ignore = [*ignore, ast_chunk['value']['variable']]
                iterable = ast_chunk['value']['iterable']
                if iterable.get('type') == ExpressionDiscriminator.ROLE_UNPACKING:
                    if not ignore_role_unpackings:
                        roles_referenced_so_far.append(iterable['value'])
            for key, value in ast_chunk.items():
                roles_referenced_so_far.extend(get_all_referenced_roles(
                    ast_chunk=value,
                    ignore_role_unpackings=ignore_role_unpackings,
                    ignore=scoped_ignore
                ))
    return list(set(filter(lambda role: role not in ignore, roles_referenced_so_far)))


def get_all_referenced_enum_names(ast_chunk: Any) -> list[viv_compiler.types.EnumName]:
    """Return a list of the names of all enums referenced in the given AST chunk.

    This list will be stored in the compiled content bundle, where it's used for
    validation purposes upon the initialization of a Viv runtime.

    Args:
        ast_chunk: The full or partial AST to search for enum references.

    Returns:
        A list containing the names of all the enums referenced in the given AST chunk.
    """
    all_enum_expressions = get_all_expressions_of_type(expression_type="enum", ast_chunk=ast_chunk)
    all_referenced_enum_names = [expression['name'] for expression in all_enum_expressions]
    return all_referenced_enum_names


def get_all_referenced_adapter_function_names(ast_chunk: Any) -> list[viv_compiler.types.AdapterFunctionName]:
    """Return a list of the names of all adapter functions referenced in the given AST chunk.

    This list will be stored in the compiled content bundle, where it's used for
    validation purposes upon the initialization of a Viv runtime.

    Args:
        ast_chunk: The full or partial AST to search for adapter-function references.

    Returns:
        A list containing the names of all the adapter functions referenced in the given AST chunk.
    """
    all_adapter_function_references = get_all_expressions_of_type(
        expression_type="adapterFunctionCall",
        ast_chunk=ast_chunk
    )
    all_referenced_adapter_function_names = [expression['name'] for expression in all_adapter_function_references]
    return all_referenced_adapter_function_names


def get_all_expressions_of_type(expression_type: str, ast_chunk: Any) -> list[Any]:
    """Return a list containing values for all expressions of the given type that are nested in the given AST chunk.

    Args:
        expression_type: String indicating the type of Viv expression to search for.
        ast_chunk: The AST chunk to search for expressions of the given type.

    Returns:
        A list containing all the Viv expressions of the given type in the given AST chunk.
    """
    expressions = []
    if isinstance(ast_chunk, list):
        for element in ast_chunk:
            expressions.extend(get_all_expressions_of_type(expression_type=expression_type, ast_chunk=element))
    elif isinstance(ast_chunk, dict):
        if 'type' in ast_chunk and ast_chunk['type'] == expression_type:
            expression_of_type = ast_chunk['value']
            expressions.append(expression_of_type)
        else:
            for key, value in ast_chunk.items():
                expressions.extend(get_all_expressions_of_type(expression_type=expression_type, ast_chunk=value))
    return expressions


def get_all_negated_expressions(ast_chunk: Any) -> list[viv_compiler.types.Expression]:
    """
    Return every negated expression in the given AST chunk.

    Args:
        ast_chunk: The full or partial AST to search for negated expressions.

    Returns:
        A list containing all the negated Viv expressions in the given AST chunk.
    """
    negated_expressions = []
    if isinstance(ast_chunk, list):
        for element in ast_chunk:
            negated_expressions.extend(get_all_negated_expressions(ast_chunk=element))
    elif isinstance(ast_chunk, dict):
        if ast_chunk.get("negated"):
            negated_expressions.append(ast_chunk)
        for value in ast_chunk.values():
            negated_expressions.extend(get_all_negated_expressions(ast_chunk=value))
    return negated_expressions


def contains_eval_fail_safe_operator(ast_chunk: Any) -> bool:
    """Return whether the given AST chunk contains an eval fail-safe operator.

    Args:
        ast_chunk: The full or partial AST to search for expressions of the given type.

    Returns:
        True if the given AST chunk contains an eval fail-safe operator, else False.
    """
    if isinstance(ast_chunk, list):
        for element in ast_chunk:
            if contains_eval_fail_safe_operator(ast_chunk=element):
                return True
    elif isinstance(ast_chunk, dict):
        if 'type' in ast_chunk and ast_chunk['type'] == ExpressionDiscriminator.EVAL_FAIL_SAFE:
            return True
        else:
            for key, value in ast_chunk.items():
                if contains_eval_fail_safe_operator(ast_chunk=value):
                    return True
    return False
