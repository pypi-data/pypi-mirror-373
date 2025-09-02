#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    resolution.py: graphical reports of QA resolution parameters
"""

from warnings import warn

import numpy as np
from numpy.fft import rfft
import pandas as pd

import matplotlib.pyplot as plt

from scipy.ndimage import rotate as ndirotate
from scipy.ndimage import zoom as ndizoom
from scipy.signal import correlate
from scipy.signal.windows import hamming

from scipy.optimize import curve_fit
from scipy.integrate import cumulative_trapezoid
from scipy.special import erf, sici
from scipy.interpolate import interp1d

from skimage.morphology import binary_erosion, binary_dilation, disk
from skimage.feature import canny
from skimage.transform import hough_line, hough_line_peaks
from skimage.filters import sobel

import statsmodels.api as sm
lowess = sm.nonparametric.lowess

from .. phantoms import TO4, PIQTMTF, PIQTSNR, find_phantom
from .. dcmio import (
    pix_spacing_yx,  approx_phase_orientation, phase_enc_dirn,
    approx_slice_orientation, seq_name, series_number
)
from .. tools import (
    peakdet, add_phase_encode_mark, image_from_dicom,
    rectangular_roi, rectangular_roi_coords
)


def _x_limits(roi):
    """
    Indices with which to trim a bars roi in x.

    Trim such that it just includes the ends of the bars and no more.
    That way we'll get the maximum contrast when we project it along y.
    """
    proj_x = np.mean(roi, axis=0)
    proj_x = np.max(proj_x) - proj_x
    w = np.hanning(4)
    proj_x = np.convolve(w/np.sum(w), proj_x, mode='valid')
    proj_x = proj_x - np.percentile(proj_x, 25)
    inds = np.where(proj_x > 0)[0]
    firstx, lastx = inds[0], inds[-1]
    return firstx, lastx


def _y_limits(roi):
    """
    Indices with which to trim a bars roi in y.

    Trim such that it just includes the ends of the bars and no more.
    That way we'll get the maximum contrast when we project it along x.
    """
    proj_y = np.mean(roi, axis=1)
    proj_y = np.max(proj_y) - proj_y
    w = np.hanning(4)
    proj_y = np.convolve(w/np.sum(w), proj_y, mode='valid')
    proj_y = proj_y - np.percentile(proj_y, 25)
    inds = np.where(proj_y > 0)[0]
    firsty, lasty = inds[0], inds[-1]
    return firsty, lasty


def _opt_angle(roi, axis=None):
    """
    Angle in degrees by which to rotate the bars roi.

    The angle that optimizes the 'contrast'.
    """

    if axis is None:
        # Assume bars are aligned along longer axis os roi
        axis = 0 if roi.shape[0] >= roi.shape[1] else 1

    # Accept vertical or horizontal bars in phantom description
    if axis == 0:
        firsty, lasty = _y_limits(roi)
        zoomed = ndizoom(roi[firsty:lasty, :], zoom=4)
    else:
        firstx, lastx = _x_limits(roi)
        zoomed = ndizoom(roi[:, firstx:lastx], zoom=4)

    angles = np.linspace(-3, 3, 81)
    modulation = []
    for i, angle in enumerate(angles):
        rotated = ndirotate(zoomed, angle, mode='wrap', order=3)
        profile = np.mean(rotated, axis=axis)
        profile -= np.mean(profile)
        modulation.append(np.sum(profile ** 2))

    maxima, _ = peakdet(modulation, delta=0.1*np.max(modulation))
    peakindices = maxima[:, 0].astype(int)
    index = sorted(peakindices, key=lambda i: modulation[i])[-1]
    return angles[index]


def _bar_profile(roi, angle=0, zoom=1, axis=None):
    """
    Extract a profile from a bars roi.

    Rotates first by the given angle in degrees.
    This is a normalised projection onto the x (or y) axis - a 1d numpy array.
    """
    # Accept vertical or horizontal bars in phantom description
    if axis is None:
        # Assume bars are aligned along longer axis os roi
        axis = 0 if roi.shape[0] >= roi.shape[1] else 1

    if axis == 0:
        # bars vertical, clip in y
        firsty, lasty = _y_limits(roi)
        # interpolate up
        zoomed = ndizoom(roi[firsty:lasty], zoom=zoom)
        # rotate
        rotated = ndirotate(zoomed, angle, mode='wrap', order=3)
        # project onto x axis
        profile = np.mean(rotated, axis=0)
    else:
        # bars horizontal, clip in x
        firstx, lastx = _x_limits(roi)
        # interpolate up
        zoomed = ndizoom(roi[:, firstx:lastx], zoom=zoom)
        # rotate
        rotated = ndirotate(zoomed, angle, mode='wrap', order=3)
        # project onto y axis
        profile = np.mean(rotated, axis=1)

    # normalise to 'background'
    profile /= np.mean((profile[:2] + profile[-2:]) / 2)
    return profile


def _correl_peak(profile, d_mm, bar_width_mm):
    """Peak of cross correlation function with the assumed form of the bars."""
    nbars = 4
    bar_width_pixels = max(1, int(round(bar_width_mm / d_mm)))
    template = (
        nbars * ([-1] * bar_width_pixels + [1] * bar_width_pixels) +
        [-1] * bar_width_pixels
    )
    correl = correlate(template, profile)
    return np.max(correl) / len(template)


def to4_bars_report(dobj, flipped_ud=False, flipped_rl=False, phantom=TO4, frame=None):
    """
    Resolution Report showing the modulation pattern for each of the line pattern ROI.

    Parameters
    ----------
    dobj: dicom object
        image of TO4 phantom
    flipped_ud: bool, optional
        image requires top bottom reflection
    flipped_rl: bool, optional
        image requires left right reflecton
    phantom: dict, optional
        description of phantom
    frame: int
        index in multiframe

    Returns
    -------
    pandas Dataframe

    """
    image = image_from_dicom(dobj, frame)
    pix_dims = np.asarray(pix_spacing_yx(dobj))
    if flipped_ud:
        image = np.flipud(image)
    if flipped_rl:
        image = np.fliplr(image)

    rects = phantom['Features']['Bars']
    spacings = phantom['FeatureSizes']['Bars']

    # find_phantom returns pixel coordinates in natural order (x, y)
    expected_radius = phantom['Diameter'] / 2 / pix_dims[0]
    centre_x, centre_y, _ = find_phantom(image, expected_radius)
    centre = centre_x, centre_y

    zoom = 4

    assert len(spacings) == len(rects)

    rois = [
        rectangular_roi(image, pix_dims=pix_dims, rect=rect, centre=centre)
        for rect in rects
    ]
    angles = [_opt_angle(roi) for roi in rois]
    angle = np.mean(angles[1:-1])

    ncols = 3
    nrows = int(np.ceil(len(rois)/float(ncols)))
    posn_mins = []
    posn_maxs = []
    fig, axs = plt.subplots(
        nrows=nrows, ncols=ncols, figsize=(5*ncols, 4*nrows)
    )
    for i, roi in enumerate(rois):
        profile = 1 - _bar_profile(roi, angle=angle, zoom=zoom)
        posns = (np.arange(len(profile)) - len(profile)/2) * pix_dims[1] / zoom
        correl = _correl_peak(profile, pix_dims[1]/zoom, spacings[i])
        # norm_abs_integral = np.sum(np.abs(profile-0.5)) / npixels[i]
        ax = axs.flat[i]
        ax.plot(posns, profile)
        ax.grid(True)

        ax.text(0.70, 0.70, 'Correl. = %0.3f' % correl, transform=ax.transAxes)
        ax.set_title('Bars: %0.2f mm' % spacings[i])

        # nb doesn't seem much good - we want *contrast* not average ....
        # ax.text(0.8, 0.8, 'Modl = %0.2f' % norm_abs_integral, transform=ax.transAxes)
        # ax.set_title('TO4 Bars: %0.2f mm' % spacings[i])
        posn_mins.append(np.min(posns))
        posn_maxs.append(np.max(posns))

    posn_globmin = np.min(posn_mins)
    posn_globmax = np.max(posn_maxs)

    for ax in axs.flat[:len(rois)]:
        ax.set_xlim(posn_globmin, posn_globmax)

    ax_im = axs.flat[len(rois)]
    ax_im.imshow(image, cmap='bone')

    for rect in rects:
        x, y, dx, dy = rectangular_roi_coords(pix_dims, rect, centre)
        # TODO: cycle colours
        ax_im.add_artist(
            plt.Rectangle([x, y], dx, dy, color='red', alpha=0.25)
        )

    for ax in axs.flat[len(rois):]:
        ax.axis('off')

    fig.suptitle(
        "%s %s (Phase %s) Pixel Size = %0.2fx%0.2f mm" % (
            approx_slice_orientation(dobj),
            seq_name(dobj),
            approx_phase_orientation(dobj),
            pix_spacing_yx(dobj)[1],
            pix_spacing_yx(dobj)[0],
            ),
        fontsize=18
    )

    return pd.DataFrame()


def mtf_block_edges(roi):
    """
    Get the strongest four lines in ROI corresponding to the four edges of the mtf block.

    Parameters
    ----------
    roi: ndarray (2d)
        image containing mtf block

    Returns
    -------

    tuple (ndarray (1d, ndarray (1d))
        angles and distances
    """
    def centre_angle(roi, theta, dist):
        """Angle around image centre to sort edges by."""
        theta = np.pi/2 - theta
        if dist > np.hypot(*np.array(roi.shape) / 2):
            theta += np.pi
        return np.mod(theta, 2*np.pi)

    mask = roi > roi.mean()
    mask = binary_dilation(mask, disk(3)) & ~binary_erosion(mask, disk(3))
    edges = mask & canny(roi/roi.mean(), sigma=3) & mask

    # Hough Line Tranform
    tested_angles = np.r_[
        np.linspace(-np.pi / 8, np.pi / 8, 60),
        np.linspace(3*np.pi / 8, 5*np.pi / 8, 60)

    ]
    h, theta, d = hough_line(edges, theta=tested_angles)

    # Pick 4 best lines (reduced threshold slightly from default of 0.5)
    peaks = hough_line_peaks(h, theta, d, threshold=0.4*h.max(), num_peaks=4)
    angles, dists = peaks[1][:4], peaks[2][:4]

    # Sort around centre of block
    angles, dists = zip(*sorted(
        zip(angles, dists),
        key=lambda pair: centre_angle(roi, pair[0], pair[1])
    ))
    return angles, dists


def intersection(line1, line2):
    """
    Intersection of two lines in Hesse normal form.

    See https://stackoverflow.com/a/383527/5087436
    For mtf block edges.

    Parameters
    ----------
    line1: pair of float
        first line expressed as angle and distance
    line2: pair of float
        second line expressed as angle and distance

    Returns
    -------
    tuple of float
        coordinates of intersection (x, y)

    """
    theta1, rho1 = line1
    theta2, rho2 = line2
    A = np.array([
        [np.cos(theta1), np.sin(theta1)],
        [np.cos(theta2), np.sin(theta2)]
    ])
    b = [rho1, rho2]

    x0, y0 = np.linalg.solve(A, b)
    return x0, y0


def mtf_block_subrois(roi, angles, dists):
    """
    ROIs for the four edges of the mtf block.

    The ROIs are reoriented so as to all have the edge in the same position
    and returned in a dictionary.

    The standard orintation is that of the top edge in the PIQT phantom.

    Parameters
    ----------
    roi: ndarray (2d)
        image containing mtf block
    angles: ndarray (1d)
       angles of mtf block edges
    dists: ndarray (1d)
       distances of mtf block edges

    Returns
    -------
    dict
        sub regions

    """

    def extract_bbox(line1, line2, line3):
        """
        Bounding box defined by intersections of lines.

        [(x1, y1), (x2, y2)]
        """
        p1 = np.array(intersection(line1, line2))
        p2 = np.array(intersection(line1, line3))
        ps = np.array([p1, p2])
        return np.array([
            np.min(ps, axis=0),
            np.max(ps, axis=0)
        ])

    ny, nx = roi.shape

    # NB hough angle defined such that 0 is vertical 90 is horizontal
    horiz_angles, horiz_dists = zip(*[
        (angle, dist) for angle, dist in zip(angles, dists) if abs(np.degrees(angle)) > 45
    ])
    vert_angles, vert_dists = zip(*[
        (angle, dist) for angle, dist in zip(angles, dists) if abs(np.degrees(angle)) <= 45
    ])

    subrois = {}
    # 'horizontal' edges
    for horiz_angle, horiz_dist in zip(horiz_angles, horiz_dists):
        line1 = horiz_angle, horiz_dist
        line2 = vert_angles[0], vert_dists[0]
        line3 = vert_angles[1], vert_dists[1]

        bbox = extract_bbox(line1, line2, line3)

        line_segment_length = np.hypot(*(bbox[1] - bbox[0]))
        width, height = abs(bbox[1][0] - bbox[0][0]), abs(bbox[1][1] - bbox[0][1])
        bbox[0] -= (-width/10, height/2)
        bbox[1] += (-width/10, height/2)

        bbox = np.round(bbox).astype(int)
        bbox = np.clip(bbox, 0, None)
        bbox[1][0] = np.clip(bbox[1][0], None, nx-1)
        bbox[1][1] = np.clip(bbox[1][1], None, ny-1)

        (x1, y1), (x2, y2) = bbox
        subroi = roi[y1:y2, x1:x2]

        # adjust so as in 'standard' orientation and save under a label
        profile = subroi.sum(axis=1)
        twists = 0 if profile[-1] > profile[0] else 2
        label = 'Upper' if y1 < ny/2 else 'Lower'
        subrois[label] = np.rot90(subroi, twists)

    # 'vertical' edges
    for vert_angle, vert_dist in zip(vert_angles, vert_dists):
        line1 = vert_angle, vert_dist
        line2 = horiz_angles[0], horiz_dists[0]
        line3 = horiz_angles[1], horiz_dists[1]

        bbox = extract_bbox(line1, line2, line3)
        # FIXME: shouldn't we set line_segment_length again?

        # shrink along edge and grow perpendicular
        dx, dy = abs(bbox[1][0] - bbox[0][0]), abs(bbox[1][1] - bbox[0][1])
        bbox[0] -= (dx/2, -dy/15)
        bbox[1] += (dx/2, -dy/15)

        bbox = np.round(bbox).astype(int)
        bbox = np.clip(bbox, 0, None)
        bbox[1][0] = np.clip(bbox[1][0], None, nx-1)
        bbox[1][1] = np.clip(bbox[1][1], None, ny-1)

        (x1, y1), (x2, y2) = bbox
        subroi = roi[y1:y2, x1:x2]

        # adjust so as in 'standard' orientation and save under a label
        profile = subroi.sum(axis=0)
        twists = 3 if profile[-1] > profile[0] else 1
        label = 'Left' if x1 < nx/2 else 'Right'
        subrois[label] = np.rot90(subroi, twists)

    return dict(sorted(
        subrois.items(),
        key=lambda x: ['Upper', 'Lower', 'Left', 'Right'].index(x[0])
    ))


def initial_edge_fit(roi, method=sobel):
    """
    Initial fit to mtf block edge in image using edge detection.

    Parameters
    ----------
    roi: ndarray (2d)
        image containing a single mtf block edge
    method: callable, optional
        edge detection function to use

    Returns
    -------
    tuple of float
        slope and intercept of detected line
    """
    edges = method(roi)
    points = []
    for i, col in enumerate(edges.T):
        x, y = i, np.argmax(col)
        points.append((x, y))
    X, Y = np.asarray(points).T
    X, Y = X[1:-1], Y[1:-1]
    slope, intercept = np.polyfit(X, Y, deg=1)
    return slope, intercept


def si(x):
    """
    Sine-integral function for edge
    NB conventions: sici(x)[0] is the integral (0, x) of the *unnormalised* sinc function sin(x) / x 
    whereas np.sinc is the *normalised* sinc function defined as sin(pi x) / pi x (from 0, x)
    This means it would correspond to first zero crossing at pi rather than at one.
    We can scale it to match the sinc definition and shift it up so the integral goes from -inf to x
    """
    return 0.5 + sici(np.pi * x)[0] / np.pi


def phi(x):
    """
    Error function for edge
    The integral (-inf, x) of a unit width Gaussian is phi(x) = 0.5 * (1 + erf(x/sqrt(2)))
    """
    return 0.5 * (1 + erf(x / np.sqrt(2)))


def roi_edge_model_erf(XY, i0, i1, a, b, c, d, e, f, sigma, intercept, slope):
    """
    Function to model edge in the mtf block using an error function.

    A linear fit to the edge position and an error fn blurring of the edge.
    A quadratic bias field for the image intensities is also allowed.

    Parameters
    ----------
    XY:
        x and y coordinates of positions in the roi
    i0, i1: float, float
        backgound and foreground intensity
    a, b, c, d, e, f:
        quadratic gain field
    sigma:
        width of error function at edge
    intercept: float
        intercept of line passing through edge
    slope: float
        slope of line passing through edge

    Returns
    -------
    ndarray (1d) of float
        flattened predicted image
    """
    x, y = XY
    # Quadratic model of bias field
    gain = a + b*x + c*y + d * x**2 + e * y**2 + f * x*y
    # Linear model of edge position
    loc = intercept + x * slope
    # Error function model of edge transition
    result = gain * (i0 + (i1 - i0) * phi((y - loc) / sigma))
    # curve_fit() needs the modelled image flattened to 1D
    return result.ravel()


def roi_edge_model_magsi(XY, i0, i1, a, b, c, d, e, f, sigma, intercept, slope):
    """
    Function to model edge in the mtf block using magnitude of sine integral.

    A linear fit to the edge position with rectified sine integral blurring.
    A quadratic bias field for the image intensities is also allowed.

    Parameters
    ----------
    XY:
        x and y coordinates of positions in the roi
    i0, i1: float, float
        backgound and foreground intensity
    a, b, c, d, e, f:
        quadratic gain field
    sigma:
        width of error function at edge
    intercept: float
        intercept of line passing through edge
    slope: float
        slope of line passing through edge

    Returns
    -------
    ndarray (1d) of float
        flattened predicted image
    """
    x, y = XY
    # Quadratic model of bias field
    gain = a + b*x + c*y + d * x**2 + e * y**2 + f * x*y
    # Linear model of edge position
    loc = intercept + x * slope
    # Rectified sine integral function model of edge transition
    result = abs(gain * (i0 + (i1 - i0) * si((y - loc) / sigma)))
    # curve_fit() needs the modelled image flattened to 1D
    return result.ravel()


def fit_edge_model(roi, model):
    """
    Non-linear least squares fit of model to an mtf block edge in an image.

    Gives an estimate of the edge position and inclination as well as a bias
    field correction to apply to the images in further analysis,

    Parameters
    ----------
    roi: ndarray (2d)
        image with single mtf block edge
    model: function
        model to fit

    Returns
    -------
    tuple (float, float, ndarray)
        slope and intercept of edge and bias field image

    """
    # Coordinates
    X, Y = np.meshgrid(np.arange(roi.shape[1]), np.arange(roi.shape[0]))

    # Starting Point:
    # - top-left and bottom-right for background and foreground respectively
    # - uniform gain
    # - edge thickness of one pixelne pixel
    # - edge position and slope from edge detection in image
    i0_0 = roi[:10, :10].mean()
    i1_0 = roi[-10:, -10:].mean()
    a_0 = 1.0
    b_0 = c_0 = d_0 = e_0 = f_0 = 0.0
    sigma_0 = 1.0
    slope_0, intercept_0 = initial_edge_fit(roi)

    p0 = [i0_0, i1_0, a_0, b_0, c_0, d_0, e_0, f_0, sigma_0, intercept_0, slope_0]

    # Data to fit
    popt, pcov = curve_fit(model, xdata=(X, Y), ydata=roi.flatten(), p0=p0)
    i0, i1, a, b, c, d, e, f, sigma, intercept, slope = popt

    gain_field = a + b*X + c*Y + d * X**2 + e * Y**2 + f * X*Y
    return slope, intercept, gain_field


def edge_profile_from_roi(roi, pix_dims, model=roi_edge_model_magsi):
    """
    Return irregularly sampled edge response from image consisting of a horizontal ROI around the edge.

    Assumes the edge also appears approximately horizontal in the image,
    rising left to right and bright at the bottom.

    Parameters
    ----------
    roi: ndarray (2d)
        image array of single edge
    pix_dims: tuple of floats
        pixel dimensions (dy, dx)
    model: callable, optional
        modelling function
        (default is rectified si fn along edge with bias field correction)

    Returns
    -------
    tuple (ndarray, ndarray)
        x-positions and signal values
    """

    def _increasing(y):
        return sum(y[:len(y)]) > sum(y[len(y):])

    # Edge should be horizontal in ROI, rising left to right and bright at the bottom
    assert roi.shape[1] > roi.shape[0]
    assert _increasing(roi.mean(axis=1))
    assert _increasing(roi.mean(axis=0))

    # Only square pixels for now
    dy, dx = pix_dims
    assert np.isclose(dx, dy)

    X, Y = np.meshgrid(np.arange(roi.shape[1]), np.arange(roi.shape[0]))
    nrows, ncols = roi.shape
    slope, intercept, gain_field = fit_edge_model(roi.astype(float), model)

    # Normalise and flatten
    pixvals = (roi / gain_field).ravel()

    # Doesn't seem to matter which way across the edge - cross it vertically.
    y_shifts_at_x = np.arange(ncols) * slope + intercept
    Y_shifted = (Y - y_shifts_at_x[X]).ravel()
    sort_order_col = np.argsort(Y_shifted)
    proj_factor_col = np.abs(np.cos(np.arctan(slope)))
    effective_pixel_size_col = dy * proj_factor_col
    locns_mm, vals_at_locns = Y_shifted[sort_order_col] * effective_pixel_size_col, pixvals[sort_order_col]

    # Normalise to unit range; assume curve is rising from minumum at start
    npoints = len(vals_at_locns)
    lower = vals_at_locns[:npoints//4].mean()
    upper = vals_at_locns[3*npoints//4:].mean()
    return locns_mm, (vals_at_locns - lower) / (upper - lower)


def esf_model(x_mm, sigma, width, centre, scale):
    """
    Model fitting function for edge function (sine integral with gaussian smoothing)
    x_mm: ndarry of float
        positions in mm
    sigma: float
        width of gaussian in mm
    width: float
        width of sinc/sine-intergal in mm
    centre: float
        position of centre of edge in mm
    scale: float
        scaling factor from normalised edge

    Returns
    -------
    ndarray of float: model with given parameters evaluated at x_mm positions

    """
    n = len(x_mm)
    if n < 10:
        warn(f'Bad data length x_mm: {n}')

    if not np.all(np.isfinite(x_mm)):
        warn(f'Bad data range x_mm: ...')

    x_grid = np.linspace(x_mm.min()-abs(centre)-0.1, x_mm.max()+abs(centre)+0.1, n)
    dx = x_grid[1] - x_grid[0]
    assert dx > 0

    s = np.sinc(x_grid / width)
    assert np.all(np.isfinite(s))
    assert s.sum() > 1e-5

    if sigma > 0.5 * dx:
        g = np.exp(-x_grid**2 / (2*sigma**2))
        assert np.all(np.isfinite(g))
        if g.sum() > 1e-6:
            g /= g.sum()
        else:
            if (g>0).sum() > 1:
                warn(f'g has {(g>0).sum()} non-zeros when replacing by delta; sigma={sigma}')
            g = np.zeros_like(g)
            g[np.searchsorted(x_grid, 0)] = 1

        assert g.sum() > 1e-5
        c = np.convolve(g, s, mode='same')
        assert np.all(np.isfinite(c))
        assert c.sum() > 1e-5

        c /= (c.sum() * dx)
        assert np.all(np.isfinite(c))
    else:
        c = s / (s.sum() * dx)

    e = cumulative_trapezoid(c, dx=dx, initial=0)
    assert np.all(np.isfinite(e))

    ei = interp1d(x_grid + centre, e)
    if not np.all(np.isfinite(ei(x_mm))):
        warn(f'Bad model params: sigma: {sigma}, width: {width}, centre: {centre}, scale: {scale}')
    return ei(x_mm) * scale


def esf_model_abs(x_mm, sigma, width, centre, scale):
    """
    Model fitting function for edge function (abs of sine integral with gaussian smoothing)
    x_mm: ndarry of float
        positions in mm
    sigma: float
        width of gaussian in mm
    width: float
        width of sinc/sine-intergal in mm
    centre: float
        position of centre of edge in mm
    scale: float
        scaling factor from normalised edge

    Returns
    -------
    ndarray of float: model with given parameters evaluated at x_mm positions
    """
    return abs(
        esf_model(x_mm, sigma, width, centre, scale)
    )


def fit_esf_model(x_mm, y, pix_sz_mm, model=esf_model_abs):
    """
    Fit a model edge to an empiral edge spread function for edge function
    x_mm: ndarry of float
        positions in mm
    y: ndarray of float
        empirical edge function
    pix_sz_mm: float
        expected pixel size im mm
    model: callable
        fitting function to use (default is sine-integral with minor gaussian smoothing and rectification)

    Returns
    -------
    tuple of fit parameters (sigma, width, centre, scale)
    """

    # Box constraints and starting point
    # Looks like it's very sensitive to the starting point for sinc width
    # TODO (RHD) replace these magic number with something more principled
    #       (mm)    sigma            width           centre  scale
    lower_bounds = (0.001*pix_sz_mm, 0.25*pix_sz_mm, -1,     0.9)
    start_points = (0.05*pix_sz_mm,  pix_sz_mm,       0,     1.0)
    upper_bounds = (0.2*pix_sz_mm,   4*pix_sz_mm,     1,     1.1)
    popt, _ = curve_fit(
        model,
        x_mm, y,
        p0=start_points,
        bounds=(lower_bounds, upper_bounds),
        method='dogbox',
        loss='soft_l1'
    )
    return popt


def fitted_esf(x_mm, y, pix_sz_mm, model=esf_model_abs):
    """
    Fit to empirical edge function using esf model

    x_mm: ndarry of float
        positions in mm
    y: ndarray of float
        empirical edge function
    pix_sz_mm: float
        expected pixel size im mm
    model: callable
        esf function to fit

    Returns
    -------
    ndarray of float: fit evaluated at the given x positions (mm)

    """
    sigma_opt, width_opt, centre_opt, scale_opt = fit_esf_model(x_mm, y, pix_sz_mm, model=model)
    return esf_model(x_mm, sigma_opt, width_opt, centre_opt, scale_opt)


def fitted_esf_abs(x_mm, y, pix_sz_mm, model=esf_model_abs):
    """
    Fit to empirical edge function using esf model (rectified version)

    x_mm: ndarry of float
        positions in mm
    y: ndarray of float
        empirical edge function
    pix_sz_mm: float
        expected pixel size im mm
    model: callable
        esf function to fit

    Returns
    -------
    ndarray of float: fit evaluated at the given x positions (mm)

    """
    return abs(fitted_esf(x_mm, y, pix_sz_mm, model=model))


def lowess_regrid(x_mm, esf, edge_margin_mm):
    """
    Regrid edge spread function after smoothing with loess.

    Parameters
    ----------
    x_mm: ndarray (1d)
        x axis for esf in mm
    esf: ndarray (1d)
        esf defined at x locations
    edge_margin_mm: float
        region around edge to consider for esf (mm)

    Returns
    -------
    smoothed line response function: ndarray (1d)

    """
    # Trim down
    window = (-edge_margin_mm < x_mm) & (x_mm < edge_margin_mm)
    esf = esf[window]
    x_mm = x_mm[window]

    x = x_mm
    y = esf - esf.mean()

    # Lowess fit on irregular (but monotonic) grid
    assert list(x) == sorted(x)
    w = lowess(y, x, frac=0.05, return_sorted=False)

    # Interpolate onto a regular grid
    fn = interp1d(x, w, kind='cubic')
    x_grid = np.linspace(x.min(), x.max(), 512)
    w_grid = fn(x_grid)
    return x_grid, w_grid + esf.mean()


def lsf_from_esf(x_mm, esf):
    """
    Derive line response by differentiating edge response and applying window.

    Parameters
    ----------
    x_mm: ndarray (1d)
        x axis for esf and lsf in mm
    esf: ndarray (1d)
        edge response defined at x locations

    Returns
    -------
    ndarray (1d) of float
        line response function

    """
    grid_spacing = x_mm[1] - x_mm[0]
    lsf = np.gradient(esf, grid_spacing)
    return lsf * hamming(len(lsf))


def mtf_from_lsf(x_mm, lsf):
    """
    Derive modulation transfer function by Fourier transforming edge response.

    MTF is normalised to unity at zero frequency.

    Parameters
    ----------
    x_mm: ndarray (1d)
        x axis for lsf in mm
    lsf: ndarray (1d)
        lsf defined at x locations

    Returns
    -------
    tuple of ndarray (1d) of float
        modulation transfer function

    """
    npoints = len(lsf)

    mtf = np.abs(rfft(np.pad(lsf, npoints//2, mode='constant')))

    # Normalize to expected maximum at DC
    if mtf.argmax() != 0:
        warn("MTF maximum is not at zero")
    mtf /= mtf[0]

    # x axis for the mtf - cycles per mm
    effective_pixel_size = x_mm[1] - x_mm[0]
    k_mtf = np.arange(2*len(mtf)) / npoints / effective_pixel_size / 2

    return k_mtf, mtf


def mtf_edge_analysis(roi, pix_dims, edge_margin, use_esf_model=False, correct_sign=False):
    """
    Analysis of single edge of mtf block.
    Assumes edge is positive going top to bottom and is at a shallow positive angle.

    Parameters
    ----------
    roi: ndarray (2d)
        image array containing single edge of mtf block
    pix_dims: tuple of floats
        pixels sizes (y, x)
    edge_margin: float
        number of pixels to include either side of edge
    use_esf_model: bool
        use theoretical edge model for interpolation
    correct_sign: bool
        patch up rectification of left hand side of esf

    Returns
    -------
    tuple
        results from edge analysis
    """

    x_mm, esf = edge_profile_from_roi(roi, pix_dims)

    if use_esf_model:
        if correct_sign:
            esf_fitted = fitted_esf(x_mm, esf, pix_dims[0])
            esf *= np.sign(esf_fitted)
            x_mm_grid, esf_grid = lowess_regrid(x_mm, esf, edge_margin * pix_dims[0])
            esf_grid = interp1d(x_mm, esf_fitted)(x_mm_grid)
        else:
            esf_fitted = fitted_esf_abs(x_mm, esf, pix_dims[0])
            x_mm_grid, esf_grid = lowess_regrid(x_mm, esf, edge_margin * pix_dims[0])
            esf_grid = interp1d(x_mm, esf_fitted)(x_mm_grid)
    else:
        x_mm_grid, esf_grid = lowess_regrid(x_mm, esf, edge_margin * pix_dims[0])

    lsf = lsf_from_esf(x_mm_grid, esf_grid)
    x_mtf, mtf = mtf_from_lsf(x_mm_grid, lsf)

    return x_mm, esf, x_mm_grid, esf_grid, lsf, x_mtf, mtf


def mtf_report(
        mtf_dobj, centring_dobj=None,
        mtf_frame=None, centring_frame=None,
        mtf_phantom=PIQTMTF, centring_phantom=PIQTSNR,
        cutoff_freq=3.0, edge_margin=3.5, fliplr=False, flipud=False, block_index=0,
        edges=None, use_esf_model=False, correct_sign=False):
    """
    Resolution Report based on MTF block in PIQT phantom.

    Parameters
    ----------
    mtf_dobj: dicom object
        slice or multiframe with mtf block
    centring_dobj: dicom object, optional
        slice or multiframe with SNR region for phantom centring
    mtf_frame: int, optional
        frame number of mtf image if multiframe
    centring_frame: int, optional
        frame number of centring image if multiframe
    mtf_phantom: dict, optional
        phantom description of mtf image
    centring_phantom: dict, optional
        phantom description of centring image
    cutoff_freq: float, optional
        maximum spatial frequency to consider in mtf in cycles/mm
    edge_margin: float, optional
        number of pixels to include either side of the edge
    fliplr: bool, optional
        image requires left right reflecton
    flipud: bool, optional
        image requires top bottom reflection
    block_index: int, optional
        block number in phantoms with multiple mtf blocks
    edges: list, optional
        restrict analysis to specified edges
    use_esf_model: bool
        use theoretical edge model for interpolation
    correct_sign: bool
        patch up rectification of left hand side of esf

    Returns
    -------
    pandas Dataframe
        50% maximum frequency of mtf for each edge in MTF block

    """
    def find_index(x, value):
        return np.diff(np.sign(x - value)).nonzero()[0][0]

    def half_max(x, y):
        x_interp = np.linspace(x[0], x[-1], 50)
        y_interp = interp1d(x, y)(x_interp)
        return x_interp[(abs(y_interp - 0.5)).argmin()]

    mtf_image = image_from_dicom(mtf_dobj, mtf_frame)
    centring_image = image_from_dicom(
        centring_dobj if centring_dobj is not None else mtf_dobj,
        centring_frame
    )

    if fliplr:
        mtf_image = np.fliplr(mtf_image)
        centring_image = np.fliplr(centring_image)

    if flipud:
        mtf_image = np.flipud(mtf_image)
        centring_image = np.flipud(centring_image)

    # Voxel geometry - require square pixels for now
    dy, dx = pix_spacing_yx(mtf_dobj)
    assert np.isclose(dx, dy)

    # NB find_phantom returns pixel coordinates in "natural" order (x, y)
    expected_radius = centring_phantom['Diameter'] / 2 / dx
    centre_x, centre_y, radius = find_phantom(centring_image, expected_radius)
    centre = centre_x, centre_y

    # A ROI covering all of the mtf block
    block = mtf_phantom['Features']['Blocks'][block_index]
    roi = rectangular_roi(mtf_image, pix_dims=(dy, dx), rect=block, centre=centre)

    # Extract subroi for each edge
    angles, dists = mtf_block_edges(roi)
    subrois = mtf_block_subrois(roi, angles, dists)

    if edges is not None:
        subrois = {name: roi for name, roi in subrois.items() if name in edges}

    # Perform the edge analyses
    analyses = {
        name: mtf_edge_analysis(
            subroi, pix_dims=(dy, dx), edge_margin=edge_margin,
            use_esf_model=use_esf_model, correct_sign=correct_sign
        )
        for (name, subroi) in subrois.items()
    }

    # These are actually the point where the mtf falls to 0.5 the value at DC
    halfmaxima = {}
    for name in analyses:
        x_mm, esf, x_mm_grid, esf_grid, lsf, x_mtf, mtf = analyses[name]
        cutoff_index = find_index(x_mtf, cutoff_freq)
        halfmaxima[name] = half_max(x_mtf[:cutoff_index+1], mtf[:cutoff_index+1])

    # Plot results
    fig, axs = plt.subplots(2, 2, figsize=(12, 9))
    axs = axs.ravel()

    # Image
    ax = axs[0]
    ax.imshow(mtf_image, cmap='bone')
    ax.axis('off')
    ax.grid(False)

    # Show phase encoding direction
    add_phase_encode_mark(axs[0], phase_enc_dirn(mtf_dobj))

    nrows, ncols = mtf_image.shape

    # Graphics of ROI to draw on image
    (x, y), (width, height) = np.array(block) / (dy, dx)
    # TODO: are we missing an off-by-one adjustment here?
    x = int(round(x + centre_x))
    y = int(round(y + centre_y))
    ax.axvline(centre_x, linewidth=0.5, color='C1')
    ax.axhline(centre_y, linewidth=0.5, color='C1')
    ax.add_artist(
        plt.Circle((centre_x, centre_y), radius, color='C1', fill=False)
    )
    ax.text(x, y, '({}, {})'.format(x, y), color='C2')
    ax.add_artist(
        plt.Rectangle((x, y), width, height, color='C2', fill=False, linewidth=0.5)
    )
    ax.vlines([x+dx/2], y, y+height, color='C2', linewidth=0.5)
    ax.hlines([y+dy/2], x, x+width, color='C2', linewidth=0.5)

    ax.set_title(
        r'Series %d, Image %d, %0.1fx%0.1fmm (%s)' %
        (series_number(mtf_dobj), mtf_dobj.InstanceNumber, dy, dx, approx_phase_orientation(mtf_dobj))
    )

    # MTF Analysis
    for name in analyses:
        x_mm, esf, x_mm_grid, esf_grid, lsf, x_mtf, mtf = analyses[name]
        ax = axs[1]
        p = ax.plot(x_mm, esf, '.', markersize=2, alpha=0.5)
        ax.plot(x_mm_grid, esf_grid, label=name, color=p[0].get_color())
        ax.set_xlim(x_mm_grid[0], x_mm_grid[-1])

        ax = axs[2]
        ax.plot(x_mm_grid, lsf, label=name)
        ax.set_xlim(x_mm_grid[0], x_mm_grid[-1])

        ax = axs[3]
        cutoff_index = find_index(x_mtf, cutoff_freq)
        x_mtf, mtf = x_mtf[:cutoff_index+1], mtf[:cutoff_index+1]
        halfmax = halfmaxima[name]
        p = ax.plot(x_mtf, mtf, label='%s: %0.2f' % (name, halfmax))
        ax.vlines(halfmax, 0, 0.5, color=p[0].get_color(), linewidth=1, linestyle='dotted')

    ax = axs[1]
    ax.grid(True)
    ax.set_xlabel('Distance from Edge (mm)')
    ax.set_ylabel('Normalised Brightness')
    ax.set_title('Fitted Edge Spread Function')
    ax.legend()

    ax = axs[2]
    ax.grid(True)
    ax.set_xlabel('Distance from Edge (mm)')
    ax.set_title('Line Spread Function (Windowed)')
    ax.legend()

    ax = axs[3]
    ax.set_xlim(0, cutoff_freq)
    ax.grid(True)
    ax.set_xlabel('Spatial Frequency (cycles per mm)')
    ax.set_ylabel('Modulation Depth')
    ax.set_title('Modulation Transfer Function')
    ax.axhline(0.5, linewidth=1, color='black', linestyle='dotted')
    ax.legend()

    fig.suptitle('Resolution [%s]' % seq_name(mtf_dobj), fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    return pd.DataFrame({'MTF_50': halfmaxima}, index=subrois.keys())
