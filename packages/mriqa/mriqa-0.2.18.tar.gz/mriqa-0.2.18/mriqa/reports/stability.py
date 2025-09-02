# -*- coding: utf-8 -*-
"""stability.py: graphical reports of fbirn QA parameters."""

import numpy as np
from scipy.ndimage import shift

import matplotlib.pyplot as plt
import pandas as pd

from .. fbirn import (
    roi_means_time_course, signal_image, signal_summary,
    snr_summary, sfnr_summary, fluctuation_and_drift,
    ghostiness_trends, magnitude_spectrum, weisskoff,
    fwhm_smoothness_xyz_preprocessed, centre_of_mass,
    static_spatial_noise_image, temporalnoise_fluct_image,
    sfnr_image, dicom_objs_sorted_on_time, time_series_generic
)


def fbirn_short_report(dobjs, maxtimes=1_000_000):
    """
    Abbreviated form of fbirn QA report for quarterly QA.
    """
    # might be a mosaic, an object per-slice or a multiframe
    dobjs = dicom_objs_sorted_on_time(dobjs)
    time_series, (dx, dy, dz, dt) = time_series_generic(dobjs, maxtimes)
    nt, nz, ny, nx = time_series.shape

    scanner = dobjs[0].StationName
    date = dobjs[0].AcquisitionDate if 'AcquisitionDate' in dobjs[0] else dobjs[0].AcquisitionDateTime[:8]

    assert nx > 0 and ny > 0 and nz > 0 and nt > 0
    assert dx > 0 and dy > 0 and (dz > 0 or nz == 1) and dt > 0

    tstart = 2 + nt % 2
    zmiddle = nz // 2
    central_slice_time_series = time_series[tstart:, zmiddle, :, :]

    # Time course of gain fluctuations in an ROI
    roisize = 15

    time_course = roi_means_time_course(central_slice_time_series, roisize=roisize)
    nt = len(time_course)
    (a, b, c) = np.polyfit(range(nt), time_course, deg=2)
    trend = np.polyval((a, b, c), range(nt))

    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    axs = axs.flat

    # Average Image
    im = axs[0].imshow(signal_image(central_slice_time_series), cmap='viridis')
    axs[0].axis('off')
    axs[0].set_title(
        'Signal Image [ROI = %0.1f]' % signal_summary(central_slice_time_series, roisize=roisize)
    )
    fig.colorbar(im, ax=axs[0])

    # Show the region of interest to be used
    x1, x2, y1, y2 = int(nx/2-roisize/2), int(nx/2+roisize/2), int(ny/2-roisize/2), int(ny/2+roisize/2)
    axs[0].axhline(y=y1, xmin=(x1+0.5)/nx,    xmax=(x2+0.5)/nx,    color='y')
    axs[0].axvline(x=x1, ymin=(ny-y1-0.5)/ny, ymax=(ny-y2-0.5)/ny, color='y')
    axs[0].axhline(y=y2, xmin=(x1+0.5)/nx,    xmax=(x2+0.5)/nx,    color='y')
    axs[0].axvline(x=x2, ymin=(ny-y1-0.5)/ny, ymax=(ny-y2-0.5)/ny, color='y')

    # Time course of gain fluctuations in an ROI
    axs[1].plot(np.arange(nt), time_course, '+-', label='observed')
    axs[1].plot(np.arange(nt), trend, '-', label='fit')
    sd, fluct, drift_raw, drift_fit = fluctuation_and_drift(
                                  central_slice_time_series, roisize=roisize)
    axs[1].set_title('[%%fluct, drift, driftfit] = [%.2f %.2f %.2f]' % (fluct, drift_raw, drift_fit))
    axs[1].set_xlabel('Frame Number')
    axs[1].set_ylabel('Raw Signal (ROI)')
    axs[1].grid(True)
    axs[1].legend()

    # Average strength of ghosts and of the 'brightest' ghosts
    pmeans, gmeans, bright_gmeans, snrs = ghostiness_trends(time_series)
    axs[2].plot(range(1, len(gmeans)+1), 100*gmeans/pmeans, '-', label='Ghosts')
    axs[2].plot(range(1, len(bright_gmeans)+1), 100*bright_gmeans/pmeans, '-', label='Bright Ghosts')

    axs[2].set_title('Ghostiness')
    axs[2].set_xlabel('Frame No')
    axs[2].set_ylabel('Relative Intensity (%)')
    axs[2].grid(True)
    axs[2].legend()

    # Magnitude spectrum of temporal fluctuations in an ROI
    spectrum = magnitude_spectrum(central_slice_time_series, roisize=roisize)
    nf = len(spectrum)
    frequencies = np.linspace(0, (nf-1.0)/dt/nf/2.0, num=nf)
    # df = 1 / dt

    axs[3].plot(frequencies, spectrum, '-')
    mean, snr, sfnr = (
        signal_summary(central_slice_time_series, roisize=roisize),
        snr_summary(central_slice_time_series, roisize=roisize),
        sfnr_summary(central_slice_time_series, roisize=roisize)
    )

    axs[3].set_title('[Mean, SNR, SFNR] = [%.1f %.1f %.1f]' % (mean, snr, sfnr))
    axs[3].set_xlabel('Frequency (Hz)')
    axs[3].set_ylabel('Magnitude Spectrum (mean scaled)')
    axs[3].grid(True)

    fig.suptitle('fBIRN Stability for %s on %s' % (scanner, date), fontsize=20)

    return pd.DataFrame(
        [(fluct, drift_fit, np.mean(100*gmeans/pmeans), np.mean(100*bright_gmeans/pmeans), mean, snr, sfnr)],
        columns=['Fluctuations', 'FittedDrift', 'Ghosts', 'BrightGhosts', 'SignalMean', 'SNR', 'SFNR'],
        index=["%s_%s" % (scanner, date)]
    )


