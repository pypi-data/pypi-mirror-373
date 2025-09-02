# -*- coding: utf-8 -*-
"""
    tools.py: helper routines for qa images
"""

from itertools import groupby
from warnings import warn
from math import sqrt, ceil

import numpy as np
from numpy import ma

from pydicom.dataset import Dataset

from scipy.ndimage import center_of_mass
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy import stats
from scipy.interpolate import UnivariateSpline
from scipy.optimize import curve_fit, least_squares

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from mriqa.phantoms import phantom_mask_2d, find_phantom
from mriqa.dcmio import (
    coil_elements, number_of_frames, is_multiframe, is_enhancedmr,
    series_number, instance_number, acquisition_number, manufacturer,
    slice_location, rx_coil_name, rx_coil_id, pix_spacing_yx
)


def all_ims(dobjs):
    """
    All images in list of dicom objects as numpy array.

    The array will have shape (nimages, ny, nx).
    If first object is a multiframe return all the frames instead
    (and ignore any following objects)

    Parameters
    ----------
    dobjs : list of dicom objects

    Returns
    -------
    Numpy array from all the objects or all the frames if a multiframe

    """
    if isinstance(dobjs, Dataset):
        dobjs = [dobjs]
    if is_multiframe(dobjs[0]):
        images = dobjs[0].pixel_array
    else:
        images = np.asarray([d.pixel_array for d in dobjs])
    return images & (2**dobjs[0].BitsStored - 1)


def single_im(dobj):
    """
    Single image as numpy array.

    Parameters
    ----------
    dobj : dicom object

    Returns
    -------
    Numpy array directly from object or from first frame if multiframe

    """
    return all_ims(dobj)[0]


def im_pair(dobja, dobjb=None):
    """
    Pair of images as numpy array based on two dicom images or a multiframe.

    Parameters
    ----------
    dobja : first dicom object
    dobjb : optional second dicom object

    Returns
    -------
    Two numpy arrays from two objects or from first two frames if multiframe

    """
    if dobjb is None:
        images = all_ims([dobja])
    else:
        images = all_ims([dobja, dobjb])
    if len(images) < 2:
        raise ValueError('Two dicom objects or a dicom multiframe required for im_pair()')

    imagea, imageb = images[:2]
    return imagea, imageb


def mean_im(dobja, dobjb=None):
    """
    Mean image of two dicom images (or multiframe).

    Falls back to just a single image of only one given

    Parameters
    ----------
    dobja : first dicom object
    dobjb : optional second dicom object

    Returns
    -------
    Average of dicom image data as numpy array

    """
    try:
        imagea, imageb = im_pair(dobja, dobjb)
        return (imagea + imageb).astype(np.float64) / 2
    except ValueError:
        return single_im(dobja)


def diff_im(dobja, dobjb=None):
    """
    Difference of two dicom images (or multiframe).

    Parameters
    ----------
    dobja : first dicom object
    dobjb : optional second dicom object

    Returns
    -------
    Difference of dicom image data as numpy array

    """
    imagea, imageb = im_pair(dobja, dobjb)
    return imagea.astype(np.float64) - imageb.astype(np.float64)


def image_snr_map(imagea, imageb, global_noise=False, noise_mask=None):
    """
    SNR map based two numpy arrays.

    Noise is estimate from an roi in the difference image.
    This may be either passed in explicitly, taken from the image backgound or from the phantom foreground.

    Parameters
    ----------
    imagea : first image
    imageb : second image
    global_noise: use stddev of diff image as single noise figure
    noise_mask: explicit mask to use for noise

    Returns
    -------
    SNR map of dicom image data as masked numpy array (signal image normalised to noise estimate)

    """
    imagea, imageb = imagea.astype(np.float64), imageb.astype(np.float64)
    mean_image, diff_image = (imagea + imageb) / 2, imagea - imageb
    mask_foreground = phantom_mask_2d(mean_image, mode='Erode')
    if noise_mask is not None:
        mask_background = noise_mask
    elif global_noise:
        mask_background = ~phantom_mask_2d(mean_image, mode='Dilate')
    else:
        mask_background = mask_foreground

    image_foreground = ma.masked_where(~mask_foreground, mean_image)
    noise_level = ma.masked_where(~mask_background, diff_image).std()
    return np.sqrt(2) * image_foreground / noise_level


def snr_map(dobja, dobjb=None, frame=None, global_noise=False, noise_mask=None):
    """
    SNR map based two dicom images (or multiframe).

    Noise is estimate from an roi in the difference image.
    This may be either passed in explicitly, taken from the image backgound or from the phantom foreground.

    Parameters
    ----------
    dobja : first dicom object
    dobjb : optional second dicom object
    frame : optional frame for case of two multiframes.
    global_noise: use stddev of diff image as single noise figure
    noise_mask: explicit mask to use for noise

    Returns
    -------
    SNR map of dicom image data as masked numpy array (signal image normalised to noise estimate)

    """
    if is_multiframe(dobja) and number_of_frames(dobja) >= 2:
        imagea, imageb = all_images_from_dicom(dobja)[:2]
    elif dobjb is not None:
        imagea, imageb = image_from_dicom(dobja, frame), image_from_dicom(dobjb, frame)
    else:
        raise ValueError('Require either two dicom objects or a multiframe')
    return image_snr_map(imagea, imageb, global_noise, noise_mask)


