"""
Some tests for the configuration module
"""
import pytest
import numpy as np
import astropy.units as u

from hydrad_tools.configure import Configure


@pytest.fixture
def configuration():
    return {
        'general': {
            'minimum_collisional_coupling_timescale': 0.01*u.s,
            'force_single_fluid': False,
            'output_interval': 10*u.s,
            'total_time': 5e3*u.s,
            'write_file_physical': True,
            'write_file_ion_populations': True,
            'write_file_hydrogen_level_populations': True,
            'write_file_timescales': True,
            'write_file_equation_terms': True,
            'logging_frequency': 1000,
            'heat_flux_limiting_coefficient': 0.167,
            'heat_flux_timestep_limit': 1e-10*u.s,
            'use_kinetic_model': True,
            'loop_length': 90*u.Mm,
            'loop_inclination': 0*u.deg,
            'footpoint_height': 5*u.Mm,
        },
        'initial_conditions': {
            'footpoint_temperature': 1e4*u.K,
            'footpoint_density': 1e12*u.cm**(-3),
            'heating_location': 45*u.Mm,
            'heating_scale_height': 1e300*u.cm,
            'isothermal': True,
        },
        'grid': {
            'minimum_delta_s': 1.*u.cm,
            'maximum_variation': 0.1,
            'maximum_refinement_level': 12,
            'adapt': True,
            'adapt_every_n_time_steps': 1000,
            'refine_on_density': True,
            'refine_on_electron_energy': True,
            'refine_on_hydrogen_energy': True,
            'minimum_fractional_difference': 0.05,
            'maximum_fractional_difference': 0.1,
            'linear_restriction': True,
            'enforce_conservation': True,
            'minimum_cells': 150,
            'maximum_cells': 30000,
        },
        'solver': {
            'epsilon': 0.01,
            'safety_radiation': 0.1,
            'safety_conduction': 1.0,
            'safety_advection': 1.0,
            'safety_viscosity': 1.0,
            'safety_atomic': 1.0,
            'cutoff_ion_fraction': 1e-6,
            'epsilon_d': 0.1,
            'epsilon_r': 1.8649415311920072,
            'timestep_increase_limit': 0.05,
            'minimum_radiation_temperature': 2e4*u.K,
            'zero_over_temperature_interval': 5e2*u.K,
            'minimum_temperature': 1e4*u.K,
            'maximum_optically_thin_density': 1e12*u.cm**(-3),

        },
        'radiation': {
            'use_power_law_radiative_losses': True,
            'decouple_ionization_state_solver': True,
            'density_dependent_rates': True,
            'optically_thick_radiation': True,
            'nlte_chromosphere': True,
            'elements_nonequilibrium': ['iron'],
            'elements_equilibrium': ['iron', 'He', 1],
            'ranges_dataset': 'ranges',
            'emissivity_dataset': 'chianti_v7',
            'abundance_dataset': 'asplund',
            'rates_dataset': 'chianti_v7',
        },
        'heating': {
            'background_heating': False,
            'heat_electrons': True,
        }
    }


def test_collisions_header(configuration):
    c = Configure(configuration, freeze_date=True)
    collisions_header = f"""// ****
// *
// * #defines for configuring the shortest collisional coupling timescale
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****

// **** Physics ****
#define MINIMUM_COLLISIONAL_COUPLING_TIME_SCALE 0.01

// **** End of Physics ****"""
    assert c.collisions_header == collisions_header
    c.config['general']['force_single_fluid'] = True
    collisions_header = f"""// ****
// *
// * #defines for configuring the shortest collisional coupling timescale
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****

// **** Physics ****
#define MINIMUM_COLLISIONAL_COUPLING_TIME_SCALE 0.01
#define FORCE_SINGLE_FLUID
// **** End of Physics ****"""
    assert c.collisions_header == collisions_header


