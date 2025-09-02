#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""noras.py: graphical reports of NORAS standard QA."""

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import PowerNorm
from matplotlib.patches import Circle

from .. phantoms import SIEMENSD165, find_phantom
from .. dcmio import pix_spacing_yx, rx_coil_id, rx_coil_name
from .. tools import image_from_dicom


REFERENCE_VALUES_1T5 = {
    'RX1': 80,
    'RX2': 100,
    'RX3': 100,
    'RX4': 80,
    'RX5': 80,
    'RX6': 100,
    'RX7': 100,
    'RX8': 80,
    'BTM;TOP': 280
}

REFERENCE_VALUES_3T = {
    'RX1': 220,
    'RX2': 300,
    'RX3': 300,
    'RX4': 220,
    'RX5': 220,
    'RX6': 300,
    'RX7': 300,
    'RX8': 220,
    'BTM;TOP': 700
}


def _signal_disc(dobj, phantom=SIEMENSD165, target_area_mm2=22000):
    """
    Disc ROI within phantom for signal measurement.
    """

    image = image_from_dicom(dobj)
    dy, dx = pix_spacing_yx(dobj)
    if not np.isclose(dy, dx):
        raise ValueError('Only square pixels supported for NORAS QA images')

    # Find_phantom returns pixel coordinates in natural order (x, y)
    expected_radius = phantom['Diameter'] / 2 / dy
    centre_x, centre_y, radius = find_phantom(image, expected_radius)

    # Adjust radius for required area (provided that wouldn't extend it outside phantom)
    phantom_area_mm2 = np.pi * (radius * dy) ** 2
    radius_factor = np.sqrt(target_area_mm2 / phantom_area_mm2)
    if radius_factor < 1:
        radius *= radius_factor

    return centre_x, centre_y, radius


def _noise_disc(dobj, target_area_mm2=2500):
    """Disc ROI in lower RH corner of image for background measurement."""
    # Radius of noise roi in bottom right corner
    image = image_from_dicom(dobj)
    ny, nx = image.shape

    # require square pixels
    dy, dx = pix_spacing_yx(dobj)
    if not np.isclose(dy, dx):
        raise ValueError('Only square pixels supported for NORAS QA images')

    radius = np.sqrt(target_area_mm2 / np.pi) / dy
    centre_y, centre_x = int(ny - radius), int(nx - radius)

    return centre_x, centre_y, radius


def _disc_to_mask(shape, centre_x, centre_y, radius):
    """Binary mask based on centre and radius of circular ROI."""
    y, x = np.ogrid[:shape[0], :shape[1]]
    y -= centre_y
    x -= centre_x
    return x**2 + y**2 < radius**2


