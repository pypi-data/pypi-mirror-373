"""
FletX Core Types and Interfaces.

This module defines the core types, interfaces, and data structures
used throughout the FletX system.
"""

import flet as ft
from abc import ABC, abstractmethod
from typing import (
    Dict, Any, Type, Optional, Callable, List, Union
)
from dataclasses import dataclass, field
from enum import Enum


####
##      BINDING TYPE CLASS
#####
class BindingType(Enum):
    """Types of reactive bindings"""

    ONE_WAY = "one_way"          # Reactive -> Widget
    TWO_WAY = "two_way"          # Reactive <-> Widget  
    ONE_TIME = "one_time"        # Reactive -> Widget (once)
    COMPUTED = "computed"        # Computed from multiple reactives


####
##      BINDING CONFIGURATION CLASS
#####
@dataclass
class BindingConfig:
    """Configuration for a reactive binding"""

    reactive_attr: str
    binding_type: BindingType = BindingType.ONE_WAY
    transform_to_widget: Optional[Callable[[Any], Any]] = None
    transform_from_widget: Optional[Callable[[Any], Any]] = None
    validation: Optional[Callable[[Any], bool]] = None
    on_change: Optional[Callable[[Any, Any], None]] = None  # (old_value, new_value)
    condition: Optional[Callable[[], bool]] = None
    debounce_ms: Optional[int] = None
    throttle_ms: Optional[int] = None


####
##      COMPUTED BINDING CONFIGURATION CLASS
#####
@dataclass
class ComputedBindingConfig:
    """Configuration for computed reactive bindings"""

    compute_fn: Callable[[], Any]
    dependencies: List[str]  # Names of reactive attributes
    transform: Optional[Callable[[Any], Any]] = None
    on_change: Optional[Callable[[Any, Any], None]] = None


####
##      REATIVE FORM VALIDATION RULE CLASS
#####
@dataclass
class FormFieldValidationRule:
    """Form Field Validation rule"""

    validate_fn: Union[str, Callable[[Union[str,int,float,bool]],bool]] 
    err_message: str
