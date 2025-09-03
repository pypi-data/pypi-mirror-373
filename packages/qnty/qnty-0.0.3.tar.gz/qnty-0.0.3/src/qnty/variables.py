"""
Consolidated Variables Module - Complete Edition
===============================================

Consolidated variable definitions for all variable types.
Uses the exact same source of truth and approach as consolidated units system.
Auto-generated from unit_data.json and dimension_mapping.json.
"""

from typing import Any, cast

from .dimension import (
    ABSORBED_DOSE,
    ACCELERATION,
    ACTIVATION_ENERGY,
    AMOUNT_OF_SUBSTANCE,
    ANGLE_PLANE,
    ANGLE_SOLID,
    ANGULAR_ACCELERATION,
    ANGULAR_MOMENTUM,
    AREA,
    AREA_PER_UNIT_VOLUME,
    ATOMIC_WEIGHT,
    CONCENTRATION,
    DIMENSIONLESS,
    DYNAMIC_FLUIDITY,
    ELECTRICAL_CONDUCTANCE,
    ELECTRICAL_PERMITTIVITY,
    ELECTRICAL_RESISTIVITY,
    ELECTRIC_CAPACITANCE,
    ELECTRIC_CHARGE,
    ELECTRIC_CURRENT_INTENSITY,
    ELECTRIC_DIPOLE_MOMENT,
    ELECTRIC_FIELD_STRENGTH,
    ELECTRIC_INDUCTANCE,
    ELECTRIC_POTENTIAL,
    ELECTRIC_RESISTANCE,
    ENERGY_FLUX,
    ENERGY_HEAT_WORK,
    ENERGY_PER_UNIT_AREA,
    FORCE,
    FORCE_BODY,
    FORCE_PER_UNIT_MASS,
    FREQUENCY_VOLTAGE_RATIO,
    FUEL_CONSUMPTION,
    HEAT_OF_COMBUSTION,
    HEAT_OF_FUSION,
    HEAT_OF_VAPORIZATION,
    HEAT_TRANSFER_COEFFICIENT,
    ILLUMINANCE,
    KINETIC_ENERGY_OF_TURBULENCE,
    LENGTH,
    LINEAR_MASS_DENSITY,
    LINEAR_MOMENTUM,
    LUMINANCE_SELF,
    LUMINOUS_FLUX,
    LUMINOUS_INTENSITY,
    MAGNETIC_FIELD,
    MAGNETIC_FLUX,
    MAGNETIC_INDUCTION_FIELD_STRENGTH,
    MAGNETIC_MOMENT,
    MAGNETIC_PERMEABILITY,
    MAGNETOMOTIVE_FORCE,
    MASS,
    MASS_DENSITY,
    MASS_FLOW_RATE,
    MASS_FLUX,
    MASS_FRACTION_OF_I,
    MASS_TRANSFER_COEFFICIENT,
    MOLALITY_OF_SOLUTE_I,
    MOLARITY_OF_I,
    MOLAR_CONCENTRATION_BY_MASS,
    MOLAR_FLOW_RATE,
    MOLAR_FLUX,
    MOLAR_HEAT_CAPACITY,
    MOLE_FRACTION_OF_I,
    MOMENTUM_FLOW_RATE,
    MOMENTUM_FLUX,
    MOMENT_OF_INERTIA,
    NORMALITY_OF_SOLUTION,
    PARTICLE_DENSITY,
    PERMEABILITY,
    PHOTON_EMISSION_RATE,
    POWER_PER_UNIT_MASS,
    POWER_PER_UNIT_VOLUME,
    POWER_THERMAL_DUTY,
    PRESSURE,
    RADIATION_DOSE_EQUIVALENT,
    RADIATION_EXPOSURE,
    RADIOACTIVITY,
    SECOND_MOMENT_OF_AREA,
    SECOND_RADIATION_CONSTANT_PLANCK,
    SPECIFIC_ENTHALPY,
    SPECIFIC_GRAVITY,
    SPECIFIC_HEAT_CAPACITY_CONSTANT_PRESSURE,
    SPECIFIC_LENGTH,
    SPECIFIC_SURFACE,
    SPECIFIC_VOLUME,
    STRESS,
    SURFACE_MASS_DENSITY,
    SURFACE_TENSION,
    TEMPERATURE,
    THERMAL_CONDUCTIVITY,
    TIME,
    TORQUE,
    TURBULENCE_ENERGY_DISSIPATION_RATE,
    VELOCITY_ANGULAR,
    VELOCITY_LINEAR,
    VISCOSITY_DYNAMIC,
    VISCOSITY_KINEMATIC,
    VOLUME,
    VOLUMETRIC_CALORIFIC_HEATING_VALUE,
    VOLUMETRIC_COEFFICIENT_OF_EXPANSION,
    VOLUMETRIC_FLOW_RATE,
    VOLUMETRIC_FLUX,
    VOLUMETRIC_MASS_FLOW_RATE,
    VOLUME_FRACTION_OF_I,
    WAVENUMBER
)
from .unit import UnitConstant, UnitDefinition
from .units import DimensionlessUnits
from .variable import FastQuantity, TypeSafeSetter
from .variable_types.typed_variable import TypedVariable

