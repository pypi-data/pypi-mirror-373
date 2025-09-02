#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ghosting.py: epi ghosting assessment (from fbirn).

external dependencies:
- scikit-image
"""

from glob import glob
import os.path

import numpy as np

from skimage.filters import threshold_otsu
from skimage.morphology import binary_dilation
from skimage.morphology.footprints import square
from skimage.measure import label, regionprops

from pydicom import dcmread


# Analysis II (FBIRN Only)
def phantom_mask_2d(image, dilate=False):
    """
    Generate an (optionally) dilated mask of phantom using an Otsu Threshold.

    Parameters
    ----------
    image: Numpy rank-2 image array (ny,nx)

    Returns
    -------
    Numpy binary mask array of same dimensions

    """
    # Global otsu threshold
    threshold = threshold_otsu(image)
    mask = image > threshold

    # Clean out small artefact regions using connected component analysis
    labels = label(mask)
    phantom_label = sorted(regionprops(labels), key=lambda x: x.area)[-1].label
    mask = (labels == phantom_label)

    # Dilate the mask
    if dilate:
        mask = binary_dilation(mask, square(3))

    return mask


def ghost_mask(ph_mask, pe_axis='col'):
    """
    Return the ghost region given the phantom mask.

    This is just the mask defining the phantom rolled by
    half the field of view in the 'phase-encoding' direction
    to match the Nyquist N/2 ghost position.

    Parameters
    ----------
    ph_mask: Numpy 8 bit mask representing phantom in image
    pe_axis: The phase encoding direction {'col', 'row'}

    Returns
    -------
    Numpy 8 bit mask array of same dimensions

    """
    # Handle single slice or volumes
    if np.ndim(ph_mask) == 2:
        ny, nx = ph_mask.shape
        col_axis, row_axis = 0, 1
    elif np.ndim(ph_mask) == 3:
        _, ny, nx = ph_mask.shape
        col_axis, row_axis = 1, 2
    else:
        raise ValueError('Only Rank 2 and 3 masks allowed')

    # Roll by n/2 in phase encoding direction (default will be column)
    if pe_axis == 'col':
        rolled_mask = np.roll(ph_mask, ny//2, col_axis)
    elif pe_axis == 'row':
        rolled_mask = np.roll(ph_mask, nx//2, row_axis)
    else:
        raise ValueError("Only 'row' and 'col' allowed as axes for ghost mask")

    return rolled_mask


def slice_ghostiness(slice_, pe_axis='col'):
    """
    Ghostiness statistics.

    Returns four ghost statistics for a given volume:
        phantom mean, host mean, bright ghost mean and snr

    Parameters
    ----------
    slice: Numpy rank-2 image (at single timepoint)
    pe_axis: The phase encoding direction {'col', 'row'}

    Returns
    -------
    Tuple of statistics

    """
    # Phantom, ghost masks
    ph_mask_tight = phantom_mask_2d(slice_, dilate=False)
    ph_mask_loose = phantom_mask_2d(slice_, dilate=True)

    # Host is just phantom mask rolled along phase encoding direction
    gh_mask = ghost_mask(ph_mask_tight, pe_axis)

    # Masks for phantom only, ghost only and noise background only
    p_only_mask =  ph_mask_tight & ~gh_mask
    g_only_mask = ~ph_mask_loose &  gh_mask
    n_only_mask = ~ph_mask_loose & ~gh_mask

    # Generate masked arrays from volume and masks and use them to get stats
    # NB take ones complement as masked means ignore in numpy masked arrays
    p_only_marray = np.ma.array(slice_, mask=~p_only_mask)
    g_only_marray = np.ma.array(slice_, mask=~g_only_mask)
    n_only_marray = np.ma.array(slice_, mask=~n_only_mask)

    # Calculate some useful stats
    pmean = p_only_marray.mean()
    nmean = n_only_marray.mean()
    nstd  = n_only_marray.std()
    snr   = nmean / nstd
    gmean = g_only_marray.mean()

    # Sort all of voxels in ghost and find average of top decile
    # This is the mean of the 'bright ghosts' according to the fBIRN protocol
    voxel_count  = g_only_marray.count()
    voxel_list   = g_only_marray.flatten()
    voxel_list.sort(axis=None, endwith=False)
    voxel_list   = voxel_list[-voxel_count//10:]
    bright_gmean = voxel_list.mean()

    # TODO: SNR looks dubious here - unclear whether it is needed
    # Return tuple of statistics
    return pmean, gmean, bright_gmean, snr


if __name__ == "__main__":

    class Usage(Exception):
        """Usage."""

        def __init__(self, msg):
            Exception.__init__(self)
            self.msg = msg

    import getopt
    import sys

    try:
        try:
            opts, args = getopt.getopt(
                sys.argv[1:],
                'hi', ['help', 'interactive']
            )
        except getopt.error as e:
            raise Usage(e)

        # process options
        interactive = True
        for opt, _ in opts:
            if opt in ('-h', '--help'):
                print(__doc__)
                sys.exit(0)
            if opt in ('-i', '--interactive'):
                interactive = True

        if len(args) < 1:
            raise Usage('No data directory specified')

        for datadir in args:
            for fname in glob(os.path.join(datadir, '*')):
                d = dcmread(fname)
                print(datadir, d.InstanceNumber, slice_ghostiness(d.pixel_data()))

        sys.exit(0)

    except Usage as err:
        print('%s, for help please use --help' % err.msg, file=sys.stderr)
        sys.exit(2)