def test_heating_config(configuration):
    # TODO: test background heating
    # No events
    c = Configure(configuration, freeze_date=True)
    heating_config = f"""0.0 0.0 0.0

0


Configuration file generated by hydrad_tools on {c.date}"""
    assert c.heating_cfg == heating_config
    # 1 event
    c.config['heating']['events'] = [
        {'time_start': 0.*u.s, 'rise_duration': 100.*u.s, 'decay_duration': 100.*u.s,
         'total_duration': 200.*u.s, 'location': 0*u.cm, 'scale_height': 1e300*u.cm,
         'rate': 0.1*u.erg/(u.cm**3)/u.s}
    ]
    heating_config = f"""0.0 0.0 0.0

1

0.0 1e+300 0.1 0.0 100.0 100.0 200.0

Configuration file generated by hydrad_tools on {c.date}"""
    assert c.heating_cfg == heating_config


def test_heating_header(configuration):
    c = Configure(configuration, freeze_date=True)
    # Electron Heating
    header = f'''// ****
// *
// * #defines for configuring the heating model
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****
#define HEATED_SPECIES 0


#include "../../Radiation_Model/source/config.h"'''
    assert c.heating_header == header
    # Ion Heating
    c.config['heating']['heat_electrons'] = False
    header = f'''// ****
// *
// * #defines for configuring the heating model
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****
#define HEATED_SPECIES 1


#include "../../Radiation_Model/source/config.h"'''
    assert c.heating_header == header
    # Other Heating Models
    c.config['heating']['alfven_wave_heating'] = True
    c.config['heating']['beam_heating'] = True
    header = f'''// ****
// *
// * #defines for configuring the heating model
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****
#define HEATED_SPECIES 1
#define BEAM_HEATING
#define ALFVEN_WAVE_HEATING
#include "../../Radiation_Model/source/config.h"'''
    assert c.heating_header == header


def test_hydrad_config(configuration):
    c = Configure(configuration, freeze_date=True)
    config = f"""Initial_Conditions/profiles/initial.amr
Initial_Conditions/profiles/initial.amr.gravity
5000.0
10.0

Configuration file generated by hydrad_tools on {c.date}"""
    assert c.hydrad_cfg == config
    c.config['general']['poly_fit_gravity'] = np.array([1, 2, 3])
    c.config['general']['poly_fit_magnetic_field'] = np.array([1, 2, 3])
    config = f"""Initial_Conditions/profiles/initial.amr
poly_fit.gravity
poly_fit.magnetic_field
5000.0
10.0

Configuration file generated by hydrad_tools on {c.date}"""
    assert c.hydrad_cfg == config
    c.config['general']['initial_amr_file'] = 'Results/profile10.amr'
    config = f"""Results/profile10.amr
poly_fit.gravity
poly_fit.magnetic_field
5000.0
10.0

Configuration file generated by hydrad_tools on {c.date}"""


