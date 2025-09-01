"""
EvoSphere API Module

FastAPI-based web service interface for EvoSphere evolutionary bio-compiler.
Provides REST API access to all six patent-pending innovations.

Authors: Krishna Bajpai and Vedanshi Gupta
"""

from .server import create_app, EvoSphereAPI

__version__ = "1.0.0"
__all__ = [
    'create_app',
    'EvoSphereAPI'
]
