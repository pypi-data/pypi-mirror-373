# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-29

### Added

- Initial release of Gymix Python SDK
- User management endpoints (`/users/info`)
- Gym information endpoints (`/gym/info`)
- Complete backup management:
  - Create backups (`/backup/create`)
  - List backups (`/backup/list`)
  - Download backups (`/backup/download/{backup_id}`)
  - Delete backups (`/backup/delete/{backup_id}`)
  - Get backup plan info (`/backup/plan`)
- Health check endpoint (`/health`)
- Comprehensive error handling with custom exception classes
- Type hints support for better IDE integration
- Authentication with Bearer tokens
- File upload support for backup creation
- Automatic retry logic and timeout handling
- Context manager support for proper resource cleanup
- Full documentation and examples

### Features

- 🏋️ User profile and gym management
- 🏢 Gym details, subscriptions, and plans
- 💾 Complete backup service integration
- 🔐 Secure API key authentication
- 📊 Health monitoring capabilities
- 🛡️ Type-safe development experience
- ⚡ Efficient HTTP session management
- 🚨 Comprehensive error handling

### API Coverage

- ✅ GET `/users/info` - Get user profile and gyms
- ✅ POST `/gym/info` - Get gym details and subscription info
- ✅ POST `/backup/create` - Upload backup files
- ✅ GET `/backup/plan` - Get backup plan information
- ✅ GET `/backup/list` - List all backups
- ✅ POST `/backup/download/{backup_id}` - Get download URLs
- ✅ DELETE `/backup/delete/{backup_id}` - Delete backups
- ✅ GET `/health` - API health check
