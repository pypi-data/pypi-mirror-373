"""
{{ name | pascal_case }} Controller.

This controller class is generated from a template.

🛠️ Customization Guide:
- You can rename or extend this class as needed.
  → Example: Inherit from a different base if you use a custom controller class.
- Add your own reactive attributes using types like `RxInt`, `RxStr`, `RxBool`, etc.
- Implement methods to handle business logic, side effects, or custom events.
- Controllers can be injected into components or apps using dependency injection or manual wiring.
"""

from fletx.core import (
    FletXController, RxInt
)

class {{ name | pascal_case }}Controller(FletXController):
    """{{ name | pascal_case }} Controller"""

    def __init__(self):
        # 🎯 Define your reactive state here
        count = RxInt(0)  # This value can be bound to a component
        super().__init__()

    def on_initialized(self):
        """Hook called when initializing controller"""
        print("{{ name | pascal_case }}Controller initialized.")

    def on_ready(self):
        """Hook called when the controller is ready"""
        print("{{ name | pascal_case }}Controller is READY!!!")
    
    def on_disposed(self):
        """Hook called when disposing controller"""
        print("{{ name | pascal_case }}Controller is disposing")

    # 💡 Example: add methods to update state or handle events
    # def increment(self):
    #     self.count.value += 1

    # def reset(self):
    #     self.count.value = 0