def fbirn_full_report(dobjs, maxtimes=1_000_000, correct_drift=False):
    """
    Full fbirn QA report for fMRI Stability QA and Annual Report.
    """
    # might be a mosaic, an object per-slice or a multiframe
    dobjs = dicom_objs_sorted_on_time(dobjs)
    time_series, (dx, dy, dz, dt) = time_series_generic(dobjs, maxtimes)
    nt, nz, ny, nx = time_series.shape

    scanner = dobjs[0].StationName
    date = dobjs[0].AcquisitionDate if 'AcquisitionDate' in dobjs[0] else dobjs[0].AcquisitionDateTime[:8]

    assert nx > 0 and ny > 0 and nz > 0 and nt > 0
    assert dx > 0 and dy > 0 and (dz > 0 or nz == 1) and dt > 0

    tstart = 2 + nt % 2
    zmiddle = nz // 2
    central_slice_time_series = time_series[tstart:, zmiddle, :, :]

    # Time course of gain fluctuations in an ROI
    roisize = 15

    time_course = roi_means_time_course(central_slice_time_series, roisize=roisize)
    nt = len(time_course)
    (a, b, c) = np.polyfit(range(nt), time_course, deg=2)
    trend = np.polyval((a, b, c), range(nt))

    fig = plt.figure(figsize=(15, 12))

    axs = []
    for row in range(2):
        axs.append(plt.subplot2grid((3, 12), (row, 0), colspan=4))
        axs.append(plt.subplot2grid((3, 12), (row, 4), colspan=4))
        axs.append(plt.subplot2grid((3, 12), (row, 8), colspan=4))

    axs.append(plt.subplot2grid((3, 12), (2, 0), colspan=3))
    axs.append(plt.subplot2grid((3, 12), (2, 3), colspan=3))
    axs.append(plt.subplot2grid((3, 12), (2, 6), colspan=3))
    axs.append(plt.subplot2grid((3, 12), (2, 9), colspan=3))

    # Time course of gain fluctuations in an ROI
    axs[0].plot(np.arange(nt), time_course, '+-', label='observed')
    axs[0].plot(np.arange(nt), trend, '-', label='fit')
    sd, fluct, drift_raw, drift_fit = fluctuation_and_drift(
                                  central_slice_time_series, roisize=roisize)
    axs[0].set_title('[%%fluct, drift, driftfit] = [%.2f %.2f %.2f]' % (fluct, drift_raw, drift_fit))
    axs[0].set_xlabel('Frame Number')
    axs[0].set_ylabel('Raw Signal (ROI)')
    axs[0].grid(True)
    axs[0].legend()

    # Magnitude spectrum of temporal fluctuations in an ROI
    spectrum = magnitude_spectrum(central_slice_time_series, roisize=roisize)
    nf = len(spectrum)
    frequencies = np.linspace(0, (nf-1.0)/dt/nf/2.0, num=nf)
    # df = 1 / dt

    axs[1].plot(frequencies, spectrum, '-')
    mean, snr, sfnr = (
        signal_summary(central_slice_time_series, roisize=roisize),
        snr_summary(central_slice_time_series, roisize=roisize),
        sfnr_summary(central_slice_time_series, roisize=roisize)
    )

    axs[1].set_title('[Mean, SNR, SFNR] = [%.1f %.1f %.1f]' % (mean, snr, sfnr))
    axs[1].set_xlabel('Frequency (Hz)')
    axs[1].set_ylabel('Magnitude Spectrum (mean scaled)')
    axs[1].grid(True)

    # Weisskoff plot of fluctuation noise as a function of ROI size
    roc, covs = weisskoff(central_slice_time_series, max_roisize=roisize)

    axs[2].loglog(range(1, len(covs)+1), 100*covs, '+-', label='Measured')
    axs[2].loglog(
        range(1, len(covs)+1),
        100*covs[0] / np.arange(1, len(covs)+1),
        '-',
        label='Calculated'
    )
    axs[2].set_title('Weisskoff Plot ROC = %.2f pixels' % roc)
    axs[2].set_xlabel('ROI Width')
    axs[2].set_ylabel('100*CoV')
    axs[2].grid(True, 'both')
    axs[2].legend()

    # Image Smoothness (Gaussian Random Field Theory)
    fwhmx, fwhmy, fwhmz = fwhm_smoothness_xyz_preprocessed(time_series, (dx, dy,  dz))

    # Filter out the negative values (specially for Z)
    # We tagged them as they were giving NaNs from log(-ve no.)
    framenos = range(1, len(fwhmx)+1)
    filtered_xresults = [(frameno, f) for (frameno, f) in zip(framenos, fwhmx) if f > 0]
    if filtered_xresults:
        framenos, fwhmx = zip(*filtered_xresults)
        p1, = axs[3].plot(framenos, fwhmx, '+-', label='X')
    else:
        p1, = axs[3].plot([1], [0], '+-', label='X')
    framenos = range(1, len(fwhmy)+1)
    filtered_yresults = [(frameno, f) for (frameno, f) in zip(framenos, fwhmy) if f > 0]
    if filtered_yresults:
        framenos, fwhmy = zip(*filtered_xresults)
        p2, = axs[3].plot(framenos, fwhmy, '+-', label='Y')
    else:
        p2, = axs[3].plot([1], [0], '+-', label='Y')

    # The result now seems to be the same as the fBIRN analysis
    framenos = range(1, len(fwhmz)+1)
    filtered_zresults = [(frameno, f) for (frameno, f) in zip(framenos, fwhmz) if f > 0]
    if filtered_zresults:
        framenos, fwhmz = zip(*filtered_zresults)
        p3, = axs[3].plot(framenos, fwhmz, '+-', label='Z')
    else:
        p2, = axs[3].plot([1], [0], '+-', label='Z')

    axs[3].set_title(
        'FWHM (%d/%d points suppressed in Z)' % (len(time_series)-len(framenos), len(time_series))
    )
    axs[3].set_xlabel('Frame No')
    axs[3].set_ylabel('FWHM X,Y,Z (mm)')
    axs[3].grid(True)
    axs[3].legend()

    # Movement of the phantom Centre of Gravity from its starting position
    cofg = centre_of_mass(time_series)
    axs[4].plot(
        range(1, len(cofg) + 1),
        [x - cofg[0][0] for (x, y, z) in cofg], '-', label='X'
    )
    axs[4].plot(
        range(1, len(cofg) + 1),
        [y-cofg[0][1] for (x, y, z) in cofg], '-', label='Y'
    )
    axs[4].plot(
        range(1, len(cofg) + 1),
        [z - cofg[0][2] for (x, y, z) in cofg], '-', label='Z'
    )
    axs[4].set_title('Relative Position')
    axs[4].set_xlabel('Frame No')
    axs[4].set_ylabel('X, Y, Z Position (Pixels)')
    axs[4].grid(True)
    axs[4].legend()

    # Average strength of ghosts and of the 'brightest' ghosts
    pmeans, gmeans, bright_gmeans, snrs = ghostiness_trends(time_series)
    axs[5].plot(range(1, len(gmeans)+1), 100*gmeans/pmeans, '-', label='Ghosts')
    axs[5].plot(range(1, len(bright_gmeans)+1), 100*bright_gmeans/pmeans, '-', label='Bright Ghosts')

    axs[5].set_title('Ghostiness')
    axs[5].set_xlabel('Frame No')
    axs[5].set_ylabel('Relative Intensity (%)')
    axs[5].grid(True)
    axs[5].legend()

    # Shift the images to correct for frequency drift.
    # This is in "phase" dirn, but can do on both axes as will be negligible in the freq dirn
    # The images can be shifted by subpixel amounts using scipy.ndimage.shift()
    # but as this implies interpolation we avoid this for calculating the region of interest statistics
    # and we only "roll" the images by integer numbers of pixels.
    # Consequence is this will only reduce, not avoid shift artefacts in the static snr image. 
    if correct_drift:
        cofg = np.asarray(cofg)
        xshifts, yshifts, _ = (cofg - cofg[0]).T
        shifted_time_series = np.array([
            shift(im, (-yshift, -xshift), mode='wrap')
            for (im, xshift, yshift) in zip(central_slice_time_series, xshifts, yshifts)
        ])

        xshifts, yshifts = xshifts.round().astype(int), yshifts.round().astype(int)
        rolled_time_series = np.array([
            np.roll(im, (-yshift, -xshift), axis=(0, 1))
            for (im, xshift, yshift) in zip(central_slice_time_series, xshifts, yshifts)
        ])

        roi_snr = snr_summary(rolled_time_series, roisize=roisize)
        roi_signal = signal_summary(rolled_time_series, roisize=roisize)
        roi_sfnr = sfnr_summary(rolled_time_series, roisize=roisize)
        central_slice_time_series = shifted_time_series
    else:
        roi_snr = snr_summary(central_slice_time_series, roisize=roisize)
        roi_signal = signal_summary(central_slice_time_series, roisize=roisize)
        roi_sfnr = sfnr_summary(central_slice_time_series, roisize=roisize)
            
    # Image of average spatial noise
    ssn = static_spatial_noise_image(central_slice_time_series)
    im = axs[6].imshow(ssn, cmap='coolwarm', vmin=-np.max(ssn), vmax=np.max(ssn))
    axs[6].axis('off')
    axs[6].set_title('Static Spatial Noise [SNR = %0.1f]' % roi_snr)
    fig.colorbar(im, ax=axs[6], fraction=0.046, pad=0.04)

    # Average Image
    im = axs[7].imshow(signal_image(central_slice_time_series), cmap='viridis')
    axs[7].axis('off')
    axs[7].set_title('Signal [ROI = %0.1f]' % roi_signal)
    fig.colorbar(im, ax=axs[7], fraction=0.046, pad=0.04)

    # Image of temporal fluctuations
    im = axs[8].imshow(temporalnoise_fluct_image(central_slice_time_series), cmap='viridis')
    axs[8].axis('off')
    axs[8].set_title('Temporal Fluctuation')
    fig.colorbar(im, ax=axs[8], fraction=0.046, pad=0.04)

    # Image of normalised temporal fluctuations
    sfnri = sfnr_image(central_slice_time_series)
    sfnri[sfnri > 500] = 500
    im = axs[9].imshow(sfnri, cmap='viridis')
    axs[9].axis('off')
    axs[9].set_title('SFNR [ROI = %0.1f]' % roi_sfnr)
    fig.colorbar(im, ax=axs[9], fraction=0.046, pad=0.04)

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.suptitle('fBIRN Stability for %s on %s' % (scanner, date), fontsize=22)

    return pd.DataFrame(
        [(fluct, drift_fit, np.mean(100*gmeans/pmeans), np.mean(100*bright_gmeans/pmeans), mean, snr, sfnr)],
        columns=['Fluctuations', 'FittedDrift', 'Ghosts', 'BrightGhosts', 'SignalMean', 'SNR', 'SFNR'],
        index=["%s_%s" % (scanner, date)]
    )
