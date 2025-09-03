"""
Qnty - High-Performance Unit System for Engineering
====================================================

A fast, type-safe unit system library for Python with dimensional safety
and optimized unit conversions for engineering calculations.
"""

from .dimension import BaseDimension, DimensionSignature
from .equation import Equation
from .expression import Expression
from .unit import registry
from .units import register_all_units
from .variable import FastQuantity, TypeSafeSetter, TypeSafeVariable
from .variables import (
    AbsorbedDose,
    Acceleration,
    ActivationEnergy,
    AmountOfSubstance,
    AnglePlane,
    AngleSolid,
    AngularAcceleration,
    AngularMomentum,
    Area,
    AreaPerUnitVolume,
    AtomicWeight,
    Concentration,
    DynamicFluidity,
    ElectricCapacitance,
    ElectricCharge,
    ElectricCurrentIntensity,
    ElectricDipoleMoment,
    ElectricFieldStrength,
    ElectricInductance,
    ElectricPotential,
    ElectricResistance,
    ElectricalConductance,
    ElectricalPermittivity,
    ElectricalResistivity,
    EnergyFlux,
    EnergyHeatWork,
    EnergyPerUnitArea,
    Force,
    ForceBody,
    ForcePerUnitMass,
    FrequencyVoltageRatio,
    FuelConsumption,
    HeatOfCombustion,
    HeatOfFusion,
    HeatOfVaporization,
    HeatTransferCoefficient,
    Illuminance,
    KineticEnergyOfTurbulence,
    Length,
    LinearMassDensity,
    LinearMomentum,
    LuminanceSelf,
    LuminousFlux,
    LuminousIntensity,
    MagneticField,
    MagneticFlux,
    MagneticInductionFieldStrength,
    MagneticMoment,
    MagneticPermeability,
    MagnetomotiveForce,
    Mass,
    MassDensity,
    MassFlowRate,
    MassFlux,
    MassFractionOfI,
    MassTransferCoefficient,
    MolalityOfSoluteI,
    MolarConcentrationByMass,
    MolarFlowRate,
    MolarFlux,
    MolarHeatCapacity,
    MolarityOfI,
    MoleFractionOfI,
    MomentOfInertia,
    MomentumFlowRate,
    MomentumFlux,
    NormalityOfSolution,
    ParticleDensity,
    Permeability,
    PhotonEmissionRate,
    PowerPerUnitMass,
    PowerPerUnitVolume,
    PowerThermalDuty,
    Pressure,
    RadiationDoseEquivalent,
    RadiationExposure,
    Radioactivity,
    SecondMomentOfArea,
    SecondRadiationConstantPlanck,
    SpecificEnthalpy,
    SpecificGravity,
    SpecificHeatCapacityConstantPressure,
    SpecificLength,
    SpecificSurface,
    SpecificVolume,
    Stress,
    SurfaceMassDensity,
    SurfaceTension,
    Temperature,
    ThermalConductivity,
    Time,
    Torque,
    TurbulenceEnergyDissipationRate,
    VelocityAngular,
    VelocityLinear,
    ViscosityDynamic,
    ViscosityKinematic,
    Volume,
    VolumeFractionOfI,
    VolumetricCalorificHeatingValue,
    VolumetricCoefficientOfExpansion,
    VolumetricFlowRate,
    VolumetricFlux,
    VolumetricMassFlowRate,
    Wavenumber
)

# Register all units to the global registry
register_all_units(registry)

# Finalize registry after all registrations
registry.finalize_registration()

# Version information
__version__ = "0.0.3"

# Define public API
__all__ = [
    # Core variable types (most commonly used)
    "Length", "Pressure", "Temperature", "Time", "Mass", "Volume", "Area",
    "Force", "EnergyHeatWork", "PowerThermalDuty",

    # Core classes for advanced usage
    "FastQuantity", "TypeSafeVariable", "TypeSafeSetter",
    "DimensionSignature", "BaseDimension",
    "Expression", "Equation",

    # All other variable types (95 additional types)
    "AbsorbedDose", "Acceleration", "ActivationEnergy", "AmountOfSubstance",
    "AnglePlane", "AngleSolid", "AngularAcceleration", "AngularMomentum",
    "AreaPerUnitVolume", "AtomicWeight", "Concentration", "DynamicFluidity",
    "ElectricCapacitance", "ElectricCharge", "ElectricCurrentIntensity",
    "ElectricDipoleMoment", "ElectricFieldStrength", "ElectricInductance",
    "ElectricPotential", "ElectricResistance", "ElectricalConductance",
    "ElectricalPermittivity", "ElectricalResistivity", "EnergyFlux",
    "EnergyPerUnitArea", "ForceBody", "ForcePerUnitMass",
    "FrequencyVoltageRatio", "FuelConsumption", "HeatOfCombustion",
    "HeatOfFusion", "HeatOfVaporization", "HeatTransferCoefficient",
    "Illuminance", "KineticEnergyOfTurbulence", "LinearMassDensity",
    "LinearMomentum", "LuminanceSelf", "LuminousFlux", "LuminousIntensity",
    "MagneticField", "MagneticFlux", "MagneticInductionFieldStrength",
    "MagneticMoment", "MagneticPermeability", "MagnetomotiveForce",
    "MassDensity", "MassFlowRate", "MassFlux", "MassFractionOfI",
    "MassTransferCoefficient", "MolalityOfSoluteI", "MolarConcentrationByMass",
    "MolarFlowRate", "MolarFlux", "MolarHeatCapacity", "MolarityOfI",
    "MoleFractionOfI", "MomentOfInertia", "MomentumFlowRate", "MomentumFlux",
    "NormalityOfSolution", "ParticleDensity", "Permeability",
    "PhotonEmissionRate", "PowerPerUnitMass", "PowerPerUnitVolume",
    "RadiationDoseEquivalent", "RadiationExposure", "Radioactivity",
    "SecondMomentOfArea", "SecondRadiationConstantPlanck", "SpecificEnthalpy",
    "SpecificGravity", "SpecificHeatCapacityConstantPressure",
    "SpecificLength", "SpecificSurface", "SpecificVolume", "Stress",
    "SurfaceMassDensity", "SurfaceTension", "ThermalConductivity", "Torque",
    "TurbulenceEnergyDissipationRate", "VelocityAngular", "VelocityLinear",
    "ViscosityDynamic", "ViscosityKinematic", "VolumeFractionOfI",
    "VolumetricCalorificHeatingValue", "VolumetricCoefficientOfExpansion",
    "VolumetricFlowRate", "VolumetricFlux", "VolumetricMassFlowRate",
    "Wavenumber",
]

