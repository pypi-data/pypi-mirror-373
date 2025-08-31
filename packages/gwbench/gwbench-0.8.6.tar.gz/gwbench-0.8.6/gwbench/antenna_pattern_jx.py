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


from functools import partial

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as np

import gwbench.utils as utils
from gwbench.basic_relations import tau_spa_PN35

cos = np.cos
sin = np.sin
exp = np.exp
log = np.log
pi  = np.pi

i_vec = np.array([1,0,0])
j_vec = np.array([0,1,0])
k_vec = np.array([0,0,1])

def detector_response(hfp, hfc, f, Mc, eta, tc, ra, dec, psi, loc, use_rot, user_locs=None):
    '''
    Calculate the detector response for a given detector location and orientation.

    Parameters
    ----------
    hfp : jnp.ndarray
        The plus polarization.
    hfc : jnp.ndarray
        The cross polarization.
    f : jnp.ndarray
        The frequency domain array [Hz].
    Mc : float
        The chirp Mass [solar mass].
    eta: float
        The symmetric mass ratio.
    tc : float
        The time of coalescence [s].
    dec : float
        The declination [rad].
    ra : float
        The right ascension [rad].
    psi : float
        The polarization angle [rad].
    loc : str
        The location (and implied orientation) of a detector.
    use_rot : bool
        Use frequency dependent time due to rotation of earth and SPA.
    user_locs : dict, optional
        User defined locations and orientations of detectors.

    Returns
    -------
    hf : jnp.ndarray
        The detector response in the frequency domain.
    '''
    Fp, Fc, Flp = antenna_pattern_and_loc_phase_fac(f, Mc, eta, tc, ra, dec, psi, loc, use_rot, user_locs=user_locs)
    return Flp * (Fp * hfp + Fc * hfc)

def antenna_pattern_and_loc_phase_fac(f, Mc, eta, tc, ra, dec, psi, loc, use_rot, user_locs=None):
    '''
    Calculate the antenna pattern and location phase factor for a given detector location and orientation.

    Parameters
    ----------
    f : jnp.ndarray
        The frequency domain [Hz].
    Mc : float
        The chirp Mass [solar mass].
    eta: float
        The symmetric mass ratio.
    tc : float
        The time of coalescence [s].
    dec : float
        The declination [rad].
    ra : float
        The right ascencsion [rad].
    psi : float
        The polarization angle [rad].
    loc : str
        The location (and implied orientation) of a detector.
    use_rot : bool
        Use frequency dependent time due to rotation of earth and SPA.
    user_locs : dict, optional
        User defined locations and orientations of detectors.

    Returns
    -------
    Fp : jnp.ndarray
        The plus polarization antenna pattern.
    Fc : jnp.ndarray
        The cross polarization antenna pattern.
    Flp : jnp.ndarray
        The location phase factor.
    '''
    det_ten, det_vec, period_to_rad = det_quants(loc, user_locs=user_locs)
    time                            = calc_rotating_time(tc, f, Mc, eta, use_rot)
    time_delay                      = calc_time_delay(calc_gra(ra, time, period_to_rad), dec, det_vec)

    return *ant_pat_funcs(det_ten, *ant_pat_vectors(calc_gra(ra, time + time_delay, period_to_rad), dec, psi)), loc_phase_func(f, time_delay)

@partial(jax.jit, static_argnames=['use_rot'])
def calc_rotating_time(tc, f, Mc, eta, use_rot):
    '''
    Calculate the time including the effects of the rotation of the earth
    using the stationary phase approximation, if use_rot is True.

    Parameters
    ----------
    tc : float
        The time of coalescence [s].
    f : jnp.ndarray
        The frequency domain [Hz].
    Mc : float
        The chirp Mass [solar mass
    use_rot : bool
        Include rotation effects.

    Returns
    -------
    time : jnp.ndarray
        The time including rotation effects [s].
    '''
    if use_rot: return tc + utils.tc_offset - tau_spa_PN35(f, Mc, eta, log=log)
    else:       return np.array([tc + utils.tc_offset])

@jax.jit
def calc_gra(ra, time, period_to_rad):
    '''
    Calculate the Greenwich Right Ascension (GRA) for a given detector location and orientation.

    Parameters
    ----------
    ra : float
        The right ascencsion [rad].
    time : jnp.ndarray
        The corrected time [s].

    Returns
    -------
    gra : jnp.ndarray
        The Greenwich Right Ascension [rad].
    '''
    return ra - period_to_rad * time

@jax.jit
def calc_time_delay(gra, dec, det_vec):
    '''
    Calculate the time delay from the geocenter for a given detector location and orientation.

    Parameters
    ----------
    gra : jnp.ndarray
        Greenwich Right Ascension [rad].
    dec : float
        Declination [rad].
    det_vec : jnp.ndarray
        Detector location vector.

    Returns
    -------
    time_delay : jnp.ndarray
        Time delay from the geocenter [s].
    '''
    # using cos/sin(dec) instead of cos/sin(theta) with polar angle (theta = pi/2 - dec)
    return np.matmul(det_vec, np.array([cos(gra)*cos(dec), sin(gra)*cos(dec), sin(dec)*np.ones_like(gra)]))

