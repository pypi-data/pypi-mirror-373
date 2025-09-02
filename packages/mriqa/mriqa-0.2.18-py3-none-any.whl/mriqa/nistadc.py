#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""nistadc.py: NIST Diffusion phantom ADC Analysis."""

from typing import Optional, Tuple, Dict, Any, Sequence, List
from numpy.typing import ArrayLike, NDArray
from warnings import warn

import numpy as np
import xarray as xr

import pydicom as dcm

from scipy.optimize import curve_fit
from scipy.ndimage import binary_fill_holes, median_filter
from skimage.filters import threshold_otsu, sobel, laplace
from skimage.segmentation import watershed
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.morphology import (
    binary_erosion, binary_dilation,
    convex_hull_image, disk as mdisk
)
from skimage.draw import disk
from skimage.measure import label, regionprops

from . dcmio import (
    diffusion_bvalue, seq_name,
    slice_location, matrix_yx, pix_spacing_yx, approx_slice_orientation,
    software_versions, manufacturer, is_multiframe
)

from . mfxarray import mf_to_xa

RADIUS_GROW = 1.5
RADIUS_TRIM = 2.5  # in pixels: might want to do this in mm?


# Routines for extracting dwi multiframes and series to xarray arrays


def _isotropic_index(pffgs: dcm.Sequence, index_loc: int = 3) -> int:
    """
    Get the index value that corresponds to the (isotropic) trace images.

    Parameters
    ----------
    pffgs
        dicom per frame functional groups sequence
    index_loc
        the index position to consider

    Returns
    -------
    The index value that is used for isotropic (trace) images.

    """
    # TODO (RHD): Any way to do this without specifying the index position use?

    indices = set()
    for pffg in pffgs:
        diffn = pffg.MRDiffusionSequence[0]
        if 'DiffusionDirectionality' in diffn:
            if diffn.DiffusionDirectionality in ('NONE', 'ISOTROPIC'):
                indices.add(
                    pffg.FrameContentSequence[0].DimensionIndexValues[index_loc]
                )
    assert len(indices) == 1
    (index,) = indices
    return index


def diffn_iso_mframe_to_xda(dobj: dcm.Dataset) -> xr.DataArray:
    """
    Get a DataArray corresponding to just the "isotropic" frames.

    Parameters
    ----------
    dobj
        dicom multiframe diffusion dataset

    Returns
    -------
    A labelled xarray array consisting of just the isotropic trace images.

    """
    # TODO (RHD): Recheck order of the variables, bval should be on the first axis.

    index_of_iso_frames = _isotropic_index(
        dobj.PerFrameFunctionalGroupsSequence
    )
    return mf_to_xa(dobj).loc[{
        'DiffusionGradientOrientation': index_of_iso_frames,
        'StackID': '1'
    }].drop_vars([
        'DiffusionGradientOrientation', 'StackID'
    ]).rename({
        'InStackPositionNumber': 'z',
        'DiffusionBValue': 'bval'
    }).transpose('bval', 'z', 'y', 'x').sortby('bval')


def diffn_adc_mframe_to_xda(dobj: dcm.Dataset) -> xr.DataArray:
    """
    Get a DataArray corresponding to just the calculated ADC frames.

    Parameters
    ----------
    dobj
        dicom multiframe diffusion dataset

    Returns
    -------
    A labelled xarray array consisting of just the manufacturer adc maps.

    """
    index_of_iso_frames = _isotropic_index(
        dobj.PerFrameFunctionalGroupsSequence
    )
    return mf_to_xa(dobj).loc[{
        'DiffusionBValue': 1,
        'DiffusionGradientOrientation': index_of_iso_frames,
        'StackID': '1'
    }].drop_vars([
        'DiffusionGradientOrientation', 'StackID', 'DiffusionBValue'
    ]).rename({
        'InStackPositionNumber': 'z',
    }).transpose('z', 'y', 'x')


