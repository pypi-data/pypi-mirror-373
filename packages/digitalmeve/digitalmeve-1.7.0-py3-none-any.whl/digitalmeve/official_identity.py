from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class OfficialIdentity:
    """Identité 'officielle'/institutionnelle minimale (extensible)."""
    authority: str
    contact: Optional[str] = None

    def as_dict(self):
        return {
            "type": "official",
            "authority": self.authority,
            "contact": self.contact,
        }
