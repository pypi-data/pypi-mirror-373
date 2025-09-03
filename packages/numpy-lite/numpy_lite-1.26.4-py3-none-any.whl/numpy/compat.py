"""Stub for removed module to save space in minimal build."""

def __getattr__(name):
      if name == "__path__":
            return []
      raise ImportError(
            f"numpy.compat.{name} is not available in this minimal build. "
            f"This module was removed to reduce package size."
      )


def unicode(*args, **kwargs):
      raise ImportError(
            "numpy.compat.unicode is not available in this minimal build."
      )

def long(*args, **kwargs):
      raise ImportError(
            "numpy.compat.long is not available in this minimal build."
      )

def pickle(*args, **kwargs):
      raise ImportError(
            "numpy.compat.pickle is not available in this minimal build."
      )

def os_fspath(*args, **kwargs):
      raise ImportError(
            "numpy.compat.os_fspath is not available in this minimal build."
      )

def asbytes(*args, **kwargs):
      raise ImportError(
            "numpy.compat.asbytes is not available in this minimal build."
      )

def is_pathlib_path(*args, **kwargs):
      raise ImportError(
            "numpy.compat.is_pathlib_path is not available in this minimal build."
      )

def isfileobj(*args, **kwargs):
      raise ImportError(
            "numpy.compat.isfileobj is not available in this minimal build."
      )

def asunicode(*args, **kwargs):
      raise ImportError(
            "numpy.compat.asunicode is not available in this minimal build."
      )

def asstr(*args, **kwargs):
      raise ImportError(
            "numpy.compat.asstr is not available in this minimal build."
      )

def os_PathLike(*args, **kwargs):
      raise ImportError(
            "numpy.compat.os_PathLike is not available in this minimal build."
      )
__all__ = []
