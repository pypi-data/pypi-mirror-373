#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""snr.py: graphical reports of QA signal and noise parameters."""

from warnings import warn

import numpy as np
from numpy.ma import masked_where

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from scipy.stats import chi, norm

from pydicom.dataset import Dataset

from mriqa.phantoms import (
    SIEMENSLONGBOTTLE, find_phantom,
    phantom_mask_2d, noise_background_mask_2d, circular_mask
)

from mriqa.dcmio import (
    approx_phase_orientation, approx_slice_orientation,
    seq_name, protocol_name, series_number, pix_spacing_yx,
    slice_thickness, readout_bandwidth, number_of_averages,
    number_of_phase_encoding_steps,
    t_r, recon_scale_factor, phase_enc_dirn, flip_angle,
    manufacturer, is_multiframe, number_of_frames
)

from mriqa.tools import (
    mean_im, diff_im, snr_map, all_ims, im_pair, coil_elements, rx_coil_string, add_phase_encode_mark
)


def snr_report(raw_dobjs, raw_dobjsb=None,
               frame=None, frame_b=None,
               inner_snr_fraction=0.5, outer_snr_fraction=0.75,
               phantom=SIEMENSLONGBOTTLE, show_centre=False,
               coil=None):
    """
    Report on signal to noise.

    Based on images of Siemens long bottle or similar phantom.
    Use a global noise estimate to normalise the mean image.

    """
    raw_dobjs = sorted(raw_dobjs, key=approx_slice_orientation)
    orientations = [approx_slice_orientation(d) for d in raw_dobjs]
    assert len(set(orientations)) == 1
    orientation = orientations[0]

    if raw_dobjsb is not None:
        # two series
        assert len(raw_dobjsb) == len(raw_dobjs)
        raw_dobjsb = sorted(raw_dobjsb, key=approx_slice_orientation)
        assert all(approx_slice_orientation(d) == orientation for d in raw_dobjsb)
        dobja = raw_dobjs[0]
        dobjb = raw_dobjsb[0]
    elif len(raw_dobjs) >= 2:
        # single series with two slices
        dobja = raw_dobjs[0]
        dobjb = raw_dobjs[1]
    else:
        # single series multiframe
        dobja = raw_dobjs[0]
        dobjb = None

    # Voxel geometry - require square pixels
    dy, dx = pix_spacing_yx(dobja)
    assert np.isclose(dx, dy)
    dz = slice_thickness(dobja)

    info = {
        'Series':      series_number(dobja),
        'Protocol':    protocol_name(dobja),
        'Sequence':    seq_name(dobja),
        'Orient':   '/'.join([
            approx_slice_orientation(dobja), approx_phase_orientation(dobja)
        ]),
        'Bandwidth':   readout_bandwidth(dobja),
        'TR': t_r(dobja),
        'FlipAngle':   flip_angle(dobja),
        'Coil': rx_coil_string(dobja, coil),
        'VoxelVolume': dx * dy * dz,
        'NSA':         number_of_averages(dobja),
        'KSpaceLines': number_of_phase_encoding_steps(dobja)
    }

    fix_siemens_bug = manufacturer(dobja) == 'Siemens'
    fix_philips_bug = manufacturer(dobja) == 'Philips'
    fix_ge_bug = manufacturer(dobja) == 'GE'
    phase_dirn = phase_enc_dirn(dobja)

    # Siemens image scale for noise statistics though it should drop out in SNR calc.
    # nb: won't be defined for Philips/GE
    try:
        image_scale = recon_scale_factor(dobja)
    except KeyError:
        image_scale = 1.0

    mean_image = mean_im(dobja, dobjb)
    diff_image = diff_im(dobja, dobjb)
    imagea, imageb = im_pair(dobja, dobjb)

    # Exclude backgound areas in p/e direction to avoid any ghost artefacts
    noise_roi_mask = noise_background_mask_2d(
        mean_image, phase_dirn,
        fix_siemens_bug=fix_siemens_bug,
        fix_philips_bug=fix_philips_bug,
        fix_ge_bug=fix_ge_bug
    )

    snr_image = snr_map(dobja, dobjb, global_noise=True, noise_mask=noise_roi_mask)

    # Masks to help in display and histograms
    noise_roi_a = masked_where(~noise_roi_mask, imagea)
    noise_roi_b = masked_where(~noise_roi_mask, imageb)
    not_noise_roi_a = masked_where(noise_roi_mask, imagea)
    noise_pixels = np.hstack((
        noise_roi_a.compressed(),
        noise_roi_b.compressed()
    ))

    # Apply masks to difference images
    noise_diff_roi = masked_where(~noise_roi_mask, diff_image)

    # Fit normal distribution to noise difference in background roi
    noise_diff_pixels = noise_diff_roi.compressed()
    mu, sigma = norm.fit(noise_diff_pixels)

    # find_phantom returns pixel coordinates in natural order (x, y)
    expected_radius = phantom['Diameter'] / 2 / dx
    centre_x, centre_y, radius = find_phantom(mean_image, expected_radius)
    inner_snr_radius = inner_snr_fraction * radius
    outer_snr_radius = outer_snr_fraction * radius

    y, x = np.ogrid[:mean_image.shape[0], :mean_image.shape[1]]
    y -= centre_y
    x -= centre_x
    inner_disc_mask = x**2 + y**2 <= inner_snr_radius**2
    outer_disc_mask = x**2 + y**2 <= outer_snr_radius**2

    snr_inner = np.ma.array(
        snr_image, mask=np.logical_not(inner_disc_mask)
    ).mean()
    snr_outer = np.ma.array(
        snr_image, mask=np.logical_not(outer_disc_mask)
    ).mean()

    fig = plt.figure(figsize=(12, 8))
    gs = plt.GridSpec(2, 6, fig)
    axs = [
        fig.add_subplot(gs[0, :2]),
        fig.add_subplot(gs[0, 2:4]),
        fig.add_subplot(gs[0, 4:]),
        fig.add_subplot(gs[1, :3]),
        fig.add_subplot(gs[1, 3:])
    ]

    im_background = axs[0].imshow(noise_roi_a, cmap='viridis', interpolation='none')
    im_foreground = axs[0].imshow(not_noise_roi_a, cmap='viridis', interpolation='none')
    axs[0].axis('image')
    axs[0].axis('off')
    axs[0].grid(False)
    axs[0].set_title(r'Phantom and Noise Regions')

    tight_mask = phantom_mask_2d(mean_image, mode='Erode')
    tight_mask = np.ma.masked_where(tight_mask == 0, np.ones(tight_mask.shape))
    axs[0].imshow(tight_mask, cmap='rainbow', alpha=0.2)

    axs[0].add_artist(
        plt.Circle(
            (centre_x, centre_y), radius=radius,
            color='g', fill=False, linewidth=1.0
        )
    )
    axs[0].add_artist(
        plt.Circle(
            (centre_x, centre_y), radius=outer_snr_radius,
            color='g', fill=True, alpha=0.2, linewidth=1.0
        )
    )
    axs[0].add_artist(
        plt.Circle(
            (centre_x, centre_y), radius=inner_snr_radius,
            color='r', fill=True, alpha=0.2, linewidth=1.0
        )
    )
    axs[0].add_artist(
        plt.Circle(
            (centre_x, centre_y), radius=1,
            color='y', fill=True
        )
    )

    add_phase_encode_mark(axs[0], phase_dirn, colour='magenta')

    cax = make_axes_locatable(axs[0]).append_axes("left", size="3%", pad=0.6)
    fig.colorbar(im_background, cax=cax)
    cax.yaxis.set_ticks_position('left')
    cax = make_axes_locatable(axs[0]).append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im_foreground, cax=cax)

    # TODO: we are repeating logic in tools.py -> refactor DRY
    # TODO: this makes it zero, or could slice out entirely by setting to nan
    if show_centre:
        absmax = np.percentile(np.abs(diff_image), 95)
        im = axs[1].imshow(diff_image, vmin=-absmax, vmax=absmax, cmap='coolwarm', interpolation='none')
    else:
        mask_background = ~phantom_mask_2d(mean_image, mode='Dilate')
        diff_image_background = np.where(mask_background, diff_image, 0)
        absmax = np.percentile(np.abs(diff_image_background), 95)
        im = axs[1].imshow(
            diff_image_background,
            vmin=-absmax, vmax=absmax, cmap='coolwarm',
            interpolation='none'
        )
    axs[1].axis('image')
    axs[1].axis('off')
    axs[1].grid(False)
    cax = make_axes_locatable(axs[1]).append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im, cax=cax)

    axs[1].set_title(r'Paired Difference')

    slack_mask = phantom_mask_2d(mean_image, mode='Dilate')
    ystart, xstart = np.argwhere(slack_mask).min(axis=0)
    ystop, xstop = np.argwhere(slack_mask).max(axis=0) + 1

    img = axs[2].imshow(snr_image[ystart:ystop, xstart:xstop], cmap='bone')
    axs[2].axis('Off')

    divider = make_axes_locatable(axs[2])
    cax = divider.append_axes("right", size="5%", pad=0.05)

    fig.colorbar(img, cax=cax)
    axs[2].set_title(f"SNR Map [{info['Coil']}]")

    # Histogram and chi-fit to un-differenced images background
    imin, imax = 0,  int(np.ceil(np.max(noise_pixels)))
    nbins = imax - imin
    range_ = (imin + 0.5,  imax + 0.5)
    n, bins, patches = axs[3].hist(
        noise_pixels, bins=nbins, range=range_,
        density=True, alpha=0.75, label='Histogram'
    )
    # keep histogram plot scale even if fit fails
    # matplotlib >=3.2 requires querying limits to set them
    axs[3].get_xlim()
    axs[3].get_ylim()
    axs[3].autoscale(False)

    axs[3].set_xlabel('Signal Magnitude $M$')
    axs[3].set_ylabel('$P(M)$')
    axs[3].set_title(f"ROI Noise Statistics [{info['Coil']}: Combined]")
    axs[3].legend()
    axs[3].grid(True)

    # Histogram and normal fit to difference images background
    imin, imax = (
        int(np.ceil(np.min(noise_diff_pixels))),
        int(np.ceil(np.max(noise_diff_pixels)))
    )
    nbins = imax - imin
    range_ = (imin + 0.5,  imax + 0.5)
    n, bins, patches = axs[4].hist(
        noise_diff_pixels, bins=nbins, range=range_,
        density=True, alpha=0.75, label='Histogram'
    )
    # force autoscale calc (for matplotlib >=3.2) and freeze
    axs[4].get_xlim()
    axs[4].get_ylim()
    axs[4].autoscale(False)

    mu, sigma = noise_diff_pixels.mean(), noise_diff_pixels.std()
    y = norm.pdf(bins, loc=mu, scale=sigma)
    axs[4].plot(bins, y, '--', label='Normal fit')

    axs[4].text(0, 0.5 * max(n), r'$\sigma=%0.2f$' % (sigma/image_scale))
    axs[4].set_xlabel('Signal Difference $D$')
    axs[4].set_ylabel('$P(D)$')
    axs[4].set_title('ROI Noise Statistics (Difference Image)')
    axs[4].legend()
    axs[4].grid(True)

    fig.suptitle(
        '%s: %s SNR [%s, BW:%0.0dHz, TR:%0.0d, FA:%0.0d, %s] ' % (
            info['Sequence'], info['Coil'],
            phantom['Name'], info['Bandwidth'], info['TR'], info['FlipAngle'], info['Orient'],
        ),
        fontsize=16
    )
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    #fig.set_tight_layout(True)

    return pd.DataFrame(
        {info['Coil']: [snr_inner, snr_outer]},
        index=pd.Index([inner_snr_fraction, outer_snr_fraction], name='RegionSize')
    )


