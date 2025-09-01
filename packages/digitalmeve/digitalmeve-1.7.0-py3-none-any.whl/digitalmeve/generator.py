from __future__ import annotations

from base64 import b64encode
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Dict, Optional, Any, Union


_MEVE_VERSION = "1.0"
_PREVIEW_BYTES = 128  # petite empreinte lisible pour debug/aperçu


def _file_sha256(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _preview_b64(path: Path, limit: int = _PREVIEW_BYTES) -> str:
    try:
        with path.open("rb") as f:
            head = f.read(limit)
        return b64encode(head).decode("ascii")
    except Exception:
        # l’aperçu est optionnel ; en cas de souci on renvoie une chaîne vide
        return ""


def generate_meve(
    file_path: Union[str, Path],
    outdir: Optional[Union[str, Path]] = None,
    issuer: str = "Personal",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Génère une preuve .meve au format dict.

    - Ajoute les clés attendues par les tests :
      * meve_version, issuer, timestamp, metadata
      * subject: { filename, size, hash_sha256 }
      * hash (copie de subject.hash_sha256)
      * preview_b64 (aperçu base64 de quelques octets)
    - Si `outdir` est fourni, écrit un sidecar JSON : <nom_fichier>.meve.json

    Retourne le dict de preuve.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"file not found: {path}")

    # calculs
    content_hash = _file_sha256(path)
    preview = _preview_b64(path)
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    proof: Dict[str, Any] = {
        "meve_version": _MEVE_VERSION,
        "issuer": issuer,
        "timestamp": ts,
        "metadata": metadata or {},
        "subject": {
            "filename": path.name,
            "size": path.stat().st_size,
            "hash_sha256": content_hash,
        },
        # duplication utile et demandée par les tests
        "hash": content_hash,
        "preview_b64": preview,
    }

    # écriture optionnelle du sidecar
    if outdir is not None:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        outfile = out / f"{path.name}.meve.json"

        # Écriture JSON minimale sans dépendances externes
        # (on garde une indentation faible pour rester léger)
        import json

        with outfile.open("w", encoding="utf-8") as f:
            json.dump(proof, f, ensure_ascii=False, separators=(",", ":"), indent=None)

    return proof
