"""
Expression System
=================

Mathematical expressions for building equation trees with qnty variables.
"""

import math
from abc import ABC, abstractmethod
from typing import Union, cast

from .units import DimensionlessUnits

# if TYPE_CHECKING:
from .variable import FastQuantity, TypeSafeVariable


def wrap_operand(operand: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
    """
    Wrap non-Expression operands in appropriate Expression subclasses.
    
    This function handles type conversion without circular imports by using
    duck typing and delayed imports where necessary.
    """
    # Type guard for Expression types
    if hasattr(operand, 'evaluate') and hasattr(operand, 'get_variables'):
        # Already an Expression
        return cast('Expression', operand)
    elif hasattr(operand, 'name') and hasattr(operand, 'quantity') and hasattr(operand, 'is_known'):
        # TypeSafeVariable-like object
        return VariableReference(cast('TypeSafeVariable', operand))
    elif hasattr(operand, 'value') and hasattr(operand, 'unit') and hasattr(operand, '_dimension_sig'):
        # FastQuantity-like object
        return Constant(cast('FastQuantity', operand))
    elif isinstance(operand, int | float):
        # Numeric value - create dimensionless quantity

        return Constant(FastQuantity(float(operand), DimensionlessUnits.dimensionless))
    else:
        raise TypeError(f"Cannot convert {type(operand)} to Expression")


class Expression(ABC):
    """Abstract base class for mathematical expressions."""
    
    @abstractmethod
    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'FastQuantity':
        """Evaluate the expression given variable values."""
        pass
    
    @abstractmethod
    def get_variables(self) -> set[str]:
        """Get all variable symbols used in this expression."""
        pass
    
    @abstractmethod
    def simplify(self) -> 'Expression':
        """Simplify the expression."""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    def __add__(self, other: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        return BinaryOperation('+', self, wrap_operand(other))
    
    def __radd__(self, other: Union['TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        return BinaryOperation('+', wrap_operand(other), self)
    
    def __sub__(self, other: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        return BinaryOperation('-', self, wrap_operand(other))
    
    def __rsub__(self, other: Union['TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        return BinaryOperation('-', wrap_operand(other), self)
    
    def __mul__(self, other: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        return BinaryOperation('*', self, wrap_operand(other))
    
    def __rmul__(self, other: Union['TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        return BinaryOperation('*', wrap_operand(other), self)
    
    def __truediv__(self, other: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        return BinaryOperation('/', self, wrap_operand(other))
    
    def __rtruediv__(self, other: Union['TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        return BinaryOperation('/', wrap_operand(other), self)
    
    def __pow__(self, other: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        return BinaryOperation('**', self, wrap_operand(other))
    
    def __rpow__(self, other: Union['TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        return BinaryOperation('**', wrap_operand(other), self)
    
    # Comparison operators for conditional expressions
    def __lt__(self, other: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'ComparisonExpression':
        return ComparisonExpression('<', self, self._wrap_operand(other))

    def __le__(self, other: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'ComparisonExpression':
        return ComparisonExpression('<=', self, self._wrap_operand(other))
    
    def __gt__(self, other: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'ComparisonExpression':
        return ComparisonExpression('>', self, self._wrap_operand(other))
    
    def __ge__(self, other: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'ComparisonExpression':
        return ComparisonExpression('>=', self, self._wrap_operand(other))
    
    @staticmethod
    def _wrap_operand(operand: Union['Expression', 'TypeSafeVariable', 'FastQuantity', int, float]) -> 'Expression':
        """Wrap non-Expression operands in appropriate Expression subclasses."""
        return wrap_operand(operand)


class VariableReference(Expression):
    """Reference to a variable in an expression with performance optimizations."""
    
    def __init__(self, variable: 'TypeSafeVariable'):
        self.variable = variable
        # Cache the name resolution to avoid repeated lookups
        self._cached_name = None
        self._last_symbol = None
    
    @property
    def name(self) -> str:
        """Get variable name with caching for performance."""
        current_symbol = self.variable.symbol
        if self._cached_name is None or self._last_symbol != current_symbol:
            # Use symbol for optinova compatibility, fall back to name if symbol not set
            self._cached_name = current_symbol if current_symbol else self.variable.name
            self._last_symbol = current_symbol
        return self._cached_name

    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'FastQuantity':
        try:
            if self.name in variable_values:
                var = variable_values[self.name]
                if var.quantity is not None:
                    return var.quantity
            elif self.variable.quantity is not None:
                return self.variable.quantity
            
            # If we reach here, no valid quantity was found
            available_vars = list(variable_values.keys()) if variable_values else []
            raise ValueError(
                f"Cannot evaluate variable '{self.name}' without value. "
                f"Available variables: {available_vars}"
            )
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error evaluating variable '{self.name}': {e}") from e
    
    def get_variables(self) -> set[str]:
        return {self.name}
    
    def simplify(self) -> 'Expression':
        return self
    
    def __str__(self) -> str:
        return self.name


class Constant(Expression):
    """Constant value in an expression."""
    
    def __init__(self, value: 'FastQuantity'):
        self.value = value
    
    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'FastQuantity':
        return self.value
    
    def get_variables(self) -> set[str]:
        return set()
    
    def simplify(self) -> 'Expression':
        return self
    
    def __str__(self) -> str:
        return str(self.value.value)


class BinaryOperation(Expression):
    """Binary operation between two expressions."""
    
    def __init__(self, operator: str, left: Expression, right: Expression):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'FastQuantity':
        try:
            left_val = self.left.evaluate(variable_values)
            right_val = self.right.evaluate(variable_values)
            
            if self.operator == '+':
                return left_val + right_val
            elif self.operator == '-':
                return left_val - right_val
            elif self.operator == '*':
                return left_val * right_val
            elif self.operator == '/':
                # Check for division by zero
                if abs(right_val.value) < 1e-15:
                    raise ValueError(f"Division by zero in expression: {self}")
                return left_val / right_val
            elif self.operator == '**':
                # For power, right side should be dimensionless
                if isinstance(right_val.value, int | float):
                    if right_val.value < 0 and left_val.value < 0:
                        raise ValueError(f"Negative base with negative exponent: {left_val.value}^{right_val.value}")
                    result_value = left_val.value ** right_val.value
                    # For power operations, we need to handle units carefully
                    # This is a simplified implementation
                    return FastQuantity(result_value, left_val.unit)
                else:
                    raise ValueError("Exponent must be dimensionless number")
            else:
                raise ValueError(f"Unknown operator: {self.operator}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error evaluating binary operation '{self}': {e}") from e
    
    def get_variables(self) -> set[str]:
        return self.left.get_variables() | self.right.get_variables()
    
    def simplify(self) -> Expression:
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()
        
        # Basic simplification rules
        if isinstance(left_simplified, Constant) and isinstance(right_simplified, Constant):
            # Evaluate constant expressions
            dummy_vars = {}
            try:
                result = BinaryOperation(self.operator, left_simplified, right_simplified).evaluate(dummy_vars)
                return Constant(result)
            except (ValueError, TypeError, ArithmeticError):
                pass
        
        return BinaryOperation(self.operator, left_simplified, right_simplified)
    
    def __str__(self) -> str:
        # Handle operator precedence for cleaner string representation
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '**': 3}
        left_str = str(self.left)
        right_str = str(self.right)
        
        # Add parentheses only when needed based on precedence
        if isinstance(self.left, BinaryOperation) and precedence.get(self.left.operator, 0) < precedence.get(self.operator, 0):
            left_str = f"({left_str})"
        if isinstance(self.right, BinaryOperation) and precedence.get(self.right.operator, 0) < precedence.get(self.operator, 0):
            right_str = f"({right_str})"
            
        return f"{left_str} {self.operator} {right_str}"


class ComparisonExpression(Expression):
    """Comparison expression for conditional logic."""
    
    def __init__(self, operator: str, left: Expression, right: Expression):
        self.operator = operator
        self.left = left
        self.right = right
    
    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'FastQuantity':
        """Evaluate comparison and return dimensionless result (1.0 for True, 0.0 for False)."""
        
        left_val = self.left.evaluate(variable_values)
        right_val = self.right.evaluate(variable_values)
        
        # Convert to same units for comparison if possible
        try:
            if left_val._dimension_sig == right_val._dimension_sig and left_val.unit != right_val.unit:
                right_val = right_val.to(left_val.unit)
        except (ValueError, TypeError, AttributeError):
            pass
        
        if self.operator == '<':
            result = left_val.value < right_val.value
        elif self.operator == '<=':
            result = left_val.value <= right_val.value
        elif self.operator == '>':
            result = left_val.value > right_val.value
        elif self.operator == '>=':
            result = left_val.value >= right_val.value
        elif self.operator == '==':
            result = abs(left_val.value - right_val.value) < 1e-10
        elif self.operator == '!=':
            result = abs(left_val.value - right_val.value) >= 1e-10
        else:
            raise ValueError(f"Unknown comparison operator: {self.operator}")
        
        return FastQuantity(1.0 if result else 0.0, DimensionlessUnits.dimensionless)
    
    def get_variables(self) -> set[str]:
        return self.left.get_variables() | self.right.get_variables()
    
    def simplify(self) -> Expression:
        return ComparisonExpression(self.operator, self.left.simplify(), self.right.simplify())
    
    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


class UnaryFunction(Expression):
    """Unary mathematical function expression."""
    
    def __init__(self, function_name: str, operand: Expression):
        self.function_name = function_name
        self.operand = operand
    
    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'FastQuantity':
        
        operand_val = self.operand.evaluate(variable_values)
        
        if self.function_name == 'sin':
            # Assume input is in radians, result is dimensionless
            result_value = math.sin(operand_val.value)
            return FastQuantity(result_value, DimensionlessUnits.dimensionless)
        elif self.function_name == 'cos':
            result_value = math.cos(operand_val.value)
            return FastQuantity(result_value, DimensionlessUnits.dimensionless)
        elif self.function_name == 'tan':
            result_value = math.tan(operand_val.value)
            return FastQuantity(result_value, DimensionlessUnits.dimensionless)
        elif self.function_name == 'sqrt':
            # For sqrt, we need to handle units carefully
            result_value = math.sqrt(operand_val.value)
            # This is simplified - proper unit handling would need dimensional analysis
            return FastQuantity(result_value, operand_val.unit)
        elif self.function_name == 'abs':
            return FastQuantity(abs(operand_val.value), operand_val.unit)
        elif self.function_name == 'ln':
            # Natural log - input should be dimensionless
            result_value = math.log(operand_val.value)
            return FastQuantity(result_value, DimensionlessUnits.dimensionless)
        elif self.function_name == 'log10':
            result_value = math.log10(operand_val.value)
            return FastQuantity(result_value, DimensionlessUnits.dimensionless)
        elif self.function_name == 'exp':
            # Exponential - input should be dimensionless
            result_value = math.exp(operand_val.value)
            return FastQuantity(result_value, DimensionlessUnits.dimensionless)
        else:
            raise ValueError(f"Unknown function: {self.function_name}")
    
    def get_variables(self) -> set[str]:
        return self.operand.get_variables()
    
    def simplify(self) -> Expression:
        simplified_operand = self.operand.simplify()
        if isinstance(simplified_operand, Constant):
            # Evaluate constant functions at compile time
            try:
                dummy_vars = {}
                result = UnaryFunction(self.function_name, simplified_operand).evaluate(dummy_vars)
                return Constant(result)
            except (ValueError, TypeError, ArithmeticError):
                pass
        return UnaryFunction(self.function_name, simplified_operand)
    
    def __str__(self) -> str:
        return f"{self.function_name}({self.operand})"


class ConditionalExpression(Expression):
    """Conditional expression: if condition then true_expr else false_expr."""
    
    def __init__(self, condition: Expression, true_expr: Expression, false_expr: Expression):
        self.condition = condition
        self.true_expr = true_expr
        self.false_expr = false_expr
    
    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'FastQuantity':
        condition_val = self.condition.evaluate(variable_values)
        # Consider non-zero as True
        if abs(condition_val.value) > 1e-10:
            return self.true_expr.evaluate(variable_values)
        else:
            return self.false_expr.evaluate(variable_values)
    
    def get_variables(self) -> set[str]:
        return (self.condition.get_variables() |
                self.true_expr.get_variables() |
                self.false_expr.get_variables())
    
    def simplify(self) -> Expression:
        simplified_condition = self.condition.simplify()
        simplified_true = self.true_expr.simplify()
        simplified_false = self.false_expr.simplify()
        
        # If condition is constant, choose the appropriate branch
        if isinstance(simplified_condition, Constant):
            try:
                dummy_vars = {}
                condition_val = simplified_condition.evaluate(dummy_vars)
                if abs(condition_val.value) > 1e-10:
                    return simplified_true
                else:
                    return simplified_false
            except (ValueError, TypeError, ArithmeticError):
                pass
        
        return ConditionalExpression(simplified_condition, simplified_true, simplified_false)
    
    def __str__(self) -> str:
        return f"if({self.condition}, {self.true_expr}, {self.false_expr})"


# Convenience functions for mathematical operations
def sin(expr: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> UnaryFunction:
    """Sine function."""
    return UnaryFunction('sin', Expression._wrap_operand(expr))

def cos(expr: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> UnaryFunction:
    """Cosine function."""
    return UnaryFunction('cos', Expression._wrap_operand(expr))

def tan(expr: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> UnaryFunction:
    """Tangent function."""
    return UnaryFunction('tan', Expression._wrap_operand(expr))

def sqrt(expr: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> UnaryFunction:
    """Square root function."""
    return UnaryFunction('sqrt', Expression._wrap_operand(expr))

def abs_expr(expr: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> UnaryFunction:
    """Absolute value function."""
    return UnaryFunction('abs', Expression._wrap_operand(expr))

def ln(expr: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> UnaryFunction:
    """Natural logarithm function."""
    return UnaryFunction('ln', Expression._wrap_operand(expr))

def log10(expr: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> UnaryFunction:
    """Base-10 logarithm function."""
    return UnaryFunction('log10', Expression._wrap_operand(expr))

def exp(expr: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> UnaryFunction:
    """Exponential function."""
    return UnaryFunction('exp', Expression._wrap_operand(expr))

def cond_expr(condition: Union[Expression, 'ComparisonExpression'],
              true_expr: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float],
              false_expr: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> ConditionalExpression:
    """Conditional expression: if condition then true_expr else false_expr."""
    return ConditionalExpression(
        condition if isinstance(condition, Expression) else condition,
        Expression._wrap_operand(true_expr),
        Expression._wrap_operand(false_expr)
    )

def min_expr(*expressions: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> Expression:
    """Minimum of multiple expressions."""
    if len(expressions) < 2:
        raise ValueError("min_expr requires at least 2 arguments")
    
    wrapped_expressions = [Expression._wrap_operand(expr) for expr in expressions]
    result = wrapped_expressions[0]
    
    for expr in wrapped_expressions[1:]:
        # min(a, b) = if(a < b, a, b)
        result = cond_expr(result < expr, result, expr)
    
    return result

def max_expr(*expressions: Union[Expression, 'TypeSafeVariable', 'FastQuantity', int, float]) -> Expression:
    """Maximum of multiple expressions."""
    if len(expressions) < 2:
        raise ValueError("max_expr requires at least 2 arguments")
    
    wrapped_expressions = [Expression._wrap_operand(expr) for expr in expressions]
    result = wrapped_expressions[0]
    
    for expr in wrapped_expressions[1:]:
        # max(a, b) = if(a > b, a, b)
        result = cond_expr(result > expr, result, expr)
    
    return result
