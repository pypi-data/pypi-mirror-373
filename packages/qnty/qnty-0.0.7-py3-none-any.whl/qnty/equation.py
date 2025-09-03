"""
Equation System
===============

Mathematical equations for qnty variables with solving capabilities.
"""

from __future__ import annotations

from typing import cast

from .expression import Expression, VariableReference
from .variable import TypeSafeVariable


class Equation:
    """Represents a mathematical equation with left-hand side equal to right-hand side."""
    
    def __init__(self, name: str, lhs: TypeSafeVariable | Expression, rhs: Expression):
        self.name = name
        
        # Convert Variable to VariableReference if needed
        # Use duck typing to avoid circular import
        if hasattr(lhs, 'name') and hasattr(lhs, 'quantity') and hasattr(lhs, 'is_known'):
            # It's a TypeSafeVariable-like object
            self.lhs = VariableReference(cast('TypeSafeVariable', lhs))
        else:
            # It's already an Expression
            self.lhs = cast(Expression, lhs)
            
        self.rhs = rhs
        self.variables = self.get_all_variables()
    
    def get_all_variables(self) -> set[str]:
        """Get all variable names used in this equation."""
        # Both lhs and rhs should be Expressions after __init__ conversion
        lhs_vars = self.lhs.get_variables()
        rhs_vars = self.rhs.get_variables()
        return lhs_vars | rhs_vars
    
    def get_unknown_variables(self, known_vars: set[str]) -> set[str]:
        """Get variables that are unknown (not in known_vars set)."""
        return self.variables - known_vars
    
    def get_known_variables(self, known_vars: set[str]) -> set[str]:
        """Get variables that are known (in known_vars set)."""
        return self.variables & known_vars
    
    def can_solve_for(self, target_var: str, known_vars: set[str]) -> bool:
        """Check if this equation can solve for target_var given known_vars."""
        if target_var not in self.variables:
            return False
        # Direct assignment case: lhs is the variable
        if isinstance(self.lhs, VariableReference) and self.lhs.name == target_var:
            rhs_vars = self.rhs.get_variables()
            return rhs_vars.issubset(known_vars)
        unknown_vars = self.get_unknown_variables(known_vars)
        # Can solve if target_var is the only unknown
        return unknown_vars == {target_var}
    
    def solve_for(self, target_var: str, variable_values: dict[str, TypeSafeVariable]) -> TypeSafeVariable:
        """
        Solve the equation for target_var.
        Returns the target variable with updated quantity.
        """
        if target_var not in self.variables:
            raise ValueError(f"Variable '{target_var}' not found in equation")
        
        # Handle direct assignment: target = expression
        if isinstance(self.lhs, VariableReference) and self.lhs.name == target_var:
            # Direct assignment: target_var = rhs
            result_qty = self.rhs.evaluate(variable_values)
            
            # Update existing variable object to preserve references
            var_obj = variable_values.get(target_var)
            if var_obj is not None:
                # Convert result to the target variable's original unit if it had one
                if var_obj.quantity is not None and var_obj.quantity.unit is not None:
                    # Convert to the target variable's defined unit
                    try:
                        result_qty = result_qty.to(var_obj.quantity.unit)
                    except Exception:
                        # If conversion fails, keep the calculated unit
                        pass
                
                var_obj.quantity = result_qty
                var_obj.is_known = True
                return var_obj
            
            # Create new variable if not found - this shouldn't happen in normal usage
            raise ValueError(f"Variable '{target_var}' not found in variable_values")
        
        # For more complex equations, we would need algebraic manipulation
        # Currently focusing on direct assignment which covers most engineering cases
        raise NotImplementedError(f"Cannot solve for {target_var} in equation {self}. "
                                f"Only direct assignment equations (var = expression) are supported.")
    
    def check_residual(self, variable_values: dict[str, TypeSafeVariable], tolerance: float = 1e-10) -> bool:
        """
        Check if equation is satisfied by evaluating residual (LHS - RHS).
        Returns True if |residual| < tolerance, accounting for units.
        """
        try:
            # Both lhs and rhs should be Expressions after __init__ conversion
            lhs_value = self.lhs.evaluate(variable_values)
            rhs_value = self.rhs.evaluate(variable_values)
            
            # Check dimensional compatibility
            if lhs_value._dimension_sig != rhs_value._dimension_sig:
                return False
            
            # Convert to same units for comparison
            rhs_converted = rhs_value.to(lhs_value.unit)
            residual = abs(lhs_value.value - rhs_converted.value)
            
            return residual < tolerance
        except Exception:
            return False
    
    def __str__(self) -> str:
        return f"{self.lhs} = {self.rhs}"
    
    def __repr__(self) -> str:
        return f"Equation(name='{self.name}', lhs={self.lhs!r}, rhs={self.rhs!r})"


