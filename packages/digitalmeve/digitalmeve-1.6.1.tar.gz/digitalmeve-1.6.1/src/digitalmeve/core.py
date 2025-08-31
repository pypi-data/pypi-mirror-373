"""
digitalmeve.core

Point d’entrée stable du package : expose les fonctions publiques
`generate_meve` et `verify_meve` sans provoquer d’imports circulaires.
Les implémentations réelles vivent dans `generator.py` et `verifier.py`.
"""

from __future__ import annotations

__all__ = ["generate_meve", "verify_meve"]


def generate_meve(*args, **kwargs):
    """
    Proxy vers `digitalmeve.generator.generate_meve`.

    On importe à l’intérieur de la fonction pour éviter tout import
    circulaire au chargement du module.
    """
    from .generator import generate_meve as _impl

    return _impl(*args, **kwargs)


def verify_meve(*args, **kwargs):
    """
    Proxy vers `digitalmeve.verifier.verify_meve`.

    Idem : import différé pour éviter les cycles d’import.
    """
    from .verifier import verify_meve as _impl

    return _impl(*args, **kwargs)
