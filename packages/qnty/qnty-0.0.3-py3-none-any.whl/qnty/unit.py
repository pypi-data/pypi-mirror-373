"""
Unit System
===========

Unit definitions, constants and registry for the high-performance unit system.
"""

from dataclasses import dataclass

from .dimension import DIMENSIONLESS, LENGTH, PRESSURE, DimensionSignature
from .prefixes import SIPrefix, StandardPrefixes


@dataclass(frozen=True)
class UnitDefinition:
    """Immutable unit definition optimized for performance."""
    name: str
    symbol: str
    dimension: DimensionSignature
    si_factor: float
    si_offset: float = 0.0
    base_unit_name: str | None = None  # Base unit without prefix
    prefix: SIPrefix | None = None      # SI prefix if applicable
    
    @classmethod
    def with_prefix(cls, base_def: 'UnitDefinition', prefix: SIPrefix) -> 'UnitDefinition':
        """Create a new unit definition with an SI prefix."""
        return cls(
            name=prefix.apply_to_name(base_def.name),
            symbol=prefix.apply_to_symbol(base_def.symbol),
            dimension=base_def.dimension,
            si_factor=base_def.si_factor * prefix.factor,
            si_offset=base_def.si_offset,
            base_unit_name=base_def.name,
            prefix=prefix
        )


class UnitConstant:
    """Unit constant that provides type safety and performance."""
    
    def __init__(self, definition: UnitDefinition):
        self.definition = definition
        self.name = definition.name
        self.symbol = definition.symbol
        self.dimension = definition.dimension
        self.si_factor = definition.si_factor
    
    def __str__(self):
        return self.symbol
    
    def __eq__(self, other):
        """Fast equality check for unit constants."""
        return isinstance(other, UnitConstant) and self.name == other.name
    
    def __hash__(self):
        """Enable unit constants as dictionary keys."""
        return hash(self.name)


class HighPerformanceRegistry:
    """Ultra-fast registry with pre-computed conversion tables."""
    
    def __init__(self):
        self.units: dict[str, UnitDefinition] = {}
        self.conversion_table: dict[tuple[str, str], float] = {}  # (from_unit, to_unit) -> factor
        self.dimensional_groups: dict[int, list[UnitDefinition]] = {}
        self._dimension_cache: dict[int, UnitConstant] = {}  # Cache for common dimension mappings
        self._finalized = False
        self.base_units: dict[str, UnitDefinition] = {}  # Track base units for prefix generation
        self.prefixable_units: set[str] = set()  # Track which units can have prefixes

        # Keep legacy initialization for backward compatibility
        self._initialize_units()
        self._precompute_conversions()
    
    def _initialize_units(self):
        """Initialize with engineering units."""
        
        # Length units
        meter = UnitDefinition("meter", "m", LENGTH, 1.0)
        millimeter = UnitDefinition("millimeter", "mm", LENGTH, 0.001)
        centimeter = UnitDefinition("centimeter", "cm", LENGTH, 0.01)
        inch = UnitDefinition("inch", "in", LENGTH, 0.0254)
        foot = UnitDefinition("foot", "ft", LENGTH, 0.3048)
        
        # Pressure units
        pascal = UnitDefinition("pascal", "Pa", PRESSURE, 1.0)
        kilopascal = UnitDefinition("kilopascal", "kPa", PRESSURE, 1000.0)
        megapascal = UnitDefinition("megapascal", "MPa", PRESSURE, 1e6)
        psi = UnitDefinition("psi", "psi", PRESSURE, 6894.757)
        bar = UnitDefinition("bar", "bar", PRESSURE, 100000.0)
        
        # Dimensionless units
        dimensionless = UnitDefinition("dimensionless", "", DIMENSIONLESS, 1.0)
        
        # Register all units
        for unit_def in [meter, millimeter, centimeter, inch, foot,
                        pascal, kilopascal, megapascal, psi, bar, dimensionless]:
            self.units[unit_def.name] = unit_def
            
            # Group by dimension
            dim_sig = unit_def.dimension._signature
            if dim_sig not in self.dimensional_groups:
                self.dimensional_groups[dim_sig] = []
            self.dimensional_groups[dim_sig].append(unit_def)
    
    def register_unit(self, unit_def: UnitDefinition):
        """Register a single unit definition."""
        if self._finalized:
            raise RuntimeError("Cannot register units after registry is finalized")
            
        self.units[unit_def.name] = unit_def
        
        # Group by dimension
        dim_sig = unit_def.dimension._signature
        if dim_sig not in self.dimensional_groups:
            self.dimensional_groups[dim_sig] = []
        self.dimensional_groups[dim_sig].append(unit_def)
    
    def register_with_prefixes(
            self,
            unit_def: UnitDefinition,
            prefixes: list[StandardPrefixes] | None = None
        ):
        """
        Register a unit and automatically generate prefixed variants.
        
        Args:
            unit_def: The base unit definition
            prefixes: List of StandardPrefixes enum values to apply. If None, uses common prefixes.
        """
        if self._finalized:
            raise RuntimeError("Cannot register units after registry is finalized")
        
        # Register base unit
        self.register_unit(unit_def)
        self.base_units[unit_def.name] = unit_def
        self.prefixable_units.add(unit_def.name)
        
        # Generate and register prefixed variants
        if prefixes:
            for prefix_enum in prefixes:
                prefix = prefix_enum.value
                if prefix.name:  # Skip NONE prefix (empty name)
                    prefixed_unit = UnitDefinition.with_prefix(unit_def, prefix)
                    self.register_unit(prefixed_unit)
    
    def finalize_registration(self):
        """Called after all units registered to precompute conversions."""
        if not self._finalized:
            self._precompute_conversions()
            self._finalized = True

    def _precompute_conversions(self):
        """Pre-compute all unit conversions for maximum speed."""
        self.conversion_table.clear()  # Clear existing conversions
        for group in self.dimensional_groups.values():
            for from_unit in group:
                for to_unit in group:
                    if from_unit != to_unit:
                        factor = from_unit.si_factor / to_unit.si_factor
                        key = (from_unit.name, to_unit.name)
                        self.conversion_table[key] = factor
    
    def convert(self, value: float, from_unit: UnitConstant, to_unit: UnitConstant) -> float:
        """Ultra-fast conversion using pre-computed table."""
        if from_unit == to_unit:
            return value
        
        # O(1) lookup for pre-computed conversions
        key = (from_unit.name, to_unit.name)
        if key in self.conversion_table:
            return value * self.conversion_table[key]
        
        # Fallback (shouldn't happen for registered units)
        return value * from_unit.si_factor / to_unit.si_factor


# Global high-performance registry
registry = HighPerformanceRegistry()
