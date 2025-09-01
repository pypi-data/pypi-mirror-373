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


import numpy as np
import sympy as sp

import gwbench.utils as utils
from gwbench.antenna_pattern_np import ap_symbs_string
from gwbench.basic_relations import tau_spa_PN35

cos = sp.cos
sin = sp.sin
exp = sp.exp
log = sp.log
pi  = np.pi

i_vec = sp.Matrix([1,0,0])
j_vec = sp.Matrix([0,1,0])
k_vec = sp.Matrix([0,0,1])

f, Mc, eta, tc, ra, dec, psi = sp.symbols(ap_symbs_string, real=True)

def detector_response(hfp, hfc, loc, use_rot, user_locs=None):
    '''
    Calculate the sympy expression of the detector response for a given detector location and orientation.

    Parameters
    ----------
    hfp : sympy expression
        The plus polarization.
    hfc : sympy expression
        The cross polarization.
    loc : str
        The location (and implied orientation) of a detector.
    use_rot : bool
        Use frequency dependent time due to rotation of earth and SPA.
    user_locs : dict, optional
        User defined locations and orientations of detectors.

    Returns
    -------
    hf : sympy expression
        The detector response in the frequency domain.
    '''
    Fp, Fc, Flp = antenna_pattern_and_loc_phase_fac(loc, use_rot, user_locs=user_locs)
    return Flp * (Fp * hfp + Fc * hfc)

def antenna_pattern_and_loc_phase_fac(loc, use_rot, user_locs=None):
    '''
    Calculate the sympy expression of the antenna pattern and location phase factor for a given detector location and orientation.

    Parameters
    ----------
    loc : str
        location (and implied orientation) of a detector
    use_rot : bool
        use frequency dependent time due to rotation of earth and SPA
    user_locs : dict, optional
        user defined locations and orientations of detectors

    Returns
    -------
    Fp : sympy expression
        The plus polarization antenna pattern.
    Fc : sympy expression
        The cross polarization antenna pattern.
    Flp : sympy expression
        The location phase factor.
    '''
    det_ten, det_vec, period_to_rad = det_quants(loc, user_locs=user_locs)
    time                            = calc_rotating_time(tc, f, Mc, eta, use_rot)
    time_delay                      = calc_time_delay(calc_gra(ra, time, period_to_rad), dec, det_vec)

    return *ant_pat_funcs(det_ten, *ant_pat_vectors(calc_gra(ra, time + time_delay, period_to_rad), dec, psi)), loc_phase_func(f, time_delay)

def calc_rotating_time(tc, f, Mc, eta, use_rot):
    '''
    Calculate the sympy expression of the time including the effects of the rotation of the earth
    using the stationary phase approximation, if use_rot is True.

    Parameters
    ----------
    tc : symbol
        The time of coalescence [s].
    f : symbol
        The frequency domain [Hz].
    Mc : symbol
        The chirp Mass [solar mass
    use_rot : bool
        Include rotation effects.

    Returns
    -------
    time : sympy expression
        The time including rotation effects [s].
    '''
    if use_rot: return tc + utils.tc_offset - tau_spa_PN35(f, Mc, eta, log=log)
    else:       return tc + utils.tc_offset

def calc_gra(ra, time, period_to_rad):
    '''
    Calculate the sympy expression of the Greenwich Right Ascension (GRA) for a given detector location and orientation.

    Parameters
    ----------
    ra : symbol
        The right ascencsion [rad].
    time : sympy expression
        The corrected time [s].

    Returns
    -------
    gra : sympy expression
        The Greenwich Right Ascension [rad].
    '''
    return ra - period_to_rad * time

def calc_time_delay(gra, dec, det_vec):
    '''
    Calculate the sympy expression of the time delay from the geocenter for a given detector location and orientation.

    Parameters
    ----------
    gra : sympy expression
        Greenwich Right Ascension [rad].
    dec : symbol
        Declination [rad].
    det_vec : sympy expression
        Detector location vector.

    Returns
    -------
    time_delay : sympy expression
        Time delay from the geocenter [s].
    '''
    # using cos/sin(dec) instead of cos/sin(theta) with polar angle (theta = pi/2 - dec)
    return (det_vec.T*sp.Matrix([cos(gra)*cos(dec), sin(gra)*cos(dec), sin(dec)]))[0,0]

