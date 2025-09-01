"""
mdxjs-py - Python bindings for mdxjs-rs.

Mirrors the @mdx-js/mdx API:
- compile(source, options?) -> str
- compile_sync(source, options?) -> str
"""

from typing import Literal, Optional


# Import the Rust module
try:
    from .mdxjs_py import compile as _compile, compile_sync as _compile_sync

    AVAILABLE = True
except ImportError:
    # Try mock implementation for testing
    try:
        from .mock import mock_compile as _compile

        _compile_sync = _compile
        # IMPORTANT: When falling back to the mock, report unavailable so tests that
        # require the real Rust engine are correctly skipped.
        AVAILABLE = False
        import logging

        logger = logging.getLogger(__name__)
        logger.warning("Using mock MDX validator - build Rust module for production use")
    except ImportError:
        AVAILABLE = False
        _compile = None
        _compile_sync = None


def compile(  # noqa: A001
    source: str,
    *,
    development: bool | None = None,
    jsx: bool | None = None,
    jsx_import_source: str | None = None,
    jsx_runtime: Literal["automatic", "classic"] | None = None,
    pragma: str | None = None,
    pragma_frag: str | None = None,
    pragma_import_source: str | None = None,
    provider_import_source: str | None = None,
) -> str:
    """Compile MDX to JavaScript.

    Args:
        source: MDX source code
        development: Enable development mode
        jsx: Process JSX
        jsx_import_source: JSX import source
        jsx_runtime: "automatic" or "classic"
        pragma: JSX pragma
        pragma_frag: JSX pragma fragment
        pragma_import_source: Pragma import source
        provider_import_source: Provider import source

    Returns
    -------
        Compiled JavaScript code

    Raises
    ------
        ValueError: If compilation fails
        ImportError: If Rust module not available
    """
    if not AVAILABLE:
        msg = "mdxjs-py not built. Run: cd mdxjs_py && maturin develop"
        raise ImportError(msg)

    return _compile(
        source,
        development=development,
        jsx=jsx,
        jsx_import_source=jsx_import_source,
        jsx_runtime=jsx_runtime,
        pragma=pragma,
        pragma_frag=pragma_frag,
        pragma_import_source=pragma_import_source,
        provider_import_source=provider_import_source,
    )


def compile_sync(
    source: str,
    *,
    development: bool | None = None,
    jsx: bool | None = None,
    jsx_import_source: str | None = None,
    jsx_runtime: Literal["automatic", "classic"] | None = None,
    pragma: str | None = None,
    pragma_frag: str | None = None,
    pragma_import_source: str | None = None,
    provider_import_source: str | None = None,
) -> str:
    """Compile MDX to JavaScript synchronously.

    Same as compile() - Rust implementation is already synchronous.
    """
    if not AVAILABLE:
        msg = "mdxjs-py not built. Run: cd mdxjs_py && maturin develop"
        raise ImportError(msg)

    return _compile_sync(
        source,
        development=development,
        jsx=jsx,
        jsx_import_source=jsx_import_source,
        jsx_runtime=jsx_runtime,
        pragma=pragma,
        pragma_frag=pragma_frag,
        pragma_import_source=pragma_import_source,
        provider_import_source=provider_import_source,
    )


def is_available() -> bool:
    """Check if the Rust module is available."""
    return AVAILABLE


__all__ = ["compile", "compile_sync", "is_available"]
