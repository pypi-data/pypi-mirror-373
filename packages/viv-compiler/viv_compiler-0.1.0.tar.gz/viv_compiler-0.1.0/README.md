# Viv Compiler

This package contains the reference compiler for the domain-specific language (DSL) at the heart of [Viv](https://github.com/james-owen-ryan/viv), an action system for emergent narrative.

The Viv compiler accepts a *Viv source file* (`.viv`) and produces a *Viv content bundle* in a JSON-serializable format conforming to the `CompiledContentBundle` schema defined [here](https://github.com/james-owen-ryan/viv/blob/main/compiler/src/viv_compiler/types/dsl_public_schemas.py), making it ready for usage in any Viv runtime.

Once you've installed this package, you'll have access to the two compiler interfaces that are documented below:

* A **command-line interface** (`vivc`) for invoking the compiler from the command line.

* A **Python API** for invoking the compiler programmatically.


## Table of Contents

- [Installation](#installation)
- [Command-Line Interface](#command-line-interface-cli)
- [Python API](#python-api)
- [Running from Source](#running-from-source)
- [License](#license)


## Installation

Install from PyPI:

```
pip install viv-compiler
```

This installs both the `viv_compiler` Python package and the `vivc` command-line interface.

Smoke test to confirm your installation looks good:

```
vivc --test
```


## Command-Line Interface (CLI)

Once you've installed `viv-compiler`, the Viv compiler CLI will be exposed via the command `vivc` (and its alias `viv-compiler`).


### Usage

```
vivc --input path/to/source.viv [options]
```


### Arguments

* `-i, --input <path_to_source_file>`

  * Required unless `--version` or `--test` is specified.
  * Relative or absolute path to the Viv source file (`.viv`) to compile.
  * If you are using `include` statements to import between files, this should be the main entrypoint file.

* `-o, --output <path_to_output_file>`

  * Optional.
  * Path to write the compiled JSON bundle.


### Flags and Options (Optional)

* `-h, --help`

	* Show help message and exit.

* `-s, --default_salience <float>`

  * Sets the default salience (floating-point number) for actions when unspecified.
  * Default: value from `viv_compiler.config.DEFAULT_SALIENCE_VALUE`.

* `-a, --default_associations <string ...>`

  * Sets the default associations (zero or more strings) for actions when unspecified.
  * Default: value from `viv_compiler.config.DEFAULT_ASSOCIATIONS_VALUE`.

* `-r, --default_reaction_priority <float>`

  * Sets the default reaction priority (floating-point number) for actions when unspecified.
  * Default: value from `viv_compiler.config.DEFAULT_REACTION_PRIORITY_VALUE`.

* `-m, --memoization, --no-memoization`

  * Enable/disable memoization in the underlying PEG parser (slower but uses less memory).
  * Default: enabled.

* `-p, --print`

  * After compilation, pretty-print the compiled bundle JSON.

* `-l, --list`

  * After compilation, print out a list of compiled action names.

* `-d, --debug`

  * Enable verbose debugging for the underlying PEG parser.

* `-t, --test`

  * Run a smoke test using a sample Viv file to confirm the installation works.
  * Ignores `--input`.

* `-v, --version`

  * Print the current compiler version and exit.


### Examples

Compile a source file and write the resulting content bundle to file:

```
vivc --input /path/to/my-actions.viv --output /path/to/myContentBundle.json
```

Compile a source file and log the output in the console:

```
vivc --input /path/to/my-actions.viv --print
```

Log the version number for the installed Viv compiler:

```
vivc -v
```


## Python API

The API is intended for programmatic invocation of the compiler.


### `compile_from_path()`

This function invokes the compiler for a specified Viv source file.

**Arguments**

* `source_file_path` (`Path`)

	* Absolute path to a `.viv` source file.

* `default_salience` (`float`)

	* Default salience for actions (if unspecified).

* `default_associations` `(list[str])`

	* Default associations for actions (if unspecified).

* `default_reaction_priority` (`float`)
	
	* Default reaction priority for actions (if unspecified).

* `use_memoization` (`bool`)

	* Whether to enable memoization in the underlying PEG parser (faster but uses more memory).

* `debug` (`bool`)

	* Whether to enable verbose debugging for the underlying PEG parser.

**Returns**

* The compiled Viv bundle, in a JSON-serializable format conforming to the `CompiledContentBundle` schema defined in the project code.

**Raises**

* `VivCompileError`

	* Raised when compilation fails.


### `get_version()`

Returns the version string for the currently installed compiler.


### `VivCompileError`

Custom exception type raised by the API when compilation fails. Inherits from `Exception`.


### Examples

Compile a source file:

```python
from pathlib import Path
from viv_compiler import compile_from_path, VivCompileError

try:
    content_bundle = compile_from_path(source_file_path=Path("my-actions.viv"))
    print("Compilation succeeded:", content_bundle)
except VivCompileError as e:
    print("Compilation failed:", e)
```

Print the version number for the installed Viv compiler:

```python
from viv_compiler import get_version
print(get_version())
```


## Running from Source

For contributors or developers working directly from a repo checkout:

```
# Clone the Viv monorepo
git clone https://github.com/james-owen-ryan/viv
cd viv/compiler

# Create a virtual environment
python -m venv .venv-viv-compiler
source .venv-viv-compiler/bin/activate   # macOS/Linux
# Windows PowerShell: .\.venv-viv-compiler\Scripts\Activate.ps1

# Install the compiler package from source (editable)
python -m pip install -e .

# Invoke the CLI directly
python -m viv_compiler --test

# Or use the installed console script
vivc --test
```


## License

MIT License © 2025 James Ryan
