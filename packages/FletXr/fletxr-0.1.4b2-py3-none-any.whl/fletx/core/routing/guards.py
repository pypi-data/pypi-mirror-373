"""
Route Guard System

This module defines a base interface for implementing route guards.
Route guards are used to control access to specific routes based on custom logic
(e.g., authentication, permissions, feature flags, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from fletx.core.routing.models import RouteInfo
from fletx.utils.exceptions import NavigationAborted


####
##      ROUTE GUARD INTERFACE 
#####
class RouteGuard(ABC):
    """Base interface for creating route guards.

    A route guard determines whether navigation to a route should be allowed.
    It can also provide an alternative redirection route if access is denied.
    """

    @abstractmethod
    async def can_activate(self, route: RouteInfo) -> bool:
        """
        Determines whether the given route is allowed to be activated (navigated to).

        Args:
            route (RouteInfo): Information about the route being accessed.

        Returns:
            bool: True if navigation to the route is allowed, False otherwise.
        """
        pass

    @abstractmethod
    async def can_deactivate(self, current_route: RouteInfo) -> bool:
        """
        Determines whether the given route is allowed to be deactivated.
        Args:
            current_route (RouteInfo): Information about the route being deactivated.

        Returns:
            bool: _description_
        """
        pass

    @abstractmethod
    async def redirect_to(self, route: RouteInfo) -> Optional[str]:
        """
        Specifies the fallback route to redirect to if `can_activate()` returns False.

        Args:
            route (RouteInfo): Information about the route that was blocked.

        Returns:
            str: A valid route path to redirect the user to (e.g., "/login").
        """
        return None
