# ibis_sqreamdb/__init__.py
from __future__ import annotations

# FIX: We only need to import the backend now
from . import backend
from .backend import Backend

def connect(*args, **kwargs) -> Backend:
    """A user-friendly connect function for the SQreamDB backend."""
    return Backend().connect(*args, **kwargs)

__all__ = ["Backend", "connect"]
