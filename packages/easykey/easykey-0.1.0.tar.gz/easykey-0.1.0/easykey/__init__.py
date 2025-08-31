"""
EasyKey Python Package

A simple Python wrapper for the easykey CLI that provides secure keychain access.
"""

import subprocess
import json
import os
import shutil
from typing import Optional, List, Dict, Any


class EasyKeyError(Exception):
    """Exception raised by EasyKey operations."""
    pass


def _find_easykey_binary() -> str:
    """Find the easykey binary in common locations."""
    # Check if it's in PATH
    binary_path = shutil.which('easykey')
    if binary_path:
        return binary_path
    
    # Check common installation locations
    common_paths = [
        '/usr/local/bin/easykey',
        '/opt/homebrew/bin/easykey',
        os.path.expanduser('~/bin/easykey'),
        # Check relative to this package (if installed alongside)
        os.path.join(os.path.dirname(__file__), '../../bin/easykey'),
    ]
    
    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    raise EasyKeyError(
        "easykey binary not found. Please ensure easykey is installed and available in PATH, "
        "or install it to one of the standard locations: /usr/local/bin, /opt/homebrew/bin, or ~/bin"
    )


def _run_easykey_command(args: List[str]) -> str:
    """Run easykey command and return stdout."""
    try:
        binary_path = _find_easykey_binary()
        result = subprocess.run(
            [binary_path] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        raise EasyKeyError(f"easykey command failed: {error_msg}")
    except FileNotFoundError as e:
        raise EasyKeyError(f"easykey binary not found: {e}")


def secret(name: str, reason: Optional[str] = None) -> str:
    """
    Retrieve a secret from the easykey vault.
    
    Args:
        name: The name of the secret to retrieve
        reason: Optional reason for accessing the secret (for audit logging)
    
    Returns:
        The secret value as a string
        
    Raises:
        EasyKeyError: If the secret cannot be retrieved
    """
    args = ['get', name, '--quiet']
    if reason:
        args.extend(['--reason', reason])
    
    return _run_easykey_command(args)


def list(include_timestamps: bool = False) -> List[Dict[str, Any]]:
    """
    List all secrets in the easykey vault.
    
    Args:
        include_timestamps: Whether to include creation timestamps
        
    Returns:
        A list of dictionaries containing secret information
        
    Raises:
        EasyKeyError: If the secrets cannot be listed
    """
    args = ['list', '--json']
    if include_timestamps:
        args.append('--verbose')
    
    output = _run_easykey_command(args)
    if not output:
        return []
    
    try:
        return json.loads(output)
    except json.JSONDecodeError as e:
        raise EasyKeyError(f"Failed to parse easykey output: {e}")


def status() -> Dict[str, Any]:
    """
    Get the status of the easykey vault.
    
    Returns:
        A dictionary containing vault status information
        
    Raises:
        EasyKeyError: If the status cannot be retrieved
    """
    output = _run_easykey_command(['status'])
    
    # Parse the output format:
    # secrets: 5
    # last_access: 2023-08-27T15:30:45.123Z
    result = {}
    for line in output.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if key == 'secrets':
                result['secrets'] = int(value)
            elif key == 'last_access':
                result['last_access'] = value if value != '-' else None
            else:
                result[key] = value
    
    return result


# Alias for backward compatibility and convenience
get_secret = secret


__version__ = "0.1.0"
__all__ = [
    'secret',
    'get_secret', 
    'list',
    'status',
    'EasyKeyError'
]
