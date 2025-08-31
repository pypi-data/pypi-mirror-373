from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional, Union


def _file_sha256(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _preview_b64(path: Path, limit: int = 64) -> str:
    with path.open("rb") as f:
        data = f.read(limit)
    return base64.b64encode(data).decode("ascii")


def generate_meve(
    file_path: Union[str, Path],
    *,
    outdir: Optional[Path] = None,
    issuer: str = "Personal",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Génère une preuve 'MEVE' minimale sous forme de dict.
    Si `outdir` est fourni, écrit aussi <filename>.meve.json dans ce répertoire.
    Les tests attendent au moins les clés suivantes au niveau racine :
    issuer, meve_version, hash, preview_b64, subject, timestamp, metadata.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"file not found: {path}")

    digest = _file_sha256(path)

    meve: Dict[str, Any] = {
        "issuer": issuer,
        "meve_version": "1.0",
        "hash": digest,
        "preview_b64": _preview_b64(path),
        "subject": {
            "filename": path.name,
            "size": path.stat().st_size,
            "hash_sha256": digest,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }

    if outdir is not None:
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        outfile = outdir / f"{path.name}.meve.json"
        with outfile.open("w", encoding="utf-8") as f:
            json.dump(meve, f, ensure_ascii=False, indent=2)

    return meve
