"""
Widget Text personnalisé pour FletX
"""

import weakref
from typing import (
    Union, List, Callable, get_type_hints, Optional
)

from flet import *
from fletx.widgets import FletXWidget
from fletx.core.state import Reactive
from fletx.decorators.widgets import reactive_control, simple_reactive
from fletx.utils import get_logger, get_page



class ReactiveBuilder(Container, FletXWidget):
    """
    Reactive widget builder that preserves original control identity.
    It updates existing widget references instead of recreating them.
    Uses Flet's built-in update system for optimal performance.
    
    Features:
    - Automatic rebuilds when reactive dependencies update
    - Efficient dependency tracking
    - Clean disposal of observers

    Args:
        builder: Function returning a Flet control
        dependencies: Single or list of Reactive objects to watch
        auto_dispose: Automatically clean up observers (default: True)
    """

    def __init__(
        self,
        builder: Callable[[], Control],
        dependencies: Optional[Union[List[Reactive], Reactive]] = None,
        auto_dispose: bool = True
    ):
        super().__init__()
        # FletXWidget.__init__(self)
        self._logger = get_logger('FletX.ReactiveBuilder')

        self._builder = builder
        self._auto_dispose = auto_dispose
        self._dependencies = []
        self._listeners = []

        self.padding = padding.all(0)  # Default padding
        self.bgcolor = None  # Default background color
        
        # Setup reference container
        # self._ref = Ref[Control]()
        # self._current_widget = self._create_controlled_widget()

        self._logger.debug(
            "Initializing ReactiveBuilder with dependencies: %s", 
            dependencies
        )
        # Normalize dependencies
        if dependencies is not None:
            self._dependencies = (
                [dependencies] if isinstance(dependencies, Reactive) 
                else list(dependencies))
            
        self.content = self._builder()
        
        self._logger.debug("Builder function type: %s", type(builder))
        # for idx, dep in enumerate(self._dependencies):
        #     self.bind(f'_rx_dep_{idx}', dep)

        # self._setup_listeners()

    def _create_controlled_widget(self) -> Control:
        """Create widget with ref and preserved type"""

        widget = self._builder()
        widget.ref = self._ref  # Inject our reference
        return widget

    def _setup_listeners(self):
        """Setup reactive listeners using ref-based updates"""
        for dep in self._dependencies:
            def make_update_handler():
                def handler(*args, **kwargs):
                    """Handler to update the widget when dependencies change"""
                    self.content.update()
                return handler
            
            self._listeners.append(dep.listen(make_update_handler()))

    def __call__(self) -> Control:
        """Get the current controlled widget"""
        return self._current_widget

    def dispose(self):
        """Clean up all listeners"""
        for listener in self._listeners:
            listener()
        self._listeners.clear()

    def did_mount(self):
        self._setup_listeners()
        return super().did_mount()

    # def __init__(
    #     self,
    #     builder: Callable[[], Control],
    #     dependencies: Union[List[Reactive], Reactive, None] = None,
    #     auto_dispose: bool = True
    # ):
    #     self._builder = builder
    #     self._auto_dispose = auto_dispose
    #     self._dependencies: List[Reactive] = []
    #     self._listeners = []
    #     self._current_content = None
        
    #     # Normalize dependencies
    #     if dependencies is not None:
    #         self._dependencies = (
    #             [dependencies] if isinstance(dependencies, Reactive) 
    #             else dependencies
    #         )
        
    #     # Initial build
    #     self._current_content = self._build()

    # def _build(self) -> Control:
    #     """Execute builder and wrap the output while preserving reactivity"""
    #     try:
    #         content = self._builder()
            
    #         # Create dynamic bindings dictionary
    #         bindings = {}
    #         for i, dep in enumerate(self._dependencies):
    #             prop_name = f"content_attr_{i}"
    #             bindings[prop_name] = f"_rx_dep_{i}"

    #         deps = self._dependencies
            
    #         # Create reactive subclass
    #         @reactive_control(bindings=bindings)
    #         class ReactiveContent(content.__class__):
    #             """
    #             Reactive content wrapper that injects dependencies
    #             and preserves original control identity.
    #             """

    #             @classmethod
    #             def inject_dependencies(cls):
    #                 """Inject dependencies into the reactive content"""
    #                 # Inject Reactive dependencies
    #                 for i, dep in enumerate(deps):
    #                     setattr(cls, f"_rx_dep_{i}", dep)
    #                     setattr(cls, f"content_attr_{i}", None)
    #                     cls.__annotations__[f"_rx_dep_{i}"] = type(dep)
    #                     cls.__annotations__[f"content_attr_{i}"] = type(dep)

    #         # Instantiate and copy properties
    #         reactive_class = ReactiveContent
    #         reactive_class.inject_dependencies()
    #         # print(reactive_class.__dict__)
    #         wrapped = reactive_class()
            
            
    #         # 1. Copy all attributes from original content
    #         for attr, value in content.__dict__.items():
    #             if not attr.startswith('_'):  # Skip private attributes
    #                 setattr(wrapped, attr, value)
            
    #         # 2. Preserve critical Flet properties
    #         wrapped._Control__attrs = content._Control__attrs.copy()
    #         self._Control__attrs = content._Control__attrs.copy()
    #         wrapped._Control__uid = content._Control__uid
    #         self._Control__uid = content._Control__uid
    #         self.is_isolated = content.is_isolated
    #         # wrapped._Control__values = content._Control__values.copy()
            
    #         # 3. Inject dependencies as protected attributes
    #         # for i, dep in enumerate(self._dependencies):
    #         #     setattr(wrapped, f"_rx_dep_{i}", dep)
            
    #         # 4. Maintain page reference
    #         if hasattr(content, 'page') and content.page:
    #             page = content.page
    #         else: page = get_page()
            
    #         wrapped.__page = page
    #         # page.add(wrapped)  # Add to page
    #         return wrapped
            
    #     except Exception as e:
    #         return Text(f"Builder error: {e}", color="red")
        
    # def _build_add_commands(self,* args, **kwargs):
    #     """Encapsulate the build command for content"""

    #     if self._current_content is None:
    #         self._current_content = self._build()
        
    #     return self._current_content._build_add_commands(*args, **kwargs)
    
    # def build_update_commands(self, *args, **kwargs):
    #     """Encapsulate the update command for content"""

    #     if self._current_content is None:
    #         self._current_content = self._build()
        
    #     return self._current_content.build_update_commands(*args, **kwargs)
    
    # def _setup_listeners(self):
    #     """Setup reactive listeners for all dependencies"""

    #     for dep in self._dependencies:
    #         self._listeners.append(
    #             dep.listen(self._rebuild)
    #         )

    # def _rebuild(self):
    #     """Handle dependency changes"""

    #     if hasattr(self._current_content, 'page') and self._current_content.page:
    #         self._current_content = self._build()
    #         self._current_content.update()

    # def __call__(self) -> Control:
    #     """Returns the current reactive content"""

    #     return self._current_content

    # def did_mount(self):
    #     self._setup_listeners()
    #     return super().did_mount()

    # def dispose(self):
    #     """Clean up all listeners"""

    #     for listener in self._listeners:
    #         listener()
    #     self._listeners.clear()
