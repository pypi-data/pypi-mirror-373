"""API for the Viv compiler.

This API is for machines. For human use, see the CLI exposed in `cli.py`.
"""

from pathlib import Path
from typing import Sequence
from viv_compiler import __version__
from viv_compiler.types import CompiledContentBundle
from .core import compile_viv_source_code


def compile_from_path(
    *,  # Require keyword arguments only
    source_file_path: Path,
    default_salience: float = 1.0,
    default_associations: Sequence[str] = (),
    default_reaction_priority: float = 1.0,
    use_memoization: bool = True,
    debug: bool = False,
) -> CompiledContentBundle:
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
            debug: Whether to invoke verbose debugging for the PEG parser itself.

        Returns:
            The compiled content bundle.
        """
    try:
        return compile_viv_source_code(
            source_file_path=source_file_path,
            default_salience=float(default_salience),
            default_associations=list(default_associations),
            default_reaction_priority=float(default_reaction_priority),
            use_memoization=use_memoization,
            debug=debug,
        )
    except Exception as e:
        raise VivCompileError(str(e)) from e


def get_version() -> str:
    """Return the Viv version number associated with this compiler instance."""
    return __version__


class VivCompileError(Exception):
    """Raised when Viv compilation fails."""
    pass
