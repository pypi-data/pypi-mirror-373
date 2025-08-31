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


import os

import scipy.interpolate as si
from numpy import power, inf, pi, exp, tanh, cos, sin, square, ones_like
from pandas import read_csv

from gwbench.utils import cLight, min_max_mask, log_msg

noise_curves_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'noise_curves')

def psd(tec, f, f_lo=-inf, f_hi=inf, psd_file=None, is_asd=None):
    '''
    Calculate the power spectral density (PSD) for a given detector or analytical PSDs specified by tec
    given a frequency array f, and the low and high frequency cutoffs f_lo and f_hi. If a psd_file is handed over,
    the PSD is read from that file. If is_asd is True, the ASD is returned instead of the PSD.

    Parameters
    ----------
    tec : str
        The name of the detector or the analytical PSD.
    f : array
        The frequency array.
    f_lo : float
        The low frequency cutoff.
    f_hi : float
        The high frequency cutoff.
    psd_file : str
        The name of the file containing the PSD.
    is_asd : bool
        If True, the ASD is returned instead of the PSD.

    Returns
    -------
    np.ndarray
        The PSD.
    np.ndarray
        The frequency array.
    '''
    if psd_file is not None and is_asd is not None:
        # user-specified PSD file and ASD flag
        fname       = psd_file
        asd         = float(is_asd)

    elif tec in noise_curves_built_in:
        # built-in noise curves
        tec_spec    = noise_curves_built_in[tec]

        if len(tec_spec) == 2:
            # tabulated noise curve
            fname   = tec_spec[0]
            asd     = float(tec_spec[1])
        else:
            # analytical noise curve
            fname   = None
            _f_lo   = max(tec_spec[0], f_lo)
            _f_hi   = min(tec_spec[1], f_hi)
            _func   = tec_spec[2]

    else:
        # neither a built-in noise curve nor a user-specified PSD file
        log_msg(f'psd: Either provide both, psd_file and is_asd, or specify a tec from {list(noise_curves_built_in.keys())}.', 'ERROR')

    if fname is not None:
        # read the PSD data from the file
        psd_data    = read_csv(os.path.join(noise_curves_path, fname), sep = None, header = None, engine = 'python', comment = '#').to_numpy()
        # find correct limits: file vs user-set limits
        _f_lo       = max(psd_data[0,0],  f_lo)
        _f_hi       = min(psd_data[-1,0], f_hi)
        # interpolate the PSD data
        _func       = si.interp1d(psd_data[:,0], psd_data[:,1]**(1+asd))

    # check if low and high frequency cutoffs are within the frequency array
    check_f(tec, f, _f_lo, _f_hi)
    # create a mask for the frequency array based on the low and high frequency cutoffs
    mask = min_max_mask(f, _f_lo, _f_hi)
    # return the PSD and corresponding freq array
    return _func(f[mask]), f[mask]

def check_f(tec, f, f_lo, f_hi):
    if f[-1] < f_lo: raise log_msg(f'psd: The maximum frequency {f[-1]} is below the low-frequency cutoff {f_lo} of the PSD {tec}.', 'ERROR')
    if f[0]  > f_hi: raise log_msg(f'psd: The minimum frequency {f[0]} is above the high-frequency cutoff {f_hi} of the PSD {tec}.', 'ERROR')

def psd_aLIGO(f):
    x = f/245.4
    return 1.e-48 * ( 0.0152 * power(x,-4.) + 0.2935 * power(x,9./4) +
                2.7951 * power(x,3./2) - 6.5080 * power(x,3./4) + 17.7622 )

def psd_CEwb(f):
    return 5.623746655206207e-51 + 6.698419551167371e-50 * power(f,-0.125) + 7.805894950092525e-31 * power(f,-20.) + 4.35400984981997e-43 * power(f,-6.) \
            + 1.630362085130558e-53 * f + 2.445543127695837e-56 * square(f) + 5.456680257125753e-66 * power(f,5)

def psd_LISA_17(f):
    a1 = 8.2047564e-33
    a2 = 3.0292821e-38
    a3 = 1.4990886e-39
    a4 = 1.0216062e-40
    return a1 * (f/10**-4)**-6 + 0.8 * a2 * (f/(10**-3))**-4 + a3 * (f/0.1)**2 + a4

def psd_LISA_Babak17(f):
    L     = 2.5e9
    SnLoc = 2.89e-24
    SnSN  = 7.92e-23
    SnOmn = 4.00e-24
    SnAcc = (9.e-30 + 3.24e-28 * ((3.e-5/f)**10 + (1.e-4/f)**2)) * (2.*pi*f)**-4
    SGal  = 3.266e-44 * f**(-7./3.) * exp(-(f/1.426e-3)**1.183) * 0.5 * (1. + tanh(-(f-2.412e-3)/4.835e-3))
    return SGal + 20./3. * (4 * SnAcc + 2 * SnLoc + SnSN + SnOmn)/L**2 * (1 + (( 2*L*f / (0.41*cLight))**2 ))

