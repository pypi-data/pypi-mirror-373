"""
LLM UI Components Package

This package currently contains UI helpers for LLM integration.

Legacy standalone chat dialogs have been removed in favour of the unified
AI Assistant dialog integrated into the main GUI.  No public components are
exported at this time, but this package stub is kept to avoid breaking
imports in user code that may still reference *interfaces.llm.ui*.
"""

__all__: list[str] = []

__version__ = "1.1.0"  # Incremented after cleanup 