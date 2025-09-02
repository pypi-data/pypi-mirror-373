#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""geometry.py: Graphical reports of geometric QA parameters."""

# TODO: fill out docstrings numpy style
#       make dataframe returns more consistent
#       adapt to2 report to helper routines here
#       move common helper routines out to 'common' module
from functools import partial

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from scipy.optimize import curve_fit, least_squares
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from scipy.ndimage import zoom
from scipy.signal import savgol_filter

from skimage.exposure import rescale_intensity

from .. dcmio import (
    pix_spacing_yx, protocol_name, series_number, is_multiframe,
    approx_slice_orientation, approx_phase_orientation,
    readout_bandwidth, readout_sensitivity, phase_enc_dirn, is_distortion_corrected
)
from .. phantoms import find_phantom, PIQTDIST, ACRDIST, TO2
from .. tools import (
    edges_and_diameters, add_phase_encode_mark, image_from_dicom, all_images_from_dicom,
    pixel_size, rectangular_roi_coords, rectangular_roi
)


def _find_crossing(roi, invert=True):
    """Get position of grid crossing in image ROI."""
    if invert:
        roi = (roi.max() - roi).astype(float)

    # Crossing point appears as peaks in profiles
    profile_x = savgol_filter(roi.mean(axis=0), 5, 2)
    profile_y = savgol_filter(roi.mean(axis=1), 5, 2)
    cx, cy = profile_x.argmax(), profile_y.argmax()
    return cx, cy