def diffn_mframes_to_xds(
     trace_dobj: dcm.Dataset,
     adc_dobj: Optional[dcm.Dataset] = None
     ) -> xr.Dataset:
    """
    Extract xarray dataset from dicom diffusion multiframe.

    Parameters
    ----------
    trace_dobj
        dicom multiframe diffusion dataset containing trace images
    adc_dobj
        dicom multiframe diffusion dataset containing adc images

    Returns
    -------
    an xarray dataset including both sets of images (where available)

    Notes
    -----
    This is typically the Philips case where everything is a single multiframe.

    """
    traces = diffn_iso_mframe_to_xda(trace_dobj)
    if adc_dobj is not None:
        adcs = diffn_adc_mframe_to_xda(adc_dobj)
        ds = xr.Dataset({
            'trace': traces,
            'manufacturer_adc': adcs
        })
    else:
        ds = xr.Dataset({
            'trace': traces,
        })

    ds.attrs['manufacturer'] = manufacturer(trace_dobj)
    ds.attrs['software_version'] = software_versions(trace_dobj)
    ds.attrs['dy'], ds.attrs['dx'] = pix_spacing_yx(trace_dobj)
    ds.attrs['orientation'] = approx_slice_orientation(trace_dobj)
    ds.attrs['sequence'] = seq_name(trace_dobj)

    # TODO (RHD): It's not clear whether we should use just plain indices for
    # z,y,x or we should try and put in the actual voxel locations in mm based
    # on ImagePositionPatient etc. It's inconsistent at the moment.
    return ds


def diffn_hybrid_to_xds(
     trace_dobjs: Sequence[dcm.Dataset],
     adc_dobjs: Optional[Sequence[dcm.Dataset]] = None
     ) -> xr.Dataset:
    """
    Extract xarray dataset from multiple dicom diffusion multiframes.

    Parameters
    ----------
    trace_dobjs
        list of dicom multiframe diffusion datasets containing trace images
    adc_dobjs
        list dicom multiframe diffusion datasets containing adc images

    Returns
    -------
    An xarray dataset including both sets of images (where available)

    Notes
    -----
    This typically is the Siemens XA case where the multiframe is over the slices only
    but each b value is its own separate object.

    """
    trace_dobjs = sorted(
        trace_dobjs, key=lambda d: diffusion_bvalue(d, frame=0)
    )
    trace_xas = [
        mf_to_xa(dobj).loc[{'StackID': '1', 'TemporalPositionIndex': 1}].drop_vars(
            ['StackID', 'TemporalPositionIndex']
        )
        for dobj in trace_dobjs
    ]
    bvals = [diffusion_bvalue(d, frame=0) for d in trace_dobjs]
    traces = xr.concat(trace_xas, 'bval').assign_coords(bval=bvals).rename({
        'InStackPositionNumber': 'z',
    })

    if adc_dobjs:
        adcs = [
            mf_to_xa(dobj).loc[{'StackID': '1', 'TemporalPositionIndex': 1}].drop_vars(
                ['StackID', 'TemporalPositionIndex']
            )
            for dobj in adc_dobjs
        ]
        adc = adcs[0].rename({
            'InStackPositionNumber': 'z',
        })
        ds = xr.Dataset({
            'trace': traces,
            'manufacturer_adc': adc
        })
    else:
        ds = xr.Dataset({
            'trace': traces,
        })

    ds.attrs['manufacturer'] = manufacturer(trace_dobjs[0])
    ds.attrs['software_version'] = software_versions(trace_dobjs[0])
    ds.attrs['dy'], ds.attrs['dx'] = pix_spacing_yx(trace_dobjs[0])
    ds.attrs['orientation'] = approx_slice_orientation(trace_dobjs[0])
    ds.attrs['sequence'] = seq_name(trace_dobjs[0])

    return ds


