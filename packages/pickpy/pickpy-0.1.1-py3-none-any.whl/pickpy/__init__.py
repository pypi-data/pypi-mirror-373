"""
pickpy: Terminal menu utilities for Python.

Usage:
    from pickpy import TerminalMenu
"""
from .terminal import Terminal, BColors
from .menu import TerminalMenu
from .keyboard import get_key

__all__ = ["Terminal", "BColors", "TerminalMenu", "get_key"]

