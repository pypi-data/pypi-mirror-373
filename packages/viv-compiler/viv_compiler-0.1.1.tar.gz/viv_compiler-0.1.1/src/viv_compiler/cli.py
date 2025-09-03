"""Command‑line interface (CLI) for the Viv DSL compiler.

This CLI is for humans. For programmatic use, call the compiler functions exposed in `api.py`.
"""

import sys
import json
import argparse
import traceback
import viv_compiler.config
from pathlib import Path
from importlib import resources
from .api import compile_from_path, get_version
from viv_compiler.types import CompiledContentBundle


def main() -> None:
    """Command-line interface (CLI) for the Viv DSL compiler."""
    # Build the parser for command-line arguments
    parser = _build_parser()
    # Parse the command-line arguments
    args = parser.parse_args()
    # If the user has requested the compiler version, print it and exit
    if args.version:
        print(get_version())
        sys.exit(0)
    # If test mode is not engaged and no source file was provided, error and exit
    if not args.test and not args.input:
        parser.error("Unless the 'test' flag is engaged, an action file must be provided")
    # If test mode is engaged, invoke the compiler on a test file and exit
    print("\nCompiling...\n", file=sys.stderr)
    if args.test:
        _run_smoke_test(args=args)
        sys.exit(0)
    # Otherwise, it's showtime, so let's invoke the compiler
    if args.output:
        path_to_output_file = Path(args.output).expanduser().resolve()
        if not path_to_output_file.parent.exists():
            raise FileNotFoundError(f"Output-file directory does not exist: {path_to_output_file.parent}")
    else:
        path_to_output_file = None
    compiled_content_bundle = _invoke_compiler(args=args)
    # If we get to here, compilation succeeded
    print("Success!\n", file=sys.stderr)
    _emit_results(compiled_content_bundle=compiled_content_bundle, args=args, path_to_output_file=path_to_output_file)


def _build_parser() -> argparse.ArgumentParser:
    """Build the parser for our command-line arguments.

    Returns:
        A prepared parser for our command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Compile a Viv source file (.viv) to produce a content bundle ready for use in a Viv runtime",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i',
        '--input',
        metavar='source_file',
        type=str,
        help='relative or absolute path to the Viv source file (.viv) to be compiled'
    )
    parser.add_argument(
        '-o',
        '--output',
        metavar='output_file',
        type=str,
        default=None,
        help='path to which output file (.json) will be written'
    )
    parser.add_argument(
        '-s',
        '--default_salience',
        metavar='default_salience',
        type=float,
        default=viv_compiler.config.DEFAULT_SALIENCE_VALUE,
        help='default salience value to use when one is not specified'
    )
    parser.add_argument(
        '-a',
        '--default_associations',
        metavar='default_associations',
        type=str,
        nargs='*',
        default=viv_compiler.config.DEFAULT_ASSOCIATIONS_VALUE,
        help='default associations (sequence of strings) to use when not specified'
    )
    parser.add_argument(
        '-r',
        '--default_reaction_priority',
        metavar='default_reaction_priority',
        type=float,
        default=viv_compiler.config.DEFAULT_REACTION_PRIORITY_VALUE,
        help='default reaction priority to use when not specified'
    )
    parser.add_argument(
        '-p',
        '--print',
        action='store_true',
        default=False,
        help='after compilation, print compiled content bundle in console'
    )
    parser.add_argument(
        '-l',
        '--list',
        action='store_true',
        default=False,
        help='after compilation, list all compiled actions in console'
    )
    parser.add_argument(
        '-m',
        '--memoization',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='enable/disable memoization in the underlying PEG parser',
    )
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        default=False,
        help='engage debug mode in the underlying PEG parser'
    )
    parser.add_argument(
        '-t',
        '--test',
        action='store_true',
        default=False,
        help='run a simple smoke test to confirm the compiler is installed correctly'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='print compiler version and exit'
    )
    return parser


def _run_smoke_test(args: argparse.Namespace) -> None:
    """Runs a smoke test to confirm that the Viv compiler installation appears to be functioning.

    Args:
        args: Parsed command-line arguments.

    Side Effects:
        The results are printed out to `stderr`.
    """
    with resources.as_file(resources.files("viv_compiler._samples") / "smoke-test.viv") as sample_path:
        compile_from_path(
            source_file_path=sample_path,
            default_salience=float(args.default_salience),
            default_associations=args.default_associations,
            default_reaction_priority=float(args.default_reaction_priority),
            debug=False,
            use_memoization=True,
        )
        print("Smoke test passed: Viv compiler installation looks good.\n", file=sys.stderr)


def _invoke_compiler(args: argparse.Namespace) -> CompiledContentBundle:
    """Invokes the compiler on the user's specified source file, with their specified configuration settings.

    Args:
        args: Parsed command-line arguments.

    Returns:
        The compiled content bundle, if compilation succeeds.
    """
    source_file_path = Path(args.input).expanduser().resolve()
    try:
        compiled_content_bundle = compile_from_path(
            source_file_path=source_file_path,
            default_salience=float(args.default_salience),
            default_associations=args.default_associations,
            default_reaction_priority=float(args.default_reaction_priority),
            debug=args.debug,
            use_memoization=args.memoization,
        )
        return compiled_content_bundle
    except KeyboardInterrupt:
        sys.exit(130)
    except BrokenPipeError:
        # noinspection PyBroadException
        try:
            sys.stderr.close()
        except Exception:
            pass
        sys.exit(1)
    except Exception as e:
        print(f"Error encountered during compilation: {e}", file=sys.stderr)
        if args.debug:
            traceback.print_exc()
        sys.exit(1)


def _emit_results(
    compiled_content_bundle: CompiledContentBundle,
    args: argparse.Namespace,
    path_to_output_file: Path | None
) -> None:
    """Emits the compiled content bundle according to the user's specified output parameters.

    Args:
        compiled_content_bundle: A compiled content bundle.
        args: Parsed command-line arguments.

    Side Effects:
        The results are written to file and/or printed to `stderr` and `stdout`, depending on user parameters.
    """
    # If we're to print out the result, let's do so now, via `stdout` (with headers piped to `stderr`)
    if args.print:
        print("    == Result ==\n", file=sys.stderr)
        sys.stdout.write(json.dumps(compiled_content_bundle, indent=2, sort_keys=True))
        sys.stdout.write("\n\n")
    # If we're to list out the compiled actions, let's do so now (again via
    # `stdout`, with headers piped to `stderr`).
    if args.list:
        lines = []
        action_names = [action_definition['name'] for action_definition in compiled_content_bundle['actions'].values()]
        for action_name in sorted(action_names):
            lines.append(action_name)
        if not action_names:
            lines.append("N/A")
        print(f"    == Actions ({len(action_names)}) ==\n", file=sys.stderr)
        print("\n".join(f"- {line}" for line in lines), file=sys.stderr)
        print("", file=sys.stderr)
    # If an output file path has been provided, write the output file to the specified path
    if path_to_output_file:
        with open(path_to_output_file, "w", encoding="utf-8") as outfile:
            outfile.write(json.dumps(compiled_content_bundle, ensure_ascii=False))
        print(f"Wrote output to file: {path_to_output_file}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