def noras_snr_report(single_element_dobjs, combined_dobj, cmap='bone', gamma=0.5, title=None, phantom=SIEMENSD165):
    """
    Report on SNR of NORAS neurosurgical coil using Siemens "sn" sequence.

    On Siemens systems the measurements are made on the standard D165 spherical phantom.
    In addition, on 3T scanners the FFT scale factor in the system tab is
    set to a value of 0.5 to avoid signal clipping in the images.
    This is ignored here as it does not effect the SNR ratio.

    Parameters
    ----------
    single_element_dobjs : Sequence of dicom objects
        single element dicom images
    combined_dobj : dicom object
        coil combined dicom images
    cmap : Optional maplotlib colour map spec
        color map for image display (default: bone)
    gamma : Optional float
        exponent of image remapping for display (default: 0.5)
    title : Optional str
        title for plot (default: constructed from acquisition date)
    phantom : Optional str
        the phantom that was scanned

    Returns
    -------
    Pandas dataframe of results

    """
    # Mask for signal region within phantom
    signal_x, signal_y, signal_r = _signal_disc(combined_dobj, phantom)
    signal_mask = _disc_to_mask(
        shape=combined_dobj.pixel_array.shape,
        centre_x=signal_x,
        centre_y=signal_y,
        radius=signal_r
    )

    # Mask for noise region in image corner
    noise_x, noise_y, noise_r = _noise_disc(combined_dobj)
    noise_mask = _disc_to_mask(
        shape=combined_dobj.pixel_array.shape,
        centre_x=noise_x,
        centre_y=noise_y,
        radius=noise_r
    )

    # Stack of images ordered by coil element name, ending in the combined image
    dobjs = sorted(single_element_dobjs, key=rx_coil_name) + [combined_dobj]
    images = [d.pixel_array & 0x0fff for d in dobjs]

    # The names of the coil elements in the same order
    coil_element_names = [rx_coil_name(d) for d in dobjs]

    # Reference values are defined for 1.5T and 3T scanners
    field_strength = float(combined_dobj.MagneticFieldStrength)
    if np.isclose(field_strength, 1.5, atol=0.1):
        reference_values = REFERENCE_VALUES_1T5
    elif np.isclose(field_strength, 3.0, atol=0.1):
        reference_values = REFERENCE_VALUES_3T
    else:
        raise ValueError('Unsupported field strength %fT' % field_strength)

    # Calculate the SNR for each element in turn
    signal = np.array([
        np.ma.mean(np.ma.array(image, mask=np.logical_not(signal_mask)))
        for image in images
    ])
    noise = np.array([
        np.ma.std(np.ma.array(image, mask=np.logical_not(noise_mask)))
        for image in images
    ])
    snr = signal / noise

    # Construct an image montage nrows x ncols for display
    nimages = len(images)
    ncols = int(round(np.sqrt(nimages)))
    nrows = int(np.ceil(nimages / ncols))
    if ncols == 0 or nrows == 0:
        nrows = ncols = 1

    ny, nx = images[0].shape
    montage = np.zeros((ny*nrows, nx*ncols))
    for i, image in enumerate(images):
        x, y = (i % ncols) * nx, (i // ncols) * ny
        montage[y:y+ny, x:x+nx] = image

    fig, ax = plt.subplots(1, 1, figsize=(14, 14))

    # Display the images
    mplim = ax.imshow(montage, norm=PowerNorm(gamma), cmap=cmap)
    ax.axis('image')
    ax.axis('off')

    # Add labels
    textcolour = 'white'

    x_0, y_0 = nx // 16, ny // 12
    for i in range(nimages):
        # Text position
        x, y = x_0 + (i % ncols) * nx, y_0 + (i // ncols) * ny
        ax.text(
                x, y,
                'S%d/%s' % (
                    dobjs[i].SeriesNumber, coil_element_names[i]
                ),
                color=textcolour
            )
    x_0, y_0 = nx - nx // 4, ny // 12
    for i in range(nimages):
        # Text position
        x, y = x_0 + (i % ncols) * nx, y_0 + (i // ncols) * ny
        ax.text(
            x, y,
            'SNR:%0.0f' % snr[i],
            color='green' if snr[i] > reference_values[coil_element_names[i]] else 'red'
        )

    x_0, y_0 = signal_x, signal_y
    for i in range(nimages):
        # Roi position
        x, y = x_0 + (i % ncols) * nx, y_0 + (i // ncols) * ny
        ax.add_patch(Circle((x, y), radius=signal_r, fill=False, color='C1'))
        ax.text(
            x, y, '%0.0f' % signal[i],
            color='C1', horizontalalignment='center', verticalalignment='center'
        )

    x_0, y_0 = noise_x, noise_y
    for i in range(nimages):
        # Roi position
        x, y = x_0 + (i % ncols) * nx, y_0 + (i // ncols) * ny
        ax.add_patch(Circle((x, y), radius=noise_r, fill=False, color='C0'))
        ax.text(
            x, y, '%0.1f' % noise[i],
            color='C0', horizontalalignment='center', verticalalignment='center'
        )

    if title is None:
        title = 'Noras Coil SNR (%s) [%s, %s]' % (
            rx_coil_id(combined_dobj),
            combined_dobj.ManufacturerModelName,
            combined_dobj.AcquisitionDate
        )
    ax.set_title(title, fontsize=16)

    # Colourbar clipped to height of the image
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(mplim, cax=cax)

    # Return results as a pandas DataFrame
    df = pd.DataFrame(list(zip(signal, noise, snr)), columns=['Signal', 'Noise', 'SNR'], index=coil_element_names)
    df.index.name = 'Element'
    df['ReferenceLevel'] = pd.Series(reference_values)
    df['Pass'] = df.SNR >= df.ReferenceLevel

    return df
