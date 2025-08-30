"""hyperfusion: High-performance SQL execution engine with UDTF support."""

# Export main UDTF decorator and utilities
from .udtf import udtf, UDTFFunction
from .udtf.registry import registry

# CLI is available via lazy import to avoid circular import
def cli_main(*args, **kwargs):
    """Lazy import wrapper for CLI main function."""
    from .cli.main import main
    return main(*args, **kwargs)

# Import dynamic version
from ._version import __version__
__all__ = ["udtf", "UDTFFunction", "registry", "cli_main"]

# Example usage in docstring
"""
Usage as library:

    from hyperfusion import udtf
    
    @udtf
    async def my_function(x: int, y: str) -> list[dict]:
        return [{"result": x, "input": y}]

Usage as CLI:

    $ hyperfusion run
    $ hyperfusion run python-kernel --port 50051
    $ pip install hyperfusion && hyperfusion --help
"""