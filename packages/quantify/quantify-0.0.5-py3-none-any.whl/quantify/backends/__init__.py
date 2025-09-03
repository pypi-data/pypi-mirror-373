# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""
Standard library of commonly used backends.

This module contains the following class:
    - :class:`.SerialCompiler`.
"""

from .graph_compilation import SerialCompiler

__all__ = ["SerialCompiler"]
