from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

__all__ = ["verify_identity", "verify_meve"]

# Required keys for a valid MEVE object
_REQUIRED_TOP = (
    "meve_version",
    "issuer",
    "timestamp",
    "metadata",
    "subject",
    "hash",
)
_REQUIRED_SUBJECT = ("filename", "size", "hash_sha256")


# ---------------------------
# Simple identity validation
# ---------------------------
def verify_identity(value: Optional[str]) -> bool:
    """
    Return True iff `value` is a non-empty string (tests' expectation).
    """
    return isinstance(value, str) and bool(value.strip())


# ---------------------------
# MEVE loader & validators
# ---------------------------
def _load_meve(
    obj: Union[str, Path, Dict[str, Any]]
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Load a MEVE object from a file path or directly from a dict.
    Returns (data, None) if OK, else (None, {"error": "..."}).
    """
    if isinstance(obj, (str, Path)):
        p = Path(obj)
        try:
            text = p.read_text(encoding="utf-8")
            return json.loads(text), None
        except Exception:  # noqa: BLE001
            # Normalize any file-related error to the generic message expected by tests
            return None, {"error": "invalid file"}
    if isinstance(obj, dict):
        return obj, None
    return None, {"error": "invalid input type"}


def _missing_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return {"error": ..., "missing": [...]} if keys are missing, else {}."""
    missing = [k for k in _REQUIRED_TOP if k not in data]
    if missing:
        return {"error": "Missing required keys", "missing": missing}

    subj = data.get("subject", {})
    sub_missing = [k for k in _REQUIRED_SUBJECT if k not in subj]
    if sub_missing:
        return {"error": "Missing required keys", "missing": sub_missing}

    return {}


def verify_meve(
    meve: Union[str, Path, Dict[str, Any]],
    expected_issuer: Optional[str] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Verify a MEVE proof.

    Returns:
      (True, data) if valid,
      (False, {"error": "...", ...}) if invalid.
    """
    data, err = _load_meve(meve)
    if err is not None:
        return False, err
    assert data is not None

    miss = _missing_keys(data)
    if miss:
        return False, miss

    # hash consistency: top-level "hash" must equal subject.hash_sha256
    top_hash = data.get("hash")
    subj_hash = data.get("subject", {}).get("hash_sha256")
    if top_hash != subj_hash:
        return False, {"error": "hash mismatch"}

    # issuer check when an expected value is provided
    if expected_issuer is not None and data.get("issuer") != expected_issuer:
        return False, {
            "error": "issuer mismatch",
            "expected": expected_issuer,
            "found": data.get("issuer"),
        }

    return True, data
