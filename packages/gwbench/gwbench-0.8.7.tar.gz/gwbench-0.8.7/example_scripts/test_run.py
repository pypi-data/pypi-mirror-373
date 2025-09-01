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
from gwbench import Network, M_of_Mc_eta, f_isco_Msolar

#import gwbench
#gwbench.utils.tc_offset = 0

############################################################################
### settings
############################################################################

# choose which parameters to take partial derivatives for Fisher analysis
deriv_symbs_string  = 'Mc eta chi1z chi2z DL tc phic iota ra dec psi'
# choose which parameters to convert to cos (None) or log versions
conv_log            = ('Mc','DL')
# choose whether to take Earth's rotation into account
use_rot             = True
# choose whether to perform the Fisher analysis only at the network level
only_net            = True

############################################################################
### injection parameters and frequency array
############################################################################

# set the injection parameters
inj_params = {
    'Mc'    : 42.92123785996995,
    'eta'   : 0.2179560548922493,
    'chi1x' : 0.0,
    'chi1y' : 0.0,
    'chi1z' : -0.5291825652680437,
    'chi2x' : 0.0,
    'chi2y' : 0.0,
    'chi2z' : -0.5533273077110299,
    'DL'    : 595.845227743203,
    'tc'    : 0.0,
    'phic'  : 0.0,
    'iota'  : 0.2367522187410996,
    'ra'    : 4.043179805492967,
    'dec'   : 1.1829476432948405,
    'psi'   : 3.277322349164817,
    }

print('injections parameter: ', inj_params)
print()

# pick the desired frequency range
f_lo = 1.
f_hi = f_isco_Msolar(M_of_Mc_eta(inj_params['Mc'],inj_params['eta']))
df   = 2.**-4
f    = np.arange(f_lo,f_hi+df,df)

print('f_lo:', f_lo, '   f_hi:', f_hi, '   df:', df)
print()

############################################################################
### Network specification
############################################################################

# choose the desired detectors
network_spec = ['CE2-40-CBO_C','CE2-40-CBO_N','CE2-40-CBO_S']
print('network spec: ', network_spec)
print()

############################################################################
### GW Benchmarking
############################################################################

# initialize the network with the desired detectors
nnet = Network(network_spec, logger_name='3_40km_CE', logger_level='INFO')
# pass all variables to the network
nnet.set_net_vars(wf_model_name='tf2', f=f, inj_params=inj_params,
                  deriv_symbs_string=deriv_symbs_string, conv_log=conv_log, use_rot=use_rot)

# calculate the network and detector Fisher matrices, condition numbers,
# covariance matrices, error estimates (including 90%-credible sky area
# in deg), and inversion errors using numeric differentiation mehtod
nnet.calc_errors(only_net=only_net, derivs='num', step=1e-6, method='central', order=2)

############################################################################
### Check results
############################################################################

# stored from previous evaluation for tf2 waveform and inj_id=0
snr  = 2598
errs = {
    'log_Mc'      : 0.001897,
    'eta'         : 0.079625,
    'chi1z'       : 1.372351,
    'chi2z'       : 2.040251,
    'log_DL'      : 0.036080,
    'tc'          : 0.005855,
    'phic'        : 16.26113,
    'iota'        : 0.149146,
    'ra'          : 0.001219,
    'dec'         : 0.000656,
    'psi'         : 0.664313,
    'sky_area_90' : 0.010985,
    }

rtol = 1e-2
atol = 0
print(f'\nCheck if calculated and stored values agree up to a relative error of {rtol}.')
print(f'{"Network SNR".ljust(19)} calculated={str(nnet.snr).ljust(20)}   stored={str(snr).ljust(18)} agree={np.isclose(nnet.snr, snr, atol=atol, rtol=rtol)}.')
for key in errs:
    cval = nnet.errs[key]
    sval = errs[key]
    print(f'Error {key.ljust(13)} calculated={str(cval).ljust(22)} stored={str(sval).ljust(18)} agree={np.isclose(cval, sval, atol=atol, rtol=rtol)}.')
print()

############################################################################
### Check against jax method
############################################################################

# initialize the network with the desired detectors
jnet = Network(network_spec, logger_name='3_40km_CE', logger_level='INFO')
# pass all variables to the network
jnet.set_net_vars(wf_model_name='tf2_jx', f=f, inj_params=inj_params,
                  deriv_symbs_string=deriv_symbs_string, conv_log=conv_log, use_rot=use_rot)

# calculate the network and detector Fisher matrices, condition numbers,
# covariance matrices, error estimates (including 90%-credible sky area
# in deg), and inversion errors using numeric jax differentiation mehtod
jnet.calc_errors(only_net=only_net, derivs='num')

rtol = 5e-2
print(f'\nCheck if numericly calculated (numdifftools vs jax) errors agree up to a relative error of {rtol}.')
for key in errs:
    sval = nnet.errs[key]
    cval = jnet.errs[key]
    print(f'Error {key.ljust(13)}    numdifftools={str(sval).ljust(22)} jax={str(cval).ljust(22)} agree={np.isclose(cval, sval, atol=atol, rtol=rtol)}.')
print()

############################################################################
### Check against symbolic method
############################################################################

# initialize the network with the desired detectors
snet = Network(network_spec, logger_name='3_40km_CE', logger_level='INFO')
# pass all variables to the network
snet.set_net_vars(wf_model_name='tf2', f=f, inj_params=inj_params,
                  deriv_symbs_string=deriv_symbs_string, conv_log=conv_log, use_rot=use_rot)

# calculate the network and detector Fisher matrices, condition numbers,
# covariance matrices, error estimates (including 90%-credible sky area
# in deg), and inversion errors using symbolic differentiation mehtod
snet.calc_errors(only_net=only_net, derivs='sym', gen_derivs=True)

rtol = 5e-2
print(f'\nCheck if numericly and symbolicly calculated errors agree up to a relative error of {rtol}.')
for key in errs:
    sval = nnet.errs[key]
    cval = snet.errs[key]
    print(f'Error {key.ljust(13)}    numeric={str(sval).ljust(22)} symbolic={str(cval).ljust(22)} agree={np.isclose(cval, sval, atol=atol, rtol=rtol)}.')