def noise_correlation_report(dobjsa, dobjsb, coil=None):
    """
    Report on channel correlations in uncombined noise only images.

    Requires two sets of images so inter-element noise correlations
    can be performed on differences. The overall coil name should be specified
    as only the individual element names will be present in the DICOM.

    Parameters
    ----------
    dobjsa: list of dicom objects
        uncombined coil element images
    dobjsb: list of dicom objects
        uncombined coil element images
    coil: Opt[str]
        Name/ID of coil to use in report

    Returns
    -------
    dataframe: MinCorrel., MaxCorrel., DiagonalVariance, MaximumOffDiagonal

    """
    dobjsa = sorted(dobjsa, key=coil_elements)
    dobjsb = sorted(dobjsb, key=coil_elements)

    coil = rx_coil_string(dobjsa[0], coil)

    nchannels = len(dobjsa)
    assert len(dobjsa) == len(dobjsb)
    assert 1 < nchannels <= 64

    imagesa = np.asarray([d.pixel_array for d in dobjsa], dtype='int16')
    imagesb = np.asarray([d.pixel_array for d in dobjsb], dtype='int16')

    # Work around for Siemens bug in first row/col
    imagesa = imagesa[:, 1:, 1:]
    imagesb = imagesb[:, 1:, 1:]

    dimages = (imagesa - imagesb).reshape(len(imagesa), -1)

    covariance = np.cov(dimages)
    assert covariance.shape == (nchannels, nchannels)

    normalisation = np.mean(np.diag(covariance))

    fig, axs = plt.subplots(1, 2, figsize=(12, 4))

    covar_diagonal = np.diagonal(covariance)
    diag_cov = np.std(covar_diagonal) / np.mean(covar_diagonal)

    rms_diag = np.sqrt(np.sum(covar_diagonal**2))
    mask = np.ones(covariance.shape, dtype=bool)
    np.fill_diagonal(mask, False)
    offdiag_max = abs(covariance[mask]).max()

    percentage_deviations = 100 * (
        (covar_diagonal - np.mean(covar_diagonal)) / np.mean(covar_diagonal)
    )
    worst = np.argmax(percentage_deviations**2)

    axs[0].bar(
        1 + np.arange(len(percentage_deviations)),
        percentage_deviations
    )
    axs[0].axis('tight')
    axs[0].set_xlabel('Coil Element')
    axs[0].set_ylabel('Relative Difference from Average (%)')
    axs[0].set_title('Noise Power Difference from Average')
    axs[0].text(
        len(percentage_deviations) / 2, np.max(percentage_deviations),
        'Max. diff. elem. %d (%0.1f%%)' % (worst+1, percentage_deviations[worst])
    )
    axs[0].grid(True)

    img = axs[1].imshow(
        10 * np.log10(np.abs(covariance/normalisation)),
        cmap='viridis',
        interpolation='nearest'
    )
    axs[1].axis('off')
    axs[1].set_title('Coil Element Covariance (dB)')

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    cbar = fig.colorbar(img, cax=cbar_ax)
    cbar.set_label('Ratio to Diagonal (dB)', rotation=270)
    cbar.ax.yaxis.set_label_position('right')

    return pd.DataFrame({
        'MinCorrelation': np.amin(covariance),
        'MaxCorrelation': np.amax(covariance),
        'DiagonalVariance': diag_cov,
        'MaximumOffDiagonal': (100 * offdiag_max/rms_diag)
    }, index=['%s' % coil])


