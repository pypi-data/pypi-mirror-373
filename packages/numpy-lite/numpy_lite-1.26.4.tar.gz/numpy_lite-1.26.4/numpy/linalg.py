"""Stub for removed module to save space in minimal build."""

def __getattr__(name):
      if name == "__path__":
            return []
      raise ImportError(
            f"numpy.linalg.{name} is not available in this minimal build. "
            f"This module was removed to reduce package size."
      )


def matrix_power(*args, **kwargs):
      raise ImportError(
            "numpy.linalg.matrix_power is not available in this minimal build."
      )

def eigvals(*args, **kwargs):
      raise ImportError(
            "numpy.linalg.eigvals is not available in this minimal build."
      )

def lstsq(*args, **kwargs):
      raise ImportError(
            "numpy.linalg.lstsq is not available in this minimal build."
      )

def inv(*args, **kwargs):
      raise ImportError(
            "numpy.linalg.inv is not available in this minimal build."
      )
__all__ = []
