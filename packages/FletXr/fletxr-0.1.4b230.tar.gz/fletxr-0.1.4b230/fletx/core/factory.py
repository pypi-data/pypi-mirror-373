"""
FletX - FletX Widget Registry
"""

from typing import Dict, Type
import flet as ft

from fletx.utils.context import AppContext


####
##      FLETX WIDGET REGISTRY
#####
class FletXWidgetRegistry:
    """FletX Widget Registry
    This class manages the registration of FletX widgets with Flet.
    It allows widgets to be registered and ensures they are available
    for use in Flet applications.
    """

    _widgets: Dict[str, Type[ft.Control]] = {}
    """Dictionary to hold registered widget classes"""

    _registered: bool = False
    """Tracks if widgets have been registered with the Flet page"""

    _page: ft.Page = AppContext.get_data("page")
    """The Flet page where widgets will be registered"""

    @classmethod
    def register(cls, widget_class: Type[ft.Control]):
        """Registers a widget class with FletX"""

        if not issubclass(widget_class, ft.Control):
            raise TypeError(
                f"{widget_class.__name__} must inherit from flet.Control"
            )
        
        # Check if the widget class is already registered
        if widget_class.__name__ in cls._widgets:
            raise ValueError(
                f"{widget_class.__name__} is already registered"
            )
        
        # Check if the widget class is being registered after the page is registered
        if cls._registered:
            raise RuntimeError(
                "Widgets cannot be registered after the page is registered"
        )
        # Check if the widget class has the required methods
        if not hasattr(widget_class, '_get_control_name'):
            raise AttributeError(
                f"{widget_class.__name__} must implement _get_control_name method"
            )

        # Build method
        if not hasattr(widget_class, 'build'):
            raise AttributeError(
                f"{widget_class.__name__} must implement build method"
            )
        if not hasattr(widget_class, 'did_mount'):
            raise AttributeError(
                f"{widget_class.__name__} must implement did_mount method"
            )
        if not hasattr(widget_class, 'will_unmount'):
            raise AttributeError(
                f"{widget_class.__name__} must implement will_unmount method"
            )
        if not hasattr(widget_class, 'bind'):
            raise AttributeError(
                f"{widget_class.__name__} must implement bind method"
            )
        
        # widget_class._get_control_name = lambda: widget_class.__name__
        widget_class._fletx_widget = True
        widget_class._fletx_widget_registry = cls
        cls._widgets[widget_class.__name__] = widget_class
        return widget_class

    @classmethod
    def register_all(cls, page: ft.Page):
        """Registers all widgets with the given Flet page"""

        if not isinstance(page, ft.Page):
            raise TypeError("page must be an instance of flet.Page")
        
        if not cls._registered:
            for name, widget in cls._widgets.items():
                page.register_control(name, widget)
            cls._registered = True