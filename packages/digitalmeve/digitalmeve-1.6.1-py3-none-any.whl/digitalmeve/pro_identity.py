from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProIdentity:
    """Identité 'pro' minimale (extensible)."""
    name: str
    email: Optional[str] = None
    organization: Optional[str] = None

    def as_dict(self):
        return {
            "type": "pro",
            "name": self.name,
            "email": self.email,
            "organization": self.organization,
        }
