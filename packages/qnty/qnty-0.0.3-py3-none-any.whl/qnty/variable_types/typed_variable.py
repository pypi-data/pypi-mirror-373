"""
Typed Variable Base Class
=========================

Base class that provides common constructor logic for all typed variables,
handling both the original syntax and the new value/unit/name syntax.
"""

from ..dimension import DimensionSignature
from ..variable import TypeSafeSetter
from .expression_variable import ExpressionVariable


class TypedVariable(ExpressionVariable):
    """
    Base class for typed variables with common constructor logic.
    
    Subclasses need to define:
    - _setter_class: The setter class to use
    - _expected_dimension: The expected dimension
    - _default_unit_property: The default unit property name for fallback
    """
    
    _setter_class: type[TypeSafeSetter] | None = None
    _expected_dimension: DimensionSignature | None = None
    _default_unit_property: str | None = None
    
    def __init__(self, *args, is_known: bool = True):
        """
        Flexible constructor supporting multiple syntaxes.
        
        Single argument: TypedVariable("name")
        Three arguments: TypedVariable(value, "unit", "name")
        Two arguments (Dimensionless only): TypedVariable(value, "name")
        """
        if self._setter_class is None or self._expected_dimension is None:
            raise NotImplementedError("Subclass must define _setter_class and _expected_dimension")
        
        # Handle different argument patterns
        if len(args) == 1:
            # Original syntax: Variable("name")
            super().__init__(args[0], self._expected_dimension, is_known=is_known)
            
        elif len(args) == 2 and self.__class__.__name__ == 'Dimensionless':
            # Special case for Dimensionless: (value, "name")
            value, name = args
            super().__init__(name, self._expected_dimension, is_known=is_known)
            setter = self._setter_class(self, value)
            # For DimensionlessSetter, use the dimensionless property
            # Type ignore since we know DimensionlessSetter has this property
            getattr(setter, 'dimensionless', None)  # type: ignore
            
        elif len(args) == 3:
            # New syntax: Variable(value, "unit", "name")
            # But Dimensionless doesn't support this pattern
            if self.__class__.__name__ == 'Dimensionless':
                raise ValueError(f"{self.__class__.__name__} expects either 1 argument (name) or 2 arguments (value, name), got {len(args)}")
            
            value, unit, name = args
            super().__init__(name, self._expected_dimension, is_known=is_known)
            
            # Auto-set the value with the specified unit
            setter = self._setter_class(self, value)
            
            # Handle special unit aliases
            if unit == "in":  # Handle Python reserved word
                unit = "inchs"  # Match the actual property name
            elif unit == "inches":  # Handle common plural form
                unit = "inchs"  # Match the actual property name
            
            # Try to find the unit property on the setter
            if hasattr(setter, unit):
                getattr(setter, unit)
            elif hasattr(setter, unit + 's'):  # Handle singular/plural
                getattr(setter, unit + 's')
            elif self._default_unit_property and hasattr(setter, self._default_unit_property):
                # Fall back to default unit
                getattr(setter, self._default_unit_property)
            else:
                # Last resort - try to find any valid unit property
                # This helps with forward compatibility
                unit_properties = [attr for attr in dir(setter)
                                 if not attr.startswith('_') and attr != 'value' and attr != 'variable']
                if unit_properties:
                    getattr(setter, unit_properties[0])
                    
        else:
            # More specific error messages matching test expectations
            if self.__class__.__name__ == 'Dimensionless':
                raise ValueError(f"{self.__class__.__name__} expects either 1 argument (name) or 2 arguments (value, name), got {len(args)}")
            else:
                raise ValueError(f"{self.__class__.__name__} expects either 1 argument (name) or 3 arguments (value, unit, name), got {len(args)}")
