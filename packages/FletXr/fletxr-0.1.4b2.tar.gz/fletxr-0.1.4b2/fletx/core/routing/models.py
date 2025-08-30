import flet as ft
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, List, Optional, Type, Union
)

from fletx.core.routing.transitions import RouteTransition


####
##      ROUTE INFO CLASS
#####
@dataclass
class RouteInfo:
    """
    Route information
    Contains detailed information about a specific route,
    such as its path, parameters etc...
    """
    
    def __init__(
        self, 
        path: str, 
        params: Dict[str, Any] = None, 
        query: Dict[str, Any] = None,
        data: Dict[str, Any] = field(default_factory=dict),
        fragment: Optional[str] = None
    ):
        self.path = path
        self.params = params or {}
        self.query = query or {}
        self.data = data
        self.fragment = fragment
        self._extra = {}

    def add_extra(self, key: str, value: Any):
        """
        Adds additional data to the route
        Allows associating additional data with a route, 
        such as metadata, security information, or context data.
        """
        self._extra[key] = value
    
    def get_extra(self, key: str, default: Any = None) -> Any:
        """
        Gets additional data
        Retrieves the additional data associated with a route, 
        such as metadata, security information, or context data.
        """
        return self._extra.get(key, default)
    
    @property
    def full_url(self) -> str:
        """Returns the complete URL including query parameters"""

        query_str = "&".join([f"{k}={v}" for k, v in self.query.items()])
        url = self.path
        if query_str:
            url += f"?{query_str}"
        if self.fragment:
            url += f"#{self.fragment}"
        return url


####
##      NAVIGATION INTENT TYPE CLASS
#####
@dataclass
class NavigationIntent:
    """Intent data for navigation with additional context."""

    route: str
    data: Dict[str, Any] = field(default_factory=dict)
    replace: bool = False
    clear_history: bool = False
    transition: Optional['RouteTransition'] = None


####
##     ROUTE TYPE CLASS
#####
class RouteType(Enum):
    """Types of routes supported by the router."""

    PAGE = "page"           # Full page route
    VIEW = "view"           # Flet view route  
    NESTED = "nested"       # Nested route within a parent
    REDIRECT = "redirect"   # Redirect route
    MODULE = "module"       # Module route with sub-router


####
##      NAVIGATION MODE CLASS
#####
class NavigationMode(Enum):
    """Navigation modes for handling Flet's native navigation."""

    NATIVE = "native"       # Use Flet's native Page.route
    VIEWS = "views"         # Use Flet's View stack
    HYBRID = "hybrid"       # Combine both approaches


#####
##      ROUTER STATE 
#####
@dataclass
class RouterState:
    """Current state of the router."""

    current_route: RouteInfo
    history: List[RouteInfo] = field(default_factory=list)
    forward_stack: List[RouteInfo] = field(default_factory=list)
    navigation_mode: NavigationMode = NavigationMode.HYBRID
    active_views: List[ft.View] = field(default_factory=list)


#####
##      NAVIGATION RESULT
#####
class NavigationResult(Enum):
    """Result of navigation operation."""

    SUCCESS = "success"
    BLOCKED_BY_GUARD = "blocked_by_guard"
    REDIRECTED = "redirected"
    ERROR = "error"
    CANCELLED = "cancelled"


####
##      ROUTE RESOLVER INTERFACE
#####
class IRouteResolver(ABC):
    """Interface for route data resolvers."""
    
    @abstractmethod
    def resolve(self, route_info: RouteInfo) -> Any:
        """Resolve data for the route."""
        pass
