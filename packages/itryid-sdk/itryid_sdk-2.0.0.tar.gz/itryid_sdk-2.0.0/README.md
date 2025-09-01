# ItryID SDK v2.0

Modern Python SDK for ItryID authentication and game progress management with improved architecture, type safety, and error handling.

## Features

- 🔐 **User Authentication** - Register, login, logout with validation
- 🎮 **Game Progress Management** - Save/load progress with automatic sync
- 💾 **Local Storage** - Automatic local caching with fallback
- 🔄 **Retry Logic** - Automatic retry for failed network requests
- 🛡️ **Type Safety** - Full type hints and data models
- 📝 **Comprehensive Logging** - Detailed logging for debugging
- ⚡ **Modern Architecture** - Clean, maintainable code structure

## Installation

\`\`\`bash
pip install itryid-sdk
\`\`\`

## Quick Start

\`\`\`python
from itryid import ItryIDClient, GameProgress

# Initialize client
client = ItryIDClient(
    server_url="https://your-server.com/api.php",
    game_name="my_awesome_game"
)

# Register new user
try:
    response = client.register("username", "password123", "user@example.com")
    print("Registration successful!")
except ValidationError as e:
    print(f"Validation error: {e}")

# Login
try:
    response = client.login("username", "password123")
    print(f"Logged in as: {client.user.username}")
except AuthenticationError as e:
    print(f"Login failed: {e}")

# Update and save progress
client.update_progress(level=5, score=1500, achievements=["first_win"])
response = client.save_progress()
print(f"Progress saved: {response.status}")

# Load progress
progress = client.load_progress()
print(f"Current level: {progress.level}, Score: {progress.score}")
\`\`\`

## Advanced Usage

### Custom Progress Model

\`\`\`python
from itryid import GameProgress

# Create custom progress
progress = GameProgress(
    level=10,
    score=5000,
    achievements=["speedrun", "perfectionist"],
    settings={"difficulty": "hard", "sound": True}
)

# Save custom progress
client.save_progress(progress)
\`\`\`

### Error Handling

\`\`\`python
from itryid import NetworkError, AuthenticationError, ValidationError

try:
    client.login("user", "pass")
except NetworkError as e:
    print(f"Network issue: {e}")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except ValidationError as e:
    print(f"Invalid input: {e}")
\`\`\`

### Configuration

\`\`\`python
client = ItryIDClient(
    server_url="https://api.example.com",
    game_name="my_game",
    local_save_path="./saves/progress.json",  # Custom save location
    timeout=15,  # Request timeout in seconds
    retry_attempts=5  # Number of retry attempts
)
\`\`\`

## API Reference

### ItryIDClient

Main client class for interacting with ItryID API.

#### Methods

- `register(username, password, email=None)` - Register new user
- `login(username, password)` - Login user
- `logout()` - Logout and clear local data
- `is_logged_in()` - Check login status
- `save_progress(progress=None)` - Save game progress
- `load_progress()` - Load current progress
- `update_progress(**kwargs)` - Update progress fields

### Models

#### User
- `user_id: Optional[int]` - User ID from server
- `username: str` - Username
- `email: Optional[str]` - Email address
- `created_at: Optional[str]` - Account creation date

#### GameProgress
- `level: int` - Current game level
- `score: int` - Player score
- `achievements: List[str]` - Unlocked achievements
- `settings: Dict[str, Any]` - Game settings
- `last_played: Optional[str]` - Last play timestamp

#### APIResponse
- `status: str` - Response status
- `message: Optional[str]` - Response message
- `data: Optional[Dict]` - Response data
- `is_success: bool` - Success indicator

### Exceptions

- `ItryIDError` - Base exception
- `NetworkError` - Network-related errors
- `AuthenticationError` - Authentication failures
- `ValidationError` - Input validation errors
- `ServerError` - Server-side errors

## Development

### Setup Development Environment

\`\`\`bash
git clone https://github.com/IGBerko/itryid-sdk.git
cd itryid-sdk
pip install -e ".[dev]"
\`\`\`

### Run Tests

\`\`\`bash
pytest tests/ -v --cov=itryid
\`\`\`

### Code Formatting

\`\`\`bash
black itryid/
flake8 itryid/
mypy itryid/
\`\`\`

## Changelog

### v2.0.0
- Complete rewrite with modern architecture
- Added type safety and data models
- Improved error handling and validation
- Added comprehensive logging
- Better local storage management
- Retry logic for network requests
- Enhanced documentation

### v1.0.1
- Initial release
- Basic authentication and progress saving

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: https://github.com/IGBerko/itryid-sdk/issues
- Email: support@ut.itrypro.ru
