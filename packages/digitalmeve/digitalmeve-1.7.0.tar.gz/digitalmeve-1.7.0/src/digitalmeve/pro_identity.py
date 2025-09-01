from pathlib import Path
from typing import Optional, Union, Dict, Any


def format_identity(value: Optional[Union[str, Path, Dict[str, Any]]]) -> str:
    """
    Format an identity into a string.

    - str -> returns the string as is
    - Path -> returns the filename stem in uppercase
    - dict with "identity" -> returns the identity value
    - None or other -> raises AttributeError
    """
    if isinstance(value, Path):
        return value.stem.upper()
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and "identity" in value:
        return str(value["identity"])
    raise AttributeError("invalid identity")
