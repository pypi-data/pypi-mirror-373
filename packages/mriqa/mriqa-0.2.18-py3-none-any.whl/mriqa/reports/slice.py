#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""slice.py: graphical reports of QA slice parameters."""

from functools import partial

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.ndimage import zoom as ndizoom
from scipy.stats.mstats import gmean
from scipy.interpolate import UnivariateSpline

from skimage.exposure import rescale_intensity
from skimage.transform import rotate as skirotate
from skimage.transform import hough_line, hough_line_peaks
from skimage.feature import canny

from .. phantoms import TO2, ACRSP, PIQTSP, find_phantom
from .. dcmio import (
    pix_spacing_yx, slice_thickness, series_number, phase_enc_dirn
)
from .. tools import rx_coil_string, image_from_dicom, rectangular_roi_coords, add_phase_encode_mark


def _get_phantom_roi_coords(pix_dims, rect, centre):
    """
    Get phantom coordinates of a rectangle image ROI.

    The rectangle is specified as (x, y, dx, dy) in pixels.
    The ROI is shifted according to specified phantom centre (NB in pixels).
    The returned specification (x, y), (dx, dy) is in mm.
    """
    x, y, dx, dy = rect
    centre_x, centre_y = centre
    pix_y, pix_x = pix_dims
    x = (x - centre_x) * pix_x
    y = (y - centre_y) * pix_y
    dx = dx * pix_x
    dy = dy * pix_y
    return (x, y), (dx, dy)


def _opt_angle_hough(image):
    """
    Phantom rotation angle based in vertical and horizontal edges.

    Uses Hough line transform to determine small angular misalignments
    of phantom with respect to linear features. Returns angle in radians.

    """
    assert len(image.shape) == 2
    assert np.amax(image) != np.amin(image)

    # Normalize
    image = np.asarray(image, dtype='float')
    image = (image - np.amin(image)) / (np.amax(image) - np.amin(image))

    # Edges
    edges = canny(image, sigma=2, low_threshold=0.1, high_threshold=0.5)

    # Hough Angles
    _, angles, _ = hough_line_peaks(*hough_line(edges))

    # Fix to get angles as deviations from horizontal and vertical.
    angles = [
        angle - np.pi/2 if angle > np.pi/4 else
        angle + np.pi/2 if angle < -np.pi/4 else angle
        for angle in angles
    ]
    return np.mean(angles)


