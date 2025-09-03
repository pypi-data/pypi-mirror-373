"""
Base Unit Module Definition
===========================

Provides abstract base class for unit modules and registration functionality.
"""

from abc import ABC, abstractmethod
from typing import Any

from ..unit import UnitDefinition


class UnitModule(ABC):
    """Abstract base class for unit modules."""
    
    @abstractmethod
    def get_unit_definitions(self) -> list[UnitDefinition]:
        """Return list of unit definitions for this module."""
        pass
    
    @abstractmethod
    def get_units_class(self) -> type[Any]:
        """Return the units class for this module."""
        pass
    
    def register_to_registry(self, unit_registry):
        """Register all unit definitions to the given registry."""
        from ..unit import UnitConstant
        
        for unit_def in self.get_unit_definitions():
            if unit_def.name not in unit_registry.units:
                unit_registry.register_unit(unit_def)
        
        # Populate the units class with constants from registry
        units_class = self.get_units_class()
        for unit_def in self.get_unit_definitions():
            unit_constant = UnitConstant(unit_registry.units[unit_def.name])
            setattr(units_class, unit_def.name, unit_constant)
            
            # Add any aliases
            if unit_def.symbol and unit_def.symbol != unit_def.name:
                setattr(units_class, unit_def.symbol, unit_constant)
            
            # Special case for inch - add in_ alias since 'in' is a Python keyword
            if unit_def.name == "inch":
                units_class.in_ = unit_constant
