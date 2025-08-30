"""Binary management for hyperfusion."""

import platform
import os
from pathlib import Path

__all__ = ['get_binary_path']


def get_binary_path():
    """Get path to the hyperfusion binary for current platform."""
    binary_dir = Path(__file__).parent
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "windows":
        binary_name = "hyperfusion.exe"
    else:
        binary_name = "hyperfusion"
    
    # Look for platform-specific binary
    binary_path = binary_dir / f"{binary_name.replace('.exe', '')}-{system}-{arch}"
    if system == "windows":
        binary_path = binary_dir / f"{binary_path.name}.exe"
    
    if not binary_path.exists():
        binary_path = binary_dir / binary_name
    
    if not binary_path.exists():
        raise RuntimeError(f"hyperfusion binary not found for {system}-{arch}")
    
    return binary_path