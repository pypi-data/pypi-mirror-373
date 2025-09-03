"""
Comprehensive Consolidated Units Module
=======================================

Auto-generated consolidated unit definitions for all engineering units.
Contains 864 units
across 105 fields organized into 105 dimensional groups.

Generated from the complete NIST unit tables and engineering references.
"""

from .dimension import (
    ABSORBED_DOSE,
    ACCELERATION,
    ACTIVATION_ENERGY,
    AMOUNT_OF_SUBSTANCE,
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
    MASS_TRANSFER_COEFFICIENT,
    MOLALITY_OF_SOLUTE_I,
    MOLARITY_OF_I,
    MOLAR_CONCENTRATION_BY_MASS,
    MOLAR_FLOW_RATE,
    MOLAR_FLUX,
    MOLAR_HEAT_CAPACITY,
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
    WAVENUMBER
)

# Comprehensive unit definitions organized by dimensional signature
UNIT_DEFINITIONS = {

    "absorbed_dose": {
        # Absorbed Radiation Dose - LENGTH^2 TIME^-2
        "dimension": ABSORBED_DOSE,
        "units": [
            {
                "name": "erg_per_gram",
                "symbol": "erg/g",
                "si_factor": 0.0001,
                "full_name": "erg per gram",
                "notation": "erg/g",
                "aliases": ['erg_per_g'],
            },
            {
                "name": "gram_rad",
                "symbol": "g-rad",
                "si_factor": 0.01,
                "full_name": "gram-rad",
                "notation": "g-rad",
                "aliases": ['g_rad'],
            },
            {
                "name": "gray",
                "symbol": "Gy",
                "si_factor": 1.0,
                "full_name": "gray",
                "notation": "Gy",
                "aliases": ['Gy'],
            },
            {
                "name": "microgray",
                "symbol": "μGy",
                "si_factor": 1e-06,
                "full_name": "microgray",
                "notation": "μGy",
                "aliases": [],
            },
            {
                "name": "milligray",
                "symbol": "mGy",
                "si_factor": 0.001,
                "full_name": "milligray",
                "notation": "mGy",
                "aliases": [],
            },
            {
                "name": "rad",
                "symbol": "rad",
                "si_factor": 0.01,
                "full_name": "rad",
                "notation": "rad",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "acceleration": {
        # Acceleration - LENGTH TIME^-2
        "dimension": ACCELERATION,
        "units": [
            {
                "name": "foot_per_second_squared",
                "symbol": "$\\mathrm{ft} / \\mathrm{s}^{2}$ or $\\mathrm{ft} / \\mathrm{sec}^{2}$",
                "si_factor": 0.3048,
                "full_name": "foot per second squared",
                "notation": "$\\mathrm{ft} / \\mathrm{s}^{2}$ or $\\mathrm{ft} / \\mathrm{sec}^{2}$",
                "aliases": ['ft_per_s2', 'fps2'],
            },
            {
                "name": "meter_per_second_squared",
                "symbol": "$\\mathrm{m} / \\mathrm{s}^{2}$",
                "si_factor": 1.0,
                "full_name": "meter per second squared",
                "notation": "$\\mathrm{m} / \\mathrm{s}^{2}$",
                "aliases": ['m_per_s2'],
            }
        ],
        "aliases": {}
    },

    "activation_energy": {
        # Activation Energy - AMOUNT^-1 LENGTH^2 TIME^-2
        "dimension": ACTIVATION_ENERGY,
        "units": [
            {
                "name": "btu_per_pound_mole",
                "symbol": "Btu/lb-mol",
                "si_factor": 2326.0,
                "full_name": "Btu per pound mole",
                "notation": "Btu/lb-mol",
                "aliases": ['btu_per_lbmol'],
            },
            {
                "name": "calorie_mean_per_gram_mole",
                "symbol": "cal/mol",
                "si_factor": 4.18675,
                "full_name": "calorie (mean) per gram mole",
                "notation": "cal/mol",
                "aliases": ['cal_mean_per_gmol'],
            },
            {
                "name": "joule_per_gram_mole",
                "symbol": "J/mol",
                "si_factor": 1.0,
                "full_name": "joule per gram mole",
                "notation": "J/mol",
                "aliases": [],
            },
            {
                "name": "joule_per_kilogram_mole",
                "symbol": "J/kmol",
                "si_factor": 1000.0,
                "full_name": "joule per kilogram mole",
                "notation": "J/kmol",
                "aliases": [],
            },
            {
                "name": "kilocalorie_per_kilogram_mole",
                "symbol": "kcal/kmol",
                "si_factor": 4.18675,
                "full_name": "kilocalorie per kilogram mole",
                "notation": "kcal/kmol",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "amount_of_substance": {
        # Amount of Substance - AMOUNT
        "dimension": AMOUNT_OF_SUBSTANCE,
        "units": [
            {
                "name": "kilogram_mol",
                "symbol": "kmol",
                "si_factor": 1000.0,
                "full_name": "kilogram mol or kmol",
                "notation": "kmol",
                "aliases": ['kmol'],
            },
            {
                "name": "micromole",
                "symbol": "μmol",
                "si_factor": 1e-06,
                "full_name": "micromole (gram)",
                "notation": "μmol",
                "aliases": [],
            },
            {
                "name": "millimole",
                "symbol": "mmol",
                "si_factor": 0.001,
                "full_name": "millimole (gram)",
                "notation": "mmol",
                "aliases": [],
            },
            {
                "name": "mole",
                "symbol": "mol",
                "si_factor": 1.0,
                "full_name": "mole (gram)",
                "notation": "mol",
                "aliases": ['mol'],
            },
            {
                "name": "pound_mole",
                "symbol": "lb-mol or mole",
                "si_factor": 453.6,
                "full_name": "pound-mole",
                "notation": "lb-mol or mole",
                "aliases": ['lb-mol', 'mole'],
            }
        ],
        "aliases": {}
    },

    "angle_plane": {
        # Angle, Plane - Dimensionless
        "dimension": DIMENSIONLESS,
        "units": [
            {
                "name": "degree",
                "symbol": "${ }^{\\circ}$",
                "si_factor": 0.0174533,
                "full_name": "degree",
                "notation": "${ }^{\\circ}$",
                "aliases": [],
            },
            {
                "name": "gon",
                "symbol": "g or gon",
                "si_factor": 0.015708,
                "full_name": "gon",
                "notation": "g or gon",
                "aliases": ['g'],
            },
            {
                "name": "grade",
                "symbol": "g or grad",
                "si_factor": 0.015708,
                "full_name": "grade",
                "notation": "g or grad",
                "aliases": ['g', 'grad'],
            },
            {
                "name": "minute_new",
                "symbol": "c",
                "si_factor": 0.00015708,
                "full_name": "minute (new)",
                "notation": "c",
                "aliases": ['c'],
            },
            {
                "name": "minute_of_angle",
                "symbol": "'",
                "si_factor": 0.000290888,
                "full_name": "minute of angle",
                "notation": "'",
                "aliases": [],
            },
            {
                "name": "percent",
                "symbol": "\\%",
                "si_factor": 0.062832,
                "full_name": "percent",
                "notation": "\\%",
                "aliases": [],
            },
            {
                "name": "plane_angle",
                "symbol": "-",
                "si_factor": 3.141593,
                "full_name": "plane angle",
                "notation": "-",
                "aliases": [],
            },
            {
                "name": "quadrant",
                "symbol": "quadr",
                "si_factor": 1.570796,
                "full_name": "quadrant",
                "notation": "quadr",
                "aliases": [],
            },
            {
                "name": "radian",
                "symbol": "rad",
                "si_factor": 1.0,
                "full_name": "radian",
                "notation": "rad",
                "aliases": ['rad'],
            },
            {
                "name": "right_angle",
                "symbol": "$\\perp$",
                "si_factor": 1.570796,
                "full_name": "right angle",
                "notation": "$\\perp$",
                "aliases": ['perp'],
            },
            {
                "name": "round",
                "symbol": "tr or r",
                "si_factor": 6.283185,
                "full_name": "round",
                "notation": "tr or r",
                "aliases": ['tr', 'r'],
            },
            {
                "name": "second_new",
                "symbol": "cc",
                "si_factor": 1.5707999999999999e-06,
                "full_name": "second (new)",
                "notation": "cc",
                "aliases": ['cc'],
            },
            {
                "name": "second_of_angle",
                "symbol": "\"",
                "si_factor": 4.848099999999999e-06,
                "full_name": "second of angle",
                "notation": "\"",
                "aliases": [],
            },
            {
                "name": "thousandth_us",
                "symbol": "\\% (US)",
                "si_factor": 0.0015708,
                "full_name": "thousandth (US)",
                "notation": "\\% (US)",
                "aliases": [],
            },
            {
                "name": "turn",
                "symbol": "turn or rev",
                "si_factor": 6.283185,
                "full_name": "turn",
                "notation": "turn or rev",
                "aliases": ['rev'],
            }
        ],
        "aliases": {}
    },

    "angle_solid": {
        # Angle, Solid - Dimensionless
        "dimension": DIMENSIONLESS,
        "units": [
            {
                "name": "spat",
                "symbol": "spat",
                "si_factor": 12.5663,
                "full_name": "spat",
                "notation": "spat",
                "aliases": ['spat'],
            },
            {
                "name": "square_degree",
                "symbol": "$\\left({ }^{\\circ}\\right)^{2}$",
                "si_factor": 0.000304617,
                "full_name": "square degree",
                "notation": "$\\left({ }^{\\circ}\\right)^{2}$",
                "aliases": [],
            },
            {
                "name": "square_gon",
                "symbol": "(g) ${ }^{2}$",
                "si_factor": 0.00024674,
                "full_name": "square gon",
                "notation": "(g) ${ }^{2}$",
                "aliases": [],
            },
            {
                "name": "steradian",
                "symbol": "sr",
                "si_factor": 1.0,
                "full_name": "steradian",
                "notation": "sr",
                "aliases": ['sr'],
            }
        ],
        "aliases": {}
    },

    "angular_acceleration": {
        # Angular Acceleration - TIME^-2
        "dimension": ANGULAR_ACCELERATION,
        "units": [
            {
                "name": "radian_per_second_squared",
                "symbol": "$\\mathrm{rad} / \\mathrm{s}^{2}$",
                "si_factor": 1.0,
                "full_name": "radian per second squared",
                "notation": "$\\mathrm{rad} / \\mathrm{s}^{2}$",
                "aliases": [],
            },
            {
                "name": "revolution_per_second_squared",
                "symbol": "$\\mathrm{rev} / \\mathrm{sec}^{2}$",
                "si_factor": 6.2832,
                "full_name": "revolution per second squared",
                "notation": "$\\mathrm{rev} / \\mathrm{sec}^{2}$",
                "aliases": [],
            },
            {
                "name": "rpm_or_revolution_per_minute",
                "symbol": "$\\mathrm{rev} / \\mathrm{min}^{2}$ or rpm/min",
                "si_factor": 0.001745,
                "full_name": "rpm (or revolution per minute) per minute",
                "notation": "$\\mathrm{rev} / \\mathrm{min}^{2}$ or rpm/min",
                "aliases": ['rev / min^{2', 'rpm/min'],
            }
        ],
        "aliases": {}
    },

    "angular_momentum": {
        # Angular Momentum - LENGTH^2 MASS TIME^-1
        "dimension": ANGULAR_MOMENTUM,
        "units": [
            {
                "name": "gram_centimeter_squared_per_second",
                "symbol": "$\\mathrm{g} \\mathrm{cm}^{2} / \\mathrm{s}$",
                "si_factor": 1e-07,
                "full_name": "gram centimeter squared per second",
                "notation": "$\\mathrm{g} \\mathrm{cm}^{2} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "kilogram_meter_squared_per_second",
                "symbol": "$\\mathrm{kg} \\mathrm{m}^{2} / \\mathrm{s}$",
                "si_factor": 1.0,
                "full_name": "kilogram meter squared per second",
                "notation": "$\\mathrm{kg} \\mathrm{m}^{2} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "pound_force_square_foot_per_second",
                "symbol": "lb ft ${ }^{2} / \\mathrm{sec}$",
                "si_factor": 0.04214,
                "full_name": "pound force square foot per second",
                "notation": "lb ft ${ }^{2} / \\mathrm{sec}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "area": {
        # Area - LENGTH^2
        "dimension": AREA,
        "units": [
            {
                "name": "acre_general",
                "symbol": "ac",
                "si_factor": 4046.856,
                "full_name": "acre (general)",
                "notation": "ac",
                "aliases": ['ac'],
            },
            {
                "name": "are",
                "symbol": "a",
                "si_factor": 100.0,
                "full_name": "are",
                "notation": "a",
                "aliases": ['a'],
            },
            {
                "name": "arpent_quebec",
                "symbol": "arp",
                "si_factor": 3418.89,
                "full_name": "arpent (Quebec)",
                "notation": "arp",
                "aliases": ['arp'],
            },
            {
                "name": "barn",
                "symbol": "b",
                "si_factor": 1e-28,
                "full_name": "barn",
                "notation": "b",
                "aliases": ['b'],
            },
            {
                "name": "circular_inch",
                "symbol": "cin",
                "si_factor": 0.000506707,
                "full_name": "circular inch",
                "notation": "cin",
                "aliases": ['cin'],
            },
            {
                "name": "circular_mil",
                "symbol": "cmil",
                "si_factor": 5.07e-10,
                "full_name": "circular mil",
                "notation": "cmil",
                "aliases": ['cmil'],
            },
            {
                "name": "hectare",
                "symbol": "ha",
                "si_factor": 10000.0,
                "full_name": "hectare",
                "notation": "ha",
                "aliases": ['ha'],
            },
            {
                "name": "shed",
                "symbol": "shed",
                "si_factor": 1e-52,
                "full_name": "shed",
                "notation": "shed",
                "aliases": ['shed'],
            },
            {
                "name": "square_centimeter",
                "symbol": "$\\mathrm{cm}^{2}$",
                "si_factor": 0.0001,
                "full_name": "square centimeter",
                "notation": "$\\mathrm{cm}^{2}$",
                "aliases": [],
            },
            {
                "name": "square_chain_ramsden",
                "symbol": "sq ch (Rams)",
                "si_factor": 929.03,
                "full_name": "square chain (Ramsden)",
                "notation": "sq ch (Rams)",
                "aliases": [],
            },
            {
                "name": "square_chain_survey_gunters",
                "symbol": "sq ch (surv)",
                "si_factor": 404.6856,
                "full_name": "square chain (Survey, Gunter's)",
                "notation": "sq ch (surv)",
                "aliases": [],
            },
            {
                "name": "square_decimeter",
                "symbol": "$\\mathrm{dm}^{2}$",
                "si_factor": 0.01,
                "full_name": "square decimeter",
                "notation": "$\\mathrm{dm}^{2}$",
                "aliases": [],
            },
            {
                "name": "square_fermi",
                "symbol": "$\\mathrm{F}^{2}$",
                "si_factor": 1e-30,
                "full_name": "square fermi",
                "notation": "$\\mathrm{F}^{2}$",
                "aliases": [],
            },
            {
                "name": "square_foot",
                "symbol": "sq ft or ft ${ }^{2}$",
                "si_factor": 0.092903,
                "full_name": "square foot",
                "notation": "sq ft or ft ${ }^{2}$",
                "aliases": ['sq ft', 'ft { ^{2'],
            },
            {
                "name": "square_hectometer",
                "symbol": "$\\mathrm{hm}^{2}$",
                "si_factor": 10000.0,
                "full_name": "square hectometer",
                "notation": "$\\mathrm{hm}^{2}$",
                "aliases": [],
            },
            {
                "name": "square_inch",
                "symbol": "sq in or in ${ }^{2}$",
                "si_factor": 0.00064516,
                "full_name": "square inch",
                "notation": "sq in or in ${ }^{2}$",
                "aliases": ['sq in', 'in { ^{2'],
            },
            {
                "name": "square_kilometer",
                "symbol": "$\\mathrm{km}^{2}$",
                "si_factor": 1000000.0,
                "full_name": "square kilometer",
                "notation": "$\\mathrm{km}^{2}$",
                "aliases": [],
            },
            {
                "name": "square_league_statute",
                "symbol": "sq lg (stat)",
                "si_factor": 23310000.0,
                "full_name": "square league (statute)",
                "notation": "sq lg (stat)",
                "aliases": [],
            },
            {
                "name": "square_meter",
                "symbol": "$\\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "square meter",
                "notation": "$\\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "square_micron",
                "symbol": "$\\mu \\mathrm{m}^{2}$ or $\\mu^{2}$",
                "si_factor": 1e-12,
                "full_name": "square micron",
                "notation": "$\\mu \\mathrm{m}^{2}$ or $\\mu^{2}$",
                "aliases": ['mu m^{2', 'mu^{2'],
            },
            {
                "name": "square_mile_statute",
                "symbol": "sq mi (stat)",
                "si_factor": 2590000.0,
                "full_name": "square mile (statute)",
                "notation": "sq mi (stat)",
                "aliases": [],
            },
            {
                "name": "square_mile_us_survey",
                "symbol": "sq mi (US Surv)",
                "si_factor": 2590000.0,
                "full_name": "square mile (US survey)",
                "notation": "sq mi (US Surv)",
                "aliases": [],
            },
            {
                "name": "square_millimeter",
                "symbol": "$\\mathrm{mm}^{2}$",
                "si_factor": 1e-06,
                "full_name": "square millimeter",
                "notation": "$\\mathrm{mm}^{2}$",
                "aliases": [],
            },
            {
                "name": "square_nanometer",
                "symbol": "$\\mathrm{nm}^{2}$",
                "si_factor": 1e-18,
                "full_name": "square nanometer",
                "notation": "$\\mathrm{nm}^{2}$",
                "aliases": [],
            },
            {
                "name": "square_yard",
                "symbol": "sq yd",
                "si_factor": 0.836131,
                "full_name": "square yard",
                "notation": "sq yd",
                "aliases": [],
            },
            {
                "name": "township_us",
                "symbol": "twshp",
                "si_factor": 93240000.0,
                "full_name": "township (US)",
                "notation": "twshp",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "area_per_unit_volume": {
        # Area per Unit Volume - LENGTH^-1
        "dimension": AREA_PER_UNIT_VOLUME,
        "units": [
            {
                "name": "square_centimeter_per_cubic_centimeter",
                "symbol": "$\\mathrm{cm}^{2} / \\mathrm{cc}$",
                "si_factor": 100.0,
                "full_name": "square centimeter per cubic centimeter",
                "notation": "$\\mathrm{cm}^{2} / \\mathrm{cc}$",
                "aliases": [],
            },
            {
                "name": "square_foot_per_cubic_foot",
                "symbol": "$\\mathrm{ft}^{2} / \\mathrm{ft}^{3}$ or sqft/cft",
                "si_factor": 3.2808,
                "full_name": "square foot per cubic foot",
                "notation": "$\\mathrm{ft}^{2} / \\mathrm{ft}^{3}$ or sqft/cft",
                "aliases": ['ft^{2 / ft^{3', 'sqft/cft'],
            },
            {
                "name": "square_inch_per_cubic_inch",
                "symbol": "$\\mathrm{in}^{2} / \\mathrm{in}^{3}$ or sq.in./cu. in.",
                "si_factor": 1.0,
                "full_name": "square inch per cubic inch",
                "notation": "$\\mathrm{in}^{2} / \\mathrm{in}^{3}$ or sq.in./cu. in.",
                "aliases": ['in^{2 / in^{3', 'sq.in./cu. in.'],
            },
            {
                "name": "square_meter_per_cubic_meter",
                "symbol": "$\\mathrm{m}^{2} / \\mathrm{m}^{3}$ or $1 / \\mathrm{m}^{3}$",
                "si_factor": 1.0,
                "full_name": "square meter per cubic meter",
                "notation": "$\\mathrm{m}^{2} / \\mathrm{m}^{3}$ or $1 / \\mathrm{m}^{3}$",
                "aliases": ['m^{2 / m^{3', '1 / m^{3'],
            }
        ],
        "aliases": {}
    },

    "atomic_weight": {
        # Atomic Weight - AMOUNT^-1 MASS
        "dimension": ATOMIC_WEIGHT,
        "units": [
            {
                "name": "atomic_mass_unit_12c",
                "symbol": "amu",
                "si_factor": 1.0,
                "full_name": "atomic mass unit (12C)",
                "notation": "amu",
                "aliases": ['amu'],
            },
            {
                "name": "grams_per_mole",
                "symbol": "g/mol",
                "si_factor": 1.0,
                "full_name": "grams per mole",
                "notation": "g/mol",
                "aliases": [],
            },
            {
                "name": "kilograms_per_kilomole",
                "symbol": "kg/kmol",
                "si_factor": 1.0,
                "full_name": "kilograms per kilomole",
                "notation": "kg/kmol",
                "aliases": [],
            },
            {
                "name": "pounds_per_pound_mole",
                "symbol": "$\\mathrm{lb} / \\mathrm{lb}-$ mol or $\\mathrm{lb} /$ mole",
                "si_factor": 1.0,
                "full_name": "pounds per pound mole",
                "notation": "$\\mathrm{lb} / \\mathrm{lb}-$ mol or $\\mathrm{lb} /$ mole",
                "aliases": ['lb / lb- mol', 'lb / mole'],
            }
        ],
        "aliases": {}
    },

    "concentration": {
        # Concentration - LENGTH^-3 MASS
        "dimension": CONCENTRATION,
        "units": [
            {
                "name": "grains_of_i_per_cubic_foot",
                "symbol": "$\\mathrm{gr} / \\mathrm{ft}^{3}$ or gr/cft",
                "si_factor": 0.002288,
                "full_name": "grains of \"i\" per cubic foot",
                "notation": "$\\mathrm{gr} / \\mathrm{ft}^{3}$ or gr/cft",
                "aliases": ['gr / ft^{3', 'gr/cft'],
            },
            {
                "name": "grains_of_i_per_gallon_us",
                "symbol": "gr/gal",
                "si_factor": 0.017115,
                "full_name": "grains of \"i\" per gallon (US)",
                "notation": "gr/gal",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "dynamic_fluidity": {
        # Dynamic Fluidity - LENGTH MASS^-1 TIME
        "dimension": DYNAMIC_FLUIDITY,
        "units": [
            {
                "name": "meter_seconds_per_kilogram",
                "symbol": "m s/kg",
                "si_factor": 1.0,
                "full_name": "meter-seconds per kilogram",
                "notation": "m s/kg",
                "aliases": [],
            },
            {
                "name": "rhe",
                "symbol": "rhe",
                "si_factor": 1.0,
                "full_name": "rhe",
                "notation": "rhe",
                "aliases": ['rhe'],
            },
            {
                "name": "square_foot_per_pound_second",
                "symbol": "$\\mathrm{ft}^{2}$ /(lb sec)",
                "si_factor": 0.002086,
                "full_name": "square foot per pound second",
                "notation": "$\\mathrm{ft}^{2}$ /(lb sec)",
                "aliases": [],
            },
            {
                "name": "square_meters_per_newton_per_second",
                "symbol": "$\\mathrm{m}^{2} /(\\mathrm{N} \\mathrm{s})$",
                "si_factor": 1.0,
                "full_name": "square meters per newton per second",
                "notation": "$\\mathrm{m}^{2} /(\\mathrm{N} \\mathrm{s})$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "electric_capacitance": {
        # Electric Capacitance - CURRENT^2 LENGTH^-2 MASS^-1 TIME^4
        "dimension": ELECTRIC_CAPACITANCE,
        "units": [
            {
                "name": "abfarad",
                "symbol": "emu cgs",
                "si_factor": 1000000000.0,
                "full_name": "abfarad",
                "notation": "emu cgs",
                "aliases": [],
            },
            {
                "name": "cm",
                "symbol": "\"cm\"",
                "si_factor": 1.1111e-12,
                "full_name": "\"cm\"",
                "notation": "\"cm\"",
                "aliases": [],
            },
            {
                "name": "farad",
                "symbol": "F",
                "si_factor": 1.0,
                "full_name": "farad",
                "notation": "F",
                "aliases": ['F'],
            },
            {
                "name": "farad_intl",
                "symbol": "F (int)",
                "si_factor": 0.99951,
                "full_name": "farad (intl)",
                "notation": "F (int)",
                "aliases": [],
            },
            {
                "name": "jar",
                "symbol": "jar",
                "si_factor": 1.1111e-09,
                "full_name": "jar",
                "notation": "jar",
                "aliases": ['jar'],
            },
            {
                "name": "microfarad",
                "symbol": "μF",
                "si_factor": 1e-06,
                "full_name": "microfarad",
                "notation": "μF",
                "aliases": [],
            },
            {
                "name": "millifarad",
                "symbol": "mF",
                "si_factor": 0.001,
                "full_name": "millifarad",
                "notation": "mF",
                "aliases": [],
            },
            {
                "name": "nanofarad",
                "symbol": "nF",
                "si_factor": 1e-09,
                "full_name": "nanofarad",
                "notation": "nF",
                "aliases": [],
            },
            {
                "name": "picofarad",
                "symbol": "pF",
                "si_factor": 1e-12,
                "full_name": "picofarad",
                "notation": "pF",
                "aliases": [],
            },
            {
                "name": "puff",
                "symbol": "puff",
                "si_factor": 1e-12,
                "full_name": "puff",
                "notation": "puff",
                "aliases": ['puff'],
            },
            {
                "name": "statfarad",
                "symbol": "esu cgs",
                "si_factor": 1.113e-12,
                "full_name": "statfarad",
                "notation": "esu cgs",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "electric_charge": {
        # Electric Charge - AMOUNT^-1 CURRENT TIME
        "dimension": ELECTRIC_CHARGE,
        "units": [
            {
                "name": "abcoulomb",
                "symbol": "emu cgs",
                "si_factor": 0.000103643,
                "full_name": "abcoulomb",
                "notation": "emu cgs",
                "aliases": [],
            },
            {
                "name": "ampere_hour",
                "symbol": "Ah",
                "si_factor": 0.03731138,
                "full_name": "ampere-hour",
                "notation": "Ah",
                "aliases": ['Ah'],
            },
            {
                "name": "coulomb",
                "symbol": "C",
                "si_factor": 1.0364000000000001e-05,
                "full_name": "coulomb",
                "notation": "C",
                "aliases": ['C'],
            },
            {
                "name": "faraday_c12",
                "symbol": "F",
                "si_factor": 1.0,
                "full_name": "faraday (C12)",
                "notation": "F",
                "aliases": ['F'],
            },
            {
                "name": "franklin",
                "symbol": "Fr",
                "si_factor": 3.45715e-15,
                "full_name": "franklin",
                "notation": "Fr",
                "aliases": ['Fr'],
            },
            {
                "name": "kilocoulomb",
                "symbol": "kC",
                "si_factor": 0.010364000000000002,
                "full_name": "kilocoulomb",
                "notation": "kC",
                "aliases": [],
            },
            {
                "name": "microcoulomb",
                "symbol": "μC",
                "si_factor": 1.0364e-11,
                "full_name": "microcoulomb",
                "notation": "μC",
                "aliases": [],
            },
            {
                "name": "millicoulomb",
                "symbol": "mC",
                "si_factor": 1.0364000000000001e-08,
                "full_name": "millicoulomb",
                "notation": "mC",
                "aliases": [],
            },
            {
                "name": "nanocoulomb",
                "symbol": "nC",
                "si_factor": 1.0364000000000002e-14,
                "full_name": "nanocoulomb",
                "notation": "nC",
                "aliases": [],
            },
            {
                "name": "picocoulomb",
                "symbol": "pC",
                "si_factor": 1.0364000000000001e-17,
                "full_name": "picocoulomb",
                "notation": "pC",
                "aliases": [],
            },
            {
                "name": "statcoulomb",
                "symbol": "esu cgs",
                "si_factor": 3.45715e-15,
                "full_name": "statcoulomb",
                "notation": "esu cgs",
                "aliases": [],
            },
            {
                "name": "u_a_charge",
                "symbol": "u.a.",
                "si_factor": 1.66054e-24,
                "full_name": "u.a. charge",
                "notation": "u.a.",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "electric_current_intensity": {
        # Electric Current Intensity - CURRENT
        "dimension": ELECTRIC_CURRENT_INTENSITY,
        "units": [
            {
                "name": "abampere",
                "symbol": "emu cgs",
                "si_factor": 10.0,
                "full_name": "abampere",
                "notation": "emu cgs",
                "aliases": [],
            },
            {
                "name": "ampere_intl_mean",
                "symbol": "A (int mean)",
                "si_factor": 0.99985,
                "full_name": "ampere (intl mean)",
                "notation": "A (int mean)",
                "aliases": [],
            },
            {
                "name": "ampere_intl_us",
                "symbol": "A (int US)",
                "si_factor": 0.999835,
                "full_name": "ampere (intl US)",
                "notation": "A (int US)",
                "aliases": [],
            },
            {
                "name": "ampere_or_amp",
                "symbol": "A",
                "si_factor": 1.0,
                "full_name": "ampere or amp",
                "notation": "A",
                "aliases": ['A'],
            },
            {
                "name": "biot",
                "symbol": "biot",
                "si_factor": 10.0,
                "full_name": "biot",
                "notation": "biot",
                "aliases": ['biot'],
            },
            {
                "name": "statampere",
                "symbol": "esu cgs",
                "si_factor": 3.33564e-10,
                "full_name": "statampere",
                "notation": "esu cgs",
                "aliases": [],
            },
            {
                "name": "u_a_or_current",
                "symbol": "u.a.",
                "si_factor": 0.00662362,
                "full_name": "u.a. or current",
                "notation": "u.a.",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "electric_dipole_moment": {
        # Electric Dipole Moment - CURRENT LENGTH TIME
        "dimension": ELECTRIC_DIPOLE_MOMENT,
        "units": [
            {
                "name": "ampere_meter_second",
                "symbol": "A m s",
                "si_factor": 1.0,
                "full_name": "ampere meter second",
                "notation": "A m s",
                "aliases": [],
            },
            {
                "name": "coulomb_meter",
                "symbol": "C m",
                "si_factor": 1.0,
                "full_name": "coulomb meter",
                "notation": "C m",
                "aliases": [],
            },
            {
                "name": "debye",
                "symbol": "D",
                "si_factor": 3.3356e-30,
                "full_name": "debye",
                "notation": "D",
                "aliases": ['D'],
            },
            {
                "name": "electron_meter",
                "symbol": "e m",
                "si_factor": 1.6022e-19,
                "full_name": "electron meter",
                "notation": "e m",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "electric_field_strength": {
        # Electric Field Strength - CURRENT^-1 LENGTH MASS TIME^-3
        "dimension": ELECTRIC_FIELD_STRENGTH,
        "units": [
            {
                "name": "volt_per_centimeter",
                "symbol": "V/cm",
                "si_factor": 100.0,
                "full_name": "volt per centimeter",
                "notation": "V/cm",
                "aliases": [],
            },
            {
                "name": "volt_per_meter",
                "symbol": "V/m",
                "si_factor": 1.0,
                "full_name": "volt per meter",
                "notation": "V/m",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "electric_inductance": {
        # Electric Inductance - CURRENT^-2 LENGTH^2 MASS TIME^-2
        "dimension": ELECTRIC_INDUCTANCE,
        "units": [
            {
                "name": "abhenry",
                "symbol": "emu cgs",
                "si_factor": 1e-09,
                "full_name": "abhenry",
                "notation": "emu cgs",
                "aliases": [],
            },
            {
                "name": "cm",
                "symbol": "cm",
                "si_factor": 1e-09,
                "full_name": "cm",
                "notation": "cm",
                "aliases": ['cm'],
            },
            {
                "name": "henry",
                "symbol": "H",
                "si_factor": 1.0,
                "full_name": "henry",
                "notation": "H",
                "aliases": ['H'],
            },
            {
                "name": "henry_intl_mean",
                "symbol": "H (int mean)",
                "si_factor": 1.00049,
                "full_name": "henry (intl mean)",
                "notation": "H (int mean)",
                "aliases": [],
            },
            {
                "name": "henry_intl_us",
                "symbol": "H (int US)",
                "si_factor": 1.000495,
                "full_name": "henry (intl US)",
                "notation": "H (int US)",
                "aliases": [],
            },
            {
                "name": "mic",
                "symbol": "mic",
                "si_factor": 1e-06,
                "full_name": "mic",
                "notation": "mic",
                "aliases": ['mic'],
            },
            {
                "name": "microhenry",
                "symbol": "μH",
                "si_factor": 1e-06,
                "full_name": "microhenry",
                "notation": "μH",
                "aliases": [],
            },
            {
                "name": "millihenry",
                "symbol": "mH",
                "si_factor": 0.001,
                "full_name": "millihenry",
                "notation": "mH",
                "aliases": [],
            },
            {
                "name": "nanohenry",
                "symbol": "nH",
                "si_factor": 1e-09,
                "full_name": "nanohenry",
                "notation": "nH",
                "aliases": [],
            },
            {
                "name": "stathenry",
                "symbol": "esu cgs",
                "si_factor": 898760000000.0,
                "full_name": "stathenry",
                "notation": "esu cgs",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "electric_potential": {
        # Electric Potential - CURRENT^-1 LENGTH^2 MASS TIME^-3
        "dimension": ELECTRIC_POTENTIAL,
        "units": [
            {
                "name": "abvolt",
                "symbol": "emu cgs",
                "si_factor": 1e-08,
                "full_name": "abvolt",
                "notation": "emu cgs",
                "aliases": [],
            },
            {
                "name": "kilovolt",
                "symbol": "kV",
                "si_factor": 1000.0,
                "full_name": "kilovolt",
                "notation": "kV",
                "aliases": [],
            },
            {
                "name": "microvolt",
                "symbol": "μV",
                "si_factor": 1e-06,
                "full_name": "microvolt",
                "notation": "μV",
                "aliases": [],
            },
            {
                "name": "millivolt",
                "symbol": "mV",
                "si_factor": 0.001,
                "full_name": "millivolt",
                "notation": "mV",
                "aliases": [],
            },
            {
                "name": "nanovolt",
                "symbol": "nV",
                "si_factor": 1e-09,
                "full_name": "nanovolt",
                "notation": "nV",
                "aliases": [],
            },
            {
                "name": "picovolt",
                "symbol": "pV",
                "si_factor": 1e-12,
                "full_name": "picovolt",
                "notation": "pV",
                "aliases": [],
            },
            {
                "name": "statvolt",
                "symbol": "esu cgs",
                "si_factor": 299.792,
                "full_name": "statvolt",
                "notation": "esu cgs",
                "aliases": [],
            },
            {
                "name": "u_a_potential",
                "symbol": "u.a.",
                "si_factor": 27.2114,
                "full_name": "u.a. potential",
                "notation": "u.a.",
                "aliases": [],
            },
            {
                "name": "volt",
                "symbol": "V",
                "si_factor": 1.0,
                "full_name": "volt",
                "notation": "V",
                "aliases": ['V'],
            },
            {
                "name": "volt_intl_mean",
                "symbol": "V (int mean)",
                "si_factor": 1.00034,
                "full_name": "volt (intl mean)",
                "notation": "V (int mean)",
                "aliases": [],
            },
            {
                "name": "volt_us",
                "symbol": "V (int US)",
                "si_factor": 1.00033,
                "full_name": "volt (US)",
                "notation": "V (int US)",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "electric_resistance": {
        # Electric Resistance - CURRENT^-2 LENGTH^2 MASS TIME^-3
        "dimension": ELECTRIC_RESISTANCE,
        "units": [
            {
                "name": "abohm",
                "symbol": "emu cgs",
                "si_factor": 1e-09,
                "full_name": "abohm",
                "notation": "emu cgs",
                "aliases": [],
            },
            {
                "name": "jacobi",
                "symbol": "-",
                "si_factor": 0.64,
                "full_name": "jacobi",
                "notation": "-",
                "aliases": [],
            },
            {
                "name": "kiloohm",
                "symbol": "k$\\Omega$",
                "si_factor": 1000.0,
                "full_name": "kiloohm",
                "notation": "k$\\Omega$",
                "aliases": [],
            },
            {
                "name": "lenz",
                "symbol": "Metric",
                "si_factor": 80000.0,
                "full_name": "lenz",
                "notation": "Metric",
                "aliases": [],
            },
            {
                "name": "megaohm",
                "symbol": "M$\\Omega$",
                "si_factor": 1000000.0,
                "full_name": "megaohm",
                "notation": "M$\\Omega$",
                "aliases": [],
            },
            {
                "name": "milliohm",
                "symbol": "m$\\Omega$",
                "si_factor": 0.001,
                "full_name": "milliohm",
                "notation": "m$\\Omega$",
                "aliases": [],
            },
            {
                "name": "ohm",
                "symbol": "$\\Omega$",
                "si_factor": 1.0,
                "full_name": "ohm",
                "notation": "$\\Omega$",
                "aliases": [],
            },
            {
                "name": "ohm_intl_mean",
                "symbol": "$\\Omega$ (int mean)",
                "si_factor": 1.00049,
                "full_name": "ohm (intl mean)",
                "notation": "$\\Omega$ (int mean)",
                "aliases": [],
            },
            {
                "name": "ohm_intl_us",
                "symbol": "$\\Omega$ (int US)",
                "si_factor": 1.000495,
                "full_name": "ohm (intl US)",
                "notation": "$\\Omega$ (int US)",
                "aliases": [],
            },
            {
                "name": "ohm_legal",
                "symbol": "$\\Omega$ (legal)",
                "si_factor": 0.9972,
                "full_name": "ohm (legal)",
                "notation": "$\\Omega$ (legal)",
                "aliases": [],
            },
            {
                "name": "preece",
                "symbol": "preece",
                "si_factor": 1000000.0,
                "full_name": "preece",
                "notation": "preece",
                "aliases": [],
            },
            {
                "name": "statohm",
                "symbol": "csu cgs",
                "si_factor": 8.987552,
                "full_name": "statohm",
                "notation": "csu cgs",
                "aliases": [],
            },
            {
                "name": "wheatstone",
                "symbol": "-",
                "si_factor": 0.0025,
                "full_name": "wheatstone",
                "notation": "-",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "electrical_conductance": {
        # Electrical Conductance - CURRENT^2 LENGTH^-2 MASS^-1 TIME^3
        "dimension": ELECTRICAL_CONDUCTANCE,
        "units": [
            {
                "name": "emu_cgs",
                "symbol": "abmho",
                "si_factor": 1000000000.0,
                "full_name": "emu cgs",
                "notation": "abmho",
                "aliases": [],
            },
            {
                "name": "esu_cgs",
                "symbol": "statmho",
                "si_factor": 1.1127e-12,
                "full_name": "esu cgs",
                "notation": "statmho",
                "aliases": [],
            },
            {
                "name": "mho",
                "symbol": "mho",
                "si_factor": 1.0,
                "full_name": "mho",
                "notation": "mho",
                "aliases": ['mho'],
            },
            {
                "name": "microsiemens",
                "symbol": "$\\mu \\mathrm{S}$",
                "si_factor": 1e-06,
                "full_name": "microsiemens",
                "notation": "$\\mu \\mathrm{S}$",
                "aliases": [],
            },
            {
                "name": "millisiemens",
                "symbol": "mS",
                "si_factor": 0.001,
                "full_name": "millisiemens",
                "notation": "mS",
                "aliases": [],
            },
            {
                "name": "siemens",
                "symbol": "S",
                "si_factor": 1.0,
                "full_name": "siemens",
                "notation": "S",
                "aliases": ['S'],
            }
        ],
        "aliases": {}
    },

    "electrical_permittivity": {
        # Electrical Permittivity - CURRENT^2 LENGTH^-3 MASS^-1 TIME^4
        "dimension": ELECTRICAL_PERMITTIVITY,
        "units": [
            {
                "name": "farad_per_meter",
                "symbol": "F/m",
                "si_factor": 1.0,
                "full_name": "farad per meter",
                "notation": "F/m",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "electrical_resistivity": {
        # Electrical Resistivity - CURRENT^-2 LENGTH^3 MASS TIME^-3
        "dimension": ELECTRICAL_RESISTIVITY,
        "units": [
            {
                "name": "circular_mil_ohm_per_foot",
                "symbol": "circmil $\\Omega / \\mathrm{ft}$",
                "si_factor": 1.6624000000000002e-09,
                "full_name": "circular mil-ohm per foot",
                "notation": "circmil $\\Omega / \\mathrm{ft}$",
                "aliases": [],
            },
            {
                "name": "emu_cgs",
                "symbol": "abohm cm",
                "si_factor": 1e-11,
                "full_name": "emu cgs",
                "notation": "abohm cm",
                "aliases": [],
            },
            {
                "name": "microhm_inch",
                "symbol": "$\\mu \\Omega$ in",
                "si_factor": 2.5400000000000002e-08,
                "full_name": "microhm-inch",
                "notation": "$\\mu \\Omega$ in",
                "aliases": [],
            },
            {
                "name": "ohm_centimeter",
                "symbol": "$\\boldsymbol{\\Omega} \\mathbf{c m}$",
                "si_factor": 0.01,
                "full_name": "ohm-centimeter",
                "notation": "$\\boldsymbol{\\Omega} \\mathbf{c m}$",
                "aliases": [],
            },
            {
                "name": "ohm_meter",
                "symbol": "$\\Omega \\mathrm{m}$",
                "si_factor": 1.0,
                "full_name": "ohm-meter",
                "notation": "$\\Omega \\mathrm{m}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "energy_flux": {
        # Energy Flux - MASS TIME^-3
        "dimension": ENERGY_FLUX,
        "units": [
            {
                "name": "btu_per_square_foot_per_hour",
                "symbol": "$\\mathrm{Btu} / \\mathrm{ft}^{2} / \\mathrm{hr}$",
                "si_factor": 3.1546,
                "full_name": "Btu per square foot per hour",
                "notation": "$\\mathrm{Btu} / \\mathrm{ft}^{2} / \\mathrm{hr}$",
                "aliases": [],
            },
            {
                "name": "calorie_per_square_centimeter_per_second",
                "symbol": "$\\mathrm{cal} / \\mathrm{cm}^{2} / \\mathrm{s}$ or $\\mathrm{cal} /$ ( $\\mathrm{cm}^{2} \\mathrm{~s}$ )",
                "si_factor": 41868.0,
                "full_name": "calorie per square centimeter per second",
                "notation": "$\\mathrm{cal} / \\mathrm{cm}^{2} / \\mathrm{s}$ or $\\mathrm{cal} /$ ( $\\mathrm{cm}^{2} \\mathrm{~s}$ )",
                "aliases": ['cal / cm^{2 / s', 'cal / ( cm^{2 ~s )'],
            },
            {
                "name": "celsius_heat_units_chu",
                "symbol": "$\\mathrm{Chu} / \\mathrm{ft}^{2} / \\mathrm{hr}$",
                "si_factor": 5.6784,
                "full_name": "Celsius heat units (Chu) per square foot per hour",
                "notation": "$\\mathrm{Chu} / \\mathrm{ft}^{2} / \\mathrm{hr}$",
                "aliases": [],
            },
            {
                "name": "kilocalorie_per_square_foot_per_hour",
                "symbol": "$\\mathrm{kcal} /\\left(\\mathrm{ft}^{2} \\mathrm{hr}\\right)$",
                "si_factor": 12.518,
                "full_name": "kilocalorie per square foot per hour",
                "notation": "$\\mathrm{kcal} /\\left(\\mathrm{ft}^{2} \\mathrm{hr}\\right)$",
                "aliases": [],
            },
            {
                "name": "kilocalorie_per_square_meter_per_hour",
                "symbol": "$\\mathrm{kcal} /\\left(\\mathrm{m}^{2} \\mathrm{hr}\\right)$",
                "si_factor": 1.163,
                "full_name": "kilocalorie per square meter per hour",
                "notation": "$\\mathrm{kcal} /\\left(\\mathrm{m}^{2} \\mathrm{hr}\\right)$",
                "aliases": [],
            },
            {
                "name": "watt_per_square_meter",
                "symbol": "$\\mathrm{W} / \\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "watt per square meter",
                "notation": "$\\mathrm{W} / \\mathrm{m}^{2}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "energy_heat_work": {
        # Energy, Heat, Work - LENGTH^2 MASS TIME^-2
        "dimension": ENERGY_HEAT_WORK,
        "units": [
            {
                "name": "barrel_oil_equivalent_or_equivalent_barrel",
                "symbol": "bboe or boe",
                "si_factor": 6120000000.0,
                "full_name": "barrel oil equivalent or equivalent barrel",
                "notation": "bboe or boe",
                "aliases": ['bboe', 'boe'],
            },
            {
                "name": "billion_electronvolt",
                "symbol": "BeV",
                "si_factor": 1.6022000000000002e-10,
                "full_name": "billion electronvolt",
                "notation": "BeV",
                "aliases": ['BeV'],
            },
            {
                "name": "british_thermal_unit_4circ_mathrmc",
                "symbol": "Btu ( $39.2{ }^{\\circ} \\mathrm{F}$ )",
                "si_factor": 1059.67,
                "full_name": "British thermal unit ( $4^{\\circ} \\mathrm{C}$ )",
                "notation": "Btu ( $39.2{ }^{\\circ} \\mathrm{F}$ )",
                "aliases": [],
            },
            {
                "name": "british_thermal_unit_60circ_mathrmf",
                "symbol": "Btu ( $60{ }^{\\circ} \\mathrm{F}$ )",
                "si_factor": 1054.678,
                "full_name": "British thermal unit ( $60^{\\circ} \\mathrm{F}$ )",
                "notation": "Btu ( $60{ }^{\\circ} \\mathrm{F}$ )",
                "aliases": [],
            },
            {
                "name": "british_thermal_unit_international_steam_tables",
                "symbol": "Btu (IT)",
                "si_factor": 1055.055853,
                "full_name": "British thermal unit (international steam tables)",
                "notation": "Btu (IT)",
                "aliases": [],
            },
            {
                "name": "british_thermal_unit_isotc_12",
                "symbol": "Btu (ISO)",
                "si_factor": 1055.06,
                "full_name": "British thermal unit (ISO/TC 12)",
                "notation": "Btu (ISO)",
                "aliases": [],
            },
            {
                "name": "british_thermal_unit_mean",
                "symbol": "Btu (mean) or Btu",
                "si_factor": 1055.87,
                "full_name": "British thermal unit (mean)",
                "notation": "Btu (mean) or Btu",
                "aliases": ['Btu (mean)', 'Btu'],
            },
            {
                "name": "british_thermal_unit_thermochemical",
                "symbol": "Btu (therm)",
                "si_factor": 1054.35,
                "full_name": "British thermal unit (thermochemical)",
                "notation": "Btu (therm)",
                "aliases": [],
            },
            {
                "name": "calorie_20circ_mathrmc",
                "symbol": "cal ( $20^{\\circ} \\mathrm{C}$ )",
                "si_factor": 4.1819,
                "full_name": "calorie ( $20^{\\circ} \\mathrm{C}$ )",
                "notation": "cal ( $20^{\\circ} \\mathrm{C}$ )",
                "aliases": [],
            },
            {
                "name": "calorie_4circ_mathrmc",
                "symbol": "cal ( $4^{\\circ} \\mathrm{C}$ )",
                "si_factor": 4.2045,
                "full_name": "calorie ( $4^{\\circ} \\mathrm{C}$ )",
                "notation": "cal ( $4^{\\circ} \\mathrm{C}$ )",
                "aliases": [],
            },
            {
                "name": "calorie_international_steam_tables",
                "symbol": "cal (IT)",
                "si_factor": 4.18674,
                "full_name": "calorie (international steam tables)",
                "notation": "cal (IT)",
                "aliases": [],
            },
            {
                "name": "calorie_mean",
                "symbol": "cal (mean)",
                "si_factor": 4.19002,
                "full_name": "calorie (mean)",
                "notation": "cal (mean)",
                "aliases": [],
            },
            {
                "name": "calorie_nutritional",
                "symbol": "Cal (nutr)",
                "si_factor": 4184.0,
                "full_name": "Calorie (nutritional)",
                "notation": "Cal (nutr)",
                "aliases": [],
            },
            {
                "name": "calorie_thermochemical",
                "symbol": "cal (therm)",
                "si_factor": 4.184,
                "full_name": "calorie (thermochemical)",
                "notation": "cal (therm)",
                "aliases": [],
            },
            {
                "name": "celsius_heat_unit",
                "symbol": "Chu",
                "si_factor": 1899.18,
                "full_name": "Celsius heat unit",
                "notation": "Chu",
                "aliases": ['Chu'],
            },
            {
                "name": "celsius_heat_unit_15_circ_mathrmc",
                "symbol": "Chu ( $15{ }^{\\circ} \\mathrm{C}$ )",
                "si_factor": 1899.1,
                "full_name": "Celsius heat unit ( $15{ }^{\\circ} \\mathrm{C}$ )",
                "notation": "Chu ( $15{ }^{\\circ} \\mathrm{C}$ )",
                "aliases": [],
            },
            {
                "name": "electron_volt",
                "symbol": "eV",
                "si_factor": 1.6022e-19,
                "full_name": "electron volt",
                "notation": "eV",
                "aliases": ['eV'],
            },
            {
                "name": "erg",
                "symbol": "erg",
                "si_factor": 1e-07,
                "full_name": "erg",
                "notation": "erg",
                "aliases": ['erg'],
            },
            {
                "name": "foot_pound_force_duty",
                "symbol": "ft $\\mathrm{lb}_{\\mathrm{f}}$",
                "si_factor": 1.355818,
                "full_name": "foot pound force (duty)",
                "notation": "ft $\\mathrm{lb}_{\\mathrm{f}}$",
                "aliases": [],
            },
            {
                "name": "foot_poundal",
                "symbol": "ft pdl",
                "si_factor": 0.04214,
                "full_name": "foot-poundal",
                "notation": "ft pdl",
                "aliases": [],
            },
            {
                "name": "frigorie",
                "symbol": "fg",
                "si_factor": 4190.0,
                "full_name": "frigorie",
                "notation": "fg",
                "aliases": ['fg'],
            },
            {
                "name": "gigajoule",
                "symbol": "GJ",
                "si_factor": 1000000000.0,
                "full_name": "gigajoule",
                "notation": "GJ",
                "aliases": [],
            },
            {
                "name": "hartree_atomic_unit_of_energy",
                "symbol": "$\\mathrm{E}_{\\mathrm{H}}$ a.u.",
                "si_factor": 4.359700000000001e-18,
                "full_name": "hartree (atomic unit of energy)",
                "notation": "$\\mathrm{E}_{\\mathrm{H}}$ a.u.",
                "aliases": [],
            },
            {
                "name": "joule",
                "symbol": "J",
                "si_factor": 1.0,
                "full_name": "joule",
                "notation": "J",
                "aliases": ['J'],
            },
            {
                "name": "joule_international",
                "symbol": "J (intl)",
                "si_factor": 1.000165,
                "full_name": "joule (international)",
                "notation": "J (intl)",
                "aliases": [],
            },
            {
                "name": "kilocalorie_thermal",
                "symbol": "kcal (therm)",
                "si_factor": 4184.0,
                "full_name": "kilocalorie (thermal)",
                "notation": "kcal (therm)",
                "aliases": [],
            },
            {
                "name": "kilogram_force_meter",
                "symbol": "$\\mathrm{kg}_{\\mathrm{f}}$ m",
                "si_factor": 9.80665,
                "full_name": "kilogram force meter",
                "notation": "$\\mathrm{kg}_{\\mathrm{f}}$ m",
                "aliases": [],
            },
            {
                "name": "kilojoule",
                "symbol": "kJ",
                "si_factor": 1000.0,
                "full_name": "kilojoule",
                "notation": "kJ",
                "aliases": [],
            },
            {
                "name": "kiloton_tnt",
                "symbol": "kt (TNT)",
                "si_factor": 4.1799999999999995e+18,
                "full_name": "kiloton (TNT)",
                "notation": "kt (TNT)",
                "aliases": [],
            },
            {
                "name": "kilowatt_hour",
                "symbol": "kWh",
                "si_factor": 3600000.0,
                "full_name": "kilowatt hour",
                "notation": "kWh",
                "aliases": ['kWh'],
            },
            {
                "name": "liter_atmosphere",
                "symbol": "L atm",
                "si_factor": 101.325,
                "full_name": "liter atmosphere",
                "notation": "L atm",
                "aliases": [],
            },
            {
                "name": "megajoule",
                "symbol": "MJ",
                "si_factor": 1000000.0,
                "full_name": "megajoule",
                "notation": "MJ",
                "aliases": [],
            },
            {
                "name": "megaton_tnt",
                "symbol": "Mt (TNT)",
                "si_factor": 4.1799999999999995e+21,
                "full_name": "megaton (TNT)",
                "notation": "Mt (TNT)",
                "aliases": [],
            },
            {
                "name": "pound_centigrade_unit_15circ_mathrmc",
                "symbol": "pcu ( $15{ }^{\\circ} \\mathrm{C}$ )",
                "si_factor": 1899.1,
                "full_name": "pound centigrade unit ( $15^{\\circ} \\mathrm{C}$ )",
                "notation": "pcu ( $15{ }^{\\circ} \\mathrm{C}$ )",
                "aliases": [],
            },
            {
                "name": "prout",
                "symbol": "prout",
                "si_factor": 2.9638e-14,
                "full_name": "prout",
                "notation": "prout",
                "aliases": [],
            },
            {
                "name": "q_unit",
                "symbol": "Q",
                "si_factor": 1.055e+21,
                "full_name": "Q unit",
                "notation": "Q",
                "aliases": ['Q'],
            },
            {
                "name": "quad_quadrillion_btu",
                "symbol": "quad",
                "si_factor": 1.0550999999999999e+18,
                "full_name": "quad (quadrillion Btu)",
                "notation": "quad",
                "aliases": ['quad'],
            },
            {
                "name": "rydberg",
                "symbol": "Ry",
                "si_factor": 2.1799000000000002e-18,
                "full_name": "rydberg",
                "notation": "Ry",
                "aliases": ['Ry'],
            },
            {
                "name": "therm_eeg",
                "symbol": "therm (EEG)",
                "si_factor": 105510000.0,
                "full_name": "therm (EEG)",
                "notation": "therm (EEG)",
                "aliases": [],
            },
            {
                "name": "therm_refineries",
                "symbol": "therm (refy) or therm",
                "si_factor": 1055900000.0000001,
                "full_name": "therm (refineries)",
                "notation": "therm (refy) or therm",
                "aliases": ['therm (refy)', 'therm'],
            },
            {
                "name": "therm_us",
                "symbol": "therm (US) or therm",
                "si_factor": 105480000.0,
                "full_name": "therm (US)",
                "notation": "therm (US) or therm",
                "aliases": ['therm'],
            },
            {
                "name": "ton_coal_equivalent",
                "symbol": "tce (tec)",
                "si_factor": 292900000.0,
                "full_name": "ton coal equivalent",
                "notation": "tce (tec)",
                "aliases": [],
            },
            {
                "name": "ton_oil_equivalent",
                "symbol": "toe (tep)",
                "si_factor": 418700000.0,
                "full_name": "ton oil equivalent",
                "notation": "toe (tep)",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "energy_per_unit_area": {
        # Energy per Unit Area - MASS TIME^-2
        "dimension": ENERGY_PER_UNIT_AREA,
        "units": [
            {
                "name": "british_thermal_unit_per_square_foot",
                "symbol": "$\\mathrm{Btu} / \\mathrm{ft}^{2}$ or Btu/sq ft",
                "si_factor": 11354.0,
                "full_name": "British thermal unit per square foot",
                "notation": "$\\mathrm{Btu} / \\mathrm{ft}^{2}$ or Btu/sq ft",
                "aliases": ['Btu / ft^{2', 'Btu/sq ft'],
            },
            {
                "name": "joule_per_square_meter",
                "symbol": "$\\mathrm{J} / \\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "joule per square meter",
                "notation": "$\\mathrm{J} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "langley",
                "symbol": "Ly",
                "si_factor": 41840.0,
                "full_name": "Langley",
                "notation": "Ly",
                "aliases": ['Ly'],
            }
        ],
        "aliases": {}
    },

    "force": {
        # Force - LENGTH MASS TIME^-2
        "dimension": FORCE,
        "units": [
            {
                "name": "crinal",
                "symbol": "crinal",
                "si_factor": 0.1,
                "full_name": "crinal",
                "notation": "crinal",
                "aliases": [],
            },
            {
                "name": "dyne",
                "symbol": "dyn",
                "si_factor": 1e-05,
                "full_name": "dyne",
                "notation": "dyn",
                "aliases": ['dyn'],
            },
            {
                "name": "funal",
                "symbol": "funal",
                "si_factor": 1000.0,
                "full_name": "funal",
                "notation": "funal",
                "aliases": [],
            },
            {
                "name": "kilogram_force",
                "symbol": "$\\mathrm{kg}_{\\mathrm{f}}$",
                "si_factor": 9.80665,
                "full_name": "kilogram force",
                "notation": "$\\mathrm{kg}_{\\mathrm{f}}$",
                "aliases": [],
            },
            {
                "name": "kilonewton",
                "symbol": "kN",
                "si_factor": 1000.0,
                "full_name": "kilonewton",
                "notation": "kN",
                "aliases": [],
            },
            {
                "name": "kip_force",
                "symbol": "$\\operatorname{kip}_{\\mathrm{f}}$",
                "si_factor": 4448.22,
                "full_name": "kip force",
                "notation": "$\\operatorname{kip}_{\\mathrm{f}}$",
                "aliases": [],
            },
            {
                "name": "millinewton",
                "symbol": "mN",
                "si_factor": 0.001,
                "full_name": "millinewton",
                "notation": "mN",
                "aliases": [],
            },
            {
                "name": "newton",
                "symbol": "N",
                "si_factor": 1.0,
                "full_name": "newton",
                "notation": "N",
                "aliases": ['N'],
            },
            {
                "name": "ounce_force",
                "symbol": "$\\mathrm{oz}_{\\mathrm{f}}$ or oz",
                "si_factor": 0.27801385,
                "full_name": "ounce force",
                "notation": "$\\mathrm{oz}_{\\mathrm{f}}$ or oz",
                "aliases": ['oz_{f', 'oz'],
            },
            {
                "name": "pond",
                "symbol": "p",
                "si_factor": 0.0098066,
                "full_name": "pond",
                "notation": "p",
                "aliases": ['p'],
            },
            {
                "name": "pound_force",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}}$ or lb",
                "si_factor": 4.4482216,
                "full_name": "pound force",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}}$ or lb",
                "aliases": ['lb_{f', 'lb'],
            },
            {
                "name": "poundal",
                "symbol": "pdl",
                "si_factor": 0.13825495,
                "full_name": "poundal",
                "notation": "pdl",
                "aliases": ['pdl'],
            },
            {
                "name": "slug_force",
                "symbol": "$\\operatorname{slug}_{f}$",
                "si_factor": 143.117,
                "full_name": "slug force",
                "notation": "$\\operatorname{slug}_{f}$",
                "aliases": [],
            },
            {
                "name": "sthène",
                "symbol": "sn",
                "si_factor": 1000.0,
                "full_name": "sthène",
                "notation": "sn",
                "aliases": ['sn'],
            },
            {
                "name": "ton_force_long",
                "symbol": "LT",
                "si_factor": 9964.016,
                "full_name": "ton (force, long)",
                "notation": "LT",
                "aliases": ['LT'],
            },
            {
                "name": "ton_force_metric",
                "symbol": "MT",
                "si_factor": 9806.65,
                "full_name": "ton (force, metric)",
                "notation": "MT",
                "aliases": ['MT'],
            },
            {
                "name": "ton_force_short",
                "symbol": "T",
                "si_factor": 8896.44,
                "full_name": "ton (force, short)",
                "notation": "T",
                "aliases": ['T'],
            }
        ],
        "aliases": {}
    },

    "force_body": {
        # Force (Body) - LENGTH^-2 MASS TIME^-2
        "dimension": FORCE_BODY,
        "units": [
            {
                "name": "dyne_per_cubic_centimeter",
                "symbol": "dyn/cc or dyn/ $\\mathrm{cm}^{3}$",
                "si_factor": 10.0,
                "full_name": "dyne per cubic centimeter",
                "notation": "dyn/cc or dyn/ $\\mathrm{cm}^{3}$",
                "aliases": ['dyn/cc', 'dyn/ cm^{3'],
            },
            {
                "name": "kilogram_force_per_cubic_centimeter",
                "symbol": "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{cm}^{3}$",
                "si_factor": 9806700.0,
                "full_name": "kilogram force per cubic centimeter",
                "notation": "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{cm}^{3}$",
                "aliases": [],
            },
            {
                "name": "kilogram_force_per_cubic_meter",
                "symbol": "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{m}^{3}$",
                "si_factor": 9.80665,
                "full_name": "kilogram force per cubic meter",
                "notation": "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "newton_per_cubic_meter",
                "symbol": "$\\mathrm{N} / \\mathrm{m}^{3}$",
                "si_factor": 1.0,
                "full_name": "newton per cubic meter",
                "notation": "$\\mathrm{N} / \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "pound_force_per_cubic_foot",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{cft}$",
                "si_factor": 157.087,
                "full_name": "pound force per cubic foot",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{cft}$",
                "aliases": [],
            },
            {
                "name": "pound_force_per_cubic_inch",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{cu} . \\mathrm{in}$.",
                "si_factor": 271450.0,
                "full_name": "pound force per cubic inch",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{cu} . \\mathrm{in}$.",
                "aliases": [],
            },
            {
                "name": "ton_force_per_cubic_foot",
                "symbol": "ton $_{\\mathrm{f}} / \\mathrm{cft}$",
                "si_factor": 351880.0,
                "full_name": "ton force per cubic foot",
                "notation": "ton $_{\\mathrm{f}} / \\mathrm{cft}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "force_per_unit_mass": {
        # Force per Unit Mass - LENGTH TIME^-2
        "dimension": FORCE_PER_UNIT_MASS,
        "units": [
            {
                "name": "dyne_per_gram",
                "symbol": "dyn/g",
                "si_factor": 0.01,
                "full_name": "dyne per gram",
                "notation": "dyn/g",
                "aliases": [],
            },
            {
                "name": "kilogram_force_per_kilogram",
                "symbol": "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{kg}$",
                "si_factor": 9.80665,
                "full_name": "kilogram force per kilogram",
                "notation": "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{kg}$",
                "aliases": [],
            },
            {
                "name": "newton_per_kilogram",
                "symbol": "N/kg",
                "si_factor": 1.0,
                "full_name": "newton per kilogram",
                "notation": "N/kg",
                "aliases": [],
            },
            {
                "name": "pound_force_per_pound_mass",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{lb}$ or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{lb}_{\\mathrm{m}}$",
                "si_factor": 9.80665,
                "full_name": "pound force per pound mass",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{lb}$ or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{lb}_{\\mathrm{m}}$",
                "aliases": ['lb_{f / lb', 'lb_{f / lb_{m'],
            },
            {
                "name": "pound_force_per_slug",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}} /$ slug",
                "si_factor": 0.3048,
                "full_name": "pound force per slug",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}} /$ slug",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "frequency_voltage_ratio": {
        # Frequency Voltage Ratio - CURRENT LENGTH^-2 MASS^-1 TIME^3
        "dimension": FREQUENCY_VOLTAGE_RATIO,
        "units": [
            {
                "name": "cycles_per_second_per_volt",
                "symbol": "cycle/(sec V)",
                "si_factor": 1.0,
                "full_name": "cycles per second per volt",
                "notation": "cycle/(sec V)",
                "aliases": [],
            },
            {
                "name": "hertz_per_volt",
                "symbol": "Hz/V",
                "si_factor": 1.0,
                "full_name": "hertz per volt",
                "notation": "Hz/V",
                "aliases": [],
            },
            {
                "name": "terahertz_per_volt",
                "symbol": "THz/V",
                "si_factor": 1000000000000.0,
                "full_name": "terahertz per volt",
                "notation": "THz/V",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "fuel_consumption": {
        # Fuel Consumption - LENGTH^-2
        "dimension": FUEL_CONSUMPTION,
        "units": [
            {
                "name": "100_km_per_liter",
                "symbol": "$100 \\mathrm{~km} / \\mathrm{l}$",
                "si_factor": 100.0,
                "full_name": "100 km per liter",
                "notation": "$100 \\mathrm{~km} / \\mathrm{l}$",
                "aliases": [],
            },
            {
                "name": "gallons_uk",
                "symbol": "gal (UK)/ 100 mi",
                "si_factor": 35.4,
                "full_name": "gallons (UK) per 100 miles",
                "notation": "gal (UK)/ 100 mi",
                "aliases": [],
            },
            {
                "name": "gallons_us",
                "symbol": "gal (US)/ 100 mi",
                "si_factor": 42.51,
                "full_name": "gallons (US) per 100 miles",
                "notation": "gal (US)/ 100 mi",
                "aliases": [],
            },
            {
                "name": "kilometers_per_gallon_uk",
                "symbol": "km/gal (UK)",
                "si_factor": 0.21997,
                "full_name": "kilometers per gallon (UK)",
                "notation": "km/gal (UK)",
                "aliases": [],
            },
            {
                "name": "kilometers_per_gallon_us",
                "symbol": "km/gal(US)",
                "si_factor": 0.26417,
                "full_name": "kilometers per gallon (US)",
                "notation": "km/gal(US)",
                "aliases": [],
            },
            {
                "name": "kilometers_per_liter",
                "symbol": "km/l",
                "si_factor": 1.0,
                "full_name": "kilometers per liter",
                "notation": "km/l",
                "aliases": [],
            },
            {
                "name": "liters_per_100_km",
                "symbol": "$1 / 100 \\mathrm{~km}$",
                "si_factor": 100.0,
                "full_name": "liters per 100 km",
                "notation": "$1 / 100 \\mathrm{~km}$",
                "aliases": [],
            },
            {
                "name": "liters_per_kilometer",
                "symbol": "1/km",
                "si_factor": 1.0,
                "full_name": "liters per kilometer",
                "notation": "1/km",
                "aliases": [],
            },
            {
                "name": "meters_per_gallon_uk",
                "symbol": "m/gal (UK)",
                "si_factor": 0.00021997,
                "full_name": "meters per gallon (UK)",
                "notation": "m/gal (UK)",
                "aliases": [],
            },
            {
                "name": "meters_per_gallon_us",
                "symbol": "1/gal (US)",
                "si_factor": 0.00022642000000000004,
                "full_name": "meters per gallon (US)",
                "notation": "1/gal (US)",
                "aliases": [],
            },
            {
                "name": "miles_per_gallon_uk",
                "symbol": "mi/gal (UK) or mpg (UK)",
                "si_factor": 0.35401,
                "full_name": "miles per gallon (UK)",
                "notation": "mi/gal (UK) or mpg (UK)",
                "aliases": ['mi/gal (UK)', 'mpg (UK)'],
            },
            {
                "name": "miles_per_gallon_us",
                "symbol": "mi/gal (US) or mpg (US)",
                "si_factor": 0.42514,
                "full_name": "miles per gallon (US)",
                "notation": "mi/gal (US) or mpg (US)",
                "aliases": ['mi/gal (US)', 'mpg (US)'],
            },
            {
                "name": "miles_per_liter",
                "symbol": "mi/l",
                "si_factor": 1.6093,
                "full_name": "miles per liter",
                "notation": "mi/l",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "heat_of_combustion": {
        # Heat of Combustion - LENGTH^2 TIME^-2
        "dimension": HEAT_OF_COMBUSTION,
        "units": [
            {
                "name": "british_thermal_unit_per_pound",
                "symbol": "Btu/lb",
                "si_factor": 2326.0,
                "full_name": "British thermal unit per pound",
                "notation": "Btu/lb",
                "aliases": [],
            },
            {
                "name": "calorie_per_gram",
                "symbol": "$\\mathrm{cal} / \\mathrm{g}$",
                "si_factor": 4186.0,
                "full_name": "calorie per gram",
                "notation": "$\\mathrm{cal} / \\mathrm{g}$",
                "aliases": [],
            },
            {
                "name": "chu_per_pound",
                "symbol": "Chu/lb",
                "si_factor": 4186.8,
                "full_name": "Chu per pound",
                "notation": "Chu/lb",
                "aliases": [],
            },
            {
                "name": "joule_per_kilogram",
                "symbol": "J/kg",
                "si_factor": 1.0,
                "full_name": "joule per kilogram",
                "notation": "J/kg",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "heat_of_fusion": {
        # Heat of Fusion - LENGTH^2 TIME^-2
        "dimension": HEAT_OF_FUSION,
        "units": [
            {
                "name": "british_thermal_unit_mean",
                "symbol": "Btu (mean)/lb",
                "si_factor": 2327.79,
                "full_name": "British thermal unit (mean) per pound",
                "notation": "Btu (mean)/lb",
                "aliases": [],
            },
            {
                "name": "british_thermal_unit_per_pound",
                "symbol": "Btu/lb",
                "si_factor": 2326.0,
                "full_name": "British thermal unit per pound",
                "notation": "Btu/lb",
                "aliases": [],
            },
            {
                "name": "calorie_per_gram",
                "symbol": "$\\mathrm{cal} / \\mathrm{g}$",
                "si_factor": 4186.0,
                "full_name": "calorie per gram",
                "notation": "$\\mathrm{cal} / \\mathrm{g}$",
                "aliases": [],
            },
            {
                "name": "chu_per_pound",
                "symbol": "Chu/lb",
                "si_factor": 4186.8,
                "full_name": "Chu per pound",
                "notation": "Chu/lb",
                "aliases": [],
            },
            {
                "name": "joule_per_kilogram",
                "symbol": "J/kg",
                "si_factor": 1.0,
                "full_name": "joule per kilogram",
                "notation": "J/kg",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "heat_of_vaporization": {
        # Heat of Vaporization - LENGTH^2 TIME^-2
        "dimension": HEAT_OF_VAPORIZATION,
        "units": [
            {
                "name": "british_thermal_unit_per_pound",
                "symbol": "Btu/lb",
                "si_factor": 2326.0,
                "full_name": "British thermal unit per pound",
                "notation": "Btu/lb",
                "aliases": [],
            },
            {
                "name": "calorie_per_gram",
                "symbol": "$\\mathrm{cal} / \\mathrm{g}$",
                "si_factor": 4186.0,
                "full_name": "calorie per gram",
                "notation": "$\\mathrm{cal} / \\mathrm{g}$",
                "aliases": [],
            },
            {
                "name": "chu_per_pound",
                "symbol": "Chu/lb",
                "si_factor": 4186.8,
                "full_name": "Chu per pound",
                "notation": "Chu/lb",
                "aliases": [],
            },
            {
                "name": "joule_per_kilogram",
                "symbol": "J/kg",
                "si_factor": 1.0,
                "full_name": "joule per kilogram",
                "notation": "J/kg",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "heat_transfer_coefficient": {
        # Heat Transfer Coefficient - MASS TEMP^-1 TIME^-3
        "dimension": HEAT_TRANSFER_COEFFICIENT,
        "units": [
            {
                "name": "btu_per_square_foot_per_hour_per_degree_fahrenheit_or_rankine",
                "symbol": "$\\mathrm{Btu} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}{ }^{\\circ} \\mathrm{F}\\right)$",
                "si_factor": 5.679,
                "full_name": "Btu per square foot per hour per degree Fahrenheit (or Rankine)",
                "notation": "$\\mathrm{Btu} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}{ }^{\\circ} \\mathrm{F}\\right)$",
                "aliases": [],
            },
            {
                "name": "watt_per_square_meter_per_degree_celsius_or_kelvin",
                "symbol": "$\\mathrm{W} /\\left(\\mathrm{m}^{2}{ }^{\\circ} \\mathrm{C}\\right)$",
                "si_factor": 1.0,
                "full_name": "watt per square meter per degree Celsius (or kelvin)",
                "notation": "$\\mathrm{W} /\\left(\\mathrm{m}^{2}{ }^{\\circ} \\mathrm{C}\\right)$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "illuminance": {
        # Illuminance - LENGTH^-2 LUMINOUS_INTENSITY
        "dimension": ILLUMINANCE,
        "units": [
            {
                "name": "foot_candle",
                "symbol": "$\\mathrm{ft}-\\mathrm{C}$ or $\\mathrm{ft}-\\mathrm{Cd}$",
                "si_factor": 10.76391,
                "full_name": "foot-candle",
                "notation": "$\\mathrm{ft}-\\mathrm{C}$ or $\\mathrm{ft}-\\mathrm{Cd}$",
                "aliases": ['ft-C', 'ft-Cd'],
            },
            {
                "name": "lux",
                "symbol": "lx",
                "si_factor": 1.0,
                "full_name": "lux",
                "notation": "lx",
                "aliases": ['lx'],
            },
            {
                "name": "nox",
                "symbol": "nox",
                "si_factor": 0.001,
                "full_name": "nox",
                "notation": "nox",
                "aliases": ['nox'],
            },
            {
                "name": "phot",
                "symbol": "ph",
                "si_factor": 10000.0,
                "full_name": "phot",
                "notation": "ph",
                "aliases": ['ph'],
            },
            {
                "name": "skot",
                "symbol": "skot",
                "si_factor": 0.001,
                "full_name": "skot",
                "notation": "skot",
                "aliases": ['skot'],
            }
        ],
        "aliases": {}
    },

    "kinetic_energy_of_turbulence": {
        # Kinetic Energy of Turbulence - LENGTH^2 TIME^-2
        "dimension": KINETIC_ENERGY_OF_TURBULENCE,
        "units": [
            {
                "name": "square_foot_per_second_squared",
                "symbol": "$\\mathrm{ft}^{2} / \\mathrm{s}^{2}$ or sqft/sec ${ }^{2}$",
                "si_factor": 0.0929,
                "full_name": "square foot per second squared",
                "notation": "$\\mathrm{ft}^{2} / \\mathrm{s}^{2}$ or sqft/sec ${ }^{2}$",
                "aliases": ['ft^{2 / s^{2', 'sqft/sec { ^{2'],
            },
            {
                "name": "square_meters_per_second_squared",
                "symbol": "$\\mathrm{m}^{2} / \\mathrm{s}^{2}$",
                "si_factor": 1.0,
                "full_name": "square meters per second squared",
                "notation": "$\\mathrm{m}^{2} / \\mathrm{s}^{2}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "length": {
        # Length - LENGTH
        "dimension": LENGTH,
        "units": [
            {
                "name": "arpent_quebec",
                "symbol": "arp",
                "si_factor": 58.47,
                "full_name": "arpent (Quebec)",
                "notation": "arp",
                "aliases": ['arp'],
            },
            {
                "name": "astronomic_unit",
                "symbol": "AU",
                "si_factor": 149600000000.0,
                "full_name": "astronomic unit",
                "notation": "AU",
                "aliases": ['AU'],
            },
            {
                "name": "attometer",
                "symbol": "am",
                "si_factor": 1e-18,
                "full_name": "attometer",
                "notation": "am",
                "aliases": ['am'],
            },
            {
                "name": "calibre_centinch",
                "symbol": "cin",
                "si_factor": 0.000254,
                "full_name": "calibre (centinch)",
                "notation": "cin",
                "aliases": ['cin'],
            },
            {
                "name": "centimeter",
                "symbol": "cm",
                "si_factor": 0.01,
                "full_name": "centimeter",
                "notation": "cm",
                "aliases": ['cm'],
            },
            {
                "name": "chain_engrs_or_ramsden",
                "symbol": "ch (eng or Rams)",
                "si_factor": 30.48,
                "full_name": "chain (Engr's or Ramsden)",
                "notation": "ch (eng or Rams)",
                "aliases": ['ch (eng', 'Rams)'],
            },
            {
                "name": "chain_gunters",
                "symbol": "ch (Gunt)",
                "si_factor": 20.1168,
                "full_name": "chain (Gunter's)",
                "notation": "ch (Gunt)",
                "aliases": [],
            },
            {
                "name": "chain_surveyors",
                "symbol": "ch (surv)",
                "si_factor": 20.1168,
                "full_name": "chain (surveyors)",
                "notation": "ch (surv)",
                "aliases": [],
            },
            {
                "name": "cubit_uk",
                "symbol": "cu (UK)",
                "si_factor": 0.4572,
                "full_name": "cubit (UK)",
                "notation": "cu (UK)",
                "aliases": [],
            },
            {
                "name": "ell",
                "symbol": "ell",
                "si_factor": 1.143,
                "full_name": "ell",
                "notation": "ell",
                "aliases": ['ell'],
            },
            {
                "name": "fathom",
                "symbol": "fath",
                "si_factor": 1.8288,
                "full_name": "fathom",
                "notation": "fath",
                "aliases": ['fath'],
            },
            {
                "name": "femtometre",
                "symbol": "fm",
                "si_factor": 1e-15,
                "full_name": "femtometre",
                "notation": "fm",
                "aliases": ['fm'],
            },
            {
                "name": "fermi",
                "symbol": "F",
                "si_factor": 1e-15,
                "full_name": "fermi",
                "notation": "F",
                "aliases": ['F'],
            },
            {
                "name": "foot",
                "symbol": "ft",
                "si_factor": 0.3048,
                "full_name": "foot",
                "notation": "ft",
                "aliases": ['ft'],
            },
            {
                "name": "furlong_uk_and_us",
                "symbol": "fur",
                "si_factor": 201.168,
                "full_name": "furlong (UK and US)",
                "notation": "fur",
                "aliases": ['fur'],
            },
            {
                "name": "inch",
                "symbol": "in",
                "si_factor": 0.0254,
                "full_name": "inch",
                "notation": "in",
                "aliases": ['in'],
            },
            {
                "name": "kilometer",
                "symbol": "km",
                "si_factor": 1000.0,
                "full_name": "kilometer",
                "notation": "km",
                "aliases": ['km'],
            },
            {
                "name": "league_us_statute",
                "symbol": "lg (US, stat)",
                "si_factor": 4828.0,
                "full_name": "league (US, statute)",
                "notation": "lg (US, stat)",
                "aliases": [],
            },
            {
                "name": "lieue_metric",
                "symbol": "lieue (metric)",
                "si_factor": 4000.0,
                "full_name": "lieue (metric)",
                "notation": "lieue (metric)",
                "aliases": [],
            },
            {
                "name": "ligne_metric",
                "symbol": "ligne (metric)",
                "si_factor": 0.0023,
                "full_name": "ligne (metric)",
                "notation": "ligne (metric)",
                "aliases": [],
            },
            {
                "name": "line_us",
                "symbol": "li (US)",
                "si_factor": 0.000635,
                "full_name": "line (US)",
                "notation": "li (US)",
                "aliases": [],
            },
            {
                "name": "link_surveyors",
                "symbol": "li (surv)",
                "si_factor": 0.201168,
                "full_name": "link (surveyors)",
                "notation": "li (surv)",
                "aliases": [],
            },
            {
                "name": "meter",
                "symbol": "m",
                "si_factor": 1.0,
                "full_name": "meter",
                "notation": "m",
                "aliases": ['m'],
            },
            {
                "name": "micrometer",
                "symbol": "$\\mu \\mathrm{m}$",
                "si_factor": 1e-06,
                "full_name": "micrometer",
                "notation": "$\\mu \\mathrm{m}$",
                "aliases": [],
            },
            {
                "name": "micron",
                "symbol": "$\\mu$",
                "si_factor": 1e-06,
                "full_name": "micron",
                "notation": "$\\mu$",
                "aliases": ['mu'],
            },
            {
                "name": "mil",
                "symbol": "mil",
                "si_factor": 2.54e-05,
                "full_name": "mil",
                "notation": "mil",
                "aliases": ['mil'],
            },
            {
                "name": "mile_geographical",
                "symbol": "mi",
                "si_factor": 7421.59,
                "full_name": "mile (geographical)",
                "notation": "mi",
                "aliases": ['mi'],
            },
            {
                "name": "mile_us_nautical",
                "symbol": "mi (US, naut)",
                "si_factor": 1853.2,
                "full_name": "mile (US, nautical)",
                "notation": "mi (US, naut)",
                "aliases": [],
            },
            {
                "name": "mile_us_statute",
                "symbol": "mi",
                "si_factor": 1609.344,
                "full_name": "mile (US, statute)",
                "notation": "mi",
                "aliases": ['mi'],
            },
            {
                "name": "mile_us_survey",
                "symbol": "mi (US, surv)",
                "si_factor": 1609.3,
                "full_name": "mile (US, survey)",
                "notation": "mi (US, surv)",
                "aliases": [],
            },
            {
                "name": "millimeter",
                "symbol": "mm",
                "si_factor": 0.001,
                "full_name": "millimeter",
                "notation": "mm",
                "aliases": ['mm'],
            },
            {
                "name": "millimicron",
                "symbol": "$\\mathrm{m} \\mu$",
                "si_factor": 1e-09,
                "full_name": "millimicron",
                "notation": "$\\mathrm{m} \\mu$",
                "aliases": [],
            },
            {
                "name": "nanometer",
                "symbol": "nm",
                "si_factor": 1e-09,
                "full_name": "nanometer",
                "notation": "nm",
                "aliases": [],
            },
            {
                "name": "nanometer_or_nanon",
                "symbol": "nm",
                "si_factor": 1e-09,
                "full_name": "nanometer or nanon",
                "notation": "nm",
                "aliases": ['nm'],
            },
            {
                "name": "parsec",
                "symbol": "pc",
                "si_factor": 3.086e+16,
                "full_name": "parsec",
                "notation": "pc",
                "aliases": ['pc'],
            },
            {
                "name": "perche",
                "symbol": "rod",
                "si_factor": 5.0292,
                "full_name": "perche",
                "notation": "rod",
                "aliases": ['rod'],
            },
            {
                "name": "pica",
                "symbol": "pica",
                "si_factor": 0.0042175,
                "full_name": "pica",
                "notation": "pica",
                "aliases": ['pica'],
            },
            {
                "name": "picometer",
                "symbol": "pm",
                "si_factor": 1e-12,
                "full_name": "picometer",
                "notation": "pm",
                "aliases": ['pm'],
            },
            {
                "name": "point_didot",
                "symbol": "pt (Didot)",
                "si_factor": 0.00037597,
                "full_name": "point (Didot)",
                "notation": "pt (Didot)",
                "aliases": [],
            },
            {
                "name": "point_us",
                "symbol": "pt (US)",
                "si_factor": 0.00035146,
                "full_name": "point (US)",
                "notation": "pt (US)",
                "aliases": [],
            },
            {
                "name": "rod_or_pole",
                "symbol": "rod",
                "si_factor": 5.0292,
                "full_name": "rod or pole",
                "notation": "rod",
                "aliases": ['rod'],
            },
            {
                "name": "span",
                "symbol": "span",
                "si_factor": 0.2286,
                "full_name": "span",
                "notation": "span",
                "aliases": ['span'],
            },
            {
                "name": "thou_millinch",
                "symbol": "thou",
                "si_factor": 2.54e-05,
                "full_name": "thou (millinch)",
                "notation": "thou",
                "aliases": ['thou'],
            },
            {
                "name": "toise_metric",
                "symbol": "toise (metric)",
                "si_factor": 2.0,
                "full_name": "toise (metric)",
                "notation": "toise (metric)",
                "aliases": [],
            },
            {
                "name": "yard",
                "symbol": "yd",
                "si_factor": 0.9144,
                "full_name": "yard",
                "notation": "yd",
                "aliases": ['yd'],
            },
            {
                "name": "ångström",
                "symbol": "$\\AA$",
                "si_factor": 1e-10,
                "full_name": "ångström",
                "notation": "$\\AA$",
                "aliases": ['AA'],
            }
        ],
        "aliases": {}
    },

    "linear_mass_density": {
        # Linear Mass Density - LENGTH^-1 MASS
        "dimension": LINEAR_MASS_DENSITY,
        "units": [
            {
                "name": "denier",
                "symbol": "denier",
                "si_factor": 1.111e-07,
                "full_name": "denier",
                "notation": "denier",
                "aliases": [],
            },
            {
                "name": "kilogram_per_centimeter",
                "symbol": "kg/cm",
                "si_factor": 100.0,
                "full_name": "kilogram per centimeter",
                "notation": "kg/cm",
                "aliases": [],
            },
            {
                "name": "kilogram_per_meter",
                "symbol": "kg/m",
                "si_factor": 1.0,
                "full_name": "kilogram per meter",
                "notation": "kg/m",
                "aliases": [],
            },
            {
                "name": "pound_per_foot",
                "symbol": "lb/ft",
                "si_factor": 1.488,
                "full_name": "pound per foot",
                "notation": "lb/ft",
                "aliases": [],
            },
            {
                "name": "pound_per_inch",
                "symbol": "lb/in",
                "si_factor": 17.858,
                "full_name": "pound per inch",
                "notation": "lb/in",
                "aliases": [],
            },
            {
                "name": "pound_per_yard",
                "symbol": "lb/yd",
                "si_factor": 0.49606,
                "full_name": "pound per yard",
                "notation": "lb/yd",
                "aliases": [],
            },
            {
                "name": "ton_metric",
                "symbol": "t/km or MT/km",
                "si_factor": 1.0,
                "full_name": "ton (metric) per kilometer",
                "notation": "t/km or MT/km",
                "aliases": ['t/km', 'MT/km'],
            }
        ],
        "aliases": {}
    },

    "linear_momentum": {
        # Linear Momentum - LENGTH MASS TIME^-1
        "dimension": LINEAR_MOMENTUM,
        "units": [
            {
                "name": "foot_pounds_force_per_hour",
                "symbol": "${\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}}}^{/} \\mathrm{h}$ or $\\mathrm{ft}-\\mathrm{lb} / \\mathrm{hr}$",
                "si_factor": 3.8400000000000005e-05,
                "full_name": "foot pounds force per hour",
                "notation": "${\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}}}^{/} \\mathrm{h}$ or $\\mathrm{ft}-\\mathrm{lb} / \\mathrm{hr}$",
                "aliases": ['{ft lb_{f^{/ h', 'ft-lb / hr'],
            },
            {
                "name": "foot_pounds_force_per_minute",
                "symbol": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\min$ or $\\mathrm{ft}-\\mathrm{lb} /$ min",
                "si_factor": 0.0023042,
                "full_name": "foot pounds force per minute",
                "notation": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\min$ or $\\mathrm{ft}-\\mathrm{lb} /$ min",
                "aliases": ['ft lb_{f / min', 'ft-lb / min'],
            },
            {
                "name": "foot_pounds_force_per_second",
                "symbol": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{s}$ or ft-lb/sec",
                "si_factor": 0.13825,
                "full_name": "foot pounds force per second",
                "notation": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{s}$ or ft-lb/sec",
                "aliases": ['ft lb_{f / s', 'ft-lb/sec'],
            },
            {
                "name": "gram_centimeters_per_second",
                "symbol": "$\\mathrm{g} \\mathrm{cm} / \\mathrm{s}$",
                "si_factor": 1e-05,
                "full_name": "gram centimeters per second",
                "notation": "$\\mathrm{g} \\mathrm{cm} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "kilogram_meters_per_second",
                "symbol": "$\\mathrm{kg} \\mathrm{m} / \\mathrm{s}$",
                "si_factor": 1.0,
                "full_name": "kilogram meters per second",
                "notation": "$\\mathrm{kg} \\mathrm{m} / \\mathrm{s}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "luminance_self": {
        # Luminance (self) - LENGTH^-2 LUMINOUS_INTENSITY
        "dimension": LUMINANCE_SELF,
        "units": [
            {
                "name": "apostilb",
                "symbol": "asb",
                "si_factor": 0.31831,
                "full_name": "apostilb",
                "notation": "asb",
                "aliases": ['asb'],
            },
            {
                "name": "blondel",
                "symbol": "B1",
                "si_factor": 0.31831,
                "full_name": "blondel",
                "notation": "B1",
                "aliases": [],
            },
            {
                "name": "candela_per_square_meter",
                "symbol": "$\\mathrm{cd} / \\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "candela per square meter",
                "notation": "$\\mathrm{cd} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "foot_lambert",
                "symbol": "ft-L",
                "si_factor": 3.426259,
                "full_name": "foot-lambert",
                "notation": "ft-L",
                "aliases": [],
            },
            {
                "name": "lambert",
                "symbol": "L",
                "si_factor": 3183.1,
                "full_name": "lambert",
                "notation": "L",
                "aliases": ['L'],
            },
            {
                "name": "luxon",
                "symbol": "luxon",
                "si_factor": 10000.0,
                "full_name": "luxon",
                "notation": "luxon",
                "aliases": [],
            },
            {
                "name": "nit",
                "symbol": "nit",
                "si_factor": 1.0,
                "full_name": "nit",
                "notation": "nit",
                "aliases": ['nit'],
            },
            {
                "name": "stilb",
                "symbol": "sb",
                "si_factor": 10000.0,
                "full_name": "stilb",
                "notation": "sb",
                "aliases": ['sb'],
            },
            {
                "name": "troland",
                "symbol": "luxon",
                "si_factor": 10000.0,
                "full_name": "troland",
                "notation": "luxon",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "luminous_flux": {
        # Luminous Flux - LUMINOUS_INTENSITY
        "dimension": LUMINOUS_FLUX,
        "units": [
            {
                "name": "candela_steradian",
                "symbol": "cd sr",
                "si_factor": 1.0,
                "full_name": "candela steradian",
                "notation": "cd sr",
                "aliases": [],
            },
            {
                "name": "lumen",
                "symbol": "lumen",
                "si_factor": 1.0,
                "full_name": "lumen",
                "notation": "lumen",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "luminous_intensity": {
        # Luminous Intensity - LUMINOUS_INTENSITY
        "dimension": LUMINOUS_INTENSITY,
        "units": [
            {
                "name": "candela",
                "symbol": "cd",
                "si_factor": 1.0,
                "full_name": "candela",
                "notation": "cd",
                "aliases": ['cd'],
            },
            {
                "name": "candle_international",
                "symbol": "Cd (int)",
                "si_factor": 1.01937,
                "full_name": "candle (international)",
                "notation": "Cd (int)",
                "aliases": [],
            },
            {
                "name": "carcel",
                "symbol": "carcel",
                "si_factor": 10.0,
                "full_name": "carcel",
                "notation": "carcel",
                "aliases": [],
            },
            {
                "name": "hefner_unit",
                "symbol": "HK",
                "si_factor": 0.903,
                "full_name": "Hefner unit",
                "notation": "HK",
                "aliases": ['HK'],
            }
        ],
        "aliases": {}
    },

    "magnetic_field": {
        # Magnetic Field - CURRENT LENGTH^-1
        "dimension": MAGNETIC_FIELD,
        "units": [
            {
                "name": "ampere_per_meter",
                "symbol": "A/m",
                "si_factor": 1.0,
                "full_name": "ampere per meter",
                "notation": "A/m",
                "aliases": [],
            },
            {
                "name": "lenz",
                "symbol": "lenz",
                "si_factor": 1.0,
                "full_name": "lenz",
                "notation": "lenz",
                "aliases": ['lenz'],
            },
            {
                "name": "oersted",
                "symbol": "Oe",
                "si_factor": 79.57747,
                "full_name": "oersted",
                "notation": "Oe",
                "aliases": ['Oe'],
            },
            {
                "name": "praoersted",
                "symbol": "-",
                "si_factor": 11459.08,
                "full_name": "praoersted",
                "notation": "-",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "magnetic_flux": {
        # Magnetic Flux - CURRENT^-1 LENGTH^2 MASS TIME^-2
        "dimension": MAGNETIC_FLUX,
        "units": [
            {
                "name": "kapp_line",
                "symbol": "-",
                "si_factor": 6.000000000000001e-05,
                "full_name": "kapp line",
                "notation": "-",
                "aliases": [],
            },
            {
                "name": "line",
                "symbol": "line",
                "si_factor": 1e-08,
                "full_name": "line",
                "notation": "line",
                "aliases": ['line'],
            },
            {
                "name": "maxwell",
                "symbol": "Mx",
                "si_factor": 1e-08,
                "full_name": "maxwell",
                "notation": "Mx",
                "aliases": ['Mx'],
            },
            {
                "name": "microweber",
                "symbol": "μWb",
                "si_factor": 1e-06,
                "full_name": "microweber",
                "notation": "μWb",
                "aliases": [],
            },
            {
                "name": "milliweber",
                "symbol": "mWb",
                "si_factor": 0.001,
                "full_name": "milliweber",
                "notation": "mWb",
                "aliases": [],
            },
            {
                "name": "unit_pole",
                "symbol": "unit pole",
                "si_factor": 1.2565999999999998e-07,
                "full_name": "unit pole",
                "notation": "unit pole",
                "aliases": [],
            },
            {
                "name": "weber",
                "symbol": "Wb",
                "si_factor": 1.0,
                "full_name": "weber",
                "notation": "Wb",
                "aliases": ['Wb'],
            }
        ],
        "aliases": {}
    },

    "magnetic_induction_field_strength": {
        # Magnetic Induction Field Strength - CURRENT^-1 MASS TIME^-2
        "dimension": MAGNETIC_INDUCTION_FIELD_STRENGTH,
        "units": [
            {
                "name": "gamma",
                "symbol": "$\\gamma$",
                "si_factor": 1e-09,
                "full_name": "gamma",
                "notation": "$\\gamma$",
                "aliases": [],
            },
            {
                "name": "gauss",
                "symbol": "G",
                "si_factor": 0.0001,
                "full_name": "gauss",
                "notation": "G",
                "aliases": ['G'],
            },
            {
                "name": "line_per_square_centimeter",
                "symbol": "line $/ \\mathrm{cm}^{2}$",
                "si_factor": 0.0001,
                "full_name": "line per square centimeter",
                "notation": "line $/ \\mathrm{cm}^{2}$",
                "aliases": [],
            },
            {
                "name": "maxwell_per_square_centimeter",
                "symbol": "$\\mathrm{Mx} / \\mathrm{cm}^{2}$",
                "si_factor": 0.0001,
                "full_name": "maxwell per square centimeter",
                "notation": "$\\mathrm{Mx} / \\mathrm{cm}^{2}$",
                "aliases": [],
            },
            {
                "name": "microtesla",
                "symbol": "μT",
                "si_factor": 1e-06,
                "full_name": "microtesla",
                "notation": "μT",
                "aliases": [],
            },
            {
                "name": "millitesla",
                "symbol": "mT",
                "si_factor": 0.001,
                "full_name": "millitesla",
                "notation": "mT",
                "aliases": [],
            },
            {
                "name": "nanotesla",
                "symbol": "nT",
                "si_factor": 1e-09,
                "full_name": "nanotesla",
                "notation": "nT",
                "aliases": [],
            },
            {
                "name": "tesla",
                "symbol": "T",
                "si_factor": 1.0,
                "full_name": "tesla",
                "notation": "T",
                "aliases": ['T'],
            },
            {
                "name": "u_a",
                "symbol": "u.a.",
                "si_factor": 2350520000000000.0,
                "full_name": "u.a.",
                "notation": "u.a.",
                "aliases": [],
            },
            {
                "name": "weber_per_square_meter",
                "symbol": "$\\mathrm{Wb} / \\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "weber per square meter",
                "notation": "$\\mathrm{Wb} / \\mathrm{m}^{2}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "magnetic_moment": {
        # Magnetic Moment - CURRENT LENGTH^2
        "dimension": MAGNETIC_MOMENT,
        "units": [
            {
                "name": "bohr_magneton",
                "symbol": "Bohr magneton",
                "si_factor": 9.273999999999999e-24,
                "full_name": "Bohr magneton",
                "notation": "Bohr magneton",
                "aliases": [],
            },
            {
                "name": "joule_per_tesla",
                "symbol": "J/T",
                "si_factor": 1.0,
                "full_name": "joule per tesla",
                "notation": "J/T",
                "aliases": [],
            },
            {
                "name": "nuclear_magneton",
                "symbol": "nucl. Magneton",
                "si_factor": 5.0508e-27,
                "full_name": "nuclear magneton",
                "notation": "nucl. Magneton",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "magnetic_permeability": {
        # Magnetic Permeability - CURRENT^-2 LENGTH^2 MASS TIME^-2
        "dimension": MAGNETIC_PERMEABILITY,
        "units": [
            {
                "name": "henrys_per_meter",
                "symbol": "H/m",
                "si_factor": 1.0,
                "full_name": "henrys per meter",
                "notation": "H/m",
                "aliases": [],
            },
            {
                "name": "newton_per_square_ampere",
                "symbol": "N/A ${ }^{2}$",
                "si_factor": 1.0,
                "full_name": "newton per square ampere",
                "notation": "N/A ${ }^{2}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "magnetomotive_force": {
        # Magnetomotive Force - CURRENT
        "dimension": MAGNETOMOTIVE_FORCE,
        "units": [
            {
                "name": "abampere_turn",
                "symbol": "emu cgs",
                "si_factor": 10.0,
                "full_name": "abampere-turn",
                "notation": "emu cgs",
                "aliases": [],
            },
            {
                "name": "ampere",
                "symbol": "A",
                "si_factor": 1.0,
                "full_name": "ampere",
                "notation": "A",
                "aliases": ['A'],
            },
            {
                "name": "ampere_turn",
                "symbol": "A-turn",
                "si_factor": 2864.77,
                "full_name": "ampere-turn",
                "notation": "A-turn",
                "aliases": [],
            },
            {
                "name": "gilbert",
                "symbol": "Gb",
                "si_factor": 0.79577,
                "full_name": "gilbert",
                "notation": "Gb",
                "aliases": ['Gb'],
            },
            {
                "name": "kiloampere",
                "symbol": "kA",
                "si_factor": 1000.0,
                "full_name": "kiloampere",
                "notation": "kA",
                "aliases": [],
            },
            {
                "name": "microampere",
                "symbol": "μA",
                "si_factor": 1e-06,
                "full_name": "microampere",
                "notation": "μA",
                "aliases": [],
            },
            {
                "name": "milliampere",
                "symbol": "mA",
                "si_factor": 0.001,
                "full_name": "milliampere",
                "notation": "mA",
                "aliases": [],
            },
            {
                "name": "nanoampere",
                "symbol": "nA",
                "si_factor": 1e-09,
                "full_name": "nanoampere",
                "notation": "nA",
                "aliases": [],
            },
            {
                "name": "picoampere",
                "symbol": "pA",
                "si_factor": 1e-12,
                "full_name": "picoampere",
                "notation": "pA",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "mass": {
        # Mass - MASS
        "dimension": MASS,
        "units": [
            {
                "name": "atomic_mass_unit_12_mathrmc",
                "symbol": "$\\mathrm{u}\\left({ }^{12} \\mathrm{C}\\right)$ or amu",
                "si_factor": 1.6605000000000002e-27,
                "full_name": "atomic mass unit ( ${ }^{12} \\mathrm{C}$ )",
                "notation": "$\\mathrm{u}\\left({ }^{12} \\mathrm{C}\\right)$ or amu",
                "aliases": ['uleft({ ^{12 Cright)', 'amu'],
            },
            {
                "name": "carat_metric",
                "symbol": "ct",
                "si_factor": 0.0002,
                "full_name": "carat (metric)",
                "notation": "ct",
                "aliases": ['ct'],
            },
            {
                "name": "cental",
                "symbol": "sh cwt, cH",
                "si_factor": 45.359,
                "full_name": "cental",
                "notation": "sh cwt, cH",
                "aliases": [],
            },
            {
                "name": "centigram",
                "symbol": "cg",
                "si_factor": 1e-05,
                "full_name": "centigram",
                "notation": "cg",
                "aliases": ['cg'],
            },
            {
                "name": "clove_uk",
                "symbol": "cl",
                "si_factor": 3.6287,
                "full_name": "clove (UK)",
                "notation": "cl",
                "aliases": ['cl'],
            },
            {
                "name": "drachm_apothecary",
                "symbol": "dr (ap)",
                "si_factor": 0.0038879,
                "full_name": "drachm (apothecary)",
                "notation": "dr (ap)",
                "aliases": [],
            },
            {
                "name": "dram_avoirdupois",
                "symbol": "dr (av)",
                "si_factor": 0.0017718,
                "full_name": "dram (avoirdupois)",
                "notation": "dr (av)",
                "aliases": [],
            },
            {
                "name": "dram_troy",
                "symbol": "dr (troy)",
                "si_factor": 0.0038879,
                "full_name": "dram (troy)",
                "notation": "dr (troy)",
                "aliases": [],
            },
            {
                "name": "grain",
                "symbol": "gr",
                "si_factor": 6.4799e-05,
                "full_name": "grain",
                "notation": "gr",
                "aliases": ['gr'],
            },
            {
                "name": "gram",
                "symbol": "g",
                "si_factor": 0.001,
                "full_name": "gram",
                "notation": "g",
                "aliases": ['g'],
            },
            {
                "name": "hundredweight_long_or_gross",
                "symbol": "cwt, lg cwt",
                "si_factor": 50.802,
                "full_name": "hundredweight, long or gross",
                "notation": "cwt, lg cwt",
                "aliases": [],
            },
            {
                "name": "hundredweight_short_or_net",
                "symbol": "sh cwt",
                "si_factor": 45.359,
                "full_name": "hundredweight, short or net",
                "notation": "sh cwt",
                "aliases": [],
            },
            {
                "name": "kilogram",
                "symbol": "kg",
                "si_factor": 1.0,
                "full_name": "kilogram",
                "notation": "kg",
                "aliases": ['kg'],
            },
            {
                "name": "kip",
                "symbol": "kip",
                "si_factor": 453.59,
                "full_name": "kip",
                "notation": "kip",
                "aliases": ['kip'],
            },
            {
                "name": "microgram",
                "symbol": "$\\mu \\mathrm{g}$",
                "si_factor": 1e-09,
                "full_name": "microgram",
                "notation": "$\\mu \\mathrm{g}$",
                "aliases": [],
            },
            {
                "name": "milligram",
                "symbol": "mg",
                "si_factor": 1e-06,
                "full_name": "milligram",
                "notation": "mg",
                "aliases": ['mg'],
            },
            {
                "name": "ounce_apothecary",
                "symbol": "oz (ap)",
                "si_factor": 0.031103,
                "full_name": "ounce (apothecary)",
                "notation": "oz (ap)",
                "aliases": [],
            },
            {
                "name": "ounce_avoirdupois",
                "symbol": "oz",
                "si_factor": 0.02835,
                "full_name": "ounce (avoirdupois)",
                "notation": "oz",
                "aliases": ['oz'],
            },
            {
                "name": "ounce_troy",
                "symbol": "oz (troy)",
                "si_factor": 0.031103,
                "full_name": "ounce (troy)",
                "notation": "oz (troy)",
                "aliases": [],
            },
            {
                "name": "pennyweight_troy",
                "symbol": "dwt (troy)",
                "si_factor": 0.0015552,
                "full_name": "pennyweight (troy)",
                "notation": "dwt (troy)",
                "aliases": [],
            },
            {
                "name": "pood_russia",
                "symbol": "pood",
                "si_factor": 16.38,
                "full_name": "pood, (Russia)",
                "notation": "pood",
                "aliases": ['pood'],
            },
            {
                "name": "pound_apothecary",
                "symbol": "lb (ap)",
                "si_factor": 0.37324,
                "full_name": "pound (apothecary)",
                "notation": "lb (ap)",
                "aliases": [],
            },
            {
                "name": "pound_avoirdupois",
                "symbol": "lb (av)",
                "si_factor": 0.45359,
                "full_name": "pound (avoirdupois)",
                "notation": "lb (av)",
                "aliases": [],
            },
            {
                "name": "pound_mass",
                "symbol": "$\\mathrm{lb}_{\\mathrm{m}}$",
                "si_factor": 0.45359,
                "full_name": "pound mass",
                "notation": "$\\mathrm{lb}_{\\mathrm{m}}$",
                "aliases": [],
            },
            {
                "name": "pound_troy",
                "symbol": "lb (troy)",
                "si_factor": 0.37324,
                "full_name": "pound (troy)",
                "notation": "lb (troy)",
                "aliases": [],
            },
            {
                "name": "quarter_uk",
                "symbol": "qt",
                "si_factor": 12.7,
                "full_name": "quarter (UK)",
                "notation": "qt",
                "aliases": ['qt'],
            },
            {
                "name": "quintal_metric",
                "symbol": "q, dt",
                "si_factor": 100.0,
                "full_name": "quintal, metric",
                "notation": "q, dt",
                "aliases": [],
            },
            {
                "name": "quital_us",
                "symbol": "quint (US)",
                "si_factor": 45.359,
                "full_name": "quital, US",
                "notation": "quint (US)",
                "aliases": [],
            },
            {
                "name": "scruple_avoirdupois",
                "symbol": "scf",
                "si_factor": 0.001575,
                "full_name": "scruple (avoirdupois)",
                "notation": "scf",
                "aliases": ['scf'],
            },
            {
                "name": "slug",
                "symbol": "sl",
                "si_factor": 14.594,
                "full_name": "slug",
                "notation": "sl",
                "aliases": ['sl'],
            },
            {
                "name": "stone_uk",
                "symbol": "st",
                "si_factor": 6.3503,
                "full_name": "stone (UK)",
                "notation": "st",
                "aliases": ['st'],
            },
            {
                "name": "ton_metric",
                "symbol": "t",
                "si_factor": 1000.0,
                "full_name": "ton, metric",
                "notation": "t",
                "aliases": ['t'],
            },
            {
                "name": "ton_us_long",
                "symbol": "lg ton",
                "si_factor": 1016.0,
                "full_name": "ton, US, long",
                "notation": "lg ton",
                "aliases": [],
            },
            {
                "name": "ton_us_short",
                "symbol": "sh ton",
                "si_factor": 907.18,
                "full_name": "ton, US, short",
                "notation": "sh ton",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "mass_density": {
        # Mass Density - LENGTH^-3 MASS
        "dimension": MASS_DENSITY,
        "units": [
            {
                "name": "gram_per_cubic_centimeter",
                "symbol": "g/cc or g/ml",
                "si_factor": 1000.0,
                "full_name": "gram per cubic centimeter",
                "notation": "g/cc or g/ml",
                "aliases": ['g/cc', 'g/ml'],
            },
            {
                "name": "gram_per_cubic_decimeter",
                "symbol": "$\\mathrm{g} / \\mathrm{dm}^{3}$",
                "si_factor": 1.0,
                "full_name": "gram per cubic decimeter",
                "notation": "$\\mathrm{g} / \\mathrm{dm}^{3}$",
                "aliases": [],
            },
            {
                "name": "gram_per_cubic_meter",
                "symbol": "$\\mathrm{g} / \\mathrm{m}^{3}$",
                "si_factor": 0.001,
                "full_name": "gram per cubic meter",
                "notation": "$\\mathrm{g} / \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "gram_per_liter",
                "symbol": "$\\mathrm{g} / \\mathrm{l}$ or g/L",
                "si_factor": 1.0,
                "full_name": "gram per liter",
                "notation": "$\\mathrm{g} / \\mathrm{l}$ or g/L",
                "aliases": ['g / l', 'g/L'],
            },
            {
                "name": "kilogram_per_cubic_meter",
                "symbol": "$\\mathrm{kg} / \\mathrm{m}^{3}$",
                "si_factor": 1.0,
                "full_name": "kilogram per cubic meter",
                "notation": "$\\mathrm{kg} / \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "ounce_avdp",
                "symbol": "oz/gal",
                "si_factor": 7.489152,
                "full_name": "ounce (avdp) per US gallon",
                "notation": "oz/gal",
                "aliases": [],
            },
            {
                "name": "pound_avdp",
                "symbol": "$\\mathrm{lb} / \\mathrm{cu} \\mathrm{ft}$ or lb/ft ${ }^{3}$",
                "si_factor": 16.01846,
                "full_name": "pound (avdp) per cubic foot",
                "notation": "$\\mathrm{lb} / \\mathrm{cu} \\mathrm{ft}$ or lb/ft ${ }^{3}$",
                "aliases": ['lb / cu ft', 'lb/ft { ^{3'],
            },
            {
                "name": "pound_mass",
                "symbol": "$\\mathrm{lb} / \\mathrm{cu}$ in or $\\mathrm{lb} / \\mathrm{in}^{3}$",
                "si_factor": 0.000276799,
                "full_name": "pound (mass) per cubic inch",
                "notation": "$\\mathrm{lb} / \\mathrm{cu}$ in or $\\mathrm{lb} / \\mathrm{in}^{3}$",
                "aliases": ['lb / cu in', 'lb / in^{3'],
            },
            {
                "name": "ton_metric",
                "symbol": "$\\mathrm{t} / \\mathrm{m}^{3}$ or MT $/ \\mathrm{m}^{3}$",
                "si_factor": 1000.0,
                "full_name": "ton (metric) per cubic meter",
                "notation": "$\\mathrm{t} / \\mathrm{m}^{3}$ or MT $/ \\mathrm{m}^{3}$",
                "aliases": ['t / m^{3', 'MT / m^{3'],
            }
        ],
        "aliases": {}
    },

    "mass_flow_rate": {
        # Mass Flow Rate - MASS TIME^-1
        "dimension": MASS_FLOW_RATE,
        "units": [
            {
                "name": "kilograms_per_day",
                "symbol": "kg/d",
                "si_factor": 1.1574000000000001e-05,
                "full_name": "kilograms per day",
                "notation": "kg/d",
                "aliases": [],
            },
            {
                "name": "kilograms_per_hour",
                "symbol": "kg/h",
                "si_factor": 0.00027778,
                "full_name": "kilograms per hour",
                "notation": "kg/h",
                "aliases": [],
            },
            {
                "name": "kilograms_per_minute",
                "symbol": "kg/min",
                "si_factor": 0.016667,
                "full_name": "kilograms per minute",
                "notation": "kg/min",
                "aliases": [],
            },
            {
                "name": "kilograms_per_second",
                "symbol": "kg/s",
                "si_factor": 1.0,
                "full_name": "kilograms per second",
                "notation": "kg/s",
                "aliases": [],
            },
            {
                "name": "metric_tons_per_day",
                "symbol": "MT/d or MTD",
                "si_factor": 0.01157,
                "full_name": "metric tons per day",
                "notation": "MT/d or MTD",
                "aliases": ['MT/d', 'MTD'],
            },
            {
                "name": "metric_tons_per_hour",
                "symbol": "MT/h or MTD",
                "si_factor": 0.2778,
                "full_name": "metric tons per hour",
                "notation": "MT/h or MTD",
                "aliases": ['MT/h', 'MTD'],
            },
            {
                "name": "metric_tons_per_minute",
                "symbol": "MT/h",
                "si_factor": 16.67,
                "full_name": "metric tons per minute",
                "notation": "MT/h",
                "aliases": [],
            },
            {
                "name": "metric_tons_per_second",
                "symbol": "MT/s",
                "si_factor": 1000.0,
                "full_name": "metric tons per second",
                "notation": "MT/s",
                "aliases": [],
            },
            {
                "name": "metric_tons_per_year_365_d",
                "symbol": "MT/yr or MTY",
                "si_factor": 3.171e-05,
                "full_name": "metric tons per year (365 d)",
                "notation": "MT/yr or MTY",
                "aliases": ['MT/yr', 'MTY'],
            },
            {
                "name": "pounds_per_day",
                "symbol": "$\\mathrm{lb} / \\mathrm{d}$ or $\\mathrm{lb} / \\mathrm{da}$ or PPD",
                "si_factor": 5.248999999999999e-06,
                "full_name": "pounds per day",
                "notation": "$\\mathrm{lb} / \\mathrm{d}$ or $\\mathrm{lb} / \\mathrm{da}$ or PPD",
                "aliases": ['lb / d', 'lb / da', 'PPD'],
            },
            {
                "name": "pounds_per_hour",
                "symbol": "$\\mathrm{lb} / \\mathrm{h}$ or lb/hr or PPH",
                "si_factor": 0.00012598,
                "full_name": "pounds per hour",
                "notation": "$\\mathrm{lb} / \\mathrm{h}$ or lb/hr or PPH",
                "aliases": ['lb / h', 'lb/hr', 'PPH'],
            },
            {
                "name": "pounds_per_minute",
                "symbol": "$\\mathrm{lb} / \\mathrm{min}$ or PPM",
                "si_factor": 0.0075586,
                "full_name": "pounds per minute",
                "notation": "$\\mathrm{lb} / \\mathrm{min}$ or PPM",
                "aliases": ['lb / min', 'PPM'],
            },
            {
                "name": "pounds_per_second",
                "symbol": "$\\mathrm{lb} / \\mathrm{s}$ or lb/sec or PPS",
                "si_factor": 0.45351,
                "full_name": "pounds per second",
                "notation": "$\\mathrm{lb} / \\mathrm{s}$ or lb/sec or PPS",
                "aliases": ['lb / s', 'lb/sec', 'PPS'],
            }
        ],
        "aliases": {}
    },

    "mass_flux": {
        # Mass Flux - LENGTH^-2 MASS TIME^-1
        "dimension": MASS_FLUX,
        "units": [
            {
                "name": "kilogram_per_square_meter_per_day",
                "symbol": "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$",
                "si_factor": 1.1574000000000001e-05,
                "full_name": "kilogram per square meter per day",
                "notation": "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$",
                "aliases": [],
            },
            {
                "name": "kilogram_per_square_meter_per_hour",
                "symbol": "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$",
                "si_factor": 0.00027778000000000004,
                "full_name": "kilogram per square meter per hour",
                "notation": "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$",
                "aliases": [],
            },
            {
                "name": "kilogram_per_square_meter_per_minute",
                "symbol": "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~min}\\right)$",
                "si_factor": 0.016667,
                "full_name": "kilogram per square meter per minute",
                "notation": "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~min}\\right)$",
                "aliases": [],
            },
            {
                "name": "kilogram_per_square_meter_per_second",
                "symbol": "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$",
                "si_factor": 1.0,
                "full_name": "kilogram per square meter per second",
                "notation": "$\\mathrm{kg} /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$",
                "aliases": [],
            },
            {
                "name": "pound_per_square_foot_per_day",
                "symbol": "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or lb/sqft/ da",
                "si_factor": 5.6478000000000004e-05,
                "full_name": "pound per square foot per day",
                "notation": "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or lb/sqft/ da",
                "aliases": ['lb /left(ft^{2 ~dright)', 'lb/sqft/ da'],
            },
            {
                "name": "pound_per_square_foot_per_hour",
                "symbol": "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or lb/sqft/ hr",
                "si_factor": 0.0013555,
                "full_name": "pound per square foot per hour",
                "notation": "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or lb/sqft/ hr",
                "aliases": ['lb /left(ft^{2 ~hright)', 'lb/sqft/ hr'],
            },
            {
                "name": "pound_per_square_foot_per_minute",
                "symbol": "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\min \\right)$ or lb/ sqft/min",
                "si_factor": 0.081329,
                "full_name": "pound per square foot per minute",
                "notation": "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\min \\right)$ or lb/ sqft/min",
                "aliases": ['lb /left(ft^{2 min right)', 'lb/ sqft/min'],
            },
            {
                "name": "pound_per_square_foot_per_second",
                "symbol": "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or lb/sqft/ sec",
                "si_factor": 4.8797,
                "full_name": "pound per square foot per second",
                "notation": "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or lb/sqft/ sec",
                "aliases": ['lb /left(ft^{2 ~sright)', 'lb/sqft/ sec'],
            }
        ],
        "aliases": {}
    },

    "mass_fraction_of_i": {
        # Mass Fraction of "i" - Dimensionless
        "dimension": DIMENSIONLESS,
        "units": [
            {
                "name": "grains_of_i_per_pound_total",
                "symbol": "$\\mathrm{gr}_{\\mathrm{i}} / \\mathrm{lb}$",
                "si_factor": 0.00014286,
                "full_name": "grains of \"i\" per pound total",
                "notation": "$\\mathrm{gr}_{\\mathrm{i}} / \\mathrm{lb}$",
                "aliases": [],
            },
            {
                "name": "gram_of_i_per_kilogram_total",
                "symbol": "$\\mathrm{g}_{\\mathrm{i}} / \\mathrm{kg}$",
                "si_factor": 0.001,
                "full_name": "gram of \"i\" per kilogram total",
                "notation": "$\\mathrm{g}_{\\mathrm{i}} / \\mathrm{kg}$",
                "aliases": [],
            },
            {
                "name": "kilogram_of_i_per_kilogram_total",
                "symbol": "$\\mathrm{kg}_{\\mathrm{i}} / \\mathrm{kg}$",
                "si_factor": 1.0,
                "full_name": "kilogram of \"i\" per kilogram total",
                "notation": "$\\mathrm{kg}_{\\mathrm{i}} / \\mathrm{kg}$",
                "aliases": [],
            },
            {
                "name": "pound_of_i_per_pound_total",
                "symbol": "$\\mathrm{lb}_{\\mathrm{i}} / \\mathrm{lb}$",
                "si_factor": 1.0,
                "full_name": "pound of \"i\" per pound total",
                "notation": "$\\mathrm{lb}_{\\mathrm{i}} / \\mathrm{lb}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "mass_transfer_coefficient": {
        # Mass Transfer Coefficient - LENGTH^-2 MASS TIME^-1
        "dimension": MASS_TRANSFER_COEFFICIENT,
        "units": [
            {
                "name": "gram_per_square_centimeter_per_second",
                "symbol": "$\\mathrm{g} / \\mathrm{cm}^{2} / \\mathrm{s}$",
                "si_factor": 0.1,
                "full_name": "gram per square centimeter per second",
                "notation": "$\\mathrm{g} / \\mathrm{cm}^{2} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "kilogram_per_square_meter_per_second",
                "symbol": "$\\mathrm{kg} / \\mathrm{m}^{2} / \\mathrm{s}$",
                "si_factor": 1.0,
                "full_name": "kilogram per square meter per second",
                "notation": "$\\mathrm{kg} / \\mathrm{m}^{2} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "pounds_force_per_cubic_foot_per_hour",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}^{3} / \\mathrm{h}$ or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{cft} / \\mathrm{hr}$",
                "si_factor": 15.709,
                "full_name": "pounds force per cubic foot per hour",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}^{3} / \\mathrm{h}$ or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{cft} / \\mathrm{hr}$",
                "aliases": ['lb_{f / ft^{3 / h', 'lb_{f / cft / hr'],
            },
            {
                "name": "pounds_mass_per_square_foot_per_hour",
                "symbol": "lb/(ft ${ }^{2} \\mathrm{hr}$ ) or lb/sqft/ hr",
                "si_factor": 0.00013562,
                "full_name": "pounds mass per square foot per hour",
                "notation": "lb/(ft ${ }^{2} \\mathrm{hr}$ ) or lb/sqft/ hr",
                "aliases": ['lb/(ft { ^{2 hr )', 'lb/sqft/ hr'],
            },
            {
                "name": "pounds_mass_per_square_foot_per_second",
                "symbol": "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or lb/sqft/ sec",
                "si_factor": 0.48824,
                "full_name": "pounds mass per square foot per second",
                "notation": "$\\mathrm{lb} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or lb/sqft/ sec",
                "aliases": ['lb /left(ft^{2 ~sright)', 'lb/sqft/ sec'],
            }
        ],
        "aliases": {}
    },

    "molality_of_solute_i": {
        # Molality of Solute "i" - AMOUNT MASS^-1
        "dimension": MOLALITY_OF_SOLUTE_I,
        "units": [
            {
                "name": "gram_moles_of_i_per_kilogram",
                "symbol": "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{kg}$",
                "si_factor": 1.0,
                "full_name": "gram moles of \"i\" per kilogram",
                "notation": "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{kg}$",
                "aliases": [],
            },
            {
                "name": "kilogram_mols_of_i_per_kilogram",
                "symbol": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kg}$",
                "si_factor": 1000.0,
                "full_name": "kilogram mols of \"i\" per kilogram",
                "notation": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kg}$",
                "aliases": [],
            },
            {
                "name": "kmols_of_i_per_kilogram",
                "symbol": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kg}$",
                "si_factor": 1000.0,
                "full_name": "kmols of \"i\" per kilogram",
                "notation": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kg}$",
                "aliases": [],
            },
            {
                "name": "mols_of_i_per_gram",
                "symbol": "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{g}$",
                "si_factor": 1000.0,
                "full_name": "mols of \"i\" per gram",
                "notation": "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{g}$",
                "aliases": [],
            },
            {
                "name": "pound_moles_of_i_per_pound_mass",
                "symbol": "mole $_{\\mathrm{i}} / \\mathrm{lb}$ (mass)",
                "si_factor": 1000.0,
                "full_name": "pound moles of \"i\" per pound mass",
                "notation": "mole $_{\\mathrm{i}} / \\mathrm{lb}$ (mass)",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "molar_concentration_by_mass": {
        # Molar Concentration by Mass - AMOUNT
        "dimension": MOLAR_CONCENTRATION_BY_MASS,
        "units": [
            {
                "name": "gram_mole_or_mole_per_gram",
                "symbol": "mol/g",
                "si_factor": 1.0,
                "full_name": "gram mole or mole per gram",
                "notation": "mol/g",
                "aliases": [],
            },
            {
                "name": "gram_mole_or_mole_per_kilogram",
                "symbol": "mol/kg",
                "si_factor": 0.001,
                "full_name": "gram mole or mole per kilogram",
                "notation": "mol/kg",
                "aliases": [],
            },
            {
                "name": "kilogram_mole_or_kmol_per_kilogram",
                "symbol": "kmol/kg",
                "si_factor": 1.0,
                "full_name": "kilogram mole or kmol per kilogram",
                "notation": "kmol/kg",
                "aliases": [],
            },
            {
                "name": "micromole_per_gram",
                "symbol": "$\\mu \\mathrm{mol} / \\mathrm{g}$",
                "si_factor": 1e-06,
                "full_name": "micromole per gram",
                "notation": "$\\mu \\mathrm{mol} / \\mathrm{g}$",
                "aliases": [],
            },
            {
                "name": "millimole_per_gram",
                "symbol": "mmol/g",
                "si_factor": 0.001,
                "full_name": "millimole per gram",
                "notation": "mmol/g",
                "aliases": [],
            },
            {
                "name": "picomole_per_gram",
                "symbol": "pmol/g",
                "si_factor": 1e-12,
                "full_name": "picomole per gram",
                "notation": "pmol/g",
                "aliases": [],
            },
            {
                "name": "pound_mole_per_pound",
                "symbol": "$\\mathrm{lb}-\\mathrm{mol} / \\mathrm{lb}$ or mole/lb",
                "si_factor": 1.0,
                "full_name": "pound mole per pound",
                "notation": "$\\mathrm{lb}-\\mathrm{mol} / \\mathrm{lb}$ or mole/lb",
                "aliases": ['lb-mol / lb', 'mole/lb'],
            }
        ],
        "aliases": {}
    },

    "molar_flow_rate": {
        # Molar Flow Rate - AMOUNT TIME^-1
        "dimension": MOLAR_FLOW_RATE,
        "units": [
            {
                "name": "gram_mole_per_day",
                "symbol": "mol/d",
                "si_factor": 4.167e-05,
                "full_name": "gram mole per day",
                "notation": "mol/d",
                "aliases": [],
            },
            {
                "name": "gram_mole_per_hour",
                "symbol": "mol/h",
                "si_factor": 0.001,
                "full_name": "gram mole per hour",
                "notation": "mol/h",
                "aliases": [],
            },
            {
                "name": "gram_mole_per_minute",
                "symbol": "mol/min",
                "si_factor": 0.06,
                "full_name": "gram mole per minute",
                "notation": "mol/min",
                "aliases": [],
            },
            {
                "name": "gram_mole_per_second",
                "symbol": "mol/s",
                "si_factor": 3.6,
                "full_name": "gram mole per second",
                "notation": "mol/s",
                "aliases": [],
            },
            {
                "name": "kilogram_mole_or_kmol_per_day",
                "symbol": "kmol/d",
                "si_factor": 0.04167,
                "full_name": "kilogram mole or kmol per day",
                "notation": "kmol/d",
                "aliases": [],
            },
            {
                "name": "kilogram_mole_or_kmol_per_hour",
                "symbol": "kmol/h",
                "si_factor": 1.0,
                "full_name": "kilogram mole or kmol per hour",
                "notation": "kmol/h",
                "aliases": [],
            },
            {
                "name": "kilogram_mole_or_kmol_per_minute",
                "symbol": "kmol/min",
                "si_factor": 60.0,
                "full_name": "kilogram mole or kmol per minute",
                "notation": "kmol/min",
                "aliases": [],
            },
            {
                "name": "kilogram_mole_or_kmol_per_second",
                "symbol": "kmol/s",
                "si_factor": 3600.0,
                "full_name": "kilogram mole or kmol per second",
                "notation": "kmol/s",
                "aliases": [],
            },
            {
                "name": "pound_mole_or_lb_mol_per_day",
                "symbol": "lb-mol/d or mole/da",
                "si_factor": 0.0189,
                "full_name": "pound mole or lb-mol per day",
                "notation": "lb-mol/d or mole/da",
                "aliases": ['lb-mol/d', 'mole/da'],
            },
            {
                "name": "pound_mole_or_lb_mol_per_hour",
                "symbol": "lb-mol/h or mole/hr",
                "si_factor": 0.4535,
                "full_name": "pound mole or lb-mol per hour",
                "notation": "lb-mol/h or mole/hr",
                "aliases": ['lb-mol/h', 'mole/hr'],
            },
            {
                "name": "pound_mole_or_lb_mol_per_minute",
                "symbol": "lb-mol/min or mole/ min",
                "si_factor": 27.21,
                "full_name": "pound mole or lb-mol per minute",
                "notation": "lb-mol/min or mole/ min",
                "aliases": ['lb-mol/min', 'mole/ min'],
            },
            {
                "name": "pound_mole_or_lb_mol_per_second",
                "symbol": "$\\mathrm{lb}-\\mathrm{mol} / \\mathrm{s}$ or mole/sec",
                "si_factor": 1633.0,
                "full_name": "pound mole or lb-mol per second",
                "notation": "$\\mathrm{lb}-\\mathrm{mol} / \\mathrm{s}$ or mole/sec",
                "aliases": ['lb-mol / s', 'mole/sec'],
            }
        ],
        "aliases": {}
    },

    "molar_flux": {
        # Molar Flux - AMOUNT LENGTH^-2 TIME^-1
        "dimension": MOLAR_FLUX,
        "units": [
            {
                "name": "kmol_per_square_meter_per_day",
                "symbol": "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$",
                "si_factor": 1.1574000000000001e-05,
                "full_name": "kmol per square meter per day",
                "notation": "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$",
                "aliases": [],
            },
            {
                "name": "kmol_per_square_meter_per_hour",
                "symbol": "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$",
                "si_factor": 0.00027778000000000004,
                "full_name": "kmol per square meter per hour",
                "notation": "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$",
                "aliases": [],
            },
            {
                "name": "kmol_per_square_meter_per_minute",
                "symbol": "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2}\\right.$ amin $)$",
                "si_factor": 0.016667,
                "full_name": "kmol per square meter per minute",
                "notation": "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2}\\right.$ amin $)$",
                "aliases": [],
            },
            {
                "name": "kmol_per_square_meter_per_second",
                "symbol": "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$",
                "si_factor": 1.0,
                "full_name": "kmol per square meter per second",
                "notation": "$\\mathrm{kmol} /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$",
                "aliases": [],
            },
            {
                "name": "pound_mole_per_square_foot_per_day",
                "symbol": "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or mole/sqft/da",
                "si_factor": 5.6478000000000004e-05,
                "full_name": "pound mole per square foot per day",
                "notation": "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or mole/sqft/da",
                "aliases": ['lb-mol /left(ft^{2 ~dright)', 'mole/sqft/da'],
            },
            {
                "name": "pound_mole_per_square_foot_per_hour",
                "symbol": "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or mole/sqft/hr",
                "si_factor": 0.0013555,
                "full_name": "pound mole per square foot per hour",
                "notation": "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or mole/sqft/hr",
                "aliases": ['lb-mol /left(ft^{2 ~hright)', 'mole/sqft/hr'],
            },
            {
                "name": "pound_mole_per_square_foot_per_minute",
                "symbol": "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~min}\\right)$ or mole/sqft/min",
                "si_factor": 0.081329,
                "full_name": "pound mole per square foot per minute",
                "notation": "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~min}\\right)$ or mole/sqft/min",
                "aliases": ['lb-mol /left(ft^{2 ~minright)', 'mole/sqft/min'],
            },
            {
                "name": "pound_mole_per_square_foot_per_second",
                "symbol": "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or mole/sqft/sec",
                "si_factor": 4.8797,
                "full_name": "pound mole per square foot per second",
                "notation": "$\\mathrm{lb}-\\mathrm{mol} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or mole/sqft/sec",
                "aliases": ['lb-mol /left(ft^{2 ~sright)', 'mole/sqft/sec'],
            }
        ],
        "aliases": {}
    },

    "molar_heat_capacity": {
        # Molar Heat Capacity - AMOUNT^-1 LENGTH^2 TEMP^-1 TIME^-2
        "dimension": MOLAR_HEAT_CAPACITY,
        "units": [
            {
                "name": "btu_per_pound_mole_per_degree_fahrenheit_or_degree_rankine",
                "symbol": "Btu/lb-mol/ ${ }^{\\circ} \\mathrm{F}$",
                "si_factor": 4.1868,
                "full_name": "Btu per pound mole per degree Fahrenheit (or degree Rankine)",
                "notation": "Btu/lb-mol/ ${ }^{\\circ} \\mathrm{F}$",
                "aliases": [],
            },
            {
                "name": "calories_per_gram_mole_per_kelvin_or_degree_celsius",
                "symbol": "cal/(mol K)",
                "si_factor": 4.1868,
                "full_name": "calories per gram mole per kelvin (or degree Celsius)",
                "notation": "cal/(mol K)",
                "aliases": [],
            },
            {
                "name": "joule_per_gram_mole_per_kelvin_or_degree_celsius",
                "symbol": "J/(mol K)",
                "si_factor": 1.0,
                "full_name": "joule per gram mole per kelvin (or degree Celsius)",
                "notation": "J/(mol K)",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "molarity_of_i": {
        # Molarity of "i" - AMOUNT LENGTH^-3
        "dimension": MOLARITY_OF_I,
        "units": [
            {
                "name": "gram_moles_of_i_per_cubic_meter",
                "symbol": "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{m}^{3}$ or $\\mathrm{c}_{\\mathrm{i}}$",
                "si_factor": 1.0,
                "full_name": "gram moles of \"i\" per cubic meter",
                "notation": "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{m}^{3}$ or $\\mathrm{c}_{\\mathrm{i}}$",
                "aliases": ['mol_{i / m^{3', 'c_{i'],
            },
            {
                "name": "gram_moles_of_i_per_liter",
                "symbol": "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{l}$",
                "si_factor": 1000.0,
                "full_name": "gram moles of \"i\" per liter",
                "notation": "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{l}$",
                "aliases": [],
            },
            {
                "name": "kilogram_moles_of_i_per_cubic_meter",
                "symbol": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{m}^{3}$",
                "si_factor": 1000.0,
                "full_name": "kilogram moles of \"i\" per cubic meter",
                "notation": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "kilogram_moles_of_i_per_liter",
                "symbol": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{l}$",
                "si_factor": 1000000.0,
                "full_name": "kilogram moles of \"i\" per liter",
                "notation": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{l}$",
                "aliases": [],
            },
            {
                "name": "pound_moles_of_i_per_cubic_foot",
                "symbol": "lb $\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{ft}^{3}$ or $\\mathrm{mole}_{\\mathrm{i}} /$ cft",
                "si_factor": 77844.0,
                "full_name": "pound moles of \"i\" per cubic foot",
                "notation": "lb $\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{ft}^{3}$ or $\\mathrm{mole}_{\\mathrm{i}} /$ cft",
                "aliases": ['lb mol_{i / ft^{3', 'mole_{i / cft'],
            },
            {
                "name": "pound_moles_of_i_per_gallon_us",
                "symbol": "lb $\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{gal}$ or $\\mathrm{mole}_{\\mathrm{i}} /$ gal",
                "si_factor": 10406.0,
                "full_name": "pound moles of \" $i$ \" per gallon (US)",
                "notation": "lb $\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{gal}$ or $\\mathrm{mole}_{\\mathrm{i}} /$ gal",
                "aliases": ['lb mol_{i / gal', 'mole_{i / gal'],
            }
        ],
        "aliases": {}
    },

    "mole_fraction_of_i": {
        # Mole Fraction of "i" - Dimensionless
        "dimension": DIMENSIONLESS,
        "units": [
            {
                "name": "gram_mole_of_i_per_gram_mole_total",
                "symbol": "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{mol}$",
                "si_factor": 1.0,
                "full_name": "gram mole of \"i\" per gram mole total",
                "notation": "$\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{mol}$",
                "aliases": [],
            },
            {
                "name": "kilogram_mole_of_i_per_kilogram_mole_total",
                "symbol": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kmol}$",
                "si_factor": 1.0,
                "full_name": "kilogram mole of \"i\" per kilogram mole total",
                "notation": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kmol}$",
                "aliases": [],
            },
            {
                "name": "kilomole_of_i_per_kilomole_total",
                "symbol": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kmol}$",
                "si_factor": 1.0,
                "full_name": "kilomole of \"i\" per kilomole total",
                "notation": "$\\mathrm{kmol}_{\\mathrm{i}} / \\mathrm{kmol}$",
                "aliases": [],
            },
            {
                "name": "pound_mole_of_i_per_pound_mole_total",
                "symbol": "lb $\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{lb} \\mathrm{mol}$",
                "si_factor": 1.0,
                "full_name": "pound mole of \"i\" per pound mole total",
                "notation": "lb $\\mathrm{mol}_{\\mathrm{i}} / \\mathrm{lb} \\mathrm{mol}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "moment_of_inertia": {
        # Moment of Inertia - LENGTH^2 MASS
        "dimension": MOMENT_OF_INERTIA,
        "units": [
            {
                "name": "gram_force_centimeter_square_second",
                "symbol": "$\\mathrm{g}_{\\mathrm{f}} \\mathrm{cm} \\mathrm{s}^{2}$",
                "si_factor": 9.8067e-05,
                "full_name": "gram force centimeter square second",
                "notation": "$\\mathrm{g}_{\\mathrm{f}} \\mathrm{cm} \\mathrm{s}^{2}$",
                "aliases": [],
            },
            {
                "name": "gram_square_centimeter",
                "symbol": "$\\mathrm{g} \\mathrm{cm}^{2}$",
                "si_factor": 1e-07,
                "full_name": "gram square centimeter",
                "notation": "$\\mathrm{g} \\mathrm{cm}^{2}$",
                "aliases": [],
            },
            {
                "name": "kilogram_force_centimeter_square_second",
                "symbol": "$\\mathrm{kg}_{\\mathrm{f}} \\mathrm{cm} \\mathrm{s}{ }^{2}$",
                "si_factor": 0.098067,
                "full_name": "kilogram force centimeter square second",
                "notation": "$\\mathrm{kg}_{\\mathrm{f}} \\mathrm{cm} \\mathrm{s}{ }^{2}$",
                "aliases": [],
            },
            {
                "name": "kilogram_force_meter_square_second",
                "symbol": "$\\mathrm{kg}_{\\mathrm{f}} \\mathrm{m} \\mathrm{s}^{2}$",
                "si_factor": 9.8067,
                "full_name": "kilogram force meter square second",
                "notation": "$\\mathrm{kg}_{\\mathrm{f}} \\mathrm{m} \\mathrm{s}^{2}$",
                "aliases": [],
            },
            {
                "name": "kilogram_square_centimeter",
                "symbol": "$\\mathrm{kg} \\mathrm{cm}^{2}$",
                "si_factor": 0.0001,
                "full_name": "kilogram square centimeter",
                "notation": "$\\mathrm{kg} \\mathrm{cm}^{2}$",
                "aliases": [],
            },
            {
                "name": "kilogram_square_meter",
                "symbol": "$\\mathrm{kg} \\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "kilogram square meter",
                "notation": "$\\mathrm{kg} \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "ounce_force_inch_square_second",
                "symbol": "$\\mathrm{oz}_{\\mathrm{f}}$ in $\\mathrm{s}^{2}$",
                "si_factor": 0.0070616,
                "full_name": "ounce force inch square second",
                "notation": "$\\mathrm{oz}_{\\mathrm{f}}$ in $\\mathrm{s}^{2}$",
                "aliases": [],
            },
            {
                "name": "ounce_mass_square_inch",
                "symbol": "oz in ${ }^{2}$",
                "si_factor": 1.8290000000000003e-05,
                "full_name": "ounce mass square inch",
                "notation": "oz in ${ }^{2}$",
                "aliases": [],
            },
            {
                "name": "pound_mass_square_foot",
                "symbol": "lb ft ${ }^{2}$ or lb sq ft",
                "si_factor": 0.04214,
                "full_name": "pound mass square foot",
                "notation": "lb ft ${ }^{2}$ or lb sq ft",
                "aliases": ['lb ft { ^{2', 'lb sq ft'],
            },
            {
                "name": "pound_mass_square_inch",
                "symbol": "$\\mathrm{lb} \\mathrm{in}^{2}$",
                "si_factor": 0.00029264000000000004,
                "full_name": "pound mass square inch",
                "notation": "$\\mathrm{lb} \\mathrm{in}^{2}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "momentum_flow_rate": {
        # Momentum Flow Rate - LENGTH MASS TIME^-2
        "dimension": MOMENTUM_FLOW_RATE,
        "units": [
            {
                "name": "foot_pounds_per_square_hour",
                "symbol": "$\\mathrm{ft} \\mathrm{lb} / \\mathrm{h}^{2}$ or $\\mathrm{ft} \\mathrm{lb} / \\mathrm{hr}^{2}$",
                "si_factor": 1.0671e-08,
                "full_name": "foot pounds per square hour",
                "notation": "$\\mathrm{ft} \\mathrm{lb} / \\mathrm{h}^{2}$ or $\\mathrm{ft} \\mathrm{lb} / \\mathrm{hr}^{2}$",
                "aliases": ['ft lb / h^{2', 'ft lb / hr^{2'],
            },
            {
                "name": "foot_pounds_per_square_minute",
                "symbol": "$\\mathrm{ft} \\mathrm{lb} / \\mathrm{min}^{2}$",
                "si_factor": 3.8417e-05,
                "full_name": "foot pounds per square minute",
                "notation": "$\\mathrm{ft} \\mathrm{lb} / \\mathrm{min}^{2}$",
                "aliases": [],
            },
            {
                "name": "foot_pounds_per_square_second",
                "symbol": "$\\mathrm{ft} \\mathrm{lb} / \\mathrm{s}^{2}$ or ft lb/sec ${ }^{2}$",
                "si_factor": 0.1383,
                "full_name": "foot pounds per square second",
                "notation": "$\\mathrm{ft} \\mathrm{lb} / \\mathrm{s}^{2}$ or ft lb/sec ${ }^{2}$",
                "aliases": ['ft lb / s^{2', 'ft lb/sec { ^{2'],
            },
            {
                "name": "gram_centimeters_per_square_second",
                "symbol": "$\\mathrm{g} \\mathrm{cm} / \\mathrm{s}^{2}$",
                "si_factor": 1e-05,
                "full_name": "gram centimeters per square second",
                "notation": "$\\mathrm{g} \\mathrm{cm} / \\mathrm{s}^{2}$",
                "aliases": [],
            },
            {
                "name": "kilogram_meters_per_square_second",
                "symbol": "$\\mathrm{kg} \\mathrm{m} / \\mathrm{s}^{2}$",
                "si_factor": 1.0,
                "full_name": "kilogram meters per square second",
                "notation": "$\\mathrm{kg} \\mathrm{m} / \\mathrm{s}^{2}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "momentum_flux": {
        # Momentum Flux - LENGTH^-1 MASS TIME^-2
        "dimension": MOMENTUM_FLUX,
        "units": [
            {
                "name": "dyne_per_square_centimeter",
                "symbol": "dyn/ $\\mathrm{cm}^{2}$",
                "si_factor": 10.0,
                "full_name": "dyne per square centimeter",
                "notation": "dyn/ $\\mathrm{cm}^{2}$",
                "aliases": [],
            },
            {
                "name": "gram_per_centimeter_per_square_second",
                "symbol": "$\\mathrm{g} / \\mathrm{cm} / \\mathrm{s}^{2}$",
                "si_factor": 10.0,
                "full_name": "gram per centimeter per square second",
                "notation": "$\\mathrm{g} / \\mathrm{cm} / \\mathrm{s}^{2}$",
                "aliases": [],
            },
            {
                "name": "newton_per_square_meter",
                "symbol": "$\\mathrm{N} / \\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "newton per square meter",
                "notation": "$\\mathrm{N} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "pound_force_per_square_foot",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{sq} \\mathrm{ft}$",
                "si_factor": 478.8,
                "full_name": "pound force per square foot",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{sq} \\mathrm{ft}$",
                "aliases": [],
            },
            {
                "name": "pound_mass_per_foot_per_square_second",
                "symbol": "$\\mathrm{lb}_{\\mathrm{m}} / \\mathrm{ft} / \\mathrm{s}^{2}$ or $\\mathrm{lb} / \\mathrm{ft} / \\mathrm{sec}^{2}$",
                "si_factor": 14.882,
                "full_name": "pound mass per foot per square second",
                "notation": "$\\mathrm{lb}_{\\mathrm{m}} / \\mathrm{ft} / \\mathrm{s}^{2}$ or $\\mathrm{lb} / \\mathrm{ft} / \\mathrm{sec}^{2}$",
                "aliases": ['lb_{m / ft / s^{2', 'lb / ft / sec^{2'],
            }
        ],
        "aliases": {}
    },

    "normality_of_solution": {
        # Normality of Solution - AMOUNT LENGTH^-3
        "dimension": NORMALITY_OF_SOLUTION,
        "units": [
            {
                "name": "gram_equivalents_per_cubic_meter",
                "symbol": "$\\mathrm{eq} / \\mathrm{m}^{3}$",
                "si_factor": 1.0,
                "full_name": "gram equivalents per cubic meter",
                "notation": "$\\mathrm{eq} / \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "gram_equivalents_per_liter",
                "symbol": "eq/l",
                "si_factor": 1000.0,
                "full_name": "gram equivalents per liter",
                "notation": "eq/l",
                "aliases": [],
            },
            {
                "name": "pound_equivalents_per_cubic_foot",
                "symbol": "$\\mathrm{lb} \\mathrm{eq} / \\mathrm{ft}^{3}$ or lb eq/cft",
                "si_factor": 77844.0,
                "full_name": "pound equivalents per cubic foot",
                "notation": "$\\mathrm{lb} \\mathrm{eq} / \\mathrm{ft}^{3}$ or lb eq/cft",
                "aliases": ['lb eq / ft^{3', 'lb eq/cft'],
            },
            {
                "name": "pound_equivalents_per_gallon",
                "symbol": "lb eq/gal (US)",
                "si_factor": 10406.0,
                "full_name": "pound equivalents per gallon",
                "notation": "lb eq/gal (US)",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "particle_density": {
        # Particle Density - LENGTH^-3
        "dimension": PARTICLE_DENSITY,
        "units": [
            {
                "name": "particles_per_cubic_centimeter",
                "symbol": "part/cm ${ }^{3}$ or part/cc",
                "si_factor": 10000.0,
                "full_name": "particles per cubic centimeter",
                "notation": "part/cm ${ }^{3}$ or part/cc",
                "aliases": ['part/cm { ^{3', 'part/cc'],
            },
            {
                "name": "particles_per_cubic_foot",
                "symbol": "part/ $\\mathrm{ft}^{3}$ or part/cft",
                "si_factor": 35.31,
                "full_name": "particles per cubic foot",
                "notation": "part/ $\\mathrm{ft}^{3}$ or part/cft",
                "aliases": ['part/ ft^{3', 'part/cft'],
            },
            {
                "name": "particles_per_cubic_meter",
                "symbol": "part $/ \\mathrm{m}^{3}$",
                "si_factor": 1.0,
                "full_name": "particles per cubic meter",
                "notation": "part $/ \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "particles_per_gallon_us",
                "symbol": "part/gal",
                "si_factor": 264.14,
                "full_name": "particles per gallon (US)",
                "notation": "part/gal",
                "aliases": [],
            },
            {
                "name": "particles_per_liter",
                "symbol": "part/l",
                "si_factor": 1000.0,
                "full_name": "particles per liter",
                "notation": "part/l",
                "aliases": [],
            },
            {
                "name": "particles_per_milliliter",
                "symbol": "part/ml",
                "si_factor": 10000.0,
                "full_name": "particles per milliliter",
                "notation": "part/ml",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "permeability": {
        # Permeability - LENGTH^2
        "dimension": PERMEABILITY,
        "units": [
            {
                "name": "darcy",
                "symbol": "darcy",
                "si_factor": 9.8692e-13,
                "full_name": "darcy",
                "notation": "darcy",
                "aliases": [],
            },
            {
                "name": "square_feet",
                "symbol": "$\\mathrm{ft}^{2}$ or sq ft",
                "si_factor": 0.0929,
                "full_name": "square feet",
                "notation": "$\\mathrm{ft}^{2}$ or sq ft",
                "aliases": ['ft^{2', 'sq ft'],
            },
            {
                "name": "square_meters",
                "symbol": "$\\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "square meters",
                "notation": "$\\mathrm{m}^{2}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "photon_emission_rate": {
        # Photon Emission Rate - LENGTH^-2 TIME^-1
        "dimension": PHOTON_EMISSION_RATE,
        "units": [
            {
                "name": "rayleigh",
                "symbol": "R",
                "si_factor": 10000000000.0,
                "full_name": "rayleigh",
                "notation": "R",
                "aliases": ['R'],
            },
            {
                "name": "reciprocal_square_meter_second",
                "symbol": "$1 /\\left(\\mathrm{m}^{2} \\mathrm{sec}\\right)$",
                "si_factor": 1.0,
                "full_name": "reciprocal square meter second",
                "notation": "$1 /\\left(\\mathrm{m}^{2} \\mathrm{sec}\\right)$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "power_per_unit_mass": {
        # Power per Unit Mass or Specific Power - LENGTH^2 TIME^-3
        "dimension": POWER_PER_UNIT_MASS,
        "units": [
            {
                "name": "british_thermal_unit_per_hour_per_pound_mass",
                "symbol": "Btu/h/lb or Btu/ (lb hr)",
                "si_factor": 0.64612,
                "full_name": "British thermal unit per hour per pound mass",
                "notation": "Btu/h/lb or Btu/ (lb hr)",
                "aliases": ['Btu/h/lb', 'Btu/ (lb hr)'],
            },
            {
                "name": "calorie_per_second_per_gram",
                "symbol": "cal/s/g or cal/(g sec)",
                "si_factor": 4186.8,
                "full_name": "calorie per second per gram",
                "notation": "cal/s/g or cal/(g sec)",
                "aliases": ['cal/s/g', 'cal/(g sec)'],
            },
            {
                "name": "kilocalorie_per_hour_per_kilogram",
                "symbol": "kcal/h/kg or kcal/ (kg hr)",
                "si_factor": 1.163,
                "full_name": "kilocalorie per hour per kilogram",
                "notation": "kcal/h/kg or kcal/ (kg hr)",
                "aliases": ['kcal/h/kg', 'kcal/ (kg hr)'],
            },
            {
                "name": "watt_per_kilogram",
                "symbol": "W/kg",
                "si_factor": 1.0,
                "full_name": "watt per kilogram",
                "notation": "W/kg",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "power_per_unit_volume": {
        # Power per Unit Volume or Power Density - LENGTH^-1 MASS TIME^-3
        "dimension": POWER_PER_UNIT_VOLUME,
        "units": [
            {
                "name": "british_thermal_unit_per_hour_per_cubic_foot",
                "symbol": "$\\mathrm{Btu} / \\mathrm{h} / \\mathrm{ft}^{3}$ or $\\mathrm{Btu} / \\mathrm{hr} /$ cft",
                "si_factor": 10.35,
                "full_name": "British thermal unit per hour per cubic foot",
                "notation": "$\\mathrm{Btu} / \\mathrm{h} / \\mathrm{ft}^{3}$ or $\\mathrm{Btu} / \\mathrm{hr} /$ cft",
                "aliases": ['Btu / h / ft^{3', 'Btu / hr / cft'],
            },
            {
                "name": "calorie_per_second_per_cubic_centimeter",
                "symbol": "$\\mathrm{cal} / \\mathrm{s} / \\mathrm{cm}^{3}$ or $\\mathrm{cal} / \\mathrm{s} / \\mathrm{cc}$",
                "si_factor": 4186800.0,
                "full_name": "calorie per second per cubic centimeter",
                "notation": "$\\mathrm{cal} / \\mathrm{s} / \\mathrm{cm}^{3}$ or $\\mathrm{cal} / \\mathrm{s} / \\mathrm{cc}$",
                "aliases": ['cal / s / cm^{3', 'cal / s / cc'],
            },
            {
                "name": "chu_per_hour_per_cubic_foot",
                "symbol": "Chu/h/ft3 or Chu/hr/ cft",
                "si_factor": 18.63,
                "full_name": "Chu per hour per cubic foot",
                "notation": "Chu/h/ft3 or Chu/hr/ cft",
                "aliases": ['Chu/h/ft3', 'Chu/hr/ cft'],
            },
            {
                "name": "kilocalorie_per_hour_per_cubic_centimeter",
                "symbol": "$\\mathrm{kcal} / \\mathrm{h} / \\mathrm{cm}^{3}$ or $\\mathrm{kcal} /$ hr/cc",
                "si_factor": 1.163,
                "full_name": "kilocalorie per hour per cubic centimeter",
                "notation": "$\\mathrm{kcal} / \\mathrm{h} / \\mathrm{cm}^{3}$ or $\\mathrm{kcal} /$ hr/cc",
                "aliases": ['kcal / h / cm^{3', 'kcal / hr/cc'],
            },
            {
                "name": "kilocalorie_per_hour_per_cubic_foot",
                "symbol": "$\\mathrm{kcal} / \\mathrm{h} / \\mathrm{ft}^{3}$ or $\\mathrm{kcal} / \\mathrm{hr} /$ cft",
                "si_factor": 41.071,
                "full_name": "kilocalorie per hour per cubic foot",
                "notation": "$\\mathrm{kcal} / \\mathrm{h} / \\mathrm{ft}^{3}$ or $\\mathrm{kcal} / \\mathrm{hr} /$ cft",
                "aliases": ['kcal / h / ft^{3', 'kcal / hr / cft'],
            },
            {
                "name": "kilocalorie_per_second_per_cubic_centimeter",
                "symbol": "kcal/s/cm ${ }^{3}$ or kcal/s/ cc",
                "si_factor": 4186800000.0,
                "full_name": "kilocalorie per second per cubic centimeter",
                "notation": "kcal/s/cm ${ }^{3}$ or kcal/s/ cc",
                "aliases": ['kcal/s/cm { ^{3', 'kcal/s/ cc'],
            },
            {
                "name": "watt_per_cubic_meter",
                "symbol": "$\\mathrm{W} / \\mathrm{m}^{3}$",
                "si_factor": 1.0,
                "full_name": "watt per cubic meter",
                "notation": "$\\mathrm{W} / \\mathrm{m}^{3}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "power_thermal_duty": {
        # Power, Thermal Duty - LENGTH^2 MASS TIME^-3
        "dimension": POWER_THERMAL_DUTY,
        "units": [
            {
                "name": "abwatt_emu_of_power",
                "symbol": "emu",
                "si_factor": 1e-08,
                "full_name": "abwatt (emu of power)",
                "notation": "emu",
                "aliases": ['emu'],
            },
            {
                "name": "boiler_horsepower",
                "symbol": "HP (boiler)",
                "si_factor": 9809.5,
                "full_name": "boiler horsepower",
                "notation": "HP (boiler)",
                "aliases": [],
            },
            {
                "name": "british_thermal_unit_mean",
                "symbol": "Btu (mean)/hr or Btu/hr",
                "si_factor": 0.293297,
                "full_name": "British thermal unit (mean) per hour",
                "notation": "Btu (mean)/hr or Btu/hr",
                "aliases": ['Btu (mean)/hr', 'Btu/hr'],
            },
            {
                "name": "british_thermal_unit_thermochemical",
                "symbol": "Btu (therm)/hr or Btu/hr",
                "si_factor": 0.292875,
                "full_name": "British thermal unit (thermochemical) per hour",
                "notation": "Btu (therm)/hr or Btu/hr",
                "aliases": ['Btu (therm)/hr', 'Btu/hr'],
            },
            {
                "name": "calorie_mean",
                "symbol": "cal (mean)/hr",
                "si_factor": 0.00116389,
                "full_name": "calorie (mean) per hour",
                "notation": "cal (mean)/hr",
                "aliases": [],
            },
            {
                "name": "calorie_thermochemical",
                "symbol": "cal (therm)/hr",
                "si_factor": 0.00116222,
                "full_name": "calorie (thermochemical) per hour",
                "notation": "cal (therm)/hr",
                "aliases": [],
            },
            {
                "name": "donkey",
                "symbol": "donkey",
                "si_factor": 250.0,
                "full_name": "donkey",
                "notation": "donkey",
                "aliases": [],
            },
            {
                "name": "erg_per_second",
                "symbol": "erg/s",
                "si_factor": 1e-07,
                "full_name": "erg per second",
                "notation": "erg/s",
                "aliases": [],
            },
            {
                "name": "foot_pondal_per_second",
                "symbol": "ft pdl/s",
                "si_factor": 0.04214,
                "full_name": "foot pondal per second",
                "notation": "ft pdl/s",
                "aliases": [],
            },
            {
                "name": "foot_pound_force_per_hour",
                "symbol": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{hr}$",
                "si_factor": 0.00037044000000000004,
                "full_name": "foot pound force per hour",
                "notation": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{hr}$",
                "aliases": [],
            },
            {
                "name": "foot_pound_force_per_minute",
                "symbol": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\min$",
                "si_factor": 0.022597,
                "full_name": "foot pound force per minute",
                "notation": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\min$",
                "aliases": [],
            },
            {
                "name": "foot_pound_force_per_second",
                "symbol": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{s}$",
                "si_factor": 1.355818,
                "full_name": "foot pound force per second",
                "notation": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "gigawatt",
                "symbol": "GW",
                "si_factor": 1000000000.0,
                "full_name": "gigawatt",
                "notation": "GW",
                "aliases": [],
            },
            {
                "name": "horsepower_550_mathrmft_mathrmlb_mathrmf_mathrms",
                "symbol": "HP",
                "si_factor": 745.7,
                "full_name": "horsepower ( $550 \\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}} / \\mathrm{s}$ )",
                "notation": "HP",
                "aliases": ['HP'],
            },
            {
                "name": "horsepower_electric",
                "symbol": "HP (elect)",
                "si_factor": 746.0,
                "full_name": "horsepower (electric)",
                "notation": "HP (elect)",
                "aliases": [],
            },
            {
                "name": "horsepower_uk",
                "symbol": "HP (UK)",
                "si_factor": 745.7,
                "full_name": "horsepower (UK)",
                "notation": "HP (UK)",
                "aliases": [],
            },
            {
                "name": "kcal_per_hour",
                "symbol": "kcal/hr",
                "si_factor": 1.16389,
                "full_name": "kcal per hour",
                "notation": "kcal/hr",
                "aliases": [],
            },
            {
                "name": "kilogram_force_meter_per_second",
                "symbol": "$\\mathrm{kg}_{\\mathrm{f}} \\mathrm{m} / \\mathrm{s}$",
                "si_factor": 9.80665,
                "full_name": "kilogram force meter per second",
                "notation": "$\\mathrm{kg}_{\\mathrm{f}} \\mathrm{m} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "kilowatt",
                "symbol": "kW",
                "si_factor": 1000.0,
                "full_name": "kilowatt",
                "notation": "kW",
                "aliases": ['kW'],
            },
            {
                "name": "megawatt",
                "symbol": "MW",
                "si_factor": 1000000.0,
                "full_name": "megawatt",
                "notation": "MW",
                "aliases": ['MW'],
            },
            {
                "name": "metric_horsepower",
                "symbol": "HP (metric)",
                "si_factor": 735.499,
                "full_name": "metric horsepower",
                "notation": "HP (metric)",
                "aliases": [],
            },
            {
                "name": "microwatt",
                "symbol": "μW",
                "si_factor": 1e-06,
                "full_name": "microwatt",
                "notation": "μW",
                "aliases": [],
            },
            {
                "name": "million_british_thermal_units_per_hour_petroleum",
                "symbol": "MMBtu/hr",
                "si_factor": 293297.0,
                "full_name": "million British thermal units per hour (petroleum)",
                "notation": "MMBtu/hr",
                "aliases": [],
            },
            {
                "name": "million_kilocalorie_per_hour",
                "symbol": "MM kcal/hr",
                "si_factor": 1163890.0,
                "full_name": "million kilocalorie per hour",
                "notation": "MM kcal/hr",
                "aliases": [],
            },
            {
                "name": "milliwatt",
                "symbol": "mW",
                "si_factor": 0.001,
                "full_name": "milliwatt",
                "notation": "mW",
                "aliases": [],
            },
            {
                "name": "prony",
                "symbol": "prony",
                "si_factor": 98.0665,
                "full_name": "prony",
                "notation": "prony",
                "aliases": [],
            },
            {
                "name": "ton_of_refrigeration_us",
                "symbol": "CTR (US)",
                "si_factor": 3516.8,
                "full_name": "ton of refrigeration (US)",
                "notation": "CTR (US)",
                "aliases": [],
            },
            {
                "name": "ton_or_refrigeration_uk",
                "symbol": "CTR (UK)",
                "si_factor": 3922.7,
                "full_name": "ton or refrigeration (UK)",
                "notation": "CTR (UK)",
                "aliases": [],
            },
            {
                "name": "volt_ampere",
                "symbol": "VA",
                "si_factor": 1.0,
                "full_name": "volt-ampere",
                "notation": "VA",
                "aliases": ['VA'],
            },
            {
                "name": "water_horsepower",
                "symbol": "HP (water)",
                "si_factor": 746.043,
                "full_name": "water horsepower",
                "notation": "HP (water)",
                "aliases": [],
            },
            {
                "name": "watt",
                "symbol": "W",
                "si_factor": 1.0,
                "full_name": "watt",
                "notation": "W",
                "aliases": ['W'],
            },
            {
                "name": "watt_international_mean",
                "symbol": "W (int, mean)",
                "si_factor": 1.00019,
                "full_name": "watt (international, mean)",
                "notation": "W (int, mean)",
                "aliases": [],
            },
            {
                "name": "watt_international_us",
                "symbol": "watt (int, US)",
                "si_factor": 1.000165,
                "full_name": "watt (international, US)",
                "notation": "watt (int, US)",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "pressure": {
        # Pressure - LENGTH^-1 MASS TIME^-2
        "dimension": PRESSURE,
        "units": [
            {
                "name": "atmosphere_standard",
                "symbol": "atm",
                "si_factor": 101325.0,
                "full_name": "atmosphere, standard",
                "notation": "atm",
                "aliases": ['atm'],
            },
            {
                "name": "bar",
                "symbol": "bar",
                "si_factor": 100000.0,
                "full_name": "bar",
                "notation": "bar",
                "aliases": ['bar'],
            },
            {
                "name": "barye",
                "symbol": "barye",
                "si_factor": 0.1,
                "full_name": "barye",
                "notation": "barye",
                "aliases": [],
            },
            {
                "name": "dyne_per_square_centimeter",
                "symbol": "dyn $/ \\mathrm{cm}^{2}$",
                "si_factor": 0.1,
                "full_name": "dyne per square centimeter",
                "notation": "dyn $/ \\mathrm{cm}^{2}$",
                "aliases": [],
            },
            {
                "name": "foot_of_mercury_60_circ_mathrmf",
                "symbol": "ft Hg ( $60{ }^{\\circ} \\mathrm{F}$ )",
                "si_factor": 40526.0,
                "full_name": "foot of mercury ( $60{ }^{\\circ} \\mathrm{F}$ )",
                "notation": "ft Hg ( $60{ }^{\\circ} \\mathrm{F}$ )",
                "aliases": [],
            },
            {
                "name": "foot_of_water_60_circ_mathrmf",
                "symbol": "ft $\\mathrm{H}_{2} \\mathrm{O}\\left(60^{\\circ} \\mathrm{F}\\right)$",
                "si_factor": 2989.0,
                "full_name": "foot of water ( $60{ }^{\\circ} \\mathrm{F}$ )",
                "notation": "ft $\\mathrm{H}_{2} \\mathrm{O}\\left(60^{\\circ} \\mathrm{F}\\right)$",
                "aliases": [],
            },
            {
                "name": "gigapascal",
                "symbol": "GPa",
                "si_factor": 1000000000.0,
                "full_name": "gigapascal",
                "notation": "GPa",
                "aliases": ['GPa'],
            },
            {
                "name": "hectopascal",
                "symbol": "hPa",
                "si_factor": 100.0,
                "full_name": "hectopascal",
                "notation": "hPa",
                "aliases": ['hPa'],
            },
            {
                "name": "inch_of_mercury_60_circ_mathrmf",
                "symbol": "in $\\mathrm{Hg}\\left(60{ }^{\\circ} \\mathrm{F}\\right)$",
                "si_factor": 3386.4,
                "full_name": "inch of mercury ( $60{ }^{\\circ} \\mathrm{F}$ )",
                "notation": "in $\\mathrm{Hg}\\left(60{ }^{\\circ} \\mathrm{F}\\right)$",
                "aliases": [],
            },
            {
                "name": "inch_of_water_60_circ_mathrmf",
                "symbol": "in $\\mathrm{H}_{2} \\mathrm{O}\\left(60^{\\circ} \\mathrm{F}\\right)$",
                "si_factor": 248.845,
                "full_name": "inch of water ( $60{ }^{\\circ} \\mathrm{F}$ )",
                "notation": "in $\\mathrm{H}_{2} \\mathrm{O}\\left(60^{\\circ} \\mathrm{F}\\right)$",
                "aliases": [],
            },
            {
                "name": "kilogram_force_per_square_centimeter",
                "symbol": "at or $\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{cm}^{2}$",
                "si_factor": 98067.0,
                "full_name": "kilogram force per square centimeter",
                "notation": "at or $\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{cm}^{2}$",
                "aliases": ['at', 'kg_{f / cm^{2'],
            },
            {
                "name": "kilogram_force_per_square_meter",
                "symbol": "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{m}^{2}$",
                "si_factor": 9.80665,
                "full_name": "kilogram force per square meter",
                "notation": "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "kilopascal",
                "symbol": "kPa",
                "si_factor": 1000.0,
                "full_name": "kilopascal",
                "notation": "kPa",
                "aliases": [],
            },
            {
                "name": "kip_force_per_square_inch",
                "symbol": "KSI or ksi or kip ${ }_{f} / \\mathrm{in}^{2}$",
                "si_factor": 6894800.0,
                "full_name": "kip force per square inch",
                "notation": "KSI or ksi or kip ${ }_{f} / \\mathrm{in}^{2}$",
                "aliases": ['KSI', 'ksi', 'kip { _{f / in^{2'],
            },
            {
                "name": "megapascal",
                "symbol": "MPa",
                "si_factor": 1000000.0,
                "full_name": "megapascal",
                "notation": "MPa",
                "aliases": ['MPa'],
            },
            {
                "name": "meter_of_water_4circ_mathrmc",
                "symbol": "$\\mathrm{m} \\mathrm{H}_{2} \\mathrm{O}\\left(4^{\\circ} \\mathrm{C}\\right)$",
                "si_factor": 9806.4,
                "full_name": "meter of water ( $4^{\\circ} \\mathrm{C}$ )",
                "notation": "$\\mathrm{m} \\mathrm{H}_{2} \\mathrm{O}\\left(4^{\\circ} \\mathrm{C}\\right)$",
                "aliases": [],
            },
            {
                "name": "microbar",
                "symbol": "$\\mu \\mathrm{bar}$",
                "si_factor": 0.1,
                "full_name": "microbar",
                "notation": "$\\mu \\mathrm{bar}$",
                "aliases": [],
            },
            {
                "name": "millibar",
                "symbol": "mbar",
                "si_factor": 100.0,
                "full_name": "millibar",
                "notation": "mbar",
                "aliases": ['mbar'],
            },
            {
                "name": "millimeter_of_mercury_4circ_mathrmc",
                "symbol": "$\\mathrm{mm} \\mathrm{Hg}\\left(4^{\\circ} \\mathrm{C}\\right)$",
                "si_factor": 133.322,
                "full_name": "millimeter of mercury ( $4^{\\circ} \\mathrm{C}$ )",
                "notation": "$\\mathrm{mm} \\mathrm{Hg}\\left(4^{\\circ} \\mathrm{C}\\right)$",
                "aliases": [],
            },
            {
                "name": "millimeter_of_water_4circ_mathrmc",
                "symbol": "$\\mathrm{mm} \\mathrm{H}_{2} \\mathrm{O}\\left(4^{\\circ} \\mathrm{C}\\right)$",
                "si_factor": 9.806375,
                "full_name": "millimeter of water ( $4^{\\circ} \\mathrm{C}$ )",
                "notation": "$\\mathrm{mm} \\mathrm{H}_{2} \\mathrm{O}\\left(4^{\\circ} \\mathrm{C}\\right)$",
                "aliases": [],
            },
            {
                "name": "newton_per_square_meter",
                "symbol": "$\\mathrm{N} / \\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "newton per square meter",
                "notation": "$\\mathrm{N} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "ounce_force_per_square_inch",
                "symbol": "OSI or osi or $\\mathrm{oz}_{\\mathrm{f}} / \\mathrm{in}^{2}$",
                "si_factor": 430.922,
                "full_name": "ounce force per square inch",
                "notation": "OSI or osi or $\\mathrm{oz}_{\\mathrm{f}} / \\mathrm{in}^{2}$",
                "aliases": ['OSI', 'osi'],
            },
            {
                "name": "pascal",
                "symbol": "Pa",
                "si_factor": 1.0,
                "full_name": "pascal",
                "notation": "Pa",
                "aliases": ['Pa'],
            },
            {
                "name": "pièze",
                "symbol": "pz",
                "si_factor": 1000.0,
                "full_name": "pièze",
                "notation": "pz",
                "aliases": ['pz'],
            },
            {
                "name": "pound_force_per_square_foot",
                "symbol": "PSF or psf or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}^{2}$",
                "si_factor": 47.880259,
                "full_name": "pound force per square foot",
                "notation": "PSF or psf or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}^{2}$",
                "aliases": ['psf'],
            },
            {
                "name": "pound_force_per_square_inch",
                "symbol": "PSI or psi or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{in}^{2}$",
                "si_factor": 6894.8,
                "full_name": "pound force per square inch",
                "notation": "PSI or psi or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{in}^{2}$",
                "aliases": ['psi'],
            },
            {
                "name": "torr",
                "symbol": "torr or mm Hg ( $0{ }^{\\circ}$ C)",
                "si_factor": 133.322,
                "full_name": "torr",
                "notation": "torr or mm Hg ( $0{ }^{\\circ}$ C)",
                "aliases": ['mm Hg ( 0{ ^{circ C)'],
            }
        ],
        "aliases": {}
    },

    "radiation_dose_equivalent": {
        # Radiation Dose Equivalent - LENGTH^2 TIME^-2
        "dimension": RADIATION_DOSE_EQUIVALENT,
        "units": [
            {
                "name": "microsievert",
                "symbol": "μSv",
                "si_factor": 1e-06,
                "full_name": "microsievert",
                "notation": "μSv",
                "aliases": [],
            },
            {
                "name": "millisievert",
                "symbol": "mSv",
                "si_factor": 0.001,
                "full_name": "millisievert",
                "notation": "mSv",
                "aliases": [],
            },
            {
                "name": "rem",
                "symbol": "rem",
                "si_factor": 0.01,
                "full_name": "rem",
                "notation": "rem",
                "aliases": ['rem'],
            },
            {
                "name": "sievert",
                "symbol": "Sv",
                "si_factor": 1.0,
                "full_name": "sievert",
                "notation": "Sv",
                "aliases": ['Sv'],
            }
        ],
        "aliases": {}
    },

    "radiation_exposure": {
        # Radiation Exposure - CURRENT MASS^-1 TIME
        "dimension": RADIATION_EXPOSURE,
        "units": [
            {
                "name": "coulomb_per_kilogram",
                "symbol": "C/kg",
                "si_factor": 1.0,
                "full_name": "coulomb per kilogram",
                "notation": "C/kg",
                "aliases": [],
            },
            {
                "name": "d_unit",
                "symbol": "D unit",
                "si_factor": 0.0258,
                "full_name": "D unit",
                "notation": "D unit",
                "aliases": [],
            },
            {
                "name": "pastille_dose_b_unit",
                "symbol": "B unit",
                "si_factor": 0.129,
                "full_name": "pastille dose (B unit)",
                "notation": "B unit",
                "aliases": [],
            },
            {
                "name": "röentgen",
                "symbol": "R",
                "si_factor": 0.000258,
                "full_name": "röentgen",
                "notation": "R",
                "aliases": ['R'],
            }
        ],
        "aliases": {}
    },

    "radioactivity": {
        # Radioactivity - TIME^-1
        "dimension": RADIOACTIVITY,
        "units": [
            {
                "name": "becquerel",
                "symbol": "Bq",
                "si_factor": 1.0,
                "full_name": "becquerel",
                "notation": "Bq",
                "aliases": ['Bq'],
            },
            {
                "name": "curie",
                "symbol": "Ci",
                "si_factor": 37000000000.0,
                "full_name": "curie",
                "notation": "Ci",
                "aliases": ['Ci'],
            },
            {
                "name": "gigabecquerel",
                "symbol": "GBq",
                "si_factor": 1000000000.0,
                "full_name": "gigabecquerel",
                "notation": "GBq",
                "aliases": [],
            },
            {
                "name": "kilobecquerel",
                "symbol": "kBq",
                "si_factor": 1000.0,
                "full_name": "kilobecquerel",
                "notation": "kBq",
                "aliases": [],
            },
            {
                "name": "mache_unit",
                "symbol": "Mache",
                "si_factor": 13.32,
                "full_name": "Mache unit",
                "notation": "Mache",
                "aliases": [],
            },
            {
                "name": "megabecquerel",
                "symbol": "MBq",
                "si_factor": 1000000.0,
                "full_name": "megabecquerel",
                "notation": "MBq",
                "aliases": [],
            },
            {
                "name": "rutherford",
                "symbol": "Rd",
                "si_factor": 1000000.0,
                "full_name": "rutherford",
                "notation": "Rd",
                "aliases": ['Rd'],
            },
            {
                "name": "stat",
                "symbol": "stat",
                "si_factor": 1.34e-16,
                "full_name": "stat",
                "notation": "stat",
                "aliases": ['stat'],
            }
        ],
        "aliases": {}
    },

    "second_moment_of_area": {
        # Second Moment of Area - LENGTH^4
        "dimension": SECOND_MOMENT_OF_AREA,
        "units": [
            {
                "name": "centimeter_quadrupled",
                "symbol": "$\\mathrm{cm}^{4}$",
                "si_factor": 1e-08,
                "full_name": "centimeter quadrupled",
                "notation": "$\\mathrm{cm}^{4}$",
                "aliases": [],
            },
            {
                "name": "foot_quadrupled",
                "symbol": "$\\mathrm{ft}^{4}$",
                "si_factor": 0.008631,
                "full_name": "foot quadrupled",
                "notation": "$\\mathrm{ft}^{4}$",
                "aliases": [],
            },
            {
                "name": "inch_quadrupled",
                "symbol": "in ${ }^{4}$",
                "si_factor": 4.1623e-07,
                "full_name": "inch quadrupled",
                "notation": "in ${ }^{4}$",
                "aliases": [],
            },
            {
                "name": "meter_quadrupled",
                "symbol": "$\\mathrm{m}^{4}$",
                "si_factor": 1.0,
                "full_name": "meter quadrupled",
                "notation": "$\\mathrm{m}^{4}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "second_radiation_constant_planck": {
        # Second Radiation Constant (Planck) - LENGTH TEMP
        "dimension": SECOND_RADIATION_CONSTANT_PLANCK,
        "units": [
            {
                "name": "meter_kelvin",
                "symbol": "m K",
                "si_factor": 1.0,
                "full_name": "meter kelvin",
                "notation": "m K",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "specific_enthalpy": {
        # Specific Enthalpy - LENGTH^2 TIME^-2
        "dimension": SPECIFIC_ENTHALPY,
        "units": [
            {
                "name": "british_thermal_unit_mean",
                "symbol": "Btu (mean)/lb",
                "si_factor": 2327.8,
                "full_name": "British thermal unit (mean) per pound",
                "notation": "Btu (mean)/lb",
                "aliases": [],
            },
            {
                "name": "british_thermal_unit_per_pound",
                "symbol": "Btu/lb",
                "si_factor": 2324.4,
                "full_name": "British thermal unit per pound",
                "notation": "Btu/lb",
                "aliases": [],
            },
            {
                "name": "calorie_per_gram",
                "symbol": "$\\mathrm{cal} / \\mathrm{g}$",
                "si_factor": 4186.8,
                "full_name": "calorie per gram",
                "notation": "$\\mathrm{cal} / \\mathrm{g}$",
                "aliases": [],
            },
            {
                "name": "chu_per_pound",
                "symbol": "Chu/lb",
                "si_factor": 4186.8,
                "full_name": "Chu per pound",
                "notation": "Chu/lb",
                "aliases": [],
            },
            {
                "name": "joule_per_kilogram",
                "symbol": "J/kg",
                "si_factor": 1.0,
                "full_name": "joule per kilogram",
                "notation": "J/kg",
                "aliases": [],
            },
            {
                "name": "kilojoule_per_kilogram",
                "symbol": "kJ/kg",
                "si_factor": 1000.0,
                "full_name": "kilojoule per kilogram",
                "notation": "kJ/kg",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "specific_gravity": {
        # Specific Gravity - Dimensionless
        "dimension": DIMENSIONLESS,
        "units": [
            {
                "name": "dimensionless",
                "symbol": "Dmls",
                "si_factor": 1.0,
                "full_name": "Dimensionless",
                "notation": "Dmls",
                "aliases": ['Dmls'],
            }
        ],
        "aliases": {}
    },

    "specific_heat_capacity_constant_pressure": {
        # Specific Heat Capacity (Constant Pressure) - LENGTH^2 MASS TEMP^-1 TIME^-2
        "dimension": SPECIFIC_HEAT_CAPACITY_CONSTANT_PRESSURE,
        "units": [
            {
                "name": "btu_per_pound_per_degree_fahrenheit_or_degree_rankine",
                "symbol": "Btu/(lb ${ }^{\\circ} \\mathrm{F}$ )",
                "si_factor": 4186.8,
                "full_name": "Btu per pound per degree Fahrenheit (or degree Rankine)",
                "notation": "Btu/(lb ${ }^{\\circ} \\mathrm{F}$ )",
                "aliases": [],
            },
            {
                "name": "calories_per_gram_per_kelvin_or_degree_celsius",
                "symbol": "cal/(g K)",
                "si_factor": 4186.8,
                "full_name": "calories per gram per kelvin (or degree Celsius)",
                "notation": "cal/(g K)",
                "aliases": [],
            },
            {
                "name": "joules_per_kilogram_per_kelvin_or_degree_celsius",
                "symbol": "J/(kg K)",
                "si_factor": 1.0,
                "full_name": "joules per kilogram per kelvin (or degree Celsius)",
                "notation": "J/(kg K)",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "specific_length": {
        # Specific Length - LENGTH MASS^-1
        "dimension": SPECIFIC_LENGTH,
        "units": [
            {
                "name": "centimeter_per_gram",
                "symbol": "cm/g",
                "si_factor": 10.0,
                "full_name": "centimeter per gram",
                "notation": "cm/g",
                "aliases": [],
            },
            {
                "name": "cotton_count",
                "symbol": "cc",
                "si_factor": 590500000.0,
                "full_name": "cotton count",
                "notation": "cc",
                "aliases": ['cc'],
            },
            {
                "name": "ft_per_pound",
                "symbol": "ft/lb",
                "si_factor": 0.67192,
                "full_name": "ft per pound",
                "notation": "ft/lb",
                "aliases": [],
            },
            {
                "name": "meters_per_kilogram",
                "symbol": "m/kg",
                "si_factor": 1.0,
                "full_name": "meters per kilogram",
                "notation": "m/kg",
                "aliases": [],
            },
            {
                "name": "newton_meter",
                "symbol": "Nm",
                "si_factor": 1000.0,
                "full_name": "newton meter",
                "notation": "Nm",
                "aliases": ['Nm'],
            },
            {
                "name": "worsted",
                "symbol": "worsted",
                "si_factor": 888679999.9999999,
                "full_name": "worsted",
                "notation": "worsted",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "specific_surface": {
        # Specific Surface - LENGTH^2 MASS^-1
        "dimension": SPECIFIC_SURFACE,
        "units": [
            {
                "name": "square_centimeter_per_gram",
                "symbol": "$\\mathrm{cm}^{2} / \\mathrm{g}$",
                "si_factor": 0.1,
                "full_name": "square centimeter per gram",
                "notation": "$\\mathrm{cm}^{2} / \\mathrm{g}$",
                "aliases": [],
            },
            {
                "name": "square_foot_per_kilogram",
                "symbol": "$\\mathrm{ft}^{2} / \\mathrm{kg}$ or sq ft/kg",
                "si_factor": 0.092903,
                "full_name": "square foot per kilogram",
                "notation": "$\\mathrm{ft}^{2} / \\mathrm{kg}$ or sq ft/kg",
                "aliases": ['ft^{2 / kg', 'sq ft/kg'],
            },
            {
                "name": "square_foot_per_pound",
                "symbol": "$\\mathrm{ft}^{2} / \\mathrm{lb}$ or sq ft/lb",
                "si_factor": 0.20482,
                "full_name": "square foot per pound",
                "notation": "$\\mathrm{ft}^{2} / \\mathrm{lb}$ or sq ft/lb",
                "aliases": ['ft^{2 / lb', 'sq ft/lb'],
            },
            {
                "name": "square_meter_per_gram",
                "symbol": "$\\mathrm{m}^{2} / \\mathrm{g}$",
                "si_factor": 1000.0,
                "full_name": "square meter per gram",
                "notation": "$\\mathrm{m}^{2} / \\mathrm{g}$",
                "aliases": [],
            },
            {
                "name": "square_meter_per_kilogram",
                "symbol": "$\\mathrm{m}^{2} / \\mathrm{kg}$",
                "si_factor": 1.0,
                "full_name": "square meter per kilogram",
                "notation": "$\\mathrm{m}^{2} / \\mathrm{kg}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "specific_volume": {
        # Specific Volume - LENGTH^3 MASS^-1
        "dimension": SPECIFIC_VOLUME,
        "units": [
            {
                "name": "cubic_centimeter_per_gram",
                "symbol": "$\\mathrm{cm}^{3} / \\mathrm{g}$ or $\\mathrm{cc} / \\mathrm{g}$",
                "si_factor": 0.001,
                "full_name": "cubic centimeter per gram",
                "notation": "$\\mathrm{cm}^{3} / \\mathrm{g}$ or $\\mathrm{cc} / \\mathrm{g}$",
                "aliases": ['cm^{3 / g', 'cc / g'],
            },
            {
                "name": "cubic_foot_per_kilogram",
                "symbol": "$\\mathrm{ft}^{3} / \\mathrm{kg}$ or $\\mathrm{cft} / \\mathrm{kg}$",
                "si_factor": 0.028317,
                "full_name": "cubic foot per kilogram",
                "notation": "$\\mathrm{ft}^{3} / \\mathrm{kg}$ or $\\mathrm{cft} / \\mathrm{kg}$",
                "aliases": ['ft^{3 / kg', 'cft / kg'],
            },
            {
                "name": "cubic_foot_per_pound",
                "symbol": "$\\mathrm{ft}^{3} / \\mathrm{lb}$ or $\\mathrm{cft} / \\mathrm{lb}$",
                "si_factor": 0.062428,
                "full_name": "cubic foot per pound",
                "notation": "$\\mathrm{ft}^{3} / \\mathrm{lb}$ or $\\mathrm{cft} / \\mathrm{lb}$",
                "aliases": ['ft^{3 / lb', 'cft / lb'],
            },
            {
                "name": "cubic_meter_per_kilogram",
                "symbol": "$\\mathrm{m}^{3} / \\mathrm{kg}$",
                "si_factor": 1.0,
                "full_name": "cubic meter per kilogram",
                "notation": "$\\mathrm{m}^{3} / \\mathrm{kg}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "stress": {
        # Stress - LENGTH^-1 MASS TIME^-2
        "dimension": STRESS,
        "units": [
            {
                "name": "dyne_per_square_centimeter",
                "symbol": "dyn/ $\\mathrm{cm}^{2}$",
                "si_factor": 0.1,
                "full_name": "dyne per square centimeter",
                "notation": "dyn/ $\\mathrm{cm}^{2}$",
                "aliases": [],
            },
            {
                "name": "gigapascal",
                "symbol": "GPa",
                "si_factor": 1000000000.0,
                "full_name": "gigapascal",
                "notation": "GPa",
                "aliases": ['GPa'],
            },
            {
                "name": "hectopascal",
                "symbol": "hPa",
                "si_factor": 100.0,
                "full_name": "hectopascal",
                "notation": "hPa",
                "aliases": ['hPa'],
            },
            {
                "name": "kilogram_force_per_square_centimeter",
                "symbol": "at or $\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{cm}^{2}$",
                "si_factor": 98067.0,
                "full_name": "kilogram force per square centimeter",
                "notation": "at or $\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{cm}^{2}$",
                "aliases": ['at', 'kg_{f / cm^{2'],
            },
            {
                "name": "kilogram_force_per_square_meter",
                "symbol": "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{m}^{2}$",
                "si_factor": 9.80665,
                "full_name": "kilogram force per square meter",
                "notation": "$\\mathrm{kg}_{\\mathrm{f}} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "kip_force_per_square_inch",
                "symbol": "KSI or ksi or kip ${ }_{f} / \\mathrm{in}^{2}$",
                "si_factor": 6894800.0,
                "full_name": "kip force per square inch",
                "notation": "KSI or ksi or kip ${ }_{f} / \\mathrm{in}^{2}$",
                "aliases": ['KSI', 'ksi', 'kip { _{f / in^{2'],
            },
            {
                "name": "megapascal",
                "symbol": "MPa",
                "si_factor": 1000000.0,
                "full_name": "megapascal",
                "notation": "MPa",
                "aliases": ['MPa'],
            },
            {
                "name": "newton_per_square_meter",
                "symbol": "$\\mathrm{N} / \\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "newton per square meter",
                "notation": "$\\mathrm{N} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "ounce_force_per_square_inch",
                "symbol": "OSI or osi or $\\mathrm{oz}_{\\mathrm{f}} / \\mathrm{in}^{2}$",
                "si_factor": 430.922,
                "full_name": "ounce force per square inch",
                "notation": "OSI or osi or $\\mathrm{oz}_{\\mathrm{f}} / \\mathrm{in}^{2}$",
                "aliases": ['OSI', 'osi', 'oz_{f / in^{2'],
            },
            {
                "name": "pascal",
                "symbol": "Pa",
                "si_factor": 1.0,
                "full_name": "pascal",
                "notation": "Pa",
                "aliases": ['Pa'],
            },
            {
                "name": "pound_force_per_square_foot",
                "symbol": "PSF or psf or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}^{2}$",
                "si_factor": 47.880259,
                "full_name": "pound force per square foot",
                "notation": "PSF or psf or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}^{2}$",
                "aliases": ['PSF', 'psf', 'lb_{f / ft^{2'],
            },
            {
                "name": "pound_force_per_square_inch",
                "symbol": "PSI or psi or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{in}^{2}$",
                "si_factor": 6894.8,
                "full_name": "pound force per square inch",
                "notation": "PSI or psi or $\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{in}^{2}$",
                "aliases": ['psi'],
            }
        ],
        "aliases": {}
    },

    "surface_mass_density": {
        # Surface Mass Density - LENGTH^-2 MASS
        "dimension": SURFACE_MASS_DENSITY,
        "units": [
            {
                "name": "gram_per_square_centimeter",
                "symbol": "$\\mathrm{kg} / \\mathrm{cm}^{2}$",
                "si_factor": 10.0,
                "full_name": "gram per square centimeter",
                "notation": "$\\mathrm{kg} / \\mathrm{cm}^{2}$",
                "aliases": [],
            },
            {
                "name": "gram_per_square_meter",
                "symbol": "$\\mathrm{g} / \\mathrm{m}^{2}$",
                "si_factor": 0.001,
                "full_name": "gram per square meter",
                "notation": "$\\mathrm{g} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "kilogram_per_square_meter",
                "symbol": "$\\mathrm{kg} / \\mathrm{m}^{2}$",
                "si_factor": 1.0,
                "full_name": "kilogram per square meter",
                "notation": "$\\mathrm{kg} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "pound_mass",
                "symbol": "$\\mathrm{lb} / \\mathrm{ft}^{2}$",
                "si_factor": 4.882427,
                "full_name": "pound (mass) per square foot",
                "notation": "$\\mathrm{lb} / \\mathrm{ft}^{2}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "surface_tension": {
        # Surface Tension - MASS TIME^-2
        "dimension": SURFACE_TENSION,
        "units": [
            {
                "name": "dyne_per_centimeter",
                "symbol": "dyn/cm",
                "si_factor": 0.001,
                "full_name": "dyne per centimeter",
                "notation": "dyn/cm",
                "aliases": [],
            },
            {
                "name": "gram_force_per_centimeter",
                "symbol": "$\\mathrm{g}_{\\mathrm{f}} / \\mathrm{cm}$",
                "si_factor": 0.0102,
                "full_name": "gram force per centimeter",
                "notation": "$\\mathrm{g}_{\\mathrm{f}} / \\mathrm{cm}$",
                "aliases": [],
            },
            {
                "name": "newton_per_meter",
                "symbol": "N/m",
                "si_factor": 1.0,
                "full_name": "newton per meter",
                "notation": "N/m",
                "aliases": [],
            },
            {
                "name": "pound_force_per_foot",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}$",
                "si_factor": 14.594,
                "full_name": "pound force per foot",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{ft}$",
                "aliases": [],
            },
            {
                "name": "pound_force_per_inch",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{in}$",
                "si_factor": 175.13,
                "full_name": "pound force per inch",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}} / \\mathrm{in}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "temperature": {
        # Temperature - TEMP
        "dimension": TEMPERATURE,
        "units": [
            {
                "name": "degree_celsius_unit_size",
                "symbol": "$\\mathrm{C}^{\\circ}$",
                "si_factor": 1.0,
                "full_name": "degree Celsius (unit size)",
                "notation": "$\\mathrm{C}^{\\circ}$",
                "aliases": [],
            },
            {
                "name": "degree_fahrenheit_unit_size",
                "symbol": "$\\mathrm{F}^{\\circ}$",
                "si_factor": 0.555556,
                "full_name": "degree Fahrenheit (unit size)",
                "notation": "$\\mathrm{F}^{\\circ}$",
                "aliases": [],
            },
            {
                "name": "degree_réaumur_unit_size",
                "symbol": "Ré ${ }^{\\circ}$",
                "si_factor": 1.25,
                "full_name": "degree Réaumur (unit size)",
                "notation": "Ré ${ }^{\\circ}$",
                "aliases": [],
            },
            {
                "name": "kelvin_absolute_scale",
                "symbol": "K",
                "si_factor": 1.0,
                "full_name": "kelvin (absolute scale)",
                "notation": "K",
                "aliases": ['K'],
            },
            {
                "name": "rankine_absolute_scale",
                "symbol": "${ }^{\\circ} \\mathrm{R}$",
                "si_factor": 0.555556,
                "full_name": "Rankine (absolute scale)",
                "notation": "${ }^{\\circ} \\mathrm{R}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "thermal_conductivity": {
        # Thermal Conductivity - LENGTH MASS TEMP TIME^-3
        "dimension": THERMAL_CONDUCTIVITY,
        "units": [
            {
                "name": "btu_it",
                "symbol": "Btu (IT)/(in hr ${ }^{\\circ} \\mathrm{F}$ )",
                "si_factor": 0.207688,
                "full_name": "Btu (IT) per inch per hour per degree Fahrenheit",
                "notation": "Btu (IT)/(in hr ${ }^{\\circ} \\mathrm{F}$ )",
                "aliases": [],
            },
            {
                "name": "btu_therm",
                "symbol": "$\\mathrm{Btu} /\\left(\\mathrm{ft} \\mathrm{hr}{ }^{\\circ} \\mathrm{F}\\right)$",
                "si_factor": 0.017296,
                "full_name": "Btu (therm) per foot per hour per degree Fahrenheit",
                "notation": "$\\mathrm{Btu} /\\left(\\mathrm{ft} \\mathrm{hr}{ }^{\\circ} \\mathrm{F}\\right)$",
                "aliases": [],
            },
            {
                "name": "calorie_therm",
                "symbol": "$\\operatorname{cal}(\\mathrm{IT}) /\\left(\\mathrm{cm} \\mathrm{s}^{\\circ} \\mathrm{C}\\right)$",
                "si_factor": 4.184,
                "full_name": "calorie (therm) per centimeter per second per degree Celsius",
                "notation": "$\\operatorname{cal}(\\mathrm{IT}) /\\left(\\mathrm{cm} \\mathrm{s}^{\\circ} \\mathrm{C}\\right)$",
                "aliases": [],
            },
            {
                "name": "joule_per_second_per_centimeter_per_kelvin",
                "symbol": "J/(cm s K)",
                "si_factor": 0.01,
                "full_name": "joule per second per centimeter per kelvin",
                "notation": "J/(cm s K)",
                "aliases": [],
            },
            {
                "name": "watt_per_centimeter_per_kelvin",
                "symbol": "W/(cm K)",
                "si_factor": 1.0,
                "full_name": "watt per centimeter per kelvin",
                "notation": "W/(cm K)",
                "aliases": [],
            },
            {
                "name": "watt_per_meter_per_kelvin",
                "symbol": "W/(m K)",
                "si_factor": 0.01,
                "full_name": "watt per meter per kelvin",
                "notation": "W/(m K)",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "time": {
        # Time - TIME
        "dimension": TIME,
        "units": [
            {
                "name": "blink",
                "symbol": "blink",
                "si_factor": 0.864,
                "full_name": "blink",
                "notation": "blink",
                "aliases": [],
            },
            {
                "name": "century",
                "symbol": "-",
                "si_factor": 3155800000.0,
                "full_name": "century",
                "notation": "-",
                "aliases": [],
            },
            {
                "name": "chronon_or_tempon",
                "symbol": "-",
                "si_factor": 1e-23,
                "full_name": "chronon or tempon",
                "notation": "-",
                "aliases": [],
            },
            {
                "name": "gigan_or_eon",
                "symbol": "Ga or eon",
                "si_factor": 3.1558e+16,
                "full_name": "gigan or eon",
                "notation": "Ga or eon",
                "aliases": ['Ga', 'eon'],
            },
            {
                "name": "hour",
                "symbol": "h or hr",
                "si_factor": 3600.0,
                "full_name": "hour",
                "notation": "h or hr",
                "aliases": ['h', 'hr'],
            },
            {
                "name": "julian_year",
                "symbol": "a (jul) or yr",
                "si_factor": 31557000.0,
                "full_name": "Julian year",
                "notation": "a (jul) or yr",
                "aliases": ['a (jul)', 'yr'],
            },
            {
                "name": "mean_solar_day",
                "symbol": "da or d",
                "si_factor": 86400.0,
                "full_name": "mean solar day",
                "notation": "da or d",
                "aliases": ['da', 'd'],
            },
            {
                "name": "microsecond",
                "symbol": "μs",
                "si_factor": 1e-06,
                "full_name": "microsecond",
                "notation": "μs",
                "aliases": [],
            },
            {
                "name": "millenium",
                "symbol": "-",
                "si_factor": 31558000000.0,
                "full_name": "millenium",
                "notation": "-",
                "aliases": [],
            },
            {
                "name": "millisecond",
                "symbol": "ms",
                "si_factor": 0.001,
                "full_name": "millisecond",
                "notation": "ms",
                "aliases": [],
            },
            {
                "name": "minute",
                "symbol": "min",
                "si_factor": 60.0,
                "full_name": "minute",
                "notation": "min",
                "aliases": ['min'],
            },
            {
                "name": "nanosecond",
                "symbol": "ns",
                "si_factor": 1e-09,
                "full_name": "nanosecond",
                "notation": "ns",
                "aliases": [],
            },
            {
                "name": "picosecond",
                "symbol": "ps",
                "si_factor": 1e-12,
                "full_name": "picosecond",
                "notation": "ps",
                "aliases": [],
            },
            {
                "name": "second",
                "symbol": "s",
                "si_factor": 1.0,
                "full_name": "second",
                "notation": "s",
                "aliases": ['s'],
            },
            {
                "name": "shake",
                "symbol": "shake",
                "si_factor": 1e-08,
                "full_name": "shake",
                "notation": "shake",
                "aliases": [],
            },
            {
                "name": "sidereal_year_1900_ad",
                "symbol": "a (sider) or yr",
                "si_factor": 31551999.999999996,
                "full_name": "sidereal year (1900 AD)",
                "notation": "a (sider) or yr",
                "aliases": ['a (sider)', 'yr'],
            },
            {
                "name": "tropical_year",
                "symbol": "a (trop)",
                "si_factor": 31557000.0,
                "full_name": "tropical year",
                "notation": "a (trop)",
                "aliases": [],
            },
            {
                "name": "wink",
                "symbol": "wink",
                "si_factor": 3.33333e-12,
                "full_name": "wink",
                "notation": "wink",
                "aliases": ['wink'],
            },
            {
                "name": "year",
                "symbol": "a or y or yr",
                "si_factor": 31558000.0,
                "full_name": "year",
                "notation": "a or y or yr",
                "aliases": ['a', 'y', 'yr'],
            }
        ],
        "aliases": {}
    },

    "torque": {
        # Torque - LENGTH^2 MASS TIME^-2
        "dimension": TORQUE,
        "units": [
            {
                "name": "centimeter_kilogram_force",
                "symbol": "cm kg ${ }_{\\mathrm{f}}$",
                "si_factor": 0.098067,
                "full_name": "centimeter kilogram force",
                "notation": "cm kg ${ }_{\\mathrm{f}}$",
                "aliases": [],
            },
            {
                "name": "dyne_centimeter",
                "symbol": "dyn cm",
                "si_factor": 1e-07,
                "full_name": "dyne centimeter",
                "notation": "dyn cm",
                "aliases": [],
            },
            {
                "name": "foot_kilogram_force",
                "symbol": "$\\mathrm{ft} \\mathrm{kg}_{\\mathrm{f}}$",
                "si_factor": 2.9891,
                "full_name": "foot kilogram force",
                "notation": "$\\mathrm{ft} \\mathrm{kg}_{\\mathrm{f}}$",
                "aliases": [],
            },
            {
                "name": "foot_pound_force",
                "symbol": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}}$",
                "si_factor": 1.3558,
                "full_name": "foot pound force",
                "notation": "$\\mathrm{ft} \\mathrm{lb}_{\\mathrm{f}}$",
                "aliases": [],
            },
            {
                "name": "foot_poundal",
                "symbol": "ft pdl",
                "si_factor": 0.04214,
                "full_name": "foot poundal",
                "notation": "ft pdl",
                "aliases": [],
            },
            {
                "name": "in_pound_force",
                "symbol": "in $\\mathrm{lb}_{\\mathrm{f}}$",
                "si_factor": 0.11298,
                "full_name": "in pound force",
                "notation": "in $\\mathrm{lb}_{\\mathrm{f}}$",
                "aliases": [],
            },
            {
                "name": "inch_ounce_force",
                "symbol": "in $\\mathrm{OZ}_{\\mathrm{f}}$",
                "si_factor": 0.0070616,
                "full_name": "inch ounce force",
                "notation": "in $\\mathrm{OZ}_{\\mathrm{f}}$",
                "aliases": [],
            },
            {
                "name": "meter_kilogram_force",
                "symbol": "$\\mathrm{m} \\mathrm{kg}_{\\mathrm{f}}$",
                "si_factor": 9.8067,
                "full_name": "meter kilogram force",
                "notation": "$\\mathrm{m} \\mathrm{kg}_{\\mathrm{f}}$",
                "aliases": [],
            },
            {
                "name": "newton_centimeter",
                "symbol": "N cm",
                "si_factor": 0.01,
                "full_name": "newton centimeter",
                "notation": "N cm",
                "aliases": [],
            },
            {
                "name": "newton_meter",
                "symbol": "N m",
                "si_factor": 1.0,
                "full_name": "newton meter",
                "notation": "N m",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "turbulence_energy_dissipation_rate": {
        # Turbulence Energy Dissipation Rate - LENGTH^2 TIME^-3
        "dimension": TURBULENCE_ENERGY_DISSIPATION_RATE,
        "units": [
            {
                "name": "square_foot_per_cubic_second",
                "symbol": "$\\mathrm{ft}^{2} / \\mathrm{s}^{3}$ or sq ft/sec ${ }^{3}$",
                "si_factor": 0.0929,
                "full_name": "square foot per cubic second",
                "notation": "$\\mathrm{ft}^{2} / \\mathrm{s}^{3}$ or sq ft/sec ${ }^{3}$",
                "aliases": ['ft^{2 / s^{3', 'sq ft/sec { ^{3'],
            },
            {
                "name": "square_meter_per_cubic_second",
                "symbol": "$\\mathrm{m}^{2} / \\mathrm{s}^{3}$",
                "si_factor": 1.0,
                "full_name": "square meter per cubic second",
                "notation": "$\\mathrm{m}^{2} / \\mathrm{s}^{3}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "velocity_angular": {
        # Velocity, Angular - TIME^-1
        "dimension": VELOCITY_ANGULAR,
        "units": [
            {
                "name": "degree_per_minute",
                "symbol": "deg/min or ${ }^{\\circ} / \\mathrm{min}$",
                "si_factor": 0.000290888,
                "full_name": "degree per minute",
                "notation": "deg/min or ${ }^{\\circ} / \\mathrm{min}$",
                "aliases": ['deg/min', '{ ^{circ / min'],
            },
            {
                "name": "degree_per_second",
                "symbol": "deg/s or ${ }^{\\circ}$ /s",
                "si_factor": 0.0174533,
                "full_name": "degree per second",
                "notation": "deg/s or ${ }^{\\circ}$ /s",
                "aliases": ['deg/s', '{ ^{circ /s'],
            },
            {
                "name": "grade_per_minute",
                "symbol": "gon/min or grad/min",
                "si_factor": 0.000261799,
                "full_name": "grade per minute",
                "notation": "gon/min or grad/min",
                "aliases": ['gon/min', 'grad/min'],
            },
            {
                "name": "radian_per_minute",
                "symbol": "$\\mathrm{rad} / \\mathrm{min}$",
                "si_factor": 0.016667,
                "full_name": "radian per minute",
                "notation": "$\\mathrm{rad} / \\mathrm{min}$",
                "aliases": [],
            },
            {
                "name": "radian_per_second",
                "symbol": "$\\mathrm{rad} / \\mathrm{s}$",
                "si_factor": 1.0,
                "full_name": "radian per second",
                "notation": "$\\mathrm{rad} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "revolution_per_minute",
                "symbol": "rev/m or rpm",
                "si_factor": 0.010472,
                "full_name": "revolution per minute",
                "notation": "rev/m or rpm",
                "aliases": ['rev/m', 'rpm'],
            },
            {
                "name": "revolution_per_second",
                "symbol": "rev/s or rps",
                "si_factor": 6.283185,
                "full_name": "revolution per second",
                "notation": "rev/s or rps",
                "aliases": ['rev/s', 'rps'],
            },
            {
                "name": "turn_per_minute",
                "symbol": "tr/min",
                "si_factor": 0.010472,
                "full_name": "turn per minute",
                "notation": "tr/min",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "velocity_linear": {
        # Velocity, Linear - LENGTH TIME^-1
        "dimension": VELOCITY_LINEAR,
        "units": [
            {
                "name": "foot_per_hour",
                "symbol": "ft/h or ft/hr or fph",
                "si_factor": 8.4667e-05,
                "full_name": "foot per hour",
                "notation": "ft/h or ft/hr or fph",
                "aliases": ['ft/h', 'ft/hr', 'fph'],
            },
            {
                "name": "foot_per_minute",
                "symbol": "ft/min or fpm",
                "si_factor": 0.00508,
                "full_name": "foot per minute",
                "notation": "ft/min or fpm",
                "aliases": ['ft/min', 'fpm'],
            },
            {
                "name": "foot_per_second",
                "symbol": "ft/s or fps",
                "si_factor": 0.3048,
                "full_name": "foot per second",
                "notation": "ft/s or fps",
                "aliases": ['ft/s', 'fps'],
            },
            {
                "name": "inch_per_second",
                "symbol": "in/s or ips",
                "si_factor": 0.0254,
                "full_name": "inch per second",
                "notation": "in/s or ips",
                "aliases": ['in/s', 'ips'],
            },
            {
                "name": "international_knot",
                "symbol": "knot",
                "si_factor": 0.0514444,
                "full_name": "international knot",
                "notation": "knot",
                "aliases": ['knot'],
            },
            {
                "name": "kilometer_per_hour",
                "symbol": "km/h ot kph",
                "si_factor": 0.027778,
                "full_name": "kilometer per hour",
                "notation": "km/h ot kph",
                "aliases": [],
            },
            {
                "name": "kilometer_per_second",
                "symbol": "km/s",
                "si_factor": 1000.0,
                "full_name": "kilometer per second",
                "notation": "km/s",
                "aliases": [],
            },
            {
                "name": "meter_per_second",
                "symbol": "$\\mathrm{m} / \\mathrm{s}$",
                "si_factor": 1.0,
                "full_name": "meter per second",
                "notation": "$\\mathrm{m} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "mile_per_hour",
                "symbol": "$\\mathrm{mi} / \\mathrm{h}$ or $\\mathrm{mi} / \\mathrm{hr}$ or mph",
                "si_factor": 0.0444704,
                "full_name": "mile per hour",
                "notation": "$\\mathrm{mi} / \\mathrm{h}$ or $\\mathrm{mi} / \\mathrm{hr}$ or mph",
                "aliases": ['mi / h', 'mi / hr', 'mph'],
            }
        ],
        "aliases": {}
    },

    "viscosity_dynamic": {
        # Viscosity, Dynamic - LENGTH^-1 MASS TIME^-1
        "dimension": VISCOSITY_DYNAMIC,
        "units": [
            {
                "name": "centipoise",
                "symbol": "cP or cPo",
                "si_factor": 0.01,
                "full_name": "centipoise",
                "notation": "cP or cPo",
                "aliases": ['cP', 'cPo'],
            },
            {
                "name": "dyne_second_per_square_centimeter",
                "symbol": "dyn s/ $\\mathrm{cm}^{2}$",
                "si_factor": 1.0,
                "full_name": "dyne second per square centimeter",
                "notation": "dyn s/ $\\mathrm{cm}^{2}$",
                "aliases": [],
            },
            {
                "name": "kilopound_second_per_square_meter",
                "symbol": "kip $\\mathrm{s} / \\mathrm{m}^{2}$",
                "si_factor": 98.0665,
                "full_name": "kilopound second per square meter",
                "notation": "kip $\\mathrm{s} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "millipoise",
                "symbol": "mP or mPo",
                "si_factor": 0.001,
                "full_name": "millipoise",
                "notation": "mP or mPo",
                "aliases": ['mP', 'mPo'],
            },
            {
                "name": "newton_second_per_square_meter",
                "symbol": "$\\mathrm{N} \\mathrm{s} / \\mathrm{m}^{2}$",
                "si_factor": 10.0,
                "full_name": "newton second per square meter",
                "notation": "$\\mathrm{N} \\mathrm{s} / \\mathrm{m}^{2}$",
                "aliases": [],
            },
            {
                "name": "pascal_second",
                "symbol": "Pa s or PI",
                "si_factor": 10.0,
                "full_name": "pascal second",
                "notation": "Pa s or PI",
                "aliases": ['Pa s', 'PI'],
            },
            {
                "name": "poise",
                "symbol": "P or Po",
                "si_factor": 1.0,
                "full_name": "poise",
                "notation": "P or Po",
                "aliases": ['P', 'Po'],
            },
            {
                "name": "pound_force_hour_per_square_foot",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}} \\mathrm{h} / \\mathrm{ft}^{2}$ or $\\mathrm{lb} \\mathrm{hr} / \\mathrm{sq}$ ft",
                "si_factor": 1723690.0,
                "full_name": "pound force hour per square foot",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}} \\mathrm{h} / \\mathrm{ft}^{2}$ or $\\mathrm{lb} \\mathrm{hr} / \\mathrm{sq}$ ft",
                "aliases": ['lb_{f h / ft^{2', 'lb hr / sq ft'],
            },
            {
                "name": "pound_force_second_per_square_foot",
                "symbol": "$\\mathrm{lb}_{\\mathrm{f}} \\mathrm{s} / \\mathrm{ft}^{2}$ or $\\mathrm{lb} \\mathrm{sec} / \\mathrm{sq}$ ft",
                "si_factor": 478.803,
                "full_name": "pound force second per square foot",
                "notation": "$\\mathrm{lb}_{\\mathrm{f}} \\mathrm{s} / \\mathrm{ft}^{2}$ or $\\mathrm{lb} \\mathrm{sec} / \\mathrm{sq}$ ft",
                "aliases": ['lb_{f s / ft^{2', 'lb sec / sq ft'],
            }
        ],
        "aliases": {}
    },

    "viscosity_kinematic": {
        # Viscosity, Kinematic - LENGTH^2 TIME^-1
        "dimension": VISCOSITY_KINEMATIC,
        "units": [
            {
                "name": "centistokes",
                "symbol": "cSt",
                "si_factor": 1e-06,
                "full_name": "centistokes",
                "notation": "cSt",
                "aliases": ['cSt'],
            },
            {
                "name": "millistokes",
                "symbol": "mSt",
                "si_factor": 1e-07,
                "full_name": "millistokes",
                "notation": "mSt",
                "aliases": ['mSt'],
            },
            {
                "name": "square_centimeter_per_second",
                "symbol": "$\\mathrm{cm}^{2} / \\mathrm{s}$",
                "si_factor": 0.0001,
                "full_name": "square centimeter per second",
                "notation": "$\\mathrm{cm}^{2} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "square_foot_per_hour",
                "symbol": "$\\mathrm{ft}^{2} / \\mathrm{h}$ or $\\mathrm{ft}^{2} / \\mathrm{hr}$",
                "si_factor": 2.58064e-05,
                "full_name": "square foot per hour",
                "notation": "$\\mathrm{ft}^{2} / \\mathrm{h}$ or $\\mathrm{ft}^{2} / \\mathrm{hr}$",
                "aliases": ['ft^{2 / h', 'ft^{2 / hr'],
            },
            {
                "name": "square_foot_per_second",
                "symbol": "$\\mathrm{ft}^{2} / \\mathrm{s}$",
                "si_factor": 0.092903,
                "full_name": "square foot per second",
                "notation": "$\\mathrm{ft}^{2} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "square_meters_per_second",
                "symbol": "$\\mathrm{m}^{2} / \\mathrm{s}$",
                "si_factor": 1.0,
                "full_name": "square meters per second",
                "notation": "$\\mathrm{m}^{2} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "stokes",
                "symbol": "St",
                "si_factor": 0.0001,
                "full_name": "stokes",
                "notation": "St",
                "aliases": ['St'],
            }
        ],
        "aliases": {}
    },

    "volume": {
        # Volume - LENGTH^3
        "dimension": VOLUME,
        "units": [
            {
                "name": "acre_foot",
                "symbol": "ac-ft",
                "si_factor": 1233.48,
                "full_name": "acre foot",
                "notation": "ac-ft",
                "aliases": [],
            },
            {
                "name": "acre_inch",
                "symbol": "ac-in",
                "si_factor": 102.79,
                "full_name": "acre inch",
                "notation": "ac-in",
                "aliases": [],
            },
            {
                "name": "barrel_us_liquid",
                "symbol": "bbl (US liq)",
                "si_factor": 0.1192405,
                "full_name": "barrel (US Liquid)",
                "notation": "bbl (US liq)",
                "aliases": [],
            },
            {
                "name": "barrel_us_petro",
                "symbol": "bbl",
                "si_factor": 0.158987,
                "full_name": "barrel (US, Petro)",
                "notation": "bbl",
                "aliases": ['bbl'],
            },
            {
                "name": "board_foot_measure",
                "symbol": "BM or fbm",
                "si_factor": 0.00235974,
                "full_name": "board foot measure",
                "notation": "BM or fbm",
                "aliases": ['BM', 'fbm'],
            },
            {
                "name": "bushel_us_dry",
                "symbol": "bu (US dry)",
                "si_factor": 0.0352391,
                "full_name": "bushel (US Dry)",
                "notation": "bu (US dry)",
                "aliases": [],
            },
            {
                "name": "centiliter",
                "symbol": "cl or cL",
                "si_factor": 1e-05,
                "full_name": "centiliter",
                "notation": "cl or cL",
                "aliases": ['cl', 'cL'],
            },
            {
                "name": "cord",
                "symbol": "cord or cd",
                "si_factor": 3.62456,
                "full_name": "cord",
                "notation": "cord or cd",
                "aliases": ['cd'],
            },
            {
                "name": "cord_foot",
                "symbol": "cord-ft",
                "si_factor": 0.4530695,
                "full_name": "cord foot",
                "notation": "cord-ft",
                "aliases": [],
            },
            {
                "name": "cubic_centimeter",
                "symbol": "$\\mathrm{cm}^{3}$ or cc",
                "si_factor": 1e-06,
                "full_name": "cubic centimeter",
                "notation": "$\\mathrm{cm}^{3}$ or cc",
                "aliases": ['cm^{3', 'cc'],
            },
            {
                "name": "cubic_decameter",
                "symbol": "dam ${ }^{3}$",
                "si_factor": 1000.0,
                "full_name": "cubic decameter",
                "notation": "dam ${ }^{3}$",
                "aliases": [],
            },
            {
                "name": "cubic_decimeter",
                "symbol": "$\\mathrm{dm}^{3}$",
                "si_factor": 0.001,
                "full_name": "cubic decimeter",
                "notation": "$\\mathrm{dm}^{3}$",
                "aliases": [],
            },
            {
                "name": "cubic_foot",
                "symbol": "cu ft or ft ${ }^{3}$",
                "si_factor": 0.0283168,
                "full_name": "cubic foot",
                "notation": "cu ft or ft ${ }^{3}$",
                "aliases": ['cu ft', 'ft { ^{3'],
            },
            {
                "name": "cubic_inch",
                "symbol": "cu in or $\\mathrm{in}^{3}$",
                "si_factor": 1.63871e-05,
                "full_name": "cubic inch",
                "notation": "cu in or $\\mathrm{in}^{3}$",
                "aliases": ['cu in', 'in^{3'],
            },
            {
                "name": "cubic_kilometer",
                "symbol": "$\\mathrm{km}^{3}$",
                "si_factor": 1000000000.0,
                "full_name": "cubic kilometer",
                "notation": "$\\mathrm{km}^{3}$",
                "aliases": [],
            },
            {
                "name": "cubic_meter",
                "symbol": "$\\mathrm{m}^{3}$",
                "si_factor": 1.0,
                "full_name": "cubic meter",
                "notation": "$\\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "cubic_micrometer",
                "symbol": "$\\mu \\mathrm{m}^{3}$",
                "si_factor": 1e-18,
                "full_name": "cubic micrometer",
                "notation": "$\\mu \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "cubic_mile_us_intl",
                "symbol": "cu mi",
                "si_factor": 4168180000.0000005,
                "full_name": "cubic mile (US, Intl)",
                "notation": "cu mi",
                "aliases": [],
            },
            {
                "name": "cubic_millimeter",
                "symbol": "$\\mathrm{mm}^{3}$",
                "si_factor": 1e-09,
                "full_name": "cubic millimeter",
                "notation": "$\\mathrm{mm}^{3}$",
                "aliases": [],
            },
            {
                "name": "cubic_yard",
                "symbol": "cu yd or $\\mathrm{yd}^{3}$",
                "si_factor": 0.7645549,
                "full_name": "cubic yard",
                "notation": "cu yd or $\\mathrm{yd}^{3}$",
                "aliases": ['cu yd', 'yd^{3'],
            },
            {
                "name": "decastére",
                "symbol": "dast",
                "si_factor": 10.0,
                "full_name": "decastére",
                "notation": "dast",
                "aliases": ['dast'],
            },
            {
                "name": "deciliter",
                "symbol": "dl or dL",
                "si_factor": 0.0001,
                "full_name": "deciliter",
                "notation": "dl or dL",
                "aliases": ['dl', 'dL'],
            },
            {
                "name": "fluid_drachm_uk",
                "symbol": "fl dr (UK)",
                "si_factor": 3.5516299999999996e-06,
                "full_name": "fluid drachm (UK)",
                "notation": "fl dr (UK)",
                "aliases": [],
            },
            {
                "name": "fluid_dram_us",
                "symbol": "fl dr (US liq)",
                "si_factor": 3.69669e-06,
                "full_name": "fluid dram (US)",
                "notation": "fl dr (US liq)",
                "aliases": [],
            },
            {
                "name": "fluid_ounce_us",
                "symbol": "fl oz",
                "si_factor": 2.95735e-05,
                "full_name": "fluid ounce (US)",
                "notation": "fl oz",
                "aliases": [],
            },
            {
                "name": "gallon_imperial_uk",
                "symbol": "gal (UK) or Imp gal",
                "si_factor": 0.00454609,
                "full_name": "gallon (Imperial UK)",
                "notation": "gal (UK) or Imp gal",
                "aliases": ['gal (UK)', 'Imp gal'],
            },
            {
                "name": "gallon_us_dry",
                "symbol": "gal (US dry)",
                "si_factor": 0.004404884,
                "full_name": "gallon (US Dry)",
                "notation": "gal (US dry)",
                "aliases": [],
            },
            {
                "name": "gallon_us_liquid",
                "symbol": "gal",
                "si_factor": 0.003785412,
                "full_name": "gallon (US Liquid)",
                "notation": "gal",
                "aliases": ['gal'],
            },
            {
                "name": "last",
                "symbol": "last",
                "si_factor": 2.9095,
                "full_name": "last",
                "notation": "last",
                "aliases": ['last'],
            },
            {
                "name": "liter",
                "symbol": "1 or L",
                "si_factor": 0.001,
                "full_name": "liter",
                "notation": "1 or L",
                "aliases": ['1', 'L'],
            },
            {
                "name": "microliter",
                "symbol": "$\\mu \\mathrm{l}$ or $\\mu \\mathrm{L}$",
                "si_factor": 1e-09,
                "full_name": "microliter",
                "notation": "$\\mu \\mathrm{l}$ or $\\mu \\mathrm{L}$",
                "aliases": ['mu l', 'mu L'],
            },
            {
                "name": "milliliter",
                "symbol": "ml",
                "si_factor": 1e-06,
                "full_name": "milliliter",
                "notation": "ml",
                "aliases": ['ml'],
            },
            {
                "name": "mohr_centicube",
                "symbol": "cc",
                "si_factor": 1.00238e-06,
                "full_name": "Mohr centicube",
                "notation": "cc",
                "aliases": ['cc'],
            },
            {
                "name": "pint_uk",
                "symbol": "pt (UK)",
                "si_factor": 0.000568262,
                "full_name": "pint (UK)",
                "notation": "pt (UK)",
                "aliases": [],
            },
            {
                "name": "pint_us_dry",
                "symbol": "pt (US dry)",
                "si_factor": 0.000550611,
                "full_name": "pint (US Dry)",
                "notation": "pt (US dry)",
                "aliases": [],
            },
            {
                "name": "pint_us_liquid",
                "symbol": "pt",
                "si_factor": 0.000473176,
                "full_name": "pint (US Liquid)",
                "notation": "pt",
                "aliases": ['pt'],
            },
            {
                "name": "quart_us_dry",
                "symbol": "qt (US dry)",
                "si_factor": 0.00110122,
                "full_name": "quart (US Dry)",
                "notation": "qt (US dry)",
                "aliases": [],
            },
            {
                "name": "stére",
                "symbol": "st",
                "si_factor": 1.0,
                "full_name": "stére",
                "notation": "st",
                "aliases": ['st'],
            },
            {
                "name": "tablespoon_metric",
                "symbol": "tbsp (Metric)",
                "si_factor": 1.5000000000000002e-05,
                "full_name": "tablespoon (Metric)",
                "notation": "tbsp (Metric)",
                "aliases": [],
            },
            {
                "name": "tablespoon_us",
                "symbol": "tbsp",
                "si_factor": 1.47868e-05,
                "full_name": "tablespoon (US)",
                "notation": "tbsp",
                "aliases": ['tbsp'],
            },
            {
                "name": "teaspoon_us",
                "symbol": "tsp",
                "si_factor": 4.928919999999999e-06,
                "full_name": "teaspoon (US)",
                "notation": "tsp",
                "aliases": ['tsp'],
            }
        ],
        "aliases": {}
    },

    "volume_fraction_of_i": {
        # Volume Fraction of "i" - Dimensionless
        "dimension": DIMENSIONLESS,
        "units": [
            {
                "name": "cubic_centimeters_of_i_per_cubic_meter_total",
                "symbol": "$\\mathrm{cm}_{\\mathrm{i}}^{3} / \\mathrm{m}^{3}$ or $\\mathrm{cc}_{\\mathrm{i}} / \\mathrm{m}^{3}$",
                "si_factor": 0.0001,
                "full_name": "cubic centimeters of \"i\" per cubic meter total",
                "notation": "$\\mathrm{cm}_{\\mathrm{i}}^{3} / \\mathrm{m}^{3}$ or $\\mathrm{cc}_{\\mathrm{i}} / \\mathrm{m}^{3}$",
                "aliases": ['cm_{i^{3 / m^{3', 'cc_{i / m^{3'],
            },
            {
                "name": "cubic_foot_of_i_per_cubic_foot_total",
                "symbol": "$\\mathrm{ft}_{\\mathrm{i}}^{3} / \\mathrm{ft}^{3}$ or $\\mathrm{cft}_{\\mathrm{i}} / \\mathrm{cft}$",
                "si_factor": 1.0,
                "full_name": "cubic foot of \"i\" per cubic foot total",
                "notation": "$\\mathrm{ft}_{\\mathrm{i}}^{3} / \\mathrm{ft}^{3}$ or $\\mathrm{cft}_{\\mathrm{i}} / \\mathrm{cft}$",
                "aliases": ['ft_{i^{3 / ft^{3', 'cft_{i / cft'],
            },
            {
                "name": "cubic_meters_of_i_per_cubic_meter_total",
                "symbol": "$\\mathrm{m}_{\\mathrm{i}}{ }^{3} / \\mathrm{m}^{3}$",
                "si_factor": 1.0,
                "full_name": "cubic meters of \" i \" per cubic meter total",
                "notation": "$\\mathrm{m}_{\\mathrm{i}}{ }^{3} / \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "gallons_of_i_per_gallon_total",
                "symbol": "$\\mathrm{gal}_{\\mathrm{i}} / \\mathrm{gal}$",
                "si_factor": 1.0,
                "full_name": "gallons of \"i\" per gallon total",
                "notation": "$\\mathrm{gal}_{\\mathrm{i}} / \\mathrm{gal}$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "volumetric_calorific_heating_value": {
        # Volumetric Calorific (Heating) Value - LENGTH^-1 MASS TIME^-2
        "dimension": VOLUMETRIC_CALORIFIC_HEATING_VALUE,
        "units": [
            {
                "name": "british_thermal_unit_per_cubic_foot",
                "symbol": "$\\mathrm{Btu} / \\mathrm{ft}^{3}$ or Btu/cft",
                "si_factor": 37260.0,
                "full_name": "British thermal unit per cubic foot",
                "notation": "$\\mathrm{Btu} / \\mathrm{ft}^{3}$ or Btu/cft",
                "aliases": ['Btu / ft^{3', 'Btu/cft'],
            },
            {
                "name": "british_thermal_unit_per_gallon_uk",
                "symbol": "Btu/gal (UK)",
                "si_factor": 232090.0,
                "full_name": "British thermal unit per gallon (UK)",
                "notation": "Btu/gal (UK)",
                "aliases": [],
            },
            {
                "name": "british_thermal_unit_per_gallon_us",
                "symbol": "Btu/gal (US)",
                "si_factor": 193260.0,
                "full_name": "British thermal unit per gallon (US)",
                "notation": "Btu/gal (US)",
                "aliases": [],
            },
            {
                "name": "calorie_per_cubic_centimeter",
                "symbol": "$\\mathrm{cal} / \\mathrm{cm}^{3}$ or $\\mathrm{cal} / \\mathrm{cc}$",
                "si_factor": 4186800.0,
                "full_name": "calorie per cubic centimeter",
                "notation": "$\\mathrm{cal} / \\mathrm{cm}^{3}$ or $\\mathrm{cal} / \\mathrm{cc}$",
                "aliases": ['cal / cm^{3', 'cal / cc'],
            },
            {
                "name": "chu_per_cubic_foot",
                "symbol": "$\\mathrm{Chu} / \\mathrm{ft}^{3}$ or $\\mathrm{Chu} / \\mathrm{cft}$",
                "si_factor": 67067.0,
                "full_name": "Chu per cubic foot",
                "notation": "$\\mathrm{Chu} / \\mathrm{ft}^{3}$ or $\\mathrm{Chu} / \\mathrm{cft}$",
                "aliases": ['Chu / ft^{3', 'Chu / cft'],
            },
            {
                "name": "joule_per_cubic_meter",
                "symbol": "$\\mathrm{J} / \\mathrm{m}^{3}$",
                "si_factor": 1.0,
                "full_name": "joule per cubic meter",
                "notation": "$\\mathrm{J} / \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "kilocalorie_per_cubic_foot",
                "symbol": "$\\mathrm{kcal} / \\mathrm{ft}^{3}$ or $\\mathrm{kcal} / \\mathrm{cft}$",
                "si_factor": 147860.0,
                "full_name": "kilocalorie per cubic foot",
                "notation": "$\\mathrm{kcal} / \\mathrm{ft}^{3}$ or $\\mathrm{kcal} / \\mathrm{cft}$",
                "aliases": ['kcal / ft^{3', 'kcal / cft'],
            },
            {
                "name": "kilocalorie_per_cubic_meter",
                "symbol": "$\\mathrm{kcal} / \\mathrm{m}^{3}$",
                "si_factor": 4186.8,
                "full_name": "kilocalorie per cubic meter",
                "notation": "$\\mathrm{kcal} / \\mathrm{m}^{3}$",
                "aliases": [],
            },
            {
                "name": "therm_100_k_btu",
                "symbol": "thm/cft",
                "si_factor": 3726000000.0,
                "full_name": "therm ( 100 K Btu ) per cubic foot",
                "notation": "thm/cft",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "volumetric_coefficient_of_expansion": {
        # Volumetric Coefficient of Expansion - LENGTH^-3 MASS TEMP^-1
        "dimension": VOLUMETRIC_COEFFICIENT_OF_EXPANSION,
        "units": [
            {
                "name": "gram_per_cubic_centimeter_per_kelvin_or_degree_celsius",
                "symbol": "$\\mathrm{g} / \\mathrm{cm}^{3} / \\mathrm{K}$ or g/cc/ ${ }^{\\circ} \\mathrm{C}$",
                "si_factor": 1000.0,
                "full_name": "gram per cubic centimeter per kelvin (or degree Celsius)",
                "notation": "$\\mathrm{g} / \\mathrm{cm}^{3} / \\mathrm{K}$ or g/cc/ ${ }^{\\circ} \\mathrm{C}$",
                "aliases": ['g / cm^{3 / K', 'g/cc/ { ^{circ C'],
            },
            {
                "name": "kilogram_per_cubic_meter_per_kelvin_or_degree_celsius",
                "symbol": "$\\mathrm{kg} / \\mathrm{m}^{3} / \\mathrm{K}$ or $\\mathrm{kg} / \\mathrm{m}^{3} /{ }^{\\circ}$ C",
                "si_factor": 1.0,
                "full_name": "kilogram per cubic meter per kelvin (or degree Celsius)",
                "notation": "$\\mathrm{kg} / \\mathrm{m}^{3} / \\mathrm{K}$ or $\\mathrm{kg} / \\mathrm{m}^{3} /{ }^{\\circ}$ C",
                "aliases": ['kg / m^{3 / K', 'kg / m^{3 /{ ^{circ C'],
            },
            {
                "name": "pound_per_cubic_foot_per_degree_fahrenheit_or_degree_rankine",
                "symbol": "$\\mathrm{lb} / \\mathrm{ft}^{3} /{ }^{\\circ} \\mathrm{R}$ or $\\mathrm{lb} / \\mathrm{cft} /{ }^{\\circ} \\mathrm{F}$",
                "si_factor": 28.833,
                "full_name": "pound per cubic foot per degree Fahrenheit (or degree Rankine)",
                "notation": "$\\mathrm{lb} / \\mathrm{ft}^{3} /{ }^{\\circ} \\mathrm{R}$ or $\\mathrm{lb} / \\mathrm{cft} /{ }^{\\circ} \\mathrm{F}$",
                "aliases": ['lb / ft^{3 /{ ^{circ R', 'lb / cft /{ ^{circ F'],
            },
            {
                "name": "pound_per_cubic_foot_per_kelvin_or_degree_celsius",
                "symbol": "$\\mathrm{lb} / \\mathrm{ft}^{3} / \\mathrm{K}$ or $\\mathrm{lb} / \\mathrm{cft} /{ }^{\\circ} \\mathrm{C}$",
                "si_factor": 16.018,
                "full_name": "pound per cubic foot per kelvin (or degree Celsius)",
                "notation": "$\\mathrm{lb} / \\mathrm{ft}^{3} / \\mathrm{K}$ or $\\mathrm{lb} / \\mathrm{cft} /{ }^{\\circ} \\mathrm{C}$",
                "aliases": ['lb / ft^{3 / K', 'lb / cft /{ ^{circ C'],
            }
        ],
        "aliases": {}
    },

    "volumetric_flow_rate": {
        # Volumetric Flow Rate - LENGTH^3 TIME^-1
        "dimension": VOLUMETRIC_FLOW_RATE,
        "units": [
            {
                "name": "cubic_feet_per_day",
                "symbol": "$\\mathrm{ft}^{3} / \\mathrm{d}$ or $\\mathrm{cft} / \\mathrm{da}$ or cfd",
                "si_factor": 3.2778e-07,
                "full_name": "cubic feet per day",
                "notation": "$\\mathrm{ft}^{3} / \\mathrm{d}$ or $\\mathrm{cft} / \\mathrm{da}$ or cfd",
                "aliases": ['ft^{3 / d', 'cft / da', 'cfd'],
            },
            {
                "name": "cubic_feet_per_hour",
                "symbol": "$\\mathrm{ft}^{3} / \\mathrm{h}$ or $\\mathrm{cft} / \\mathrm{hr}$ or cfh",
                "si_factor": 7.866699999999999e-06,
                "full_name": "cubic feet per hour",
                "notation": "$\\mathrm{ft}^{3} / \\mathrm{h}$ or $\\mathrm{cft} / \\mathrm{hr}$ or cfh",
                "aliases": ['ft^{3 / h', 'cft / hr', 'cfh'],
            },
            {
                "name": "cubic_feet_per_minute",
                "symbol": "$\\mathrm{ft}^{3} / \\mathrm{min}$ or $\\mathrm{cft} / \\mathrm{min}$ or cfm",
                "si_factor": 0.000472,
                "full_name": "cubic feet per minute",
                "notation": "$\\mathrm{ft}^{3} / \\mathrm{min}$ or $\\mathrm{cft} / \\mathrm{min}$ or cfm",
                "aliases": ['ft^{3 / min', 'cft / min', 'cfm'],
            },
            {
                "name": "cubic_feet_per_second",
                "symbol": "$\\mathrm{ft}^{3} / \\mathrm{s}$ or cft/sec or cfs",
                "si_factor": 0.02832,
                "full_name": "cubic feet per second",
                "notation": "$\\mathrm{ft}^{3} / \\mathrm{s}$ or cft/sec or cfs",
                "aliases": ['ft^{3 / s', 'cft/sec', 'cfs'],
            },
            {
                "name": "cubic_meters_per_day",
                "symbol": "$\\mathrm{m}^{3} / \\mathrm{d}$",
                "si_factor": 1.1574000000000001e-05,
                "full_name": "cubic meters per day",
                "notation": "$\\mathrm{m}^{3} / \\mathrm{d}$",
                "aliases": [],
            },
            {
                "name": "cubic_meters_per_hour",
                "symbol": "$\\mathrm{m}^{3} / \\mathrm{h}$",
                "si_factor": 0.00027778,
                "full_name": "cubic meters per hour",
                "notation": "$\\mathrm{m}^{3} / \\mathrm{h}$",
                "aliases": [],
            },
            {
                "name": "cubic_meters_per_minute",
                "symbol": "$\\mathrm{m}^{3} / \\min$",
                "si_factor": 0.016667,
                "full_name": "cubic meters per minute",
                "notation": "$\\mathrm{m}^{3} / \\min$",
                "aliases": [],
            },
            {
                "name": "cubic_meters_per_second",
                "symbol": "$\\mathrm{m}^{3} / \\mathrm{s}$",
                "si_factor": 1.0,
                "full_name": "cubic meters per second",
                "notation": "$\\mathrm{m}^{3} / \\mathrm{s}$",
                "aliases": [],
            },
            {
                "name": "gallons_per_day",
                "symbol": "gal/d or gpd or gal/ da",
                "si_factor": 0.002628,
                "full_name": "gallons per day",
                "notation": "gal/d or gpd or gal/ da",
                "aliases": ['gal/d', 'gpd', 'gal/ da'],
            },
            {
                "name": "gallons_per_hour",
                "symbol": "gal/h or gph or gal/ hr",
                "si_factor": 0.06308,
                "full_name": "gallons per hour",
                "notation": "gal/h or gph or gal/ hr",
                "aliases": ['gal/h', 'gph', 'gal/ hr'],
            },
            {
                "name": "gallons_per_minute",
                "symbol": "gal/min or gpm",
                "si_factor": 3.785,
                "full_name": "gallons per minute",
                "notation": "gal/min or gpm",
                "aliases": ['gal/min', 'gpm'],
            },
            {
                "name": "gallons_per_second",
                "symbol": "gal/s or gps or gal/ sec",
                "si_factor": 227.1,
                "full_name": "gallons per second",
                "notation": "gal/s or gps or gal/ sec",
                "aliases": ['gal/s', 'gps', 'gal/ sec'],
            },
            {
                "name": "liters_per_day",
                "symbol": "1/d",
                "si_factor": 0.00069444,
                "full_name": "liters per day",
                "notation": "1/d",
                "aliases": [],
            },
            {
                "name": "liters_per_hour",
                "symbol": "1/h",
                "si_factor": 0.016667,
                "full_name": "liters per hour",
                "notation": "1/h",
                "aliases": [],
            },
            {
                "name": "liters_per_minute",
                "symbol": "$1 / \\mathrm{min}$",
                "si_factor": 1.0,
                "full_name": "liters per minute",
                "notation": "$1 / \\mathrm{min}$",
                "aliases": [],
            },
            {
                "name": "liters_per_second",
                "symbol": "1/s",
                "si_factor": 60.0,
                "full_name": "liters per second",
                "notation": "1/s",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "volumetric_flux": {
        # Volumetric Flux - LENGTH TIME^-1
        "dimension": VOLUMETRIC_FLUX,
        "units": [
            {
                "name": "cubic_feet_per_square_foot_per_day",
                "symbol": "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or $\\mathrm{cft} / \\mathrm{sqft} /$ da",
                "si_factor": 3.5276e-06,
                "full_name": "cubic feet per square foot per day",
                "notation": "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or $\\mathrm{cft} / \\mathrm{sqft} /$ da",
                "aliases": ['ft^{3 /left(ft^{2 ~dright)', 'cft / sqft / da'],
            },
            {
                "name": "cubic_feet_per_square_foot_per_hour",
                "symbol": "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or $\\mathrm{cft} / \\mathrm{sqft} /$ hr",
                "si_factor": 8.466300000000001e-05,
                "full_name": "cubic feet per square foot per hour",
                "notation": "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or $\\mathrm{cft} / \\mathrm{sqft} /$ hr",
                "aliases": ['ft^{3 /left(ft^{2 ~hright)', 'cft / sqft / hr'],
            },
            {
                "name": "cubic_feet_per_square_foot_per_minute",
                "symbol": "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\min \\right)$ or $\\mathrm{cft} /$ sqft/min",
                "si_factor": 0.0050798,
                "full_name": "cubic feet per square foot per minute",
                "notation": "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\min \\right)$ or $\\mathrm{cft} /$ sqft/min",
                "aliases": ['ft^{3 /left(ft^{2 min right)', 'cft / sqft/min'],
            },
            {
                "name": "cubic_feet_per_square_foot_per_second",
                "symbol": "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or cft/sqft/ sec",
                "si_factor": 0.30479,
                "full_name": "cubic feet per square foot per second",
                "notation": "$\\mathrm{ft}^{3} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or cft/sqft/ sec",
                "aliases": ['ft^{3 /left(ft^{2 ~sright)', 'cft/sqft/ sec'],
            },
            {
                "name": "cubic_meters_per_square_meter_per_day",
                "symbol": "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$",
                "si_factor": 1.1574000000000001e-05,
                "full_name": "cubic meters per square meter per day",
                "notation": "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$",
                "aliases": [],
            },
            {
                "name": "cubic_meters_per_square_meter_per_hour",
                "symbol": "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$",
                "si_factor": 0.00027778,
                "full_name": "cubic meters per square meter per hour",
                "notation": "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$",
                "aliases": [],
            },
            {
                "name": "cubic_meters_per_square_meter_per_minute",
                "symbol": "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~min}\\right)$",
                "si_factor": 0.016667,
                "full_name": "cubic meters per square meter per minute",
                "notation": "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~min}\\right)$",
                "aliases": [],
            },
            {
                "name": "cubic_meters_per_square_meter_per_second",
                "symbol": "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$",
                "si_factor": 1.0,
                "full_name": "cubic meters per square meter per second",
                "notation": "$\\mathrm{m}^{3} /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$",
                "aliases": [],
            },
            {
                "name": "gallons_per_square_foot_per_day",
                "symbol": "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or gal/ sqft/da",
                "si_factor": 0.00047138000000000003,
                "full_name": "gallons per square foot per day",
                "notation": "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~d}\\right)$ or gal/ sqft/da",
                "aliases": ['gal /left(ft^{2 ~dright)', 'gal/ sqft/da'],
            },
            {
                "name": "gallons_per_square_foot_per_hour",
                "symbol": "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or gal/ sqft/hr",
                "si_factor": 0.011313,
                "full_name": "gallons per square foot per hour",
                "notation": "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~h}\\right)$ or gal/ sqft/hr",
                "aliases": ['gal /left(ft^{2 ~hright)', 'gal/ sqft/hr'],
            },
            {
                "name": "gallons_per_square_foot_per_minute",
                "symbol": "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~min}\\right)$ or gal/ sqft/min or gpm/sqft",
                "si_factor": 0.67878,
                "full_name": "gallons per square foot per minute",
                "notation": "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~min}\\right)$ or gal/ sqft/min or gpm/sqft",
                "aliases": ['gal /left(ft^{2 ~minright)', 'gal/ sqft/min', 'gpm/sqft'],
            },
            {
                "name": "gallons_per_square_foot_per_second",
                "symbol": "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or gal/ $\\mathrm{sqft} / \\mathrm{sec}$",
                "si_factor": 40.727,
                "full_name": "gallons per square foot per second",
                "notation": "$\\mathrm{gal} /\\left(\\mathrm{ft}^{2} \\mathrm{~s}\\right)$ or gal/ $\\mathrm{sqft} / \\mathrm{sec}$",
                "aliases": ['gal /left(ft^{2 ~sright)', 'gal/ sqft / sec'],
            },
            {
                "name": "liters_per_square_meter_per_day",
                "symbol": "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$",
                "si_factor": 1.1574000000000001e-05,
                "full_name": "liters per square meter per day",
                "notation": "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~d}\\right)$",
                "aliases": [],
            },
            {
                "name": "liters_per_square_meter_per_hour",
                "symbol": "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$",
                "si_factor": 0.00027778,
                "full_name": "liters per square meter per hour",
                "notation": "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~h}\\right)$",
                "aliases": [],
            },
            {
                "name": "liters_per_square_meter_per_minute",
                "symbol": "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~min}\\right)$",
                "si_factor": 0.016667,
                "full_name": "liters per square meter per minute",
                "notation": "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~min}\\right)$",
                "aliases": [],
            },
            {
                "name": "liters_per_square_meter_per_second",
                "symbol": "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$",
                "si_factor": 1.0,
                "full_name": "liters per square meter per second",
                "notation": "$1 /\\left(\\mathrm{m}^{2} \\mathrm{~s}\\right)$",
                "aliases": [],
            }
        ],
        "aliases": {}
    },

    "volumetric_mass_flow_rate": {
        # Volumetric Mass Flow Rate - LENGTH^-3 MASS TIME^-1
        "dimension": VOLUMETRIC_MASS_FLOW_RATE,
        "units": [
            {
                "name": "gram_per_second_per_cubic_centimeter",
                "symbol": "$\\mathrm{g} /\\left(\\mathrm{s} \\mathrm{cm}^{3}\\right)$ or g/s/cc or $\\mathrm{g} / \\mathrm{cc} / \\mathrm{sec}$",
                "si_factor": 1000.0,
                "full_name": "gram per second per cubic centimeter",
                "notation": "$\\mathrm{g} /\\left(\\mathrm{s} \\mathrm{cm}^{3}\\right)$ or g/s/cc or $\\mathrm{g} / \\mathrm{cc} / \\mathrm{sec}$",
                "aliases": ['g /left(s cm^{3right)', 'g/s/cc', 'g / cc / sec'],
            },
            {
                "name": "kilogram_per_hour_per_cubic_foot",
                "symbol": "kg/(h ft ${ }^{3}$ ) or kg/hr/ cft",
                "si_factor": 0.0098096,
                "full_name": "kilogram per hour per cubic foot",
                "notation": "kg/(h ft ${ }^{3}$ ) or kg/hr/ cft",
                "aliases": ['kg/(h ft { ^{3 )', 'kg/hr/ cft'],
            },
            {
                "name": "kilogram_per_hour_per_cubic_meter",
                "symbol": "kg/(h m3) or kg/hr/ cu.m",
                "si_factor": 0.00027778000000000004,
                "full_name": "kilogram per hour per cubic meter",
                "notation": "kg/(h m3) or kg/hr/ cu.m",
                "aliases": ['kg/(h m3)', 'kg/hr/ cu.m'],
            },
            {
                "name": "kilogram_per_second_per_cubic_meter",
                "symbol": "$\\mathrm{kg} /\\left(\\mathrm{s} \\mathrm{m}^{3}\\right)$ or kg/sec/ cu.m",
                "si_factor": 1.0,
                "full_name": "kilogram per second per cubic meter",
                "notation": "$\\mathrm{kg} /\\left(\\mathrm{s} \\mathrm{m}^{3}\\right)$ or kg/sec/ cu.m",
                "aliases": ['kg /left(s m^{3right)', 'kg/sec/ cu.m'],
            },
            {
                "name": "pound_per_hour_per_cubic_foot",
                "symbol": "$\\mathrm{lb} /\\left(\\mathrm{h} \\mathrm{ft}^{3}\\right)$ or $\\mathrm{lb} / \\mathrm{hr} / \\mathrm{cft}$ or PPH/cft",
                "si_factor": 0.0044496,
                "full_name": "pound per hour per cubic foot",
                "notation": "$\\mathrm{lb} /\\left(\\mathrm{h} \\mathrm{ft}^{3}\\right)$ or $\\mathrm{lb} / \\mathrm{hr} / \\mathrm{cft}$ or PPH/cft",
                "aliases": ['lb /left(h ft^{3right)', 'lb / hr / cft', 'PPH/cft'],
            },
            {
                "name": "pound_per_minute_per_cubic_foot",
                "symbol": "lb/(min $\\mathrm{ft}^{3}$ ) or lb/ $\\mathrm{min} / \\mathrm{cft}$",
                "si_factor": 0.26697,
                "full_name": "pound per minute per cubic foot",
                "notation": "lb/(min $\\mathrm{ft}^{3}$ ) or lb/ $\\mathrm{min} / \\mathrm{cft}$",
                "aliases": ['lb/(min ft^{3 )', 'lb/ min / cft'],
            },
            {
                "name": "pound_per_second_per_cubic_foot",
                "symbol": "b/(s ft ${ }^{3}$ ) or lb/sec/cft",
                "si_factor": 16.018,
                "full_name": "pound per second per cubic foot",
                "notation": "b/(s ft ${ }^{3}$ ) or lb/sec/cft",
                "aliases": ['b/(s ft { ^{3 )', 'lb/sec/cft'],
            }
        ],
        "aliases": {}
    },

    "wavenumber": {
        # Wavenumber - LENGTH^-1
        "dimension": WAVENUMBER,
        "units": [
            {
                "name": "diopter",
                "symbol": "D",
                "si_factor": 1.0,
                "full_name": "diopter",
                "notation": "D",
                "aliases": ['D'],
            },
            {
                "name": "kayser",
                "symbol": "K",
                "si_factor": 100.0,
                "full_name": "kayser",
                "notation": "K",
                "aliases": ['K'],
            },
            {
                "name": "reciprocal_meter",
                "symbol": "1/m",
                "si_factor": 1.0,
                "full_name": "reciprocal meter",
                "notation": "1/m",
                "aliases": [],
            }
        ],
        "aliases": {}
    }

}


def create_unit_class(class_name: str, dimension_data: dict) -> type:
    """Dynamically create a unit class with all unit constants as attributes."""
    from .unit import UnitConstant, UnitDefinition
    from .prefixes import get_prefix_by_name
    
    # Create a new class dynamically
    unit_class = type(class_name, (), {})
    
    # Get the dimension
    dimension = dimension_data["dimension"]
    
    # Create UnitDefinition and UnitConstant for each unit
    for unit_data in dimension_data["units"]:
        # Check if this unit was generated from a prefix
        prefix = None
        base_unit_name = None
        if unit_data.get("generated_from_prefix", False):
            # Try to identify the prefix and base unit
            unit_name = unit_data["name"]
            for prefix_name in ["yotta", "zetta", "exa", "peta", "tera", "giga", "mega", "kilo", "hecto", "deca",
                               "deci", "centi", "milli", "micro", "nano", "pico", "femto", "atto", "zepto", "yocto"]:
                if unit_name.startswith(prefix_name):
                    potential_base = unit_name[len(prefix_name):]
                    # Check if this base unit exists in the same dimension
                    for other_unit in dimension_data["units"]:
                        if other_unit["name"] == potential_base and not other_unit.get("generated_from_prefix", False):
                            prefix = get_prefix_by_name(prefix_name)
                            base_unit_name = potential_base
                            break
                    if prefix:
                        break
        
        unit_def = UnitDefinition(
            name=unit_data["name"],
            symbol=unit_data["symbol"],
            dimension=dimension,
            si_factor=unit_data["si_factor"],
            si_offset=0.0,
            base_unit_name=base_unit_name,
            prefix=prefix
        )
        unit_constant = UnitConstant(unit_def)
        
        # Set as class attribute
        setattr(unit_class, unit_data["name"], unit_constant)
        
        # Add aliases
        for alias in unit_data.get("aliases", []):
            if alias and not hasattr(unit_class, alias):
                setattr(unit_class, alias, unit_constant)
    
    return unit_class


def register_all_units(registry):
    """Register all unit definitions to the given registry with prefix support."""
    from .unit import UnitDefinition
    from .prefixes import get_prefix_by_name, StandardPrefixes, PREFIXABLE_UNITS
    
    # First pass: register base units with prefixes where applicable
    for dimension_data in UNIT_DEFINITIONS.values():
        dimension = dimension_data["dimension"]
        
        # Collect base units that need prefix registration
        base_units_to_register = {}
        regular_units = []
        
        for unit_data in dimension_data["units"]:
            unit_name = unit_data["name"]
            if unit_name in PREFIXABLE_UNITS and not unit_data.get("generated_from_prefix", False):
                # This is a base unit that should be registered with prefixes
                base_units_to_register[unit_name] = unit_data
            else:
                regular_units.append(unit_data)
        
        # Register base units with automatic prefix generation
        for unit_name, unit_data in base_units_to_register.items():
            unit_def = UnitDefinition(
                name=unit_data["name"],
                symbol=unit_data["symbol"],
                dimension=dimension,
                si_factor=unit_data["si_factor"],
                si_offset=0.0
            )
            
            if unit_def.name not in registry.units:
                # Get the prefixes for this unit
                prefixes = PREFIXABLE_UNITS.get(unit_name, [])
                registry.register_with_prefixes(unit_def, prefixes)
        
        # Register regular units (non-prefixable or already prefixed)
        for unit_data in regular_units:
            if not unit_data.get("generated_from_prefix", False):
                # Only register if not generated (since prefixed variants are auto-generated above)
                unit_def = UnitDefinition(
                    name=unit_data["name"],
                    symbol=unit_data["symbol"],
                    dimension=dimension,
                    si_factor=unit_data["si_factor"],
                    si_offset=0.0
                )
                
                if unit_def.name not in registry.units:
                    registry.register_unit(unit_def)
    
    # Finalize the registry to compute conversions
    registry.finalize_registration()


# Create unit classes dynamically for ALL dimensions
AbsorbedDoseUnits = create_unit_class("AbsorbedDoseUnits", UNIT_DEFINITIONS["absorbed_dose"])
AccelerationUnits = create_unit_class("AccelerationUnits", UNIT_DEFINITIONS["acceleration"])
ActivationEnergyUnits = create_unit_class("ActivationEnergyUnits", UNIT_DEFINITIONS["activation_energy"])
AmountOfSubstanceUnits = create_unit_class("AmountOfSubstanceUnits", UNIT_DEFINITIONS["amount_of_substance"])
AnglePlaneUnits = create_unit_class("AnglePlaneUnits", UNIT_DEFINITIONS["angle_plane"])
AngleSolidUnits = create_unit_class("AngleSolidUnits", UNIT_DEFINITIONS["angle_solid"])
AngularAccelerationUnits = create_unit_class("AngularAccelerationUnits", UNIT_DEFINITIONS["angular_acceleration"])
AngularMomentumUnits = create_unit_class("AngularMomentumUnits", UNIT_DEFINITIONS["angular_momentum"])
AreaUnits = create_unit_class("AreaUnits", UNIT_DEFINITIONS["area"])
AreaPerUnitVolumeUnits = create_unit_class("AreaPerUnitVolumeUnits", UNIT_DEFINITIONS["area_per_unit_volume"])
AtomicWeightUnits = create_unit_class("AtomicWeightUnits", UNIT_DEFINITIONS["atomic_weight"])
ConcentrationUnits = create_unit_class("ConcentrationUnits", UNIT_DEFINITIONS["concentration"])
DynamicFluidityUnits = create_unit_class("DynamicFluidityUnits", UNIT_DEFINITIONS["dynamic_fluidity"])
ElectricCapacitanceUnits = create_unit_class("ElectricCapacitanceUnits", UNIT_DEFINITIONS["electric_capacitance"])
ElectricChargeUnits = create_unit_class("ElectricChargeUnits", UNIT_DEFINITIONS["electric_charge"])
ElectricCurrentIntensityUnits = create_unit_class("ElectricCurrentIntensityUnits", UNIT_DEFINITIONS["electric_current_intensity"])
ElectricDipoleMomentUnits = create_unit_class("ElectricDipoleMomentUnits", UNIT_DEFINITIONS["electric_dipole_moment"])
ElectricFieldStrengthUnits = create_unit_class("ElectricFieldStrengthUnits", UNIT_DEFINITIONS["electric_field_strength"])
ElectricInductanceUnits = create_unit_class("ElectricInductanceUnits", UNIT_DEFINITIONS["electric_inductance"])
ElectricPotentialUnits = create_unit_class("ElectricPotentialUnits", UNIT_DEFINITIONS["electric_potential"])
ElectricResistanceUnits = create_unit_class("ElectricResistanceUnits", UNIT_DEFINITIONS["electric_resistance"])
ElectricalConductanceUnits = create_unit_class("ElectricalConductanceUnits", UNIT_DEFINITIONS["electrical_conductance"])
ElectricalPermittivityUnits = create_unit_class("ElectricalPermittivityUnits", UNIT_DEFINITIONS["electrical_permittivity"])
ElectricalResistivityUnits = create_unit_class("ElectricalResistivityUnits", UNIT_DEFINITIONS["electrical_resistivity"])
EnergyFluxUnits = create_unit_class("EnergyFluxUnits", UNIT_DEFINITIONS["energy_flux"])
EnergyHeatWorkUnits = create_unit_class("EnergyHeatWorkUnits", UNIT_DEFINITIONS["energy_heat_work"])
EnergyPerUnitAreaUnits = create_unit_class("EnergyPerUnitAreaUnits", UNIT_DEFINITIONS["energy_per_unit_area"])
ForceUnits = create_unit_class("ForceUnits", UNIT_DEFINITIONS["force"])
ForceBodyUnits = create_unit_class("ForceBodyUnits", UNIT_DEFINITIONS["force_body"])
ForcePerUnitMassUnits = create_unit_class("ForcePerUnitMassUnits", UNIT_DEFINITIONS["force_per_unit_mass"])
FrequencyVoltageRatioUnits = create_unit_class("FrequencyVoltageRatioUnits", UNIT_DEFINITIONS["frequency_voltage_ratio"])
FuelConsumptionUnits = create_unit_class("FuelConsumptionUnits", UNIT_DEFINITIONS["fuel_consumption"])
HeatOfCombustionUnits = create_unit_class("HeatOfCombustionUnits", UNIT_DEFINITIONS["heat_of_combustion"])
HeatOfFusionUnits = create_unit_class("HeatOfFusionUnits", UNIT_DEFINITIONS["heat_of_fusion"])
HeatOfVaporizationUnits = create_unit_class("HeatOfVaporizationUnits", UNIT_DEFINITIONS["heat_of_vaporization"])
HeatTransferCoefficientUnits = create_unit_class("HeatTransferCoefficientUnits", UNIT_DEFINITIONS["heat_transfer_coefficient"])
IlluminanceUnits = create_unit_class("IlluminanceUnits", UNIT_DEFINITIONS["illuminance"])
KineticEnergyOfTurbulenceUnits = create_unit_class("KineticEnergyOfTurbulenceUnits", UNIT_DEFINITIONS["kinetic_energy_of_turbulence"])
LengthUnits = create_unit_class("LengthUnits", UNIT_DEFINITIONS["length"])
LinearMassDensityUnits = create_unit_class("LinearMassDensityUnits", UNIT_DEFINITIONS["linear_mass_density"])
LinearMomentumUnits = create_unit_class("LinearMomentumUnits", UNIT_DEFINITIONS["linear_momentum"])
LuminanceSelfUnits = create_unit_class("LuminanceSelfUnits", UNIT_DEFINITIONS["luminance_self"])
LuminousFluxUnits = create_unit_class("LuminousFluxUnits", UNIT_DEFINITIONS["luminous_flux"])
LuminousIntensityUnits = create_unit_class("LuminousIntensityUnits", UNIT_DEFINITIONS["luminous_intensity"])
MagneticFieldUnits = create_unit_class("MagneticFieldUnits", UNIT_DEFINITIONS["magnetic_field"])
MagneticFluxUnits = create_unit_class("MagneticFluxUnits", UNIT_DEFINITIONS["magnetic_flux"])
MagneticInductionFieldStrengthUnits = create_unit_class("MagneticInductionFieldStrengthUnits", UNIT_DEFINITIONS["magnetic_induction_field_strength"])
MagneticMomentUnits = create_unit_class("MagneticMomentUnits", UNIT_DEFINITIONS["magnetic_moment"])
MagneticPermeabilityUnits = create_unit_class("MagneticPermeabilityUnits", UNIT_DEFINITIONS["magnetic_permeability"])
MagnetomotiveForceUnits = create_unit_class("MagnetomotiveForceUnits", UNIT_DEFINITIONS["magnetomotive_force"])
MassUnits = create_unit_class("MassUnits", UNIT_DEFINITIONS["mass"])
MassDensityUnits = create_unit_class("MassDensityUnits", UNIT_DEFINITIONS["mass_density"])
MassFlowRateUnits = create_unit_class("MassFlowRateUnits", UNIT_DEFINITIONS["mass_flow_rate"])
MassFluxUnits = create_unit_class("MassFluxUnits", UNIT_DEFINITIONS["mass_flux"])
MassFractionOfIUnits = create_unit_class("MassFractionOfIUnits", UNIT_DEFINITIONS["mass_fraction_of_i"])
MassTransferCoefficientUnits = create_unit_class("MassTransferCoefficientUnits", UNIT_DEFINITIONS["mass_transfer_coefficient"])
MolalityOfSoluteIUnits = create_unit_class("MolalityOfSoluteIUnits", UNIT_DEFINITIONS["molality_of_solute_i"])
MolarConcentrationByMassUnits = create_unit_class("MolarConcentrationByMassUnits", UNIT_DEFINITIONS["molar_concentration_by_mass"])
MolarFlowRateUnits = create_unit_class("MolarFlowRateUnits", UNIT_DEFINITIONS["molar_flow_rate"])
MolarFluxUnits = create_unit_class("MolarFluxUnits", UNIT_DEFINITIONS["molar_flux"])
MolarHeatCapacityUnits = create_unit_class("MolarHeatCapacityUnits", UNIT_DEFINITIONS["molar_heat_capacity"])
MolarityOfIUnits = create_unit_class("MolarityOfIUnits", UNIT_DEFINITIONS["molarity_of_i"])
MoleFractionOfIUnits = create_unit_class("MoleFractionOfIUnits", UNIT_DEFINITIONS["mole_fraction_of_i"])
MomentOfInertiaUnits = create_unit_class("MomentOfInertiaUnits", UNIT_DEFINITIONS["moment_of_inertia"])
MomentumFlowRateUnits = create_unit_class("MomentumFlowRateUnits", UNIT_DEFINITIONS["momentum_flow_rate"])
MomentumFluxUnits = create_unit_class("MomentumFluxUnits", UNIT_DEFINITIONS["momentum_flux"])
NormalityOfSolutionUnits = create_unit_class("NormalityOfSolutionUnits", UNIT_DEFINITIONS["normality_of_solution"])
ParticleDensityUnits = create_unit_class("ParticleDensityUnits", UNIT_DEFINITIONS["particle_density"])
PermeabilityUnits = create_unit_class("PermeabilityUnits", UNIT_DEFINITIONS["permeability"])
PhotonEmissionRateUnits = create_unit_class("PhotonEmissionRateUnits", UNIT_DEFINITIONS["photon_emission_rate"])
PowerPerUnitMassUnits = create_unit_class("PowerPerUnitMassUnits", UNIT_DEFINITIONS["power_per_unit_mass"])
PowerPerUnitVolumeUnits = create_unit_class("PowerPerUnitVolumeUnits", UNIT_DEFINITIONS["power_per_unit_volume"])
PowerThermalDutyUnits = create_unit_class("PowerThermalDutyUnits", UNIT_DEFINITIONS["power_thermal_duty"])
PressureUnits = create_unit_class("PressureUnits", UNIT_DEFINITIONS["pressure"])
RadiationDoseEquivalentUnits = create_unit_class("RadiationDoseEquivalentUnits", UNIT_DEFINITIONS["radiation_dose_equivalent"])
RadiationExposureUnits = create_unit_class("RadiationExposureUnits", UNIT_DEFINITIONS["radiation_exposure"])
RadioactivityUnits = create_unit_class("RadioactivityUnits", UNIT_DEFINITIONS["radioactivity"])
SecondMomentOfAreaUnits = create_unit_class("SecondMomentOfAreaUnits", UNIT_DEFINITIONS["second_moment_of_area"])
SecondRadiationConstantPlanckUnits = create_unit_class("SecondRadiationConstantPlanckUnits", UNIT_DEFINITIONS["second_radiation_constant_planck"])
SpecificEnthalpyUnits = create_unit_class("SpecificEnthalpyUnits", UNIT_DEFINITIONS["specific_enthalpy"])
SpecificGravityUnits = create_unit_class("SpecificGravityUnits", UNIT_DEFINITIONS["specific_gravity"])
SpecificHeatCapacityConstantPressureUnits = create_unit_class("SpecificHeatCapacityConstantPressureUnits", UNIT_DEFINITIONS["specific_heat_capacity_constant_pressure"])
SpecificLengthUnits = create_unit_class("SpecificLengthUnits", UNIT_DEFINITIONS["specific_length"])
SpecificSurfaceUnits = create_unit_class("SpecificSurfaceUnits", UNIT_DEFINITIONS["specific_surface"])
SpecificVolumeUnits = create_unit_class("SpecificVolumeUnits", UNIT_DEFINITIONS["specific_volume"])
StressUnits = create_unit_class("StressUnits", UNIT_DEFINITIONS["stress"])
SurfaceMassDensityUnits = create_unit_class("SurfaceMassDensityUnits", UNIT_DEFINITIONS["surface_mass_density"])
SurfaceTensionUnits = create_unit_class("SurfaceTensionUnits", UNIT_DEFINITIONS["surface_tension"])
TemperatureUnits = create_unit_class("TemperatureUnits", UNIT_DEFINITIONS["temperature"])
ThermalConductivityUnits = create_unit_class("ThermalConductivityUnits", UNIT_DEFINITIONS["thermal_conductivity"])
TimeUnits = create_unit_class("TimeUnits", UNIT_DEFINITIONS["time"])
TorqueUnits = create_unit_class("TorqueUnits", UNIT_DEFINITIONS["torque"])
TurbulenceEnergyDissipationRateUnits = create_unit_class("TurbulenceEnergyDissipationRateUnits", UNIT_DEFINITIONS["turbulence_energy_dissipation_rate"])
VelocityAngularUnits = create_unit_class("VelocityAngularUnits", UNIT_DEFINITIONS["velocity_angular"])
VelocityLinearUnits = create_unit_class("VelocityLinearUnits", UNIT_DEFINITIONS["velocity_linear"])
ViscosityDynamicUnits = create_unit_class("ViscosityDynamicUnits", UNIT_DEFINITIONS["viscosity_dynamic"])
ViscosityKinematicUnits = create_unit_class("ViscosityKinematicUnits", UNIT_DEFINITIONS["viscosity_kinematic"])
VolumeUnits = create_unit_class("VolumeUnits", UNIT_DEFINITIONS["volume"])
VolumeFractionOfIUnits = create_unit_class("VolumeFractionOfIUnits", UNIT_DEFINITIONS["volume_fraction_of_i"])
VolumetricCalorificHeatingValueUnits = create_unit_class("VolumetricCalorificHeatingValueUnits", UNIT_DEFINITIONS["volumetric_calorific_heating_value"])
VolumetricCoefficientOfExpansionUnits = create_unit_class("VolumetricCoefficientOfExpansionUnits", UNIT_DEFINITIONS["volumetric_coefficient_of_expansion"])
VolumetricFlowRateUnits = create_unit_class("VolumetricFlowRateUnits", UNIT_DEFINITIONS["volumetric_flow_rate"])
VolumetricFluxUnits = create_unit_class("VolumetricFluxUnits", UNIT_DEFINITIONS["volumetric_flux"])
VolumetricMassFlowRateUnits = create_unit_class("VolumetricMassFlowRateUnits", UNIT_DEFINITIONS["volumetric_mass_flow_rate"])
WavenumberUnits = create_unit_class("WavenumberUnits", UNIT_DEFINITIONS["wavenumber"])

# Create standalone DimensionlessUnits class for backward compatibility
class DimensionlessUnits:
    """Standalone dimensionless units class."""
    from .unit import UnitConstant, UnitDefinition
    
    # Standard dimensionless unit
    dimensionless_def = UnitDefinition(
        name="dimensionless",
        symbol="",
        dimension=DIMENSIONLESS,
        si_factor=1.0,
        si_offset=0.0
    )
    dimensionless = UnitConstant(dimensionless_def)


# Module-level function for compatibility with existing code
def get_consolidated_modules():
    """Return a list of module-like objects for consolidated units."""
    class ConsolidatedModule:
        """Mock module object for compatibility with existing registration system."""
        
        def __init__(self, dimension_type: str):
            self.dimension_type = dimension_type
            self.dimension_data = UNIT_DEFINITIONS[dimension_type]
        
        def register_to_registry(self, registry):
            """Register units for this dimension to the registry."""
            from .unit import UnitDefinition
            dimension = self.dimension_data["dimension"]
            
            for unit_data in self.dimension_data["units"]:
                unit_def = UnitDefinition(
                    name=unit_data["name"],
                    symbol=unit_data["symbol"],
                    dimension=dimension,
                    si_factor=unit_data["si_factor"],
                    si_offset=unit_data.get("si_offset", 0.0)
                )
                
                if unit_def.name not in registry.units:
                    registry.register_unit(unit_def)
    
    return [
        ConsolidatedModule(dimension_name) for dimension_name in UNIT_DEFINITIONS
    ]


# Statistics
TOTAL_UNITS = 864
TOTAL_FIELDS = 105
TOTAL_DIMENSIONS = 105
