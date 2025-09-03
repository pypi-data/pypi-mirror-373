"""
Expression Variable Base Class
==============================

Base class that extends TypeSafeVariable with mathematical expression
and equation capabilities.
"""

from __future__ import annotations

from ..equation import Equation
from ..expression import Expression, wrap_operand
from ..variable import FastQuantity, TypeSafeVariable


class ExpressionVariable(TypeSafeVariable):
    """
    TypeSafeVariable extended with expression and equation capabilities.
    
    This adds mathematical operations that create expressions and equations,
    keeping the base TypeSafeVariable free of these dependencies.
    """
    
    def equals(self, expression: Expression | TypeSafeVariable | FastQuantity | int | float):
        """Create an equation: self = expression."""
        # Wrap the expression in proper Expression type
        rhs_expr = wrap_operand(expression)
        return Equation(f"{self.name}_eq", self, rhs_expr)
    
    def __add__(self, other: TypeSafeVariable | FastQuantity | int | float) -> Expression:
        """Add this variable to another operand, returning an Expression."""
        return wrap_operand(self) + wrap_operand(other)

    def __radd__(self, other: FastQuantity | int | float) -> Expression:
        """Reverse add for this variable."""
        return wrap_operand(other) + wrap_operand(self)
    
    def __sub__(self, other: TypeSafeVariable | FastQuantity | int | float) -> Expression:
        """Subtract another operand from this variable, returning an Expression."""
        return wrap_operand(self) - wrap_operand(other)
    
    def __rsub__(self, other: FastQuantity | int | float) -> Expression:
        """Reverse subtract for this variable."""
        return wrap_operand(other) - wrap_operand(self)
    
    def __mul__(self, other: TypeSafeVariable | FastQuantity | int | float) -> Expression:
        """Multiply this variable by another operand, returning an Expression."""
        return wrap_operand(self) * wrap_operand(other)
    
    def __rmul__(self, other: FastQuantity | int | float) -> Expression:
        """Reverse multiply for this variable."""
        return wrap_operand(other) * wrap_operand(self)
    
    def __truediv__(self, other: TypeSafeVariable | FastQuantity | int | float) -> Expression:
        """Divide this variable by another operand, returning an Expression."""
        return wrap_operand(self) / wrap_operand(other)

    def __rtruediv__(self, other: FastQuantity | int | float) -> Expression:
        """Reverse divide for this variable."""
        return wrap_operand(other) / wrap_operand(self)
    
    def __pow__(self, other: TypeSafeVariable | FastQuantity | int | float) -> Expression:
        """Raise this variable to a power, returning an Expression."""
        return wrap_operand(self) ** wrap_operand(other)

    def __rpow__(self, other: FastQuantity | int | float) -> Expression:
        """Reverse power for this variable."""
        return wrap_operand(other) ** wrap_operand(self)
