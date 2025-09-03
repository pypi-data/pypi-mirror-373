"""
portndock - Dev-focused port watcher/killer with Docker awareness and live TUI.

A cross-platform terminal tool for developers to easily find and kill processes 
using specific ports, with special support for Docker containers.
"""

__version__ = "1.0.2"
__author__ = "Marc Carlo Dy"
__email__ = "dymarccarlo@yahoo.com"

from .main import main

__all__ = ["main"]