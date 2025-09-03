"""
SI Prefix System
================

Standard SI prefixes for unit multiplication/division.
Provides systematic handling of metric prefixes like kilo-, milli-, micro-, etc.
"""

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class SIPrefix:
    """
    Standard SI prefix definition.
    
    Attributes:
        name: Full prefix name (e.g., "kilo", "milli")
        symbol: Standard symbol (e.g., "k", "m")
        factor: Multiplication factor relative to base unit (e.g., 1000, 0.001)
    """
    name: str
    symbol: str
    factor: float
    
    def apply_to_name(self, base_name: str) -> str:
        """Apply prefix to a base unit name."""
        if not self.name:
            return base_name
        return f"{self.name}{base_name}"
    
    def apply_to_symbol(self, base_symbol: str) -> str:
        """Apply prefix to a base unit symbol."""
        if not self.symbol:
            return base_symbol
        return f"{self.symbol}{base_symbol}"


class StandardPrefixes(Enum):
    """
    Standard SI prefixes with their multiplication factors.
    
    From yotta (10^24) to yocto (10^-24).
    """
    # Larger prefixes (10^3 to 10^24)
    YOTTA = SIPrefix("yotta", "Y", 1e24)
    ZETTA = SIPrefix("zetta", "Z", 1e21)
    EXA = SIPrefix("exa", "E", 1e18)
    PETA = SIPrefix("peta", "P", 1e15)
    TERA = SIPrefix("tera", "T", 1e12)
    GIGA = SIPrefix("giga", "G", 1e9)
    MEGA = SIPrefix("mega", "M", 1e6)
    KILO = SIPrefix("kilo", "k", 1e3)
    HECTO = SIPrefix("hecto", "h", 1e2)
    DECA = SIPrefix("deca", "da", 1e1)
    
    # Base (no prefix)
    NONE = SIPrefix("", "", 1.0)
    
    # Smaller prefixes (10^-1 to 10^-24)
    DECI = SIPrefix("deci", "d", 1e-1)
    CENTI = SIPrefix("centi", "c", 1e-2)
    MILLI = SIPrefix("milli", "m", 1e-3)
    MICRO = SIPrefix("micro", "μ", 1e-6)
    NANO = SIPrefix("nano", "n", 1e-9)
    PICO = SIPrefix("pico", "p", 1e-12)
    FEMTO = SIPrefix("femto", "f", 1e-15)
    ATTO = SIPrefix("atto", "a", 1e-18)
    ZEPTO = SIPrefix("zepto", "z", 1e-21)
    YOCTO = SIPrefix("yocto", "y", 1e-24)


# Common prefix groups for different unit types
COMMON_LENGTH_PREFIXES = [
    StandardPrefixes.KILO,
    StandardPrefixes.CENTI,
    StandardPrefixes.MILLI,
    StandardPrefixes.MICRO,
    StandardPrefixes.NANO,
]

COMMON_MASS_PREFIXES = [
    StandardPrefixes.KILO,  # Note: kilogram is the SI base unit
    StandardPrefixes.MILLI,
    StandardPrefixes.MICRO,
]

COMMON_TIME_PREFIXES = [
    StandardPrefixes.MILLI,
    StandardPrefixes.MICRO,
    StandardPrefixes.NANO,
    StandardPrefixes.PICO,
]

COMMON_ELECTRIC_PREFIXES = [
    StandardPrefixes.KILO,
    StandardPrefixes.MILLI,
    StandardPrefixes.MICRO,
    StandardPrefixes.NANO,
    StandardPrefixes.PICO,
]

COMMON_ENERGY_PREFIXES = [
    StandardPrefixes.KILO,
    StandardPrefixes.MEGA,
    StandardPrefixes.GIGA,
]

COMMON_POWER_PREFIXES = [
    StandardPrefixes.KILO,
    StandardPrefixes.MEGA,
    StandardPrefixes.GIGA,
    StandardPrefixes.MILLI,
    StandardPrefixes.MICRO,
]

COMMON_PRESSURE_PREFIXES = [
    StandardPrefixes.KILO,
    StandardPrefixes.MEGA,
    StandardPrefixes.GIGA,
]


def get_prefix_by_name(name: str) -> SIPrefix | None:
    """Get a prefix by its name (e.g., 'kilo', 'milli')."""
    for prefix_enum in StandardPrefixes:
        if prefix_enum.value.name == name:
            return prefix_enum.value
    return None


def get_prefix_by_symbol(symbol: str) -> SIPrefix | None:
    """Get a prefix by its symbol (e.g., 'k', 'm')."""
    for prefix_enum in StandardPrefixes:
        if prefix_enum.value.symbol == symbol:
            return prefix_enum.value
    return None


def get_prefix_by_factor(factor: float, tolerance: float = 1e-10) -> SIPrefix | None:
    """Get a prefix by its multiplication factor."""
    for prefix_enum in StandardPrefixes:
        if abs(prefix_enum.value.factor - factor) < tolerance:
            return prefix_enum.value
    return None


# Define which units should get automatic prefixes
PREFIXABLE_UNITS = {
    # Base SI units
    'meter': COMMON_LENGTH_PREFIXES,
    'gram': COMMON_MASS_PREFIXES,
    'second': COMMON_TIME_PREFIXES,
    'ampere': COMMON_ELECTRIC_PREFIXES,
    'kelvin': [],  # Temperature usually doesn't use prefixes
    'mole': [
        StandardPrefixes.MILLI,
        StandardPrefixes.MICRO
    ],
    'candela': [],  # Luminous intensity rarely uses prefixes
    
    # Derived SI units
    'pascal': COMMON_PRESSURE_PREFIXES,
    'joule': COMMON_ENERGY_PREFIXES,
    'watt': COMMON_POWER_PREFIXES,
    'coulomb': COMMON_ELECTRIC_PREFIXES,
    'volt': COMMON_ELECTRIC_PREFIXES,
    'farad': [
        StandardPrefixes.MILLI,
        StandardPrefixes.MICRO,
        StandardPrefixes.NANO,
        StandardPrefixes.PICO
    ],
    'ohm': [
        StandardPrefixes.KILO,
        StandardPrefixes.MEGA,
        StandardPrefixes.MILLI
    ],
    'siemens': [
        StandardPrefixes.MILLI,
        StandardPrefixes.MICRO
    ],
    'weber': [
        StandardPrefixes.MILLI,
        StandardPrefixes.MICRO
    ],
    'tesla': [
        StandardPrefixes.MILLI,
        StandardPrefixes.MICRO,
        StandardPrefixes.NANO
    ],
    'henry': [
        StandardPrefixes.MILLI,
        StandardPrefixes.MICRO,
        StandardPrefixes.NANO
    ],
    'lumen': [],
    'lux': [],
    'becquerel': [
        StandardPrefixes.KILO,
        StandardPrefixes.MEGA,
        StandardPrefixes.GIGA
    ],
    'gray': [
        StandardPrefixes.MILLI,
        StandardPrefixes.MICRO
    ],
    'sievert': [
        StandardPrefixes.MILLI,
        StandardPrefixes.MICRO
    ],
    'hertz': [
        StandardPrefixes.KILO,
        StandardPrefixes.MEGA,
        StandardPrefixes.GIGA
    ],
    'newton': [
        StandardPrefixes.KILO,
        StandardPrefixes.MILLI
    ],
    'bar': [
        StandardPrefixes.MILLI
    ],  # Common non-SI unit
    'liter': [
        StandardPrefixes.MILLI,
        StandardPrefixes.MICRO
    ],  # Common non-SI unit
}
