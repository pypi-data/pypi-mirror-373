from __future__ import annotations

from pathlib import Path
from typing import Optional, Union, Mapping


def format_identity(value: Optional[Union[str, Path, Mapping]]) -> str:
    """
    - str  -> retourne la string telle quelle
    - Path -> retourne le nom du fichier (sans extension) en MAJUSCULES
    - dict -> si clé 'identity' présente, on la renvoie
    - autres / None -> lève AttributeError
    """
    if isinstance(value, Path):
        return value.stem.upper()
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping) and "identity" in value:
        return str(value["identity"])
    raise AttributeError("invalid identity")
