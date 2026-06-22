"""
Cache de respuestas para evitar exceder RPD de Gemini.
Permite desarrollar sin consumir llamadas a API.
"""

import json
import os
from typing import Optional
from .models import TransferenceInput, TransferenceAnalysis

CACHE_FILE = os.path.join(os.path.dirname(__file__), ".cache.json")


def _get_cache_key(transfer: TransferenceInput) -> str:
    """Generar clave única para una transferencia."""
    return f"{transfer.id_movimiento}_{transfer.monto}_{transfer.concepto}"


def get_cached_analysis(transfer: TransferenceInput) -> Optional[TransferenceAnalysis]:
    """Obtener análisis desde caché si existe."""
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)

    key = _get_cache_key(transfer)
    if key in cache:
        data = cache[key]
        return TransferenceAnalysis(**data)
    return None


def save_to_cache(transfer: TransferenceInput, analysis: TransferenceAnalysis) -> None:
    """Guardar análisis en caché."""
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)

    key = _get_cache_key(transfer)
    cache[key] = analysis.model_dump()

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def clear_cache() -> None:
    """Limpiar caché."""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)


def cache_stats() -> dict:
    """Obtener estadísticas del caché."""
    if not os.path.exists(CACHE_FILE):
        return {"cached_items": 0, "file_size_kb": 0}

    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)

    size_kb = os.path.getsize(CACHE_FILE) / 1024
    return {"cached_items": len(cache), "file_size_kb": round(size_kb, 2)}
