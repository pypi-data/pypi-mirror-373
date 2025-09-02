#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""spectroscopy.py: graphical reports of Spectroscopy QA."""

import numpy as np
import pandas as pd
from scipy.signal.windows import tukey
from scipy.optimize import curve_fit, fmin
from scipy.fftpack import fft, fftfreq, fftshift
from scipy.integrate import quad

import matplotlib.pyplot as plt

from .. dcmio import (
    spectroscopy_data, dwell_time, t_e, t_r,
    seq_name, larmor_frequency
)


def _autophase(spectrum, p0=0.0, window=None):
    """
    Automatic zero order phase correction value.

    Parameters
    ----------
    spectrum : ndarray
        Array of NMR data.
    p0 : float
        Initial zero order phase in degrees.
    window : int
        Number of points around peak for balance (deflt 5% of spectrum)
    Returns
    -------
    p0:
        Phase corrections in degrees.

    """
    if window is None:
        window = len(spectrum) // 20

    def peak_minima_score(p0, spectrum, window=window):
        """Find simple minima balance around highest peak in real part."""
        r = np.real(spectrum * np.exp(np.radians(p0) * 1j))
        k = np.argmax(r)
        min_left = r[k - window//2:k].min()
        min_right = r[k:k + window//2].min()
        return abs(min_left - min_right)

    return fmin(peak_minima_score, x0=[p0], args=(spectrum, window), disp=False)[0]


def _spectrum_from_fid(z, effective_dwell_time_s, larmor_freq_hz, water_ppm, alpha, phase):
    """
    Reconstruct spectrum from time domain data.

    Parameters
    ----------
    z: ndarray (1d) of complex128
       complex time domain data
    effective_dwell_time_s: float
        time between data samples in seconds
    larmor_freq_hz: float
        proton larmor frequency in Hz
    water_ppm: float
        reference chemical shift to assume for water peak
    alpha:
        scale parameter of tukey apodization filter
    phase: float or None
         phase correction to apply to data, None implies automatic

    Returns
    -------
    tuple (ndarray (1d), ndarray(1d), float)
        spectrum and phase applied

    """
    PPM = 1e-6

    # (1) apodization with tukey window
    nz = len(z)
    z *= tukey(2*nz, alpha)[nz:]

    # (2) zero fill
    z = np.r_[z, np.zeros_like(z)]

    # (3) (complex) fft
    spectrum = fftshift(fft(z))

    # (4) Phase correction: looks pretty well phased already
    if phase is None:
        phase = _autophase(spectrum)
    spectrum *= np.exp(np.radians(phase) * 1j)

    # (5) Rolling background correction: would need areas clear of peaks to do that

    # (6) Frequency scale: adjust to standard scale in ppm using assumed water chemical shift
    frequencies = fftshift(fftfreq(2*nz, d=effective_dwell_time_s)) / larmor_freq_hz / PPM + water_ppm
    return frequencies, spectrum, phase


def _fit_real_gaussian(frequencies, spectrum, window=None):
    """Fit a Gaussian line model to highest peak in given frequency window."""
    # Gaussian model
    def model(x, a, mu, sigma):
        return a * np.exp(-(x - mu)**2 / (2 * sigma**2))

    if window is not None:
        # freq scale is negative but interval given as positive
        f1, f2 = window
        i1, i2 = sorted(np.searchsorted(frequencies, (-f2, -f1)))
        spectrum = spectrum[i1:i2]
        frequencies = frequencies[i1:i2]
    a_0 = spectrum.real.max()
    f_0 = frequencies[spectrum.real.argmax()]
    w_0 = 0.05
    p0 = a_0, f_0, w_0

    popt, _ = curve_fit(
        model,
        frequencies,
        spectrum.real,
        p0=p0
    )
    return popt, model


def _fit_real_lorentzian(frequencies, spectrum, window=None):
    """Fit a Gaussian line model to highest peak in given frequency window."""
    # Assume the peak is Lorentzian - gamma here is HWHM, height is a*gamma
    def model(x, a, mu, gamma):
        return a * gamma / (gamma**2 + (x - mu)**2)

    if window is not None:
        # freq scale is negative but interval given as positive
        f1, f2 = window
        i1, i2 = sorted(np.searchsorted(frequencies, (-f2, -f1)))
        spectrum = spectrum[i1:i2]
        frequencies = frequencies[i1:i2]

    a_0 = spectrum.real.max()
    f_0 = frequencies[spectrum.real.argmax()]
    w_0 = 0.1
    p0 = a_0, f_0, w_0

    popt, _ = curve_fit(
        model,
        frequencies,
        spectrum.real,
        p0=p0
    )
    return popt, model


def svs_report(dobj, water_ppm=-4.89, phase=None):
    """
    Report on SVS acquisition in Siemens Spectroscopy Phantom.

    Spectrum phasing, acetate line shape and width and residual water

    Parameters
    ----------
    dobj: dicom object
        non-image object with time domain data
    water_ppm: float, optional
        reference chemical shift to assume for water peak
    phase: float or None, optional
         phase correction to apply to data, default is automatic

    Returns
    -------
    pandas Dataframe

    """
    # Water ref frequency is normally 4.65-4.7 ppm but at room temp should be about 4.85
    # Siemens seem to use 4.89 so we'll use that by default - not clear this is quite rightt.
    PPM = 1e-6

    larmor_freq_hz = larmor_frequency(dobj) * 1e6
    real_dwell_time_ms = dwell_time(dobj)
    echo_time_ms = t_e(dobj)
    repetition_time_ms = t_r(dobj)
    sequence_name = seq_name(dobj)
    tukey_alpha = 0.5

    # Time domain signal
    # (0) extract complex fid (oversampling already removed?)
    z = spectroscopy_data(dobj)
    nz = len(z)

    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    axs = axs.flat
    ax = axs[0]
    ax.plot(real_dwell_time_ms * np.arange(nz), abs(z) / max(abs(z)), label='Signal', linewidth=1.0)
    ax.plot(real_dwell_time_ms * np.arange(nz), tukey(2*nz, alpha=tukey_alpha)[nz:], label='Window (Tukey)')
    ax.grid(True)
    ax.legend()
    ax.set_xlabel('ms')
    ax.set_ylabel('Normalised Signal')
    ax.set_title('SVS{echo_time_ms:0.0f}/{repetition_time_ms:0.0f} ({sequence_name})'.format(**locals()))

    # Spectrum
    frequencies, spectrum, phase = _spectrum_from_fid(
        z,
        effective_dwell_time_s=real_dwell_time_ms / 1000,
        larmor_freq_hz=larmor_freq_hz,
        water_ppm=water_ppm,
        alpha=tukey_alpha,
        phase=phase
    )

    ax = axs[1]
    ax.plot(-frequencies, spectrum.real)
    ax.set_xlim([5, 0])
    ax.grid(True)
    ax.axvline(-water_ppm, color='C1')

    line_fit_text = 'Phase: {phase:0.2f}'.format(**locals()) + r'$^{o}$'
    ax.text(
        0.1, 0.75,
        line_fit_text,
        bbox=dict(facecolor='none', boxstyle='round', alpha=0.75),
        transform=ax.transAxes
    )

    ax.set_xlabel(r'$\delta$ (ppm)')
    ax.set_ylabel('Signal')
    ax.set_title('Full Spectrum (Real)')

    ax1 = ax.twiny()
    ax1.set_xlim(ax.get_xlim())
    ax1.set_xticks(ax.get_xticks())
    ax1.set_xticklabels([
        "%0.0f" % (-(x + water_ppm) * PPM * larmor_freq_hz)
        for x in ax.get_xticks()
    ])

    # Fit to Acetate -CH3 singlet
    acetate_window = (1.88, 2.08)
    (a, f, w), model = _fit_real_gaussian(frequencies, spectrum, window=acetate_window)

    integral, _ = quad(model, -acetate_window[1], -acetate_window[0], args=(a, f, w))

    centre = -f
    # need \sqrt{8 \ln 2} conversion to work in fwhm rather than sigma
    fwhm = np.sqrt(8 * np.log(2)) * w * PPM * larmor_freq_hz
    height = a
    area = integral * PPM * larmor_freq_hz

    ax = axs[2]
    ax.plot(-frequencies, abs(spectrum), ':', label='Magnitude', alpha=0.75)
    ax.plot(-frequencies, spectrum.real, '-.', label='Real')
    ax.plot(-frequencies, model(frequencies, a, f, w), label='Fit', alpha=0.75)
    ax.set_xlim(reversed(acetate_window))
    ax.grid(True)
    ax.legend()
    line_fit_text = '\n'.join([
        'Acetate:',
        '    Centre = {centre:0.3f} ppm',
        '    FWHM = {fwhm:0.1f} Hz',
        '    Area = {area:0.3g}',
        '    Height = {height:0.3g}'
    ]).format(**locals())
    ax.text(
        0.1, 0.75,
        line_fit_text,
        bbox=dict(facecolor='none', boxstyle='round', alpha=0.75),
        transform=ax.transAxes
    )
    ax.set_xlabel(r'$\delta$ (ppm)')
    ax.set_ylabel('Signal')
    ax.set_title('Acetate')
    ax1 = ax.twiny()
    ax1.set_xlim(ax.get_xlim())
    ax1.set_xticks(ax.get_xticks())
    ax1.set_xticklabels([
        "%0.0f" % (-(x + water_ppm) * PPM * larmor_freq_hz)
        for x in ax.get_xticks()
    ])

    # Residual water
    ax = axs[3]
    ax.plot(-frequencies+water_ppm, spectrum.real, label='Real')
    ax.plot(-frequencies+water_ppm, spectrum.imag, label='Imaginary')
    ax.set_xlim([0.075, -0.075])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel(r'$\delta$ (ppm) wrt Water')
    ax.set_ylabel('Signal')
    ax.set_title('Residual Water')
    ax1 = ax.twiny()
    ax1.set_xlim(ax.get_xlim())
    ax1.set_xticks(ax.get_xticks())
    ax1.set_xticklabels([
        "%0.0f" % (-x * PPM * larmor_freq_hz)
        for x in ax.get_xticks()
    ])

    fig.suptitle('Spectroscopy (SVS) - Metabolite Spectrum', fontsize=16)

    fig.tight_layout()

    return pd.DataFrame.from_dict(
        {sequence_name: ['Acetate', height, fwhm, centre, area]},
        orient='index', columns=['Species', 'Height', 'FWHMHz', 'LocationPPM', 'AreaHz']
    )


def fid_report(dobj, phase=None):
    """
    Report on unsupressed water FID.

    Parameters
    ----------
    dobj: dicom object
        non-image object with time domain data
    phase: float or None, optional
         phase correction to apply to data, default is automatic

    Returns
    -------
    pandas Dataframe


    """
    PPM = 1e-6

    larmor_freq_hz = larmor_frequency(dobj) * 1e6
    real_dwell_time_ms = dwell_time(dobj)
    sequence_name = seq_name(dobj)
    tukey_alpha = 0.5

    # Time domain signal
    # (0) extract complex fid (oversampling already removed?)
    z = spectroscopy_data(dobj)
    nz = len(z)

    fig, axs = plt.subplots(1, 2, figsize=(15, 5))
    axs = axs.flat
    ax = axs[0]
    ax.plot(real_dwell_time_ms * np.arange(nz), abs(z) / max(abs(z)), label='Signal', linewidth=1.0)
    ax.plot(real_dwell_time_ms * np.arange(nz), tukey(2*nz, alpha=tukey_alpha)[nz:], label='Window (Tukey)')
    ax.grid(True)
    ax.legend()
    ax.set_xlabel('ms')
    ax.set_ylabel('Normalised Signal')
    ax.set_title('FID({sequence_name})'.format(**locals()))

    # Spectrum (frequencies in ppm)
    frequencies, spectrum, phase = _spectrum_from_fid(
        z,
        effective_dwell_time_s=real_dwell_time_ms / 1000,
        larmor_freq_hz=larmor_freq_hz,
        water_ppm=0,
        alpha=tukey_alpha,
        phase=phase
    )

    # Fit to water
    water_window = (-0.25, 0.25)

    (a, f, w), model = _fit_real_lorentzian(frequencies, spectrum, window=water_window)
    integral, _ = quad(model, -water_window[1], -water_window[0], args=(a, f, w))

    centre = -f
    # w is hwhm for lorentzian here
    fwhm = 2 * w * PPM * larmor_freq_hz
    area = integral * PPM * larmor_freq_hz
    height = a / w

    ax = axs[1]
    ax.plot(-frequencies, abs(spectrum), ':', label='Magnitude', alpha=0.5)
    ax.plot(-frequencies, spectrum.real, '-.', label='Real')
    ax.plot(-frequencies, model(frequencies, a, f, w), label='Fit', alpha=0.5)
    ax.set_xlim(reversed(water_window))
    ax.grid(True)
    ax.legend()
    line_fit_text = '\n'.join([
        'Water:',
        '    Phase = {phase:0.2f} $^o$',
        '    FWHM = {fwhm:0.1f} Hz',
        '    Area = {area:0.3g}',
        '    Height = {height:0.3g}'
    ]).format(**locals())
    ax.text(
        0.1, 0.75,
        line_fit_text,
        bbox=dict(facecolor='none', boxstyle='round', alpha=0.75),
        transform=ax.transAxes
    )
    ax.set_xlabel(r'$\delta$ (ppm) wrt Nominal Water')
    ax.set_ylabel('Signal')
    ax.set_title('Water')
    ax1 = ax.twiny()
    ax1.set_xlim(ax.get_xlim())
    ax1.set_xticks(ax.get_xticks())
    ax1.set_xticklabels([
        "%0.0f" % (-x * PPM * larmor_freq_hz)
        for x in ax.get_xticks()
    ])

    fig.suptitle('Spectroscopy (FID) - Water Linewidth', fontsize=16)

    fig.tight_layout()

    return pd.DataFrame.from_dict(
        {sequence_name: ['Water', height, fwhm, centre, area]},
        orient='index', columns=['Species', 'Height', 'FWHMHz', 'LocationPPM', 'AreaHz']
    )
