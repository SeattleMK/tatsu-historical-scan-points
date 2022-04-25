"""
UserHistory
"""

from typing import Any
from dataclasses import dataclass, field

@dataclass
class UserHistory:
    """
    Stores each user's post count as a dataclass object
    """

    users: dict = field(default_factory=dict)

    def __setattr__(self, name: str, value: Any) -> None:
        self.users[name] = value

    def __getattr__(self, name: str) -> Any:
        return self.users[name]