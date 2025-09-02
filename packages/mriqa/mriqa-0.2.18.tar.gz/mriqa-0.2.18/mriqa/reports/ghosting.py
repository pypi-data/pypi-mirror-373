#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ghosting.py: graphical reports of QA ghosting parameters."""

import numpy as np
import pandas as pd

from scipy.ndimage import zoom as ndizoom

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from mriqa.phantoms import GE10CMSPHERE, find_phantom, circular_mask, rectangular_mask

from mriqa.dcmio import (
    number_of_frames, pix_spacing_yx, approx_phase_orientation,
    approx_slice_orientation, seq_name, protocol_name, matrix_yx,
    series_number, t_r, t_e, readout_bandwidth, phase_enc_dirn
)

from mriqa.tools import add_phase_encode_mark, image_from_dicom


def _interpolate_to_min_resolution(image, min_matrix):
    """
    Interpolate to minum matrix size.
    Returns (possibly) interpolated image and pixel size scale factors
    """
    # Interpolate up to min_matrix * min_matrix if less
    old_ny, old_nx = image.shape
    assert old_nx == old_ny
    if old_ny < min_matrix:
        image = ndizoom(image, zoom=min_matrix/old_ny)
        new_ny, new_nx = image.shape
        return image, old_ny / new_ny, old_nx / new_nx
    return image, 1.0, 1.0