def noise_statistics_report_multichannel(dobjs, coil=None):
    """
    Report on noise statistics in uncombined noise only images.

    Fits a central-chi distribution to the noise magnitude.

    The number of degrees of freedom is fitted but should be approximately
    twice the number of coil elements in the sum of squares combination.
    A small reduction can result from cross channel correlations.

    The overall coil name should be specified as only the individual
    element names will be present in the DICOM.

    Parameters
    ----------
    dobjs: list of dicom objects
        uncombined coil element noise only images
    coil: Opt[str]
        Name/ID of coil to use in report

    Returns
    -------
    dataframe:  number of channels, fitted degrees of freedom, scale parameter

    """
    nchannels = len(dobjs)
    images = np.asarray([d.pixel_array & 0x0fff for d in dobjs], dtype='int16')

    coil = rx_coil_string(dobjs[0], coil)

    # Work around for Siemens bug in first row/col
    images = images[:, 1:, 1:]

    rmsimage = np.sqrt(np.sum(images.astype(float)**2, axis=0))
    rmsimage = np.round(rmsimage).astype(int)[1:, 1:]

    # Central-chi fit to rms noise, allow dof to vary but should be 2*nchannels
    df, loc, scale = chi.fit(rmsimage.reshape(-1), floc=0)

    imin, imax = 0,  int(np.ceil(np.max(rmsimage)))
    nbins = imax - imin
    range_ = (imin + 0.5,  imax + 0.5)
    n, bins, _ = plt.hist(
        rmsimage.reshape(-1),
        bins=nbins, range=range_, density=True, alpha=0.75, label='Histogram'
    )

    y = chi.pdf(bins, df, loc, scale)
    plt.plot(bins, y, '--', label=r'$\chi$ fit (dof=%0.1f)' % df)

    mu, sigma = rmsimage.mean(), rmsimage.std()
    plt.text(
        0, 0.5 * max(n),
        r'df=%d, $\mu=%0.2f$, $\sigma=%0.2f$, $scale=%0.2f$' %
        (df, mu, sigma, scale)
    )
    plt.xlabel('Signal Magnitude $M$')
    plt.ylabel('$P(M)$')
    plt.title('Noise Statistics for Manually Sum-Of-Squares Combined Images')
    plt.legend()
    plt.grid(True)

    return pd.DataFrame({
        'Channels': nchannels,
        'DegreesOfFreedom': df,
        'Scale': scale
    }, index=[coil])