def _find_centroid(roi, invert=False):
    """Get the best fit centroid of a blurred disc in an image ROI."""
    def disc_at(x0, y0, r, s, bg, sigma, nx, ny):
        """
        Construct a blurred disc with background at the given position.

        x0, y0: position
        r: disc size (radius)
        s: disc brightness
        bg: background brightness
        sigma: width of gaussian blur
        nx, ny: size of roi
        """
        assert 0 <= x0 < nx and 0 <= y0 < ny
        assert r > 1
        assert s > 0 and bg >= 0
        assert sigma > 0.5

        # NB: constructed as transpose hence shape=(nx, ny)
        disc = s * np.fromfunction(
            lambda x, y: np.clip(r - np.hypot(x-x0, y-y0), 0, 1),
            shape=(nx, ny)
        ).T + bg
        return gaussian_filter(disc, sigma)

    def model_fun(params, roi=roi):
        """Fit a disc."""
        x, y, r, s, bg, sigma = params
        ny, nx = roi.shape
        model_roi = disc_at(x, y, r, s, bg, sigma, nx, ny)
        return (roi - model_roi).ravel()

    if invert:
        roi = (roi.max() - roi).astype(float)

    # Box constraints on parameters
    window = roi.shape[0]
    lower_bound, initial_value, upper_bound = zip(*[
        (0, window//2, window),  # x
        (0, window//2, window),  # y
        (4, 5, 8),               # r: disc size (radius)
        (0.95*roi.max(), roi.max(), 1.05*roi.max()),  # s: disc brightness
        (0, roi.min(), max(np.median(roi), 1)),  # bg: background intensity
        (0.5, 1.5, 2.0)  # sigma: blurring width
    ])
    cx, cy, r0, s0, bg0, sigma0 = least_squares(
        model_fun,
        x0=initial_value,
        bounds=[lower_bound, upper_bound]
    ).x
    return cx, cy


def _get_position_offsets(image, finder_func,
                          expected_posns, spacing_mm, pix_mm, centre):
    """Get a dict between expected object posns and their posns in image."""
    centre_x, centre_y = centre

    # Size of the boxes in pixels to take from the image
    # around the expected point positions
    # Use the spacing to determine this
    # NB: we want this to be an odd number so there is a central pixel.
    box_size = int(np.ceil(0.5 * spacing_mm / pix_mm) // 2 * 2 + 1)
    box_centre = box_size // 2

    # Find positions of inner points so as to adjust for phantom misalignment
    offsets = {}
    for x_mm, y_mm in expected_posns:
        x = int((x_mm / pix_mm) + centre_x)
        y = int((y_mm / pix_mm) + centre_y)
        patch = image[
            y - box_size//2: y + box_size//2 + 1,
            x - box_size//2: x + box_size//2 + 1
        ].astype(float)
        cx, cy = finder_func(patch)

        cx_mm = (cx - box_centre) * pix_mm
        cy_mm = (cy - box_centre) * pix_mm

        offsets[(x_mm, y_mm)] = (cx_mm, cy_mm)
    return offsets


def _get_rigid_transform(xs, ys, xs_displaced, ys_displaced):
    """Get rigid transformation func between original and displaced points."""
    # Fit rigid transformation to offsets to account for phantom positioning
    # Coordinate arrays will be (2, n)
    from_ = np.vstack([xs, ys])
    to_ = np.vstack([xs_displaced, ys_displaced])

    def rigid_transform(coords, alpha, x_shift, y_shift, shape=from_.shape):
        coords_xy = coords.reshape(shape)
        c, s = np.cos(alpha), np.sin(alpha)
        A = np.array([[c, -s], [s, c]])
        b = np.array([x_shift, y_shift])
        return (A.dot(coords_xy) + b[:, None]).reshape(coords.shape)

    # Best fit transformation parameters
    (alpha, x_shift, y_shift), _ = curve_fit(
        rigid_transform, from_.ravel(), to_.ravel(), p0=(0.0, 0.0, 0.0)
    )

    # Transformation function based on these parameters
    return partial(
        rigid_transform, alpha=alpha, x_shift=x_shift, y_shift=y_shift
    )


def _distortion_report(dobj, finder_func, phantom, frame):
    """
    Report on ACR/PIQT distortion measurements.

    Takes a dicom object which is a single slice through the distortion grid
    and plots the image with an overlay of the marker locations and
    an interpolated position error field.

    """
    # Get image data from single images or multiframes
    image = image_from_dicom(dobj, frame=frame, dtype=float)

    # Pixels dimensions - square pixels only
    pix_mm = pixel_size(dobj)

    # Interpolate up to improve precision
    interpolation_factor = 2
    image = rescale_intensity(zoom(image, interpolation_factor), out_range=(0, 1))
    pix_mm /= interpolation_factor

    # NB we are taking out shifts here, which will be taken out again
    # when we do the rigid fit - do we really need this?
    # if not then can lose the `centre_x` etc setting it to half the image size
    # on the other hand we could plot this fit to show detection of phantom
    # these offsets are image (pixel) space
    radius = phantom['Diameter'] / 2 / pix_mm
    centre_x, centre_y, radius = find_phantom(image, expected_radius=radius)
    # Find positions of inner points so as to adjust for phantom misalignment
    # Results are in phantom (mm) space
    spacing_mm = phantom['FeatureSizes']['InnerPoints']
    offsets = _get_position_offsets(
        image, finder_func,
        phantom['Features']['InnerPoints'],
        spacing_mm=spacing_mm, pix_mm=pix_mm, centre=(centre_x, centre_y)
    )
    (xs_mm, dxs_mm), (ys_mm, dys_mm) = np.asarray(list(offsets.items())).T
    xs_mm_displaced = xs_mm + dxs_mm
    ys_mm_displaced = ys_mm + dys_mm

    # Fit rigid transform to offsets to account for phantom positioning
    # NB: This is all still in phantom (mm) space
    transform = _get_rigid_transform(
        xs_mm, ys_mm, xs_mm_displaced, ys_mm_displaced
    )

    # Apply transformation to full set of points
    shifted_features = [
        tuple(transform(np.array([x, y]), shape=(2, 1)))
        for (x, y) in phantom['Features']['GridPoints']
    ]

    # Find positions of all markers relative to the offset positions
    offsets = _get_position_offsets(
        image, finder_func, shifted_features,
        spacing_mm=spacing_mm, pix_mm=pix_mm, centre=(centre_x, centre_y)
    )
    (xs_mm, dxs_mm), (ys_mm, dys_mm) = np.asarray(list(offsets.items())).T

    # Horizontal scale - indices of features down the left and right edges sorted into pairs
    min_x = min(x for (x, _) in phantom['Features']['GridPoints'])
    max_x = max(x for (x, _) in phantom['Features']['GridPoints'])
    hmargins = sorted(
        (y, x, i) for i, (x, y) in enumerate(phantom['Features']['GridPoints'])
        if x in (min_x, max_x)
    )
    hmargins = [i for (_, _, i) in hmargins]

    # Distances between the paired end points
    horizontal_dists_mm = [
        np.hypot(
            xs_mm[j] + dxs_mm[j] - xs_mm[i] + dxs_mm[i],
            ys_mm[j] + dys_mm[j] - ys_mm[i] + dys_mm[i]
        )
        for (i, j) in zip(hmargins[:-1:2], hmargins[1::2])
    ]

    # Horizontal scale - indices of features along the upper and lower edges sorted into pairs
    min_y = min(y for (_, y) in phantom['Features']['GridPoints'])
    max_y = max(y for (_, y) in phantom['Features']['GridPoints'])
    vmargins = sorted(
        (x, y, i) for i, (x, y) in enumerate(phantom['Features']['GridPoints'])
        if y in (min_y, max_y)
    )
    vmargins = [i for (_, _, i) in vmargins]

    # Distances between the end points
    vertical_dists_mm = [
        np.hypot(
            xs_mm[j] + dxs_mm[j] - xs_mm[i] + dxs_mm[i],
            ys_mm[j] + dys_mm[j] - ys_mm[i] + dys_mm[i]
        )
        for (i, j) in zip(vmargins[:-1:2], vmargins[1::2])
    ]

    # Statistics for scale and distortion
    mean_h = np.mean(horizontal_dists_mm)
    mean_v = np.mean(vertical_dists_mm)
    std_h = np.std(horizontal_dists_mm)
    std_v = np.std(vertical_dists_mm)

    pcent_distort_h = 100 * std_h / mean_h
    pcent_distort_v = 100 * std_v / mean_v

    # Image shaped grid for colour overlay
    ny, nx = image.shape
    grid_y, grid_x = np.mgrid[0:nx, 0:ny]

    # Positions on overlay are in pixels
    xs_pixels = (xs_mm / pix_mm) + centre_x
    ys_pixels = (ys_mm / pix_mm) + centre_y
    points = np.vstack([xs_pixels, ys_pixels]).T

    # But interpolated values in colour map will be in mm
    values = np.hypot(dxs_mm, dys_mm)
    grid = griddata(points, values, (grid_x, grid_y), method='linear')

    # Plotting area including text box at bottom
    fig = plt.figure(figsize=(12, 6))
    gs = plt.GridSpec(6, 2, fig)
    axs = [
        fig.add_subplot(gs[:5, 0]),
        fig.add_subplot(gs[:5, 1]),
        fig.add_subplot(gs[5, :2])
    ]

    axs[0].imshow(image, cmap='bone')
    axs[0].axis('off')
    axs[0].grid(False)

    # Over plot the marker positions and their displacements
    axs[0].scatter(
        xs_pixels, ys_pixels,
        s=60, marker='o', facecolors='none', edgecolors='red'
    )
    xs_displaced_pixels = ((xs_mm + dxs_mm) / pix_mm) + centre_x
    ys_displaced_pixels = ((ys_mm + dys_mm) / pix_mm) + centre_y
    axs[0].scatter(
        xs_displaced_pixels, ys_displaced_pixels,
        s=100, marker='+', color='green'
    )

    # Colour wash of position error in mm
    cmap = 'cividis' if 'cividis' in plt.colormaps() else 'viridis'
    im = axs[0].imshow(grid, cmap=cmap, alpha=0.5)

    # Show phase encoding direction
    add_phase_encode_mark(axs[0], phase_enc_dirn(dobj))

    # Show labels for distortion correction etc
    labels = []
    try:
        dcorrn_status = 'ON' if is_distortion_corrected(dobj) else 'OFF'
        labels.append('DC:%s' % dcorrn_status)
    except KeyError:
        pass
    if labels:
        axs[0].text(
            0.1, 0.95, '\n'.join(labels),
            color='white',
            horizontalalignment='center',
            verticalalignment='center',
            transform=axs[0].transAxes
        )

    # Add colour bar fitted to plot height
    divider = make_axes_locatable(axs[0])
    cax = divider.append_axes("right", size="5%", pad=0.05)
    clb = fig.colorbar(im, cax=cax)
    clb.set_label('Positional Error (mm)')

    axs[0].set_title('Distortion Map')

    im = axs[1].imshow(image, cmap='bone')
    axs[1].axis('off')
    axs[1].grid(False)

    for (i, j) in zip(hmargins[:-1:2], hmargins[1::2]):
        x_a = ((xs_mm[i] + dxs_mm[i]) / pix_mm) + centre_x
        y_a = ((ys_mm[i] + dys_mm[i]) / pix_mm) + centre_y
        x_b = ((xs_mm[j] + dxs_mm[j]) / pix_mm) + centre_x
        y_b = ((ys_mm[j] + dys_mm[j]) / pix_mm) + centre_y
        separation_mm = np.hypot(
            xs_mm[j] + dxs_mm[j] - xs_mm[i] + dxs_mm[i],
            ys_mm[j] + dys_mm[j] - ys_mm[i] + dys_mm[i]
        )
        axs[1].plot([x_a, x_b], [y_a, y_b], color='C1')
        axs[1].text(
            x_b, y_b, ' %0.1f' % separation_mm, color='C1'
        )

    for (i, j) in zip(vmargins[:-1:2], vmargins[1::2]):
        x_a = ((xs_mm[i] + dxs_mm[i]) / pix_mm) + centre_x
        y_a = ((ys_mm[i] + dys_mm[i]) / pix_mm) + centre_y
        x_b = ((xs_mm[j] + dxs_mm[j]) / pix_mm) + centre_x
        y_b = ((ys_mm[j] + dys_mm[j]) / pix_mm) + centre_y
        separation_mm = np.hypot(
            xs_mm[j] + dxs_mm[j] - xs_mm[i] + dxs_mm[i],
            ys_mm[j] + dys_mm[j] - ys_mm[i] + dys_mm[i]
        )
        axs[1].plot([x_a, x_b], [y_a, y_b], color='C2')
        axs[1].text(
            x_b, y_b, ' %0.1f' % separation_mm, color='C2', rotation=-45
        )

    # Dummy axis to match colour bar - just to keep image size the same
    divider = make_axes_locatable(axs[1])
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cax.axis('off')

    axs[1].set_title(
        '[H: %0.1f mm %0.2f%%, V: %0.1f mm %0.2f%%]' %
        (mean_h, pcent_distort_h, mean_v, pcent_distort_v)
    )

    axs[2].axis(False)
    text = '\n'.join([
        'Horizontal Scale / Distortion: %0.1f mm / %0.2f%%' % (mean_h, pcent_distort_h),
        'Vertical Scale / Distortion:   %0.1f mm / %0.2f%%' % (mean_v, pcent_distort_v)
    ])
    axs[2].text(
        0, 0.9, text,
        verticalalignment='top', horizontalalignment='left',
        transform=axs[2].transAxes,
        color='black', fontsize=12
    )

    return pd.DataFrame.from_dict({
        'Series':               [series_number(dobj)],
        'Protocol':             [protocol_name(dobj)],
        'Orientation':          [approx_slice_orientation(dobj)],
        'PhaseDirection':       [approx_phase_orientation(dobj)],
        'PixelBandwidth':       [readout_bandwidth(dobj)],  # Hz/pix
        'Sensitivity':          [readout_sensitivity(dobj)],  # mm/ppm
        'HorizontalScale':      [mean_h],  # mm
        'HorizontalDistortion': [pcent_distort_h],  # % deviation
        'VerticalScale':        [mean_v],
        'VerticalDistortion':   [pcent_distort_v]
    }).set_index('Series')


def piqt_distortion_report(dobj, finder_func=_find_centroid,
                           phantom=PIQTDIST, frame=None):
    """
    Report on PIQT distortion measurements.

    Takes a dicom object which is a single slice through the distortion grid
    and plots the image with an overlay of the marker locations and
    an interpolated position error field.

    """
    return _distortion_report(dobj, finder_func, phantom, frame)


def acr_distortion_report(dobj, finder_func=_find_crossing,
                          phantom=ACRDIST, frame=None):
    """
    Report on ACR distortion measurements.

    Takes a dicom object which is a single slice through the distortion grid
    and plots the image with an overlay of the marker locations and
    an interpolated position error field.

    """
    return _distortion_report(dobj, finder_func, phantom, frame)


def to2_distortion_report(dobj, flipped_ud=False, flipped_rl=False,
                          phantom=TO2, frame=None):
    """
    Report on TO2 distortion measurements.

    Takes a dicom object which is a single slice around the middle
    of the phantom and plots the image with the distortion box positions
    marked on, the extracted ROI with the profiles marked on
    and the estinated values for the image scaling and distortion.
    Assumes a known size for the distortion box (120mm square in TO2).

    Parameters
    ----------
    dobj: pydicom dicom object
        image to consider
    flipped_ud: bool
        whether image is flipped vertically
    flipped_rl: bool
        whether image is flipped horizontally
    phantom: dict
        description of phantom
    frame: int
        specific frame of multiframe

    Returns
    -------
    dataframe: nominal_diameter, measured_diameter, deviation, fitted_deviation


    """
    # Get image data and reorient if need be
    image = image_from_dicom(dobj, frame)
    pixel_spacing = pix_spacing_yx(dobj)

    if flipped_ud:
        image = np.flipud(image)
    if flipped_rl:
        image = np.fliplr(image)

    pix_dims = np.asarray(pixel_spacing)

    # Plotting area including text box at bottom
    fig = plt.figure(figsize=(12, 6))
    gs = plt.GridSpec(6, 2, fig)
    axs = [
        fig.add_subplot(gs[:5, 0]),
        fig.add_subplot(gs[:5, 1]),
        fig.add_subplot(gs[5, :2])
    ]
    fig.subplots_adjust(wspace=0.5)

    # Show phantom image
    axs[0].imshow(image, cmap='bone')
    axs[0].axis('off')
    axs[0].axis('image')

    # Show phase encoding direction
    add_phase_encode_mark(axs[0], phase_enc_dirn(dobj))

    # Show labels for distortion correction etc
    labels = []
    try:
        dcorrn_status = 'ON' if is_distortion_corrected(dobj) else 'OFF'
        labels.append('DC:%s' % dcorrn_status)
    except KeyError:
        pass
    if labels:
        axs[0].text(
            0.1, 0.95, '\n'.join(labels),
            color='white',
            horizontalalignment='center',
            verticalalignment='center',
            transform=axs[0].transAxes
        )

    # Find centre of phantom in pixel coords
    expected_radius = phantom['Diameter'] / 2 / pix_dims[0]
    centre_x, centre_y, _ = find_phantom(image, expected_radius)
    centre = centre_x, centre_y

    # Positions of distortion box
    box = phantom['Features']['Boxes'][0]
    boxsize = phantom['FeatureSizes']['Boxes'][0]

    # Outer bounding rectangle for distortion box
    x, y, dx, dy = rectangular_roi_coords(pix_dims, box, centre)
    axs[0].add_artist(
        plt.Rectangle([x, y], dx, dy, fill=False, edgecolor='r')
    )

    # Inner bounding rectangle for distortion box
    x, y, dx, dy = rectangular_roi_coords(
        pix_dims,
        np.array(box) + [[boxsize, boxsize], [-2*boxsize, -2*boxsize]],
        centre
    )
    axs[0].add_artist(
        plt.Rectangle([x, y], dx, dy, fill=False, edgecolor='r')
    )
    axs[0].set_title('%s' % protocol_name(dobj))

    # Outer bounding rectangle for distortion box to select ROI
    box_roi = rectangular_roi(image, pix_dims, box, centre).copy()

    # Foreground fill inner region using average of boundary pixels
    margin_x, margin_y = np.round(
        np.array([boxsize, boxsize]) / pix_dims
    ).astype(int)
    fill_value = (
        np.mean(box_roi[margin_y, margin_x:-margin_x]) +
        np.mean(box_roi[-margin_y, margin_x:-margin_x]) +
        np.mean(box_roi[margin_y:-margin_y, margin_x]) +
        np.mean(box_roi[margin_y:-margin_y, -margin_x])
    ) / 4
    box_roi[margin_y:-margin_y, margin_x:-margin_x] = fill_value

    # Interpolate up for smoother profiles
    zoom_factor = 4
    box_roi = zoom(box_roi, zoom_factor)
    pix_dims = pix_dims / zoom_factor

    # Show Region of Interest
    axs[1].imshow(box_roi, cmap='bone')
    axs[1].axis('off')
    axs[1].axis('image')

    # Horizontal profiles (inverted)
    row_h1 = box_roi.shape[0] // 4
    profile_h1 = np.mean(box_roi[row_h1-1:row_h1+2, :], axis=0)
    profile_h1 = profile_h1[len(profile_h1)//2] - profile_h1

    row_h2 = box_roi.shape[0] // 2
    profile_h2 = np.mean(box_roi[row_h2-1:row_h2+2, :], axis=0)
    profile_h2 = profile_h2[len(profile_h2)//2] - profile_h2

    row_h3 = 3 * box_roi.shape[0] // 4
    profile_h3 = np.mean(box_roi[row_h3-1:row_h3+2, :], axis=0)
    profile_h3 = profile_h3[len(profile_h3)//2] - profile_h3

    # Overlay horizontal profiles on ROI image
    im_height = box_roi.shape[0]
    profile_height = np.max(profile_h1)
    axs[1].plot(row_h1 - profile_h1 / profile_height * im_height / 10)
    axs[1].plot(row_h2 - profile_h2 / profile_height * im_height / 10)
    axs[1].plot(row_h3 - profile_h3 / profile_height * im_height / 10)

    # Horizontal Separations
    profile_len = len(profile_h1)
    d_h1a = np.argmax(profile_h1[:profile_len//4])
    d_h1b = np.argmax(profile_h1[-profile_len//4:])
    dist_h1_pix = (d_h1b + profile_len - profile_len//4 - d_h1a)
    dist_h1_mm = dist_h1_pix * pix_dims[1]

    d_h2a = np.argmax(profile_h2[:profile_len//4])
    d_h2b = np.argmax(profile_h2[-profile_len//4:])
    dist_h2_pix = (d_h2b + profile_len - profile_len//4 - d_h2a)
    dist_h2_mm = dist_h2_pix * pix_dims[1]

    d_h3a = np.argmax(profile_h3[:profile_len//4])
    d_h3b = np.argmax(profile_h3[-profile_len//4:])
    dist_h3_pix = (d_h3b + profile_len - profile_len//4 - d_h3a)
    dist_h3_mm = dist_h3_pix * pix_dims[1]

    text_delta = profile_len / 30
    axs[1].text(d_h1a + text_delta, row_h1 - text_delta, '%0.2f' % dist_h1_mm)
    axs[1].text(d_h2a + text_delta, row_h2 - text_delta, '%0.2f' % dist_h2_mm)
    axs[1].text(d_h3a + text_delta, row_h3 - text_delta, '%0.2f' % dist_h3_mm)

    # Vertical profiles (inverted)
    col_v1 = box_roi.shape[1] // 4
    profile_v1 = np.mean(box_roi[:, col_v1-1:col_v1+2], axis=1)
    profile_v1 = profile_v1[len(profile_v1)//2] - profile_v1

    col_v2 = box_roi.shape[1] // 2
    profile_v2 = np.mean(box_roi[:, col_v2-1:col_v2+2], axis=1)
    profile_v2 = profile_v2[len(profile_v2)//2] - profile_v2

    col_v3 = 3 * box_roi.shape[1] // 4
    profile_v3 = np.mean(box_roi[:, col_v3-1:col_v3+2], axis=1)
    profile_v3 = profile_v3[len(profile_v3)//2] - profile_v3

    # Overlay vertical profiles on ROI image
    im_width = box_roi.shape[1]
    profile_height = np.max(profile_v1)
    axs[1].plot(
        col_v1 + profile_v1/profile_height * im_width/10,
        list(range(len(profile_v1)))
    )
    axs[1].plot(
        col_v2 + profile_v2/profile_height * im_width/10,
        list(range(len(profile_v2)))
    )
    axs[1].plot(
        col_v3 + profile_v3/profile_height * im_width/10,
        list(range(len(profile_v3)))
    )

    # Vertical Separations
    profile_len = len(profile_v1)
    d_v1a = np.argmax(profile_v1[:profile_len//4])
    d_v1b = np.argmax(profile_v1[-profile_len//4:])
    dist_v1_pix = (d_v1b + profile_len - profile_len//4 - d_v1a)
    dist_v1_mm = dist_v1_pix * pix_dims[0]

    d_v2a = np.argmax(profile_v2[:profile_len//4])
    d_v2b = np.argmax(profile_v2[-profile_len//4:])
    dist_v2_pix = (d_v2b + profile_len - profile_len//4 - d_v2a)
    dist_v2_mm = dist_v2_pix * pix_dims[0]

    d_v3a = np.argmax(profile_v3[:profile_len//4])
    d_v3b = np.argmax(profile_v3[-profile_len//4:])
    dist_v3_pix = (d_v3b + profile_len - profile_len//4 - d_v3a)
    dist_v3_mm = dist_v3_pix * pix_dims[0]

    dists_h_mm = [dist_h1_mm, dist_h2_mm, dist_h3_mm]
    dists_v_mm = [dist_v1_mm, dist_v2_mm, dist_v3_mm]

    text_delta = profile_len / 30
    axs[1].text(col_v1 + text_delta, d_v1a + text_delta, '%0.2f' % dist_v1_mm)
    axs[1].text(col_v2 + text_delta, d_v2a + text_delta, '%0.2f' % dist_v2_mm)
    axs[1].text(col_v3 + text_delta, d_v3a + text_delta, '%0.2f' % dist_v3_mm)

    mean_h = np.mean(dists_h_mm)
    mean_v = np.mean(dists_v_mm)
    std_h = np.std(dists_h_mm)
    std_v = np.std(dists_v_mm)

    pcent_distort_h = 100 * std_h / mean_h
    pcent_distort_v = 100 * std_v / mean_v

    axs[1].set_title(
        '[H: %0.1f mm %0.3f %%, V: %0.1f mm %0.3f %%]' %
        (mean_h, pcent_distort_h, mean_v, pcent_distort_v)
    )

    axs[2].axis(False)
    text = '\n'.join([
        'Horizontal Scale / Distortion: %0.1f mm / %0.2f %%' % (mean_h, pcent_distort_h),
        'Vertical Scale / Distortion:   %0.1f mm / %0.2f %%' % (mean_v, pcent_distort_v)
    ])
    axs[2].text(
        0, 0.9, text,
        verticalalignment='top', horizontalalignment='left',
        transform=axs[2].transAxes,
        color='black', fontsize=12
    )

    return pd.DataFrame.from_dict({
        'Series':               [series_number(dobj)],
        'Protocol':             [protocol_name(dobj)],
        'Orientation':          [approx_slice_orientation(dobj)],
        'PhaseDirection':       [approx_phase_orientation(dobj)],
        'PixelBandwidth':       [readout_bandwidth(dobj)],  # Hz/pix
        'Sensitivity':          [readout_sensitivity(dobj)],  # mm/ppm
        'HorizontalScale':      [mean_h],  # mm
        'HorizontalDistortion': [pcent_distort_h],  # % deviation
        'VerticalScale':        [mean_v],
        'VerticalDistortion':   [pcent_distort_v]
    }).set_index('Series')


def circularity_report(dobj, phantom, interpolation_factor=4, excluded_sector=0, frame=None, axes=None):
    """
    Report on circularity of phantom image.

    Non-circularity is taken as an indication of image distortion.
    Includes raw and fiited plots of phantom diamater as function of angle.

    Parameters
    ----------
    dobj: pydicom dicom object
        image to consider
    phantom: dict
        description of phantom
    interpolation_factor: Opt[float]
        scaling factor to use to increase 'resolution' of image
    excluded_sector: Opt[float]
        angle in degrees to exclude to handle bubbles
    frame: int
        specific frame of multiframe
    axes: Opt[matplotlib axes object]

    Returns
    -------
    dataframe: nominal_diameter, measured_diameter, deviation, fitted_deviation

    """

    # Assume if we have multiple frames and no frame specified they can be just averaged together
    if is_multiframe(dobj) and frame is None:
        image = all_images_from_dicom(dobj, float)
        image = image.mean(axis=tuple(range(image.ndim-2)))
    else:
        image = image_from_dicom(dobj, frame, float)

    # Voxel geometry - require square pixels
    dy, dx = pix_spacing_yx(dobj)
    assert np.isclose(dx, dy)

    # Interpolate to get reasonable accuracy
    image = rescale_intensity(zoom(image, interpolation_factor))
    dy /= interpolation_factor
    dx /= interpolation_factor

    # Initial phantom centre/radius estimate from image
    expected_radius_pixels = phantom['Diameter'] / 2 / dx
    centre_x, centre_y, radius = find_phantom(image, expected_radius_pixels)

    # Fitted diameters from radial profiles
    theta, edge_a, edge_b, diameters, fitted_diameters = edges_and_diameters(
        image,
        centre_x, centre_y,
        radius=radius,
        ntheta=45,
        excluded_sector=excluded_sector
    )

    # Convert result from pixels to mm
    edge_a *= dx
    edge_b *= dx
    diameters *= dx
    fitted_diameters *= dx

    deviation = np.ptp(diameters) / 2
    fitted_deviation = np.ptp(fitted_diameters) / 2

    if axes is None or len(axes) < 4:
        fig, axs = plt.subplots(1, 2, figsize=(10, 4))
        axs = axs.T.ravel()
    else:
        axs = axes
        fig = axs[0].get_figure()

    axs[0].plot(np.degrees(theta), edge_a)
    axs[0].plot(np.degrees(theta), edge_b)
    axs[0].text(
        0.125, 0.5,
        'Mean Diameter: %0.1f mm' % diameters.mean(),
        transform=axs[0].transAxes
    )
    axs[0].set_xlabel(r'Angle $\theta^\circ$')
    axs[0].set_ylabel(r'Profile Position (mm)')
    axs[0].autoscale(enable=True, axis='x', tight=True)
    axs[0].grid(True)
    axs[0].set_title('Edge Positions')

    axs[1].plot(np.degrees(theta), diameters, '.')
    axs[1].plot(np.degrees(theta), fitted_diameters, '-')
    axs[1].text(
        0.125, 0.5,
        r'Fitted Deviation: $\pm %0.2f$ mm' % fitted_deviation,
        transform=axs[1].transAxes
    )
    axs[1].text(
        0.125, 0.6,
        r'Raw Deviation: $\pm %0.2f$ mm' % deviation,
        transform=axs[1].transAxes
    )
    axs[1].set_xlabel(r'Angle $\theta^\circ$')
    axs[1].set_ylabel(r'Profile Length (mm)')
    axs[1].axis('tight')
    axs[1].grid(True)
    axs[1].set_title('Phantom Diameters')

    fig.suptitle('Scale and Circularity [%s]' % phantom['Name'], fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    return pd.DataFrame({
        'Nominal': phantom['Diameter'],
        'Diameter': diameters.mean(),
        'Deviation': deviation,
        'FittedDeviation': fitted_deviation
    }, index=[phantom['Name']])