def ghosting_report(dobjs, phantom=GE10CMSPHERE, frame=None, axes=None):
    """
    Report on ghosting from a spherical phantom (or cylindrical for single axis)

    Based on images acquired of a small phantom.
    Produces image plots and returns a dataframe of results.

    """
    assert 1 <= len(dobjs) <= 6, 'Require 1-6 images (%d)' % len(dobjs)
    assert all(
        seq_name(d) == seq_name(dobjs[0]) for d in dobjs
    ), 'Sequences must be consistent (%s)' % [seq_name(d) for d in dobjs]
    assert all(
        pix_spacing_yx(d) == pix_spacing_yx(dobjs[0]) for d in dobjs
    ), 'Pixel spacings must be consistent %s' % [pix_spacing_yx(d) for d in dobjs]
    assert all(
        (d.Rows, d.Columns) == (dobjs[0].Rows, dobjs[0].Columns) for d in dobjs
    ), 'Matrix sizes must be consistent'
    # Square pixels only
    assert np.isclose(*pix_spacing_yx(dobjs[0])), 'Pixels must be square'

    if axes is None:
        fig, axs2 = plt.subplots(len(dobjs), 2, figsize=(10, 4*len(dobjs)))
        if len(axs2.shape) < 2:
            axs2 = [axs2]
    else:
        figs = [a.get_figure() for a in axes]
        assert len(set(figs)) == 1
        fig = figs[0]
        axs2 = list(zip(axes[0::2], axes[1::2]))

    # TODO: this is messy with a 2d array of axes - we want to flatten this ...
    # Display images and collect results in pandas df, one row per dicom object
    results = None
    for dobj, axs in zip(dobjs, axs2):
        # Image data
        image = image_from_dicom(dobj, frame, dtype=float)
        pix_dims = pix_spacing_yx(dobj)

        # Interpolate up to 256*256 if less
        image, scale_y, scale_x = _interpolate_to_min_resolution(image, 256)
        pix_dims = pix_dims[0] * scale_y, pix_dims[1] * scale_x
        ny, nx = image.shape

        # Find the phantom
        expected_radius = phantom['Diameter'] / 2 / pix_dims[0]
        centre_x, centre_y, radius = find_phantom(image, expected_radius)

        # Phantom ROI
        phantom_mask = circular_mask(image, 0.85 * radius, centre_x, centre_y)
        margin_w = centre_x - 1.25 * radius
        margin_e = centre_x + 1.25 * radius
        margin_n = centre_y - 1.25 * radius
        margin_s = centre_y + 1.25 * radius

        # Ghost ROIs
        ghost_mask_w = rectangular_mask(image, 0, margin_w, margin_n, margin_s)
        ghost_mask_e = rectangular_mask(image, margin_e, nx-1, margin_n, margin_s)
        ghost_mask_n = rectangular_mask(image, margin_w, margin_e, 0, margin_n)
        ghost_mask_s = rectangular_mask(image, margin_w, margin_e, margin_s, ny-1)

        # Intensities in ROIs
        s_p = np.ma.masked_where(~phantom_mask, image).mean()
        s_n = np.ma.masked_where(~ghost_mask_n, image).mean()
        s_s = np.ma.masked_where(~ghost_mask_s, image).mean()
        s_e = np.ma.masked_where(~ghost_mask_e, image).mean()
        s_w = np.ma.masked_where(~ghost_mask_w, image).mean()

        # Ghost Ratio
        aapm_gr = abs(((s_w + s_e) - (s_n + s_s)) / (2 * s_p))

        # Standard windowed image with detected phantom position
        axs[0].imshow(image, cmap='bone')
        axs[0].imshow(phantom_mask, cmap='rainbow', alpha=0.25)
        axs[0].axis('image')
        axs[0].axis('off')
        axs[0].add_artist(
            plt.Circle((centre_x, centre_y), radius=radius, color='r', fill=False)
        )
        axs[0].set_title(protocol_name(dobj).ljust(20)[:20].strip('_'))

        # Show phase encoding direction
        add_phase_encode_mark(axs[0], phase_enc_dirn(dobj))

        # Low windowed image to show ghosts with ROIs
        mask_cmap = ListedColormap([
            (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)
        ])

        # Try and make "ghost" window more robust using the 98th percentile
        # of the background instead of fixed 0.02 times the phantom maximum
        vmax = np.percentile(
            np.ma.array(
                image,
                mask=~(ghost_mask_w | ghost_mask_e | ghost_mask_n | ghost_mask_s)
            ).compressed(),
            98
        )
        axs[1].imshow(
            np.where(image > 0, image, 0),
            cmap='viridis', vmax=vmax
        )
        axs[1].imshow(
            ghost_mask_n | ghost_mask_s | ghost_mask_e | ghost_mask_w,
            vmax=1, cmap=mask_cmap, alpha=0.25
        )
        axs[1].axis('image')
        axs[1].axis('off')
        axs[1].set_title(
            '%s(%s): Image %d:%d, GR:%0.2f%%' % (
                approx_slice_orientation(dobj), approx_phase_orientation(dobj),
                series_number(dobj), dobj.InstanceNumber, 100 * aapm_gr
            )
        )

        field_of_view_mm = (
            matrix_yx(dobj)[0] * pix_spacing_yx(dobj)[0],
            matrix_yx(dobj)[1] * pix_spacing_yx(dobj)[1]
        )

        result = pd.DataFrame.from_dict({
            'Series':         [series_number(dobj)],
            'Frames':         [number_of_frames(dobj)],
            'TR':             [t_r(dobj)],
            'TE':             [t_e(dobj)],
            'Matrix':         [matrix_yx(dobj)],
            'Sequence':       [seq_name(dobj)],
            'FoV':            [field_of_view_mm],
            'Bandwidth':      [readout_bandwidth(dobj)],
            'PhaseAxis':      [phase_enc_dirn(dobj)],
            'PhaseDirection': [approx_phase_orientation(dobj)],
            'Protocol':       [protocol_name(dobj)],
            'Orientation':    [approx_slice_orientation(dobj)],
            'Phantom':        [s_p],
            'Left':           [s_w],
            'Right':          [s_e],
            'Top':            [s_n],
            'Bottom':         [s_s],
            'GhostRatio':     [100 * aapm_gr]
        }).set_index('Series')

        results = result if results is None else pd.concat([results, result], ignore_index=True)

    fig.suptitle('Ghosting [%s]' % seq_name(dobj), fontsize=16)

    return results
