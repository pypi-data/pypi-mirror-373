try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("viv-compiler")
    except PackageNotFoundError:
        # If we're running from a repo checkout, not the published package,
        # we can pull the version from file.
        from ._version import __version__
except ImportError as e:
    raise RuntimeError("viv_compiler appears to be corrupted: missing file `_version.py`") from e


from .api import compile_from_path, get_version, VivCompileError
__all__ = ["compile_from_path", "get_version", "VivCompileError", "__version__"]