def noise_statistics_report_combined(dobj):
    """
    Report on noise statistics in sum of squares combined noise only images.

    Fits a central-chi distribution to the noise magnitude.

    The number of degrees of freedom is fitted but should be approximately
    twice the number of coil elements in the sum of squares combination.
    A small reduction can result from cross channel correlations.

    Parameters
    ----------
    dobj: dicom objects
         noise only sum-of-squares combined image

    Returns
    -------
    dataframe:  number of channels, fitted degrees of freedom, scale parameter

    """
    rmsimage = np.asarray(dobj.pixel_array & 0x0fff, dtype='int16')
    imin, imax = 0,  int(np.ceil(np.max(rmsimage)))
    nbins = imax - imin
    range_ = (imin + 0.5,  imax + 0.5)

    n, bins, _ = plt.hist(
        rmsimage.reshape(-1),
        bins=nbins, range=range_, density=True, alpha=0.75, label='Histogram'
    )
    df, loc, scale = chi.fit(rmsimage.reshape(-1), floc=0)

    y = chi.pdf(bins, df, loc, scale)
    plt.plot(bins, y, '--', label=r'$\chi$ fit (dof=%0.1f)' % df)
    mu, sigma = rmsimage.mean(), rmsimage.std()
    plt.text(
        0, 0.5 * max(n),
        r'df=%d, $\mu=%0.2f$, $\sigma=%0.2f$, $scale=%0.2f$' %
        (df, mu, sigma, scale)
    )
    plt.xlabel('Signal Magnitude $M$')
    plt.ylabel('$P(M)$')
    plt.title('Noise Statistics for System Sum-Of-Squares Combined Images')
    plt.legend()
    plt.grid(True)

    return pd.DataFrame({
        'DegreesOfFreedom': df,
        'Scale': scale
    }, index=[rx_coil_string(dobj)])


