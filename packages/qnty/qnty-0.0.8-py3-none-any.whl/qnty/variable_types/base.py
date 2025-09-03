"""
Base Variable Module Definition
===============================

Provides abstract base class for variable modules and registration functionality.
"""

from abc import ABC, abstractmethod
from typing import Any


class VariableModule(ABC):
    """Abstract base class for variable modules."""
    
    @abstractmethod
    def get_variable_class(self) -> type[Any]:
        """Return the variable class for this module."""
        pass
    
    @abstractmethod
    def get_setter_class(self) -> type[Any]:
        """Return the setter class for this module."""
        pass
    
    @abstractmethod
    def get_expected_dimension(self) -> Any:
        """Return the expected dimension for this variable type."""
        pass
    
    def register_to_registry(self, variable_registry):
        """Register this variable module to the given registry."""
        variable_registry.register_module(
            self.get_expected_dimension(),
            self.get_variable_class(),
            self.get_setter_class()
        )


class VariableRegistry:
    """Registry for variable modules."""
    
    def __init__(self):
        self._modules = {}
    
    def register_module(self, dimension, variable_class, setter_class):
        """Register a variable module."""
        self._modules[dimension] = {
            'variable_class': variable_class,
            'setter_class': setter_class
        }
    
    def get_variable_class(self, dimension):
        """Get variable class for a dimension."""
        return self._modules.get(dimension, {}).get('variable_class')
    
    def get_setter_class(self, dimension):
        """Get setter class for a dimension."""
        return self._modules.get(dimension, {}).get('setter_class')
