"""
Navigation Middleware

This module provides a middleware system to intercept navigation events
and perform custom logic before and after route changes.
"""

from typing import Callable, Any, Optional
from fletx.core.routing.models import RouteInfo
from fletx.core.routing.models import (
    NavigationIntent
)

class RouteMiddleware:
    """Navigation middleware system.

    Allows registering hooks that run before or after a route change.
    Useful for logging, analytics, access control, confirmation dialogs, etc.
    """

    async def before_navigation(
        self, 
        from_route: RouteInfo, 
        to_route: RouteInfo
    ) -> Optional[NavigationIntent]:
        
        """Execute before navigation. Return NavigationIntent to redirect."""
        return None
    
    async def after_navigation(self, route_info: RouteInfo) -> None:
        """Execute after successful navigation."""
        pass
    
    async def on_navigation_error(
        self, 
        error: Exception, 
        route_info: RouteInfo
    ) -> None:
        """Execute when navigation fails."""
        pass
