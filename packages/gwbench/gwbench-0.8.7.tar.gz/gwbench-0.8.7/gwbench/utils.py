# Copyright (C) 2020  Ssohrab Borhanian
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import logging
import os
import sys
from logging import getLevelName

import numpy as np

################################################################################
# constants
################################################################################

#-----constants in SI units-----
GNewton    = 6.6743e-11
cLight     = 2.99792458e8
Msun       = 1.9884099021470415e+30
Mpc        = 3.085677581491367e+22
REarth     = 6.371e6
AU         = 1.4959787066e11
year       = 3.1536e7
hPlanck    = 6.62607015e-34
TEarthSol  = 86400   # solar day    (24h 60m 60s)
TEarthSid  = 86164.1 # sidereal day (23h 56m  4.0905s, found root 86164.09053826332)
TEarth     = TEarthSid
tc_offset  = 25134.55 # offset to tc: tc_gwbench = tc_bilby + tc_offset

#-----convert mass in solar masses to seconds-----
MTsun             = Msun * GNewton / cLight**3
#-----convert mass/distance in solar mass/Mpc to dimensionless-----
strain_fac        = GNewton / cLight**2 * Msun/Mpc
#-----convert seconds to radians with a periodicty of one day-----
time_to_rad_earth = 2 * np.pi / TEarth

################################################################################
# detector specifications --- location and geometry
################################################################################

# V-shaped interferometers have opening angles of pi/3, L-shaped interferometers have pi/2 (which is the default).
shape_opening_angles = {
    'L' : np.pi / 2.,
    'V1': np.pi / 3.,
    'V2': np.pi / 3.,
    'V3': np.pi / 3.,
    }

# V2 and V3 interferometers in a triangular configuration require a correction to the azimuth angle of the y-arm; default is 0.
# If the shape is not specified, the azimuth angle is not corrected and needs to be specified in the detector specifications correctly.
azimuth_shape_corr = {
    'L' : 0.,
    'V1': 0.,
    'V2': 2. * np.pi / 3.,
    'V3': 4. * np.pi / 3.,
    }

# the y-arm is the default arm for computation therefore a correction is needed, if either x-arm or bisector is specified; default is 0.
azimuth_arm_corr = {
    'x'       : np.pi / 2.,
    'bisector': np.pi / 4.,
    'y'       : 0.,
    }

