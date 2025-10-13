"""
Backward compatibility module for ban_judge.
This module re-exports functions from the new detectors module.
"""
from .detectors import check_text, preprocess_text, update_words

__all__ = ["check_text", "preprocess_text", "update_words"]
