"""
Some tests for the configuration module
"""
import pytest
import astropy.units as u

from hydrad_tools.configure import Configure


@pytest.fixture
def configuration():
    return {
        'general': {
            'minimum_collisional_coupling_timescale': 0.01*u.s,
            'force_single_fluid': False,
        },
        'initial_conditions': {},
        'grid': {},
        'solver': {},
        'radiation': {},
        'heating': {
            'background_heating': False,
            'heat_electrons': True, 
        }
    }


def test_collisions_header(configuration):
    c = Configure(configuration)
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
    c = Configure(configuration)
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
    c = Configure(configuration)
    # Electron Heating
    heating_header = f'''// ****
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
    assert c.heating_header == heating_header
    # Ion Heating
    c.config['heating']['heat_electrons'] = False
    heating_header = f'''// ****
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
    assert c.heating_header == heating_header
    # Other Heating Models
    c.config['heating']['alfven_wave_heating'] = True
    c.config['heating']['beam_heating'] = True
    heating_header = f'''// ****
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
    assert c.heating_header == heating_header
