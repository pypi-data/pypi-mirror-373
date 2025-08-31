"""
Global context of the application.

This context holds shared state and configuration accessible throughout
the lifecycle of the application, enabling consistent data management
and coordination between different components and pages.
"""

import flet as ft
import threading
from typing import Optional, Dict, Any

####
##      FLETX APPLICATION CONTEXT
#####
class AppContext:
    """
    Global context of the FletX application.

    Provides shared state and configuration accessible across all components
    and pages within the FletX app lifecycle.
    """
    
    _page: Optional[ft.Page] = None
    _data: Dict[str, Any] = {}
    _debug: bool = False
    _is_initialized: bool = False
    _lock = threading.Lock()
    
    @classmethod
    def initialize(cls, page: ft.Page, debug: bool = False):
        """Initializes the global context"""

        with cls._lock:
            cls._page = page
            cls._debug = debug
            cls._data = {}
            cls._is_initialized = True
    
    @classmethod
    def get_page(cls) -> Optional[ft.Page]:
        """Retrieves the current Flet page"""
        return cls._page
    
    @classmethod
    def set_data(cls, key: str, value: Any):
        """Stores data in the context"""

        with cls._lock:
            cls._data[key] = value
    
    @classmethod
    def get_data(cls, key: str, default: Any = None) -> Any:
        """Retrieves data from the context"""
        return cls._data.get(key, default)
    
    @classmethod
    def remove_data(cls, key: str) -> bool:
        """Removes data from the context"""

        if key in cls._data:
            del cls._data[key]
            return True
        return False
    
    @classmethod
    def clear_data(cls):
        """Clears all data from the context"""
        cls._data.clear()
    
    @classmethod
    def is_debug(cls) -> bool:
        """Returns whether debug mode is enabled"""
        return cls._debug