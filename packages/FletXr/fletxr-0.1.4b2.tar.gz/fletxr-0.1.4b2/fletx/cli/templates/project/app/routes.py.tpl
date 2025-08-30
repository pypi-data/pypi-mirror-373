"""
{{ project_name }} Application routing module.
Version: {{ version }}
"""


# Import your pages here
from fletx.navigation import (
    ModuleRouter, TransitionType, RouteTransition
)
from fletx.decorators import register_router

from .pages import CounterPage, NotFoundPage

# Define {{ project_name | pascal_case }} routes here
routes = [
    {
        'path': '/',
        'component': CounterPage,
    },
    {
        'path': '/**',
        'component': NotFoundPage,
    },
]

@register_router
class {{ project_name | pascal_case }}Router(ModuleRouter):
    """{{ project_name }} Routing Module."""

    name = '{{ project_name }}'
    base_path = '/'
    is_root = True
    routes = routes
    sub_routers = []