@jax.jit
def loc_phase_func(f, time_delay):
    '''
    Calculate the location phase factor encoding the phase difference between the signal at the
    detector and the signal at the geocenter.

    Parameters
    ----------
    f : jnp.ndarray
        Frequency domain [Hz].
    time_delay : jnp.ndarray
        The corrected time [s].

    Returns
    -------
    Flp : jnp.ndarray
        Location phase factor
    '''
    return exp(1j * 2*pi * utils.mod_1(f * time_delay, np=np))

@jax.jit
def ant_pat_funcs(det_ten, XX, YY):
    '''
    Calculate the antenna pattern for a given detector location and orientation.

    Parameters
    ----------
    det_ten : jnp.ndarray
        The detector tensor.
    XX : jnp.ndarray
        The x-arm antenna pattern vector.
    YY : jnp.ndarray
        The y-arm antenna pattern vector.

    Returns
    -------
    Fp : jnp.ndarray
        The plus polarization antenna pattern.
    Fc : jnp.ndarray
        The cross polarization antenna pattern.
    '''
    return (0.5 * (np.matmul(det_ten,XX) * XX - np.matmul(det_ten,YY) * YY)).sum(axis=0), \
           (0.5 * (np.matmul(det_ten,XX) * YY + np.matmul(det_ten,YY) * XX)).sum(axis=0)

@jax.jit
def ant_pat_vectors(gra, dec, psi):
    '''
    Calculate the antenna pattern vectors for a given detector location and orientation.

    Parameters
    ----------
    gra : jnp.ndarray
        Greenwich Right Ascension [rad]
    dec : float
        Declination [rad]
    psi : float
        Polarization angle [rad]

    Returns
    -------
    XX : jnp.ndarray
        x-arm antenna pattern vector
    YY : jnp.ndarray
        y-arm antenna pattern vector
    '''
    return np.array([  cos(psi)*sin(gra) - sin(psi)*cos(gra)*sin(dec),
                      -cos(psi)*cos(gra) - sin(psi)*sin(gra)*sin(dec),
                                np.ones_like(gra) * sin(psi)*cos(dec) ]), \
           np.array([ -sin(psi)*sin(gra) - cos(psi)*cos(gra)*sin(dec),
                       sin(psi)*cos(gra) - cos(psi)*sin(gra)*sin(dec),
                                np.ones_like(gra) * cos(psi)*cos(dec) ])

def det_quants(loc, user_locs=None):
    '''
    Calculate the detector tensor, location vector, and period around geocenter for a given detector location and orientation.

    Parameters
    ----------
    loc : str
        Location (and implied orientation) of a detector.
    user_locs : dict, optional
        User defined locations and orientations of detectors.

    Returns
    -------
    det_ten : jnp.ndarray
        Detector tensor.
    det_vec : jnp.ndarray
        Detector location vector.
    period_to_rad : float
        Time to radian conversion factor for the passed period: 2pi/period [rad/s].
    '''
    alpha, beta, gamma, opening_angle, radius, period = utils.det_specs(loc, user_locs=user_locs)
    # insert polar angle theta = pi/2 - beta instead of latitude beta
    EulerD1 = np.matmul(np.matmul(rot_mat_2(alpha), rot_mat_1(pi/2 - beta)), rot_mat_2(gamma))

    eDArm1 = np.matmul(EulerD1, i_vec)
    eDArm2 = np.matmul(EulerD1, (cos(opening_angle) * i_vec + sin(opening_angle) * j_vec))

    return np.outer(eDArm1,eDArm1) - np.outer(eDArm2,eDArm2), -radius / utils.cLight * np.matmul(EulerD1, k_vec), 2*np.pi / period

@jax.jit
def rot_mat_1(angle):
    '''
    Calculate the rotation matrix for a given angle around axis 1.

    Parameters
    ----------
    angle : float
        Rotation angle [rad]

    Returns
    -------
    rot : jnp.ndarray
        Rotation matrix
    '''
    c = np.cos(angle)
    s = np.sin(angle)
    return np.array( [ [c,0,s], [0,1,0], [-s,0,c] ] )

@jax.jit
def rot_mat_2(angle):
    '''
    Calculate the rotation matrix for a given angle around axis 2.

    Parameters
    ----------
    angle : float
        Rotation angle [rad]

    Returns
    -------
    rot : jnp.ndarray
        Rotation matrix
    '''
    c = np.cos(angle)
    s = np.sin(angle)
    return np.array( [ [c,-s,0], [s,c,0], [0,0,1] ] )