def diffn_series_to_xds(
     trace_dobjs: Sequence[dcm.Dataset],
     adc_dobjs: Optional[Sequence[dcm.Dataset]] = None
     ) -> xr.Dataset:
    """
    Extract xarray dataset from a sereis of single frame dicom diffusion images.

    Parameters
    ----------
    trace_dobjs
        list of dicom diffusion trace images
    adc_dobjs
        list of dicom diffusion adc images

    Returns
    -------
    An xarray dataset including both sets of images (where available)

    Notes
    -----
    This is the Siemens VE and GE case with traditional single frame DICOM,
    every slice position and every bvalue is a separate DICOM object.

    """
    trace_dobjs = sorted(
        trace_dobjs, key=lambda d: (diffusion_bvalue(d), slice_location(d))
    )

    nbvals = len(set(diffusion_bvalue(d) for d in trace_dobjs))
    nz = len(trace_dobjs) // nbvals
    bvals = [diffusion_bvalue(d) for d in trace_dobjs[::nz]]
    z = [slice_location(d) for d in trace_dobjs[:nz]]
    ny, nx = matrix_yx(trace_dobjs[0])

    imgdata = np.array(
        [d.pixel_array & (2**d.BitsStored - 1) for d in trace_dobjs],
        dtype=float
    )
    for i, d in enumerate(trace_dobjs):
        if 'RescaleSlope' in d:
            imgdata[i] *= d.RescaleSlope
        if 'RescaleIntercept' in d:
            imgdata[i] += d.RescaleIntercept

    traces = xr.DataArray(
        imgdata.reshape(nbvals, nz, ny, nx),
        dims=('bval', 'z', 'y', 'x'),
        coords={
            'bval': ('bval', bvals, {'units': 'sec/mm2'}),
            'z': ('z', z, {'units': 'mm'})
        },
        name='bval_imgs'
    )

    if adc_dobjs:
        adc_dobjs = sorted(adc_dobjs, key=slice_location)
        z = [slice_location(d) for d in adc_dobjs]
        if not np.allclose(z,  traces.coords['z']):
            # work around for GE bug: change of sign in slice_location
            # TODO (RHD): may be better to use ImagePositionPatient projected
            # along slice orientation
            adc_dobjs = sorted(adc_dobjs, key=lambda x: -slice_location(x))
            z = [-slice_location(d) for d in adc_dobjs]
            if not np.allclose(z,  traces.coords['z'], atol=0.1):
                raise ValueError(
                    f"ADC maps not aligned with trace images: {z} {traces.coords['z']}"
                )
            else:
                warn('GE Issue: slice positions reversed with respect to trace images')
                z = list(traces.coords['z'])

        # Apply any rescaling - we want meaningful real world units
        # (assume no Philips realworld scaling here)
        imgdata = np.array([
            d.pixel_array & (2**d.BitsStored - 1)
            for d in adc_dobjs
        ], dtype=float)

        for i, d in enumerate(adc_dobjs):
            if 'RescaleSlope' in d:
                imgdata[i] *= d.RescaleSlope
            if 'RescaleIntercept' in d:
                imgdata[i] += d.RescaleIntercept

        adcs = xr.DataArray(
            imgdata,
            dims=('z', 'y', 'x'),
            coords={'z': z},
            name='manufacturer_adc',
            attrs={
                # assume "usual" units
                'units': 'um2/sec'
            }
        )

        if not np.allclose(adcs.coords['z'], traces.coords['z']):
            raise ValueError('ADC maps not aligned with trace images')

        ds = xr.Dataset({
            'trace': traces,
            'manufacturer_adc': adcs
        })
    else:
        ds = xr.Dataset({
            'trace': traces,
        })

    # TODO (RHD): Do we want to simplify the z coords to be
    # just 0..n rather than slice posn once we've checked for consistency?
    ds.attrs['manufacturer'] = manufacturer(trace_dobjs[0])
    ds.attrs['software_version'] = software_versions(trace_dobjs[0])
    ds.attrs['dy'], ds.attrs['dx'] = pix_spacing_yx(trace_dobjs[0])
    ds.attrs['orientation'] = approx_slice_orientation(trace_dobjs[0])
    ds.attrs['sequence'] = seq_name(trace_dobjs[0])

    return ds


