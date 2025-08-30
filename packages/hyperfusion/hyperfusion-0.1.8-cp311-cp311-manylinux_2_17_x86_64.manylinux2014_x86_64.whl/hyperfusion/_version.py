"""Version information for hyperfusion."""

import os
import subprocess
import re


def get_version_from_git(for_pypi=False):
    """Get version from git tags or fallback to development version.
    
    Args:
        for_pypi: If True, returns PyPI-compatible version (no local identifiers)
    """
    # First, check if version is set via environment variable (used in CI)
    env_version = os.environ.get('HYPERFUSION_VERSION')
    if env_version:
        # If the env version is in git describe format, convert it
        if re.match(r'^v?(\d+\.\d+\.\d+)-(\d+)-g([a-f0-9]+)(-dirty)?$', env_version):
            match = re.match(r'^v?(\d+\.\d+\.\d+)-(\d+)-g([a-f0-9]+)(-dirty)?$', env_version)
            if match:
                base_version, commits, sha, dirty = match.groups()
                if for_pypi:
                    # PyPI-compatible: just use base version + dev + commits
                    dev_version = f"{base_version}.dev{commits}"
                else:
                    # Local version: include git hash
                    dev_version = f"{base_version}.dev{commits}+g{sha}"
                    if dirty:
                        dev_version += ".dirty"
                return dev_version
        elif re.match(r'^v?\d+\.\d+\.\d+$', env_version):
            return env_version.lstrip('v')
        elif re.match(r'^[a-f0-9]{7,40}(-dirty)?$', env_version):
            # Just a commit hash from git describe when no tags available
            if for_pypi:
                # Use a timestamp-based version for uniqueness
                import time
                timestamp = int(time.time()) % 100000  # Last 5 digits for uniqueness
                return f"0.1.0.dev{timestamp}"
            else:
                return f"0.1.0.dev0+{env_version}"
        else:
            return env_version
    
    try:
        # Try to get version from git describe
        result = subprocess.run(
            ['git', 'describe', '--tags', '--always', '--dirty'],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        
        # If it's a clean tag (no additional commits), use it directly
        if re.match(r'^v?\d+\.\d+\.\d+$', version):
            return version.lstrip('v')
        
        # If it's a development version, format it properly
        match = re.match(r'^v?(\d+\.\d+\.\d+)-(\d+)-g([a-f0-9]+)(-dirty)?$', version)
        if match:
            base_version, commits, sha, dirty = match.groups()
            if for_pypi:
                # PyPI-compatible: just use base version + dev + commits
                dev_version = f"{base_version}.dev{commits}"
            else:
                # Local version: include git hash
                dev_version = f"{base_version}.dev{commits}+g{sha}"
                if dirty:
                    dev_version += ".dirty"
            return dev_version
        
        # Handle case where git describe only returns commit hash (no tags found)
        if re.match(r'^[a-f0-9]{7,40}(-dirty)?$', version):
            if for_pypi:
                # Use a timestamp-based version for uniqueness
                import time
                timestamp = int(time.time()) % 100000
                return f"0.1.0.dev{timestamp}"
            else:
                return f"0.1.0.dev0+{version}"
        
        # Fallback for other cases
        if for_pypi:
            import time
            timestamp = int(time.time()) % 100000
            return f"0.1.0.dev{timestamp}"
        else:
            return f"0.1.0.dev0+{version}"
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback when git is not available or not in a git repository
        return '0.1.0.dev0'


# Check if we're in a PyPI publishing context
_is_pypi_build = os.environ.get('PYPI_PUBLISHING', '').lower() in ('true', '1', 'yes')
__version__ = get_version_from_git(for_pypi=_is_pypi_build)