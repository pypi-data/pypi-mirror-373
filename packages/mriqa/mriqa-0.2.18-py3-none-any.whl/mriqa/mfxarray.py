#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mfxarray.py: Extracting dicom multiframes into labelled arrays."""

import re

import numpy as np
import xarray as xr

import pydicom as dcm
from pydicom.datadict import keyword_for_tag


def _index_label(dimindex: dcm.Dataset) -> str:
    """
    Get a label for an multiframe index based on the tag name.

    Failing that use the DimensionDescriptionLabel or a string from (gggg,eeee)

    Parameters
    ----------
    dimindex
        component of DimensionIndex sequence

    Returns
    -------
    suitable label for dimension of multiframe

    """
    def camel(a: str) -> str:
        """Tidy up free text descriptions to be a bit more like tag names."""
        return re.sub(
            r'(_|-)+', ' ', re.sub(r'\W+|^(?=\d)', '_', a)
        ).title().replace(' ', '')

    index_ptr = dimindex.DimensionIndexPointer
    # keyword_for_tag returns empty string if tag not in dict
    label = keyword_for_tag(index_ptr)
    if not label:
        # Philips put in a label whereas Siemens don't seem to.
        # May need more thought on mapping to variable name
        if 'DimensionDescriptionLabel' in dimindex:
            label = camel(dimindex.DimensionDescriptionLabel)
        else:
            label = camel('Tag' + str(index_ptr))
    return label


def mf_to_xa(dobj: dcm.Dataset) -> xr.DataArray:
    """
    "Un-opinionated" mapping from a dicom (diffusion) multiframe to an xarray.

    Parameters
    ----------
    dobj
        dicom multiframe

    Returns
    -------
    A labelled xarray array constructed from the multiframe.

    """
    # TODO (RHD): Decide whether we want real world units or just indices for voxels.

    # The image data in frame order - will have dims: nframes * ny * nx
    mfdata = (dobj.pixel_array & (2**dobj.BitsStored - 1)).astype(float)

    # Apply image scaling - special handling for Philips
    sfg = dobj.SharedFunctionalGroupsSequence[0]
    pffgs = dobj.PerFrameFunctionalGroupsSequence
    if 'RealWorldValueMappingSequence' in sfg:
        rwvm = sfg.RealWorldValueMappingSequence[0]
        if 'RealWorldValueSlope' in rwvm:
            mfdata *= rwvm.RealWorldValueSlope
        if 'RealWorldValueIntercept' in rwvm:
            mfdata += rwvm.RealWorldValueIntercept
        if 'MeasurementUnitsCodeSequence' in rwvm:
            # Special case for ADC: generally have an extra factor 10^6
            if rwvm.MeasurementUnitsCodeSequence[0].CodeValue == 'mm2/s':
                mfdata *= 1e6
    else:
        for i, pffg in enumerate(dobj.PerFrameFunctionalGroupsSequence):
            if 'PixelValueTransformationSequence' in pffg:
                pvt = pffg.PixelValueTransformationSequence[0]
                if 'RescaleSlope' in pvt:
                    mfdata[i] *= pvt.RescaleSlope
                if 'RescaleIntercept' in pvt:
                    mfdata[i] += pvt.RescaleIntercept

    # We can get the axes labels and the info to extract the values
    # from the DimensionIndexSequence
    # Each one corresponds to an index DimensionIndexValues
    # From these pointers and the indices in the frames we can get the values
    # The accessors are closures to access these
    labels = [
        _index_label(dimindex)
        for dimindex in dobj.DimensionIndexSequence
    ]
    fgpointers = [
        dimindex.FunctionalGroupPointer
        for dimindex in dobj.DimensionIndexSequence
    ]
    indexpointers = [
        dimindex.DimensionIndexPointer
        for dimindex in dobj.DimensionIndexSequence
    ]
    accessors = [
        lambda pffg, index, fgp=fgp, ip=ip:
            pffg[fgp][0][ip].value if ip in pffg[fgp][0] else index
        for fgp, ip in zip(fgpointers, indexpointers)
    ]

    # Check range of indices
    pffgs = dobj.PerFrameFunctionalGroupsSequence
    all_indices = np.array([
        pffg.FrameContentSequence[0].DimensionIndexValues for pffg in pffgs
    ], dtype=int).T
    index_vectors = [sorted(set(indices)) for indices in all_indices]
    index_lengths = [len(index_vector) for index_vector in index_vectors]
    dims = tuple(index_lengths)
    xadata = np.empty(dims + mfdata.shape[-2:], dtype=mfdata.dtype)

    # Want list of arrays of coords
    indices = pffgs[0].FrameContentSequence[0].DimensionIndexValues
    dtypes = []
    for accessor, index in zip(accessors, indices):
        dtypes.append(type(accessor(pffgs[0], index)))
    coords = [np.empty(dim, dtype=dtype) for (dim, dtype) in zip(dims, dtypes)]

    for frame, pffg in enumerate(pffgs):
        indices = pffg.FrameContentSequence[0].DimensionIndexValues
        np_indices = tuple([
            index_vector.index(i)
            for index_vector, i in zip(index_vectors, indices)
        ])
        xadata[np_indices] = mfdata[frame]
        for i, (accessor, index) in enumerate(zip(accessors, indices)):
            coords[i][np_indices[i]] = accessor(pffg, index)

    # TODO (RHD): might want to enforce z (if exists), y, x as trailing coordinates
    ny, nx = xadata.shape[-2:]
    return xr.DataArray(
        xadata,
        dims=labels + ['y', 'x'],
        coords={
            label: (label, coord_vector)
            # TODO (RHD): was this sensitive to original coordinate order?
            for (label, coord_vector) in zip(
                labels + ['y', 'x'], coords + [np.arange(ny), np.arange(nx)]
            )
        }
    )