# Consolidated variable definitions
VARIABLE_DEFINITIONS = {
    "AbsorbedDose": {
        "dimension": ABSORBED_DOSE,
        "default_unit": "gray",
        "units": [
            ("erg per gram", "erg_per_gram", 0.0001, "erg/g", ['erg_per_g']),
            ("gram-rad", "gram_rad", 0.01, "g-rad", ['g_rad']),
            ("gray", "gray", 1.0, "Gy", ['Gy']),
            ("rad", "rad", 0.01, "rad", []),
            ("milligray", "milligray", 0.001, "mGy", ['mGy']),
            ("microgray", "microgray", 1e-06, "μGy", ['μGy'])
        ],
        "field_name": "absorbed_dose",
        "display_name": "Absorbed Radiation Dose",
    },
    "Acceleration": {
        "dimension": ACCELERATION,
        "default_unit": "meter_per_second_squared",
        "units": [
            ("meter per second squared", "meter_per_second_squared", 1.0, "$\\mathrm{m} / \\mathrm{s}^{2}$", ['m_per_s2']),
            ("foot per second squared", "foot_per_second_squared", 0.3048, "$\\mathrm{ft} / \\mathrm{s}^{2}$ or $\\mathrm{ft} / \\mathrm{sec}^{2}$", ['ft_per_s2', 'fps2'])
        ],
        "field_name": "acceleration",
        "display_name": "Acceleration",
    },
    "ActivationEnergy": {
        "dimension": ACTIVATION_ENERGY,
        "default_unit": "joule_per_gram_mole",
        "units": [
            ("Btu per pound mole", "Btu_per_pound_mole", 2326.0, "Btu/lb-mol", ['btu_per_lbmol']),
            ("calorie (mean) per gram mole", "calorie_(mean)_per_gram_mole", 4.18675, "cal/mol", ['cal_mean_per_gmol']),
            ("joule per gram mole", "joule_per_gram_mole", 1.0, "J/mol", []),
            ("joule per kilogram mole", "joule_per_kilogram_mole", 1000.0, "J/kmol", []),
            ("kilocalorie per kilogram mole", "kilocalorie_per_kilogram_mole", 4.18675, "kcal/kmol", [])
        ],
        "field_name": "activation_energy",
        "display_name": "Activation Energy",
    },
    "AmountOfSubstance": {
        "dimension": AMOUNT_OF_SUBSTANCE,
        "default_unit": "mole_(gram)",
        "units": [
            ("kilogram mol or kmol", "kilogram_mol_or_kmol", 1000.0, "kmol", ['kmol']),
            ("mole (gram)", "mole_(gram)", 1.0, "mol", ['mol']),
            ("pound-mole", "pound_mole", 453.6, "lb-mol or mole", ['lb-mol', 'mole']),
            ("millimole (gram)", "millimole_(gram)", 0.001, "mmol", ['mmol']),
            ("micromole (gram)", "micromole_(gram)", 1e-06, "μmol", ['μmol'])
        ],
        "field_name": "amount_of_substance",
        "display_name": "Amount of Substance",
    },
    "AnglePlane": {
        "dimension": ANGLE_PLANE,
        "default_unit": "radian",
        "units": [
            ("degree", "degree", 0.0174533, "${ }^{\\circ}$", []),
            ("gon", "gon", 0.015708, "g or gon", ['g']),
            ("grade", "grade", 0.015708, "g or grad", ['g', 'grad']),
            ("minute (new)", "minute_(new)", 0.00015708, "c", ['c']),
            ("minute of angle", "minute_of_angle", 0.000290888, "'", []),
            ("percent", "percent", 0.062832, "\\%", []),
            ("plane angle", "plane_angle", 3.141593, "-", []),
            ("quadrant", "quadrant", 1.570796, "quadr", []),
            ("radian", "radian", 1.0, "rad", ['rad']),
            ("right angle", "right_angle", 1.570796, "$\\perp$", ['perp']),
            ("round", "round", 6.283185, "tr or r", ['tr', 'r']),
            ("second (new)", "second_(new)", 1.5707999999999999e-06, "cc", ['cc']),
            ("second of angle", "second_of_angle", 4.848099999999999e-06, "\"", []),
            ("thousandth (US)", "thousandth_(US)", 0.0015708, "\\% (US)", []),
            ("turn", "turn", 6.283185, "turn or rev", ['rev'])
        ],
        "field_name": "angle_plane",
        "display_name": "Angle, Plane",
    },
    "AngleSolid": {
        "dimension": ANGLE_SOLID,
        "default_unit": "steradian",
        "units": [
            ("spat", "spat", 12.5663, "spat", ['spat']),
            ("square degree", "square_degree", 0.000304617, "$\\left({ }^{\\circ}\\right)^{2}$", []),
            ("square gon", "square_gon", 0.00024674, "(g) ${ }^{2}$", []),
            ("steradian", "steradian", 1.0, "sr", ['sr'])
        ],
        "field_name": "angle_solid",
        "display_name": "Angle, Solid",
    },
    "AngularAcceleration": {
        "dimension": ANGULAR_ACCELERATION,
        "default_unit": "radian_per_second_squared",
        "units": [
            ("radian per second squared", "radian_per_second_squared", 1.0, "$\\mathrm{rad} / \\mathrm{s}^{2}$", []),
            ("revolution per second squared", "revolution_per_second_squared", 6.2832, "$\\mathrm{rev} / \\mathrm{sec}^{2}$", []),
            ("rpm (or revolution per minute) per minute", "rpm_(or_revolution_per_minute)_per_minute", 0.001745, "$\\mathrm{rev} / \\mathrm{min}^{2}$ or rpm/min", ['rev / min^{2', 'rpm/min'])
        ],
        "field_name": "angular_acceleration",
        "display_name": "Angular Acceleration",
    },
    "AngularMomentum": {
        "dimension": ANGULAR_MOMENTUM,
        "default_unit": "kilogram_meter_squared_per_second",
        "units": [
            ("gram centimeter squared per second", "gram_centimeter_squared_per_second", 1e-07, "$\\mathrm{g} \\mathrm{cm}^{2} / \\mathrm{s}$", []),
            ("kilogram meter squared per second", "kilogram_meter_squared_per_second", 1.0, "$\\mathrm{kg} \\mathrm{m}^{2} / \\mathrm{s}$", []),
            ("pound force square foot per second", "pound_force_square_foot_per_second", 0.04214, "lb ft ${ }^{2} / \\mathrm{sec}$", [])
        ],
        "field_name": "angular_momentum",
        "display_name": "Angular Momentum",
    },
    "Area": {
        "dimension": AREA,
        "default_unit": "square_meter",
        "units": [
            ("acre (general)", "acre_(general)", 4046.856, "ac", ['ac']),
            ("are", "are", 100.0, "a", ['a']),
            ("arpent (Quebec)", "arpent_(Quebec)", 3418.89, "arp", ['arp']),
            ("barn", "barn", 1e-28, "b", ['b']),
            ("circular inch", "circular_inch", 0.000506707, "cin", ['cin']),
            ("circular mil", "circular_mil", 5.07e-10, "cmil", ['cmil']),
            ("hectare", "hectare", 10000.0, "ha", ['ha']),
            ("shed", "shed", 1e-52, "shed", ['shed']),
            ("square centimeter", "square_centimeter", 0.0001, "$\\mathrm{cm}^{2}$", []),
            ("square chain (Ramsden)", "square_chain_(Ramsden)", 929.03, "sq ch (Rams)", []),
            ("square chain (Survey, Gunter's)", "square_chain_(Survey,_Gunter's)", 404.6856, "sq ch (surv)", []),
            ("square decimeter", "square_decimeter", 0.01, "$\\mathrm{dm}^{2}$", []),
            ("square fermi", "square_fermi", 1e-30, "$\\mathrm{F}^{2}$", []),
            ("square foot", "square_foot", 0.092903, "sq ft or ft ${ }^{2}$", ['sq ft', 'ft { ^{2']),
            ("square hectometer", "square_hectometer", 10000.0, "$\\mathrm{hm}^{2}$", []),
            ("square inch", "square_inch", 0.00064516, "sq in or in ${ }^{2}$", ['sq in', 'in { ^{2']),
            ("square kilometer", "square_kilometer", 1000000.0, "$\\mathrm{km}^{2}$", []),
            ("square league (statute)", "square_league_(statute)", 23310000.0, "sq lg (stat)", []),
            ("square meter", "square_meter", 1.0, "$\\mathrm{m}^{2}$", []),
            ("square micron", "square_micron", 1e-12, "$\\mu \\mathrm{m}^{2}$ or $\\mu^{2}$", ['mu m^{2', 'mu^{2']),
            ("square mile (statute)", "square_mile_(statute)", 2590000.0, "sq mi (stat)", []),
            ("square mile (US survey)", "square_mile_(US_survey)", 2590000.0, "sq mi (US Surv)", []),
            ("square millimeter", "square_millimeter", 1e-06, "$\\mathrm{mm}^{2}$", []),
            ("square nanometer", "square_nanometer", 1e-18, "$\\mathrm{nm}^{2}$", []),
            ("square yard", "square_yard", 0.836131, "sq yd", []),
            ("township (US)", "township_(US)", 93240000.0, "twshp", [])
        ],
        "field_name": "area",
        "display_name": "Area",
    },
    "AreaPerUnitVolume": {
        "dimension": AREA_PER_UNIT_VOLUME,
        "default_unit": "square_inch_per_cubic_inch",
        "units": [
            ("square centimeter per cubic centimeter", "square_centimeter_per_cubic_centimeter", 100.0, "$\\mathrm{cm}^{2} / \\mathrm{cc}$", []),
            ("square foot per cubic foot", "square_foot_per_cubic_foot", 3.2808, "$\\mathrm{ft}^{2} / \\mathrm{ft}^{3}$ or sqft/cft", ['ft^{2 / ft^{3', 'sqft/cft']),
            ("square inch per cubic inch", "square_inch_per_cubic_inch", 1.0, "$\\mathrm{in}^{2} / \\mathrm{in}^{3}$ or sq.in./cu. in.", ['in^{2 / in^{3', 'sq.in./cu. in.']),
            ("square meter per cubic meter", "square_meter_per_cubic_meter", 1.0, "$\\mathrm{m}^{2} / \\mathrm{m}^{3}$ or $1 / \\mathrm{m}^{3}$", ['m^{2 / m^{3', '1 / m^{3'])
        ],
        "field_name": "area_per_unit_volume",
        "display_name": "Area per Unit Volume",
    },
    "AtomicWeight": {
        "dimension": ATOMIC_WEIGHT,
        "default_unit": "atomic_mass_unit_(12C)",
        "units": [
            ("atomic mass unit (12C)", "atomic_mass_unit_(12C)", 1.0, "amu", ['amu']),
            ("grams per mole", "grams_per_mole", 1.0, "g/mol", []),
            ("kilograms per kilomole", "kilograms_per_kilomole", 1.0, "kg/kmol", []),
            ("pounds per pound mole", "pounds_per_pound_mole", 1.0, "$\\mathrm{lb} / \\mathrm{lb}-$ mol or $\\mathrm{lb} /$ mole", ['lb / lb- mol', 'lb / mole'])
        ],
        "field_name": "atomic_weight",
        "display_name": "Atomic Weight",
    },
    "Concentration": {
        "dimension": CONCENTRATION,
        "default_unit": "grains_of_\"i\"_per_cubic_foot",
        "units": [
            ("grains of \"i\" per cubic foot", "grains_of_\"i\"_per_cubic_foot", 0.002288, "$\\mathrm{gr} / \\mathrm{ft}^{3}$ or gr/cft", ['gr / ft^{3', 'gr/cft']),
            ("grains of \"i\" per gallon (US)", "grains_of_\"i\"_per_gallon_(US)", 0.017115, "gr/gal", [])
        ],
        "field_name": "concentration",
        "display_name": "Concentration",
    },
    "DynamicFluidity": {
        "dimension": DYNAMIC_FLUIDITY,
        "default_unit": "meter_seconds_per_kilogram",
        "units": [
            ("meter-seconds per kilogram", "meter_seconds_per_kilogram", 1.0, "m s/kg", []),
            ("rhe", "rhe", 1.0, "rhe", ['rhe']),
            ("square foot per pound second", "square_foot_per_pound_second", 0.002086, "$\\mathrm{ft}^{2}$ /(lb sec)", []),
            ("square meters per newton per second", "square_meters_per_newton_per_second", 1.0, "$\\mathrm{m}^{2} /(\\mathrm{N} \\mathrm{s})$", [])
        ],
        "field_name": "dynamic_fluidity",
        "display_name": "Dynamic Fluidity",
    },
    "ElectricCapacitance": {
        "dimension": ELECTRIC_CAPACITANCE,
        "default_unit": "farad",
        "units": [
            ("\"cm\"", "\"cm\"", 1.1111e-12, "\"cm\"", []),
            ("abfarad", "abfarad", 1000000000.0, "emu cgs", []),
            ("farad", "farad", 1.0, "F", ['F']),
            ("farad (intl)", "farad_(intl)", 0.99951, "F (int)", []),
            ("jar", "jar", 1.1111e-09, "jar", ['jar']),
            ("puff", "puff", 1e-12, "puff", ['puff']),
            ("statfarad", "statfarad", 1.113e-12, "esu cgs", []),
            ("millifarad", "millifarad", 0.001, "mF", ['mF']),
            ("microfarad", "microfarad", 1e-06, "μF", ['μF']),
            ("nanofarad", "nanofarad", 1e-09, "nF", ['nF']),
            ("picofarad", "picofarad", 1e-12, "pF", ['pF'])
        ],
        "field_name": "electric_capacitance",
        "display_name": "Electric Capacitance",
    },
    "ElectricCharge": {
        "dimension": ELECTRIC_CHARGE,
        "default_unit": "faraday_(C12)",
        "units": [
            ("abcoulomb", "abcoulomb", 0.000103643, "emu cgs", []),
            ("ampere-hour", "ampere_hour", 0.03731138, "Ah", ['Ah']),
            ("coulomb", "coulomb", 1.0364000000000001e-05, "C", ['C']),
            ("faraday (C12)", "faraday_(C12)", 1.0, "F", ['F']),
            ("franklin", "franklin", 3.45715e-15, "Fr", ['Fr']),
            ("statcoulomb", "statcoulomb", 3.45715e-15, "esu cgs", []),
            ("u.a. charge", "u_a__charge", 1.66054e-24, "u.a.", []),
            ("kilocoulomb", "kilocoulomb", 0.010364000000000002, "kC", ['kC']),
            ("millicoulomb", "millicoulomb", 1.0364000000000001e-08, "mC", ['mC']),
            ("microcoulomb", "microcoulomb", 1.0364e-11, "μC", ['μC']),
            ("nanocoulomb", "nanocoulomb", 1.0364000000000002e-14, "nC", ['nC']),
            ("picocoulomb", "picocoulomb", 1.0364000000000001e-17, "pC", ['pC'])
        ],
        "field_name": "electric_charge",
        "display_name": "Electric Charge",
    },
    "ElectricCurrentIntensity": {
        "dimension": ELECTRIC_CURRENT_INTENSITY,
        "default_unit": "ampere_or_amp",
        "units": [
            ("abampere", "abampere", 10.0, "emu cgs", []),
            ("ampere (intl mean)", "ampere_(intl_mean)", 0.99985, "A (int mean)", []),
            ("ampere (intl US)", "ampere_(intl_US)", 0.999835, "A (int US)", []),
            ("ampere or amp", "ampere_or_amp", 1.0, "A", ['A']),
            ("biot", "biot", 10.0, "biot", ['biot']),
            ("statampere", "statampere", 3.33564e-10, "esu cgs", []),
            ("u.a. or current", "u_a__or_current", 0.00662362, "u.a.", [])
        ],
        "field_name": "electric_current_intensity",
        "display_name": "Electric Current Intensity",
    },
    "ElectricDipoleMoment": {
        "dimension": ELECTRIC_DIPOLE_MOMENT,
        "default_unit": "ampere_meter_second",
        "units": [
            ("ampere meter second", "ampere_meter_second", 1.0, "A m s", []),
            ("coulomb meter", "coulomb_meter", 1.0, "C m", []),
            ("debye", "debye", 3.3356e-30, "D", ['D']),
            ("electron meter", "electron_meter", 1.6022e-19, "e m", [])
        ],
        "field_name": "electric_dipole_moment",
        "display_name": "Electric Dipole Moment",
    },
    "ElectricFieldStrength": {
        "dimension": ELECTRIC_FIELD_STRENGTH,
        "default_unit": "volt_per_meter",
        "units": [
            ("volt per centimeter", "volt_per_centimeter", 100.0, "V/cm", []),
            ("volt per meter", "volt_per_meter", 1.0, "V/m", [])
        ],
        "field_name": "electric_field_strength",
        "display_name": "Electric Field Strength",
    },
    "ElectricInductance": {
        "dimension": ELECTRIC_INDUCTANCE,
        "default_unit": "henry",
        "units": [
            ("abhenry", "abhenry", 1e-09, "emu cgs", []),
            ("cm", "cm", 1e-09, "cm", ['cm']),
            ("henry", "henry", 1.0, "H", ['H']),
            ("henry (intl mean)", "henry_(intl_mean)", 1.00049, "H (int mean)", []),
            ("henry (intl US)", "henry_(intl_US)", 1.000495, "H (int US)", []),
            ("mic", "mic", 1e-06, "mic", ['mic']),
            ("stathenry", "stathenry", 898760000000.0, "esu cgs", []),
            ("millihenry", "millihenry", 0.001, "mH", ['mH']),
            ("microhenry", "microhenry", 1e-06, "μH", ['μH']),
            ("nanohenry", "nanohenry", 1e-09, "nH", ['nH'])
        ],
        "field_name": "electric_inductance",
        "display_name": "Electric Inductance",
    },
    "ElectricPotential": {
        "dimension": ELECTRIC_POTENTIAL,
        "default_unit": "volt",
        "units": [
            ("abvolt", "abvolt", 1e-08, "emu cgs", []),
            ("statvolt", "statvolt", 299.792, "esu cgs", []),
            ("u.a. potential", "u_a__potential", 27.2114, "u.a.", []),
            ("volt", "volt", 1.0, "V", ['V']),
            ("volt (intl mean)", "volt_(intl_mean)", 1.00034, "V (int mean)", []),
            ("volt (US)", "volt_(US)", 1.00033, "V (int US)", []),
            ("kilovolt", "kilovolt", 1000.0, "kV", ['kV']),
            ("millivolt", "millivolt", 0.001, "mV", ['mV']),
            ("microvolt", "microvolt", 1e-06, "μV", ['μV']),
            ("nanovolt", "nanovolt", 1e-09, "nV", ['nV']),
            ("picovolt", "picovolt", 1e-12, "pV", ['pV'])
        ],
        "field_name": "electric_potential",
        "display_name": "Electric Potential",
    },
    "ElectricResistance": {
        "dimension": ELECTRIC_RESISTANCE,
        "default_unit": "ohm",
        "units": [
            ("abohm", "abohm", 1e-09, "emu cgs", []),
            ("jacobi", "jacobi", 0.64, "-", []),
            ("lenz", "lenz", 80000.0, "Metric", []),
            ("ohm", "ohm", 1.0, "$\\Omega$", []),
            ("ohm (intl mean)", "ohm_(intl_mean)", 1.00049, "$\\Omega$ (int mean)", []),
            ("ohm (intl US)", "ohm_(intl_US)", 1.000495, "$\\Omega$ (int US)", []),
            ("ohm (legal)", "ohm_(legal)", 0.9972, "$\\Omega$ (legal)", []),
            ("preece", "preece", 1000000.0, "preece", []),
            ("statohm", "statohm", 8.987552, "csu cgs", []),
            ("wheatstone", "wheatstone", 0.0025, "-", []),
            ("kiloohm", "kiloohm", 1000.0, "k$\\Omega$", ['k$\\\\Omega$']),
            ("megaohm", "megaohm", 1000000.0, "M$\\Omega$", ['M$\\\\Omega$']),
            ("milliohm", "milliohm", 0.001, "m$\\Omega$", ['m$\\\\Omega$'])
        ],
        "field_name": "electric_resistance",
        "display_name": "Electric Resistance",
    },
    "ElectricalConductance": {
        "dimension": ELECTRICAL_CONDUCTANCE,
        "default_unit": "mho",
        "units": [
            ("emu cgs", "emu_cgs", 1000000000.0, "abmho", []),
            ("esu cgs", "esu_cgs", 1.1127e-12, "statmho", []),
            ("mho", "mho", 1.0, "mho", ['mho']),
            ("microsiemens", "microsiemens", 1e-06, "$\\mu \\mathrm{S}$", []),
            ("siemens", "siemens", 1.0, "S", ['S']),
            ("millisiemens", "millisiemens", 0.001, "mS", ['mS'])
        ],
        "field_name": "electrical_conductance",
        "display_name": "Electrical Conductance",
    },
    "ElectricalPermittivity": {
        "dimension": ELECTRICAL_PERMITTIVITY,
        "default_unit": "farad_per_meter",
        "units": [
            ("farad per meter", "farad_per_meter", 1.0, "F/m", [])
        ],
        "field_name": "electrical_permittivity",
        "display_name": "Electrical Permittivity",
    },
    "ElectricalResistivity": {
        "dimension": ELECTRICAL_RESISTIVITY,
        "default_unit": "ohm_meter",
        "units": [
            ("circular mil-ohm per foot", "circular_mil_ohm_per_foot", 1.6624000000000002e-09, "circmil $\\Omega / \\mathrm{ft}$", []),
            ("emu cgs", "emu_cgs", 1e-11, "abohm cm", []),
            ("microhm-inch", "microhm_inch", 2.5400000000000002e-08, "$\\mu \\Omega$ in", []),
            ("ohm-centimeter", "ohm_centimeter", 0.01, "$\\boldsymbol{\\Omega} \\mathbf{c m}$", []),
            ("ohm-meter", "ohm_meter", 1.0, "$\\Omega \\mathrm{m}$", [])
        ],
        "field_name": "electrical_resistivity",
        "display_name": "Electrical Resistivity",
    },
    "EnergyFlux": {
        "dimension": ENERGY_FLUX,
        "default_unit": "watt_per_square_meter",
        "units": [
            ("Btu per square foot per hour", "Btu_per_square_foot_per_hour", 3.1546, "$\\mathrm{Btu} / \\mathrm{ft}^{2} / \\mathrm{hr}$", []),
            ("calorie per square centimeter per second", "calorie_per_square_centimeter_per_second", 41868.0, "$\\mathrm{cal} / \\mathrm{cm}^{2} / \\mathrm{s}$ or $\\mathrm{cal} /$ ( $\\mathrm{cm}^{2} \\mathrm{~s}$ )", ['cal / cm^{2 / s', 'cal / ( cm^{2 ~s )']),
            ("Celsius heat units (Chu) per square foot per hour", "Celsius_heat_units_(Chu)_per_square_foot_per_hour", 5.6784, "$\\mathrm{Chu} / \\mathrm{ft}^{2} / \\mathrm{hr}$", []),
            ("kilocalorie per square foot per hour", "kilocalorie_per_square_foot_per_hour", 12.518, "$\\mathrm{kcal} /\\left(\\mathrm{ft}^{2} \\mathrm{hr}\\right)$", []),
            ("kilocalorie per square meter per hour", "kilocalorie_per_square_meter_per_hour", 1.163, "$\\mathrm{kcal} /\\left(\\mathrm{m}^{2} \\mathrm{hr}\\right)$", []),
            ("watt per square meter", "watt_per_square_meter", 1.0, "$\\mathrm{W} / \\mathrm{m}^{2}$", [])
        ],
        "field_name": "energy_flux",
        "display_name": "Energy Flux",
    },
    "EnergyHeatWork": {
        "dimension": ENERGY_HEAT_WORK,
        "default_unit": "joule",
        "units": [
            ("barrel oil equivalent or equivalent barrel", "barrel_oil_equivalent_or_equivalent_barrel", 6120000000.0, "bboe or boe", ['bboe', 'boe']),
            ("billion electronvolt", "billion_electronvolt", 1.6022000000000002e-10, "BeV", ['BeV']),
            ("British thermal unit ( $4^{\\circ} \\mathrm{C}$ )", "British_thermal_unit_(_$4^{\\circ}_\\mathrm{C}$_)", 1059.67, "Btu ( $39.2{ }^{\\circ} \\mathrm{F}$ )", []),
            ("British thermal unit ( $60^{\\circ} \\mathrm{F}$ )", "British_thermal_unit_(_$60^{\\circ}_\\mathrm{F}$_)", 1054.678, "Btu ( $60{ }^{\\circ} \\mathrm{F}$ )", []),
            ("British thermal unit (international steam tables)", "British_thermal_unit_(international_steam_tables)", 1055.055853, "Btu (IT)", []),
            ("British thermal unit (ISO/TC 12)", "British_thermal_unit_(ISO/TC_12)", 1055.06, "Btu (ISO)", []),
            ("British thermal unit (mean)", "British_thermal_unit_(mean)", 1055.87, "Btu (mean) or Btu", ['Btu (mean)', 'Btu']),
            ("British thermal unit (thermochemical)", "British_thermal_unit_(thermochemical)", 1054.35, "Btu (therm)", []),
            ("calorie ( $20^{\\circ} \\mathrm{C}$ )", "calorie_(_$20^{\\circ}_\\mathrm{C}$_)", 4.1819, "cal ( $20^{\\circ} \\mathrm{C}$ )", []),
            ("calorie ( $4^{\\circ} \\mathrm{C}$ )", "calorie_(_$4^{\\circ}_\\mathrm{C}$_)", 4.2045, "cal ( $4^{\\circ} \\mathrm{C}$ )", []),
            ("calorie (international steam tables)", "calorie_(international_steam_tables)", 4.18674, "cal (IT)", []),
            ("calorie (mean)", "calorie_(mean)", 4.19002, "cal (mean)", []),
            ("Calorie (nutritional)", "Calorie_(nutritional)", 4184.0, "Cal (nutr)", []),
            ("calorie (thermochemical)", "calorie_(thermochemical)", 4.184, "cal (therm)", []),
            ("Celsius heat unit", "Celsius_heat_unit", 1899.18, "Chu", ['Chu']),
            ("Celsius heat unit ( $15{ }^{\\circ} \\mathrm{C}$ )", "Celsius_heat_unit_(_$15{_}^{\\circ}_\\mathrm{C}$_)", 1899.1, "Chu ( $15{ }^{\\circ} \\mathrm{C}$ )", []),
            ("electron volt", "electron_volt", 1.6022e-19, "eV", ['eV']),
            ("erg", "erg", 1e-07, "erg", ['erg']),
            ("foot pound force (duty)", "foot_pound_force_(duty)", 1.355818, "ft $\\mathrm{lb}_{\\mathrm{f}}$", []),
            ("foot-poundal", "foot_poundal", 0.04214, "ft pdl", []),
            ("frigorie", "frigorie", 4190.0, "fg", ['fg']),
            ("hartree (atomic unit of energy)", "hartree_(atomic_unit_of_energy)", 4.359700000000001e-18, "$\\mathrm{E}_{\\mathrm{H}}$ a.u.", []),
            ("joule", "joule", 1.0, "J", ['J']),
            ("joule (international)", "joule_(international)", 1.000165, "J (intl)", []),
            ("kilocalorie (thermal)", "kilocalorie_(thermal)", 4184.0, "kcal (therm)", []),
            ("kilogram force meter", "kilogram_force_meter", 9.80665, "$\\mathrm{kg}_{\\mathrm{f}}$ m", []),
            ("kiloton (TNT)", "kiloton_(TNT)", 4.1799999999999995e+18, "kt (TNT)", []),
            ("kilowatt hour", "kilowatt_hour", 3600000.0, "kWh", ['kWh']),
            ("liter atmosphere", "liter_atmosphere", 101.325, "L atm", []),
            ("megaton (TNT)", "megaton_(TNT)", 4.1799999999999995e+21, "Mt (TNT)", []),
            ("pound centigrade unit ( $15^{\\circ} \\mathrm{C}$ )", "pound_centigrade_unit_(_$15^{\\circ}_\\mathrm{C}$_)", 1899.1, "pcu ( $15{ }^{\\circ} \\mathrm{C}$ )", []),
            ("prout", "prout", 2.9638e-14, "prout", []),
            ("Q unit", "Q_unit", 1.055e+21, "Q", ['Q']),
            ("quad (quadrillion Btu)", "quad_(quadrillion_Btu)", 1.0550999999999999e+18, "quad", ['quad']),
            ("rydberg", "rydberg", 2.1799000000000002e-18, "Ry", ['Ry']),
            ("therm (EEG)", "therm_(EEG)", 105510000.0, "therm (EEG)", []),
            ("therm (refineries)", "therm_(refineries)", 1055900000.0000001, "therm (refy) or therm", ['therm (refy)', 'therm']),
            ("therm (US)", "therm_(US)", 105480000.0, "therm (US) or therm", ['therm']),
            ("ton coal equivalent", "ton_coal_equivalent", 292900000.0, "tce (tec)", []),
            ("ton oil equivalent", "ton_oil_equivalent", 418700000.0, "toe (tep)", []),
            ("kilojoule", "kilojoule", 1000.0, "kJ", ['kJ']),
            ("megajoule", "megajoule", 1000000.0, "MJ", ['MJ']),
            ("gigajoule", "gigajoule", 1000000000.0, "GJ", ['GJ'])
        ],
        "field_name": "energy_heat_work",
        "display_name": "Energy, Heat, Work",
    },
    "EnergyPerUnitArea": {
        "dimension": ENERGY_PER_UNIT_AREA,
        "default_unit": "joule_per_square_meter",
        "units": [
            ("British thermal unit per square foot", "British_thermal_unit_per_square_foot", 11354.0, "$\\mathrm{Btu} / \\mathrm{ft}^{2}$ or Btu/sq ft", ['Btu / ft^{2', 'Btu/sq ft']),
            ("joule per square meter", "joule_per_square_meter", 1.0, "$\\mathrm{J} / \\mathrm{m}^{2}$", []),
            ("Langley", "Langley", 41840.0, "Ly", ['Ly'])
        ],
        "field_name": "energy_per_unit_area",
        "display_name": "Energy per Unit Area",
    },
    "Force": {
        "dimension": FORCE,
        "default_unit": "newton",
        "units": [
            ("crinal", "crinal", 0.1, "crinal", []),
            ("dyne", "dyne", 1e-05, "dyn", ['dyn']),
            ("funal", "funal", 1000.0, "funal", []),
            ("kilogram force", "kilogram_force", 9.80665, "$\\mathrm{kg}_{\\mathrm{f}}$", []),
            ("kip force", "kip_force", 4448.22, "$\\operatorname{kip}_{\\mathrm{f}}$", []),
            ("newton", "newton", 1.0, "N", ['N']),
            ("ounce force", "ounce_force", 0.27801385, "$\\mathrm{oz}_{\\mathrm{f}}$ or oz", ['oz_{f', 'oz']),
            ("pond", "pond", 0.0098066, "p", ['p']),
            ("pound force", "pound_force", 4.4482216, "$\\mathrm{lb}_{\\mathrm{f}}$ or lb", ['lb_{f', 'lb']),
            ("poundal", "poundal", 0.13825495, "pdl", ['pdl']),
            ("slug force", "slug_force", 143.117, "$\\operatorname{slug}_{f}$", []),
            ("sthène", "sthène", 1000.0, "sn", ['sn']),
            ("ton (force, long)", "ton_(force,_long)", 9964.016, "LT", ['LT']),
            ("ton (force, metric)", "ton_(force,_metric)", 9806.65, "MT", ['MT']),
            ("ton (force, short)", "ton_(force,_short)", 8896.44, "T", ['T']),
            ("kilonewton", "kilonewton", 1000.0, "kN", ['kN']),
            ("millinewton", "millinewton", 0.001, "mN", ['mN'])
        ],
        "field_name": "force",
        "display_name": "Force",
    },
    "ForceBody": {
        "dimension": FORCE_BODY,
        "default_unit": "newton_per_cubic_meter",
        "units": [
            ("dyne per cubic centimeter", "dyne_per_cubic_centimeter", 10.0, "dyn/cc or dyn/ $\\mathrm{cm}^{3}$", ['dyn/cc', 'dyn/ cm^{3']),
            ("kilogram force per cubic centimeter", "kilogram_force_per_cubic_centimeter", 9806700.0, "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{cm}^{3}$", []),
            ("kilogram force per cubic meter", "kilogram_force_per_cubic_meter", 9.80665, "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{m}^{3}$", []),
            ("newton per cubic meter", "newton_per_cubic_meter", 1.0, "$\\mathrm{N} / \\mathrm{m}^{3}$", []),
            ("pound force per cubic foot", "pound_force_per_cubic_foot", 157.087, "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{cft}$", []),
            ("pound force per cubic inch", "pound_force_per_cubic_inch", 271450.0, "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{cu} . \\mathrm{in}$.", []),
            ("ton force per cubic foot", "ton_force_per_cubic_foot", 351880.0, "ton $_{\\mathrm{f}} / \\mathrm{cft}$", [])
        ],
        "field_name": "force_body",
        "display_name": "Force (Body)",
    },
    "ForcePerUnitMass": {
        "dimension": FORCE_PER_UNIT_MASS,
        "default_unit": "newton_per_kilogram",
        "units": [
            ("dyne per gram", "dyne_per_gram", 0.01, "dyn/g", []),
            ("kilogram force per kilogram", "kilogram_force_per_kilogram", 9.80665, "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{kg}$", []),
            ("newton per kilogram", "newton_per_kilogram", 1.0, "N/kg", []),
            ("pound force per pound mass", "pound_force_per_pound_mass", 9.80665, "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{lb}$ or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{lb}_{\\mathrm{m}}$", ['lb_{f / lb', 'lb_{f / lb_{m']),
            ("pound force per slug", "pound_force_per_slug", 0.3048, "$\\mathrm{lb}_{\\mathrm{f}} /$ slug", [])
        ],
        "field_name": "force_per_unit_mass",
        "display_name": "Force per Unit Mass",
    },
    "FrequencyVoltageRatio": {
        "dimension": FREQUENCY_VOLTAGE_RATIO,
        "default_unit": "cycles_per_second_per_volt",
        "units": [
            ("cycles per second per volt", "cycles_per_second_per_volt", 1.0, "cycle/(sec V)", []),
            ("hertz per volt", "hertz_per_volt", 1.0, "Hz/V", []),
            ("terahertz per volt", "terahertz_per_volt", 1000000000000.0, "THz/V", [])
        ],
        "field_name": "frequency_voltage_ratio",
        "display_name": "Frequency Voltage Ratio",
    },
    "FuelConsumption": {
        "dimension": FUEL_CONSUMPTION,
        "default_unit": "kilometers_per_liter",
        "units": [
            ("100 km per liter", "100_km_per_liter", 100.0, "$100 \\mathrm{~km} / \\mathrm{l}$", []),
            ("gallons (UK) per 100 miles", "gallons_(UK)_per_100_miles", 35.4, "gal (UK)/ 100 mi", []),
            ("gallons (US) per 100 miles", "gallons_(US)_per_100_miles", 42.51, "gal (US)/ 100 mi", []),
            ("kilometers per gallon (UK)", "kilometers_per_gallon_(UK)", 0.21997, "km/gal (UK)", []),
            ("kilometers per gallon (US)", "kilometers_per_gallon_(US)", 0.26417, "km/gal(US)", []),
            ("kilometers per liter", "kilometers_per_liter", 1.0, "km/l", []),
            ("liters per 100 km", "liters_per_100_km", 100.0, "$1 / 100 \\mathrm{~km}$", []),
            ("liters per kilometer", "liters_per_kilometer", 1.0, "1/km", []),
            ("meters per gallon (UK)", "meters_per_gallon_(UK)", 0.00021997, "m/gal (UK)", []),
            ("meters per gallon (US)", "meters_per_gallon_(US)", 0.00022642000000000004, "1/gal (US)", []),
            ("miles per gallon (UK)", "miles_per_gallon_(UK)", 0.35401, "mi/gal (UK) or mpg (UK)", ['mi/gal (UK)', 'mpg (UK)']),
            ("miles per gallon (US)", "miles_per_gallon_(US)", 0.42514, "mi/gal (US) or mpg (US)", ['mi/gal (US)', 'mpg (US)']),
            ("miles per liter", "miles_per_liter", 1.6093, "mi/l", [])
        ],
        "field_name": "fuel_consumption",
        "display_name": "Fuel Consumption",
    },
    "HeatOfCombustion": {
        "dimension": HEAT_OF_COMBUSTION,
        "default_unit": "joule_per_kilogram",
        "units": [
            ("British thermal unit per pound", "British_thermal_unit_per_pound", 2326.0, "Btu/lb", []),
            ("calorie per gram", "calorie_per_gram", 4186.0, "$\\mathrm{cal} / \\mathrm{g}$", []),
            ("Chu per pound", "Chu_per_pound", 4186.8, "Chu/lb", []),
            ("joule per kilogram", "joule_per_kilogram", 1.0, "J/kg", [])
        ],
        "field_name": "heat_of_combustion",
        "display_name": "Heat of Combustion",
    },
    "HeatOfFusion": {
        "dimension": HEAT_OF_FUSION,
        "default_unit": "joule_per_kilogram",
        "units": [
            ("British thermal unit (mean) per pound", "British_thermal_unit_(mean)_per_pound", 2327.79, "Btu (mean)/lb", []),
            ("British thermal unit per pound", "British_thermal_unit_per_pound", 2326.0, "Btu/lb", []),
            ("calorie per gram", "calorie_per_gram", 4186.0, "$\\mathrm{cal} / \\mathrm{g}$", []),
            ("Chu per pound", "Chu_per_pound", 4186.8, "Chu/lb", []),
            ("joule per kilogram", "joule_per_kilogram", 1.0, "J/kg", [])
        ],
        "field_name": "heat_of_fusion",
        "display_name": "Heat of Fusion",
    },
    "HeatOfVaporization": {
        "dimension": HEAT_OF_VAPORIZATION,
        "default_unit": "joule_per_kilogram",
        "units": [
            ("British thermal unit per pound", "British_thermal_unit_per_pound", 2326.0, "Btu/lb", []),
            ("calorie per gram", "calorie_per_gram", 4186.0, "$\\mathrm{cal} / \\mathrm{g}$", []),
            ("Chu per pound", "Chu_per_pound", 4186.8, "Chu/lb", []),
            ("joule per kilogram", "joule_per_kilogram", 1.0, "J/kg", [])
        ],
        "field_name": "heat_of_vaporization",
        "display_name": "Heat of Vaporization",
    },
    "HeatTransferCoefficient": {
        "dimension": HEAT_TRANSFER_COEFFICIENT,
        "default_unit": "watt_per_square_meter_per_degree_Celsius_(or_kelvin)",
        "units": [
            ("Btu per square foot per hour per degree Fahrenheit (or Rankine)", "Btu_per_square_foot_per_hour_per_degree_Fahrenheit_(or_Rankine)", 5.679, "$\\mathrm{Btu} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}{ }^{\\circ} \\mathrm{F}\\right)$", []),
            ("watt per square meter per degree Celsius (or kelvin)", "watt_per_square_meter_per_degree_Celsius_(or_kelvin)", 1.0, "$\\mathrm{W} /\\left(\\mathrm{m}^{2}{ }^{\\circ} \\mathrm{C}\\right)$", [])
        ],
        "field_name": "heat_transfer_coefficient",
        "display_name": "Heat Transfer Coefficient",
    },
    "Illuminance": {
        "dimension": ILLUMINANCE,
        "default_unit": "lux",
        "units": [
            ("foot-candle", "foot_candle", 10.76391, "$\\mathrm{ft}-\\mathrm{C}$ or $\\mathrm{ft}-\\mathrm{Cd}$", ['ft-C', 'ft-Cd']),
            ("lux", "lux", 1.0, "lx", ['lx']),
            ("nox", "nox", 0.001, "nox", ['nox']),
            ("phot", "phot", 10000.0, "ph", ['ph']),
            ("skot", "skot", 0.001, "skot", ['skot'])
        ],
        "field_name": "illuminance",
        "display_name": "Illuminance",
    },
    "KineticEnergyOfTurbulence": {
        "dimension": KINETIC_ENERGY_OF_TURBULENCE,
        "default_unit": "square_meters_per_second_squared",
        "units": [
            ("square foot per second squared", "square_foot_per_second_squared", 0.0929, "$\\mathrm{ft}^{2} / \\mathrm{s}^{2}$ or sqft/sec ${ }^{2}$", ['ft^{2 / s^{2', 'sqft/sec { ^{2']),
            ("square meters per second squared", "square_meters_per_second_squared", 1.0, "$\\mathrm{m}^{2} / \\mathrm{s}^{2}$", [])
        ],
        "field_name": "kinetic_energy_of_turbulence",
        "display_name": "Kinetic Energy of Turbulence",
    },
    "Length": {
        "dimension": LENGTH,
        "default_unit": "meter",
        "units": [
            ("ångström", "ångström", 1e-10, "$\\AA$", ['AA']),
            ("arpent (Quebec)", "arpent_(Quebec)", 58.47, "arp", ['arp']),
            ("astronomic unit", "astronomic_unit", 149600000000.0, "AU", ['AU']),
            ("attometer", "attometer", 1e-18, "am", ['am']),
            ("calibre (centinch)", "calibre_(centinch)", 0.000254, "cin", ['cin']),
            ("centimeter", "centimeter", 0.01, "cm", ['cm']),
            ("chain (Engr's or Ramsden)", "chain_(Engr's_or_Ramsden)", 30.48, "ch (eng or Rams)", ['ch (eng', 'Rams)']),
            ("chain (Gunter's)", "chain_(Gunter's)", 20.1168, "ch (Gunt)", []),
            ("chain (surveyors)", "chain_(surveyors)", 20.1168, "ch (surv)", []),
            ("cubit (UK)", "cubit_(UK)", 0.4572, "cu (UK)", []),
            ("ell", "ell", 1.143, "ell", ['ell']),
            ("fathom", "fathom", 1.8288, "fath", ['fath']),
            ("femtometre", "femtometre", 1e-15, "fm", ['fm']),
            ("fermi", "fermi", 1e-15, "F", ['F']),
            ("foot", "foot", 0.3048, "ft", ['ft']),
            ("furlong (UK and US)", "furlong_(UK_and_US)", 201.168, "fur", ['fur']),
            ("inch", "inch", 0.0254, "in", ['in']),
            ("kilometer", "kilometer", 1000.0, "km", ['km']),
            ("league (US, statute)", "league_(US,_statute)", 4828.0, "lg (US, stat)", []),
            ("lieue (metric)", "lieue_(metric)", 4000.0, "lieue (metric)", []),
            ("ligne (metric)", "ligne_(metric)", 0.0023, "ligne (metric)", []),
            ("line (US)", "line_(US)", 0.000635, "li (US)", []),
            ("link (surveyors)", "link_(surveyors)", 0.201168, "li (surv)", []),
            ("meter", "meter", 1.0, "m", ['m']),
            ("micrometer", "micrometer", 1e-06, "$\\mu \\mathrm{m}$", []),
            ("micron", "micron", 1e-06, "$\\mu$", ['mu']),
            ("mil", "mil", 2.54e-05, "mil", ['mil']),
            ("mile (geographical)", "mile_(geographical)", 7421.59, "mi", ['mi']),
            ("mile (US, nautical)", "mile_(US,_nautical)", 1853.2, "mi (US, naut)", []),
            ("mile (US, statute)", "mile_(US,_statute)", 1609.344, "mi", ['mi']),
            ("mile (US, survey)", "mile_(US,_survey)", 1609.3, "mi (US, surv)", []),
            ("millimeter", "millimeter", 0.001, "mm", ['mm']),
            ("millimicron", "millimicron", 1e-09, "$\\mathrm{m} \\mu$", []),
            ("nanometer or nanon", "nanometer_or_nanon", 1e-09, "nm", ['nm']),
            ("parsec", "parsec", 3.086e+16, "pc", ['pc']),
            ("perche", "perche", 5.0292, "rod", ['rod']),
            ("pica", "pica", 0.0042175, "pica", ['pica']),
            ("picometer", "picometer", 1e-12, "pm", ['pm']),
            ("point (Didot)", "point_(Didot)", 0.00037597, "pt (Didot)", []),
            ("point (US)", "point_(US)", 0.00035146, "pt (US)", []),
            ("rod or pole", "rod_or_pole", 5.0292, "rod", ['rod']),
            ("span", "span", 0.2286, "span", ['span']),
            ("thou (millinch)", "thou_(millinch)", 2.54e-05, "thou", ['thou']),
            ("toise (metric)", "toise_(metric)", 2.0, "toise (metric)", []),
            ("yard", "yard", 0.9144, "yd", ['yd']),
            ("nanometer", "nanometer", 1e-09, "nm", ['nm'])
        ],
        "field_name": "length",
        "display_name": "Length",
    },
    "LinearMassDensity": {
        "dimension": LINEAR_MASS_DENSITY,
        "default_unit": "kilogram_per_meter",
        "units": [
            ("denier", "denier", 1.111e-07, "denier", []),
            ("kilogram per centimeter", "kilogram_per_centimeter", 100.0, "kg/cm", []),
            ("kilogram per meter", "kilogram_per_meter", 1.0, "kg/m", []),
            ("pound per foot", "pound_per_foot", 1.488, "lb/ft", []),
            ("pound per inch", "pound_per_inch", 17.858, "lb/in", []),
            ("pound per yard", "pound_per_yard", 0.49606, "lb/yd", []),
            ("ton (metric) per kilometer", "ton_(metric)_per_kilometer", 1.0, "t/km or MT/km", ['t/km', 'MT/km']),
            ("ton (metric) per meter", "ton_(metric)_per_meter", 1000.0, "t/m or MT/m", ['t/m', 'MT/m'])
        ],
        "field_name": "linear_mass_density",
        "display_name": "Linear Mass Density",
    },
    "LinearMomentum": {
        "dimension": LINEAR_MOMENTUM,
        "default_unit": "kilogram_meters_per_second",
        "units": [
            ("foot pounds force per hour", "foot_pounds_force_per_hour", 3.8400000000000005e-05, "${\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}}}^{/} \\mathrm{h}$ or $\\mathrm{ft}-\\mathrm{lb} / \\mathrm{hr}$", ['{ft lb_{f^{/ h', 'ft-lb / hr']),
            ("foot pounds force per minute", "foot_pounds_force_per_minute", 0.0023042, "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\min$ or $\\mathrm{ft}-\\mathrm{lb} /$ min", ['ft lb_{f / min', 'ft-lb / min']),
            ("foot pounds force per second", "foot_pounds_force_per_second", 0.13825, "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{s}$ or ft-lb/sec", ['ft lb_{f / s', 'ft-lb/sec']),
            ("gram centimeters per second", "gram_centimeters_per_second", 1e-05, "$\\mathrm{g} \\mathrm{cm} / \\mathrm{s}$", []),
            ("kilogram meters per second", "kilogram_meters_per_second", 1.0, "$\\mathrm{kg} \\mathrm{m} / \\mathrm{s}$", [])
        ],
        "field_name": "linear_momentum",
        "display_name": "Linear Momentum",
    },
    "LuminanceSelf": {
        "dimension": LUMINANCE_SELF,
        "default_unit": "candela_per_square_meter",
        "units": [
            ("apostilb", "apostilb", 0.31831, "asb", ['asb']),
            ("blondel", "blondel", 0.31831, "B1", []),
            ("candela per square meter", "candela_per_square_meter", 1.0, "$\\mathrm{cd} / \\mathrm{m}^{2}$", []),
            ("foot-lambert", "foot_lambert", 3.426259, "ft-L", []),
            ("lambert", "lambert", 3183.1, "L", ['L']),
            ("luxon", "luxon", 10000.0, "luxon", []),
            ("nit", "nit", 1.0, "nit", ['nit']),
            ("stilb", "stilb", 10000.0, "sb", ['sb']),
            ("troland", "troland", 10000.0, "luxon", [])
        ],
        "field_name": "luminance_self",
        "display_name": "Luminance (self)",
    },
    "LuminousFlux": {
        "dimension": LUMINOUS_FLUX,
        "default_unit": "candela_steradian",
        "units": [
            ("candela steradian", "candela_steradian", 1.0, "cd sr", []),
            ("lumen", "lumen", 1.0, "lumen", [])
        ],
        "field_name": "luminous_flux",
        "display_name": "Luminous Flux",
    },
    "LuminousIntensity": {
        "dimension": LUMINOUS_INTENSITY,
        "default_unit": "candela",
        "units": [
            ("candela", "candela", 1.0, "cd", ['cd']),
            ("candle (international)", "candle_(international)", 1.01937, "Cd (int)", []),
            ("carcel", "carcel", 10.0, "carcel", []),
            ("Hefner unit", "Hefner_unit", 0.903, "HK", ['HK'])
        ],
        "field_name": "luminous_intensity",
        "display_name": "Luminous Intensity",
    },
    "MagneticField": {
        "dimension": MAGNETIC_FIELD,
        "default_unit": "ampere_per_meter",
        "units": [
            ("ampere per meter", "ampere_per_meter", 1.0, "A/m", []),
            ("lenz", "lenz", 1.0, "lenz", ['lenz']),
            ("oersted", "oersted", 79.57747, "Oe", ['Oe']),
            ("praoersted", "praoersted", 11459.08, "-", [])
        ],
        "field_name": "magnetic_field",
        "display_name": "Magnetic Field",
    },
    "MagneticFlux": {
        "dimension": MAGNETIC_FLUX,
        "default_unit": "weber",
        "units": [
            ("kapp line", "kapp_line", 6.000000000000001e-05, "-", []),
            ("line", "line", 1e-08, "line", ['line']),
            ("maxwell", "maxwell", 1e-08, "Mx", ['Mx']),
            ("unit pole", "unit_pole", 1.2565999999999998e-07, "unit pole", []),
            ("weber", "weber", 1.0, "Wb", ['Wb']),
            ("milliweber", "milliweber", 0.001, "mWb", ['mWb']),
            ("microweber", "microweber", 1e-06, "μWb", ['μWb'])
        ],
        "field_name": "magnetic_flux",
        "display_name": "Magnetic Flux",
    },
    "MagneticInductionFieldStrength": {
        "dimension": MAGNETIC_INDUCTION_FIELD_STRENGTH,
        "default_unit": "tesla",
        "units": [
            ("gamma", "gamma", 1e-09, "$\\gamma$", []),
            ("gauss", "gauss", 0.0001, "G", ['G']),
            ("line per square centimeter", "line_per_square_centimeter", 0.0001, "line $/ \\mathrm{cm}^{2}$", []),
            ("maxwell per square centimeter", "maxwell_per_square_centimeter", 0.0001, "$\\mathrm{Mx} / \\mathrm{cm}^{2}$", []),
            ("tesla", "tesla", 1.0, "T", ['T']),
            ("u.a.", "u_a_", 2350520000000000.0, "u.a.", []),
            ("weber per square meter", "weber_per_square_meter", 1.0, "$\\mathrm{Wb} / \\mathrm{m}^{2}$", []),
            ("millitesla", "millitesla", 0.001, "mT", ['mT']),
            ("microtesla", "microtesla", 1e-06, "μT", ['μT']),
            ("nanotesla", "nanotesla", 1e-09, "nT", ['nT'])
        ],
        "field_name": "magnetic_induction_field_strength",
        "display_name": "Magnetic Induction Field Strength",
    },
    "MagneticMoment": {
        "dimension": MAGNETIC_MOMENT,
        "default_unit": "joule_per_tesla",
        "units": [
            ("Bohr magneton", "Bohr_magneton", 9.273999999999999e-24, "Bohr magneton", []),
            ("joule per tesla", "joule_per_tesla", 1.0, "J/T", []),
            ("nuclear magneton", "nuclear_magneton", 5.0508e-27, "nucl. Magneton", [])
        ],
        "field_name": "magnetic_moment",
        "display_name": "Magnetic Moment",
    },
    "MagneticPermeability": {
        "dimension": MAGNETIC_PERMEABILITY,
        "default_unit": "henrys_per_meter",
        "units": [
            ("henrys per meter", "henrys_per_meter", 1.0, "H/m", []),
            ("newton per square ampere", "newton_per_square_ampere", 1.0, "N/A ${ }^{2}$", [])
        ],
        "field_name": "magnetic_permeability",
        "display_name": "Magnetic Permeability",
    },
    "MagnetomotiveForce": {
        "dimension": MAGNETOMOTIVE_FORCE,
        "default_unit": "ampere",
        "units": [
            ("abampere-turn", "abampere_turn", 10.0, "emu cgs", []),
            ("ampere", "ampere", 1.0, "A", ['A']),
            ("ampere-turn", "ampere_turn", 2864.77, "A-turn", []),
            ("gilbert", "gilbert", 0.79577, "Gb", ['Gb']),
            ("kiloampere", "kiloampere", 1000.0, "kA", ['kA']),
            ("milliampere", "milliampere", 0.001, "mA", ['mA']),
            ("microampere", "microampere", 1e-06, "μA", ['μA']),
            ("nanoampere", "nanoampere", 1e-09, "nA", ['nA']),
            ("picoampere", "picoampere", 1e-12, "pA", ['pA'])
        ],
        "field_name": "magnetomotive_force",
        "display_name": "Magnetomotive Force",
    },
    "Mass": {
        "dimension": MASS,
        "default_unit": "kilogram",
        "units": [
            ("slug", "slug", 14.594, "sl", ['sl']),
            ("atomic mass unit ( ${ }^{12} \\mathrm{C}$ )", "atomic_mass_unit_(_${_}^{12}_\\mathrm{C}$_)", 1.6605000000000002e-27, "$\\mathrm{u}\\left({ }^{12} \\mathrm{C}\\right)$ or amu", ['uleft({ ^{12 Cright)', 'amu']),
            ("carat (metric)", "carat_(metric)", 0.0002, "ct", ['ct']),
            ("cental", "cental", 45.359, "sh cwt, cH", []),
            ("centigram", "centigram", 1e-05, "cg", ['cg']),
            ("clove (UK)", "clove_(UK)", 3.6287, "cl", ['cl']),
            ("drachm (apothecary)", "drachm_(apothecary)", 0.0038879, "dr (ap)", []),
            ("dram (avoirdupois)", "dram_(avoirdupois)", 0.0017718, "dr (av)", []),
            ("dram (troy)", "dram_(troy)", 0.0038879, "dr (troy)", []),
            ("grain", "grain", 6.4799e-05, "gr", ['gr']),
            ("gram", "gram", 0.001, "g", ['g']),
            ("hundredweight, long or gross", "hundredweight,_long_or_gross", 50.802, "cwt, lg cwt", []),
            ("hundredweight, short or net", "hundredweight,_short_or_net", 45.359, "sh cwt", []),
            ("kilogram", "kilogram", 1.0, "kg", ['kg']),
            ("kip", "kip", 453.59, "kip", ['kip']),
            ("microgram", "microgram", 1e-09, "$\\mu \\mathrm{g}$", []),
            ("milligram", "milligram", 1e-06, "mg", ['mg']),
            ("ounce (apothecary)", "ounce_(apothecary)", 0.031103, "oz (ap)", []),
            ("ounce (avoirdupois)", "ounce_(avoirdupois)", 0.02835, "oz", ['oz']),
            ("ounce (troy)", "ounce_(troy)", 0.031103, "oz (troy)", []),
            ("pennyweight (troy)", "pennyweight_(troy)", 0.0015552, "dwt (troy)", []),
            ("pood, (Russia)", "pood,_(Russia)", 16.38, "pood", ['pood']),
            ("pound (apothecary)", "pound_(apothecary)", 0.37324, "lb (ap)", []),
            ("pound (avoirdupois)", "pound_(avoirdupois)", 0.45359, "lb (av)", []),
            ("pound (troy)", "pound_(troy)", 0.37324, "lb (troy)", []),
            ("pound mass", "pound_mass", 0.45359, "$\\mathrm{lb}_{\\mathrm{m}}$", []),
            ("quarter (UK)", "quarter_(UK)", 12.7, "qt", ['qt']),
            ("quintal, metric", "quintal,_metric", 100.0, "q, dt", []),
            ("quital, US", "quital,_US", 45.359, "quint (US)", []),
            ("scruple (avoirdupois)", "scruple_(avoirdupois)", 0.001575, "scf", ['scf']),
            ("stone (UK)", "stone_(UK)", 6.3503, "st", ['st']),
            ("ton, metric", "ton,_metric", 1000.0, "t", ['t']),
            ("ton, US, long", "ton,_US,_long", 1016.0, "lg ton", []),
            ("ton, US, short", "ton,_US,_short", 907.18, "sh ton", [])
        ],
        "field_name": "mass",
        "display_name": "Mass",
    },
    "MassDensity": {
        "dimension": MASS_DENSITY,
        "default_unit": "gram_per_cubic_decimeter",
        "units": [
            ("gram per cubic centimeter", "gram_per_cubic_centimeter", 1000.0, "g/cc or g/ml", ['g/cc', 'g/ml']),
            ("gram per cubic decimeter", "gram_per_cubic_decimeter", 1.0, "$\\mathrm{g} / \\mathrm{dm}^{3}$", []),
            ("gram per cubic meter", "gram_per_cubic_meter", 0.001, "$\\mathrm{g} / \\mathrm{m}^{3}$", []),
            ("gram per liter", "gram_per_liter", 1.0, "$\\mathrm{g} / \\mathrm{l}$ or g/L", ['g / l', 'g/L']),
            ("kilogram per cubic meter", "kilogram_per_cubic_meter", 1.0, "$\\mathrm{kg} / \\mathrm{m}^{3}$", []),
            ("ounce (avdp) per US gallon", "ounce_(avdp)_per_US_gallon", 7.489152, "oz/gal", []),
            ("pound (avdp) per cubic foot", "pound_(avdp)_per_cubic_foot", 16.01846, "$\\mathrm{lb} / \\mathrm{cu} \\mathrm{ft}$ or lb/ft ${ }^{3}$", ['lb / cu ft', 'lb/ft { ^{3']),
            ("pound (avdp) per US gallon", "pound_(avdp)_per_US_gallon", 119.826, "lb/gal", []),
            ("pound (mass) per cubic inch", "pound_(mass)_per_cubic_inch", 0.000276799, "$\\mathrm{lb} / \\mathrm{cu}$ in or $\\mathrm{lb} / \\mathrm{in}^{3}$", ['lb / cu in', 'lb / in^{3']),
            ("ton (metric) per cubic meter", "ton_(metric)_per_cubic_meter", 1000.0, "$\\mathrm{t} / \\mathrm{m}^{3}$ or MT $/ \\mathrm{m}^{3}$", ['t / m^{3', 'MT / m^{3'])
        ],
        "field_name": "mass_density",
        "display_name": "Mass Density",
    },
    "MassFlowRate": {
        "dimension": MASS_FLOW_RATE,
        "default_unit": "kilograms_per_second",
        "units": [
            ("kilograms per day", "kilograms_per_day", 1.1574000000000001e-05, "kg/d", []),
            ("kilograms per hour", "kilograms_per_hour", 0.00027778, "kg/h", []),
            ("kilograms per minute", "kilograms_per_minute", 0.016667, "kg/min", []),
            ("kilograms per second", "kilograms_per_second", 1.0, "kg/s", []),
            ("metric tons per day", "metric_tons_per_day", 0.01157, "MT/d or MTD", ['MT/d', 'MTD']),
            ("metric tons per hour", "metric_tons_per_hour", 0.2778, "MT/h or MTD", ['MT/h', 'MTD']),
            ("metric tons per minute", "metric_tons_per_minute", 16.67, "MT/h", []),
            ("metric tons per second", "metric_tons_per_second", 1000.0, "MT/s", []),
            ("metric tons per year (365 d)", "metric_tons_per_year_(365_d)", 3.171e-05, "MT/yr or MTY", ['MT/yr', 'MTY']),
            ("pounds per day", "pounds_per_day", 5.248999999999999e-06, "$\\mathrm{lb} / \\mathrm{d}$ or $\\mathrm{lb} / \\mathrm{da}$ or PPD", ['lb / d', 'lb / da', 'PPD']),
            ("pounds per hour", "pounds_per_hour", 0.00012598, "$\\mathrm{lb} / \\mathrm{h}$ or lb/hr or PPH", ['lb / h', 'lb/hr', 'PPH']),
            ("pounds per minute", "pounds_per_minute", 0.0075586, "$\\mathrm{lb} / \\mathrm{min}$ or PPM", ['lb / min', 'PPM']),
            ("pounds per second", "pounds_per_second", 0.45351, "$\\mathrm{lb} / \\mathrm{s}$ or lb/sec or PPS", ['lb / s', 'lb/sec', 'PPS'])
        ],
        "field_name": "mass_flow_rate",
        "display_name": "Mass Flow Rate",
    },
    "MassFlux": {
        "dimension": MASS_FLUX,
        "default_unit": "kilogram_per_square_meter_per_second",
        "units": [
            ("kilogram per square meter per day", "kilogram_per_square_meter_per_day", 1.1574000000000001e-05, "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$", []),
            ("kilogram per square meter per hour", "kilogram_per_square_meter_per_hour", 0.00027778000000000004, "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$", []),
            ("kilogram per square meter per minute", "kilogram_per_square_meter_per_minute", 0.016667, "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~min}\\right)$", []),
            ("kilogram per square meter per second", "kilogram_per_square_meter_per_second", 1.0, "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$", []),
            ("pound per square foot per day", "pound_per_square_foot_per_day", 5.6478000000000004e-05, "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or lb/sqft/ da", ['lb /left(ft^{2 ~dright)', 'lb/sqft/ da']),
            ("pound per square foot per hour", "pound_per_square_foot_per_hour", 0.0013555, "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or lb/sqft/ hr", ['lb /left(ft^{2 ~hright)', 'lb/sqft/ hr']),
            ("pound per square foot per minute", "pound_per_square_foot_per_minute", 0.081329, "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\min \\right)$ or lb/ sqft/min", ['lb /left(ft^{2 min right)', 'lb/ sqft/min']),
            ("pound per square foot per second", "pound_per_square_foot_per_second", 4.8797, "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or lb/sqft/ sec", ['lb /left(ft^{2 ~sright)', 'lb/sqft/ sec'])
        ],
        "field_name": "mass_flux",
        "display_name": "Mass Flux",
    },
    "MassFractionOfI": {
        "dimension": MASS_FRACTION_OF_I,
        "default_unit": "kilogram_of_\"i\"_per_kilogram_total",
        "units": [
            ("grains of \"i\" per pound total", "grains_of_\"i\"_per_pound_total", 0.00014286, "$\\mathrm{gr}_{\\mathrm{i}} / \\mathrm{lb}$", []),
            ("gram of \"i\" per kilogram total", "gram_of_\"i\"_per_kilogram_total", 0.001, "$\\mathrm{g}_{\\mathrm{i}} / \\mathrm{kg}$", []),
            ("kilogram of \"i\" per kilogram total", "kilogram_of_\"i\"_per_kilogram_total", 1.0, "$\\mathrm{kg}_{\\mathrm{i}} / \\mathrm{kg}$", []),
            ("pound of \"i\" per pound total", "pound_of_\"i\"_per_pound_total", 1.0, "$\\mathrm{lb}_{\\mathrm{i}} / \\mathrm{lb}$", [])
        ],
        "field_name": "mass_fraction_of_i",
        "display_name": "Mass Fraction of \"i\"",
    },
    "MassTransferCoefficient": {
        "dimension": MASS_TRANSFER_COEFFICIENT,
        "default_unit": "kilogram_per_square_meter_per_second",
        "units": [
            ("gram per square centimeter per second", "gram_per_square_centimeter_per_second", 0.1, "$\\mathrm{g} / \\mathrm{cm}^{2} / \\mathrm{s}$", []),
            ("kilogram per square meter per second", "kilogram_per_square_meter_per_second", 1.0, "$\\mathrm{kg} / \\mathrm{m}^{2} / \\mathrm{s}$", []),
            ("pounds force per cubic foot per hour", "pounds_force_per_cubic_foot_per_hour", 15.709, "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}^{3} / \\mathrm{h}$ or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{cft} / \\mathrm{hr}$", ['lb_{f / ft^{3 / h', 'lb_{f / cft / hr']),
            ("pounds mass per square foot per hour", "pounds_mass_per_square_foot_per_hour", 0.00013562, "lb/(ft ${ }^{2} \\mathrm{hr}$ ) or lb/sqft/ hr", ['lb/(ft { ^{2 hr )', 'lb/sqft/ hr']),
            ("pounds mass per square foot per second", "pounds_mass_per_square_foot_per_second", 0.48824, "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or lb/sqft/ sec", ['lb /left(ft^{2 ~sright)', 'lb/sqft/ sec'])
        ],
        "field_name": "mass_transfer_coefficient",
        "display_name": "Mass Transfer Coefficient",
    },
    "MolalityOfSoluteI": {
        "dimension": MOLALITY_OF_SOLUTE_I,
        "default_unit": "gram_moles_of_\"i\"_per_kilogram",
        "units": [
            ("gram moles of \"i\" per kilogram", "gram_moles_of_\"i\"_per_kilogram", 1.0, "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{kg}$", []),
            ("kilogram mols of \"i\" per kilogram", "kilogram_mols_of_\"i\"_per_kilogram", 1000.0, "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kg}$", []),
            ("kmols of \"i\" per kilogram", "kmols_of_\"i\"_per_kilogram", 1000.0, "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kg}$", []),
            ("mols of \"i\" per gram", "mols_of_\"i\"_per_gram", 1000.0, "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{g}$", []),
            ("pound moles of \"i\" per pound mass", "pound_moles_of_\"i\"_per_pound_mass", 1000.0, "mole $_{\\mathrm{i}} / \\mathrm{lb}$ (mass)", [])
        ],
        "field_name": "molality_of_solute_i",
        "display_name": "Molality of Solute \"i\"",
    },
    "MolarConcentrationByMass": {
        "dimension": MOLAR_CONCENTRATION_BY_MASS,
        "default_unit": "gram_mole_or_mole_per_gram",
        "units": [
            ("gram mole or mole per gram", "gram_mole_or_mole_per_gram", 1.0, "mol/g", []),
            ("gram mole or mole per kilogram", "gram_mole_or_mole_per_kilogram", 0.001, "mol/kg", []),
            ("kilogram mole or kmol per kilogram", "kilogram_mole_or_kmol_per_kilogram", 1.0, "kmol/kg", []),
            ("micromole per gram", "micromole_per_gram", 1e-06, "$\\mu \\mathrm{mol} / \\mathrm{g}$", []),
            ("millimole per gram", "millimole_per_gram", 0.001, "mmol/g", []),
            ("picomole per gram", "picomole_per_gram", 1e-12, "pmol/g", []),
            ("pound mole per pound", "pound_mole_per_pound", 1.0, "$\\mathrm{lb}-\\mathrm{mol} / \\mathrm{lb}$ or mole/lb", ['lb-mol / lb', 'mole/lb'])
        ],
        "field_name": "molar_concentration_by_mass",
        "display_name": "Molar Concentration by Mass",
    },
    "MolarFlowRate": {
        "dimension": MOLAR_FLOW_RATE,
        "default_unit": "kilogram_mole_or_kmol_per_hour",
        "units": [
            ("gram mole per day", "gram_mole_per_day", 4.167e-05, "mol/d", []),
            ("gram mole per hour", "gram_mole_per_hour", 0.001, "mol/h", []),
            ("gram mole per minute", "gram_mole_per_minute", 0.06, "mol/min", []),
            ("gram mole per second", "gram_mole_per_second", 3.6, "mol/s", []),
            ("kilogram mole or kmol per day", "kilogram_mole_or_kmol_per_day", 0.04167, "kmol/d", []),
            ("kilogram mole or kmol per hour", "kilogram_mole_or_kmol_per_hour", 1.0, "kmol/h", []),
            ("kilogram mole or kmol per minute", "kilogram_mole_or_kmol_per_minute", 60.0, "kmol/min", []),
            ("kilogram mole or kmol per second", "kilogram_mole_or_kmol_per_second", 3600.0, "kmol/s", []),
            ("pound mole or lb-mol per day", "pound_mole_or_lb_mol_per_day", 0.0189, "lb-mol/d or mole/da", ['lb-mol/d', 'mole/da']),
            ("pound mole or lb-mol per hour", "pound_mole_or_lb_mol_per_hour", 0.4535, "lb-mol/h or mole/hr", ['lb-mol/h', 'mole/hr']),
            ("pound mole or lb-mol per minute", "pound_mole_or_lb_mol_per_minute", 27.21, "lb-mol/min or mole/ min", ['lb-mol/min', 'mole/ min']),
            ("pound mole or lb-mol per second", "pound_mole_or_lb_mol_per_second", 1633.0, "$\\mathrm{lb}-\\mathrm{mol} / \\mathrm{s}$ or mole/sec", ['lb-mol / s', 'mole/sec'])
        ],
        "field_name": "molar_flow_rate",
        "display_name": "Molar Flow Rate",
    },
    "MolarFlux": {
        "dimension": MOLAR_FLUX,
        "default_unit": "kmol_per_square_meter_per_second",
        "units": [
            ("kmol per square meter per day", "kmol_per_square_meter_per_day", 1.1574000000000001e-05, "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$", []),
            ("kmol per square meter per hour", "kmol_per_square_meter_per_hour", 0.00027778000000000004, "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$", []),
            ("kmol per square meter per minute", "kmol_per_square_meter_per_minute", 0.016667, "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2}\\right.$ amin $)$", []),
            ("kmol per square meter per second", "kmol_per_square_meter_per_second", 1.0, "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$", []),
            ("pound mole per square foot per day", "pound_mole_per_square_foot_per_day", 5.6478000000000004e-05, "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or mole/sqft/da", ['lb-mol /left(ft^{2 ~dright)', 'mole/sqft/da']),
            ("pound mole per square foot per hour", "pound_mole_per_square_foot_per_hour", 0.0013555, "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or mole/sqft/hr", ['lb-mol /left(ft^{2 ~hright)', 'mole/sqft/hr']),
            ("pound mole per square foot per minute", "pound_mole_per_square_foot_per_minute", 0.081329, "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~min}\\right)$ or mole/sqft/min", ['lb-mol /left(ft^{2 ~minright)', 'mole/sqft/min']),
            ("pound mole per square foot per second", "pound_mole_per_square_foot_per_second", 4.8797, "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or mole/sqft/sec", ['lb-mol /left(ft^{2 ~sright)', 'mole/sqft/sec'])
        ],
        "field_name": "molar_flux",
        "display_name": "Molar Flux",
    },
    "MolarHeatCapacity": {
        "dimension": MOLAR_HEAT_CAPACITY,
        "default_unit": "joule_per_gram_mole_per_kelvin_(or_degree_Celsius)",
        "units": [
            ("Btu per pound mole per degree Fahrenheit (or degree Rankine)", "Btu_per_pound_mole_per_degree_Fahrenheit_(or_degree_Rankine)", 4.1868, "Btu/lb-mol/ ${ }^{\\circ} \\mathrm{F}$", []),
            ("calories per gram mole per kelvin (or degree Celsius)", "calories_per_gram_mole_per_kelvin_(or_degree_Celsius)", 4.1868, "cal/(mol K)", []),
            ("joule per gram mole per kelvin (or degree Celsius)", "joule_per_gram_mole_per_kelvin_(or_degree_Celsius)", 1.0, "J/(mol K)", [])
        ],
        "field_name": "molar_heat_capacity",
        "display_name": "Molar Heat Capacity",
    },
    "MolarityOfI": {
        "dimension": MOLARITY_OF_I,
        "default_unit": "gram_moles_of_\"i\"_per_cubic_meter",
        "units": [
            ("gram moles of \"i\" per cubic meter", "gram_moles_of_\"i\"_per_cubic_meter", 1.0, "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{m}^{3}$ or $\\mathrm{c}_{\\mathrm{i}}$", ['mol_{i / m^{3', 'c_{i']),
            ("gram moles of \"i\" per liter", "gram_moles_of_\"i\"_per_liter", 1000.0, "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{l}$", []),
            ("kilogram moles of \"i\" per cubic meter", "kilogram_moles_of_\"i\"_per_cubic_meter", 1000.0, "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{m}^{3}$", []),
            ("kilogram moles of \"i\" per liter", "kilogram_moles_of_\"i\"_per_liter", 1000000.0, "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{l}$", []),
            ("pound moles of \"i\" per cubic foot", "pound_moles_of_\"i\"_per_cubic_foot", 77844.0, "lb $\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{ft}^{3}$ or $\\mathrm{mole}_{\\mathrm{i}} /$ cft", ['lb mol_{i / ft^{3', 'mole_{i / cft']),
            ("pound moles of \" $i$ \" per gallon (US)", "pound_moles_of_\"_$i$_\"_per_gallon_(US)", 10406.0, "lb $\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{gal}$ or $\\mathrm{mole}_{\\mathrm{i}} /$ gal", ['lb mol_{i / gal', 'mole_{i / gal'])
        ],
        "field_name": "molarity_of_i",
        "display_name": "Molarity of \"i\"",
    },
    "MoleFractionOfI": {
        "dimension": MOLE_FRACTION_OF_I,
        "default_unit": "gram_mole_of_\"i\"_per_gram_mole_total",
        "units": [
            ("gram mole of \"i\" per gram mole total", "gram_mole_of_\"i\"_per_gram_mole_total", 1.0, "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{mol}$", []),
            ("kilogram mole of \"i\" per kilogram mole total", "kilogram_mole_of_\"i\"_per_kilogram_mole_total", 1.0, "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kmol}$", []),
            ("kilomole of \"i\" per kilomole total", "kilomole_of_\"i\"_per_kilomole_total", 1.0, "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kmol}$", []),
            ("pound mole of \"i\" per pound mole total", "pound_mole_of_\"i\"_per_pound_mole_total", 1.0, "lb $\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{lb} \\mathrm{mol}$", [])
        ],
        "field_name": "mole_fraction_of_i",
        "display_name": "Mole Fraction of \"i\"",
    },
    "MomentOfInertia": {
        "dimension": MOMENT_OF_INERTIA,
        "default_unit": "kilogram_square_meter",
        "units": [
            ("gram force centimeter square second", "gram_force_centimeter_square_second", 9.8067e-05, "$\\mathrm{g}_{\\mathrm{f}} \\mathrm{cm} \\mathrm{s}^{2}$", []),
            ("gram square centimeter", "gram_square_centimeter", 1e-07, "$\\mathrm{g} \\mathrm{cm}^{2}$", []),
            ("kilogram force centimeter square second", "kilogram_force_centimeter_square_second", 0.098067, "$\\mathrm{kg}_{\\mathrm{f}} \\mathrm{cm} \\mathrm{s}{ }^{2}$", []),
            ("kilogram force meter square second", "kilogram_force_meter_square_second", 9.8067, "$\\mathrm{kg}_{\\mathrm{f}} \\mathrm{m} \\mathrm{s}^{2}$", []),
            ("kilogram square centimeter", "kilogram_square_centimeter", 0.0001, "$\\mathrm{kg} \\mathrm{cm}^{2}$", []),
            ("kilogram square meter", "kilogram_square_meter", 1.0, "$\\mathrm{kg} \\mathrm{m}^{2}$", []),
            ("ounce force inch square second", "ounce_force_inch_square_second", 0.0070616, "$\\mathrm{oz}_{\\mathrm{f}}$ in $\\mathrm{s}^{2}$", []),
            ("ounce mass square inch", "ounce_mass_square_inch", 1.8290000000000003e-05, "oz in ${ }^{2}$", []),
            ("pound mass square foot", "pound_mass_square_foot", 0.04214, "lb ft ${ }^{2}$ or lb sq ft", ['lb ft { ^{2', 'lb sq ft']),
            ("pound mass square inch", "pound_mass_square_inch", 0.00029264000000000004, "$\\mathrm{lb} \\mathrm{in}^{2}$", [])
        ],
        "field_name": "moment_of_inertia",
        "display_name": "Moment of Inertia",
    },
    "MomentumFlowRate": {
        "dimension": MOMENTUM_FLOW_RATE,
        "default_unit": "kilogram_meters_per_square_second",
        "units": [
            ("foot pounds per square hour", "foot_pounds_per_square_hour", 1.0671e-08, "$\\mathrm{ft} \\mathrm{lb} / \\mathrm{h}^{2}$ or $\\mathrm{ft} \\mathrm{lb} / \\mathrm{hr}^{2}$", ['ft lb / h^{2', 'ft lb / hr^{2']),
            ("foot pounds per square minute", "foot_pounds_per_square_minute", 3.8417e-05, "$\\mathrm{ft} \\mathrm{lb} / \\mathrm{min}^{2}$", []),
            ("foot pounds per square second", "foot_pounds_per_square_second", 0.1383, "$\\mathrm{ft} \\mathrm{lb} / \\mathrm{s}^{2}$ or ft lb/sec ${ }^{2}$", ['ft lb / s^{2', 'ft lb/sec { ^{2']),
            ("gram centimeters per square second", "gram_centimeters_per_square_second", 1e-05, "$\\mathrm{g} \\mathrm{cm} / \\mathrm{s}^{2}$", []),
            ("kilogram meters per square second", "kilogram_meters_per_square_second", 1.0, "$\\mathrm{kg} \\mathrm{m} / \\mathrm{s}^{2}$", [])
        ],
        "field_name": "momentum_flow_rate",
        "display_name": "Momentum Flow Rate",
    },
    "MomentumFlux": {
        "dimension": MOMENTUM_FLUX,
        "default_unit": "newton_per_square_meter",
        "units": [
            ("dyne per square centimeter", "dyne_per_square_centimeter", 10.0, "dyn/ $\\mathrm{cm}^{2}$", []),
            ("gram per centimeter per square second", "gram_per_centimeter_per_square_second", 10.0, "$\\mathrm{g} / \\mathrm{cm} / \\mathrm{s}^{2}$", []),
            ("newton per square meter", "newton_per_square_meter", 1.0, "$\\mathrm{N} / \\mathrm{m}^{2}$", []),
            ("pound force per square foot", "pound_force_per_square_foot", 478.8, "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{sq} \\mathrm{ft}$", []),
            ("pound mass per foot per square second", "pound_mass_per_foot_per_square_second", 14.882, "$\\mathrm{lb}_{\\mathrm{m}} / \\mathrm{ft} / \\mathrm{s}^{2}$ or $\\mathrm{lb} / \\mathrm{ft} / \\mathrm{sec}^{2}$", ['lb_{m / ft / s^{2', 'lb / ft / sec^{2'])
        ],
        "field_name": "momentum_flux",
        "display_name": "Momentum Flux",
    },
    "NormalityOfSolution": {
        "dimension": NORMALITY_OF_SOLUTION,
        "default_unit": "gram_equivalents_per_cubic_meter",
        "units": [
            ("gram equivalents per cubic meter", "gram_equivalents_per_cubic_meter", 1.0, "$\\mathrm{eq} / \\mathrm{m}^{3}$", []),
            ("gram equivalents per liter", "gram_equivalents_per_liter", 1000.0, "eq/l", []),
            ("pound equivalents per cubic foot", "pound_equivalents_per_cubic_foot", 77844.0, "$\\mathrm{lb} \\mathrm{eq} / \\mathrm{ft}^{3}$ or lb eq/cft", ['lb eq / ft^{3', 'lb eq/cft']),
            ("pound equivalents per gallon", "pound_equivalents_per_gallon", 10406.0, "lb eq/gal (US)", [])
        ],
        "field_name": "normality_of_solution",
        "display_name": "Normality of Solution",
    },
    "ParticleDensity": {
        "dimension": PARTICLE_DENSITY,
        "default_unit": "particles_per_cubic_meter",
        "units": [
            ("particles per cubic centimeter", "particles_per_cubic_centimeter", 10000.0, "part/cm ${ }^{3}$ or part/cc", ['part/cm { ^{3', 'part/cc']),
            ("particles per cubic foot", "particles_per_cubic_foot", 35.31, "part/ $\\mathrm{ft}^{3}$ or part/cft", ['part/ ft^{3', 'part/cft']),
            ("particles per cubic meter", "particles_per_cubic_meter", 1.0, "part $/ \\mathrm{m}^{3}$", []),
            ("particles per gallon (US)", "particles_per_gallon_(US)", 264.14, "part/gal", []),
            ("particles per liter", "particles_per_liter", 1000.0, "part/l", []),
            ("particles per milliliter", "particles_per_milliliter", 10000.0, "part/ml", [])
        ],
        "field_name": "particle_density",
        "display_name": "Particle Density",
    },
    "Permeability": {
        "dimension": PERMEABILITY,
        "default_unit": "square_meters",
        "units": [
            ("darcy", "darcy", 9.8692e-13, "darcy", []),
            ("square feet", "square_feet", 0.0929, "$\\mathrm{ft}^{2}$ or sq ft", ['ft^{2', 'sq ft']),
            ("square meters", "square_meters", 1.0, "$\\mathrm{m}^{2}$", [])
        ],
        "field_name": "permeability",
        "display_name": "Permeability",
    },
    "PhotonEmissionRate": {
        "dimension": PHOTON_EMISSION_RATE,
        "default_unit": "reciprocal_square_meter_second",
        "units": [
            ("rayleigh", "rayleigh", 10000000000.0, "R", ['R']),
            ("reciprocal square meter second", "reciprocal_square_meter_second", 1.0, "$1 /\\left(\\mathrm{m}^{2} \\mathrm{sec}\\right)$", [])
        ],
        "field_name": "photon_emission_rate",
        "display_name": "Photon Emission Rate",
    },
    "PowerPerUnitMass": {
        "dimension": POWER_PER_UNIT_MASS,
        "default_unit": "watt_per_kilogram",
        "units": [
            ("British thermal unit per hour per pound mass", "British_thermal_unit_per_hour_per_pound_mass", 0.64612, "Btu/h/lb or Btu/ (lb hr)", ['Btu/h/lb', 'Btu/ (lb hr)']),
            ("calorie per second per gram", "calorie_per_second_per_gram", 4186.8, "cal/s/g or cal/(g sec)", ['cal/s/g', 'cal/(g sec)']),
            ("kilocalorie per hour per kilogram", "kilocalorie_per_hour_per_kilogram", 1.163, "kcal/h/kg or kcal/ (kg hr)", ['kcal/h/kg', 'kcal/ (kg hr)']),
            ("watt per kilogram", "watt_per_kilogram", 1.0, "W/kg", [])
        ],
        "field_name": "power_per_unit_mass",
        "display_name": "Power per Unit Mass or Specific Power",
    },
    "PowerPerUnitVolume": {
        "dimension": POWER_PER_UNIT_VOLUME,
        "default_unit": "watt_per_cubic_meter",
        "units": [
            ("British thermal unit per hour per cubic foot", "British_thermal_unit_per_hour_per_cubic_foot", 10.35, "$\\mathrm{Btu} / \\mathrm{h} / \\mathrm{ft}^{3}$ or $\\mathrm{Btu} / \\mathrm{hr} /$ cft", ['Btu / h / ft^{3', 'Btu / hr / cft']),
            ("calorie per second per cubic centimeter", "calorie_per_second_per_cubic_centimeter", 4186800.0, "$\\mathrm{cal} / \\mathrm{s} / \\mathrm{cm}^{3}$ or $\\mathrm{cal} / \\mathrm{s} / \\mathrm{cc}$", ['cal / s / cm^{3', 'cal / s / cc']),
            ("Chu per hour per cubic foot", "Chu_per_hour_per_cubic_foot", 18.63, "Chu/h/ft3 or Chu/hr/ cft", ['Chu/h/ft3', 'Chu/hr/ cft']),
            ("kilocalorie per hour per cubic centimeter", "kilocalorie_per_hour_per_cubic_centimeter", 1.163, "$\\mathrm{kcal} / \\mathrm{h} / \\mathrm{cm}^{3}$ or $\\mathrm{kcal} /$ hr/cc", ['kcal / h / cm^{3', 'kcal / hr/cc']),
            ("kilocalorie per hour per cubic foot", "kilocalorie_per_hour_per_cubic_foot", 41.071, "$\\mathrm{kcal} / \\mathrm{h} / \\mathrm{ft}^{3}$ or $\\mathrm{kcal} / \\mathrm{hr} /$ cft", ['kcal / h / ft^{3', 'kcal / hr / cft']),
            ("kilocalorie per second per cubic centimeter", "kilocalorie_per_second_per_cubic_centimeter", 4186800000.0, "kcal/s/cm ${ }^{3}$ or kcal/s/ cc", ['kcal/s/cm { ^{3', 'kcal/s/ cc']),
            ("watt per cubic meter", "watt_per_cubic_meter", 1.0, "$\\mathrm{W} / \\mathrm{m}^{3}$", [])
        ],
        "field_name": "power_per_unit_volume",
        "display_name": "Power per Unit Volume or Power Density",
    },
    "PowerThermalDuty": {
        "dimension": POWER_THERMAL_DUTY,
        "default_unit": "volt_ampere",
        "units": [
            ("abwatt (emu of power)", "abwatt_(emu_of_power)", 1e-08, "emu", ['emu']),
            ("boiler horsepower", "boiler_horsepower", 9809.5, "HP (boiler)", []),
            ("British thermal unit (mean) per hour", "British_thermal_unit_(mean)_per_hour", 0.293297, "Btu (mean)/hr or Btu/hr", ['Btu (mean)/hr', 'Btu/hr']),
            ("British thermal unit (mean) per minute", "British_thermal_unit_(mean)_per_minute", 17.597833, "Btu/min or Btu (mean)/min", ['Btu/min', 'Btu (mean)/min']),
            ("British thermal unit (thermochemical) per hour", "British_thermal_unit_(thermochemical)_per_hour", 0.292875, "Btu (therm)/hr or Btu/hr", ['Btu (therm)/hr', 'Btu/hr']),
            ("British thermal unit (thermochemical) per minute", "British_thermal_unit_(thermochemical)_per_minute", 17.5725, "$\\mathrm{Btu} / \\mathrm{min}$ or Btu (therm)/min", ['Btu / min', 'Btu (therm)/min']),
            ("calorie (mean) per hour", "calorie_(mean)_per_hour", 0.00116389, "cal (mean)/hr", []),
            ("calorie (thermochemical) per hour", "calorie_(thermochemical)_per_hour", 0.00116222, "cal (therm)/hr", []),
            ("donkey", "donkey", 250.0, "donkey", []),
            ("erg per second", "erg_per_second", 1e-07, "erg/s", []),
            ("foot pondal per second", "foot_pondal_per_second", 0.04214, "ft pdl/s", []),
            ("foot pound force per hour", "foot_pound_force_per_hour", 0.00037044000000000004, "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{hr}$", []),
            ("foot pound force per minute", "foot_pound_force_per_minute", 0.022597, "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\min$", []),
            ("foot pound force per second", "foot_pound_force_per_second", 1.355818, "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{s}$", []),
            ("horsepower ( $550 \\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{s}$ )", "horsepower_(_$550_\\mathrm{ft}_\\mathrm{lb}_{\\mathrm{f}}_/_\\mathrm{s}$_)", 745.7, "HP", ['HP']),
            ("horsepower (electric)", "horsepower_(electric)", 746.0, "HP (elect)", []),
            ("horsepower (UK)", "horsepower_(UK)", 745.7, "HP (UK)", []),
            ("kcal per hour", "kcal_per_hour", 1.16389, "kcal/hr", []),
            ("kilogram force meter per second", "kilogram_force_meter_per_second", 9.80665, "$\\mathrm{kg}_{\\mathrm{f}} \\mathrm{m} / \\mathrm{s}$", []),
            ("kilowatt", "kilowatt", 1000.0, "kW", ['kW']),
            ("megawatt", "megawatt", 1000000.0, "MW", ['MW']),
            ("metric horsepower", "metric_horsepower", 735.499, "HP (metric)", []),
            ("million British thermal units per hour (petroleum)", "million_British_thermal_units_per_hour_(petroleum)", 293297.0, "MMBtu/hr", []),
            ("million kilocalorie per hour", "million_kilocalorie_per_hour", 1163890.0, "MM kcal/hr", []),
            ("prony", "prony", 98.0665, "prony", []),
            ("ton of refrigeration (US)", "ton_of_refrigeration_(US)", 3516.8, "CTR (US)", []),
            ("ton or refrigeration (UK)", "ton_or_refrigeration_(UK)", 3922.7, "CTR (UK)", []),
            ("volt-ampere", "volt_ampere", 1.0, "VA", ['VA']),
            ("water horsepower", "water_horsepower", 746.043, "HP (water)", []),
            ("watt", "watt", 1.0, "W", ['W']),
            ("watt (international, mean)", "watt_(international,_mean)", 1.00019, "W (int, mean)", []),
            ("watt (international, US)", "watt_(international,_US)", 1.000165, "watt (int, US)", []),
            ("gigawatt", "gigawatt", 1000000000.0, "GW", ['GW']),
            ("milliwatt", "milliwatt", 0.001, "mW", ['mW']),
            ("microwatt", "microwatt", 1e-06, "μW", ['μW'])
        ],
        "field_name": "power_thermal_duty",
        "display_name": "Power, Thermal Duty",
    },
    "Pressure": {
        "dimension": PRESSURE,
        "default_unit": "newton_per_square_meter",
        "units": [
            ("atmosphere, standard", "atmosphere,_standard", 101325.0, "atm", ['atm']),
            ("bar", "bar", 100000.0, "bar", ['bar']),
            ("barye", "barye", 0.1, "barye", []),
            ("dyne per square centimeter", "dyne_per_square_centimeter", 0.1, "dyn $/ \\mathrm{cm}^{2}$", []),
            ("foot of mercury ( $60{ }^{\\circ} \\mathrm{F}$ )", "foot_of_mercury_(_$60{_}^{\\circ}_\\mathrm{F}$_)", 40526.0, "ft Hg ( $60{ }^{\\circ} \\mathrm{F}$ )", []),
            ("foot of water ( $60{ }^{\\circ} \\mathrm{F}$ )", "foot_of_water_(_$60{_}^{\\circ}_\\mathrm{F}$_)", 2989.0, "ft $\\mathrm{H}_{2} \\mathrm{O}\\left(60^{\\circ} \\mathrm{F}\\right)$", []),
            ("gigapascal", "gigapascal", 1000000000.0, "GPa", ['GPa']),
            ("hectopascal", "hectopascal", 100.0, "hPa", ['hPa']),
            ("inch of mercury ( $60{ }^{\\circ} \\mathrm{F}$ )", "inch_of_mercury_(_$60{_}^{\\circ}_\\mathrm{F}$_)", 3386.4, "in $\\mathrm{Hg}\\left(60{ }^{\\circ} \\mathrm{F}\\right)$", []),
            ("inch of water ( $60{ }^{\\circ} \\mathrm{F}$ )", "inch_of_water_(_$60{_}^{\\circ}_\\mathrm{F}$_)", 248.845, "in $\\mathrm{H}_{2} \\mathrm{O}\\left(60^{\\circ} \\mathrm{F}\\right)$", []),
            ("kilogram force per square centimeter", "kilogram_force_per_square_centimeter", 98067.0, "at or $\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{cm}^{2}$", ['at', 'kg_{f / cm^{2']),
            ("kilogram force per square meter", "kilogram_force_per_square_meter", 9.80665, "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{m}^{2}$", []),
            ("kip force per square inch", "kip_force_per_square_inch", 6894800.0, "KSI or ksi or kip ${ }_{f} / \\mathrm{in}^{2}$", ['KSI', 'ksi', 'kip { _{f / in^{2']),
            ("megapascal", "megapascal", 1000000.0, "MPa", ['MPa']),
            ("meter of water ( $4^{\\circ} \\mathrm{C}$ )", "meter_of_water_(_$4^{\\circ}_\\mathrm{C}$_)", 9806.4, "$\\mathrm{m} \\mathrm{H}_{2} \\mathrm{O}\\left(4^{\\circ} \\mathrm{C}\\right)$", []),
            ("microbar", "microbar", 0.1, "$\\mu \\mathrm{bar}$", []),
            ("millibar", "millibar", 100.0, "mbar", ['mbar']),
            ("millimeter of mercury ( $4^{\\circ} \\mathrm{C}$ )", "millimeter_of_mercury_(_$4^{\\circ}_\\mathrm{C}$_)", 133.322, "$\\mathrm{mm} \\mathrm{Hg}\\left(4^{\\circ} \\mathrm{C}\\right)$", []),
            ("millimeter of water ( $4^{\\circ} \\mathrm{C}$ )", "millimeter_of_water_(_$4^{\\circ}_\\mathrm{C}$_)", 9.806375, "$\\mathrm{mm} \\mathrm{H}_{2} \\mathrm{O}\\left(4^{\\circ} \\mathrm{C}\\right)$", []),
            ("newton per square meter", "newton_per_square_meter", 1.0, "$\\mathrm{N} / \\mathrm{m}^{2}$", []),
            ("ounce force per square inch", "ounce_force_per_square_inch", 430.922, "OSI or osi or $\\mathrm{oz}_{\\mathrm{f}} / \\mathrm{in}^{2}$", ['OSI', 'osi']),
            ("pascal", "pascal", 1.0, "Pa", ['Pa']),
            ("pièze", "pièze", 1000.0, "pz", ['pz']),
            ("pound force per square foot", "pound_force_per_square_foot", 47.880259, "PSF or psf or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}^{2}$", ['psf']),
            ("pound force per square inch", "pound_force_per_square_inch", 6894.8, "PSI or psi or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{in}^{2}$", ['psi']),
            ("torr", "torr", 133.322, "torr or mm Hg ( $0{ }^{\\circ}$ C)", ['mm Hg ( 0{ ^{circ C)']),
            ("kilopascal", "kilopascal", 1000.0, "kPa", ['kPa'])
        ],
        "field_name": "pressure",
        "display_name": "Pressure",
    },
    "RadiationDoseEquivalent": {
        "dimension": RADIATION_DOSE_EQUIVALENT,
        "default_unit": "sievert",
        "units": [
            ("rem", "rem", 0.01, "rem", ['rem']),
            ("sievert", "sievert", 1.0, "Sv", ['Sv']),
            ("millisievert", "millisievert", 0.001, "mSv", ['mSv']),
            ("microsievert", "microsievert", 1e-06, "μSv", ['μSv'])
        ],
        "field_name": "radiation_dose_equivalent",
        "display_name": "Radiation Dose Equivalent",
    },
    "RadiationExposure": {
        "dimension": RADIATION_EXPOSURE,
        "default_unit": "coulomb_per_kilogram",
        "units": [
            ("coulomb per kilogram", "coulomb_per_kilogram", 1.0, "C/kg", []),
            ("D unit", "D_unit", 0.0258, "D unit", []),
            ("pastille dose (B unit)", "pastille_dose_(B_unit)", 0.129, "B unit", []),
            ("röentgen", "röentgen", 0.000258, "R", ['R'])
        ],
        "field_name": "radiation_exposure",
        "display_name": "Radiation Exposure",
    },
    "Radioactivity": {
        "dimension": RADIOACTIVITY,
        "default_unit": "becquerel",
        "units": [
            ("becquerel", "becquerel", 1.0, "Bq", ['Bq']),
            ("curie", "curie", 37000000000.0, "Ci", ['Ci']),
            ("Mache unit", "Mache_unit", 13.32, "Mache", []),
            ("rutherford", "rutherford", 1000000.0, "Rd", ['Rd']),
            ("stat", "stat", 1.34e-16, "stat", ['stat']),
            ("kilobecquerel", "kilobecquerel", 1000.0, "kBq", ['kBq']),
            ("megabecquerel", "megabecquerel", 1000000.0, "MBq", ['MBq']),
            ("gigabecquerel", "gigabecquerel", 1000000000.0, "GBq", ['GBq'])
        ],
        "field_name": "radioactivity",
        "display_name": "Radioactivity",
    },
    "SecondMomentOfArea": {
        "dimension": SECOND_MOMENT_OF_AREA,
        "default_unit": "meter_quadrupled",
        "units": [
            ("inch quadrupled", "inch_quadrupled", 4.1623e-07, "in ${ }^{4}$", []),
            ("centimeter quadrupled", "centimeter_quadrupled", 1e-08, "$\\mathrm{cm}^{4}$", []),
            ("foot quadrupled", "foot_quadrupled", 0.008631, "$\\mathrm{ft}^{4}$", []),
            ("meter quadrupled", "meter_quadrupled", 1.0, "$\\mathrm{m}^{4}$", [])
        ],
        "field_name": "second_moment_of_area",
        "display_name": "Second Moment of Area",
    },
    "SecondRadiationConstantPlanck": {
        "dimension": SECOND_RADIATION_CONSTANT_PLANCK,
        "default_unit": "meter_kelvin",
        "units": [
            ("meter kelvin", "meter_kelvin", 1.0, "m K", [])
        ],
        "field_name": "second_radiation_constant_planck",
        "display_name": "Second Radiation Constant (Planck)",
    },
    "SpecificEnthalpy": {
        "dimension": SPECIFIC_ENTHALPY,
        "default_unit": "joule_per_kilogram",
        "units": [
            ("British thermal unit (mean) per pound", "British_thermal_unit_(mean)_per_pound", 2327.8, "Btu (mean)/lb", []),
            ("British thermal unit per pound", "British_thermal_unit_per_pound", 2324.4, "Btu/lb", []),
            ("calorie per gram", "calorie_per_gram", 4186.8, "$\\mathrm{cal} / \\mathrm{g}$", []),
            ("Chu per pound", "Chu_per_pound", 4186.8, "Chu/lb", []),
            ("joule per kilogram", "joule_per_kilogram", 1.0, "J/kg", []),
            ("kilojoule per kilogram", "kilojoule_per_kilogram", 1000.0, "kJ/kg", [])
        ],
        "field_name": "specific_enthalpy",
        "display_name": "Specific Enthalpy",
    },
    "SpecificGravity": {
        "dimension": SPECIFIC_GRAVITY,
        "default_unit": "Dimensionless",
        "units": [
            ("Dimensionless", "Dimensionless", 1.0, "Dmls", ['Dmls'])
        ],
        "field_name": "specific_gravity",
        "display_name": "Specific Gravity",
    },
    "SpecificHeatCapacityConstantPressure": {
        "dimension": SPECIFIC_HEAT_CAPACITY_CONSTANT_PRESSURE,
        "default_unit": "joules_per_kilogram_per_kelvin_(or_degree_Celsius)",
        "units": [
            ("Btu per pound per degree Fahrenheit (or degree Rankine)", "Btu_per_pound_per_degree_Fahrenheit_(or_degree_Rankine)", 4186.8, "Btu/(lb ${ }^{\\circ} \\mathrm{F}$ )", []),
            ("calories per gram per kelvin (or degree Celsius)", "calories_per_gram_per_kelvin_(or_degree_Celsius)", 4186.8, "cal/(g K)", []),
            ("joules per kilogram per kelvin (or degree Celsius)", "joules_per_kilogram_per_kelvin_(or_degree_Celsius)", 1.0, "J/(kg K)", [])
        ],
        "field_name": "specific_heat_capacity_constant_pressure",
        "display_name": "Specific Heat Capacity (Constant Pressure)",
    },
    "SpecificLength": {
        "dimension": SPECIFIC_LENGTH,
        "default_unit": "meters_per_kilogram",
        "units": [
            ("centimeter per gram", "centimeter_per_gram", 10.0, "cm/g", []),
            ("cotton count", "cotton_count", 590500000.0, "cc", ['cc']),
            ("ft per pound", "ft_per_pound", 0.67192, "ft/lb", []),
            ("meters per kilogram", "meters_per_kilogram", 1.0, "m/kg", []),
            ("newton meter", "newton_meter", 1000.0, "Nm", ['Nm']),
            ("worsted", "worsted", 888679999.9999999, "worsted", [])
        ],
        "field_name": "specific_length",
        "display_name": "Specific Length",
    },
    "SpecificSurface": {
        "dimension": SPECIFIC_SURFACE,
        "default_unit": "square_meter_per_kilogram",
        "units": [
            ("square centimeter per gram", "square_centimeter_per_gram", 0.1, "$\\mathrm{cm}^{2} / \\mathrm{g}$", []),
            ("square foot per kilogram", "square_foot_per_kilogram", 0.092903, "$\\mathrm{ft}^{2} / \\mathrm{kg}$ or sq ft/kg", ['ft^{2 / kg', 'sq ft/kg']),
            ("square foot per pound", "square_foot_per_pound", 0.20482, "$\\mathrm{ft}^{2} / \\mathrm{lb}$ or sq ft/lb", ['ft^{2 / lb', 'sq ft/lb']),
            ("square meter per gram", "square_meter_per_gram", 1000.0, "$\\mathrm{m}^{2} / \\mathrm{g}$", []),
            ("square meter per kilogram", "square_meter_per_kilogram", 1.0, "$\\mathrm{m}^{2} / \\mathrm{kg}$", [])
        ],
        "field_name": "specific_surface",
        "display_name": "Specific Surface",
    },
    "SpecificVolume": {
        "dimension": SPECIFIC_VOLUME,
        "default_unit": "cubic_meter_per_kilogram",
        "units": [
            ("cubic centimeter per gram", "cubic_centimeter_per_gram", 0.001, "$\\mathrm{cm}^{3} / \\mathrm{g}$ or $\\mathrm{cc} / \\mathrm{g}$", ['cm^{3 / g', 'cc / g']),
            ("cubic foot per kilogram", "cubic_foot_per_kilogram", 0.028317, "$\\mathrm{ft}^{3} / \\mathrm{kg}$ or $\\mathrm{cft} / \\mathrm{kg}$", ['ft^{3 / kg', 'cft / kg']),
            ("cubic foot per pound", "cubic_foot_per_pound", 0.062428, "$\\mathrm{ft}^{3} / \\mathrm{lb}$ or $\\mathrm{cft} / \\mathrm{lb}$", ['ft^{3 / lb', 'cft / lb']),
            ("cubic meter per kilogram", "cubic_meter_per_kilogram", 1.0, "$\\mathrm{m}^{3} / \\mathrm{kg}$", [])
        ],
        "field_name": "specific_volume",
        "display_name": "Specific Volume",
    },
    "Stress": {
        "dimension": STRESS,
        "default_unit": "newton_per_square_meter",
        "units": [
            ("dyne per square centimeter", "dyne_per_square_centimeter", 0.1, "dyn/ $\\mathrm{cm}^{2}$", []),
            ("gigapascal", "gigapascal", 1000000000.0, "GPa", ['GPa']),
            ("hectopascal", "hectopascal", 100.0, "hPa", ['hPa']),
            ("kilogram force per square centimeter", "kilogram_force_per_square_centimeter", 98067.0, "at or $\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{cm}^{2}$", ['at', 'kg_{f / cm^{2']),
            ("kilogram force per square meter", "kilogram_force_per_square_meter", 9.80665, "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{m}^{2}$", []),
            ("kip force per square inch", "kip_force_per_square_inch", 6894800.0, "KSI or ksi or kip ${ }_{f} / \\mathrm{in}^{2}$", ['KSI', 'ksi', 'kip { _{f / in^{2']),
            ("megapascal", "megapascal", 1000000.0, "MPa", ['MPa']),
            ("newton per square meter", "newton_per_square_meter", 1.0, "$\\mathrm{N} / \\mathrm{m}^{2}$", []),
            ("ounce force per square inch", "ounce_force_per_square_inch", 430.922, "OSI or osi or $\\mathrm{oz}_{\\mathrm{f}} / \\mathrm{in}^{2}$", ['OSI', 'osi', 'oz_{f / in^{2']),
            ("pascal", "pascal", 1.0, "Pa", ['Pa']),
            ("pound force per square foot", "pound_force_per_square_foot", 47.880259, "PSF or psf or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}^{2}$", ['PSF', 'psf', 'lb_{f / ft^{2']),
            ("pound force per square inch", "pound_force_per_square_inch", 6894.8, "PSI or psi or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{in}^{2}$", ['psi'])
        ],
        "field_name": "stress",
        "display_name": "Stress",
    },
    "SurfaceMassDensity": {
        "dimension": SURFACE_MASS_DENSITY,
        "default_unit": "kilogram_per_square_meter",
        "units": [
            ("gram per square centimeter", "gram_per_square_centimeter", 10.0, "$\\mathrm{kg} / \\mathrm{cm}^{2}$", []),
            ("gram per square meter", "gram_per_square_meter", 0.001, "$\\mathrm{g} / \\mathrm{m}^{2}$", []),
            ("kilogram per square meter", "kilogram_per_square_meter", 1.0, "$\\mathrm{kg} / \\mathrm{m}^{2}$", []),
            ("pound (mass) per square foot", "pound_(mass)_per_square_foot", 4.882427, "$\\mathrm{lb} / \\mathrm{ft}^{2}$", []),
            ("pound (mass) per square inch", "pound_(mass)_per_square_inch", 703.07, "$\\mathrm{lb} / \\mathrm{in}^{2}$", [])
        ],
        "field_name": "surface_mass_density",
        "display_name": "Surface Mass Density",
    },
    "SurfaceTension": {
        "dimension": SURFACE_TENSION,
        "default_unit": "newton_per_meter",
        "units": [
            ("dyne per centimeter", "dyne_per_centimeter", 0.001, "dyn/cm", []),
            ("gram force per centimeter", "gram_force_per_centimeter", 0.0102, "$\\mathrm{g}_{\\mathrm{f}} / \\mathrm{cm}$", []),
            ("newton per meter", "newton_per_meter", 1.0, "N/m", []),
            ("pound force per foot", "pound_force_per_foot", 14.594, "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}$", []),
            ("pound force per inch", "pound_force_per_inch", 175.13, "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{in}$", [])
        ],
        "field_name": "surface_tension",
        "display_name": "Surface Tension",
    },
    "Temperature": {
        "dimension": TEMPERATURE,
        "default_unit": "degree_Celsius_(unit_size)",
        "units": [
            ("degree Celsius (unit size)", "degree_Celsius_(unit_size)", 1.0, "$\\mathrm{C}^{\\circ}$", []),
            ("degree Fahrenheit (unit size)", "degree_Fahrenheit_(unit_size)", 0.555556, "$\\mathrm{F}^{\\circ}$", []),
            ("degree Réaumur (unit size)", "degree_Réaumur_(unit_size)", 1.25, "Ré ${ }^{\\circ}$", []),
            ("kelvin (absolute scale)", "kelvin_(absolute_scale)", 1.0, "K", ['K']),
            ("Rankine (absolute scale)", "Rankine_(absolute_scale)", 0.555556, "${ }^{\\circ} \\mathrm{R}$", [])
        ],
        "field_name": "temperature",
        "display_name": "Temperature",
    },
    "ThermalConductivity": {
        "dimension": THERMAL_CONDUCTIVITY,
        "default_unit": "watt_per_centimeter_per_kelvin",
        "units": [
            ("Btu (IT) per inch per hour per degree Fahrenheit", "Btu_(IT)_per_inch_per_hour_per_degree_Fahrenheit", 0.207688, "Btu (IT)/(in hr ${ }^{\\circ} \\mathrm{F}$ )", []),
            ("Btu (therm) per foot per hour per degree Fahrenheit", "Btu_(therm)_per_foot_per_hour_per_degree_Fahrenheit", 0.017296, "$\\mathrm{Btu} /\\left(\\mathrm{ft} \\mathrm{hr}{ }^{\\circ} \\mathrm{F}\\right)$", []),
            ("Btu (therm) per inch per hour per degree Fahrenheit", "Btu_(therm)_per_inch_per_hour_per_degree_Fahrenheit", 0.207549, "Btu/(in hr ${ }^{\\circ} \\mathrm{F}$ )", []),
            ("calorie (therm) per centimeter per second per degree Celsius", "calorie_(therm)_per_centimeter_per_second_per_degree_Celsius", 4.184, "$\\operatorname{cal}(\\mathrm{IT}) /\\left(\\mathrm{cm} \\mathrm{s}^{\\circ} \\mathrm{C}\\right)$", []),
            ("joule per second per centimeter per kelvin", "joule_per_second_per_centimeter_per_kelvin", 0.01, "J/(cm s K)", []),
            ("watt per centimeter per kelvin", "watt_per_centimeter_per_kelvin", 1.0, "W/(cm K)", []),
            ("watt per meter per kelvin", "watt_per_meter_per_kelvin", 0.01, "W/(m K)", [])
        ],
        "field_name": "thermal_conductivity",
        "display_name": "Thermal Conductivity",
    },
    "Time": {
        "dimension": TIME,
        "default_unit": "second",
        "units": [
            ("blink", "blink", 0.864, "blink", []),
            ("century", "century", 3155800000.0, "-", []),
            ("chronon or tempon", "chronon_or_tempon", 1e-23, "-", []),
            ("gigan or eon", "gigan_or_eon", 3.1558e+16, "Ga or eon", ['Ga', 'eon']),
            ("hour", "hour", 3600.0, "h or hr", ['h', 'hr']),
            ("Julian year", "Julian_year", 31557000.0, "a (jul) or yr", ['a (jul)', 'yr']),
            ("mean solar day", "mean_solar_day", 86400.0, "da or d", ['da', 'd']),
            ("millenium", "millenium", 31558000000.0, "-", []),
            ("minute", "minute", 60.0, "min", ['min']),
            ("second", "second", 1.0, "s", ['s']),
            ("shake", "shake", 1e-08, "shake", []),
            ("sidereal year (1900 AD)", "sidereal_year_(1900_AD)", 31551999.999999996, "a (sider) or yr", ['a (sider)', 'yr']),
            ("tropical year", "tropical_year", 31557000.0, "a (trop)", []),
            ("wink", "wink", 3.33333e-12, "wink", ['wink']),
            ("year", "year", 31558000.0, "a or y or yr", ['a', 'y', 'yr']),
            ("millisecond", "millisecond", 0.001, "ms", ['ms']),
            ("microsecond", "microsecond", 1e-06, "μs", ['μs']),
            ("nanosecond", "nanosecond", 1e-09, "ns", ['ns']),
            ("picosecond", "picosecond", 1e-12, "ps", ['ps'])
        ],
        "field_name": "time",
        "display_name": "Time",
    },
    "Torque": {
        "dimension": TORQUE,
        "default_unit": "newton_meter",
        "units": [
            ("centimeter kilogram force", "centimeter_kilogram_force", 0.098067, "cm kg ${ }_{\\mathrm{f}}$", []),
            ("dyne centimeter", "dyne_centimeter", 1e-07, "dyn cm", []),
            ("foot kilogram force", "foot_kilogram_force", 2.9891, "$\\mathrm{ft} \\mathrm{kg}_{\\mathrm{f}}$", []),
            ("foot pound force", "foot_pound_force", 1.3558, "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}}$", []),
            ("foot poundal", "foot_poundal", 0.04214, "ft pdl", []),
            ("in pound force", "in_pound_force", 0.11298, "in $\\mathrm{lb}_{\\mathrm{f}}$", []),
            ("inch ounce force", "inch_ounce_force", 0.0070616, "in $\\mathrm{OZ}_{\\mathrm{f}}$", []),
            ("meter kilogram force", "meter_kilogram_force", 9.8067, "$\\mathrm{m} \\mathrm{kg}_{\\mathrm{f}}$", []),
            ("newton centimeter", "newton_centimeter", 0.01, "N cm", []),
            ("newton meter", "newton_meter", 1.0, "N m", [])
        ],
        "field_name": "torque",
        "display_name": "Torque",
    },
    "TurbulenceEnergyDissipationRate": {
        "dimension": TURBULENCE_ENERGY_DISSIPATION_RATE,
        "default_unit": "square_meter_per_cubic_second",
        "units": [
            ("square foot per cubic second", "square_foot_per_cubic_second", 0.0929, "$\\mathrm{ft}^{2} / \\mathrm{s}^{3}$ or sq ft/sec ${ }^{3}$", ['ft^{2 / s^{3', 'sq ft/sec { ^{3']),
            ("square meter per cubic second", "square_meter_per_cubic_second", 1.0, "$\\mathrm{m}^{2} / \\mathrm{s}^{3}$", [])
        ],
        "field_name": "turbulence_energy_dissipation_rate",
        "display_name": "Turbulence Energy Dissipation Rate",
    },
    "VelocityAngular": {
        "dimension": VELOCITY_ANGULAR,
        "default_unit": "radian_per_second",
        "units": [
            ("degree per minute", "degree_per_minute", 0.000290888, "deg/min or ${ }^{\\circ} / \\mathrm{min}$", ['deg/min', '{ ^{circ / min']),
            ("degree per second", "degree_per_second", 0.0174533, "deg/s or ${ }^{\\circ}$ /s", ['deg/s', '{ ^{circ /s']),
            ("grade per minute", "grade_per_minute", 0.000261799, "gon/min or grad/min", ['gon/min', 'grad/min']),
            ("radian per minute", "radian_per_minute", 0.016667, "$\\mathrm{rad} / \\mathrm{min}$", []),
            ("radian per second", "radian_per_second", 1.0, "$\\mathrm{rad} / \\mathrm{s}$", []),
            ("revolution per minute", "revolution_per_minute", 0.010472, "rev/m or rpm", ['rev/m', 'rpm']),
            ("revolution per second", "revolution_per_second", 6.283185, "rev/s or rps", ['rev/s', 'rps']),
            ("turn per minute", "turn_per_minute", 0.010472, "tr/min", [])
        ],
        "field_name": "velocity_angular",
        "display_name": "Velocity, Angular",
    },
    "VelocityLinear": {
        "dimension": VELOCITY_LINEAR,
        "default_unit": "meter_per_second",
        "units": [
            ("foot per hour", "foot_per_hour", 8.4667e-05, "ft/h or ft/hr or fph", ['ft/h', 'ft/hr', 'fph']),
            ("foot per minute", "foot_per_minute", 0.00508, "ft/min or fpm", ['ft/min', 'fpm']),
            ("foot per second", "foot_per_second", 0.3048, "ft/s or fps", ['ft/s', 'fps']),
            ("inch per second", "inch_per_second", 0.0254, "in/s or ips", ['in/s', 'ips']),
            ("international knot", "international_knot", 0.0514444, "knot", ['knot']),
            ("kilometer per hour", "kilometer_per_hour", 0.027778, "km/h ot kph", []),
            ("kilometer per second", "kilometer_per_second", 1000.0, "km/s", []),
            ("meter per second", "meter_per_second", 1.0, "$\\mathrm{m} / \\mathrm{s}$", []),
            ("mile per hour", "mile_per_hour", 0.0444704, "$\\mathrm{mi} / \\mathrm{h}$ or $\\mathrm{mi} / \\mathrm{hr}$ or mph", ['mi / h', 'mi / hr', 'mph'])
        ],
        "field_name": "velocity_linear",
        "display_name": "Velocity, Linear",
    },
    "ViscosityDynamic": {
        "dimension": VISCOSITY_DYNAMIC,
        "default_unit": "dyne_second_per_square_centimeter",
        "units": [
            ("centipoise", "centipoise", 0.01, "cP or cPo", ['cP', 'cPo']),
            ("dyne second per square centimeter", "dyne_second_per_square_centimeter", 1.0, "dyn s/ $\\mathrm{cm}^{2}$", []),
            ("kilopound second per square meter", "kilopound_second_per_square_meter", 98.0665, "kip $\\mathrm{s} / \\mathrm{m}^{2}$", []),
            ("millipoise", "millipoise", 0.001, "mP or mPo", ['mP', 'mPo']),
            ("newton second per square meter", "newton_second_per_square_meter", 10.0, "$\\mathrm{N} \\mathrm{s} / \\mathrm{m}^{2}$", []),
            ("pascal second", "pascal_second", 10.0, "Pa s or PI", ['Pa s', 'PI']),
            ("poise", "poise", 1.0, "P or Po", ['P', 'Po']),
            ("pound force hour per square foot", "pound_force_hour_per_square_foot", 1723690.0, "$\\mathrm{lb}_{\\mathrm{f}} \\mathrm{h} / \\mathrm{ft}^{2}$ or $\\mathrm{lb} \\mathrm{hr} / \\mathrm{sq}$ ft", ['lb_{f h / ft^{2', 'lb hr / sq ft']),
            ("pound force second per square foot", "pound_force_second_per_square_foot", 478.803, "$\\mathrm{lb}_{\\mathrm{f}} \\mathrm{s} / \\mathrm{ft}^{2}$ or $\\mathrm{lb} \\mathrm{sec} / \\mathrm{sq}$ ft", ['lb_{f s / ft^{2', 'lb sec / sq ft'])
        ],
        "field_name": "viscosity_dynamic",
        "display_name": "Viscosity, Dynamic",
    },
    "ViscosityKinematic": {
        "dimension": VISCOSITY_KINEMATIC,
        "default_unit": "square_meters_per_second",
        "units": [
            ("centistokes", "centistokes", 1e-06, "cSt", ['cSt']),
            ("millistokes", "millistokes", 1e-07, "mSt", ['mSt']),
            ("square centimeter per second", "square_centimeter_per_second", 0.0001, "$\\mathrm{cm}^{2} / \\mathrm{s}$", []),
            ("square foot per hour", "square_foot_per_hour", 2.58064e-05, "$\\mathrm{ft}^{2} / \\mathrm{h}$ or $\\mathrm{ft}^{2} / \\mathrm{hr}$", ['ft^{2 / h', 'ft^{2 / hr']),
            ("square foot per second", "square_foot_per_second", 0.092903, "$\\mathrm{ft}^{2} / \\mathrm{s}$", []),
            ("square meters per second", "square_meters_per_second", 1.0, "$\\mathrm{m}^{2} / \\mathrm{s}$", []),
            ("stokes", "stokes", 0.0001, "St", ['St'])
        ],
        "field_name": "viscosity_kinematic",
        "display_name": "Viscosity, Kinematic",
    },
    "Volume": {
        "dimension": VOLUME,
        "default_unit": "cubic_meter",
        "units": [
            ("acre foot", "acre_foot", 1233.48, "ac-ft", []),
            ("acre inch", "acre_inch", 102.79, "ac-in", []),
            ("barrel (US Liquid)", "barrel_(US_Liquid)", 0.1192405, "bbl (US liq)", []),
            ("barrel (US, Petro)", "barrel_(US,_Petro)", 0.158987, "bbl", ['bbl']),
            ("board foot measure", "board_foot_measure", 0.00235974, "BM or fbm", ['BM', 'fbm']),
            ("bushel (US Dry)", "bushel_(US_Dry)", 0.0352391, "bu (US dry)", []),
            ("centiliter", "centiliter", 1e-05, "cl or cL", ['cl', 'cL']),
            ("cord", "cord", 3.62456, "cord or cd", ['cd']),
            ("cord foot", "cord_foot", 0.4530695, "cord-ft", []),
            ("cubic centimeter", "cubic_centimeter", 1e-06, "$\\mathrm{cm}^{3}$ or cc", ['cm^{3', 'cc']),
            ("cubic decameter", "cubic_decameter", 1000.0, "dam ${ }^{3}$", []),
            ("cubic decimeter", "cubic_decimeter", 0.001, "$\\mathrm{dm}^{3}$", []),
            ("cubic foot", "cubic_foot", 0.0283168, "cu ft or ft ${ }^{3}$", ['cu ft', 'ft { ^{3']),
            ("cubic inch", "cubic_inch", 1.63871e-05, "cu in or $\\mathrm{in}^{3}$", ['cu in', 'in^{3']),
            ("cubic kilometer", "cubic_kilometer", 1000000000.0, "$\\mathrm{km}^{3}$", []),
            ("cubic meter", "cubic_meter", 1.0, "$\\mathrm{m}^{3}$", []),
            ("cubic micrometer", "cubic_micrometer", 1e-18, "$\\mu \\mathrm{m}^{3}$", []),
            ("cubic mile (US, Intl)", "cubic_mile_(US,_Intl)", 4168180000.0000005, "cu mi", []),
            ("cubic millimeter", "cubic_millimeter", 1e-09, "$\\mathrm{mm}^{3}$", []),
            ("cubic yard", "cubic_yard", 0.7645549, "cu yd or $\\mathrm{yd}^{3}$", ['cu yd', 'yd^{3']),
            ("decastére", "decastére", 10.0, "dast", ['dast']),
            ("deciliter", "deciliter", 0.0001, "dl or dL", ['dl', 'dL']),
            ("fluid drachm (UK)", "fluid_drachm_(UK)", 3.5516299999999996e-06, "fl dr (UK)", []),
            ("fluid dram (US)", "fluid_dram_(US)", 3.69669e-06, "fl dr (US liq)", []),
            ("fluid ounce (US)", "fluid_ounce_(US)", 2.95735e-05, "fl oz", []),
            ("gallon (Imperial UK)", "gallon_(Imperial_UK)", 0.00454609, "gal (UK) or Imp gal", ['gal (UK)', 'Imp gal']),
            ("gallon (US Dry)", "gallon_(US_Dry)", 0.004404884, "gal (US dry)", []),
            ("gallon (US Liquid)", "gallon_(US_Liquid)", 0.003785412, "gal", ['gal']),
            ("last", "last", 2.9095, "last", ['last']),
            ("liter", "liter", 0.001, "1 or L", ['1', 'L']),
            ("microliter", "microliter", 1e-09, "$\\mu \\mathrm{l}$ or $\\mu \\mathrm{L}$", ['mu l', 'mu L']),
            ("milliliter", "milliliter", 1e-06, "ml", ['ml']),
            ("Mohr centicube", "Mohr_centicube", 1.00238e-06, "cc", ['cc']),
            ("pint (UK)", "pint_(UK)", 0.000568262, "pt (UK)", []),
            ("pint (US Dry)", "pint_(US_Dry)", 0.000550611, "pt (US dry)", []),
            ("pint (US Liquid)", "pint_(US_Liquid)", 0.000473176, "pt", ['pt']),
            ("quart (US Dry)", "quart_(US_Dry)", 0.00110122, "qt (US dry)", []),
            ("stére", "stére", 1.0, "st", ['st']),
            ("tablespoon (Metric)", "tablespoon_(Metric)", 1.5000000000000002e-05, "tbsp (Metric)", []),
            ("tablespoon (US)", "tablespoon_(US)", 1.47868e-05, "tbsp", ['tbsp']),
            ("teaspoon (US)", "teaspoon_(US)", 4.928919999999999e-06, "tsp", ['tsp'])
        ],
        "field_name": "volume",
        "display_name": "Volume",
    },
    "VolumeFractionOfI": {
        "dimension": VOLUME_FRACTION_OF_I,
        "default_unit": "cubic_foot_of_\"i\"_per_cubic_foot_total",
        "units": [
            ("cubic centimeters of \"i\" per cubic meter total", "cubic_centimeters_of_\"i\"_per_cubic_meter_total", 0.0001, "$\\mathrm{cm}_{\\mathrm{i}}^{3} / \\mathrm{m}^{3}$ or $\\mathrm{cc}_{\\mathrm{i}} / \\mathrm{m}^{3}$", ['cm_{i^{3 / m^{3', 'cc_{i / m^{3']),
            ("cubic foot of \"i\" per cubic foot total", "cubic_foot_of_\"i\"_per_cubic_foot_total", 1.0, "$\\mathrm{ft}_{\\mathrm{i}}^{3} / \\mathrm{ft}^{3}$ or $\\mathrm{cft}_{\\mathrm{i}} / \\mathrm{cft}$", ['ft_{i^{3 / ft^{3', 'cft_{i / cft']),
            ("cubic meters of \" i \" per cubic meter total", "cubic_meters_of_\"_i_\"_per_cubic_meter_total", 1.0, "$\\mathrm{m}_{\\mathrm{i}}{ }^{3} / \\mathrm{m}^{3}$", []),
            ("gallons of \"i\" per gallon total", "gallons_of_\"i\"_per_gallon_total", 1.0, "$\\mathrm{gal}_{\\mathrm{i}} / \\mathrm{gal}$", [])
        ],
        "field_name": "volume_fraction_of_i",
        "display_name": "Volume Fraction of \"i\"",
    },
    "VolumetricCalorificHeatingValue": {
        "dimension": VOLUMETRIC_CALORIFIC_HEATING_VALUE,
        "default_unit": "joule_per_cubic_meter",
        "units": [
            ("British thermal unit per cubic foot", "British_thermal_unit_per_cubic_foot", 37260.0, "$\\mathrm{Btu} / \\mathrm{ft}^{3}$ or Btu/cft", ['Btu / ft^{3', 'Btu/cft']),
            ("British thermal unit per gallon (UK)", "British_thermal_unit_per_gallon_(UK)", 232090.0, "Btu/gal (UK)", []),
            ("British thermal unit per gallon (US)", "British_thermal_unit_per_gallon_(US)", 193260.0, "Btu/gal (US)", []),
            ("calorie per cubic centimeter", "calorie_per_cubic_centimeter", 4186800.0, "$\\mathrm{cal} / \\mathrm{cm}^{3}$ or $\\mathrm{cal} / \\mathrm{cc}$", ['cal / cm^{3', 'cal / cc']),
            ("Chu per cubic foot", "Chu_per_cubic_foot", 67067.0, "$\\mathrm{Chu} / \\mathrm{ft}^{3}$ or $\\mathrm{Chu} / \\mathrm{cft}$", ['Chu / ft^{3', 'Chu / cft']),
            ("joule per cubic meter", "joule_per_cubic_meter", 1.0, "$\\mathrm{J} / \\mathrm{m}^{3}$", []),
            ("kilocalorie per cubic foot", "kilocalorie_per_cubic_foot", 147860.0, "$\\mathrm{kcal} / \\mathrm{ft}^{3}$ or $\\mathrm{kcal} / \\mathrm{cft}$", ['kcal / ft^{3', 'kcal / cft']),
            ("kilocalorie per cubic meter", "kilocalorie_per_cubic_meter", 4186.8, "$\\mathrm{kcal} / \\mathrm{m}^{3}$", []),
            ("therm ( 100 K Btu ) per cubic foot", "therm_(_100_K_Btu_)_per_cubic_foot", 3726000000.0, "thm/cft", [])
        ],
        "field_name": "volumetric_calorific_heating_value",
        "display_name": "Volumetric Calorific (Heating) Value",
    },
    "VolumetricCoefficientOfExpansion": {
        "dimension": VOLUMETRIC_COEFFICIENT_OF_EXPANSION,
        "default_unit": "kilogram_per_cubic_meter_per_kelvin_(or_degree_Celsius)",
        "units": [
            ("gram per cubic centimeter per kelvin (or degree Celsius)", "gram_per_cubic_centimeter_per_kelvin_(or_degree_Celsius)", 1000.0, "$\\mathrm{g} / \\mathrm{cm}^{3} / \\mathrm{K}$ or g/cc/ ${ }^{\\circ} \\mathrm{C}$", ['g / cm^{3 / K', 'g/cc/ { ^{circ C']),
            ("kilogram per cubic meter per kelvin (or degree Celsius)", "kilogram_per_cubic_meter_per_kelvin_(or_degree_Celsius)", 1.0, "$\\mathrm{kg} / \\mathrm{m}^{3} / \\mathrm{K}$ or $\\mathrm{kg} / \\mathrm{m}^{3} /{ }^{\\circ}$ C", ['kg / m^{3 / K', 'kg / m^{3 /{ ^{circ C']),
            ("pound per cubic foot per degree Fahrenheit (or degree Rankine)", "pound_per_cubic_foot_per_degree_Fahrenheit_(or_degree_Rankine)", 28.833, "$\\mathrm{lb} / \\mathrm{ft}^{3} /{ }^{\\circ} \\mathrm{R}$ or $\\mathrm{lb} / \\mathrm{cft} /{ }^{\\circ} \\mathrm{F}$", ['lb / ft^{3 /{ ^{circ R', 'lb / cft /{ ^{circ F']),
            ("pound per cubic foot per kelvin (or degree Celsius)", "pound_per_cubic_foot_per_kelvin_(or_degree_Celsius)", 16.018, "$\\mathrm{lb} / \\mathrm{ft}^{3} / \\mathrm{K}$ or $\\mathrm{lb} / \\mathrm{cft} /{ }^{\\circ} \\mathrm{C}$", ['lb / ft^{3 / K', 'lb / cft /{ ^{circ C'])
        ],
        "field_name": "volumetric_coefficient_of_expansion",
        "display_name": "Volumetric Coefficient of Expansion",
    },
    "VolumetricFlowRate": {
        "dimension": VOLUMETRIC_FLOW_RATE,
        "default_unit": "cubic_meters_per_second",
        "units": [
            ("cubic feet per day", "cubic_feet_per_day", 3.2778e-07, "$\\mathrm{ft}^{3} / \\mathrm{d}$ or $\\mathrm{cft} / \\mathrm{da}$ or cfd", ['ft^{3 / d', 'cft / da', 'cfd']),
            ("cubic feet per hour", "cubic_feet_per_hour", 7.866699999999999e-06, "$\\mathrm{ft}^{3} / \\mathrm{h}$ or $\\mathrm{cft} / \\mathrm{hr}$ or cfh", ['ft^{3 / h', 'cft / hr', 'cfh']),
            ("cubic feet per minute", "cubic_feet_per_minute", 0.000472, "$\\mathrm{ft}^{3} / \\mathrm{min}$ or $\\mathrm{cft} / \\mathrm{min}$ or cfm", ['ft^{3 / min', 'cft / min', 'cfm']),
            ("cubic feet per second", "cubic_feet_per_second", 0.02832, "$\\mathrm{ft}^{3} / \\mathrm{s}$ or cft/sec or cfs", ['ft^{3 / s', 'cft/sec', 'cfs']),
            ("cubic meters per day", "cubic_meters_per_day", 1.1574000000000001e-05, "$\\mathrm{m}^{3} / \\mathrm{d}$", []),
            ("cubic meters per hour", "cubic_meters_per_hour", 0.00027778, "$\\mathrm{m}^{3} / \\mathrm{h}$", []),
            ("cubic meters per minute", "cubic_meters_per_minute", 0.016667, "$\\mathrm{m}^{3} / \\min$", []),
            ("cubic meters per second", "cubic_meters_per_second", 1.0, "$\\mathrm{m}^{3} / \\mathrm{s}$", []),
            ("gallons per day", "gallons_per_day", 0.002628, "gal/d or gpd or gal/ da", ['gal/d', 'gpd', 'gal/ da']),
            ("gallons per hour", "gallons_per_hour", 0.06308, "gal/h or gph or gal/ hr", ['gal/h', 'gph', 'gal/ hr']),
            ("gallons per minute", "gallons_per_minute", 3.785, "gal/min or gpm", ['gal/min', 'gpm']),
            ("gallons per second", "gallons_per_second", 227.1, "gal/s or gps or gal/ sec", ['gal/s', 'gps', 'gal/ sec']),
            ("liters per day", "liters_per_day", 0.00069444, "1/d", []),
            ("liters per hour", "liters_per_hour", 0.016667, "1/h", []),
            ("liters per minute", "liters_per_minute", 1.0, "$1 / \\mathrm{min}$", []),
            ("liters per second", "liters_per_second", 60.0, "1/s", [])
        ],
        "field_name": "volumetric_flow_rate",
        "display_name": "Volumetric Flow Rate",
    },
    "VolumetricFlux": {
        "dimension": VOLUMETRIC_FLUX,
        "default_unit": "cubic_meters_per_square_meter_per_second",
        "units": [
            ("cubic feet per square foot per day", "cubic_feet_per_square_foot_per_day", 3.5276e-06, "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or $\\mathrm{cft} / \\mathrm{sqft} /$ da", ['ft^{3 /left(ft^{2 ~dright)', 'cft / sqft / da']),
            ("cubic feet per square foot per hour", "cubic_feet_per_square_foot_per_hour", 8.466300000000001e-05, "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or $\\mathrm{cft} / \\mathrm{sqft} /$ hr", ['ft^{3 /left(ft^{2 ~hright)', 'cft / sqft / hr']),
            ("cubic feet per square foot per minute", "cubic_feet_per_square_foot_per_minute", 0.0050798, "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\min \\right)$ or $\\mathrm{cft} /$ sqft/min", ['ft^{3 /left(ft^{2 min right)', 'cft / sqft/min']),
            ("cubic feet per square foot per second", "cubic_feet_per_square_foot_per_second", 0.30479, "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or cft/sqft/ sec", ['ft^{3 /left(ft^{2 ~sright)', 'cft/sqft/ sec']),
            ("cubic meters per square meter per day", "cubic_meters_per_square_meter_per_day", 1.1574000000000001e-05, "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$", []),
            ("cubic meters per square meter per hour", "cubic_meters_per_square_meter_per_hour", 0.00027778, "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$", []),
            ("cubic meters per square meter per minute", "cubic_meters_per_square_meter_per_minute", 0.016667, "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~min}\\right)$", []),
            ("cubic meters per square meter per second", "cubic_meters_per_square_meter_per_second", 1.0, "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$", []),
            ("gallons per square foot per day", "gallons_per_square_foot_per_day", 0.00047138000000000003, "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or gal/ sqft/da", ['gal /left(ft^{2 ~dright)', 'gal/ sqft/da']),
            ("gallons per square foot per hour", "gallons_per_square_foot_per_hour", 0.011313, "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or gal/ sqft/hr", ['gal /left(ft^{2 ~hright)', 'gal/ sqft/hr']),
            ("gallons per square foot per minute", "gallons_per_square_foot_per_minute", 0.67878, "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~min}\\right)$ or gal/ sqft/min or gpm/sqft", ['gal /left(ft^{2 ~minright)', 'gal/ sqft/min', 'gpm/sqft']),
            ("gallons per square foot per second", "gallons_per_square_foot_per_second", 40.727, "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or gal/ $\\mathrm{sqft} / \\mathrm{sec}$", ['gal /left(ft^{2 ~sright)', 'gal/ sqft / sec']),
            ("liters per square meter per day", "liters_per_square_meter_per_day", 1.1574000000000001e-05, "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$", []),
            ("liters per square meter per hour", "liters_per_square_meter_per_hour", 0.00027778, "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$", []),
            ("liters per square meter per minute", "liters_per_square_meter_per_minute", 0.016667, "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~min}\\right)$", []),
            ("liters per square meter per second", "liters_per_square_meter_per_second", 1.0, "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$", [])
        ],
        "field_name": "volumetric_flux",
        "display_name": "Volumetric Flux",
    },
    "VolumetricMassFlowRate": {
        "dimension": VOLUMETRIC_MASS_FLOW_RATE,
        "default_unit": "kilogram_per_second_per_cubic_meter",
        "units": [
            ("gram per second per cubic centimeter", "gram_per_second_per_cubic_centimeter", 1000.0, "$\\mathrm{g} /\\left(\\mathrm{s} \\mathrm{cm}^{3}\\right)$ or g/s/cc or $\\mathrm{g} / \\mathrm{cc} / \\mathrm{sec}$", ['g /left(s cm^{3right)', 'g/s/cc', 'g / cc / sec']),
            ("kilogram per hour per cubic foot", "kilogram_per_hour_per_cubic_foot", 0.0098096, "kg/(h ft ${ }^{3}$ ) or kg/hr/ cft", ['kg/(h ft { ^{3 )', 'kg/hr/ cft']),
            ("kilogram per hour per cubic meter", "kilogram_per_hour_per_cubic_meter", 0.00027778000000000004, "kg/(h m3) or kg/hr/ cu.m", ['kg/(h m3)', 'kg/hr/ cu.m']),
            ("kilogram per second per cubic meter", "kilogram_per_second_per_cubic_meter", 1.0, "$\\mathrm{kg} /\\left(\\mathrm{s} \\mathrm{m}^{3}\\right)$ or kg/sec/ cu.m", ['kg /left(s m^{3right)', 'kg/sec/ cu.m']),
            ("pound per hour per cubic foot", "pound_per_hour_per_cubic_foot", 0.0044496, "$\\mathrm{lb} /\\left(\\mathrm{h} \\mathrm{ft}^{3}\\right)$ or $\\mathrm{lb} / \\mathrm{hr} / \\mathrm{cft}$ or PPH/cft", ['lb /left(h ft^{3right)', 'lb / hr / cft', 'PPH/cft']),
            ("pound per minute per cubic foot", "pound_per_minute_per_cubic_foot", 0.26697, "lb/(min $\\mathrm{ft}^{3}$ ) or lb/ $\\mathrm{min} / \\mathrm{cft}$", ['lb/(min ft^{3 )', 'lb/ min / cft']),
            ("pound per second per cubic foot", "pound_per_second_per_cubic_foot", 16.018, "b/(s ft ${ }^{3}$ ) or lb/sec/cft", ['b/(s ft { ^{3 )', 'lb/sec/cft'])
        ],
        "field_name": "volumetric_mass_flow_rate",
        "display_name": "Volumetric Mass Flow Rate",
    },
    "Wavenumber": {
        "dimension": WAVENUMBER,
        "default_unit": "diopter",
        "units": [
            ("diopter", "diopter", 1.0, "D", ['D']),
            ("kayser", "kayser", 100.0, "K", ['K']),
            ("reciprocal meter", "reciprocal_meter", 1.0, "1/m", [])
        ],
        "field_name": "wavenumber",
        "display_name": "Wavenumber",
    }
}