def diffn_to_xds(
     trace_dobjs: Sequence[dcm.Dataset],
     adc_dobjs: Optional[Sequence[dcm.Dataset]] = None) -> xr.Dataset:
    """
    Extract xarray diffusion dataset from dicom diffusion images.

    Parameters
    ----------
    trace_dobjs
        list of dicom diffusion trace images
    adc_dobjs
        list of dicom diffusion adc images

    Returns
    -------
    An xarray dataset including both sets of images (where available)

    Notes
    -----
    This is a wrapper routine to handle all three cases
    full multiframe, partial multiframe and single frame
    according to manufacturer.

    """
    manufact = manufacturer(trace_dobjs[0])
    is_mf = is_multiframe(trace_dobjs[0])
    if manufact == 'Philips' and is_mf and len(trace_dobjs) == 1:
        return diffn_mframes_to_xds(
            trace_dobjs[0], adc_dobjs[0] if adc_dobjs else None
        )
    elif manufact == 'Siemens' and is_mf:
        return diffn_hybrid_to_xds(trace_dobjs, adc_dobjs)
    elif manufact in ['Siemens', 'GE'] and not is_mf:
        return diffn_series_to_xds(trace_dobjs, adc_dobjs)
    else:
        raise ValueError(
            f'diffn_to_xds: unable to extract {manufact} {"multiframe" if is_mf else "series"}'
        )


def nist_phantom_mask(
     image: NDArray, filter_size: float = 2,
     dilate: bool = False, erode: bool = False, disk_size: float = 1.5
     ) -> NDArray[np.bool_]:
    """
    Generate a dilated mask of the phantom using an Otsu Threshold and watershed segmentation.

    Parameters
    ----------
    image
        image array (ny, nx)
    filter_size
        scale of median filter preprocessing for initial threshold
    dilate
        whether to dilate mask before returning
    erode
        whether to erode mask before returning
    disk_size
        structuring element size for dilation/erosion

    Returns
    -------
    Binary mask array of same dimensions as input image

    Notes
    -----
    If multiple disjoint phantom slices are present (eg for a 3d volume
    flattened into a strip) then there will be multiple regions in the mask.
    Loosely based on scikit-image examples.

    """
    # TODO (RHD): there are still some magic numbers to sort out in here.

    # Get initial threshold value for start of watershed
    threshold = threshold_otsu(median_filter(image, size=filter_size))

    # Handle empty or near empty slices at the ends
    if image.mean() < 10:
        return np.zeros_like(image, dtype=bool)

    # Apply threshold (use result directly if is segment small)
    mask = image > threshold
    if mask.sum() < 20:
        return mask

    # High and Low points in image as watershed markers
    ws_markers = np.piecewise(
        image,
        [image < 0.1*threshold, image > 1.1*threshold],
        [1, 2]
    ).astype(int)

    # Edge elevation map
    elevation_map = sobel(image)

    # Watershed segmentation
    mask = binary_fill_holes(watershed(elevation_map, ws_markers) - 1)

    # Optional adjustment of mask
    if dilate:
        mask = binary_dilation(mask, footprint=mdisk(disk_size))
    if erode:
        mask = binary_erosion(mask, footprint=mdisk(disk_size))

    return mask


def find_ridges(ds: xr.Dataset, slice_: int) -> NDArray[np.int_]:
    """
    Find ridges corresponding to the tube walls in the interior of phantom.

    Parameters
    ----------
    ds
        diffusion dataset with phantom images
    slice_
        index (base 0) of slice to use for analysis

    Returns
    -------
    Binary image tracing walls of tubes.

    """
    bavg = ds.trace.isel(z=slice_).mean(dim='bval').to_numpy()
    mask = nist_phantom_mask(bavg)
    elevation = laplace(bavg.max() - bavg, ksize=3, mask=mask)
    # TODO (RHD): nb arbitrary threshold
    return elevation > np.percentile(elevation, 95)


