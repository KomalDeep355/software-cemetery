"""Public interface for the explainable repository vitality heuristic.

The scoring rules live in features.assess alongside the feature definitions so
that each signal and its effect can be audited in one place. This module gives
API/UI code a stable, descriptive import path.
"""
from .features import assess as assess_vitality

__all__ = ["assess_vitality"]