# Special Dimensionless variable - handcrafted for proper behavior
class DimensionlessSetter(TypeSafeSetter):
    """Dimensionless-specific setter with only dimensionless units."""
    
    def __init__(self, variable: 'Dimensionless', value: float):
        super().__init__(variable, value)
    
    # Dimensionless units
    @property
    def dimensionless(self) -> 'Dimensionless':
        self.variable.quantity = FastQuantity(self.value, DimensionlessUnits.dimensionless)
        return cast('Dimensionless', self.variable)
    
    # Common alias for no units
    @property
    def unitless(self) -> 'Dimensionless':
        self.variable.quantity = FastQuantity(self.value, DimensionlessUnits.dimensionless)
        return cast('Dimensionless', self.variable)


class Dimensionless(TypedVariable):
    """Type-safe dimensionless variable with expression capabilities."""

    _setter_class = DimensionlessSetter
    _expected_dimension = DIMENSIONLESS
    _default_unit_property = "dimensionless"
    
    def set(self, value: float) -> DimensionlessSetter:
        """Create a dimensionless setter for this variable with proper type annotation."""
        return DimensionlessSetter(self, value)



def convert_unit_name_to_property(unit_name: str) -> str:
    """Convert unit name to property name without automatic pluralization."""
    # Use unit name as-is for property name
    # Replace any characters that are not valid Python identifiers
    property_name = unit_name.replace('-', '_').replace(' ', '_').replace('.', '_')
    
    # Handle Python reserved words and other edge cases
    reserved_words = {'class', 'def', 'if', 'else', 'for', 'while', 'import', 'from', 'as', 'in'}
    if property_name in reserved_words:
        property_name = f"{property_name}_unit"
    
    return property_name