def test_hydrad_header(configuration):
    c = Configure(configuration, freeze_date=True)
    header = f"""// ****
// *
// * #defines for configuring the hydrodynamic model
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****

// **** Output ****
#define WRITE_FILE_PHYSICAL
#define WRITE_FILE_ION_POPULATIONS
#define WRITE_FILE_HSTATE
#define WRITE_FILE_SCALES
#define WRITE_FILE_TERMS
#define OUTPUT_EVERY_N_TIME_STEPS 1000
// **** End of Output ****

// **** Physics ****
#include "../../Heating_Model/source/config.h"
#include "../../Radiation_Model/source/config.h"
#define HEAT_FLUX_LIMITING_COEFFICIENT 0.167
#define TIME_STEP_LIMIT 1e-10
#define USE_KINETIC_MODEL
#include "collisions.h"

// **** End of Physics ****

// **** Solver ****
#define SAFETY_RADIATION 0.1
#define SAFETY_CONDUCTION 1.0
#define SAFETY_ADVECTION 1.0
#define SAFETY_VISCOSITY 1.0
#define TIME_STEP_INCREASE_LIMIT 1.05

#define MINIMUM_RADIATION_TEMPERATURE 20000.0
#define ZERO_OVER_TEMPERATURE_INTERVAL 500.0
#define MINIMUM_TEMPERATURE 10000.0
// **** End of Solver ****

// **** Grid ****
#define MAX_REFINEMENT_LEVEL 12
#define ADAPT
#define ADAPT_EVERY_N_TIME_STEPS 1000
#define REFINE_ON_DENSITY
#define REFINE_ON_ELECTRON_ENERGY
#define REFINE_ON_HYDROGEN_ENERGY
#define MIN_FRAC_DIFF 0.05
#define MAX_FRAC_DIFF 0.1
#define LINEAR_RESTRICTION
#define ENFORCE_CONSERVATION
// **** End of Grid ****"""
    assert c.hydrad_header == header
    c.config['general']['poly_fit_magnetic_field'] = np.array([1, 2, 3])
    header = f"""// ****
// *
// * #defines for configuring the hydrodynamic model
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****

// **** Output ****
#define WRITE_FILE_PHYSICAL
#define WRITE_FILE_ION_POPULATIONS
#define WRITE_FILE_HSTATE
#define WRITE_FILE_SCALES
#define WRITE_FILE_TERMS
#define OUTPUT_EVERY_N_TIME_STEPS 1000
// **** End of Output ****

// **** Physics ****
#include "../../Heating_Model/source/config.h"
#include "../../Radiation_Model/source/config.h"
#define HEAT_FLUX_LIMITING_COEFFICIENT 0.167
#define TIME_STEP_LIMIT 1e-10
#define USE_KINETIC_MODEL
#include "collisions.h"
#define USE_POLY_FIT_TO_MAGNETIC_FIELD
// **** End of Physics ****

// **** Solver ****
#define SAFETY_RADIATION 0.1
#define SAFETY_CONDUCTION 1.0
#define SAFETY_ADVECTION 1.0
#define SAFETY_VISCOSITY 1.0
#define TIME_STEP_INCREASE_LIMIT 1.05

#define MINIMUM_RADIATION_TEMPERATURE 20000.0
#define ZERO_OVER_TEMPERATURE_INTERVAL 500.0
#define MINIMUM_TEMPERATURE 10000.0
// **** End of Solver ****

// **** Grid ****
#define MAX_REFINEMENT_LEVEL 12
#define ADAPT
#define ADAPT_EVERY_N_TIME_STEPS 1000
#define REFINE_ON_DENSITY
#define REFINE_ON_ELECTRON_ENERGY
#define REFINE_ON_HYDROGEN_ENERGY
#define MIN_FRAC_DIFF 0.05
#define MAX_FRAC_DIFF 0.1
#define LINEAR_RESTRICTION
#define ENFORCE_CONSERVATION
// **** End of Grid ****"""
    assert c.hydrad_header == header


def test_initial_conditions_config(configuration):
    c = Configure(configuration, freeze_date=True)
    # Isothermal case
    config = f"""Initial_Conditions/profiles/initial.amr

9000000000.0
0.0
500000000.0

10000.0

1000000000000.0

4500000000.0
1e+300
0.0
0.0
1.0
1.0

Configuration file generated by hydrad_tools on {c.date}"""
    assert c.intial_conditions_cfg == config
    # Hydrostatic equilibrium
    c.config['initial_conditions']['isothermal'] = False
    c.config['initial_conditions']['heating_range_lower_bound'] = 1e-8*u.erg/(u.cm**3)/u.s
    c.config['initial_conditions']['heating_range_upper_bound'] = 1e2*u.erg/(u.cm**3)/u.s
    c.config['initial_conditions']['heating_range_step_size'] = 0.01
    c.config['initial_conditions']['heating_range_fine_tuning'] = 10000
    config = f"""Initial_Conditions/profiles/initial.amr

9000000000.0
0.0
500000000.0

10000.0

1000000000000.0

4500000000.0
1e+300
-8.0
2.0
0.01
10000

Configuration file generated by hydrad_tools on {c.date}"""
    assert c.intial_conditions_cfg == config