def psd_LISA_Robson18(f,curve):
    L     = 2.5e9
    fstar = 19.09e-3
    Poms  = (1.5e-11)**2 * (1. + (2.e-3/f)**4)
    Pacc  = (3.e-15)**2  * (1. + (0.4e-3/f)**2) * (1. + (f/8.e-3)**4)

    if curve == 0:
        Snoc =  10./(3. * L**2) * (Poms + 4./(2. * pi * f)**4 * Pacc)                         * (1. + 0.6 * (f/fstar)**2)
        return  10./(3. * L**2) * (Poms + 2./(2. * pi * f)**4 * (1. + cos(f/fstar)**2) * Pacc) * (1. + 0.6 * (f/fstar)**2)
    else:
        if curve == 1:
            alpha = 0.133
            beta  = 243.
            kappa = 482.
            gamma = 917.
            fk    = 0.00258
        elif curve == 2:
            alpha = 0.171
            beta  = 292.
            kappa = 1020.
            gamma = 1680.
            fk    = 0.00215
        elif curve == 3:
            alpha = 0.165
            beta  = 299.
            kappa = 611.
            gamma = 1340.
            fk    = 0.00173
        elif curve == 4:
            alpha = 0.138
            beta  = -221.
            kappa = 521.
            gamma = 1680.
            fk    = 0.00113
        Snoc =  10./(3. * L**2) * (Poms + 4./(2. * pi * f)**4 * Pacc) * (1. + 0.6 * (f/fstar)**2)
        Sc   = 9.e-45 * f**(-7./3.) * exp(-f**alpha + beta * f * sin(kappa * f)) * (1. + tanh(gamma * (fk - f)))
        return Snoc + Sc

noise_curves_built_in = {
    ### analytical noise curves
    'tec'               : [1.e-7, 1.e5, lambda x: 1.e-60 * ones_like(x)], # dummy psd for testing purposes
    'aLIGO'             : [10., 2048., psd_aLIGO],
    'CEwb'              : [5., 2048., psd_CEwb],
    'LISA-17'           : [-inf, inf, psd_LISA_17],
    'LISA-Babak17'      : [-inf, inf, psd_LISA_Babak17],
    'LISA-Robson18-gen' : [-inf, inf, lambda x: psd_LISA_Robson18(x, 0)],
    'LISA-Robson18-6mo' : [-inf, inf, lambda x: psd_LISA_Robson18(x, 1)],
    'LISA-Robson18-1yr' : [-inf, inf, lambda x: psd_LISA_Robson18(x, 2)],
    'LISA-Robson18-2yr' : [-inf, inf, lambda x: psd_LISA_Robson18(x, 3)],
    'LISA-Robson18-4yr' : [-inf, inf, lambda x: psd_LISA_Robson18(x, 4)],
    ### tabulated noise curves
    # current Cosmic Explorer curves, see https://dcc.cosmicexplorer.org/CE-T2000017/public
    'CE-40'             : ['cosmic_explorer_40km.txt', True],
    'CE-40-LF'          : ['cosmic_explorer_40km_lf.txt', True],
    'CE-20'             : ['cosmic_explorer_20km.txt', True],
    'CE-20-PM'          : ['cosmic_explorer_20km_pm.txt', True],
    # https://apps.et-gw.eu/tds/?content=3&r=18213 --> 1st (frequencies) and 4th (xylophone PSD) columns of ET10kmcolumns.txt
    'ET-10-XYL'         : ['et_10km_xylophone.txt', False],
    # https://dcc.ligo.org/LIGO-T2300041-v1/public
    'A#'                : ['a_sharp.txt', True],
    # curves used in the trade study for the Cosmic Explorer Horizon Study, see https://dcc.cosmicexplorer.org/CE-T2000007/public
    'A+'                : ['a_plus.txt', True],
    'V+'                : ['advirgo_plus.txt', True],
    'K+'                : ['kagra_plus.txt', True],
    'Voyager-CBO'       : ['voyager_cb.txt', True],
    'Voyager-PMO'       : ['voyager_pm.txt', True],
    'ET'                : ['et.txt', True],
    'CE1-10-CBO'        : ['ce1_10km_cb.txt', True],
    'CE1-20-CBO'        : ['ce1_20km_cb.txt', True],
    'CE1-30-CBO'        : ['ce1_30km_cb.txt', True],
    'CE1-40-CBO'        : ['ce1_40km_cb.txt', True],
    'CE2-10-CBO'        : ['ce2_10km_cb.txt', True],
    'CE2-20-CBO'        : ['ce2_20km_cb.txt', True],
    'CE2-30-CBO'        : ['ce2_30km_cb.txt', True],
    'CE2-40-CBO'        : ['ce2_40km_cb.txt', True],
    'CE1-10-PMO'        : ['ce1_10km_pm.txt', True],
    'CE1-20-PMO'        : ['ce1_20km_pm.txt', True],
    'CE1-30-PMO'        : ['ce1_30km_pm.txt', True],
    'CE1-40-PMO'        : ['ce1_40km_pm.txt', True],
    'CE2-10-PMO'        : ['ce2_10km_pm.txt', True],
    'CE2-20-PMO'        : ['ce2_20km_pm.txt', True],
    'CE2-30-PMO'        : ['ce2_30km_pm.txt', True],
    'CE2-40-PMO'        : ['ce2_40km_pm.txt', True],
    }
