#!/usr/bin/env python3
"""
GhostPeek - A stealthy domain reconnaissance tool

Author: kaizoku73
GitHub: https://github.com/kaizoku73/Ghostpeek
License: MIT
"""

__version__ = "1.1.0"
__author__ = "kaizoku73"

from .core import main

# Make main function available for import
__all__ = ["main", "__version__", "__author__"]