def loc_phase_func(f, time_delay):
    '''
    Calculate the sympy expression of the location phase factor encoding the phase difference between the signal at the
    detector and the signal at the geocenter.

    Parameters
    ----------
    f : symbol
        Frequency domain [Hz].
    time_delay : sympy expression
        The corrected time [s].

    Returns
    -------
    Flp : sympy expression
        Location phase factor
    '''
    return exp(1j * 2*pi*f * time_delay)

def ant_pat_funcs(det_ten, XX, YY):
    '''
    Calculate the sympy expression of the antenna pattern for a given detector location and orientation.

    Parameters
    ----------
    det_ten : sympy expression
        The detector tensor.
    XX : sympy expression
        The x-arm antenna pattern vector.
    YY : sympy expression
        The y-arm antenna pattern vector.

    Returns
    -------
    Fp : sympy expression
        The plus polarization antenna pattern.
    Fc : sympy expression
        The cross polarization antenna pattern.
    '''
    return (0.5 * (XX.T*det_ten*XX - YY.T*det_ten*YY))[0,0], \
           (0.5 * (XX.T*det_ten*YY + YY.T*det_ten*XX))[0,0]

def ant_pat_vectors(gra, dec, psi):
    '''
    Calculate the sympy expression of the antenna pattern vectors for a given detector location and orientation.

    Parameters
    ----------
    gra : sympy expression
        Greenwich Right Ascension [rad]
    dec : symbol
        Declination [rad]
    psi : symbol
        Polarization angle [rad]

    Returns
    -------
    XX : sympy expression
        x-arm antenna pattern vector
    YY : sympy expression
        y-arm antenna pattern vector
    '''
    return sp.Matrix([  cos(psi)*sin(gra) - sin(psi)*cos(gra)*sin(dec),
                       -cos(psi)*cos(gra) - sin(psi)*sin(gra)*sin(dec),
                                                     sin(psi)*cos(dec) ]), \
           sp.Matrix([ -sin(psi)*sin(gra) - cos(psi)*cos(gra)*sin(dec),
                        sin(psi)*cos(gra) - cos(psi)*sin(gra)*sin(dec),
                                                     cos(psi)*cos(dec) ])

def det_quants(loc, user_locs=None):
    '''
    Calculate the sympy expression of the detector tensor and location vector for a given detector location and orientation.

    Parameters
    ----------
    loc : str
        Location (and implied orientation) of a detector.
    user_locs : dict, optional
        User defined locations and orientations of detectors.

    Returns
    -------
    det_ten : sympy expression
        Detector tensor.
    det_vec : sympy expression
        Detector location vector.
    period_to_rad : float
        Time to radian conversion factor for the passed period: 2pi/period [rad/s].
    '''
    alpha, beta, gamma, opening_angle, radius, period = utils.det_specs(loc, user_locs=user_locs)
    # insert polar angle theta = pi/2 - beta instead of latitude beta
    EulerD1 = rot_mat_2(alpha) * rot_mat_1(pi/2 - beta) * rot_mat_2(gamma)

    eDArm1 = EulerD1 * i_vec
    eDArm2 = EulerD1 * (np.cos(opening_angle) * i_vec + np.sin(opening_angle) * j_vec)

    return eDArm1*eDArm1.T - eDArm2*eDArm2.T, -radius / utils.cLight * EulerD1*k_vec, 2 * np.pi / period

def rot_mat_1(angle):
    '''
    Calculate the sympy expression of the rotation matrix for a given angle around axis 1.

    Parameters
    ----------
    angle : float
        Rotation angle [rad]

    Returns
    -------
    rot : sympy matrix
        Rotation matrix
    '''
    c = np.cos(angle)
    s = np.sin(angle)
    return sp.Matrix( [ [c,0,s], [0,1,0], [-s,0,c] ] )

def rot_mat_2(angle):
    '''
    Calculate the sympy expression of the rotation matrix for a given angle around axis 2.

    Parameters
    ----------
    angle : float
        Rotation angle [rad]

    Returns
    -------
    rot : sympy matrix
        Rotation matrix
    '''
    c = np.cos(angle)
    s = np.sin(angle)
    return sp.Matrix( [ [c,-s,0], [s,c,0], [0,0,1] ] )
