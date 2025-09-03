"""Stub for removed module to save space in minimal build."""

def __getattr__(name):
      if name == "__path__":
            return []
      raise ImportError(
            f"numpy.array_api.{name} is not available in this minimal build. "
            f"This module was removed to reduce package size."
      )

__all__ = []