def image_uniformity_ipem80(image):
    """
    Uniformity ratios (horizontal and vertical) as determined from two images of a spherical phantom.

    Proportion of profiles through the phantom that remain within 10% of the value at the centre.

    See IPEM report 80 p

    Parameters
    ----------
    image : rank 2 ndarray

    Returns
    -------
    Tuple: (horiz profile, horiz percent uniformity, vert profile, vert percent uniformity)

    """
    # Location of the phantom centre
    x, y = center_of_mass(image)
    x, y = int(round(x)), int(round(y))

    # Profiles through the centre
    profile_x = image[y-3:y+4].mean(axis=0)
    profile_y = image[:, x-3:x+4].mean(axis=1)

    # Modal values in 10x10 ROI at the centre of phantom
    modal_val = stats.mode(image[y-4:y+5, x-4:x+5], axis=None)[0]

    # The proportion of the X profile with 10% of the modal value
    near_mode_x = list((0.9 * modal_val < profile_x) & (profile_x < 1.1 * modal_val))
    in_phantom_x = list(0.25 * modal_val < profile_x)

    # Longest uniform run in the profile as a proportion of its total width within the phantom
    run_near_mode_x = np.max([np.sum(list(g)) for b, g in groupby(near_mode_x) if b])
    run_in_phantom_x = np.max([np.sum(list(g)) for b, g in groupby(in_phantom_x) if b])

    percent_uniformity_x = 100 * run_near_mode_x / run_in_phantom_x

    # The proportion of the Y profile with 10% of the modal value
    near_mode_y = list((0.9 * modal_val < profile_y) & (profile_y < 1.1 * modal_val))
    in_phantom_y = list(0.25 * modal_val < profile_y)

    # Longest uniform run in the profile as a proportion of its total width within the phantom
    run_near_mode_y = np.max([np.sum(list(g)) for b, g in groupby(near_mode_y) if b])
    run_in_phantom_y = np.max([np.sum(list(g)) for b, g in groupby(in_phantom_y) if b])

    percent_uniformity_y = 100 * run_near_mode_y / run_in_phantom_y

    return profile_x, percent_uniformity_x, profile_y, percent_uniformity_y


def uniformity_ipem80(dobja, dobjb=None):
    """
    Uniformity ratios (horizontal and vertical) as determined from two images of a spherical phantom.

    Proportion of profiles through the phantom that remain within 10% of the value at the centre.

    See IPEM report 80 p

    Parameters
    ----------
    dobja : first dicom object
    dobjb : optional second dicom object

    Returns
    -------
    Tuple: (horiz profile, horiz percent uniformity, vert profile, vert percent uniformity)

    """
    try:
        # pair of images
        imagea, imageb = im_pair(dobja, dobjb)
    except ValueError:
        # accept single image
        imagea, imageb = im_pair(dobja, dobja)

    # Work with mean of images
    image = (imagea + imageb) / 2
    return image_uniformity_ipem80(image)


def image_uniformity_nema(image, centre_x, centre_y, radius, sigma=1.5):
    """
    NEMA NAAD based uniformity as determined from image of a spherical phantom.

    Parameters
    ----------
    image : numpy array
    centre_x, centre_y, radius: float
        expected centre ansd radius of phantom in image
    sigma : float
        width of Gaussian pre-smoothing

    Returns
    -------
    float: percent uniformity

    """
    # Smooth with Gaussian mask (NEMA has [121;242;121])
    image_smoothed = gaussian_filter(image.astype(float), sigma=sigma)

    # Select a 'MRIO' a central region of 75% by area
    nrows, ncols = image.shape
    dists = np.sqrt(
        (np.arange(nrows)[:, np.newaxis] - centre_y) ** 2 +
        (np.arange(ncols)[np.newaxis, :] - centre_x) ** 2
    )
    mroi_mask = dists < radius * np.sqrt(0.75)
    image_smoothed = np.ma.masked_where(~mroi_mask, image_smoothed)

    return 100 * (1 - naad(image_smoothed))


def uniformity_nema(dobja, dobjb=None, sigma=1.5):
    """
    NEMA NAAD based uniformity as determined from image of a spherical phantom.

    Parameters
    ----------
    dobja : dicom object
    dobjb : Opt[dicom object]
    sigma : float
        width of Gaussian pre-smoothing

    Returns
    -------
    float: percent uniformity

    """
    image = mean_im(dobja, dobjb)
    centre_x, centre_y, radius = find_phantom(image)
    return image_uniformity_nema(image, centre_x, centre_y, radius, sigma)


def _mosaic_single(dobjs):
    images = all_ims(dobjs)
    labels = [
        r'Series %d, Image %d' % (d.SeriesNumber, d.InstanceNumber) for d in dobjs
    ]
    return images, labels


def show_mosaic_single(dobjs, cmap=None, title=None):
    """
    Display a list of dicom images as a mosaic.

    Parameters
    ----------
    dobjs : sequence of dicom objects
        sequence of dicom objects to display
    cmap : matplotlib colour map
        optional colour map
    title : str
        plot title
    """
    images, labels = _mosaic_single(dobjs)
    nimages = len(images)
    ny = int(round(sqrt(nimages)))
    nx = int(ceil(nimages / ny))
    if nx == 0 or ny == 0:
        nx = ny = 1
    fig, axs = plt.subplots(ny, nx, figsize=(4*nx, 4*ny))
    if nx == ny == 1:
        axs = [axs]
    else:
        axs = axs.ravel()
    naxs = len(axs)

    for i, (ax, image) in enumerate(zip(axs, images)):
        ax.imshow(image, cmap=cmap)
        ax.axis('image')
        ax.axis('off')
        ax.set_title(labels[i])

    for i in range(nimages, naxs):
        axs[i].imshow(np.zeros_like(images[0]), cmap=cmap)
        axs[i].axis('image')
        axs[i].axis('off')

    # Title
    if title is not None:
        fig.suptitle(title, fontsize=16)