def test_initial_conditions_header(configuration):
    c = Configure(configuration, freeze_date=True)
    c.config['initial_conditions']['isothermal'] = False
    header = f"""// ****
// *
// * #defines for configuring the hydrostatic model
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****

// **** Output ****
// **** End of Output ****

// **** Physics ****
#include "../../Radiation_Model/source/config.h"



// **** Solver ****
#define EPSILON 0.01

// **** Grid ****
#define ADAPT
#define MIN_CELLS 150
#define MAX_CELLS 30000
#define MAX_REFINEMENT_LEVEL 12
#define MIN_DS 1.0
#define MAX_VARIATION 1.1"""
    assert c.initial_conditions_header == header
    c.config['initial_conditions']['isothermal'] = True
    c.config['general']['poly_fit_gravity'] = np.array([1, 2, 3])
    header = f"""// ****
// *
// * #defines for configuring the hydrostatic model
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****

// **** Output ****
// **** End of Output ****

// **** Physics ****
#include "../../Radiation_Model/source/config.h"
#define ISOTHERMAL
#define USE_POLY_FIT_TO_GRAVITY
#define POLY_FIT_TO_GRAVITY_FILE "poly_fit.gravity"

// **** Solver ****
#define EPSILON 0.01

// **** Grid ****
#define ADAPT
#define MIN_CELLS 150
#define MAX_CELLS 30000
#define MAX_REFINEMENT_LEVEL 12
#define MIN_DS 1.0
#define MAX_VARIATION 1.1"""
    assert c.initial_conditions_header == header


def test_radiation_header(configuration):
    c = Configure(configuration, freeze_date=True)
    header = f"""// ****
// *
// * #defines for configuring the radiation model
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****

// **** Physics ****
#define USE_POWER_LAW_RADIATIVE_LOSSES
#define DENSITY_DEPENDENT_RATES
#define OPTICALLY_THICK_RADIATION
#define NLTE_CHROMOSPHERE
#include "../../HYDRAD/source/collisions.h"
// **** End of Physics ****

// **** Solver ****
#define MAX_OPTICALLY_THIN_DENSITY 1000000000000.0
#define SAFETY_ATOMIC 1.0
#define CUTOFF_ION_FRACTION 1e-06
#define EPSILON_D 0.1
#define EPSILON_R 1.8649415311920072
// **** End of Solver ****"""
    assert c.radiation_header == header
    c.config['radiation']['use_power_law_radiative_losses'] = False
    c.config['radiation']['density_dependent_rates'] = False
    c.config['radiation']['optically_thick_radiation'] = False
    c.config['radiation']['nlte_chromosphere'] = False
    header = f"""// ****
// *
// * #defines for configuring the radiation model
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by hydrad_tools on {c.date}
// *
// ****

// **** Physics ****

#define NON_EQUILIBRIUM_RADIATION
#define DECOUPLE_IONIZATION_STATE_SOLVER




#include "../../HYDRAD/source/collisions.h"
// **** End of Physics ****

// **** Solver ****
#define MAX_OPTICALLY_THIN_DENSITY 1000000000000.0
#define SAFETY_ATOMIC 1.0
#define CUTOFF_ION_FRACTION 1e-06
#define EPSILON_D 0.1
#define EPSILON_R 1.8649415311920072
// **** End of Solver ****"""
    assert c.radiation_header == header


def test_radiation_config(configuration):
    c = Configure(configuration, freeze_date=True)
    config = f"""ranges
chianti_v7
asplund
chianti_v7
3
h
1
he
2
fe
26

Configuration file generated by hydrad_tools on {c.date}"""
    assert c.radiation_equilibrium_cfg == config
    config = f"""ranges
chianti_v7
asplund
chianti_v7
1
fe
26

Configuration file generated by hydrad_tools on {c.date}"""
    assert c.radiation_nonequilibrium_cfg == config
