"""
Dimension System
================

Compile-time dimensional analysis using type system for ultra-fast operations.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import final


class BaseDimension(IntEnum):
    """Base dimensions as prime numbers for efficient bit operations."""
    LENGTH = 2
    MASS = 3
    TIME = 5
    CURRENT = 7
    TEMPERATURE = 11
    AMOUNT = 13
    LUMINOSITY = 17


@final
@dataclass(frozen=True)
class DimensionSignature:
    """Immutable dimension signature for zero-cost dimensional analysis."""
    
    # Store as bit pattern for ultra-fast comparison
    _signature: int = 1
    
    @classmethod
    def create(cls, length=0, mass=0, time=0, current=0, temp=0, amount=0, luminosity=0):
        """Create dimension from exponents."""
        signature = 1
        if length != 0:
            signature *= BaseDimension.LENGTH ** length
        if mass != 0:
            signature *= BaseDimension.MASS ** mass
        if time != 0:
            signature *= BaseDimension.TIME ** time
        if current != 0:
            signature *= BaseDimension.CURRENT ** current
        if temp != 0:
            signature *= BaseDimension.TEMPERATURE ** temp
        if amount != 0:
            signature *= BaseDimension.AMOUNT ** amount
        if luminosity != 0:
            signature *= BaseDimension.LUMINOSITY ** luminosity
        
        return cls(signature)
    
    def __mul__(self, other):
        return DimensionSignature(self._signature * other._signature)
    
    def __truediv__(self, other):
        return DimensionSignature(self._signature // other._signature)
    
    def __pow__(self, power):
        return DimensionSignature(self._signature ** power)
    
    def is_compatible(self, other):
        """Ultra-fast dimensional compatibility check."""
        return self._signature == other._signature
    
    def __eq__(self, other):
        """Fast equality check for dimensions."""
        return isinstance(other, DimensionSignature) and self._signature == other._signature
    
    def __hash__(self):
        """Enable dimensions as dictionary keys."""
        return hash(self._signature)


# Pre-defined dimension constants (alphabetically ordered)
ABSORBED_DOSE = DimensionSignature.create(length=2, time=-2)  # L^2 T^-2
ACCELERATION = DimensionSignature.create(length=1, time=-2)  # L T^-2
ACTIVATION_ENERGY = DimensionSignature.create(amount=-1, length=2, time=-2)  # N^-1 L^2 T^-2
AMOUNT = DimensionSignature.create(amount=1)  # N
AMOUNT_OF_SUBSTANCE = DimensionSignature.create(amount=1)  # N
ANGLE_PLANE = DimensionSignature.create()  # Dimensionless
ANGLE_SOLID = DimensionSignature.create()  # Dimensionless
ANGULAR_ACCELERATION = DimensionSignature.create(time=-2)  # T^-2
ANGULAR_MOMENTUM = DimensionSignature.create(length=2, mass=1, time=-1)  # L^2 M T^-1
AREA = DimensionSignature.create(length=2)  # L^2
AREA_PER_UNIT_VOLUME = DimensionSignature.create(length=-1)  # L^-1
ATOMIC_WEIGHT = DimensionSignature.create(amount=-1, mass=1)  # N^-1 M
CONCENTRATION = DimensionSignature.create(length=-3, mass=1)  # L^-3 M
CURRENT = DimensionSignature.create(current=1)  # A
DIMENSIONLESS = DimensionSignature.create()  # Dimensionless
DYNAMIC_FLUIDITY = DimensionSignature.create(length=1, mass=-1, time=1)  # L M^-1 T
ELECTRICAL_CONDUCTANCE = DimensionSignature.create(current=2, length=-2, mass=-1, time=3)  # A^2 L^-2 M^-1 T^3
ELECTRICAL_PERMITTIVITY = DimensionSignature.create(current=2, length=-3, mass=-1, time=4)  # A^2 L^-3 M^-1 T^4
ELECTRICAL_RESISTIVITY = DimensionSignature.create(current=-2, length=3, mass=1, time=-3)  # A^-2 L^3 M T^-3
ELECTRIC_CAPACITANCE = DimensionSignature.create(current=2, length=-2, mass=-1, time=4)  # A^2 L^-2 M^-1 T^4
ELECTRIC_CHARGE = DimensionSignature.create(amount=-1, current=1, time=1)  # N^-1 A T
ELECTRIC_CURRENT_INTENSITY = DimensionSignature.create(current=1)  # A
ELECTRIC_DIPOLE_MOMENT = DimensionSignature.create(current=1, length=1, time=1)  # A L T
ELECTRIC_FIELD_STRENGTH = DimensionSignature.create(current=-1, length=1, mass=1, time=-3)  # A^-1 L M T^-3
ELECTRIC_INDUCTANCE = DimensionSignature.create(current=-2, length=2, mass=1, time=-2)  # A^-2 L^2 M T^-2
ELECTRIC_POTENTIAL = DimensionSignature.create(current=-1, length=2, mass=1, time=-3)  # A^-1 L^2 M T^-3
ELECTRIC_RESISTANCE = DimensionSignature.create(current=-2, length=2, mass=1, time=-3)  # A^-2 L^2 M T^-3
ENERGY_FLUX = DimensionSignature.create(mass=1, time=-3)  # M T^-3
ENERGY_HEAT_WORK = DimensionSignature.create(length=2, mass=1, time=-2)  # L^2 M T^-2
ENERGY_PER_UNIT_AREA = DimensionSignature.create(mass=1, time=-2)  # M T^-2
FORCE = DimensionSignature.create(length=1, mass=1, time=-2)  # L M T^-2
FORCE_BODY = DimensionSignature.create(length=-2, mass=1, time=-2)  # L^-2 M T^-2
FORCE_PER_UNIT_MASS = DimensionSignature.create(length=1, time=-2)  # L T^-2
FREQUENCY_VOLTAGE_RATIO = DimensionSignature.create(current=1, length=-2, mass=-1, time=3)  # A L^-2 M^-1 T^3
FUEL_CONSUMPTION = DimensionSignature.create(length=-2)  # L^-2
HEAT_OF_COMBUSTION = DimensionSignature.create(length=2, time=-2)  # L^2 T^-2
HEAT_OF_FUSION = DimensionSignature.create(length=2, time=-2)  # L^2 T^-2
HEAT_OF_VAPORIZATION = DimensionSignature.create(length=2, time=-2)  # L^2 T^-2
HEAT_TRANSFER_COEFFICIENT = DimensionSignature.create(mass=1, temp=-1, time=-3)  # M Θ^-1 T^-3
ILLUMINANCE = DimensionSignature.create(length=-2, luminosity=1)  # L^-2 J
KINETIC_ENERGY_OF_TURBULENCE = DimensionSignature.create(length=2, time=-2)  # L^2 T^-2
LENGTH = DimensionSignature.create(length=1)  # L
LINEAR_MASS_DENSITY = DimensionSignature.create(length=-1, mass=1)  # L^-1 M
LINEAR_MOMENTUM = DimensionSignature.create(length=1, mass=1, time=-1)  # L M T^-1
LUMINANCE_SELF = DimensionSignature.create(length=-2, luminosity=1)  # L^-2 J
LUMINOSITY = DimensionSignature.create(luminosity=1)  # J
LUMINOUS_FLUX = DimensionSignature.create(luminosity=1)  # J
LUMINOUS_INTENSITY = DimensionSignature.create(luminosity=1)  # J
MAGNETIC_FIELD = DimensionSignature.create(current=1, length=-1)  # A L^-1
MAGNETIC_FLUX = DimensionSignature.create(current=-1, length=2, mass=1, time=-2)  # A^-1 L^2 M T^-2
MAGNETIC_INDUCTION_FIELD_STRENGTH = DimensionSignature.create(current=-1, mass=1, time=-2)  # A^-1 M T^-2
MAGNETIC_MOMENT = DimensionSignature.create(current=1, length=2)  # A L^2
MAGNETIC_PERMEABILITY = DimensionSignature.create(current=-2, length=2, mass=1, time=-2)  # A^-2 L^2 M T^-2
MAGNETOMOTIVE_FORCE = DimensionSignature.create(current=1)  # A
MASS = DimensionSignature.create(mass=1)  # M
MASS_DENSITY = DimensionSignature.create(length=-3, mass=1)  # L^-3 M
MASS_FLOW_RATE = DimensionSignature.create(mass=1, time=-1)  # M T^-1
MASS_FLUX = DimensionSignature.create(length=-2, mass=1, time=-1)  # L^-2 M T^-1
MASS_FRACTION_OF_I = DimensionSignature.create()  # Dimensionless
MASS_TRANSFER_COEFFICIENT = DimensionSignature.create(length=-2, mass=1, time=-1)  # L^-2 M T^-1
MOLALITY_OF_SOLUTE_I = DimensionSignature.create(amount=1, mass=-1)  # N M^-1
MOLARITY_OF_I = DimensionSignature.create(amount=1, length=-3)  # N L^-3
MOLAR_CONCENTRATION_BY_MASS = DimensionSignature.create(amount=1)  # N
MOLAR_FLOW_RATE = DimensionSignature.create(amount=1, time=-1)  # N T^-1
MOLAR_FLUX = DimensionSignature.create(amount=1, length=-2, time=-1)  # N L^-2 T^-1
MOLAR_HEAT_CAPACITY = DimensionSignature.create(amount=-1, length=2, temp=-1, time=-2)  # N^-1 L^2 Θ^-1 T^-2
MOLE_FRACTION_OF_I = DimensionSignature.create()  # Dimensionless
MOMENTUM_FLOW_RATE = DimensionSignature.create(length=1, mass=1, time=-2)  # L M T^-2
MOMENTUM_FLUX = DimensionSignature.create(length=-1, mass=1, time=-2)  # L^-1 M T^-2
MOMENT_OF_INERTIA = DimensionSignature.create(length=2, mass=1)  # L^2 M
NORMALITY_OF_SOLUTION = DimensionSignature.create(amount=1, length=-3)  # N L^-3
PARTICLE_DENSITY = DimensionSignature.create(length=-3)  # L^-3
PERMEABILITY = DimensionSignature.create(length=2)  # L^2
PHOTON_EMISSION_RATE = DimensionSignature.create(length=-2, time=-1)  # L^-2 T^-1
POWER_PER_UNIT_MASS = DimensionSignature.create(length=2, time=-3)  # L^2 T^-3
POWER_PER_UNIT_VOLUME = DimensionSignature.create(length=-1, mass=1, time=-3)  # L^-1 M T^-3
POWER_THERMAL_DUTY = DimensionSignature.create(length=2, mass=1, time=-3)  # L^2 M T^-3
PRESSURE = DimensionSignature.create(length=-1, mass=1, time=-2)  # L^-1 M T^-2
RADIATION_DOSE_EQUIVALENT = DimensionSignature.create(length=2, time=-2)  # L^2 T^-2
RADIATION_EXPOSURE = DimensionSignature.create(current=1, mass=-1, time=1)  # A M^-1 T
RADIOACTIVITY = DimensionSignature.create(time=-1)  # T^-1
SECOND_MOMENT_OF_AREA = DimensionSignature.create(length=4)  # L^4
SECOND_RADIATION_CONSTANT_PLANCK = DimensionSignature.create(length=1, temp=1)  # L Θ
SPECIFIC_ENTHALPY = DimensionSignature.create(length=2, time=-2)  # L^2 T^-2
SPECIFIC_GRAVITY = DimensionSignature.create()  # Dimensionless
SPECIFIC_HEAT_CAPACITY_CONSTANT_PRESSURE = DimensionSignature.create(length=2, mass=1, temp=-1, time=-2)  # L^2 M Θ^-1 T^-2
SPECIFIC_LENGTH = DimensionSignature.create(length=1, mass=-1)  # L M^-1
SPECIFIC_SURFACE = DimensionSignature.create(length=2, mass=-1)  # L^2 M^-1
SPECIFIC_VOLUME = DimensionSignature.create(length=3, mass=-1)  # L^3 M^-1
STRESS = DimensionSignature.create(length=-1, mass=1, time=-2)  # L^-1 M T^-2
SURFACE_MASS_DENSITY = DimensionSignature.create(length=-2, mass=1)  # L^-2 M
SURFACE_TENSION = DimensionSignature.create(mass=1, time=-2)  # M T^-2
TEMPERATURE = DimensionSignature.create(temp=1)  # Θ
THERMAL_CONDUCTIVITY = DimensionSignature.create(length=1, mass=1, temp=1, time=-3)  # L M Θ T^-3
TIME = DimensionSignature.create(time=1)  # T
TORQUE = DimensionSignature.create(length=2, mass=1, time=-2)  # L^2 M T^-2
TURBULENCE_ENERGY_DISSIPATION_RATE = DimensionSignature.create(length=2, time=-3)  # L^2 T^-3
VELOCITY_ANGULAR = DimensionSignature.create(time=-1)  # T^-1
VELOCITY_LINEAR = DimensionSignature.create(length=1, time=-1)  # L T^-1
VISCOSITY_DYNAMIC = DimensionSignature.create(length=-1, mass=1, time=-1)  # L^-1 M T^-1
VISCOSITY_KINEMATIC = DimensionSignature.create(length=2, time=-1)  # L^2 T^-1
VOLUME = DimensionSignature.create(length=3)  # L^3
VOLUMETRIC_CALORIFIC_HEATING_VALUE = DimensionSignature.create(length=-1, mass=1, time=-2)  # L^-1 M T^-2
VOLUMETRIC_COEFFICIENT_OF_EXPANSION = DimensionSignature.create(length=-3, mass=1, temp=-1)  # L^-3 M Θ^-1
VOLUMETRIC_FLOW_RATE = DimensionSignature.create(length=3, time=-1)  # L^3 T^-1
VOLUMETRIC_FLUX = DimensionSignature.create(length=1, time=-1)  # L T^-1
VOLUMETRIC_MASS_FLOW_RATE = DimensionSignature.create(length=-3, mass=1, time=-1)  # L^-3 M T^-1
VOLUME_FRACTION_OF_I = DimensionSignature.create()  # Dimensionless
WAVENUMBER = DimensionSignature.create(length=-1)  # L^-1