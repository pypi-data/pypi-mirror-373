"""Utility functions for flavor."""

# Re-export platform utilities
from flavor.utils.platform import (
    get_arch_name,
    get_cpu_type,
    get_os_name,
    get_os_version,
    get_platform_string,
    normalize_platform_components,
)

# Re-export subprocess utilities
from flavor.utils.subprocess import (
    run_command,
    run_command_simple,
)

# Re-export XOR utilities
from flavor.utils.xor import (
    XOR_KEY,
    xor_decode,
    xor_encode,
)

__all__ = [
    # Platform utilities
    "get_os_name",
    "get_arch_name",
    "get_platform_string",
    "get_os_version",
    "get_cpu_type",
    "normalize_platform_components",
    # Subprocess utilities
    "run_command",
    "run_command_simple",
    # XOR utilities
    "XOR_KEY",
    "xor_encode",
    "xor_decode",
]
