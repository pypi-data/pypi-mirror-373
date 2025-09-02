#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analysis Routines for fMRI QA Images
See: Friedman and Glover JMRI 23:827-839 (2006)
See: http://www.birncommunity.org/resources/supplements/fbirn-recommendations-for-multi-center-fmri-studies/supplement-iv-fbirn-quality-assurance-program/
See: http://www.nitrc.org/projects/fbirn/
See: https://xwiki.nbirn.org:8443/xwiki/bin/view/Function-BIRN/AutomatedQA
See: http://www.fmrib.ox.ac.uk/analysis/techrep/tr00mj3/tr00mj3.pdf
See: Forman et al MRM 33:636-547 (1995)
See: Afni helper routines used in BIRN analysis: 3dvolreg 3dDetrend, 3dTstat, 3dAutomask, 3DFWHMx

Dependencies:
   Scikit-image for generating masks for Phantom vs Background
"""

from math import modf, ceil, sqrt, log
from datetime import datetime
from warnings import warn

import numpy as np
from scipy.stats import variation

# For Automatic Thresholding
from scipy.ndimage import median_filter, binary_fill_holes
from skimage.filters import threshold_otsu, sobel
from skimage.morphology import disk, binary_dilation, binary_erosion
from skimage.segmentation import watershed

from . dcmio import manufacturer, is_enhancedmr, is_multiframe


def is_mosaic(dobj):
    """
    Whether a dicom object is in Siemens proprietory mosaic form (VB17-VE11C).

    Parameters
    ----------
    dobj : dicom object

    Returns
    -------
    bool : whether the object is in Siemens MOSAIC format

    """
    return (
        manufacturer(dobj) == 'Siemens' and
        'X' not in dobj.SoftwareVersions and
        'MOSAIC' in [s.upper() for s in dobj.ImageType]
    )


def multiframe_ndims(dobj):
    """
    Number of dimensions in an enhanced mr multiframe.

    Parameters
    ----------
    dobj : dicom object

    Returns
    -------
    int : the number of the dimensions in the multiframe

    """
    if not is_multiframe(dobj):
        raise ValueError("Dicom object is not a multiframe")
    return len(dobj.DimensionIndexSequence)


def multiframe_shape(dobj):
    if not is_multiframe(dobj):
        raise ValueError("Dicom object is not a multiframe")

    pffgs = dobj.PerFrameFunctionalGroupsSequence
    dis = dobj.DimensionIndexSequence

    # Assume this layout for first part
    # Stack ID
    assert dis[0].DimensionIndexPointer == (0x0020, 0x9056)
    assert dis[0].FunctionalGroupPointer == (0x0020, 0x9111)
    # In-Stack Position Number
    assert dis[1].DimensionIndexPointer == (0x0020, 0x9057)
    assert dis[1].FunctionalGroupPointer == (0x0020, 0x9111)
    # Temporal Position Index
    assert dis[2].DimensionIndexPointer == (0x0020, 0x9128)
    assert dis[2].FunctionalGroupPointer == (0x0020, 0x9111)

    # number of unique values along each dimension axes
    # TODO: can we get this directly?
    dims = np.array([
        pffg.FrameContentSequence[0].DimensionIndexValues
        for pffg in pffgs
    ]).T

    return tuple(len(set(dim)) for dim in dims)


def acquisition_time_seconds(dobj):
    """
    Acquisition time of dicom object or first frame in object in seconds.

    Parameters
    ----------
    dobj : dicom object

    Returns
    -------
    float : the acquisition time of the object

    """
    def _tm_to_seconds(tm):
        ss, uu = modf(float(tm))
        mm, ss = divmod(ss, 100)
        hh, mm = divmod(mm, 100)
        return 3600 * hh + 60 * mm + ss + uu

    if 'AcquisitionTime' in dobj:
        # Siemens
        return _tm_to_seconds(dobj.AcquisitionTime)

    if 'TemporalPositionIdentifier' in dobj and 'RepetitionTime' in dobj:
        # GE
        return (dobj.TemporalPositionIdentifier - 1) * int(dobj.RepetitionTime) / 1000

    if is_enhancedmr(dobj):
        pffgs = dobj.PerFrameFunctionalGroupsSequence
        sfgs = dobj.SharedFunctionalGroupsSequence
        frame_contents = pffgs[0].FrameContentSequence[0]
        if 'FrameAcquisitionDateTime' in frame_contents:
            frame_acq_time = datetime.strptime(
                frame_contents.FrameAcquisitionDateTime, '%Y%m%d%H%M%S.%f'
            )
            return (frame_acq_time - datetime(2001, 1, 1)).total_seconds()
        elif 'TemporalPositionIndex' in frame_contents:
            temporal_index = frame_contents[0]
            t_r = sfgs[0].MRTimingAndRelatedParametersSequence[0].RepetitionTime / 1000
            return t_r * (temporal_index - 1)
        else:
            return 0

    raise KeyError('Acquisition Time or equivalent not found in DICOM object')


def stack_from_mosaic(dobj, nimages=None):
    """
    Extract a stack of images from a mosaic dicom object.

    Returns a rank 3 numpy array organized nz,ny,nx

    Parameters
    ----------
    dobj :
        A mosaic pydicom dicom object.
    nimages :
        Number of images expected in mosaic.

    Returns
    -------
    ndarray (3d): stack of images from Siemens dicom mosaic

    """
    # Check we have moaic with the right number of images
    assert is_mosaic(dobj)
    _NumberOfImagesInMosaic = (0x0019, 0x100a)
    if _NumberOfImagesInMosaic in dobj:
        if nimages is None:
            nimages = dobj[_NumberOfImagesInMosaic].value
        else:
            assert dobj[_NumberOfImagesInMosaic].value == nimages
    assert nimages is not None

    # Get the dicom image data as a numpy array
    mosaic = dobj.pixel_array & (2**dobj.BitsStored - 1)

    # Deduce the number of tiles and image size in mosaic from number of images
    # - assumes the mosaic is always 'square'
    ntiles = int(ceil(sqrt(nimages)))
    ny, nx = mosaic.shape[0]//ntiles, mosaic.shape[1]//ntiles

    # Unpack into a 3d numpy volume (nz, ny, nx)
    stack = np.zeros([nimages, ny, nx], dtype=mosaic.dtype)
    for i in range(nimages):
        x0 = (i % ntiles) * nx
        y0 = (i // ntiles) * ny
        stack[i] = mosaic[y0:y0+ny, x0:x0+nx]

    return stack


def quadratic_trend(y):
    """
    Quadratic trend.

    Return quadratic fit to y. Assumes equal spacing.

    Parameters
    ----------
    y : A numpy vector (ndarray)

    Returns
    -------
    ndarray (1d): quadratic fit interpolation of vector

    """
    x = list(range(len(y)))
    a, b, c = np.polyfit(x, y, deg=2)
    return np.polyval((a, b, c), x)


def detrend_quadratic(ys):
    """
    Quadratic detrending.

    May be called with an array - detrending is on the *first* index

    Return ys minus quadratic fit to ys.

    Parameters
    ----------
    ys : A numpy vector or ND array [ny, na, nb, nc]


    Returns
    -------
    ndarray : quadratic detrend of one or more vectors

    """
    # Flatten all but the first dimension - polyfit takes 1D or 2D only.
    shape = ys.shape
    nx = shape[0]
    ys_flat = ys.reshape(nx, -1)

    # Fit second order polynomial and subtract
    xs = np.arange(nx)
    abcs = np.polynomial.polynomial.polyfit(xs, ys_flat, deg=2)
    ys_flat_fit = np.polynomial.polynomial.polyval(xs, abcs, tensor=True).T

    ys_flat_detrended = ys_flat - ys_flat_fit
    ys_detrended = ys_flat_detrended.reshape(*shape)

    return ys_detrended


def dicom_objs_sorted_on_time(dobjs):
    """
    Sort list of mosaics, multiframes or single objects.
    These are respectively one time point, the whole series or single image.
    Returns a list of dicom objects sorted appropriately.
    For a multiframe this is a list with a single item.

    Parameters
    ----------
    dobjs : list
        list of pydicom objects.

    Returns
    -------
    list : dicom objects sorted by acquisition time
    """

    if not dobjs:
        raise ValueError('No dicom objects')

    # Handle multiframes, mosaics and singleframes
    if any(map(is_multiframe, dobjs)):
        if all(multiframe_shape(d)[2] == 1 for d in dobjs):
            # Siemens stack of 3D multiframes
            return sorted(dobjs, key=acquisition_time_seconds)
        elif len(dobjs) == 1 and multiframe_shape(dobjs[0])[2] > 1:
            # Philips 4D multiframe
            return dobjs
    elif all(map(is_mosaic, dobjs)):
        # A mosaic series (siemens), sort by time
        # (AcquisitionTime is used by Siemens)
        if len(dobjs) < 2:
            raise ValueError(
                "No time series, only %d dicom objects" % len(dobjs)
            )
        return sorted(dobjs, key=acquisition_time_seconds)
    elif not any(map(is_mosaic, dobjs)) and not any(map(is_multiframe, dobjs)):
        # A basic one image per object (ge) series, sort spatio-temporally
        # TemporalPositionIdentifier is used by GE, AcquisitionTime by Siemens
        if len(dobjs) < 2:
            raise ValueError(
                "No time-space series, only %d dicom objects" % len(dobjs)
            )
        if 'TemporalPositionIdentifier' in dobjs[0]:
            return sorted(
                dobjs,
                key=lambda d: (d.TemporalPositionIdentifier, d.SliceLocation)
            )
        else:
            return sorted(dobjs, key=acquisition_time_seconds)
    else:
        raise ValueError(
            "Inconsistent series: mixture of multiframes, mosaics or single slices"
        )


def time_series_single(dobjs, maxtimes=1_000_000):
    """
    Extract a GE fmri time series in basic 'single frame for object' form.

    Also a Siemens series in non-mosaic form
    Each file is expected to be one time point and one slice
    Uses TemporalPositionIdentifier which is defined by GE instead of
    AcquisitionTime. Returns a rank 4 numpy array organized nt,nz,ny,nx

    Parameters
    ----------
    dobjs :
        dicom objects sorted on time.
    maxtimes :
        maximum number of time points to consider
    Returns
    -------
    tuple: ndarray 4d volume series, tuple of voxel dimensions

    """
    # Get as list of dicom objects
    if is_mosaic(dobjs[0]) or is_multiframe(dobjs[0]):
        raise ValueError('Not a single frame time series')

    # Number of distinct slice locations and inferred number of time points
    nslices = len(set([d.SliceLocation for d in dobjs]))
    ntimes = min(maxtimes, len(dobjs) // nslices)

    # Re-sort to get slices in the right order
    if 'TemporalPositionIdentifier' in dobjs[0]:
        dobjs = sorted(
            dobjs,
            key=lambda d: (d.TemporalPositionIdentifier, d.SliceLocation)
        )
    else:
        # Siemens case is tricky as acquisition order is not slice order
        # when (as is usually the case) it is interleaved
        dobjs = sorted(
            dobjs, key=lambda d: (d.SliceLocation, acquisition_time_seconds(d))
        )
        # now we want to regroup with time as first sort key ...
        dobjs_resorted = []
        for itime in range(ntimes):
            dobjs_resorted += dobjs[itime::ntimes]
        dobjs = dobjs_resorted

    # Pixel and slice spacing in mm
    dy, dx = map(float, dobjs[0].PixelSpacing)
    dz = float(dobjs[0].SpacingBetweenSlices)

    # Temporal spacing in seconds
    if 'NumberOfTemporalPositions' in dobjs[0]:
        # GE style
        # We'll use ntimes from above rather than here so as to better handle frames missiong at the end
        if ntimes < dobjs[0].NumberOfTemporalPositions and ntimes != maxtimes:
            warn(f'Fewer images than number of temporal Positions: {ntimes}({dobjs[0].NumberOfTemporalPositions})')
        # We'll assume that the TR gives us the dt as we've no easy way to get
        # it from the times in the dicom objects as all the acquisition times
        # are the same!
        dt = float(dobjs[0].RepetitionTime) / 1000
    else:
        # Siemens VB  non-mosaic style - every slice gets its own acquisition time
        acq_times = sorted(
            set(acquisition_time_seconds(d) for d in dobjs)
        )
        dt = acq_times[1] - acq_times[0]

    # Fill a 4D stack from the image data of each object
    ny, nx = dobjs[0].pixel_array.shape
    dtype = dobjs[0].pixel_array.dtype
    stack4 = np.zeros([ntimes, nslices, ny, nx], dtype=dtype)
    for t_i in range(ntimes):
        for z_i in range(nslices):
            stack4[t_i, z_i, :, :] = (
                dobjs[t_i * nslices + z_i].pixel_array.view(np.uint16) &
                (2**dobjs[t_i * nslices + z_i].BitsStored - 1)
            ).view(dtype)

    # Return as a 4d float numpy array (t, z, y, x), nb voxel dimensions is in opposite order
    return stack4.astype(np.float64), (dx, dy, dz, dt)


def time_series_mosaic(dobjs, maxtimes=1_000_000):
    """
    Extract an fmri time series in mosaic form from specified dicom obejcts.

    Each object is expected to be one time point
    Returns a rank 4 numpy array organized nt,nz,ny,nx

    Parameters
    ----------
    directory :
        Name of directory containing dicom files.
    maxtimes :
        maximum number of time points to consider

    Returns
    -------
    tuple: ndarray 4d volume series, tuple of voxel dimensions

    """
    # Siemens Private Tag
    _NumberOfImagesInMosaic = 0x0019, 0x100a

    if not is_mosaic(dobjs[0]):
        raise ValueError('Not a mosaic time series')

    # Pixel and slice spacing in mm
    dy, dx = map(float, dobjs[0].PixelSpacing)
    dz = float(dobjs[0].SpacingBetweenSlices)

    if len(dobjs) > maxtimes:
        dobjs = dobjs[:maxtimes]

    # Temporal spacing in seconds
    acq_times = [acquisition_time_seconds(d) for d in dobjs]
    dt = acq_times[1] - acq_times[0]

    # Expand out the mosaics
    nimages = int(dobjs[0][_NumberOfImagesInMosaic].value)
    stacks = [stack_from_mosaic(dobj, nimages) for dobj in dobjs]

    # A 4d float numpy array (t, z, y, x), nb voxel sizes returned in opposite order
    return np.array(stacks, dtype=np.float64), (dx, dy, dz, dt)


def time_series_enhanced(dobj, maxtimes=1_000_000):
    """
    Extract an fmri time series in enhanced form from specified dicom object.

    We expect a single file with the full time series.
    Returns rank 4 numpy array organized nt,nz,ny,nx and the pixel dimensions.

    Parameters
    ----------
    dobj:
        Multiframe
    maxtimes :
        maximum number of time points to consider

    Returns
    -------
    tuple: ndarray 4d volume series, tuple of voxel dimensions
    """
    if not is_multiframe(dobj):
        raise ValueError('Not a multiframe time series')

    # Pixel and slice spacing in mm
    dy, dx = map(float, dobj.PerFrameFunctionalGroupsSequence[0].PixelMeasuresSequence[0].PixelSpacing)
    if 'SpacingBetweenSlices' in dobj:
        dz = float(dobj.SpacingBetweenSlices)
    else:
        dz = float(dobj.PerFrameFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SpacingBetweenSlices)

    # Temporal spacing: fall back to TR as FrameAcquisitionDateTime is broken in Philips - all the same
    '''
    datetimes = sorted(set([
        datetime.datetime.strptime(pffg.FrameContentSequence[0].FrameAcquisitionDateTime, '%Y%m%d%H%M%S.%f')
            for pffg in dobj.PerFrameFunctionalGroupsSequence
    ]))
    dt = (datetimes[1] - datetimes[0]).total_seconds() * 1000
    '''
    # Temporal spacing in seconds
    dt = float(
        dobj.SharedFunctionalGroupsSequence[0].MRTimingAndRelatedParametersSequence[0].RepetitionTime
    ) / 1000

    # Dimensions of multiframe
    nslices = len(set(
        pffg.FrameContentSequence[0].InStackPositionNumber
        for pffg in dobj.PerFrameFunctionalGroupsSequence
    ))
    ntimes = len(set(
        pffg.FrameContentSequence[0].TemporalPositionIndex
        for pffg in dobj.PerFrameFunctionalGroupsSequence
    ))
    nrows = dobj.Rows
    ncols = dobj.Columns

    # Decorated indices into multiframe, sort on time, position and use to reorder multiframe
    sortkeys = [
        ((pffg.FrameContentSequence[0].TemporalPositionIndex, pffg.FrameContentSequence[0].InStackPositionNumber), i)
        for (i, pffg) in enumerate(dobj.PerFrameFunctionalGroupsSequence)
    ]
    indices = [i[1] for i in sorted(sortkeys, key=lambda x: x[0])]

    # Make sure correctly ordered - by time then by slice

    # frame_list = zip(*sorted(zip(list(dobj.pixel_array), sortkeys), key=lambda x: x[1]))[0]
    imarray = dobj.pixel_array[indices].reshape(
        (ntimes, nslices, nrows, ncols)
    )
    if len(imarray) > maxtimes:
        imarray = imarray[:maxtimes]
    # A 4d float numpy array (t, z, y, x), nb voxel sizes returned in opposite order
    return imarray.astype(np.float64), (dx, dy, dz, dt)


def time_series_hybrid(dobjs, maxtimes=1_000_000):
    """
    Extract an fmri time series in enhanced form from sequence of dicom objects.

    We expect a multiple files each with the spatial series.
    Returns rank 4 numpy array organized nt,nz,ny,nx and the pixel dimensions.

    Parameters
    ----------
    directory :
        Name of directory containing dicom files.
    maxtimes :
        maximum number of time points to consider

    Returns
    -------
    tuple: ndarray 4d volume series, tuple of voxel dimensions

    """
    if not all(is_multiframe(d) for d in dobjs):
        raise ValueError('Some objects are not multiframes')
    if not all(multiframe_ndims(d) == 3 for d in dobjs):
        raise ValueError('Some objects have the wrong dimension')
    if not all(multiframe_shape(d)[2] == 1 for d in dobjs):
        raise ValueError('Some objects have multiple time points in multiframe')
    if len(dobjs) < 2:
        raise ValueError('More than one time point required')

    # Pixel and slice spacing in mm
    dobj0 = dobjs[0]
    dy, dx = map(float, dobj0.PerFrameFunctionalGroupsSequence[0].PixelMeasuresSequence[0].PixelSpacing)
    if 'SpacingBetweenSlices' in dobj0:
        dz = float(dobj0.SpacingBetweenSlices)
    else:
        dz = float(dobj0.PerFrameFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SpacingBetweenSlices)

    # Temporal spacing in seconds (already sorted by time)
    # TODO: the times don't seem to be changing ....
    # need to look for another field to use
    acq_times = [acquisition_time_seconds(d) for d in dobjs]
    dt = acq_times[1] - acq_times[0]

    # Dimensions of multiframes
    nslices = len(set(
        pffg.FrameContentSequence[0].InStackPositionNumber
        for pffg in dobj0.PerFrameFunctionalGroupsSequence
    ))
    nrows = dobj0.Rows
    ncols = dobj0.Columns

    # Decorated indices into multiframe, sort on position and use to reorder multiframe
    sortkeys = [
        (pffg.FrameContentSequence[0].InStackPositionNumber, i)
        for (i, pffg) in enumerate(dobj0.PerFrameFunctionalGroupsSequence)
    ]
    indices = [i[1] for i in sorted(sortkeys, key=lambda x: x[0])]

    # Make sure correctly ordered - by time then by slice
    imarray = np.array([
        d.pixel_array[indices].reshape((nslices, nrows, ncols))
        for d in dobjs
    ])

    if len(imarray) > maxtimes:
        imarray = imarray[:maxtimes]

    # A 4d float numpy array (t, z, y, x), nb voxel sizes returned in opposite order
    return imarray.astype(np.float64), (dx, dy, dz, dt)


def time_series_generic(dobjs, maxtimes=1_000_000):
    """
    Assemble a time series from DICOM objects independent of the manufacturer.

    Parameters
    ----------
    dobjs:
        list of dicom objects
    maxtimes :
        maximum number of time points to consider

    Returns
    -------
    tuple: ndarray 4d volume series, tuple of voxel dimensions

    """
    if not dobjs:
        ValueError('Empty list of dicom objects')

    if manufacturer(dobjs[0]) == 'Philips' and is_enhancedmr(dobjs[0]):
        if len(dobjs) > 1:
            raise ValueError('More than multiframe is Philips series')
        if not all(multiframe_shape(d)[2] > 1 for d in dobjs):
            raise ValueError('Wrong multiframe shape in Philips series')
        return time_series_enhanced(dobjs[0], maxtimes)
    elif manufacturer(dobjs[0]) == 'Siemens' and is_enhancedmr(dobjs[0]):
        if len(dobjs) < 2:
            raise ValueError('Multiple multiframes required for Siemens enhanced time series')
        if not all(multiframe_shape(d)[2] == 1 for d in dobjs):
            raise ValueError('Wrong multiframe shape in Siemens series')
        return time_series_hybrid(dobjs, maxtimes)
    elif manufacturer(dobjs[0]) == 'Siemens' and not is_enhancedmr(dobjs[0]) and is_mosaic(dobjs[0]):
        if len(dobjs) < 2:
            raise ValueError('Multiple objects required for Siemens mosaic time series')
        return time_series_mosaic(dobjs, maxtimes)
    elif not is_enhancedmr(dobjs[0]):
        if len(dobjs) < 2:
            raise ValueError('Multiple objects required for single images time series')
        return time_series_single(dobjs, maxtimes)
    else:
        raise ValueError('Time series form not recognised')


def get_roi(slice_time_series, roisize):
    """
    Extract a central square region of interest.

    ROI of specified linear size across in pixels.
    Friedman and Glover use a 21*21 ROI but
    15 or 16 used elsewhere.

    Returns a rank-3 numpy sub-array (nt,ny,nx)

    Parameters
    ----------
    slice_time_series :
        Numpy array organised (nt, ny, nx).
    roisize :
        Size in pixels of square ROI

    Returns
    -------
    ndarray: region of interest in a sklice as fn of time (nt, ny, nx)
    """
    nt, ny, nx = slice_time_series.shape
    return slice_time_series[
        :,
        int(ny/2-roisize/2):int(ny/2+roisize/2),
        int(nx/2-roisize/2):int(nx/2+roisize/2)
    ]


def signal_image(image_series):
    """
    Analysis 1A: Signal Image.

    Mean image across all time points
    Returns image of mean signal intensity over time

    Parameters
    ----------
    image_series :
        Numpy array organised (nt, ny, nx).

    Returns
    -------
    ndarray: mean signal slice averaging over time (2D)


    """
    return np.mean(np.asarray(image_series, dtype=float), axis=0)


def temporalnoise_fluct_image(image_series, mask_background=True):
    """
    Analysis 1B: Signal-to-Fluctuation-Noise-Ratio Image.

    Image of residuals after detrending on a pixel by pixel basis.

    Parameters
    ----------
    image_series : ndarray
        2D time series organised (nt, ny, nx)
    mask_background: bool
        mask out the background first

    Returns
    -------
    ndarray: temporal fluctation slice (2D)

    """
    # Iteration over pixels
    # TODO: is there any way to vectorise this?
    nt, ny, nx = image_series.shape
    fluct_noise = np.zeros([ny, nx])
    for y in range(ny):
        for x in range(nx):
            fluct_noise[y, x] = np.std(
                detrend_quadratic(image_series[:, y, x])
            )

    # Optionally mask out background (but beware if dividing by it later ..)
    if mask_background:
        signal = signal_image(image_series)
        fluct_noise[~phantom_mask_2d(signal)] = 0

    return fluct_noise


def sfnr_image(image_series, mask_background=True):
    """
    Analysis 1C: Signal-to-Fluctuation-Noise-Ratio Image.

    Temporal noise fluctation image normalised to signal.

    Parameters
    ----------
    image_series : ndarray
        2D time series organised (nt, ny, nx)
    mask_background: bool
        mask out the background first

    Returns
    -------
    ndarray: Signal-to-Fluctuation-Noise slice (2D)

    """
    signal = signal_image(image_series)
    fluct_noise = temporalnoise_fluct_image(
        image_series, mask_background=False
    )

    # NB BIRN matlab code uses eps to avoid division by zero
    fluct_noise[fluct_noise < 0.1] = 0.1

    # The ratio is the 'SFNR' image
    sfnr = signal / fluct_noise

    # Optionally mask out background
    if mask_background:
        sfnr[~phantom_mask_2d(signal)] = 0

    return sfnr


def sfnr_summary(image_series, roisize=21):
    """
    Analysis 1D: Signal-to Fluctuation-Noise Summary.

    Parameters
    ----------
    image_series : ndarray
        2D time series organised (nt, ny, nx)
    roisize: int
        size of region of interest to use

    Returns
    -------
    float: snr summary value

    """
    return np.mean(
        sfnr_image(
            get_roi(image_series, roisize),
            mask_background=False
        )
    )


def static_spatial_noise_image(image_series, mask_background=True):
    """
    Analysis 2: Static Spatial Noise.

    Difference between odd and even images in time series.
    Input is a time series of single plane images.
    Returns a single image of the static spatial noise.

    Parameters
    ----------
    image_series : ndarray
        2D time series organised (nt, ny, nx)
    mask_background: bool
        mask out the background first

    Returns
    -------
    ndarray: spnr slice (2D)

    """
    # Difference of sums of even and odd time points separately
    sum_even = np.sum(image_series[0::2, :, :], axis=0)
    sum_odd = np.sum(image_series[1::2, :, :], axis=0)
    diff_image = sum_odd - sum_even

    # Optionally mask out region outside phantom
    if mask_background:
        signal = np.mean(image_series, axis=0)
        diff_image[~phantom_mask_2d(signal)] = 0

    return diff_image


def snr_summary(image_series, roisize=21):
    """
    Analysis 3: SNR Summary Value.

    Derived from variance in ROI of the static spatial noise image.

    Parameters
    ----------
    image_series : ndarray
        2D time series organised (nt, ny, nx)
    rois_size: int
       size of region of interest to consider

    Returns
    -------
    ndarray: spnr slice (2D)

    """
    nt, _, _ = image_series.shape

    roi = get_roi(image_series, roisize)
    ssn_diff = static_spatial_noise_image(roi, mask_background=False)
    variance_summary_value = np.std(ssn_diff)**2

    # Signal image is mean along time axis
    signal = np.mean(roi, axis=0)

    # Summary value is mean across pixels in ROI
    signal_summary_value = np.mean(signal)

    # This is what Friedman & Glover specify.
    # It is also what is implemented in both the old and new fBIRN protocols
    return signal_summary_value / sqrt(variance_summary_value / nt)


def signal_summary(image_series, roisize=21):
    """
    Analysis 3B: Signal Summary Value.

    Mean of all pixels in roi across all time points

    Parameters
    ----------
    image_series : ndarray
        2D time series organised (nt, ny, nx)
    rois_size: int
       size of region of interest to consider

    Returns
    -------
    ndarray: spnr slice (2D)

    """
    # Signal image is mean along time axis
    signal_image = np.mean(get_roi(image_series, roisize), axis=0)
    return np.mean(signal_image)


def fluctuation_and_drift(image_series, roisize=21):
    """
    Analysis 4: Percentage Fluctuation and Drift.

    With raw drift as per fBIRN protocol
    Returns a tuple of statistics for the given roi size:
        sd_resids:
            Standard deviation of redsiduals
        percent_fluct:
            Percentage fluctuation
        drift_raw:
            Drift calculated from data (fBIRN)
        drift_fit:
            Drift calculated (Friedmann & Glover)

    Parameters
    ----------
    image_series: numpy rank 3 array
        a single slice at range of time points
    roisize: integer
        the width of the central square roi to analyse

    Returns
    -------
    tuple:  sd_resids, percent_fluct, drift_raw, drift_fit

    """
    # Time series of average intensity in ROI
    roi = get_roi(image_series, roisize)
    roi_means = np.mean(np.mean(roi, axis=2), axis=1)

    total_mean = np.mean(roi_means)

    # Quadratic trend curve
    trend = quadratic_trend(roi_means)

    # Parameters as defined in Friedman & Glover
    sd_resids = np.std(roi_means - trend)
    percent_fluct = 100*sd_resids/total_mean
    drift_fit = 100*(np.max(trend)-np.min(trend))/total_mean
    drift_raw = 100*(np.max(roi_means)-np.min(roi_means))/total_mean

    return (sd_resids, percent_fluct, drift_raw, drift_fit)


def roi_means_time_course(image_series, roisize=21):
    """
    Time series of mean intensities in ROI.

    Parameters
    ----------
    image_series: numpy rank 3 array
        a single slice at range of time points
    roisize: integer
        the width of the central square roi to analyse

    Returns
    -------
    ndarray:  time series

    """
    # Look at central ROI
    roi = get_roi(image_series, roisize)

    # Time series of ROI means (means along x and along y not along t)
    return np.mean(np.mean(roi, axis=2), axis=1)


def detrended_roi_time_course(image_series, roisize=21):
    """
    Detrended time series or ROI means.

    Parameters
    ----------
    image_series: numpy rank 3 array
        a single slice at range of time points
    roisize: integer
        the width of the central square roi to analyse

    Returns
    -------
    ndarray:  time series

    """
    return detrend_quadratic(roi_means_time_course(image_series, roisize))


def magnitude_spectrum(image_series, roisize=21):
    """
    Analysis 5: Fourier analysis of Residuals.

    Fourier magnitude spectrum of detrended ROI means.
    Detrending is on the means not pixel-by-pxel.
    Takes rank 3 numpy array (nt, ny, nx)
    Returns rank-1 numpy array of fourier components.

    Parameters
    ----------
    image_series: numpy rank 3 array
        a single slice at range of time points
    roisize: integer
        the width of the central square roi to analyse

    Returns
    -------
    ndarray:  magnitudes of Fourier components

    """
    roi_means = roi_means_time_course(image_series, roisize)

    # Use detrended series for fourier analysis
    complex_spectrum = np.fft.rfft(detrend_quadratic(roi_means))

    # Magnitude (nb not power for some reason) spectrum using mixed radix fft
    magn_spectrum = np.absolute(complex_spectrum)

    # NB rfft doesn't compute negative frequencies because of
    # the hermitian symmetry so the term at index 0 is the DC component
    # which we suppress here as suggested in the article.
    # Also NB length of spectrum is just n/2 + 1
    magn_spectrum[0] = 0

    # Scale (to percentage) by raw signal averages as done by current fBIRN s/w
    return 100.0 * magn_spectrum / np.mean(roi_means)


def weisskoff(image_series, max_roisize=21):
    """
    Analysis 6: Weisskoff analysis.

    Weisskoff, "Simple Measurement of ..."MRM 36:643 (1996)
    Returns radius of decorrelation and a vector of
    coefficients of variation as a function of side length of square ROI
    No mention is made of detrending in Friedman and Glover or Weisskoff,
    but it is clear from fBIRN that the data is to be detrended.
    We add back in the mean after detrending.

    Parameters
    ----------
    image_series: numpy rank 3 array
        a single slice at range of time points
    roisize: integer
        the width of the central square roi to analyse

    Returns
    -------
    tuple float, ndarray:  magnitudes of Fourier components

    """
    covs = []
    for roisize in range(1, max_roisize+1, 1):
        roi = get_roi(image_series, roisize)
        # Average over pixels of ROI at one timepoint
        roi_means = np.mean(np.mean(roi, axis=2), axis=1)
        # Coefficient of variation over time series
        cov = variation(detrend_quadratic(roi_means) + np.mean(roi_means))
        covs.append(cov)

    # Radius of decorrelation
    rdc = covs[0]/covs[-1]

    return rdc, np.array(covs)


# Analysis 7
# Simply plot rx/tx gains and centre frequency over time (days/weeks).
# TODO: To get the centre frequency shift we would need phase images ...
# Even then there is probably some correction going on in the sequence


# Extras (not specified in original paper but in the fBIRN potocol)

# Analysis I (fBIRN Only)
def centre_of_mass(volume_series):
    """
    Return volume centre of mass [(x,y,z), (x,y,z)..]) as a fn. of time.

    Parameters
    ----------
    volume_series: Numpy rank-4 volume time series

    Returns
    -------
    List of (x,y,z) tuple

    """
    nt, nz, ny, nx = volume_series.shape

    zramp, yramp, xramp = np.meshgrid(
        np.arange(nz), np.arange(ny), np.arange(nx),
        indexing='ij'
    )
    # Normalisation by total intensity (nb numpy 1.7+)
    volume_sums = np.sum(volume_series, (1, 2, 3))

    # List of (x, y, z) tuples
    c_of_ms = [
        (
            np.sum(volume_series[t] * xramp) / volume_sums[t],
            np.sum(volume_series[t] * yramp) / volume_sums[t],
            np.sum(volume_series[t] * zramp) / volume_sums[t]
        ) for t in range(nt)
    ]

    return c_of_ms


# Analysis II (FBIRN Only)
def phantom_mask_2d(image, filter_size=2, dilate=False, erode=False, disk_size=1.5):
    """
    Generate a dilated mask of the phantom using an Otsu Threshold and watershed segmentation.
    If multiple disjoint phantom slices are present (eg for a 3d volume flattened into a strip)
    then there will be multiple regions in the mask. Loosely based on scikit-image examples.

    TODO:RHD: there are still some magic numbers to sort out in here.

    Parameters
    ----------
    image: Numpy rank-2 image array (ny, nx)
    filter_size: scale of median filter preprocessing for initial Otsu threshold
    dilate: dilate mask before returning
    erode: erode mask before returning
    disk_size: structuring element size for dilation/erosion

    Returns
    -------
    Numpy binary mask array of same dimensions as input image

    """
    # Initial threshold for start of watershed
    threshold = threshold_otsu(median_filter(image, size=filter_size))

    # Handle empty or near empty slices at the ends
    if image.mean() < 10:
        return np.zeros_like(image, dtype=bool)

    mask = image > threshold
    if mask.sum() < 20:
        return mask

    # Watershed markers
    ws_markers = np.piecewise(
        image,
        [image < 0.1*threshold, image > 1.1*threshold],
        [1, 2]
    ).astype(int)

    # Edge elevation map
    elevation_map = sobel(image)
    mask = binary_fill_holes(watershed(elevation_map, ws_markers) - 1)

    if dilate:
        mask = binary_dilation(mask, disk(disk_size))
    if erode:
        mask = binary_erosion(mask, disk(disk_size))

    return mask


def ghost_mask(ph_mask, pe_axis='col'):
    """
    Return the ghost region given the phantom mask.

    This is just the mask defining the phantom rolled by
    half the field of view in the 'phase-encoding' direction
    to match the Nyquist N/2 ghost position. NB this will normally
    include some of the phantom as well unless the field of view is
    double the size of the phantom.

    Parameters
    ----------
    ph_mask: Numpy 8 bit mask representing phantom in image
    pe_axis: The phase encoding direction {'col', 'row'}

    Returns
    -------
    Numpy 8 bit mask array of same dimensions

    """
    # Handle single slice or volumes
    if ph_mask.ndim == 2:
        ny, nx = ph_mask.shape
        col_axis, row_axis = 0, 1
    elif ph_mask.ndim == 3:
        nz, ny, nx = ph_mask.shape
        col_axis, row_axis = 1, 2
    else:
        raise ValueError('Only Rank 2 and 3 masks allowed')

    # Roll by n/2 in phase encoding direction (default will be column)
    if pe_axis.lower() == 'col':
        rolled_mask = np.roll(ph_mask, ny//2, col_axis)
    elif pe_axis.lower() == 'row':
        rolled_mask = np.roll(ph_mask, nx//2, row_axis)
    else:
        raise ValueError("Only 'row' and 'col' allowed as axes for ghost mask")

    return rolled_mask


def volume_ghostiness(volume, phantom_mask=None, phantom_tight_mask=None, pe_axis='col'):
    """
    Return four ghost statistics for a given volume.

    Stats are phantom mean, ghost mean, bright ghost mean and snr.

    TODO: check, SNR looks dubious - unclear whether it is needed at all

    Parameters
    ----------
    volume: Numpy rank-3 image volume (at single timepoint)
    phantom_mask: Optional phantom mask
    phantom_tight_mask: Optional eroded phantom mask
    pe_axis: The phase encoding direction {'col', 'row'}

    Returns
    -------
    Tuple of statistics

    """
    nz, ny, nx = volume.shape

    # Phantom, ghost masks
    if phantom_mask is None:
        phantom_mask = np.empty_like(volume, dtype=bool)
        for z in range(nz):
            phantom_mask[z] = phantom_mask_2d(volume[z, :, :], dilate=True)

    if phantom_tight_mask is None:
        phantom_tight_mask = np.empty_like(volume, dtype=bool)
        for z in range(nz):
            phantom_tight_mask[z] = phantom_mask_2d(volume[z, :, :], erode=True)

    # Ghost mask is just generous phantom mask rolled along the phase encoding direction
    gh_mask = ghost_mask(phantom_mask, pe_axis)

    # Masks for phantom only, ghost only and noise background only
    p_only_mask =  phantom_mask & ~gh_mask
    g_only_mask = ~phantom_mask &  gh_mask
    n_only_mask = ~phantom_mask & ~gh_mask

    # Trim the phantom only mask back to an eroded version of phantom foregound
    p_only_mask &= phantom_tight_mask

    # Generate numpy masked arrays from volume and masks and use them to get stats
    # NB take complements as masked means ignore in numpy masked arrays
    p_only_marray = np.ma.array(volume, mask=~p_only_mask)
    g_only_marray = np.ma.array(volume, mask=~g_only_mask)
    n_only_marray = np.ma.array(volume, mask=~n_only_mask)

    # Calculate some useful stats
    pmean = p_only_marray.mean()
    nmean = n_only_marray.mean()
    nstd = n_only_marray.std()
    snr = nmean / nstd
    gmean = g_only_marray.mean()

    # Average of top decile of ghost pixels
    # This is the mean of the 'bright ghosts' according to the fBIRN protocol
    voxel_list = sorted(g_only_marray.compressed(), reverse=True)
    bright_gmean = np.mean(voxel_list[:len(voxel_list) // 10])

    # Return tuple of statistics
    return pmean, gmean, bright_gmean, snr


def ghostiness_trends(timeseries, pe_axis='col', fixed_mask=False):
    """
    Return four ghosting statistical trends as function of timepoint.

    Parameters
    ----------
    timeseries: Numpy rank-4 image volume time series
    pe_axis: The phase encoding direction {'col', 'row'}
    fixed_mask: Use a single phantom mask for all time_points
    Returns
    -------
    Tuple of curves

    """
    assert timeseries.ndim == 4
    nt, nz, ny, nx = timeseries.shape
    middle_volume = timeseries[nt // 2]

    if fixed_mask:
        # Phantom mask
        phantom_mask = np.empty_like(middle_volume, dtype=bool)
        for z in range(nz):
            phantom_mask[z] = phantom_mask_2d(middle_volume[z, :, :], dilate=True)

        phantom_tight_mask = np.empty_like(middle_volume, dtype=bool)
        for z in range(nz):
            phantom_tight_mask[z] = phantom_mask_2d(middle_volume[z, :, :], erode=True)
    else:
        phantom_mask = phantom_tight_mask = None

    statistics = zip(*[volume_ghostiness(vol, phantom_mask, phantom_tight_mask, pe_axis) for vol in timeseries])
    return tuple(np.asarray(statistic) for statistic in statistics)


# Analysis III
# TODO: duplicate the preprocessing done in fBIRN for fwhm:
# 3dvolreg, '-1Dfile':-
# 3dDetrend, '-polort', '2' -> data series (is this pixel by pixel fit?- yes 2nd order legendre poly)
# 3dTstat, '-mean' | 3dAutomask -> mask
# detrend over each pixel will be very slow - any way to vectorise or do we need cython?
# have a look at 3dDetrend code see if it is usable
#
# first generate a mask and only do detrending on non masked values
# probably then want to shrink the mask before doing variance normalization
# and fwhm calculation.
# can we get away without registration? movement looks to be sub pixel anyway...
# We get persistent bad values along the z axis - can't see why
# detrending, normalizing variance, changing roi don't seem to help
#
#

def phantom_mask_3d(volume, filter_size=2, dilate=False, erode=False, disk_size=1):
    """
    Generate a reduced 3D mask of the phantom using an Otsu Threshold.

    Parameters
    ----------
    image: Numpy rank-3 image array (nz, ny ,nx)

    Returns
    -------
    Numpy boolean mask array of same dimensions

    """
    # Reshape volume as an image strip so we can use the 2D routine
    nz, ny, nx = volume.shape
    image_strip = np.reshape(volume, (nz * ny, nx))
    mask_strip = phantom_mask_2d(
        image_strip, filter_size=filter_size,
        dilate=dilate, erode=erode, disk_size=disk_size
    )
    return np.reshape(mask_strip, (nz, ny, nx))


def smoothness_along_axis(volume, axis, delta):
    """
    Return the image smoothness along the given axis.

    Uses the method described in:
        Jenkinson, FMRIB Tech Rep TR00MJ3
        Fornan et al, MRM 33:636-647, 1995
    and in AFNI routine 3dFWHM.
    Expects detrending etc to have been performed already.
    Accepts masked arrays as imputs and only uses pixels outside the mask.

    Parameters
    ----------
    volume: Numpy rank-3 image array (nz,ny,nx). May be masked array.
    axis: Axis along which to take differences (z=0, y=1, x= 2)
    delta: Size of pixel in direction of differences.

    Returns
    -------
    Standard deviation of equivalent 1D Gaussian filter

    """
    assert volume.ndim == 3
    assert axis in [0, 1, 2]
    assert delta > 0

    # as per Jenkinson
    # Should handle masked arrays ok. (diff shrinks array and mask by one)
    V0 = np.var(volume, dtype=np.float64)
    if V0 == 0:
        print('V0=', V0)
        return 0

    V1 = np.var(np.diff(volume, axis=axis), dtype=np.float64)

    # as per Afni routine 3dFWHM
    arg = 1 - V1/(2*V0)

    return (
        sqrt(-1 / (4 * log(arg))) * delta
        if (arg > 0 and V1 > 0)
        else -1
    )


def fwhm_smoothness_xyz(timeseries, dimensions):
    """
    Return the FWHM of the image smoothness along each of 3 axes.

    As a function of time point. Does not normalize variance
    on a per pixel basis as indicated as optional in Jenkinson.
    Expects detrending etc to have been performed already.
    Accepts masked arrays as inputs and only uses pixels *outside*
    the masked regions.

    Parameters
    ----------
    timeseries: Numpy rank-4 time series array (nt,nz,ny,nx)
    dimensions: Voxel dimensions along each axis (dx,dy,dz) (NB order!)

    Returns
    -------
    FWHM of equivalent Gaussian in each direction as vectors of length nt.


    """
    dx, dy, dz = dimensions
    sigma2fwhm = sqrt(8*log(2))
    fwhm_x = np.array([
        sigma2fwhm * smoothness_along_axis(vol, axis=2, delta=dx)
        for vol in timeseries
    ])
    fwhm_y = np.array([
        sigma2fwhm * smoothness_along_axis(vol, axis=1, delta=dy)
        for vol in timeseries
    ])
    fwhm_z = np.array([
        sigma2fwhm * smoothness_along_axis(vol, axis=0, delta=dz)
        for vol in timeseries
    ])

    return fwhm_x, fwhm_y, fwhm_z


def fwhm_smoothness_xyz_preprocessed(timeseries, dimensions):
    """
    Whole pipeline for fwhm calc.

    Does masking to get phantom only, per pixel detrending and
    then variance normalisation.

    Parameters
    ----------
    timeseries: Numpy rank-4 time series array (nt,nz,ny,nx)
    dimensions: Voxel dimensions along each axis (dx,dy,dz) (NB order!)

    Returns
    -------
    FWHM of equivalent Gaussian in each direction as vectors of length nt.

    """
    nt, nz, ny, nx = timeseries.shape

    # preallocate
    detrended_ts = np.zeros(timeseries.shape)
    mask = phantom_mask_3d(np.sum(timeseries, axis=0), erode=True)

    # voxel-wise detrending and variance normalization
    # TODO: is there any way we can avoid this loop?
    for z in range(nz):
        for y in range(ny):
            for x in range(nx):
                if mask[z, y, x] and np.sum(np.abs(np.diff(timeseries[:, z, y, x]))) > 0:
                    detrended_ts[:, z, y, x] = detrend_quadratic(timeseries[:, z, y, x])
                    detrended_ts[:, z, y, x] /= np.std(detrended_ts[:, z, y, x])
    # nb mask in masked array is for elements *not* to include
    masked_detrended_ts = np.ma.array(
        detrended_ts,
        mask=np.tile(np.logical_not(mask), (nt, 1, 1, 1))
    )
    return fwhm_smoothness_xyz(masked_detrended_ts, dimensions)