def _refine_adjacent_regions(image, plates, pix_dims, centre):
    """
    Refine box ROI by finding edges.

    This is for the ACR phantom that has a very narrow letter box ROI.

    TODO: NB: this is very ACR specific as it assumes we a have horizontal
    TODO: letter box with sub-regions that are nearly contiguous vertically
    TODO: and clear edges surrounding the region
    """
    # Plates in image space
    rois = [
        rectangular_roi_coords(pix_dims, rect=plate, centre=centre)
        for plate in plates
    ]

    # Bounding box for all the ROIs together
    y0 = min(y for _, y, _, _ in rois)
    yn = max(y + dy for _, y, _, dy in rois)
    dy = yn - y0

    x0 = min(x for x, _, _, _ in rois)
    xn = max(x + dx for x, _, dx, _ in rois)
    dx = xn - x0

    # Increase size of this region in y to include edges
    y0 -= dy // 2
    yn += dy // 2
    dy = yn - y0

    # Extract region from image and generate vertical profile
    profile = image[y0:yn, x0:xn].mean(axis=1)

    # Find edges of region in y and reduce to integer indices
    profile -= (np.max(profile) - np.min(profile)) / 2
    r1, r2 = UnivariateSpline(np.arange(len(profile)), profile, s=0).roots()
    new_y0, new_yn = y0 + int(round(r1)), y0 + int(round(r2))

    # Adjust to avoid edges etc
    margin = 2
    new_y0 += margin
    new_yn -= margin
    new_dy = new_yn - new_y0

    # Split up evenly into sub regions according to the number of original ROIS
    nplates = len(plates)
    rois = [
        (x0, new_y0 + i * new_dy // nplates, dx, new_dy // nplates)
        for i in range(nplates)
    ]

    # Transform back to phantom space
    plates = [
        _get_phantom_roi_coords(pix_dims, roi, centre) for roi in rois
    ]

    return plates


def _contrast_is_negative(x):
    """Heuristic for whether profile is negative or positive."""
    nx = len(x)
    middle = x[nx//4:3*nx//4].mean()
    ends = np.hstack([x[:nx//4], x[-nx//4:]]).mean()
    return middle < ends


def _half_height_crossings(x):
    """
    Find half maximum positions in profile .

    Shifts profile to move its half-height to zero and uses spline
    to find zero crossings.
    """
    x = np.asarray(x)
    assert x.ndim == 1

    # find the zero crossings (no smoothing)
    half_height = x.max() / 2
    roots = UnivariateSpline(
        np.arange(len(x)), x - half_height, s=0
    ).roots()

    # handle multiple adjacent roots due to noise
    if len(roots) > 2:
        # assume sorted
        splits = np.array([
            (roots[:i].mean(), roots[i:].mean())
            for i in range(1, len(roots))
        ])
        r1, r2 = splits[
            np.argmax(splits[:, 1] - splits[:, 0])
        ]
    else:
        r1, r2 = roots
    return r1, r2


def _normalise_profile(profile):
    """
    Clean profile to zero baseline positive going peak.

    If the profile is negative then invert it and normalise
    to a linear baseline fitted to the profile ends, otherwise
    just subtract off background and normalise height
    """
    x = list(range(20)) + list(range(len(profile)-20, len(profile)))
    if _contrast_is_negative(profile):
        baseline = np.poly1d(
            np.polyfit(x, profile[x], 1)
        )(np.arange(len(profile)))
        profile /= baseline
        profile = 1 - profile
        # axes[1].plot(baseline_1, linewidth=0.33, color='C2')
    else:
        profile -= profile[x].mean()
        profile /= profile.max()

    return profile


def common_slice_profile_report(
        dobj, frame=None,
        flipped_ud=False, flipped_rl=False, transposed=False, rotate=False,
        adjust=False, phantom=TO2, plate_angle=None, coil=None, axis=None):
    """
    Report on slice profile measurement.

    Takes a DICOM object which is a single slice of phantom where the plate
    profiles are reasonably central.

    Plots the image with the profile positions marked on, the raw profile and a
    normalised profile accounting for a multiplicative bias field.

    The FWHM is reported in mm for each profile individually and for their
    geometric mean.

    """
    # Get single slice image data, handle multiframes
    image = image_from_dicom(dobj, frame)
    if image.dtype == 'int32' and np.all(image >= 0):
        image = image.astype('uint32')

    pixel_spacing = pix_spacing_yx(dobj)
    slice_thick = slice_thickness(dobj)

    coil = rx_coil_string(dobj, coil)

    pe_dirn = phase_enc_dirn(dobj)

    # Allow for non standard phantom positioning
    if flipped_ud:
        image = np.flipud(image)
    if flipped_rl:
        image = np.fliplr(image)
    if transposed:
        image = image.T
        # switch apparent direction if image is transposed
        pe_dirn = 'COL' if pe_dirn == 'ROW' else 'ROW'

    if plate_angle is None:
        plate_angle = phantom['FeatureAngles']['Plates']
    # In degrees, normally 11.7 for TO2, about 6 degrees for ACR
    assert 0 < plate_angle < 45

    if axis is None:
        axis = phantom['FeatureAxes']['Plates']
    assert axis in (0, 1)

    # Interpolate up for analysis, NB change of pixel size
    interpolation_factor = 2
    image = rescale_intensity(
        ndizoom(image, interpolation_factor),
        out_range=(image.min(), image.max())
    )
    pix_dims = np.asarray(pixel_spacing) / interpolation_factor

    # Assume square pixels
    assert np.allclose(pix_dims[0], pix_dims[1])

    # Centre phantom
    expected_radius = phantom['Diameter'] / 2 / pix_dims[0]
    centre_x, centre_y, _ = find_phantom(image, expected_radius)
    centre = centre_x, centre_y

    # Adjust phantom rotation to align to vertical and horizontal edges
    if rotate:
        opt_angle = _opt_angle_hough(image)
        image = skirotate(
            image, np.degrees(opt_angle), center=(centre_y, centre_x)
        )

    # Expected positions of plates
    plates = phantom['Features']['Plates']
    if adjust:
        # specific ACR handling for narrow adjacent regions
        plates = _refine_adjacent_regions(image, plates, pix_dims, centre)

    # Plotting area including text box at bottom
    fig = plt.figure(figsize=(16, 6))
    fig.subplots_adjust(wspace=0.5)
    gs = plt.GridSpec(4, 3, fig)
    axs = [
        fig.add_subplot(gs[:3, 0]),
        fig.add_subplot(gs[:3, 1]),
        fig.add_subplot(gs[:3, 2]),
        fig.add_subplot(gs[3, :3])
    ]

    # Phantom image plot
    axs[0].imshow(image, cmap='bone')
    axs[0].axis('off')
    axs[0].axis('image')
    add_phase_encode_mark(axs[0], pe_dirn)

    # Thick profile through first inclined plate
    x, y, dx, dy = rectangular_roi_coords(
        pix_dims, rect=plates[0], centre=centre
    )
    profile_1 = np.mean(image[y:y+dy, x:x+dx], axis=1 if axis == 0 else 0)

    # Show profile on phantom
    axs[0].add_artist(
        plt.Rectangle(
            [x, y], dx, dy, color='C0', alpha=0.25
        )
    )

    # Thick profile through second inclined plate
    x, y, dx, dy = rectangular_roi_coords(
        pix_dims, rect=plates[1], centre=centre
    )
    profile_2 = np.mean(image[y:y+dy, x:x+dx], axis=1 if axis == 0 else 0)

    # Show profile on phantom
    axs[0].add_artist(
        plt.Rectangle(
            [x, y], dx, dy, color='C1', alpha=0.25
        )
    )

    axs[0].set_title(
        r'Series %d, Image %d' %
        (series_number(dobj), dobj.InstanceNumber)
    )

    # Raw profiles plot
    axs[1].plot(profile_1, label='1')
    axs[1].plot(profile_2, label='2')
    axs[1].set_xlabel('Pixel Position')
    axs[1].set_ylabel('Image Brightness (Raw)')
    axs[1].set_title('%s Coil (%1.0f mm)' % (coil, slice_thick))
    axs[1].legend()
    axs[1].grid(True)

    # Make profiles positive and remove any baseline
    profile_1 = _normalise_profile(profile_1)
    profile_2 = _normalise_profile(profile_2)

    # Normalised profiles plot
    axs[2].plot(profile_1, label='1')
    axs[2].plot(profile_2, label='2')
    axs[2].set_xlabel('Pixel Position')
    axs[2].set_ylabel('Image Brightness (Normalised to Baseline)')
    axs[2].set_title('%s Coil (%1.0f mm)' % (coil, slice_thick))
    axs[2].legend()
    axs[2].grid(True)

    r1, r2 = _half_height_crossings(profile_1)
    fwhm_1_pixels = r2 - r1
    axs[2].axvspan(r1, r2, facecolor='C0', alpha=0.25)

    r1, r2 = _half_height_crossings(profile_2)
    fwhm_2_pixels = r2 - r1
    axs[2].axvspan(r1, r2, facecolor='C1', alpha=0.25)

    # Calc. FWHM in mm taking account of pixel rescaling and plate proj angle
    _, yspacing = pix_dims

    fwhm_gm_pixels = gmean([fwhm_1_pixels, fwhm_2_pixels])

    fwhm_1_mm = fwhm_1_pixels * yspacing * np.tan(np.radians(plate_angle))
    fwhm_2_mm = fwhm_2_pixels * yspacing * np.tan(np.radians(plate_angle))

    fwhm_gm_mm = gmean([fwhm_1_mm, fwhm_2_mm])

    axs[3].axis(False)
    text = '\n'.join([
        'Plate Angle  = %0.1f degrees' % plate_angle,
        'FWHM     (1) = %0.1f pixels, or %0.1f mm' % (round(fwhm_1_pixels, 1), round(fwhm_1_mm, 1)),
        'FWHM     (2) = %0.1d pixels, or %0.1f mm' % (round(fwhm_2_pixels, 1), round(fwhm_2_mm, 1)),
        'FWHM (GMEAN) = %0.1d pixels, or %0.1f mm' % (round(fwhm_gm_pixels, 1), round(fwhm_gm_mm, 1))

    ])
    axs[3].text(
        0, 0.9, text,
        verticalalignment='top', horizontalalignment='left',
        transform=axs[3].transAxes,
        color='black', fontsize=12
    )

    return pd.DataFrame(
        [(
            slice_thick, fwhm_1_pixels, fwhm_1_mm, fwhm_2_pixels,
            fwhm_2_mm, fwhm_gm_pixels, fwhm_gm_mm
        )],
        columns=[
            'SliceThickness', 'FWHM1Pixels', 'FWHM1MM', 'FWHM2Pixels',
            'FWHM2MM', 'FWHMGMeanPixels', 'FWHMGMeanMM'
        ]
    ).set_index('SliceThickness')


piqt_slice_profile_report = partial(common_slice_profile_report, phantom=PIQTSP)
acr_slice_profile_report = partial(common_slice_profile_report, phantom=ACRSP)
to2_slice_profile_report = partial(common_slice_profile_report, phantom=TO2)
