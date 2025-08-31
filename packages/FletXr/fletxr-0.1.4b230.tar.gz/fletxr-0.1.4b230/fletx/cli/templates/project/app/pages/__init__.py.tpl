"""
{{ project_name | pascal_case }} Application Pages module.

This module contains the application Pages.
Version: {{ version }}
"""

from .counter import CounterPage
from .not_found import NotFoundPage

__all__ = [
    'CounterPage',
    'NotFoundPage'
]