def find_tubes(
     ridges: NDArray[np.int_],
     roi_radius: float, ntubes: int
     ) -> Tuple[NDArray, NDArray, NDArray]:
    """
    Find the samples tubes in an image of the phantom.

    Parameters
    ----------
    ridges
        binary image of tube walls as determined by find_ridges
    roi_radius
        expected radius of tubes in image (pixels)
    ntubes
        the number of tubes

    Returns
    -------
    The x and y coordinates of the tubes and their best fit radii.

    """
    # Detect a range of 9 possible radii around the expected value
    hough_radii = np.linspace(np.floor(roi_radius-2), np.ceil(roi_radius+2), 9)
    hough_images = hough_circle(ridges, hough_radii)

    # Select the 13 most prominent circles found
    spacing = int(round(min(hough_radii) / np.sqrt(2)))
    _, cx, cy, radii = hough_circle_peaks(
        hough_images, hough_radii, total_num_peaks=ntubes,
        min_xdistance=spacing, min_ydistance=spacing
    )
    if len(radii) < ntubes:
        raise ValueError(f'Found only {len(radii)} of {ntubes} tubes')
    return cx, cy, radii


def find_lugs(
     ridges: NDArray, lug_radius: float, nlugs: int
     ) -> Tuple[NDArray, NDArray, NDArray]:
    """
    Find the small location tubes in an image of the phantom.

    Parameters
    ----------
    ridges
        binary image of tube walls as determined by find_ridges
    roi_radius
        expected radius of location tubes in image (pixels)
    nlugs
        the number of tubes

    Returns
    -------
    The x and y coordinates of the location tubes and their best fit radii.

    """
    # Detect a range of 6 possible radii around the expected value
    hough_radii = np.linspace(np.floor(lug_radius-1), np.ceil(lug_radius+1), 6)
    hough_images = hough_circle(ridges, hough_radii)

    # Select the most prominent 3 circles
    spacing = 2 * int(round(min(hough_radii)))
    _, cx, cy, radii = hough_circle_peaks(
        hough_images, hough_radii, total_num_peaks=nlugs,
        min_xdistance=spacing, min_ydistance=spacing
    )
    if len(radii) < nlugs:
        raise ValueError(
            f'Found only {len(radii)} of {nlugs} phantom alignment markers'
        )
    return cx, cy, radii


def vertex_angles(
     a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]
     ) -> NDArray[np.float64]:
    """
    Interior angles at each vertex of a triangle.

    Parameters
    ----------
    a, b, c
        x and y coordinates of the three corners of triangle

    Notes
    -----
    From http://ambrsoft.com/TrigoCalc/Triangles/3Points.htm

    Returns
    -------
    The angles at the three corners

    """
    xa, ya = a
    xb, yb = b
    xc, yc = c

    alpha = np.arctan2(yb - ya, xb - xa) - np.arctan2(yc - ya, xc - xa)
    beta = np.arctan2(ya - yb, xa - xb) - np.arctan2(yc - yb, xc - xb)
    gamma = np.arctan2(ya - yc, xa - xc) - np.arctan2(yb - yc, xb - xc)

    # Not sure if this is right or whether have to take it modulo 2*pi instead
    angles = np.array([
        360 - angle if angle > 180 else angle
        for angle in abs(np.degrees([alpha, beta, gamma]))
    ])
    assert np.isclose(angles.sum(), 180)
    return angles


def sorted_lugs(
     cx_l: Sequence[float], cy_l: Sequence[float], radii_l: Sequence[float]
     ) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """
    Sort the triangle of locating lugs according to their interior angles.

    Parameters
    ----------
    cx_l
        vertex x coordinates
    cy_l
        vertex y coordinates
    radii_l
        radii of lugs found at vertex

    Returns
    -------
    The vertices sorted in increasing order of interior angle

    """
    found_angles = vertex_angles(*zip(cx_l, cy_l))
    # force ascending order of angles 30, 60, 90
    # (assumed to correspond to order in phantom definition)
    sorting_order = found_angles.argsort()
    return (
        np.array(cx_l)[sorting_order],
        np.array(cy_l)[sorting_order],
        np.array(radii_l)[sorting_order]
    )


