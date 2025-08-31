from __future__ import annotations
from typing import Callable, List, Any
import inspect

from fletx import FletX
from fletx.core.effects import EffectManager

####    
def use_effect(effect_fn: Callable, dependencies: List[Any] = None):
    """Effect Decorator"""
    # Gets the effect manager instance
    # (to be integrated with FletX context)
    manager: EffectManager = FletX.find(EffectManager)
    
    # Generates a unique key based on the call location
    frame = inspect.currentframe().f_back
    key = f"useEffect_{frame.f_lineno}"
    
    manager.useEffect(effect_fn, dependencies, key)