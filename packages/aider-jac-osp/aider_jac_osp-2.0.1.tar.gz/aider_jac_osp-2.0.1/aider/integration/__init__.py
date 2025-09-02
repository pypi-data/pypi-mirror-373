"""
Python ↔ Jac Bridge Package

This package provides interfaces between the Aider Python code
and the Jac modules for OSP and Genius/MTP functionality.

Modules:
- jac_bridge.py      : Low-level communication bridge
- osp_interface.py   : High-level OSP integration interface
- mtp_interface.py   : High-level Genius/MTP interface
"""

# Make submodules accessible from the package level
from .jac_bridge import JacBridge
from .osp_interface import OSPInterface
from .mtp_interface import MTPInterface

__all__ = [
    "JacBridge",
    "OSPInterface",
    "MTPInterface",
]
