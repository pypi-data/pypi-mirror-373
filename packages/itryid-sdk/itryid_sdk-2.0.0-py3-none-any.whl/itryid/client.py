"""Modern ItryID client with improved error handling and type safety."""

import requests
import json
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime

from .exceptions import NetworkError, AuthenticationError, ValidationError, ServerError
from .models import User, GameProgress, APIResponse

logger = logging.getLogger(__name__)

class ItryIDClient:
    """Modern ItryID client with improved architecture."""
    
    def __init__(
        self, 
        server_url: str, 
        game_name: str, 
        local_save_path: Optional[Union[str, Path]] = None,
        timeout: int = 10,
        retry_attempts: int = 3
    ):
        """
        Initialize ItryID client.
        
        Args:
            server_url: Full URL to PHP API endpoint
            game_name: Name of your game/application
            local_save_path: Path to local save file (defaults to ~/.itryid/{game_name}.json)
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
        """
        self.server_url = server_url.rstrip('/')
        self.game_name = self._validate_game_name(game_name)
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        
        # Setup local save path
        if local_save_path is None:
            save_dir = Path.home() / ".itryid"
            save_dir.mkdir(exist_ok=True)
            self.local_save_path = save_dir / f"{self.game_name}.json"
        else:
            self.local_save_path = Path(local_save_path)
            self.local_save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize user and progress
        self.user = User()
        self.progress = GameProgress()
        
        # Load local data
        self._load_local_data()
        
        logger.info(f"ItryID client initialized for game: {self.game_name}")
    
    def _validate_game_name(self, game_name: str) -> str:
        """Validate and sanitize game name."""
        if not game_name or not isinstance(game_name, str):
            raise ValidationError("Game name must be a non-empty string")
        
        # Remove potentially dangerous characters
        sanitized = "".join(c for c in game_name if c.isalnum() or c in "-_.")
        if not sanitized:
            raise ValidationError("Game name contains no valid characters")
        
        return sanitized[:50]  # Limit length
    
    def _load_local_data(self) -> None:
        """Load user data and progress from local storage."""
        try:
            if self.local_save_path.exists():
                with open(self.local_save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Load user data
                if 'user' in data:
                    self.user = User.from_dict(data['user'])
                
                # Load progress data
                if 'progress' in data:
                    self.progress = GameProgress.from_dict(data['progress'])
                    
                logger.debug("Local data loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load local data: {e}")
            # Reset to defaults on error
            self.user = User()
            self.progress = GameProgress()
    
    def _save_local_data(self) -> None:
        """Save user data and progress to local storage."""
        try:
            data = {
                'user': self.user.to_dict(),
                'progress': self.progress.to_dict(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.local_save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.debug("Local data saved successfully")
        except Exception as e:
            logger.error(f"Failed to save local data: {e}")
    
    def _make_request(self, payload: Dict[str, Any]) -> APIResponse:
        """Make HTTP request to API with retry logic."""
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f"Making API request (attempt {attempt + 1}): {payload.get('action')}")
                
                response = requests.post(
                    self.server_url,
                    data=payload,
                    timeout=self.timeout,
                    headers={'User-Agent': f'ItryID-SDK/2.0.0 ({self.game_name})'}
                )
                response.raise_for_status()
                
                # Parse JSON response
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    raise ServerError(f"Invalid JSON response: {e}")
                
                api_response = APIResponse.from_dict(data)
                logger.debug(f"API response: {api_response.status}")
                
                return api_response
                
            except requests.exceptions.Timeout as e:
                last_exception = NetworkError(f"Request timeout: {e}")
            except requests.exceptions.ConnectionError as e:
                last_exception = NetworkError(f"Connection error: {e}")
            except requests.exceptions.HTTPError as e:
                last_exception = ServerError(f"HTTP error: {e}")
            except Exception as e:
                last_exception = NetworkError(f"Unexpected error: {e}")
            
            if attempt < self.retry_attempts - 1:
                logger.warning(f"Request failed, retrying... ({last_exception})")
        
        # All attempts failed
        logger.error(f"All {self.retry_attempts} attempts failed")
        raise last_exception
    
    def register(self, username: str, password: str, email: Optional[str] = None) -> APIResponse:
        """
        Register a new user.
        
        Args:
            username: Username (3-30 characters, alphanumeric + underscore)
            password: Password (minimum 6 characters)
            email: Optional email address
            
        Returns:
            APIResponse with registration result
            
        Raises:
            ValidationError: If input validation fails
            NetworkError: If network request fails
            ServerError: If server returns an error
        """
        # Validate inputs
        if not username or len(username) < 3 or len(username) > 30:
            raise ValidationError("Username must be 3-30 characters long")
        
        if not password or len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        
        if email and '@' not in email:
            raise ValidationError("Invalid email format")
        
        payload = {
            'action': 'register',
            'username': username,
            'password': password
        }
        
        if email:
            payload['email'] = email
        
        response = self._make_request(payload)
        
        if not response.is_success:
            if response.status == 'username_taken':
                raise ValidationError("Username is already taken")
            else:
                raise ServerError(response.message or response.error or "Registration failed")
        
        logger.info(f"User registered successfully: {username}")
        return response
    
    def login(self, username: str, password: str) -> APIResponse:
        """
        Login user and update local state.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            APIResponse with login result
            
        Raises:
            ValidationError: If input validation fails
            AuthenticationError: If authentication fails
            NetworkError: If network request fails
        """
        if not username or not password:
            raise ValidationError("Username and password are required")
        
        payload = {
            'action': 'login',
            'username': username,
            'password': password
        }
        
        response = self._make_request(payload)
        
        if not response.is_success:
            if response.status in ['wrong_password', 'user_not_found']:
                raise AuthenticationError("Invalid username or password")
            else:
                raise ServerError(response.message or response.error or "Login failed")
        
        # Update user state
        self.user.user_id = response.data.get('user_id') if response.data else None
        self.user.username = username
        self._save_local_data()
        
        logger.info(f"User logged in successfully: {username}")
        return response
    
    def logout(self) -> None:
        """Logout user and clear local data."""
        self.user = User()
        self.progress = GameProgress()
        self._save_local_data()
        logger.info("User logged out")
    
    def is_logged_in(self) -> bool:
        """Check if user is currently logged in."""
        return self.user.user_id is not None
    
    def join_game(self) -> APIResponse:
        """Join the current game (creates user-game relationship on server)."""
        if not self.is_logged_in():
            raise AuthenticationError("User must be logged in to join game")
        
        payload = {
            'action': 'join_game',
            'user_id': self.user.user_id,
            'game_name': self.game_name
        }
        
        response = self._make_request(payload)
        
        if not response.is_success:
            raise ServerError(response.message or response.error or "Failed to join game")
        
        logger.info(f"Joined game: {self.game_name}")
        return response
    
    def save_progress(self, progress: Optional[GameProgress] = None) -> APIResponse:
        """
        Save game progress to server and local storage.
        
        Args:
            progress: GameProgress object to save (uses current progress if None)
            
        Returns:
            APIResponse with save result
        """
        if progress:
            self.progress = progress
        
        # Always save locally first
        self._save_local_data()
        
        if not self.is_logged_in():
            logger.info("Progress saved locally (user not logged in)")
            return APIResponse(status="saved_locally", message="Progress saved locally")
        
        try:
            # Ensure user is joined to game
            self.join_game()
            
            payload = {
                'action': 'save_progress',
                'user_id': self.user.user_id,
                'game_name': self.game_name,
                'progress_json': json.dumps(self.progress.to_dict(), ensure_ascii=False)
            }
            
            response = self._make_request(payload)
            
            if not response.is_success:
                logger.warning(f"Failed to save progress to server: {response.message}")
                return APIResponse(status="saved_locally", message="Progress saved locally (server error)")
            
            logger.info("Progress saved to server successfully")
            return response
            
        except Exception as e:
            logger.warning(f"Failed to save progress to server: {e}")
            return APIResponse(status="saved_locally", message="Progress saved locally (server unavailable)")
    
    def load_progress(self) -> GameProgress:
        """Load current game progress."""
        return self.progress
    
    def update_progress(self, **kwargs) -> None:
        """
        Update progress fields.
        
        Args:
            **kwargs: Progress fields to update (level, score, achievements, etc.)
        """
        for key, value in kwargs.items():
            if hasattr(self.progress, key):
                setattr(self.progress, key, value)
            else:
                logger.warning(f"Unknown progress field: {key}")
        
        self._save_local_data()
