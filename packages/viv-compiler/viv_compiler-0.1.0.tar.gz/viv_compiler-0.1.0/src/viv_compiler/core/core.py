"""Compiler for the Viv DSL.

This high-level module invokes other components of the compiler out the full compilation pipeline:

  * Loading and parsing of the Viv DSL grammar.
  * Loading and parsing of a Viv source file.
  * Walking the parse tree with a visitor, to produce an AST.
  * Combining of ASTs, to honor 'include' statements (imports between Viv files).
  * Postprocessing of a combined AST, to produce full-fledged trope and action definitions,
    together constituting a Viv compiled content bundle.
  * Validation of the Viv compiled content bundle.
  * Emitting JSON output for the validated Viv compiled content bundle.

The entrypoint function is `compile_viv_source_code()`, and everything else
is only meant to be invoked internally, i.e., within this module.
"""

__all__ = ["compile_viv_source_code"]

import arpeggio
import viv_compiler.config
import viv_compiler.types
from typing import Any
from pathlib import Path
from importlib.resources import files
from .importer import integrate_imported_files
from .visitor import Visitor
from .postprocessor import postprocess_combined_ast
from .validator import validate_content_bundle
# noinspection PyUnresolvedReferences
from arpeggio.cleanpeg import ParserPEG


def compile_viv_source_code(
    source_file_path: Path,
    default_salience: float,
    default_associations: list[str],
    default_reaction_priority: float,
    use_memoization: bool,
    debug = False,
) -> viv_compiler.types.CompiledContentBundle:
    """Compile the given Viv source file to produce a JSON-serializable compiled content bundle.

    Args:
        source_file_path: The absolute path to the Viv source file to be parsed.
        default_salience: A user-provided default salience value to use when one is not specified
            in an action definition.
        default_associations: A user-provided default associations value to use when one is not
            specified in an action definition.
        default_reaction_priority: A user-provided default reaction priority to use when one is not
            specified in a reaction declaration.
        use_memoization: Whether to use memoization during PEG parsing (faster, but uses more memory).
        debug: Whether to invoke verbose debugging for the PEG parser itself (default: `False`).

    Returns:
        The compiled content bundle.
    """
    # Honor user-supplied config parameters, or the associated default values if none were supplied
    _honor_user_supplied_config_parameters(
        default_salience=default_salience,
        default_associations=default_associations,
        default_reaction_priority=default_reaction_priority,
    )
    # Create a Viv parser
    viv_parser = _create_viv_parser(use_memoization=use_memoization, debug=debug)
    # Load the source file to be compiled
    source_file_contents = _load_source_file(source_file_path=source_file_path)
    # Parse the source file to produce a parse tree
    tree = viv_parser.parse(_input=source_file_contents)
    # Following the visitor pattern in parsing, traverse the parse tree to gradually
    # construct an abstract syntax tree (AST).
    ast: viv_compiler.types.AST = _sanitize_ast(ast=arpeggio.visit_parse_tree(tree, Visitor()))
    # If there are any include declarations (i.e., import statements), honor those now
    combined_ast: viv_compiler.types.CombinedAST = integrate_imported_files(
        viv_parser=viv_parser,
        ast=ast,
        entry_point_file_path=source_file_path
    )
    # Conduct postprocessing to produce a final compiled content bundle
    compiled_content_bundle: viv_compiler.types.CompiledContentBundle = postprocess_combined_ast(
        combined_ast=combined_ast
    )
    # Conduct final validation. This will throw an error if any serious issues are detected.
    validate_content_bundle(content_bundle=compiled_content_bundle)
    # Finally, return the compiled content bundle
    return compiled_content_bundle


def _honor_user_supplied_config_parameters(
    default_salience: float,
    default_associations: list[str],
    default_reaction_priority: float,
) -> None:
    """Updates the global Viv compiler config to honor any user-supplied parameters.

    Args:
        default_salience: A user-provided default salience value to use when one is not specified in
            an action definition. The CLI provides a default value if the user does not supply one.
        default_associations: A user-provided default associations value to use when one is not specified
            in an action definition. The CLI provides a default value if the user does not supply one.
        default_reaction_priority: A user-provided default reaction priority to use when one is not
            specified in a reaction declaration.

    Returns:
        The compiled content bundle JSON string, if no output file path was provided, else None.
    """
    viv_compiler.config.ACTION_DEFINITION_OPTIONAL_FIELD_DEFAULT_VALUES["saliences"] = {
        "default": {'type': 'float', 'value': default_salience},
        "variable": viv_compiler.config.SALIENCES_VARIABLE_NAME,
        "body": [],
    }
    default_associations_expression = {
        "type": "list",
        "value": [{"type": "string", "value": association} for association in default_associations]
    }
    viv_compiler.config.ACTION_DEFINITION_OPTIONAL_FIELD_DEFAULT_VALUES["associations"] = {
        "default": default_associations_expression,
        "variable": viv_compiler.config.ASSOCIATIONS_VARIABLE_NAME,
        "body": [],
    }
    viv_compiler.config.REACTION_FIELD_DEFAULT_OPTIONS["priority"] = {
        "type": "float",
        "value": default_reaction_priority
    }


def _create_viv_parser(use_memoization: bool, debug: bool) -> ParserPEG:
    """Return a PEG parser initialized for the Viv DSL, with user-defined settings.

    Args:
        use_memoization: Whether to use memoization during PEG parsing (faster, but uses more memory).
        debug: Whether to invoke verbose debugging for the PEG parser itself.

    Returns:
        A PEG parser initialized for the Viv DSL.
    """
    # Load the Viv DSL grammar
    viv_grammar = files("viv_compiler.grammar").joinpath("viv.peg").read_text(encoding="utf-8")
    # Prepare and return the parser
    viv_parser = ParserPEG(
        language_def=viv_grammar,
        root_rule_name=viv_compiler.config.GRAMMAR_ROOT_SYMBOL,
        comment_rule_name=viv_compiler.config.GRAMMAR_COMMENT_SYMBOL,
        reduce_tree=False,
        ws="\t\n\r ",
        memoization=use_memoization,
        debug=debug
    )
    return viv_parser


def _load_source_file(source_file_path: Path) -> str:
    """Return the contents of the Viv source file at the given path.

    Args:
        source_file_path: Path to the Viv source file to be compiled.

    Returns:
        Contents of the Viv source file at the given path.
    """
    try:
        source_file_contents = open(source_file_path, encoding="utf8").read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Bad input file path (file not found): {source_file_path}")
    return source_file_contents


def _sanitize_ast(ast: Any) -> Any:
    """Returns a deep copy of the given AST with all (nested) Arpeggio containers replaced with plain lists.

    Args:
        ast: An AST produced by our visitor.

    Returns:
        A deep copy of the given AST with all (nested) Arpeggio containers replaced with plain lists.
    """
    if isinstance(ast, arpeggio.SemanticActionResults):
        return [_sanitize_ast(v) for v in ast]
    if isinstance(ast, dict):
        return {k: _sanitize_ast(v) for k, v in ast.items()}
    if isinstance(ast, list):
        return [_sanitize_ast(v) for v in ast]
    if isinstance(ast, tuple):
        return [_sanitize_ast(v) for v in ast]
    return ast