class EquationSystem:
    """System of equations that can be solved together."""
    
    def __init__(self, equations: list[Equation] | None = None):
        self.equations = equations or []
        self.variables = {}  # Dict[str, TypeSafeVariable]
    
    def add_equation(self, equation: Equation):
        """Add an equation to the system."""
        self.equations.append(equation)
    
    def add_variable(self, variable: TypeSafeVariable):
        """Add a variable to the system."""
        self.variables[variable.name] = variable
    
    def get_known_variables(self) -> set[str]:
        """Get names of all known variables."""
        return {name for name, var in self.variables.items() if var.is_known and var.quantity is not None}
    
    def get_unknown_variables(self) -> set[str]:
        """Get names of all unknown variables."""
        return {name for name, var in self.variables.items() if not var.is_known or var.quantity is None}
    
    def can_solve_any(self) -> bool:
        """Check if any equation can be solved with current known variables."""
        known_vars = self.get_known_variables()
        unknown_vars = self.get_unknown_variables()
        
        for equation in self.equations:
            for unknown_var in unknown_vars:
                if equation.can_solve_for(unknown_var, known_vars):
                    return True
        return False
    
    def solve_step(self) -> bool:
        """Solve one step - find and solve one equation. Returns True if progress made."""
        known_vars = self.get_known_variables()
        unknown_vars = self.get_unknown_variables()
        
        # Find an equation that can be solved
        for equation in self.equations:
            for unknown_var in unknown_vars:
                if equation.can_solve_for(unknown_var, known_vars):
                    # Solve for this variable
                    equation.solve_for(unknown_var, self.variables)
                    return True  # Progress made
        
        return False  # No progress possible
    
    def solve(self, max_iterations: int = 100) -> bool:
        """Solve the system iteratively. Returns True if fully solved."""
        for _ in range(max_iterations):
            if not self.can_solve_any():
                break
            if not self.solve_step():
                break
        
        # Check if all variables are known
        unknown_vars = self.get_unknown_variables()
        return len(unknown_vars) == 0
    
    def get_solving_order(self) -> list[str]:
        """Get the order in which variables can be solved."""
        order = []
        temp_system = EquationSystem(self.equations.copy())
        temp_system.variables = self.variables.copy()
        
        while temp_system.can_solve_any():
            known_vars = temp_system.get_known_variables()
            unknown_vars = temp_system.get_unknown_variables()
            
            # Find next solvable variable
            for equation in temp_system.equations:
                for unknown_var in unknown_vars:
                    if equation.can_solve_for(unknown_var, known_vars):
                        order.append(unknown_var)
                        # Mark as known for next iteration
                        temp_system.variables[unknown_var].is_known = True
                        break
                else:
                    continue
                break
        
        return order
    
    def __str__(self) -> str:
        return f"EquationSystem({len(self.equations)} equations, {len(self.variables)} variables)"
    
    def __repr__(self) -> str:
        return f"EquationSystem(equations={self.equations!r})"
