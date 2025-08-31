"""
RH (Reactive Html Framework) - Transform variable relationships into interactive web apps.

This package provides tools for creating reactive computational meshes where
variables can have bidirectional dependencies, automatically generating
interactive web interfaces with real-time updates.
"""

from .core import MeshBuilder

__all__ = ['MeshBuilder']
