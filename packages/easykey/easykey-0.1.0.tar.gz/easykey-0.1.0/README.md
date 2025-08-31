# EasyKey Python Package

A simple Python wrapper for the [easykey](https://github.com/kingofmac/easykey) CLI that provides secure keychain access on macOS.

## Installation

### Prerequisites

1. First, ensure you have the `easykey` CLI installed and available in your PATH
2. Install this Python package:

```bash
pip install easykey
```

### Local Development Installation

If you're working with the source code:

```bash
cd python
pip install -e .
```

## Usage

### Basic Secret Retrieval

```python
import easykey

# Get a secret (this will trigger biometric authentication)
secret = easykey.secret("MySecretName")
print(secret)

# Get a secret with a reason for audit logging
secret = easykey.secret("MySecretName", "Connecting to production database")
```

### Listing and Status

```python
import easykey

# List all secret names
secrets = easykey.list()
for secret in secrets:
    print(f"Secret: {secret['name']}")

# List secrets with creation timestamps
secrets = easykey.list(include_timestamps=True)
for secret in secrets:
    print(f"Secret: {secret['name']}, Created: {secret.get('createdAt', 'Unknown')}")

# Get vault status
status = easykey.status()
print(f"Total secrets: {status['secrets']}")
print(f"Last access: {status['last_access']}")
```



## API Reference

### Functions

- **`secret(name, reason=None)`** - Retrieve a secret value
- **`get_secret(name, reason=None)`** - Alias for `secret()`
- **`list(include_timestamps=False)`** - List all secrets
- **`status()`** - Get vault status information

### Parameters

- **`name`** (str): The name/identifier of the secret
- **`reason`** (str, optional): Reason for the operation (for audit logging)
- **`include_timestamps`** (bool): Whether to include creation timestamps in list results


### Return Values

- **`secret()`** returns the secret value as a string
- **`list()`** returns a list of dictionaries with secret information
- **`status()`** returns a dictionary with vault status

### Exceptions

All functions may raise **`EasyKeyError`** if the underlying CLI operation fails.

## Security Notes

- This package is a thin wrapper around the easykey CLI
- All security features (biometric authentication, keychain integration) are handled by the CLI
- Secrets are retrieved through subprocess calls and are not cached in Python
- The package automatically locates the easykey binary in common installation paths

## Requirements

- macOS (required by the underlying easykey CLI)
- Python 3.7+
- easykey CLI installed and accessible

## Quick Start Example

```python
import easykey

# Check vault status
status = easykey.status()
print(f"Vault contains {status['secrets']} secrets")

# List all secrets
secrets = easykey.list()
for secret in secrets:
    print(f"Found secret: {secret['name']}")

# Retrieve a specific secret (requires biometric authentication)
secret_value = easykey.secret("MySecretName", "Accessing for API call")
print(f"Secret value: {secret_value}")
```

**Note:** This is a **read-only** package. To store or manage secrets, use the easykey CLI directly.

## License

MIT License - see the main easykey project for details.
