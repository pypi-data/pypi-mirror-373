"""Data models for ItryID SDK."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import json

@dataclass
class User:
    """User data model."""
    user_id: Optional[int] = None
    username: str = "Guest"
    email: Optional[str] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class GameProgress:
    """Game progress data model."""
    level: int = 1
    score: int = 0
    achievements: list = None
    settings: Dict[str, Any] = None
    last_played: Optional[str] = None
    
    def __post_init__(self):
        if self.achievements is None:
            self.achievements = []
        if self.settings is None:
            self.settings = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameProgress':
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class APIResponse:
    """API response model."""
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        return self.status == "success"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIResponse':
        return cls(
            status=data.get("status", "error"),
            message=data.get("msg") or data.get("message"),
            data=data.get("data"),
            error=data.get("error")
        )