def snr_report_multi(dobjsa, dobjsb=None,
                     inner_snr_fraction=0.5,
                     outer_snr_fraction=0.75,
                     phantom=SIEMENSLONGBOTTLE,
                     coil=None):
    """
    Report on signal to noise based on images of Siemens long bottle phantom.

    Uses a global noise estimate to normalise the mean image.
    Requires two series, each of single slice with different coil elements.
    If a single element is given then assumed to be an rms combined image.
    Alternatively a multiframe with at least two acquisitions may be used.

    Parameters
    ----------
    dobjsa: list of dicom objects
        series consisting of individual coil images or a single combined image
    dobjsb: list of dicom objects
        series consisting of individual coil images or a single combined image
    inner_snr_fraction: Opt[float]
        linear proportion of disc for inner region of interest
    outer_snr_fraction: Opt[float]
        linear proportion of disc for outer region of interest
    phantom: dict
        phantom description, used for expected dimensions
    coil: str
        coil id/name to be used when using uncombined images

    Produces matplotlib graphics output.

    Returns
    -------
    Pandas Dataframe of results.


    """
    if isinstance(dobjsa, Dataset):
        dobjsa = [dobjsa]
    if isinstance(dobjsb, Dataset):
        dobjsb = [dobjsb]

    assert is_multiframe(dobjsa[0]) or dobjsb is not None

    dobj = dobjsa[0]
    fix_siemens_bug = manufacturer(dobj) == 'Siemens'
    fix_philips_bug = manufacturer(dobj) == 'Philips'
    fix_ge_bug = manufacturer(dobj) == 'GE'
    if is_multiframe(dobj) and manufacturer(dobj) == 'Philips':
        # Multiframes only - expect at least two frames
        nframes = number_of_frames(dobj)
        nobjs = len(dobjsa)
        assert nframes > 1
        assert nobjs == 1

        # Image data
        images = all_ims(dobj)
        pffgs = dobj.PerFrameFunctionalGroupsSequence

        # Check scale factors all the same, rescale if not
        transforms = [
            (
                float(pffg.PixelValueTransformationSequence[0].RescaleSlope),
                float(pffg.PixelValueTransformationSequence[0].RescaleIntercept)
            )
            for pffg in pffgs
        ]
        if len(set(transforms)) != 1:
            warn('snr_report_multi: applying Pixel value transformations as not consistent across frames')
            for image, transform in zip(images, transforms):
                image[:] = image * transform[0] + transform[1]

        # Assume a single slice, two acqusitions, possibly multiple elements
        assert 'DimensionIndexSequence' in dobj
        dim_seq = dobj.DimensionIndexSequence
        assert len(dim_seq) in (3, 4)

        # In-Stack Position Number
        assert dim_seq[1].DimensionIndexPointer == (0x0020, 0x9057)
        assert dim_seq[1].FunctionalGroupPointer == (0x0020, 0x9111)
        # Temporal Position Index
        assert dim_seq[2].DimensionIndexPointer == (0x0020, 0x9128)
        assert dim_seq[2].FunctionalGroupPointer == (0x0020, 0x9111)

        slices = [
            pffg.FrameContentSequence[0].DimensionIndexValues[1]
            for pffg in pffgs
        ]
        times = [
            pffg.FrameContentSequence[0].DimensionIndexValues[2]
            for pffg in pffgs
        ]
        assert len(set(slices)) == 1 and len(set(times)) == 2

        if len(dim_seq) == 4:
            # Uncombined: Coil Element (overloads ChemicalShift)
            assert dim_seq[3].DimensionIndexPointer == (0x2001, 0x1001)
            assert dim_seq[3].FunctionalGroupPointer == (0x2005, 0x140f)

        # Assume now we have two lots of nelements
        imagesa, imagesb = images[:nframes//2], images[nframes//2:]
        imagesa = np.array(imagesa, dtype=float)
        imagesb = np.array(imagesb, dtype=float)
    elif is_multiframe(dobj) and manufacturer(dobj) == 'Siemens':
        nframes = number_of_frames(dobj)
        nobjs = len(dobjsa)
        assert nframes > 1
        assert nobjs > 1

        # Check everything oriented the same
        assert len({approx_slice_orientation(d) for d in dobjsa}) == 1
        assert len({approx_phase_orientation(d) for d in dobjsa}) == 1

        # Line up uncombined images on coil element
        if len(dobjsa) > 1:
            dobjsa = sorted(dobjsa, key=lambda x: coil_elements(x)[0])

        # NB includes work around for Siemens row/col zero bug
        images = all_ims(dobjsa)[:, 1:, 1:].astype(float)
        imagesa = images[:len(images) // 2]
        imagesb = images[len(images) // 2:]

        pffgs = dobj.PerFrameFunctionalGroupsSequence

        # Assume specific multiframe layout
        dis = dobj.DimensionIndexSequence
        if len(dis) > 3:
            raise ValueError('4D multiframes not implemented yet for Siemens')

        # Stack ID
        assert dis[0].DimensionIndexPointer  == (0x0020, 0x9056)
        assert dis[0].FunctionalGroupPointer == (0x0020, 0x9111)
        # In-Stack Position Number
        assert dis[1].DimensionIndexPointer  == (0x0020, 0x9057)
        assert dis[1].FunctionalGroupPointer == (0x0020, 0x9111)
        # Temporal Position Index
        assert dis[2].DimensionIndexPointer  == (0x0020, 0x9128)
        assert dis[2].FunctionalGroupPointer == (0x0020, 0x9111)

        # Check scale factors all the same
        assert len({
            float(pffg.PixelValueTransformationSequence[0].RescaleIntercept)
            for pffg in pffgs
        }) == 1
        assert len({
            float(pffg.PixelValueTransformationSequence[0].RescaleSlope)
            for pffg in pffgs
        }) == 1

        # Number of unique values in each dimension
        # TODO: is this defined explicitly somewhere?
        nstacks_in_multiframe = len({
            pffg.FrameContentSequence[0].DimensionIndexValues[0]
            for pffg in pffgs
        })
        nslices_in_multiframe = len({
            pffg.FrameContentSequence[0].DimensionIndexValues[1]
            for pffg in pffgs
        })
        nacquisitions_in_multiframe = len({
            pffg.FrameContentSequence[0].DimensionIndexValues[2]
            for pffg in pffgs
        })

        # Handle coil and spatial series only
        assert nstacks_in_multiframe == 1
        assert nslices_in_multiframe == 1
        assert nacquisitions_in_multiframe == 2

    else:
        assert len(dobjsa) == len(dobjsb)

        # Check everything oriented the same
        assert len({
            approx_slice_orientation(d) for d in (dobjsa + dobjsb)
        }) == 1
        assert len({
            approx_phase_orientation(d) for d in (dobjsa + dobjsb)
        }) == 1

        # Line up uncombined images on coil element
        if len(dobjsa) > 1:
            dobjsa = sorted(dobjsa, key=lambda x: coil_elements(x)[0])
            dobjsb = sorted(dobjsb, key=lambda x: coil_elements(x)[0])
            assert all(
                coil_elements(a)[0] == coil_elements(b)[0]
                for a, b in zip(dobjsa, dobjsb)
            )

        # NB includes work around for Siemens or Philips row/col zero bugs
        imagesa = all_ims(dobjsa).astype(float)
        imagesb = all_ims(dobjsb).astype(float)

    # Some image information fields
    info = {
        'Series':   series_number(dobj),
        'Protocol': protocol_name(dobj),
        'Sequence': seq_name(dobj),
        'Orient':   '/'.join([
            approx_slice_orientation(dobj), approx_phase_orientation(dobj)
        ]),
        'Bandwidth': readout_bandwidth(dobj),
        'TR': t_r(dobj),
        'FlipAngle': flip_angle(dobj),
        'Coil': rx_coil_string(dobj, coil)
    }

    # Require square pixels
    pix_dims = pix_spacing_yx(dobj)
    if pix_dims[0] != pix_dims[1]:
        raise ValueError('Pixels are not square %f vs %f' % tuple(pix_dims))

    # Siemens image scale for noise statistics though it should drop out in SNR calc.
    # nb: won't be defined for Philips/GE
    try:
        image_scale = recon_scale_factor(dobj)
    except KeyError:
        image_scale = 1.0

    # Exclude backgound areas in p/e direction to avoid any ghost artefacts
    phase_dirn = phase_enc_dirn(dobj)

    # Perform rms combination of uncombined coil images
    if len(imagesa) > 1:
        rmsimagea = np.sqrt((imagesa ** 2).sum(axis=0))
        rmsimageb = np.sqrt((imagesb ** 2).sum(axis=0))
    else:
        rmsimagea = imagesa[0]
        rmsimageb = imagesb[0]

    # Combine the two acquisitions
    mean_image = (rmsimagea + rmsimageb) / 2
    diff_image = (rmsimagea - rmsimageb)

    # Construct disc shaped masks for the signal foreground in the phantom
    expected_radius = phantom['Diameter'] / 2 / pix_dims[0]
    centre_x, centre_y, radius = find_phantom(mean_image, expected_radius)
    inner_snr_radius = inner_snr_fraction * radius
    outer_snr_radius = outer_snr_fraction * radius
    inner_disc_mask = circular_mask(
        mean_image, inner_snr_radius, centre_x, centre_y
    )
    outer_disc_mask = circular_mask(
        mean_image, outer_snr_radius, centre_x, centre_y
    )

    # Masks to help in display only
    background_mask = ~phantom_mask_2d(mean_image, 'Dilate')

    # Construct a shaped mask for the background noise ROI
    noise_roi_mask = noise_background_mask_2d(
        mean_image, phase_dirn,
        fix_siemens_bug=fix_siemens_bug,
        fix_philips_bug=fix_philips_bug,
        fix_ge_bug=fix_ge_bug
    )
    noise_roi_a = masked_where(~noise_roi_mask, rmsimagea)
    noise_roi_b = masked_where(~noise_roi_mask, rmsimageb)

    # Mask to help in display only
    not_noise_roi_a = masked_where(noise_roi_mask, rmsimagea)

    # Fit chi distribution to noise in background roi
    noise_pixels = np.hstack((
        noise_roi_a.compressed(),
        noise_roi_b.compressed()
    ))
    df, loc, scale = chi.fit(noise_pixels, floc=0)

    # Apply masks to difference images
    # phantom_roi_diff = masked_where(background_mask, diff_image)
    not_phantom_roi_diff = masked_where(~background_mask, diff_image)
    noise_diff_roi = masked_where(~noise_roi_mask, diff_image)

    # Fit normal distribution to noise difference in background roi
    noise_diff_pixels = noise_diff_roi.compressed()
    mu, sigma = norm.fit(noise_diff_pixels)

    # SNR calculations using the disc ROIs for the signal
    signal_inner = np.ma.array(mean_image, mask=~inner_disc_mask).mean()
    signal_outer = np.ma.array(mean_image, mask=~outer_disc_mask).mean()

    # NB sqrt(2) correction for overestimate of noise in subtraction image
    snr_inner_diff = np.sqrt(2) * signal_inner / sigma
    snr_outer_diff = np.sqrt(2) * signal_outer / sigma

    # Matplotlib plots
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs = axs.ravel()

    # Show phantom with Regions of Interest
    axs[0].imshow(noise_roi_a, cmap='viridis', interpolation='none')
    im = axs[0].imshow(not_noise_roi_a, cmap='viridis', interpolation='none')
    axs[0].axis('image')
    axs[0].axis('off')
    axs[0].grid(False)
    axs[0].set_title('Phantom and Noise Regions')
    axs[0].add_artist(
        plt.Circle(
            (centre_x, centre_y),
            radius=outer_snr_radius, color='g',
            fill=True, alpha=0.2, linewidth=1.0
        )
    )
    axs[0].add_artist(
        plt.Circle(
            (centre_x, centre_y),
            radius=inner_snr_radius, color='r', fill=True,
            alpha=0.2, linewidth=1.0
        )
    )
    axs[0].add_artist(
        plt.Circle(
            (centre_x, centre_y),
            radius=1, color='y', fill=True
        )
    )
    fig.colorbar(im, ax=axs[0])

    # Show difference image for any artefacts
    # Centre colour range about zero in signed image
    # Use percentile rather than min/max to cope with isolated bright artefacts
    vmin = np.percentile(not_phantom_roi_diff.compressed(), 2)
    vmax = np.percentile(not_phantom_roi_diff.compressed(), 98)
    vmax = max(abs(vmin), abs(vmax))
    vmin = -vmax

    im = axs[1].imshow(
        not_phantom_roi_diff, vmin=vmin, vmax=vmax, cmap='coolwarm', interpolation='none',
    )
    axs[1].axis('image')
    axs[1].axis('off')
    axs[1].grid(False)
    fig.colorbar(im, ax=axs[1])
    axs[1].set_title(r'Paired Difference')

    # Histogram and chi-fit to un-differenced images background
    imin, imax = 0,  int(np.ceil(np.max(noise_pixels)))
    nbins = imax - imin
    range_ = (imin + 0.5,  imax + 0.5)
    n, bins, patches = axs[2].hist(
        noise_pixels, bins=nbins, range=range_,
        density=True, alpha=0.75, label='Histogram'
    )
    # keep histogram plot scale even if fit fails
    # matplotlib >=3.2 requires querying limits to set them
    axs[2].get_xlim()
    axs[2].get_ylim()
    axs[2].autoscale(False)

    y = chi.pdf(bins, df, loc, scale)
    axs[2].plot(bins, y, '--', label=r'$\chi$ fit (dof=%0.0f)' % df)
    mu, sigma = noise_pixels.mean(), noise_pixels.std()
    axs[2].text(
        0, 0.5 * max(n),
        r'$\sigma=%0.2f$, $scale=%0.2f$' %
        (sigma/image_scale, scale/image_scale)
    )
    axs[2].set_xlabel('Signal Magnitude $M$')
    axs[2].set_ylabel('$P(M)$')
    if len(imagesa) > 1:
        title2 = (
            'ROI Noise Statistics [%s:%d elements]' %
            (info['Coil'], len(imagesa))
        )
    else:
        title2 = 'ROI Noise Statistics [%s: Combined]' % info['Coil']

    axs[2].set_title(title2)
    axs[2].legend()
    axs[2].grid(True)

    # Histogram and normal fit to difference images background
    imin, imax = (
        int(np.ceil(np.min(noise_diff_pixels))),
        int(np.ceil(np.max(noise_diff_pixels)))
    )
    nbins = imax - imin
    range_ = (imin + 0.5,  imax + 0.5)
    n, bins, patches = axs[3].hist(
        noise_diff_pixels, bins=nbins, range=range_,
        density=True, alpha=0.75, label='Histogram'
    )
    # force autoscale calc (for matplotlib >=3.2) and freeze
    axs[3].get_xlim()
    axs[3].get_ylim()
    axs[3].autoscale(False)

    mu, sigma = noise_diff_pixels.mean(), noise_diff_pixels.std()
    y = norm.pdf(bins, loc=mu, scale=sigma)
    axs[3].plot(bins, y, '--', label='Normal fit')

    axs[3].text(0, 0.5 * max(n), r'$\sigma=%0.2f$' % (sigma/image_scale))
    axs[3].set_xlabel('Signal Difference $D$')
    axs[3].set_ylabel('$P(D)$')
    axs[3].set_title('ROI Noise Statistics (Difference Image)')
    axs[3].legend()
    axs[3].grid(True)

    fig.suptitle(
        '%s: %s SNR [%s, BW:%0.0dHz, TR:%0.0d, FA:%0.0d, %s] ' % (
            info['Sequence'], info['Coil'],
            phantom['Name'], info['Bandwidth'], info['TR'], info['FlipAngle'], info['Orient'],
        ),
        fontsize=16
    )
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    # TODO: return both chi and difference based estimates
    # TODO: include some of the info above
    return pd.DataFrame(
        {info['Coil']: [snr_inner_diff, snr_outer_diff]},
        index=[inner_snr_fraction, outer_snr_fraction]
    )