def create_setter_class(class_name: str, variable_name: str, definition: dict[str, Any]) -> type:
    """Dynamically create a setter class with unit properties."""
    
    # Create base setter class
    setter_class = type(
        class_name,
        (TypeSafeSetter,),
        {
            '__init__': lambda self, variable, value: TypeSafeSetter.__init__(self, variable, value),
            '__doc__': f"{variable_name}-specific setter with only {variable_name.lower()} units."
        }
    )
    
    # Add properties for each unit using unit data directly
    for unit_name, property_name, si_factor, symbol, aliases in definition["units"]:
        # Create a unit definition from the consolidated data
        def make_property(unit_nm, si_fac, sym):
            def getter(self):
                # Create unit definition and constant from consolidated unit data
                unit_def = UnitDefinition(
                    name=unit_nm,
                    symbol=sym,
                    dimension=definition["dimension"],
                    si_factor=si_fac
                )
                unit_const = UnitConstant(unit_def)
                self.variable.quantity = FastQuantity(self.value, unit_const)
                return self.variable  # type: ignore
            return property(getter)
        
        # Add the primary property to the class
        setattr(setter_class, property_name, make_property(unit_name, si_factor, symbol))
        
        # Add alias properties
        for alias in aliases:
            # Convert alias to valid property name
            alias_property = convert_unit_name_to_property(alias)
            # Only add if it's different from the main property and doesn't already exist
            if alias_property != property_name and not hasattr(setter_class, alias_property):
                setattr(setter_class, alias_property, make_property(unit_name, si_factor, symbol))
    
    return setter_class


