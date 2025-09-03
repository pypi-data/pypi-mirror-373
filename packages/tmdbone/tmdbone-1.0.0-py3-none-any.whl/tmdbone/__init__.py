"""
tmdbone: A comprehensive, resilient, and asynchronous TMDb API library.

This package provides an easy-to-use, object-oriented interface for The Movie Database API,
built with a powerful, resilient request engine that handles API key rotation,
automatic retries, and rate-limit cooldowns.
"""
from .client import TMDbOneClient
from .exceptions import TMDbException, TMDbAPIError

__version__ = "1.0.0"

# Defines the public API for the package
__all__ = ['TMDbOneClient', 'TMDbException', 'TMDbAPIError']