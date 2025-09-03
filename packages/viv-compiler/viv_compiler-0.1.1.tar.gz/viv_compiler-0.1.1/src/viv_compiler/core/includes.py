"""Module that handles importing between Viv files.

The entrypoint function is `integrate_included_files()`, and everything else is only meant to be
invoked internally, i.e., within this module.
"""

__all__ = ["integrate_included_files"]

import arpeggio
import viv_compiler.types
from pathlib import Path
from .visitor import Visitor
# noinspection PyUnresolvedReferences
from arpeggio.cleanpeg import ParserPEG


def integrate_included_files(
    viv_parser: ParserPEG,
    ast: viv_compiler.types.AST,
    entry_point_file_path: Path,
) -> viv_compiler.types.CombinedAST:
    """Handle any `include` declarations in the given AST (including any recursive ones)
    and return a dictionary containing trope definitions and action definitions.

    Args:
        viv_parser: A prepared Viv parser.
        ast: An abstract syntax tree produced by the Visitor class.
        entry_point_file_path: The file path for the file that is being directly compiled by the author.

    Returns:
        A dictionary containing trope definitions and action definitions.
    """
    # First, we need to recursively gather all included files. If we do this step first, we don't
    # need to worry about circular dependencies (Viv allows circular imports).
    all_included_file_paths = _compile_all_included_file_paths(
        viv_parser=viv_parser,
        ast=ast,
        anchor_dir=entry_point_file_path.parent,
        all_included_absolute_file_paths={entry_point_file_path}
    )
    # We'll start with the AST for the user's entry file. If there's no includes,
    # will end up being the combined AST.
    combined_ast: viv_compiler.types.CombinedAST = {"tropes": ast["tropes"], "actions": ast["actions"]}
    # Now let's parse each of the included files to build up a combined AST
    for included_file_path in all_included_file_paths:
        # Load and parse the file
        code = included_file_path.read_text(encoding="utf-8")
        # Parse the file
        try:
            tree = viv_parser.parse(_input=code)
        except arpeggio.NoMatch as parsing_error:
            raise Exception(
                f"Error encountered while parsing included file '{included_file_path}': "
                f"{str(parsing_error)}"
            )
        included_file_ast = arpeggio.visit_parse_tree(tree, Visitor())
        # Append its trope definitions
        included_trope_definitions = included_file_ast["tropes"]
        combined_ast["tropes"] += included_trope_definitions
        # Append its action definitions
        included_action_definitions = included_file_ast["actions"]
        combined_ast["actions"] += included_action_definitions
    # Return the combined AST
    return combined_ast


def _compile_all_included_file_paths(
    viv_parser: ParserPEG,
    ast: viv_compiler.types.AST,
    anchor_dir: Path,
    all_included_absolute_file_paths: set[Path],
) -> list[Path]:
    """Return a list containing absolute paths for all the files to be included in the one at hand.

    Critically, this method is robust to circular includes, however arcane, and it captures arbitrarily
    recursive includes.

    Args:
        viv_parser: A prepared Viv parser.
        ast: An abstract syntax tree produced by the Visitor class.
        all_included_absolute_file_paths: A running list containing absolute paths for all the
            files to (recursively) include.

    Returns:
        A list of all (recursively) included absolute file paths.
    """
    new_included_absolute_file_paths: list[Path] = []
    for included_file_relative_path in ast["_includes"]:
        included_file_absolute_path = (anchor_dir / included_file_relative_path).resolve()
        if included_file_absolute_path in all_included_absolute_file_paths:  # Already captured this one
            continue
        new_included_absolute_file_paths.append(included_file_absolute_path)
        all_included_absolute_file_paths.add(included_file_absolute_path)
        try:
            source_code = included_file_absolute_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(f"Bad 'include' declaration (file not found): {included_file_relative_path}")
        try:
            tree = viv_parser.parse(_input=source_code)
        except arpeggio.NoMatch as parsing_error:
            raise Exception(
                f"Error encountered while parsing included file '{included_file_relative_path}': {parsing_error}"
            )
        included_file_ast = arpeggio.visit_parse_tree(tree, Visitor())
        new_included_absolute_file_paths += _compile_all_included_file_paths(
            viv_parser=viv_parser,
            ast=included_file_ast,
            anchor_dir=included_file_absolute_path.parent,
            all_included_absolute_file_paths=all_included_absolute_file_paths,
        )
    return new_included_absolute_file_paths