def create_variable_class(class_name: str, definition: dict[str, Any], setter_class: type) -> type:
    """Dynamically create a variable class."""
    
    # Create the variable class
    variable_class = type(
        class_name,
        (TypedVariable,),
        {
            '_setter_class': setter_class,
            '_expected_dimension': definition["dimension"],
            '_default_unit_property': definition["default_unit"],
            '__doc__': f"Type-safe {class_name.lower()} variable with expression capabilities.",
            'set': lambda self, value: setter_class(self, value)
        }
    )
    
    # Add type hint for set method
    variable_class.set.__annotations__ = {'value': float, 'return': setter_class}
    
    return variable_class


# Create all variable and setter classes dynamically
for var_name, var_def in VARIABLE_DEFINITIONS.items():
    # Create setter class
    setter_name = f"{var_name}Setter"
    setter_class = create_setter_class(setter_name, var_name, var_def)
    
    # Create variable class
    variable_class = create_variable_class(var_name, var_def, setter_class)
    
    # Export them to module namespace
    globals()[setter_name] = setter_class
    globals()[var_name] = variable_class

# Individual exports for easier import
# Special Dimensionless class is already defined above

AbsorbedDoseSetter = globals()['AbsorbedDoseSetter']
AbsorbedDose = globals()['AbsorbedDose']
AccelerationSetter = globals()['AccelerationSetter']
Acceleration = globals()['Acceleration']
ActivationEnergySetter = globals()['ActivationEnergySetter']
ActivationEnergy = globals()['ActivationEnergy']
AmountOfSubstanceSetter = globals()['AmountOfSubstanceSetter']
AmountOfSubstance = globals()['AmountOfSubstance']
AnglePlaneSetter = globals()['AnglePlaneSetter']
AnglePlane = globals()['AnglePlane']
AngleSolidSetter = globals()['AngleSolidSetter']
AngleSolid = globals()['AngleSolid']
AngularAccelerationSetter = globals()['AngularAccelerationSetter']
AngularAcceleration = globals()['AngularAcceleration']
AngularMomentumSetter = globals()['AngularMomentumSetter']
AngularMomentum = globals()['AngularMomentum']
AreaSetter = globals()['AreaSetter']
Area = globals()['Area']
AreaPerUnitVolumeSetter = globals()['AreaPerUnitVolumeSetter']
AreaPerUnitVolume = globals()['AreaPerUnitVolume']
AtomicWeightSetter = globals()['AtomicWeightSetter']
AtomicWeight = globals()['AtomicWeight']
ConcentrationSetter = globals()['ConcentrationSetter']
Concentration = globals()['Concentration']
DynamicFluiditySetter = globals()['DynamicFluiditySetter']
DynamicFluidity = globals()['DynamicFluidity']
ElectricCapacitanceSetter = globals()['ElectricCapacitanceSetter']
ElectricCapacitance = globals()['ElectricCapacitance']
ElectricChargeSetter = globals()['ElectricChargeSetter']
ElectricCharge = globals()['ElectricCharge']
ElectricCurrentIntensitySetter = globals()['ElectricCurrentIntensitySetter']
ElectricCurrentIntensity = globals()['ElectricCurrentIntensity']
ElectricDipoleMomentSetter = globals()['ElectricDipoleMomentSetter']
ElectricDipoleMoment = globals()['ElectricDipoleMoment']
ElectricFieldStrengthSetter = globals()['ElectricFieldStrengthSetter']
ElectricFieldStrength = globals()['ElectricFieldStrength']
ElectricInductanceSetter = globals()['ElectricInductanceSetter']
ElectricInductance = globals()['ElectricInductance']
ElectricPotentialSetter = globals()['ElectricPotentialSetter']
ElectricPotential = globals()['ElectricPotential']
ElectricResistanceSetter = globals()['ElectricResistanceSetter']
ElectricResistance = globals()['ElectricResistance']
ElectricalConductanceSetter = globals()['ElectricalConductanceSetter']
ElectricalConductance = globals()['ElectricalConductance']
ElectricalPermittivitySetter = globals()['ElectricalPermittivitySetter']
ElectricalPermittivity = globals()['ElectricalPermittivity']
ElectricalResistivitySetter = globals()['ElectricalResistivitySetter']
ElectricalResistivity = globals()['ElectricalResistivity']
EnergyFluxSetter = globals()['EnergyFluxSetter']
EnergyFlux = globals()['EnergyFlux']
EnergyHeatWorkSetter = globals()['EnergyHeatWorkSetter']
EnergyHeatWork = globals()['EnergyHeatWork']
EnergyPerUnitAreaSetter = globals()['EnergyPerUnitAreaSetter']
EnergyPerUnitArea = globals()['EnergyPerUnitArea']
ForceSetter = globals()['ForceSetter']
Force = globals()['Force']
ForceBodySetter = globals()['ForceBodySetter']
ForceBody = globals()['ForceBody']
ForcePerUnitMassSetter = globals()['ForcePerUnitMassSetter']
ForcePerUnitMass = globals()['ForcePerUnitMass']
FrequencyVoltageRatioSetter = globals()['FrequencyVoltageRatioSetter']
FrequencyVoltageRatio = globals()['FrequencyVoltageRatio']
FuelConsumptionSetter = globals()['FuelConsumptionSetter']
FuelConsumption = globals()['FuelConsumption']
HeatOfCombustionSetter = globals()['HeatOfCombustionSetter']
HeatOfCombustion = globals()['HeatOfCombustion']
HeatOfFusionSetter = globals()['HeatOfFusionSetter']
HeatOfFusion = globals()['HeatOfFusion']
HeatOfVaporizationSetter = globals()['HeatOfVaporizationSetter']
HeatOfVaporization = globals()['HeatOfVaporization']
HeatTransferCoefficientSetter = globals()['HeatTransferCoefficientSetter']
HeatTransferCoefficient = globals()['HeatTransferCoefficient']
IlluminanceSetter = globals()['IlluminanceSetter']
Illuminance = globals()['Illuminance']
KineticEnergyOfTurbulenceSetter = globals()['KineticEnergyOfTurbulenceSetter']
KineticEnergyOfTurbulence = globals()['KineticEnergyOfTurbulence']
LengthSetter = globals()['LengthSetter']
Length = globals()['Length']
LinearMassDensitySetter = globals()['LinearMassDensitySetter']
LinearMassDensity = globals()['LinearMassDensity']
LinearMomentumSetter = globals()['LinearMomentumSetter']
LinearMomentum = globals()['LinearMomentum']
LuminanceSelfSetter = globals()['LuminanceSelfSetter']
LuminanceSelf = globals()['LuminanceSelf']
LuminousFluxSetter = globals()['LuminousFluxSetter']
LuminousFlux = globals()['LuminousFlux']
LuminousIntensitySetter = globals()['LuminousIntensitySetter']
LuminousIntensity = globals()['LuminousIntensity']
MagneticFieldSetter = globals()['MagneticFieldSetter']
MagneticField = globals()['MagneticField']
MagneticFluxSetter = globals()['MagneticFluxSetter']
MagneticFlux = globals()['MagneticFlux']
MagneticInductionFieldStrengthSetter = globals()['MagneticInductionFieldStrengthSetter']
MagneticInductionFieldStrength = globals()['MagneticInductionFieldStrength']
MagneticMomentSetter = globals()['MagneticMomentSetter']
MagneticMoment = globals()['MagneticMoment']
MagneticPermeabilitySetter = globals()['MagneticPermeabilitySetter']
MagneticPermeability = globals()['MagneticPermeability']
MagnetomotiveForceSetter = globals()['MagnetomotiveForceSetter']
MagnetomotiveForce = globals()['MagnetomotiveForce']
MassSetter = globals()['MassSetter']
Mass = globals()['Mass']
MassDensitySetter = globals()['MassDensitySetter']
MassDensity = globals()['MassDensity']
MassFlowRateSetter = globals()['MassFlowRateSetter']
MassFlowRate = globals()['MassFlowRate']
MassFluxSetter = globals()['MassFluxSetter']
MassFlux = globals()['MassFlux']
MassFractionOfISetter = globals()['MassFractionOfISetter']
MassFractionOfI = globals()['MassFractionOfI']
MassTransferCoefficientSetter = globals()['MassTransferCoefficientSetter']
MassTransferCoefficient = globals()['MassTransferCoefficient']
MolalityOfSoluteISetter = globals()['MolalityOfSoluteISetter']
MolalityOfSoluteI = globals()['MolalityOfSoluteI']
MolarConcentrationByMassSetter = globals()['MolarConcentrationByMassSetter']
MolarConcentrationByMass = globals()['MolarConcentrationByMass']
MolarFlowRateSetter = globals()['MolarFlowRateSetter']
MolarFlowRate = globals()['MolarFlowRate']
MolarFluxSetter = globals()['MolarFluxSetter']
MolarFlux = globals()['MolarFlux']
MolarHeatCapacitySetter = globals()['MolarHeatCapacitySetter']
MolarHeatCapacity = globals()['MolarHeatCapacity']
MolarityOfISetter = globals()['MolarityOfISetter']
MolarityOfI = globals()['MolarityOfI']
MoleFractionOfISetter = globals()['MoleFractionOfISetter']
MoleFractionOfI = globals()['MoleFractionOfI']
MomentOfInertiaSetter = globals()['MomentOfInertiaSetter']
MomentOfInertia = globals()['MomentOfInertia']
MomentumFlowRateSetter = globals()['MomentumFlowRateSetter']
MomentumFlowRate = globals()['MomentumFlowRate']
MomentumFluxSetter = globals()['MomentumFluxSetter']
MomentumFlux = globals()['MomentumFlux']
NormalityOfSolutionSetter = globals()['NormalityOfSolutionSetter']
NormalityOfSolution = globals()['NormalityOfSolution']
ParticleDensitySetter = globals()['ParticleDensitySetter']
ParticleDensity = globals()['ParticleDensity']
PermeabilitySetter = globals()['PermeabilitySetter']
Permeability = globals()['Permeability']
PhotonEmissionRateSetter = globals()['PhotonEmissionRateSetter']
PhotonEmissionRate = globals()['PhotonEmissionRate']
PowerPerUnitMassSetter = globals()['PowerPerUnitMassSetter']
PowerPerUnitMass = globals()['PowerPerUnitMass']
PowerPerUnitVolumeSetter = globals()['PowerPerUnitVolumeSetter']
PowerPerUnitVolume = globals()['PowerPerUnitVolume']
PowerThermalDutySetter = globals()['PowerThermalDutySetter']
PowerThermalDuty = globals()['PowerThermalDuty']
PressureSetter = globals()['PressureSetter']
Pressure = globals()['Pressure']
RadiationDoseEquivalentSetter = globals()['RadiationDoseEquivalentSetter']
RadiationDoseEquivalent = globals()['RadiationDoseEquivalent']
RadiationExposureSetter = globals()['RadiationExposureSetter']
RadiationExposure = globals()['RadiationExposure']
RadioactivitySetter = globals()['RadioactivitySetter']
Radioactivity = globals()['Radioactivity']
SecondMomentOfAreaSetter = globals()['SecondMomentOfAreaSetter']
SecondMomentOfArea = globals()['SecondMomentOfArea']
SecondRadiationConstantPlanckSetter = globals()['SecondRadiationConstantPlanckSetter']
SecondRadiationConstantPlanck = globals()['SecondRadiationConstantPlanck']
SpecificEnthalpySetter = globals()['SpecificEnthalpySetter']
SpecificEnthalpy = globals()['SpecificEnthalpy']
SpecificGravitySetter = globals()['SpecificGravitySetter']
SpecificGravity = globals()['SpecificGravity']
SpecificHeatCapacityConstantPressureSetter = globals()['SpecificHeatCapacityConstantPressureSetter']
SpecificHeatCapacityConstantPressure = globals()['SpecificHeatCapacityConstantPressure']
SpecificLengthSetter = globals()['SpecificLengthSetter']
SpecificLength = globals()['SpecificLength']
SpecificSurfaceSetter = globals()['SpecificSurfaceSetter']
SpecificSurface = globals()['SpecificSurface']
SpecificVolumeSetter = globals()['SpecificVolumeSetter']
SpecificVolume = globals()['SpecificVolume']
StressSetter = globals()['StressSetter']
Stress = globals()['Stress']
SurfaceMassDensitySetter = globals()['SurfaceMassDensitySetter']
SurfaceMassDensity = globals()['SurfaceMassDensity']
SurfaceTensionSetter = globals()['SurfaceTensionSetter']
SurfaceTension = globals()['SurfaceTension']
TemperatureSetter = globals()['TemperatureSetter']
Temperature = globals()['Temperature']
ThermalConductivitySetter = globals()['ThermalConductivitySetter']
ThermalConductivity = globals()['ThermalConductivity']
TimeSetter = globals()['TimeSetter']
Time = globals()['Time']
TorqueSetter = globals()['TorqueSetter']
Torque = globals()['Torque']
TurbulenceEnergyDissipationRateSetter = globals()['TurbulenceEnergyDissipationRateSetter']
TurbulenceEnergyDissipationRate = globals()['TurbulenceEnergyDissipationRate']
VelocityAngularSetter = globals()['VelocityAngularSetter']
VelocityAngular = globals()['VelocityAngular']
VelocityLinearSetter = globals()['VelocityLinearSetter']
VelocityLinear = globals()['VelocityLinear']
ViscosityDynamicSetter = globals()['ViscosityDynamicSetter']
ViscosityDynamic = globals()['ViscosityDynamic']
ViscosityKinematicSetter = globals()['ViscosityKinematicSetter']
ViscosityKinematic = globals()['ViscosityKinematic']
VolumeSetter = globals()['VolumeSetter']
Volume = globals()['Volume']
VolumeFractionOfISetter = globals()['VolumeFractionOfISetter']
VolumeFractionOfI = globals()['VolumeFractionOfI']
VolumetricCalorificHeatingValueSetter = globals()['VolumetricCalorificHeatingValueSetter']
VolumetricCalorificHeatingValue = globals()['VolumetricCalorificHeatingValue']
VolumetricCoefficientOfExpansionSetter = globals()['VolumetricCoefficientOfExpansionSetter']
VolumetricCoefficientOfExpansion = globals()['VolumetricCoefficientOfExpansion']
VolumetricFlowRateSetter = globals()['VolumetricFlowRateSetter']
VolumetricFlowRate = globals()['VolumetricFlowRate']
VolumetricFluxSetter = globals()['VolumetricFluxSetter']
VolumetricFlux = globals()['VolumetricFlux']
VolumetricMassFlowRateSetter = globals()['VolumetricMassFlowRateSetter']
VolumetricMassFlowRate = globals()['VolumetricMassFlowRate']
WavenumberSetter = globals()['WavenumberSetter']
Wavenumber = globals()['Wavenumber']


