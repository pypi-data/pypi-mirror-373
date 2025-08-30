# Gymix Python SDK

![PyPI](https://img.shields.io/pypi/v/gymix)
![Python](https://img.shields.io/pypi/pyversions/gymix)
![License](https://img.shields.io/pypi/l/gymix)

Official Python SDK for the Gymix API - A comprehensive gym management and backup service platform.

## Features

- 🏋️ **User Management**: Get user profile and gym information
- 🏢 **Gym Management**: Access gym details, subscriptions, and plans
- 💾 **Backup Services**: Create, list, download, and delete gym backups
- 🔐 **Authentication**: Secure API key-based authentication
- 📊 **Health Monitoring**: Check API service status
- 🚀 **Easy to Use**: Simple and intuitive Python interface
- 🛡️ **Type Safe**: Full type hints support
- ⚡ **Async Support**: Built-in support for async/await patterns

## Installation

```bash
pip install gymix
```

## Quick Start

```python
from gymix import GymixClient

# Initialize the client
client = GymixClient(api_token="your_api_token_here")

# Get user information
user_info = client.users.get_info()
print(f"Welcome, {user_info['name']} {user_info['lastname']}")

# Get gym information
gym_info = client.gym.get_info(gym_public_key="your_gym_key")
print(f"Gym: {gym_info['gym_info']['name']}")

# Create a backup
with open("backup.zip", "rb") as backup_file:
    backup = client.backup.create(
        gym_public_key="your_gym_key",
        file=backup_file
    )
print(f"Backup created with ID: {backup['id']}")

# List all backups
backups = client.backup.list(gym_public_key="your_gym_key")
for backup in backups['backups']:
    print(f"Backup: {backup['file_name']} - {backup['created_at']}")
```

## Authentication

The Gymix SDK uses Bearer token authentication. You can obtain your API token from the Gymix dashboard.

```python
from gymix import GymixClient

client = GymixClient(api_token="your_api_token_here")
```

## API Reference

### Users

#### Get User Information

```python
user_info = client.users.get_info()
```

### Gym Management

#### Get Gym Information

```python
gym_info = client.gym.get_info(gym_public_key="gym_key")
```

### Backup Services

#### Create Backup

```python
with open("backup.zip", "rb") as file:
    backup = client.backup.create(gym_public_key="gym_key", file=file)
```

#### List Backups

```python
backups = client.backup.list(gym_public_key="gym_key", verified=False)
```

#### Download Backup

```python
download_info = client.backup.download(backup_id="backup_id", gym_public_key="gym_key")
# Use download_info['download_url'] to download the file
```

#### Delete Backup

```python
result = client.backup.delete(backup_id="backup_id", gym_public_key="gym_key")
```

#### Get Backup Plan Information

```python
plan_info = client.backup.get_plan(gym_public_key="gym_key")
```

### Health Check

#### Check API Health

```python
health = client.health.check()
print(f"API Status: {health['status']}")
```

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

```python
from gymix import GymixClient
from gymix.exceptions import (
    GymixAuthenticationError,
    GymixForbiddenError,
    GymixNotFoundError,
    GymixRateLimitError,
    GymixAPIError
)

client = GymixClient(api_token="your_token")

try:
    user_info = client.users.get_info()
except GymixAuthenticationError:
    print("Invalid or expired API token")
except GymixForbiddenError:
    print("Access forbidden - check account status")
except GymixNotFoundError:
    print("Resource not found")
except GymixRateLimitError:
    print("Rate limit exceeded")
except GymixAPIError as e:
    print(f"API error: {e.message}")
```

## Configuration

### Base URL

You can customize the base URL if needed:

```python
client = GymixClient(
    api_token="your_token",
    base_url="https://custom-api.gymix.ir"
)
```

### Timeout Settings

```python
client = GymixClient(
    api_token="your_token",
    timeout=30  # seconds
)
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/mrssd/gymix-python-sdk.git
cd python-sdk

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy gymix

# Format code
black gymix tests

# Lint code
flake8 gymix tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gymix

# Run specific test file
pytest tests/test_client.py
```

## Requirements

- Python 3.7+
- requests >= 2.25.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@gymix.ir
- 📖 Documentation: https://docs.gymix.ir/python-sdk
- 🐛 Issues: https://github.com/mrssd/gymix-python-sdk/issues

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details about changes in each version.