def rigid_transform(
     A: ArrayLike, B: ArrayLike
     ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Get best rigid transform between two 2D point sets (paired).

    Notes
    -----
    Assume coordinates are n x 2 lists of row-vectors

    Parameters
    ----------
    A
        first point set
    B
        second point set

    Returns
    -------
    Rotation and translation components of best rigid transform

    """
    A, B = np.asarray(A), np.asarray(B)
    nrows, ncols = A.shape
    assert A.shape == B.shape
    assert nrows == 2
    assert ncols >= 3

    # Centre
    centroid_A = A.mean(axis=1)
    centroid_B = B.mean(axis=1)
    A_centred = A - centroid_A[:, np.newaxis]
    B_centred = B - centroid_B[:, np.newaxis]

    # Rotation part
    H = A_centred @ B_centred.T
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T

    # Handle reflection ambiguity
    if np.linalg.det(R) < 0:
        Vt[1, :] *= -1
        R = Vt.T @ U.T

    # Reconstruct translation part
    t = -R @ centroid_A + centroid_B
    return R, t


def apply_transform(
     A: NDArray[np.float64], R: NDArray[np.float64], t: NDArray[np.float64]
     ) -> NDArray[np.float64]:
    """
    Apply a rigid transform to a point set.

    Parameters
    ----------
    A
        points
    R
        rotational part of transform
    t
        translation part of transform

    Returns
    -------
    Transformed points

    """
    return R @ A + t[:, np.newaxis]


def adjusted_roi_locations(
     ds: xr.Dataset, slice_: int,
     phantom: Dict[Any, Any]
     ) -> NDArray[np.float64]:
    """
    Get the expected tube centres in the image (adjusted for phantom misalignment).

    Parameters
    ----------
    ds
        diffusion dataset
    slice_
        index of slice to use
    phantom
        phantom description

    Returns
    -------
    The expected tube locations in the image accounding for phantom misalignment

    """
    # Phantom feature description
    roi_radius_mm = phantom['FeatureSizes']['Tubes']
    roi_locations_mm = phantom['Features']['Tubes']
    ntubes = len(roi_locations_mm)
    lug_radius_mm = phantom['FeatureSizes']['Lugs']
    lug_locations_mm = phantom['Features']['Lugs']
    nlugs = len(lug_locations_mm)

    # Find all edges *within* the phantom
    ridges = find_ridges(ds, slice_)

    # Find the tubes
    roi_radius_pixels = roi_radius_mm / ds.dx
    cx, cy, radii = find_tubes(ridges, roi_radius_pixels, ntubes)
    bavg = ds.trace.isel(z=slice_).mean(dim='bval').to_numpy()

    # Remove the tubes from the edge map to leave just the alignment lugs
    seg_mask = np.zeros_like(bavg, dtype=int)
    for x, y, r in zip(cx, cy, radii):
        seg_mask[disk((y, x), r+RADIUS_GROW, shape=seg_mask.shape)] = 1
    ridges_for_lugs = ~seg_mask & ridges

    # Find the alignment lugs, sorting them according to the angles subtended
    # to match description
    lug_radius_pixels = lug_radius_mm / ds.dx
    cx_l, cy_l, radii_l = sorted_lugs(
        *find_lugs(ridges_for_lugs, lug_radius_pixels, nlugs)
    )

    # The expected locations of the lugs and the locations found in the image
    ny, nx = bavg.shape
    centre = nx//2, ny//2
    lug_locations_expected = np.array([
        (x/ds.dx + centre[0], y/ds.dy + centre[1])
        for (x, y) in lug_locations_mm
    ])
    lug_locations_found = np.asarray([(cx_l[i], cy_l[i]) for i in range(3)])

    # Deduce transform to align the model with the image and apply this
    # to the expected positions of the tubes
    R, t = rigid_transform(lug_locations_expected.T, lug_locations_found.T)
    roi_locations_pixels = [
        (x/ds.dx + centre[0], y/ds.dy + centre[1])
        for (x, y) in roi_locations_mm
    ]
    return apply_transform(
        np.array(roi_locations_pixels).T, R, t
    ).T


def labelled_segmentation(
     ds: xr.Dataset, slice_: int,
     roi_locations: ArrayLike, roi_radius_mm: float,
     radius_trim: float = RADIUS_TRIM
     ) -> NDArray[np.int_]:
    """
    Segmention of tubes in the phantom, labelling according to their position in a list of expected positions.

    Parameters
    ----------
    ds
        diffusion dataset
    slice_
        index of slice to analyse
    roi_locations
        expected tube locations
    roi_radius_mm
        expected tube sizes (in mm)
    radius_trim
        ad-hoc erosion of rois to avoid tube walls

    Returns
    -------
    Regions of interest for tubes

    """
    roi_locations = np.asarray(roi_locations)

    # Find tube positions in image
    ridges = find_ridges(ds, slice_)
    roi_radius = roi_radius_mm / ds.dx
    cx, cy, radii = find_tubes(ridges, roi_radius, len(roi_locations))
    bavg = ds.trace.isel(z=slice_).mean(dim='bval').to_numpy()

    # Interiors of all the tube Hough circle with a small erosion
    seg_mask = np.zeros_like(bavg, dtype=int)
    for x, y, r in zip(cx, cy, radii):
        seg_mask[disk((y, x), r-radius_trim, shape=seg_mask.shape)] = 1

    # Label in scikit image and use centroids to find corresponding tubes
    # There should be 0 for the background and 1-13 for the tubes
    ski_labelling = label(seg_mask)

    # Find the nearest tube in the phantom description (index from one though)
    found_centroids = {
        rp.label: rp.centroid for rp in regionprops(ski_labelling)
    }
    tubeindices = {}
    for label_, (y, x) in found_centroids.items():
        dists = [np.hypot(x-x0, y-y0) for (x0, y0) in roi_locations]
        tubeindices[label_] = int(np.argmin(dists)) + 1

    # Relabel ROIs according to which tube they refer to.
    # This is a bit tricksy: 0 is the background so we'll map
    # 0->0 and 1,13->1,13 where this is the index of the tube + 1
    # The labels of the regions will be the indices of the tubes in
    # the phantom description + 1, so they will be in the
    # same order as in the the phantom description
    return np.array([0] + list(tubeindices.values()))[ski_labelling]


def nist_tube_segments(
     ds: xr.Dataset, slice_: int, phantom: Dict[Any, Any]
     ) -> Tuple[List[NDArray], List[NDArray], Optional[List[NDArray]]]:
    """
    Segmention of tubes in the phantom.

    Parameters
    ----------
    ds
        diffusion dataset
    slice_
        index of slice to analyse
    phantom
        phantom description

    Returns
    -------
    Regions of interest for tubes

    """
    # Adjust tube locations for phantom misalignment
    tube_locations = adjusted_roi_locations(ds, slice_, phantom)
    tube_radius_mm = phantom['FeatureSizes']['Tubes']

    # Labelled segmentation where the labels correspond to know tubes
    # in the phantom description
    label_image = labelled_segmentation(
        ds, slice_, tube_locations, tube_radius_mm
    )

    # Extract a region of interest at each of the tubes
    trace_images = ds.trace.isel(z=slice_).to_numpy()
    trace_props = [
        sorted(
            regionprops(label_image, intensity_image=image),
            key=lambda p: p.label
        )
        for image in trace_images
    ]
    roi_masks = [prop.image for prop in trace_props[0]]

    # The trace roi images at each b-value, rearranged as
    # nbvals*ny*nx numpy array for each roi
    trace_roi_lists = [
        [prop.intensity_image for prop in props]
        for props in trace_props
    ]
    trace_rois = [np.asarray(ims) for ims in zip(*trace_roi_lists)]

    adc_rois = None
    if 'manufacturer_adc' in ds:
        adc_image = ds.manufacturer_adc.isel(z=slice_).to_numpy()
        # NB we are doing this twice ..
        adc_props = sorted(
            regionprops(label_image, intensity_image=adc_image),
            key=lambda p: p.label
        )
        adc_rois = [prop.intensity_image for prop in adc_props]
    else:
        adc_rois = None

    return roi_masks, trace_rois, adc_rois


def refine_tube_mask(mask, b0, margin=0.25):
    """
    Trim the mask for a tube by region growing around a small central area.

    Parameters
    ----------
    mask
        existing mask
    b0
        corresponding b0 image for intensity
    margin
        margin in intensity for region growing

    Returns
    -------
    Trimmed mask.

    """
    # Clear the boundaries of the mask so erosion doesn't stick to the edges
    assert mask.shape == b0.shape

    mask = mask.copy()
    mask[:, [0, -1]] = mask[[0, -1], :] = 0

    # Erode to a small inner region in the centre and get the mean from
    # the b=0 image there
    inner = binary_erosion(mask, footprint=mdisk(5))
    average = np.ma.masked_where(~inner, b0).mean()

    # Use the mean to define thresholds for a connected region
    # including the inner one
    lower, upper = average * (1 - margin), average * (1 + margin)
    region_mask = binary_fill_holes(((lower < b0) & (b0 < upper)) | inner)
    labels = label(region_mask, connectivity=1)
    regions = sorted(regionprops(labels), key=lambda r: r.area, reverse=True)

    # Use the convex hull to fill ragged 'cracks' in the new ROI
    return convex_hull_image(labels == regions[0].label) & mask


def adc_nllsq(
     bvalues: ArrayLike, traceimages: NDArray[np.float64],
     mask: NDArray[np.bool_]
     ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Fit an adc model on a voxel by voxel basis to the trace image.

    We'll do a direct monoexponential fit (rather than a log-transform) and
    allow for a noise floor term added in quadrature.

    ADC units are mm^2/sec scaled by 10^6 (so typical values 1000-2000)

    Parameters
    ----------
    bvalues
        vector of the bvalues of the trace images
    traceimages
        the images at each bvalue
    mask
        mask applied to images to exclude background pixels from fitting

    Returns
    -------
    M0 and ADC maps from fitting

    Notes
    -----
    This is very slow as it is a top level loop over all the voxels.

    """
    # TODO (RHD): It might be possible to speed this up as it parallelisable.

    # Noise floor estimate at each bvalue
    noise_mask = ~binary_dilation(mask)
    noise = np.array([
        traceimage[noise_mask].mean() for traceimage in traceimages
    ])

    # Mono-exponential decay with ad-hoc noise background added in quadrature
    # Noise contribution is added in linearly for signal below twice the
    # noise floor. NB not quite right as noise will be averaged non-central chi
    # more approximately Rician and mean goes to zero for first part of curve
    # - there may well be a better model for this ..
    # nb: noise is not a parameter but captured in a closure
    def diffusion_model(b, s, d):
        return np.hypot(s * np.exp(-d * b), noise)

    def fit_pixel(bvalues, signal):
        # Starting values and box constraints for parameters
        # Allow large upper bound for s in case lowest b image is not a b0
        # I suppose we could speed things up a bit by using a log transform
        # (or even just a ratio) as a starting point?
        boxes = np.array([
            # min, start, max
            [0.75*signal[0],    signal[0],  4*signal[0]],   # s
            [100e-6,            500e-6,     3000e-6],       # adc
        ]).T

        # Non-linear least squares model fit
        (s, adc), _ = curve_fit(
            diffusion_model, bvalues, signal,
            p0=boxes[1],
            bounds=boxes[[0, 2]]
        )
        return s, adc

    adc_map = np.zeros_like(traceimages[0])
    m0_map = np.zeros_like(traceimages[0])
    nrows, ncols = traceimages[0].shape
    for y in range(nrows):
        for x in range(ncols):
            if mask[y, x] and np.all(traceimages[:, y, x] > 0):
                s0, adc = fit_pixel(bvalues, traceimages[:, y, x])
                m0_map[y, x] = s0
                adc_map[y, x] = adc

    return m0_map, 1e6 * adc_map
