from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import json


RequiredKeys = ("issuer", "meve_version", "subject", "metadata", "timestamp")


def _load_meve_from_path(p: Union[str, Path]) -> Dict[str, Any]:
    """Read a .meve.json file and return its JSON content as dict."""
    path = Path(p)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def verify_identity(value: Optional[str]) -> bool:
    """
    Very small predicate used by tests:
    - valid if non-empty, all uppercase and alphanumeric.
    """
    return isinstance(value, str) and value.isupper() and value.isalnum()


def verify_meve(
    meve: Union[Dict[str, Any], str, Path],
    expected_issuer: Optional[str] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate a MEVE structure.

    - `meve` can be a dict (in-memory) or a path to a JSON file.
    - Returns (ok, info). On success, info echoes key parts.
      On failure, info contains an 'error' message (wording matters
      for the tests) and optional details.
    """
    # Load from file if a path/string is provided
    if isinstance(meve, (str, Path)):
        try:
            meve = _load_meve_from_path(meve)
        except Exception as exc:  # pragma: no cover
            return False, {"error": f"invalid file: {exc!s}"}

    # Must be a dict with required keys
    if not isinstance(meve, dict):
        return False, {"error": "invalid meve object"}

    missing = [k for k in RequiredKeys if k not in meve]
    if missing:
        # Tests look for *exact* wording with capital M
        return False, {"error": "Missing required keys", "missing": missing}

    # Optional issuer check
    if expected_issuer and meve.get("issuer") != expected_issuer:
        return False, {"error": "issuer mismatch", "expected": expected_issuer}

    # All good
    return True, {
        "issuer": meve["issuer"],
        "meve_version": meve["meve_version"],
        "subject": meve["subject"],
        "metadata": meve["metadata"],
        "timestamp": meve["timestamp"],
    }