def _mosaic(dobjs, dobjsb, op='mean'):
    if isinstance(dobjs, Dataset):
        dobjs = [dobjs]
    if isinstance(dobjsb, Dataset):
        dobjsb = [dobjsb]

    images = all_ims(dobjs)

    if dobjsb is not None:
        imagesb = all_ims(dobjsb)
        if len(imagesb) != len(images):
            raise ValueError('Two image series should be the same length')
        if op == 'mean':
            images = (images + imagesb) / 2
        elif op == 'diff':
            # nb will be signed
            images = images - imagesb

    try:
        # multi-element display if all images single element
        # non-multiframe
        elements = [coil_elements(d) for d in dobjs]
        nelements = list(map(len, elements))
        if np.all(np.array(nelements) == 1):
            elements = [e[0] for e in elements]
            have_elements = True
        else:
            have_elements = False
    except (IndexError, KeyError):
        have_elements = False

    # what about multiframes (either Philips or Siemens)?
    if have_elements:
        labels = [
            r'Series %d, Element %d' % (series_number(dobjs[0]), element) for element in elements
        ]
    elif is_multiframe(dobjs[0]):
        nframes = number_of_frames(dobjs[0])
        labels = [
            r'Series %d, Image %d, Frame %d' % (
                series_number(dobjs[i // nframes]),
                instance_number(dobjs[i // nframes]),
                i % nframes + 1
            )
            for i in range(len(images))
        ]
    else:
        labels = [
            r'Series %d, Image %d' % (series_number(d), instance_number(d)) for d in dobjs
        ]

    return images, labels


def show_mosaic(dobjs, dobjsb=None, op='mean', cmap=None, signed=False, title=None):
    """
    Display a list of dicom images or multiframe as a mosaic.

    Parameters
    ----------
    dobjs : sequence or dicom Dataset
        a list of dicom objects or single multiframe object
    dobjsb : sequence or dicom Dataset
        second list of dicom objects to average or difference with the first
    op : str
        operation to perform between the two series
    cmap : matpltolib colour map
        optional colour map
    signed : bool
        set colour scale symmetrically about zero for a signed image
    title : str
        plot title
    """
    images, labels = _mosaic(dobjs, dobjsb, op)
    assert len(images) == len(labels)
    nimages = len(images)
    if dobjsb is not None and op == 'diff':
        signed = True

    ny = int(round(sqrt(nimages)))
    nx = int(ceil(nimages / ny))
    if nx == 0 or ny == 0:
        nx = ny = 1

    vmin = np.min(images)
    vmax = np.max(images)

    fig, axs = plt.subplots(ny, nx, figsize=(4*nx, 4*ny))
    if nx == ny == 1:
        axs = [axs]
    else:
        axs = axs.ravel()
    naxs = len(axs)

    if cmap is None:
        cmap = 'coolwarm' if signed else 'gray'

    for i, (ax, image) in enumerate(zip(axs, images)):
        ax.imshow(image, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.axis('image')
        ax.axis('off')
        ax.set_title(labels[i])

    for i in range(nimages, naxs):
        axs[i].imshow(np.zeros_like(images[0]), cmap=cmap, vmin=vmin, vmax=vmax)
        axs[i].axis('image')
        axs[i].axis('off')

    # Title
    if title is not None:
        fig.suptitle(title, fontsize=16)


def _basic_montage(dobjsa, dobjsb, op):
    """
    Construct a list of images to use in a montage image from lists of dicom objects.

    Parameters
    ----------
    dobjs : sequence or dicom Dataset
        a list of dicom objects or single multiframe object
    dobjsb : sequence or dicom Dataset
        second list of dicom objects to average or difference with the first
    op : str
        operation to perform between the two series

    """
    signed = False
    # individual images
    imagesa = all_ims(dobjsa)

    if dobjsb is not None:
        imagesb = all_ims(dobjsb)

        if op == 'mean':
            images = [(a+b)/2 for (a, b) in zip(imagesa, imagesb)]
            dobjs = dobjsa
        elif op == 'diff':
            images = [
                b.astype(float) - a.astype(float)
                for (a, b) in zip(imagesa, imagesb)
            ]
            dobjs = dobjsa
            signed = True
        else:
            # just concatenate, rather than reduce
            images = imagesa + imagesb
            dobjs = dobjsa + dobjsb
    else:
        images = imagesa
        dobjs = dobjsa

    # Values of indices
    slice_positions = [int(slice_location(dobj)) for dobj in dobjs]

    # Use Acquistion Number or Series Number, whichever varies most
    series_numbers = [series_number(dobj) for dobj in dobjs]
    acquisition_numbers = [acquisition_number(dobj) for dobj in dobjs]
    useacq = len(set(acquisition_numbers)) > len(set(series_numbers))
    temporal_indices = acquisition_numbers if useacq else series_numbers

    try:
        # multi-element display if all images single element
        elements = [coil_elements(d) for d in dobjs]
        nelements_used = list(map(len, elements))
        if np.all(np.array(nelements_used) == 1):
            elements = [e[0] for e in elements]
        else:
            elements = [1]
        elements = [e + 1 for e in elements]
    except (IndexError, KeyError):
        elements = [1]
    return images, signed, series_numbers, slice_positions, temporal_indices, elements


def _philips_multiframe_montage(dobj, op):
    """
    Construct a list of images to use in a montage image from a philips multiframe.

    Parameters
    ----------
    dobj : dicom Dataset
        an enhanced dicom multiframe
    op : str
        operation to perform between the two series

    """
    if op and op not in ('mean', 'diff'):
        raise ValueError('Only operations of mean and difference supported')

    images = all_ims(dobj)
    signed = False

    pffgs = dobj.PerFrameFunctionalGroupsSequence
    nframes = len(pffgs)

    FrameContentSequence = (0x0020, 0x9111)
    StackID = (0x0020, 0x9056)
    InStackPositionNumber = (0x0020, 0x9057)
    TemporalPositionIndex = (0x0020, 0x9128)

    PhilipsMRImagingDD005 = (0x2005, 0x140f)
    ChemicalShift = (0x2001, 0x1001)

    # Assume a specific multiframe layout:
    # volume, slice, and possibly either time (dynamic) and/or chemical shift (for coil element)
    dis = dobj.DimensionIndexSequence

    # Lists of matches for each supported dimension type at index positions
    stacks_indices = [
        di.FunctionalGroupPointer == FrameContentSequence and di.DimensionIndexPointer == StackID
        for di in dis
    ]
    slices_indices = [
        di.FunctionalGroupPointer == FrameContentSequence and di.DimensionIndexPointer == InStackPositionNumber
        for di in dis
    ]
    times_indices = [
        di.FunctionalGroupPointer == FrameContentSequence and di.DimensionIndexPointer == TemporalPositionIndex
        for di in dis
    ]
    coils_indices = [
        di.FunctionalGroupPointer == PhilipsMRImagingDD005 and di.DimensionIndexPointer == ChemicalShift
        for di in dis
    ]

    # Whether each supported dimension is indexed in the multiframne
    have_stacks = any(stacks_indices)
    have_slices = any(slices_indices)
    have_times = any(times_indices)
    have_coils = any(coils_indices)

    # Check we have accounted for all the dimensions in the multiframe
    if sum([have_stacks, have_slices, have_times, have_coils]) != len(dis):
        raise ValueError('Philips Multiframe with unrecognised dimension')

    # Index of each dimension in multiframe
    stacks_axis = stacks_indices.index(True) if have_stacks else -1
    times_axis = times_indices.index(True) if have_times else -1
    coils_axis = coils_indices.index(True) if have_coils else -1

    # Use the dimension indices here - should be unique
    nstacks = len({
        pffg.FrameContentSequence[0].DimensionIndexValues[stacks_axis]
        for pffg in pffgs
    }) if have_stacks else 1
    if nstacks != 1:
        raise ValueError('Philips Multiframe with more than one stack currently unsupported')

    ntimes = len({
        pffg.FrameContentSequence[0].DimensionIndexValues[times_axis]
        for pffg in pffgs
    }) if have_times else 1

    ncoils = len({
        pffg.FrameContentSequence[0].DimensionIndexValues[coils_axis]
        for pffg in pffgs
    }) if have_coils else 1

    # Check scale factors all the same, rescale if not
    transforms = [
        (
            float(pffg.PixelValueTransformationSequence[0].RescaleSlope),
            float(pffg.PixelValueTransformationSequence[0].RescaleIntercept)
        )
        for pffg in pffgs
    ]
    if len(set(transforms)) != 1:
        warn('_philips_multiframe_montage: applying Pixel value transformations as not consistent across frames')
        for image, transform in zip(images, transforms):
            image[:] = image * transform[0] + transform[1]


    # Reshape numpy array to match multiframe layout
    ny, nx = images.shape[-2:]
    shape = tuple([
        len({pffg.FrameContentSequence[0].DimensionIndexValues[i] for pffg in pffgs})
        for i, _ in enumerate(dis)
    ]) + (ny, nx)
    images = images.reshape(shape)

    # Perform reduction along *temporal* or *coils* index axis if specified
    # removing superflous frames from list
    if op and ntimes > 1:
        if op == 'mean':
            images = images.mean(axis=times_axis)
        elif op == 'diff':
            images = np.diff(images, axis=times_axis).mean(axis=times_axis)
            signed = True
        min_time_index = min(pffg.FrameContentSequence[0].DimensionIndexValues[times_axis] for pffg in pffgs)
        pffgs = [
            pffg for pffg in pffgs
            if pffg.FrameContentSequence[0].DimensionIndexValues[times_axis] == min_time_index
        ]
    elif op and ncoils > 1:
        if op == 'mean':
            images = images.mean(axis=coils_axis)
        elif op == 'diff':
            images = np.diff(images, axis=coils_axis).mean(axis=coils_axis)
            signed = True
        min_coil_index = min(pffg.FrameContentSequence[0].DimensionIndexValues[coils_axis] for pffg in pffgs)
        pffgs = [
            pffg for pffg in pffgs
            if pffg.FrameContentSequence[0].DimensionIndexValues[coils_axis] == min_coil_index
        ]

    # Values of indices (do this after any reduction so we get labeols for retained frames only)
    series_numbers = [series_number(dobj)] * nframes

    slice_positions = [
        int(pffg.FrameContentSequence[0].InStackPositionNumber)
        for pffg in pffgs
    ] if have_slices else [0.0] * nframes

    temporal_indices = [
        int(pffg.FrameContentSequence[0].TemporalPositionIndex)
        for pffg in pffgs
    ] if have_times else [1] * nframes

    coil_elements = [
        int(pffg[PhilipsMRImagingDD005].value[0][ChemicalShift].value)
        for pffg in pffgs
    ] if have_coils else [1] * nframes

    images = images.reshape(-1, ny, nx)
    return images, signed, series_numbers, slice_positions, temporal_indices, coil_elements


# TODO: handle case of hybrid multiframes - ie multiple single coil element multiple frames
def _siemens_multiframe_montage(dobj, op):
    """
    Construct a list of images to use in a montage image from a Siemens multiframe.

    Parameters
    ----------
    dobj : dicom Dataset
        an enhanced dicom multiframe
    op : str
        operation to perform between the two series

    """
    images = all_ims(dobj)
    signed = False
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
    assert nacquisitions_in_multiframe in (1, 2)

    # TODO: Assume there is only one coil element for now
    # TODO: we'll need a different routine to handle the hybrid case
    ncoils_in_multiframe = 1

    # Perform reduction along temporal index axis if specified
    if nacquisitions_in_multiframe == 2 and op in ['mean', 'diff']:
        nf, ny, nx = images.shape
        ns, nc = nslices_in_multiframe, ncoils_in_multiframe
        images_r = images.reshape(1, ns, 2, nc, ny, nx)
        # imagesa, imagesb = images_r[:, :, 0], images_r[:, :, 1]
        if op == 'mean':
            images = images_r.mean(axis=2).reshape(ns*nc, ny, nx)
        elif op == 'diff':
            # nb now must be signed
            images = np.diff(
                images_r.astype(float), axis=2
            ).mean(axis=2).reshape(ns*nc, ny, nx)
            signed = True
        # Now need same index manipulation on func groups sequence
        pffgs_r = np.array(pffgs).reshape((1, ns, 2, nc))
        pffgs = list(pffgs_r[:, :, 0, :].reshape(-1))

    # Values of indices
    slice_positions = [
        int(pffg.FrameContentSequence[0].InStackPositionNumber)
        for pffg in pffgs
    ]

    temporal_indices = [
        int(pffg.FrameContentSequence[0].TemporalPositionIndex)
        for pffg in pffgs
    ]

    series_numbers = [series_number(dobj)] * len(pffgs)

    return images, signed, series_numbers, slice_positions, temporal_indices


def _montage(dobjsa, dobjsb=None, op='mean', signed=False):
    """
    Construct a montage (mosaic) image from a list of dicom images or a multiframe.

    Empty cells in the montage are set to nan

    Parameters
    ----------
    dobjs : sequence or dicom Dataset
        a list of dicom objects or single multiframe object
    dobjsb : sequence or dicom Dataset
        second list of dicom objects to average or difference with the first
    op : str
        operation to perform between the two series
    signed : bool
        whether to assume image is signed

    """
    if isinstance(dobjsa, Dataset):
        dobjsa = [dobjsa]

    if isinstance(dobjsb, Dataset):
        dobjsb = [dobjsb]

    if manufacturer(dobjsa[0]) == 'Philips' and is_enhancedmr(dobjsa[0]) and is_multiframe(dobjsa[0]):
        images, signed_result, series_numbers, slice_positions, temporal_indices, elements = _philips_multiframe_montage(dobjsa[0], op)
    elif manufacturer(dobjsa[0]) == 'Siemens' and is_enhancedmr(dobjsa[0]) and is_multiframe(dobjsa[0]):
        # TODO: handle case of hybrid multifreams - ie multiple single coil element multiple frames
        images, signed_result, series_numbers, slice_positions, temporal_indices = _siemens_multiframe_montage(dobjsa[0], op)
        elements = [1]
    elif not is_multiframe(dobjsa[0]):
        images, signed_result, series_numbers, slice_positions, temporal_indices, elements = _basic_montage(dobjsa, dobjsb, op)
    else:
        raise ValueError("unsupported multiframe type")

    signed = signed or signed_result
    nslices_in_mosaic = len(set(slice_positions))
    ncoils_in_mosaic = len(set(elements))

    # Montage matrix size
    nimages = len(images)
    nrows = int(round(np.sqrt(nimages)))
    ncols = int(np.ceil(nimages / nrows))
    if ncols == 0 or nrows == 0:
        nrows = ncols = 1

    # Construct montage image
    ny, nx = images[0].shape
    montage = np.full((ny*nrows, nx*ncols), np.nan)
    for i, image in enumerate(images):
        x, y = (i % ncols) * nx, (i // ncols) * ny
        montage[y:y+ny, x:x+nx] = image

    # Labels
    legends = []
    for i in range(nimages):
        # Text position
        legend = 'S%d:%d' % (
            series_numbers[i], temporal_indices[i]
        )
        if nslices_in_mosaic > 1:
            legend = '/'.join([legend, 'L%d' % slice_positions[i]])
        if ncoils_in_mosaic > 1:
            legend = '/'.join([legend, 'E%d' % elements[i]])
        legends.append(legend)

    return montage, ncols, nrows, legends, signed_result


def show_montage(dobjsa, dobjsb=None, op='mean', cmap=None,
                 signed=False, fill=True, title='Image Montage', figsize=(14, 14)):
    """
    Display a list of dicom images or multiframe as a montage (mosaic).

    Parameters
    ----------
    dobjs : sequence or dicom Dataset
        a list of dicom objects or single multiframe object
    dobjsb : sequence or dicom Dataset
        second list of dicom objects to average or difference with the first
    op : str
        operation to perform between the two series
    cmap : matplotlib colour map
        colour map to use for image
    signed : bool
        whether to assume image is signed
    fill : bool
        whether to fill undefined parts of montage with zeros
    title : str
        title for plot.
    figsize: (float, float)
        size for matplotlib figure


    """
    montage, ncols, nrows, legends, signed = _montage(dobjsa, dobjsb, op, signed)

    fig, ax = plt.subplots(1, 1, figsize=figsize)

    # Preferred colourmaps
    if cmap is None:
        cmap = 'coolwarm' if signed else 'gray'
    textcolour = 'black' if signed else 'white'

    # Centre colour range in signed
    vmin, vmax = np.nanmin(montage), np.nanmax(montage)
    if signed:
        vmax = max(abs(vmin), abs(vmax))
        vmin = -vmax

    # Fill in undefined region with zeros
    if fill:
        montage = np.nan_to_num(montage)

    # Display image
    mplim = ax.imshow(montage, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.axis('image')
    ax.axis('off')

    # Add labels
    nx, ny = montage.shape[1] // ncols, montage.shape[0] // nrows
    x_0, y_0 = nx // 16, ny // 12
    for i, legend in enumerate(legends):
        # Text position
        x, y = x_0 + (i % ncols) * nx, y_0 + (i // ncols) * ny
        ax.text(x, y, legend, color=textcolour)

    # Title
    ax.set_title(title, fontsize=16)

    # Colourbar clipped to height of image
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(mplim, cax=cax)

    return ax


def normalized_profile(profile):
    """
    Normalize profile by removing quadratic multiplicative bias.

    Assumes profile is dark against bright baseline.

    Parameters
    ----------
    profile : 1d profile

    Returns
    -------
    Positive going profile with baseline of zero.

    """
    plen = len(profile)
    x = list(range(plen//4)) + list(range(3*plen/4, plen))
    baseline = np.poly1d(np.polyfit(x, profile[x], 2))(list(range(plen)))
    return 1 - profile / baseline


def profile_params(profile):
    """
    Position and fwhm of profile.

    Assumes profile already normalized. Values in pixels if profile from image.

    Parameters
    ----------
    profile : 1d profile

    Returns
    -------
    Tuple: (position, full width half maximum)

    """
    plen = len(profile)
    spline = UnivariateSpline(plen, profile - np.amax(profile)/2, s=0)
    r1, r2 = spline.roots()  # find the roots
    assert r2 > r1
    fwhm = r2 - r1
    turning_points = spline.derivative().roots()
    location = [p for p in turning_points if r1 < p < r2][0]
    return location, fwhm


def peakdet(v, delta, x=None):
    """
    Detect peaks in signal.

    Converted from MATLAB script at http://billauer.co.il/peakdet.html

    Returns two arrays

    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.

    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.

    """
    maxtab = []
    mintab = []

    if x is None:
        x = np.arange(len(v))
    else:
        x = np.asarray(x)

    v = np.asarray(v)

    if v.ndim != 1 or x.shape != v.shape:
        raise ValueError('Inputs v and x must be vectors of the same length')

    if not np.isscalar(delta) or delta <= 0:
        raise ValueError('Input argument delta must be a positive scalar')

    mn, mx = np.Inf, -np.Inf
    mnpos, mxpos = np.NaN, np.NaN

    lookingformax = True

    for i, v_i in enumerate(v):
        if v_i > mx:
            mx = v_i
            mxpos = x[i]
        if v_i < mn:
            mn = v_i
            mnpos = x[i]

        if lookingformax:
            if v_i < mx - delta:
                maxtab.append((mxpos, mx))
                mn = v_i
                mnpos = x[i]
                lookingformax = False
        else:
            if v_i > mn + delta:
                mintab.append((mnpos, mn))
                mx = v_i
                mxpos = x[i]
                lookingformax = True

    return np.array(maxtab), np.array(mintab)


def _gaussian_fit(x, y):
    """
    Fit the location of a Gaussian to a single peak in a curve.

    Parameters
    ----------
    x, y: rank 1 np arrays

    Returns
    -------
    float: location of fitted maximum

    """
    def gaussian(x, ampl, centre, stdev):
        return ampl * np.exp(-(x - float(centre)) ** 2 / (2.0 * stdev ** 2 + np.finfo(float).eps))

    if len(x) < 3:
        raise RuntimeError("At least 3 points required for Gaussian fitting")

    ampl_0, centre_0, stddev_0 = np.max(y), (x[0] + x[-1])/2, (x[1] - x[0]) * 2
    initial = [ampl_0, centre_0, stddev_0]
    lower_bounds = [0.75 * ampl_0, centre_0 - 2.0, stddev_0 / 4]
    upper_bounds = [1.25 * ampl_0, centre_0 + 2.0, 2 * stddev_0]

    try:
        params, _ = curve_fit(gaussian, x, y, initial, xtol=0.01, bounds=(lower_bounds, upper_bounds))
    except RuntimeError as e:
        # print(window, index)
        warn("gaussian_fit: fitting error [%s] (trying a looser tolerance)" % e)
        params, _ = curve_fit(gaussian, x, y, initial, xtol=0.25, bounds=(lower_bounds, upper_bounds))
    return params[1]


def _refine_peak(row, index, window_half_width=8):
    """
    Refine a peak position in a profile previously determined with argmax.

    Parameters
    ----------
    row: rank 1 np array
        profile row
    index: int
        initial peak position

    window_half_width: Opt[int]
        number of either side of point to bracket

    Returns
    -------
    float: refined peak position

    """
    if not (window_half_width <= index < len(row) + window_half_width, index):
        warn('_refine_peak: peak too close to edge')
        return float(index)

    # Centre the window around the previously detected peak
    y = row[index-window_half_width:index+window_half_width]
    x = np.arange(len(y))

    # and fit a Gaussian
    try:
        return _gaussian_fit(x, y) + index - window_half_width
    except RuntimeError as e:
        warn("_refine_peak: %s" % e)
        return float(index)


def positive_gradient(r):
    """
    Gradient of profiles with sign flip of second half so gradient is positive at both ends.

    Assumes all profiles have a rising edge in the first half and a falling one in the second

    Parameters
    ----------
    r: rank 2 numpy array
        array of profiles arranged nprofiles, npoints

    Returns
    -------
    tuple: rank 2 array, rank 1 array, float
        array of profile derivatives arranged nprofiles, npoints

    """
    assert r.ndim == 2

    nprofiles, npoints = r.shape
    dr = np.gradient(r, axis=-1)

    # Derivatives with second (negative) edge flipped positive
    split = npoints // 2
    dr[:, split:] *= -1
    return dr


def radial_profiles(image, centre, radius, ntheta=45, npoints=512, margin=1.25, excluded_sector=0):
    """
    Sequence of radial profiles across diameter of phantom.

    Profiles pass through the given centre over a range of angles
    covering a total of 180 degrees.

    Image should consist of a single uniform circular phantom
    and should already be interpolated up by an appropriate factor
    to increase the resolution of the profiles.

    Parameters
    ----------
    image: rank 2 numpy array
        phantom image to generate profiles from
    centre: tuple of float
        coordinates of centre of phantom in pixels (x, y)
    radius: float
        radius in pixels of phantom in image
    ntheta: Opt[int]
        number of angles to take over 180 degrees
    npoints: Opt[int]
        number of points along profile
    margin: Opt[float]
        additional proportion of radius to include in profile
    excluded_sector: Opt[float]
        angle in degrees to excluded_sector around ends of interval for bubbles

    Returns
    -------
    tuple: rank 2 array, rank 1 array, float
        profiles, angles, spacing along profile in pixels

    """
    centre_x, centre_y = centre

    # Symmetrical range of profiles about origin
    R = radius * margin
    theta = np.linspace(-np.pi/2+np.radians(excluded_sector)/2, np.pi/2-np.radians(excluded_sector)/2, ntheta)
    xas, yas = R * np.cos(theta), R * np.sin(theta)
    xbs, ybs = -xas, -yas

    # then add in offset to actual centre
    xas += centre_x
    xbs += centre_x
    yas += centre_y
    ybs += centre_y

    r = []
    for xa, xb, ya, yb in zip(xas, xbs, yas, ybs):
        x = np.linspace(xa, xb, npoints)
        y = np.linspace(ya, yb, npoints)
        r.append(map_coordinates(image, np.vstack((y, x))))
    r = np.asarray(r)

    delta_r = 2 * R / npoints

    return r, theta, delta_r


def profile_edges(r):
    """
    Get position of phantom edges from radial profiles (pixels).

    Parameters
    ----------
    r: rank 2 numpy array
        stack of radial profiles

    Returns
    -------
    tuple of vectors
        positions of edges in pixels

    """
    # Assume the two edges are in 1st and 2nd halves of line
    split = r.shape[1] // 2

    # We start with just argmax and refine with a Gaussian peak fit
    x0_x1 = []
    for line in positive_gradient(r):
        edge_a = line[:split]
        edge_b = line[split:]
        x0 = _refine_peak(edge_a, np.argmax(edge_a))
        x1 = _refine_peak(edge_b, np.argmax(edge_b)) + split
        x0_x1.append((x0, x1))

    x0, x1 = np.array(x0_x1).T

    return x0, x1


def profile_diameters(r):
    """
    Get diameters of circular phantom from radial profiles (pixels).

    Parameters
    ----------
    r: rank 2 numpy array
        stack of radial profiles

    Returns
    -------
    vector of diameters in pixels

    """
    a, b = profile_edges(r)
    return b - a


def fit_diameters(diameters, angles):
    """
    Fit a sinusoidal function to the profile diameters.

    The profiles are given at a range of angles.
    These should lie with a semi circle ie in [-pi/2, pi/2]

    The fit is of a single component with period one, but with
    scale and phase to be determined. The purpose is get an estimate
    of the 'elliptical' distortion of the circular phantom.

    Uses a robust fit to exclude occasional outliers due to bubbles etc.

    Parameters
    ----------
    diameters: rank 1 numpy array
        vector of diameters in pixels
    angles: rank 1 numpy array
        vector of angles in radians

    Returns
    -------
    tuple: offset, a, b, fitted curve

    """
    assert np.all((0 < diameters) & (diameters < 1024))
    assert np.all((-np.pi/2 <= angles) & (angles <= np.pi/2))

    def sinfn(angles, offset, a, b):
        return offset + a * np.cos(2*angles) + b * np.sin(2*angles)

    def sinlossfn(params, angles, diameters):
        offset, a, b = params
        return sinfn(angles, offset, a, b) - diameters

    offset, a, b = least_squares(
        sinlossfn, args=(angles, diameters),
        x0=(diameters.mean(), 0, 0),
        loss='soft_l1'
    ).x
    fitted_diameters = sinfn(angles, offset, a, b)

    return offset, a, b, fitted_diameters


def edges_and_diameters(image, centre_x, centre_y, radius, ntheta=45, excluded_sector=0):
    """
    Circularity of phantom image.

    Non-circularity is taken as an indication of image distortion.
    The image should have been previously interpolated to higher resolution.
    Works exclusivly in image pixel coordinates so doesn't require pixel size.
    Returns edge positions and diameters as a function of angle in radians

    Parameters
    ----------
    image: numpy 2D array
        image to consider
    centre_x, centre_y, radius: float
        expected centre and radius of phantom in image
    excluded_sector: float
        angle in degrees to exclude around bubbles in phantom

    Returns
    -------
    tuple: theta, edge_a, edge_b, measured_diameters, fitted_diameters (in radians and pixels)

    """
    r, theta, delta_r = radial_profiles(
        image, centre=(centre_x, centre_y), radius=radius, ntheta=ntheta, excluded_sector=excluded_sector
    )
    edge_a, edge_b = profile_edges(r)
    diameters = profile_diameters(r)
    _, _, _, fitted_diameters = fit_diameters(diameters, theta)

    edge_a *= delta_r
    edge_b *= delta_r
    diameters *= delta_r
    fitted_diameters *= delta_r

    return theta, edge_a, edge_b, diameters, fitted_diameters


def naad(image):
    """
    Normalized Absolute Average Deviation.

    Parameters
    ----------
    image: numpy 2D array
        image to consider

    Returns
    -------
    float: Normalized Absolute Average Deviation

    """
    mad = abs(image - image.mean()).mean()
    return mad / image.mean()


def watermark():
    """
    Water mark with environmant info including versions of significant packages.

    Returns
    -------
    dict: information about environment

    """
    from platform import node, python_implementation, python_version, system, release
    from datetime import datetime, timezone
    from time import time
    from getpass import getuser

    iso_dt = datetime.fromtimestamp(
        int(time()),
        timezone.utc
    ).astimezone().isoformat()

    def package_versions(packages):
        versions = {}
        for package in packages:
            try:
                imported = __import__(package)
            except ImportError:
                versions[package] = 'not installed'
            else:
                versions[package] = imported.__version__
        return versions

    wmark = {
        'CalculationTime': iso_dt,
        'User': '%s/%s' % (node(), getuser()),
        'PythonVersion':  '%s %s' % (python_implementation(), python_version()),
        'Platform': '%s %s' % (system(), release())
    }
    wmark.update(
        package_versions(['mriqa', 'dcmextras', 'pydicom', 'scipy', 'numpy', 'skimage', 'matplotlib'])
    )

    return wmark


def add_phase_encode_mark(ax, dirn, colour='white'):
    """
    Add a symbol to indicate the phase encoding direction to existing image.

    Parameters
    ----------
    ax: matplotlib.axes.Axes
        image axes to plot symbol on
    dirn: str
        phase encoding direction 'ROW' or 'COL'

    """
    if dirn.startswith('R'):
        xytext = (0.15, 0.1)
        xy_a = (0.25, 0.1)
        xy_b = (0.05, 0.1)
    else:
        xytext = (0.1, 0.15)
        xy_a = (0.1, 0.25)
        xy_b = (0.1, 0.05)

    ax.annotate(
        r'$\varphi$',
        verticalalignment='center',
        horizontalalignment='center',
        xy=xy_a, xycoords='axes fraction',
        xytext=xytext, textcoords='axes fraction',
        color=colour,
        arrowprops={'color': colour, 'arrowstyle': '->'}
    )
    ax.annotate(
        r'$\varphi$',
        verticalalignment='center',
        horizontalalignment='center',
        xy=xy_b, xycoords='axes fraction',
        xytext=xytext, textcoords='axes fraction',
        color=colour,
        arrowprops={'color': colour, 'arrowstyle': '->'}
    )


def rx_coil_string(dobj, coil=None):
    """
    Best string representation of coil for plots with optional default.

    Parameters
    ----------
    dobj: dicom object

    coil : str
        override value

    Returns
    -------
    str: coil label

    """
    if coil is not None:
        return coil

    try:
        id_ = rx_coil_id(dobj).strip()
    except KeyError:
        id_ = ''
    try:
        name = rx_coil_name(dobj).strip()
    except KeyError:
        name = ''

    return id_ if id_ else name if name else 'RxCoil'


def image_from_dicom(dobj, frame=None, dtype=None):
    """Get image as numpy array from single frame or multiframe DICOM."""
    image = dobj.pixel_array & (2**dobj.BitsStored - 1)

    if is_multiframe(dobj):
        frame = frame if frame is not None else number_of_frames(dobj) // 2
        image = image[frame]

    return image.astype(dtype) if dtype is not None else image


def all_images_from_dicom(dobj, dtype=None):
    """Get images as nd numpy array from single frame or multiframe DICOM."""
    image = dobj.pixel_array & (2**dobj.BitsStored - 1)
    return image.astype(dtype) if dtype is not None else image


def pixel_size(dobj):
    """Get size of square pixels in mm."""
    # Pixels dimensions - square pixels only
    pix_dy, pix_dx = pix_spacing_yx(dobj)
    assert np.isclose(pix_dx, pix_dy)
    return pix_dx


def rectangular_roi_coords(pix_dims, rect, centre):
    """
    Get indices and offsets of a rectangle ROI.

    The rectangle is specified as (x, y, dx, dy) in mm.
    The ROI is shifted according to specified phantom centre (NB in pixels).
    The returned specification (x, y, dx, dy) is in (integer) pixels.
    TODO: do we need to do off by 0.5 fix?
    TODO: Cf convention in dicom/skimage/matplotlib)

    """
    centre_x, centre_y = centre
    (x, y), (dx, dy) = np.round((np.array(rect) / pix_dims)).astype('int')
    x += centre_x
    y += centre_y
    return x, y, dx, dy


def rectangular_roi(image, pix_dims, rect, centre):
    """
    Extract a rectangular region of interest from an image.

    The rectangle is specified as (x, y, dx, dy) in mm.
    The region of interest is shifted according to the specified
    phantom centre (NB in pixels). The returned ROI is a view
    on the original image array.
    """
    x, y, dx, dy = rectangular_roi_coords(pix_dims, rect, centre)
    return image[y:y+dy, x:x+dx]
