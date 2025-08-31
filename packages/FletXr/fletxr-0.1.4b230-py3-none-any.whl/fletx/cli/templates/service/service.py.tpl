"""
{{ name | pascal_case }} Controller.

This Service class is generated from a template.
"""

from fletx.core import FletXService


class {{ name | pascal_case }}Service(FletXService):
    """{{ name | pascal_case }} Service"""

    def __init__(self, *args, **kwargs):
        self.base_url = ""

        # Init base class
        super().__init__(**kwargs)

    def on_start(self):
        """Do stuf here on {{ name | pascal_case }}Service start"""
        pass
    
    def on_stop(self):
        """Do stuf here on {{ name | pascal_case }}Service stop"""
        pass