# Module registration compatibility
def get_consolidated_variable_modules():
    """Return module-like objects for consolidated variables."""
    
    class ConsolidatedVariableModule:
        """Mock module object for compatibility with existing registration system."""
        
        def __init__(self, var_name: str):
            self.var_name = var_name
            self.definition = VARIABLE_DEFINITIONS[var_name]
            self.variable_class = globals()[var_name]
            self.setter_class = globals()[f"{var_name}Setter"]
        
        def get_variable_class(self):
            return self.variable_class
        
        def get_setter_class(self):
            return self.setter_class
        
        def get_expected_dimension(self):
            return self.definition["dimension"]
    
    return [
        ConsolidatedVariableModule("AbsorbedDose"),
        ConsolidatedVariableModule("Acceleration"),
        ConsolidatedVariableModule("ActivationEnergy"),
        ConsolidatedVariableModule("AmountOfSubstance"),
        ConsolidatedVariableModule("AnglePlane"),
        ConsolidatedVariableModule("AngleSolid"),
        ConsolidatedVariableModule("AngularAcceleration"),
        ConsolidatedVariableModule("AngularMomentum"),
        ConsolidatedVariableModule("Area"),
        ConsolidatedVariableModule("AreaPerUnitVolume"),
        ConsolidatedVariableModule("AtomicWeight"),
        ConsolidatedVariableModule("Concentration"),
        ConsolidatedVariableModule("DynamicFluidity"),
        ConsolidatedVariableModule("ElectricCapacitance"),
        ConsolidatedVariableModule("ElectricCharge"),
        ConsolidatedVariableModule("ElectricCurrentIntensity"),
        ConsolidatedVariableModule("ElectricDipoleMoment"),
        ConsolidatedVariableModule("ElectricFieldStrength"),
        ConsolidatedVariableModule("ElectricInductance"),
        ConsolidatedVariableModule("ElectricPotential"),
        ConsolidatedVariableModule("ElectricResistance"),
        ConsolidatedVariableModule("ElectricalConductance"),
        ConsolidatedVariableModule("ElectricalPermittivity"),
        ConsolidatedVariableModule("ElectricalResistivity"),
        ConsolidatedVariableModule("EnergyFlux"),
        ConsolidatedVariableModule("EnergyHeatWork"),
        ConsolidatedVariableModule("EnergyPerUnitArea"),
        ConsolidatedVariableModule("Force"),
        ConsolidatedVariableModule("ForceBody"),
        ConsolidatedVariableModule("ForcePerUnitMass"),
        ConsolidatedVariableModule("FrequencyVoltageRatio"),
        ConsolidatedVariableModule("FuelConsumption"),
        ConsolidatedVariableModule("HeatOfCombustion"),
        ConsolidatedVariableModule("HeatOfFusion"),
        ConsolidatedVariableModule("HeatOfVaporization"),
        ConsolidatedVariableModule("HeatTransferCoefficient"),
        ConsolidatedVariableModule("Illuminance"),
        ConsolidatedVariableModule("KineticEnergyOfTurbulence"),
        ConsolidatedVariableModule("Length"),
        ConsolidatedVariableModule("LinearMassDensity"),
        ConsolidatedVariableModule("LinearMomentum"),
        ConsolidatedVariableModule("LuminanceSelf"),
        ConsolidatedVariableModule("LuminousFlux"),
        ConsolidatedVariableModule("LuminousIntensity"),
        ConsolidatedVariableModule("MagneticField"),
        ConsolidatedVariableModule("MagneticFlux"),
        ConsolidatedVariableModule("MagneticInductionFieldStrength"),
        ConsolidatedVariableModule("MagneticMoment"),
        ConsolidatedVariableModule("MagneticPermeability"),
        ConsolidatedVariableModule("MagnetomotiveForce"),
        ConsolidatedVariableModule("Mass"),
        ConsolidatedVariableModule("MassDensity"),
        ConsolidatedVariableModule("MassFlowRate"),
        ConsolidatedVariableModule("MassFlux"),
        ConsolidatedVariableModule("MassFractionOfI"),
        ConsolidatedVariableModule("MassTransferCoefficient"),
        ConsolidatedVariableModule("MolalityOfSoluteI"),
        ConsolidatedVariableModule("MolarConcentrationByMass"),
        ConsolidatedVariableModule("MolarFlowRate"),
        ConsolidatedVariableModule("MolarFlux"),
        ConsolidatedVariableModule("MolarHeatCapacity"),
        ConsolidatedVariableModule("MolarityOfI"),
        ConsolidatedVariableModule("MoleFractionOfI"),
        ConsolidatedVariableModule("MomentOfInertia"),
        ConsolidatedVariableModule("MomentumFlowRate"),
        ConsolidatedVariableModule("MomentumFlux"),
        ConsolidatedVariableModule("NormalityOfSolution"),
        ConsolidatedVariableModule("ParticleDensity"),
        ConsolidatedVariableModule("Permeability"),
        ConsolidatedVariableModule("PhotonEmissionRate"),
        ConsolidatedVariableModule("PowerPerUnitMass"),
        ConsolidatedVariableModule("PowerPerUnitVolume"),
        ConsolidatedVariableModule("PowerThermalDuty"),
        ConsolidatedVariableModule("Pressure"),
        ConsolidatedVariableModule("RadiationDoseEquivalent"),
        ConsolidatedVariableModule("RadiationExposure"),
        ConsolidatedVariableModule("Radioactivity"),
        ConsolidatedVariableModule("SecondMomentOfArea"),
        ConsolidatedVariableModule("SecondRadiationConstantPlanck"),
        ConsolidatedVariableModule("SpecificEnthalpy"),
        ConsolidatedVariableModule("SpecificGravity"),
        ConsolidatedVariableModule("SpecificHeatCapacityConstantPressure"),
        ConsolidatedVariableModule("SpecificLength"),
        ConsolidatedVariableModule("SpecificSurface"),
        ConsolidatedVariableModule("SpecificVolume"),
        ConsolidatedVariableModule("Stress"),
        ConsolidatedVariableModule("SurfaceMassDensity"),
        ConsolidatedVariableModule("SurfaceTension"),
        ConsolidatedVariableModule("Temperature"),
        ConsolidatedVariableModule("ThermalConductivity"),
        ConsolidatedVariableModule("Time"),
        ConsolidatedVariableModule("Torque"),
        ConsolidatedVariableModule("TurbulenceEnergyDissipationRate"),
        ConsolidatedVariableModule("VelocityAngular"),
        ConsolidatedVariableModule("VelocityLinear"),
        ConsolidatedVariableModule("ViscosityDynamic"),
        ConsolidatedVariableModule("ViscosityKinematic"),
        ConsolidatedVariableModule("Volume"),
        ConsolidatedVariableModule("VolumeFractionOfI"),
        ConsolidatedVariableModule("VolumetricCalorificHeatingValue"),
        ConsolidatedVariableModule("VolumetricCoefficientOfExpansion"),
        ConsolidatedVariableModule("VolumetricFlowRate"),
        ConsolidatedVariableModule("VolumetricFlux"),
        ConsolidatedVariableModule("VolumetricMassFlowRate"),
        ConsolidatedVariableModule("Wavenumber")
    ]

