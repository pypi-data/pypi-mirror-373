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
from scipy.integrate import simpson

#-----overlap function-------
def scalar_product_integrand(hf, gf, psd):
    '''
    Calculate the integrand of the scalar product given two frequency domain waveforms and the power spectral density.

    Parameters
    ----------
    hf : np.ndarray
        Frequency domain waveform.
    gf : np.ndarray
        Frequency domain waveform.
    psd : np.ndarray
        Power spectral density.

    Returns
    -------
    np.ndarray
        Integrand of the scalar product.
    '''
    return 4 * (hf.real * gf.real + hf.imag * gf.imag) / psd

def scalar_product(hf, gf, psd, freqs):
    """
    Calculate the scalar product given two frequency domain waveforms, the power spectral density, and the frequency array.

    Parameters
    ----------
    hf : np.ndarray
        Frequency domain waveform.
    gf : np.ndarray
        Frequency domain waveform.
    psd : np.ndarray
        Power spectral density.
    freqs : np.ndarray
        Frequency array.

    Returns
    -------
    float
        Scalar product.
    """
    return simpson(scalar_product_integrand(hf, gf, psd), x=freqs)

#-----SNR function-------
def snr_square_integrand(hf, psd):
    """
    Calculate the integrand of the square of the signal-to-noise ratio given a frequency domain waveform and the power spectral density.

    Parameters
    ----------
    hf : np.ndarray
        Frequency domain waveform.
    psd : np.ndarray
        Power spectral density.

    Returns
    -------
    np.ndarray
        Integrand of the square of the signal-to-noise ratio.
    """
    return scalar_product_integrand(hf, hf, psd)

def snr_square(hf, psd, freqs):
    """
    Calculate the square of the signal-to-noise ratio given a frequency domain waveform, the power spectral density, and the frequency array.

    Parameters
    ----------
    hf : np.ndarray
        Frequency domain waveform.
    psd : np.ndarray
        Power spectral density.
    freqs : np.ndarray
        Frequency array.

    Returns
    -------
    float
        Square of the signal-to-noise ratio.
    """
    return scalar_product(hf, hf, psd, freqs)

def snr(hf, psd, freqs):
    """
    Calculate the signal-to-noise ratio given a frequency domain waveform, the power spectral density, and the frequency array.

    Parameters
    ----------
    hf : np.ndarray
        Frequency domain waveform.
    psd : np.ndarray
        Power spectral density.
    freqs : np.ndarray
        Frequency array.

    Returns
    -------
    float
        Signal-to-noise ratio.
    """
    return np.sqrt(snr_square(hf, psd, freqs))

def snr_snr_square(hf, psd, freqs):
    """
    Calculate the signal-to-noise ratio and the square of the signal-to-noise ratio given a frequency domain waveform, the power spectral density, and the frequency array.

    Parameters
    ----------
    hf : np.ndarray
        Frequency domain waveform.
    psd : np.ndarray
        Power spectral density.
    freqs : np.ndarray
        Frequency array.

    Returns
    -------
    float
        Signal-to-noise ratio.
    float
        Square of the signal-to-noise ratio.
    """
    snr_sq = snr_square(hf, psd, freqs)
    return np.sqrt(snr_sq), snr_sq

#-----Cutler Vallisneri bias-----
def cutler_vallisneri_overlap_vec(del_hf, delta_hf, psd, freqs):
    """
    Calculate the Cutler-Vallisneri overlap vector, see Eq. (12) in Cutler and Vallisneri (2007).

    Parameters
    ----------
    del_hf : np.ndarray
        Partial derivatives of the frequency domain waveform.
    delta_hf : np.ndarray
         difference between the detector responses in the frequency domain.
    psd : np.ndarray
        Power spectral density.
    freqs : np.ndarray
        Frequency array.

    Returns
    -------
    np.ndarray
        Cutler-Vallisneri overlap vector.
    """
    return np.array([ scalar_product(del_hf[deriv], delta_hf, psd, freqs) for deriv in del_hf ])

def cutler_vallisneri_bias(cov, overlap_vec):
    """
    Calculate the Cutler-Vallisneri bias given the covariance matrix and the overlap vector, see Eq. (12) in Cutler and Vallisneri (2007).

    Parameters
    ----------
    cov : np.ndarray
        Covariance matrix.
    overlap_vec : np.ndarray
        Overlap vector.

    Returns
    -------
    np.ndarray
        Cutler-Vallisneri bias.
    """
    return np.matmul(cov, overlap_vec)

#-----fft method from Anuradha-------
def rfft_normalized(time_series, dt, n=None):
    """
    Calculate the normalized real-valued discrete Fourier transform of a time series.

    Parameters
    ----------
    time_series : np.ndarray
        Time series.
    dt : float
        Time step.
    n : int, optional
        Number of points in the output.

    Returns
    -------
    np.ndarray
        Normalized real-valued discrete Fourier transform.
    """
    return np.fft.rfft(time_series, n) * dt

def fft_normalized(time_series, dt, n=None):
    """
    Calculate the normalized complex-valued discrete Fourier transform of a time series.

    Parameters
    ----------
    time_series : np.ndarray
        Time series.
    dt : float
        Time step.
    n : int, optional
        Number of points in the output.

    Returns
    -------
    np.ndarray
        Normalized complex-valued discrete Fourier transform.
    """
    return np.fft.fft(time_series, n) * dt
