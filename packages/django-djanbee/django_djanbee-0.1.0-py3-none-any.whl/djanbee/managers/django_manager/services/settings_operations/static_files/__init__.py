"""
Django static files configuration handlers.

This package provides handlers for configuring static files in Django using
different strategies like WhiteNoise, Nginx, and Apache.
"""

from .static_root_handler import StaticRootHandler
from .static_root_handler_display import StaticRootHandlerDisplay

__all__ = [
    'StaticRootHandler',
    'StaticRootHandlerDisplay'
]