# In-built detector specifications for the LIGO-Virgo-KAGRA detectors and various fiducial detector configurations.
# ----
# Switched to more precise angles for H, L, V, K, I, ET1, ET2, ET3 on 2022_03_29, found at: https://lscsoft.docs.ligo.org/lalsuite/lal/_l_a_l_detectors_8h_source.html
det_specs_built_in = {
    # 2G sites
    'H'     : {'longitude':-2.08405676917, 'latitude': 0.81079526383, 'arm_azimuth': np.pi-5.65487724844, 'which_arm':'y', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'L'     : {'longitude':-1.58430937078, 'latitude': 0.53342313506, 'arm_azimuth': np.pi-4.40317772346, 'which_arm':'y', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'V'     : {'longitude': 0.18333805213, 'latitude': 0.76151183984, 'arm_azimuth': np.pi-0.33916285222, 'which_arm':'y', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'K'     : {'longitude': 2.396441015,   'latitude': 0.6355068497,  'arm_azimuth': np.pi-1.054113,      'which_arm':'y', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'I'     : {'longitude': 1.33401332494, 'latitude': 0.24841853020, 'arm_azimuth': np.pi-1.57079637051, 'which_arm':'y', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'LHO'   : {'longitude':-2.06982474503, 'latitude': 0.81079270401, 'arm_azimuth': 2.19910516123923,    'which_arm':'x', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'LLO'   : {'longitude':-1.5572845695,  'latitude': 0.53342110078, 'arm_azimuth': 3.45080197126464,    'which_arm':'x', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'LIO'   : {'longitude': 1.3444416672,  'latitude': 0.34231239582, 'arm_azimuth': 2.05248780779809,    'which_arm':'x', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    # fiducial ET sites
    'ET1'   : {'longitude': 0.18333805213, 'latitude': 0.76151183984, 'arm_azimuth': np.pi-0.33916285222, 'which_arm':'y', 'shape':'V1', 'radius':REarth, 'period':TEarthSid},
    'ET2'   : {'longitude': 0.18333805213, 'latitude': 0.76151183984, 'arm_azimuth': np.pi-0.33916285222, 'which_arm':'y', 'shape':'V2', 'radius':REarth, 'period':TEarthSid},
    'ET3'   : {'longitude': 0.18333805213, 'latitude': 0.76151183984, 'arm_azimuth': np.pi-0.33916285222, 'which_arm':'y', 'shape':'V3', 'radius':REarth, 'period':TEarthSid},
    'ETS1'  : {'longitude': 0.1643518379,  'latitude': 0.70714923527, 'arm_azimuth': 1.5707963267949,     'which_arm':'x', 'shape':'V1', 'radius':REarth, 'period':TEarthSid},
    'ETS2'  : {'longitude': 0.1643518379,  'latitude': 0.70714923527, 'arm_azimuth': 1.5707963267949,     'which_arm':'x', 'shape':'V2', 'radius':REarth, 'period':TEarthSid},
    'ETS3'  : {'longitude': 0.1643518379,  'latitude': 0.70714923527, 'arm_azimuth': 1.5707963267949,     'which_arm':'x', 'shape':'V3', 'radius':REarth, 'period':TEarthSid},
    # fiducial CE sites
    'C'     : {'longitude':-1.9691740,     'latitude': 0.764918,      'arm_azimuth': 0.,                  'which_arm':'y', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'N'     : {'longitude':-1.8584265,     'latitude': 0.578751,      'arm_azimuth':-np.pi/3.,            'which_arm':'y', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'S'     : {'longitude': 2.5307270,     'latitude':-0.593412,      'arm_azimuth': np.pi/4.,            'which_arm':'y', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'CEA'   : {'longitude':-2.18166156499, 'latitude': 0.80285145592, 'arm_azimuth': 4.53785605518526,    'which_arm':'x', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'CEB'   : {'longitude':-1.64060949687, 'latitude': 0.50614548308, 'arm_azimuth': 3.49065850398866,    'which_arm':'x', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    'CES'   : {'longitude': 2.5307270,     'latitude':-0.593412,      'arm_azimuth': np.pi/4.,            'which_arm':'y', 'shape':'L',  'radius':REarth, 'period':TEarthSid},
    }

def det_specs(loc, user_locs=None):
    '''
    Calculate the detector angles and shape for a given detector location.

    Parameters
    ----------
    loc : str
        Location (and implied orientation) of a detector.
    user_locs : dict
        User defined locations and orientations of detectors.

        This should specify
            'longitude':      longitude in radians,
            'latitude':       latitude in radians,
            'arm_azimuth':    azimuth of the specified arm in radians; the arm can be specified with 'which_arm' and the default 'y',
            'which_arm':      specify the arm with respect to which to take the azimuth: ['x', 'y', 'bisector'],
            'shape':          shape of the interferometer ['L', 'V1', 'V2', 'V3']; takes precededence over 'opening_angle',
            'opening_angle':  opening angle of the interferometer in radians; if 'shape' is specified, this is ignored,
            'radius':         Default: REarth;      radius from the geocenter of the detector's location in meters,
            'period':         Default: TEarthSid;   period of the detector around the geocenter in seconds,

    Returns
    -------
    alpha : float
        Longitude [rad]
    beta : float
        Latitude [rad]
    gamma : float
        Angle from 'Due East' to y-arm [rad]
    opening_angle or shape : float or str
        Opening angle of the detector or shape of interferometer (e.g. 'L', 'V1', ...), default is pi/2.
    radius : float
        Radius from the geocenter of the detector's location [m], default is REarth.
    period : float
        Period of the detector around the geocenter [s], default is TEarthSid.
    '''
    if user_locs is not None and loc in user_locs: _loc = user_locs[loc]
    elif loc in det_specs_built_in:                _loc = det_specs_built_in[loc]
    else: log_msg(f'det_specs: Provided location {loc} is neither among the implemented locations nor in provided user_locs.', level='ERROR')

    if 'shape' in _loc:
        if _loc['shape'] not in shape_opening_angles:
            log_msg(f'det_specs: Provided shape {_loc["shape"]} is not among the implemented shapes {list(shape_opening_angles.keys())}.', level='ERROR')
        opening_angle = shape_opening_angles[_loc['shape']]
        gamma_corr    = azimuth_shape_corr[_loc['shape']]
    else:
        opening_angle = _loc.get('opening_angle', np.pi / 2.)
        gamma_corr    = 0.

    return (_loc['longitude'],
            _loc['latitude'],
            _loc['arm_azimuth'] + azimuth_arm_corr[_loc['which_arm']] + gamma_corr, 
            opening_angle,
            _loc.get('radius', REarth),
            _loc.get('period', TEarthSid))

################################################################################
# basic functions
################################################################################

def reduce_symbols_strings(string1, string2):
    '''
    Combine two sympy symbols strings without duplicates.

    Parameters
    ----------
    string1 : str
        First sympy symbols string.
    string2 : str
        Second sympy symbols string.

    Returns
    -------
    str
        Combined sympy symbols string without duplicates.
    '''
    # combine the two lists
    symbols_list = string1.split(' ') + string2.split(' ')
    # remove duplicates
    symbols_list = list(dict.fromkeys(symbols_list))

    # recreate a string of symbols and return it
    return ' '.join(symbols_list)

def remove_symbols(string1, string2, keep_same=True):
    '''
    Remove symbols from one sympy symbols string that are not present in the other.

    Parameters
    ----------
    string1 : str
        First sympy symbols string.
    string2 : str
        Second sympy symbols string.
    keep_same : bool
        If True, keep the symbols that are present in both strings.

    Returns
    -------
    str
        Combined sympy symbols string without duplicates.
    '''
    symbs_list1 = string1.split(' ')
    symbs_list2 = string2.split(' ')
    # remove unwanted symbols from 1
    if keep_same:
        symbols_list = [x for x in symbs_list1 if x in symbs_list2]
    else:
        symbols_list = [x for x in symbs_list1 if x not in symbs_list2]

    # recreate a string of symbols and return it
    return ' '.join(symbols_list)

def get_sub_array_ids(arr, sub_arr):
    '''
    Get the indices of the elements of a subarray in a larger array.

    Parameters
    ----------
    arr : np.ndarray
        Larger array.
    sub_arr : np.ndarray
        Subarray.

    Returns
    -------
    np.ndarray
        Indices of the elements of the subarray in the larger array.
    '''
    return min_max_mask(arr, sub_arr[0], sub_arr[-1])

def get_sub_dict(dic, key_list, keep_in_dict=True):
    '''
    Get a subset of a dictionary based on a list of keys.

    Parameters
    ----------
    dic : dict
        Dictionary.
    key_list : list
        List of keys.
    keep_in_dict : bool
        If True, keep the keys in the dict. If False, keep the complientary keys.

    Returns
    -------
    dict
        Subset of the dictionary.
    '''
    if type(key_list) == str: key_list = key_list.split(' ')
    if keep_in_dict: return {k:v for k,v in dic.items() if k     in key_list}
    else:            return {k:v for k,v in dic.items() if k not in key_list}

def is_subset_lists(sub, sup):
    '''
    Check if a list is a subset of another list.

    Parameters
    ----------
    sub : list
        Sublist.
    sup : list
        Superlist.

    Returns
    -------
    bool
        True if the sublist is a subset of the superlist, False otherwise.
    '''
    return all([el in sup for el in sub])

def min_max_mask(arr, min_val=-np.inf, max_val=np.inf, strict_min=False, strict_max=False):
    '''
    Create a mask for an array based on minimum and maximum values.

    Parameters
    ----------
    arr : np.ndarray
        Array.
    min_val : float
        Minimum value. Default is -np.inf.
    max_val : float
        Maximum value. Default is np.inf.
    strict_min : bool
        If True, the minimum value is excluded. Default is False.
    strict_max : bool
        If True, the maximum value is excluded. Default is False.

    Returns
    -------
    mask : np.ndarray
        Mask for the array.
    '''
    if strict_min: min_mask = arr >  min_val
    else:          min_mask = arr >= min_val

    if strict_max: max_mask = arr <  max_val
    else:          max_mask = arr <= max_val

    return np.logical_and(min_mask, max_mask)

################################################################################
# waveform manipluations
################################################################################

#-----stable evaluation of exponential phase factors-----
def mod_1(val, np=np):
    '''
    Return stable evaluation of mod(val, 1) for a value val to be inserted in exp(1j * 2pi * val).
    The returned value is always in the range [0, 1).

    Parameters
    ----------
    val : np.ndarray or jnp.ndarray
        Values

    Returns
    -------
    mod : np.ndarray or jnp.ndarray
        mod(val, 1)
    '''
    return val - np.floor(val)

#-----convert waveform polarizations to amplitude and phase-----
def transform_hfpc_to_amp_pha(hfpc, f, params_list, np=np):
    '''
    Calculate and transform the complex frequency domain waveform for the plus and cross polarizations to amplitude and phase.

    Parameters
    ----------
    hfpc : np.ndarray
        Complex frequency domain waveform for the plus and cross polarizations.
    f : np.ndarray
        Frequency array.
    params_list : list
        List of parameters.

    Returns
    -------
    np.ndarray
        Amplitude of the plus polarization.
    np.ndarray
        Phase of the plus polarization.
    np.ndarray
        Amplitude of the cross polarization.
    np.ndarray
        Phase of the cross polarization.
    '''
    hfp, hfc = hfpc(f, *params_list)
    return pl_cr_to_amp_pha(hfp, hfc, np=np)

def pl_cr_to_amp_pha(hfp, hfc, np=np):
    '''
    Transform the plus and cross polarizations to amplitude and phase.

    Parameters
    ----------
    hfp : np.ndarray
        Plus polarization.
    hfc : np.ndarray
        Cross polarization.

    Returns
    -------
    np.ndarray
        Amplitude of the plus polarization.
    np.ndarray
        Phase of the plus polarization.
    np.ndarray
        Amplitude of the cross polarization.
    np.ndarray
        Phase of the cross polarization.
    '''
    hfp_amp, hfp_pha = amp_pha_from_z(hfp, np=np)
    hfc_amp, hfc_pha = amp_pha_from_z(hfc, np=np)
    return hfp_amp, hfp_pha, hfc_amp, hfc_pha

#-----convert amp/phase derivatives to re/im ones-----
def z_deriv_from_amp_pha(amp, pha, del_amp, del_pha, np=np):
    '''
    Calculate the real and imaginary part of waveform derivatives from the amplitude and phase and their derivatives.

    Parameters
    ----------
    amp : np.ndarray
        Amplitude of the waveform.
    pha : np.ndarray
        Phase of the waveform.
    del_amp : np.ndarray
        Derivative of the amplitude.
    del_pha : np.ndarray
        Derivative of the phase.

    Returns
    -------
    np.ndarray
        Real part of the waveform derivative.
    np.ndarray
        Imaginary part of the waveform derivative.
    '''
    if len(del_amp.shape) == 2: return np.array([ del_amp[:,i] * np.exp(1j*pha) + amp * np.exp(1j*pha) * 1j * del_pha[:,i]
                                                  for i in range(del_amp.shape[1]) ], dtype=complex).T
    else:                       return del_amp * np.exp(1j*pha) + amp * np.exp(1j*pha) * 1j * del_pha

#-----re/im vs. amp/phase transformations-----
def re_im_from_amp_pha(amp, pha, np=np):
    '''
    Calculate the real and imaginary part of a complex number from its amplitude and phase.

    Parameters
    ----------
    amp : np.ndarray
        Amplitude.
    pha : np.ndarray
        Phase.

    Returns
    -------
    np.ndarray
        Real part of the complex number.
    np.ndarray
        Imaginary part of the complex number.
    '''
    return re_im_from_z(z_from_amp_pha(amp, pha), np=np)

def amp_pha_from_re_im(re, im, np=np):
    '''
    Calculate the amplitude and phase of a complex number from its real and imaginary part.

    Parameters
    ----------
    re : np.ndarray
        Real part.
    im : np.ndarray
        Imaginary part.

    Returns
    -------
    np.ndarray
        Amplitude.
    np.ndarray
        Phase.
    '''
    return amp_pha_from_z(z_from_re_im(re, im), np=np)

#-----re/im or amp/phase vs. complex number transformations-----
def re_im_from_z(z, np=np):
    '''
    Calculate the real and imaginary part of a complex number.

    Parameters
    ----------
    z : np.ndarray
        Complex number.

    Returns
    -------
    np.ndarray
        Real part of the complex number.
    np.ndarray
        Imaginary part of the complex number.
    '''
    return np.real(z), np.imag(z)

def z_from_re_im(re, im):
    '''
    Calculate the complex number from its real and imaginary part.

    Parameters:
        re (array): Real part.
        im (array): Imaginary part.

    Returns:
        array: Complex number.
    '''
    return re + 1j * im

def amp_pha_from_z(z, np=np):
    '''
    Calculate the amplitude and phase of a complex number.

    Parameters
    ----------
    z : np.ndarray
        Complex number.

    Returns
    -------
    np.ndarray
        Amplitude.
    np.ndarray
        Phase.
    '''
    return np.abs(z), np.unwrap(np.angle(z))

def z_from_amp_pha(amp, pha, np=np):
    '''
    Calculate the complex number from its amplitude and phase.

    Parameters
    ----------
    amp : np.ndarray
        Amplitude.
    pha : np.ndarray
        Phase.

    Returns
    -------
    np.ndarray
        Complex number.
    '''
    return amp * np.exp(1j*pha)


################################################################################
# IO functions
################################################################################

#-----Block and unblock printing-----
def block_print(active=True):
    '''
    Block printing to the standard output.

    Parameters
    ----------
    active : bool
        If True, block the printing. If False, do nothing.
    '''
    if active: sys.stdout = open(os.devnull, 'w')
    return

def unblock_print(active=True):
    '''
    Unblock printing to the standard output.

    Parameters
    ----------
    active : bool
        If True, unblock the printing. If False, do nothing.
    '''
    if active: sys.stdout = sys.__stdout__
    return

#-----sending warning or error message-----
def log_msg(message, logger=None, level='INFO'):
    '''
    Log a message to the standard output or a logger.

    Parameters
    ----------
    message : str
        Message to be logged.
    logger : logging.Logger
        Logger to log the message. If None, the message is printed to the standard output.
    level : str
        Level of the message, if a logger is used. Can be 'DEBUG', 'INFO', 'WARNING', 'ERROR', or 'CRITICAL'.
    '''
    if logger is None: print(level + ': ' + message)
    else:              logger.log(getLevelName(level), message)
    if level in ['ERROR', 'CRITICAL']: sys.exit()

def get_logger(name, level='INFO', stdout=True, logfile=None):
    '''
    Get a logger.

    Parameters
    ----------
    name : str
        Name of the logger.
    level : str
        Level of the logger. Can be 'DEBUG', 'INFO', 'WARNING', 'ERROR', or 'CRITICAL'.
    stdout : bool
        If True, log to the standard output.
    logfile : str
        If not None, log to a file with the given name.

    Returns
    -------
    logging.Logger
        Logger.
    '''
    logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s : %(message)s')
    if stdout: logging.basicConfig(stream = sys.stdout)
    if logfile is not None: logging.basicConfig(filename = logfile, filemode = 'w')
    logger = logging.getLogger(name)
    set_logger_level(logger, level)
    return logger

def set_logger_level(logger, level):
    '''
    Set the level of a logger.

    Parameters
    ----------
    logger : logging.Logger
        Logger.
    level : str
        Level of the logger. Can be 'DEBUG', 'INFO', 'WARNING', 'ERROR', or 'CRITICAL'.
    '''
    logger.setLevel(level)


################################################################################
# network_spec handlers
################################################################################

def read_det_keys_from_label(network_label):
    '''
    Read the network label and find all detectors.

    Parameters
    ----------
    network_label : str
        Network label.

    Returns
    -------
    list
        list: List of detector keys.
    '''
    det_keys = []

    ##-----read the network label and find all detectors-----
    keys = list(network_label)

    # - in network list means that all 2G detectors up to that index are to be
    # taken at aLIGO sensitivity
    aLIGO = int('-' in keys)
    if aLIGO: aLIGO_id = keys.index('-')

    # + in network list means that all 2G detectors up to that index are to be
    # taken at A+ sensitivity
    a_pl = int('+' in keys)
    if a_pl: a_pl_id = keys.index('+')

    # v in network list means that all 2G detectors up to that index are to be
    # taken at Voyager sensitivity
    voy = int('v' in keys)
    if voy:
        voy_id = keys.index('v')
        tmp = int(keys[voy_id+1] == 'p')
        voy_pmo = tmp * 'PMO' + (1-tmp) * 'CBO'

    # find out which locations with which PSDs are in the network
    for loc in det_specs_built_in:
        if loc in keys:
            loc_id = keys.index(loc)

            if loc in ('H','L','V','K','I'):
                if aLIGO and loc_id < aLIGO_id:
                    name = 'aLIGO_'+loc
                elif a_pl and loc_id < a_pl_id:
                    if loc == 'V':
                        name = 'V+_'+loc
                    elif loc == 'K':
                        name = 'K+_'+loc
                    else:
                        name = 'A+_'+loc
                elif voy and loc_id < voy_id:
                    name = 'Voyager-{}_{}'.format(voy_pmo,loc)

            elif loc in ('C','N','S'):
                if keys[loc_id+1] == 'c':
                    name = f'CE-{keys[loc_id+2]}0'
                    if   keys[loc_id+2] == 'l': name += '-LF'
                    elif keys[loc_id+2] == 'p': name += '-PM'
                    name += f'_{loc}'
                else:
                    ce_a = int(keys[loc_id+1] == 'a') # 0 for i, 1 for a - CE1 as i, CE2 as a
                    ce_arm = int(keys[loc_id+2])*10  # arm length (n for n*10km)
                    tmp = int(keys[loc_id+3] == 'p')
                    ce_pmo = tmp * 'PMO' + (1-tmp) * 'CBO'
                    name = f'CE{ce_a+1}-{ce_arm}-{ce_pmo}_{loc}'

            det_keys.append(name)

    # add 3 ET detectors
    if 'E' in keys:
        for name in ['ET_ET1','ET_ET2','ET_ET3']:
            det_keys.append(name)

    return det_keys
