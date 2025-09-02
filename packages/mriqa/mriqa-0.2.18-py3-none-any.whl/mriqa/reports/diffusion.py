#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""diffusion.py: Graphical reports of water diffusion tests."""

from collections import Counter

from typing import Optional, Dict, Any, Sequence

import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm

import numpy as np
import pandas as pd

import pydicom as dcm

from scipy.stats import trimboth
from skimage.morphology import (
    binary_erosion, disk as mdisk
)

from .. phantoms import NISTDWI, nist_adc_k30
from .. nistadc import (
    diffn_to_xds, nist_phantom_mask, adc_nllsq,
    nist_tube_segments, refine_tube_mask
)

SLICE = 10


def nist_dwi_calibration_report(
     trace_dobjs: Sequence[dcm.Dataset],
     adc_dobjs: Optional[Sequence[dcm.Dataset]] = None,
     slice_: int = SLICE, phantom: Dict[str, Any] = NISTDWI,
     phantom_temperature: float = 20,
     flip_rl: bool = False, flip_ud: bool = False
     ) -> pd.DataFrame:
    """
    NIST DWI Phantom ADC scale calibration report.

    Produce a report of the calibration of the adc scale bases in nonlinear fitting and the manufacturer's method.

    Parameters
    ----------
    trace_dobjs
        dicom objects with trace ("bvalue") images
    adc_objects
        dicom objects with manufacturer's calculated adc maps
    slice_
        index of slice to use in analysis
    phantom
        phantom description
    phantom_temperature
        temperature of phantom at time of scan - determines expected adc results
    flip_rl
        correct for images flipped right-left
    flip_ud
        correct for images flipped up-down

    Notes
    -----
    Produces a matplotlib figure the can be shown with plt.show()

    Returns
    -------
    Pandas dataframe with results of region of interest analysis.

    """
    # Extract from dicom as an xarray dataset
    ds = diffn_to_xds(trace_dobjs=trace_dobjs, adc_dobjs=adc_dobjs)

    # Handle the phantom positioned in a non-standard orientation
    if flip_rl:
        ds.trace.data = np.flip(ds.trace.data, axis=-1)
        if 'manufacturer_adc' in ds:
            ds.manufacturer_adc.data = np.flip(ds.manufacturer_adc.data, axis=-1)
    if flip_ud:
        ds.trace.data = np.flip(ds.trace.data, axis=-2)
        if 'manufacturer_adc' in ds:
            ds.manufacturer_adc.data = np.flip(ds.manufacturer_adc.data, axis=-2)

    # ADC maps either using non-linear least squares based on the trace images
    # or manufacturer produced maps
    # The only masking is to exclude the exterior of the phantom.
    traces = ds.trace.isel(z=slice_)
    bvalues = ds.trace.coords['bval'].to_numpy()
    whole_phantom_mask = nist_phantom_mask(traces.mean(dim='bval').to_numpy())
    m0_image, nllsq_adc_image = adc_nllsq(
        bvalues, traces.to_numpy(), whole_phantom_mask
    )
    if 'manufacturer_adc' in ds:
        manuf_adc_image = ds.manufacturer_adc.isel(z=slice_).to_numpy() * whole_phantom_mask

    # Per tube ROI Analysis within phantom:
    #   Align phantom description to images and identify tubes
    #   nist_tube_segments returns rois for manufacturer adc only if available
    roi_masks, trace_rois, manuf_adc_rois = nist_tube_segments(ds, slice_, phantom)

    # Repeat fitting of adc model to the trace rois on a pixel by pixel basis
    m0_rois, nllsq_adc_rois = zip(*[
        adc_nllsq(bvalues, trace_roi, roi_mask)
        for (trace_roi, roi_mask) in zip(trace_rois, roi_masks)
    ])

    # Refine the masks based on both the adc_map and b0
    # TODO (RHD): maybe make refine_tube_mask() take the adc map as well?
    b0_rois = [trace_roi[0] for trace_roi in trace_rois]
    roi_masks = [
        roi_mask if nllsq_adc_roi[roi_mask].std() < 0.075*nllsq_adc_roi[roi_mask].mean()
        else refine_tube_mask(roi_mask, b0_roi)
        for (roi_mask, b0_roi, nllsq_adc_roi) in zip(roi_masks, b0_rois, nllsq_adc_rois)
    ]

    # The nominal adc values for each tube based on the temperature
    # and the PVP concentrations
    roi_concentrations = phantom['FeatureProperties']['Concentrations']
    nominal_adc_values = [
        nist_adc_k30(c, phantom_temperature) for c in roi_concentrations
    ]

    # ADC summary statistics of the ROIs;
    # nb use refined mask and trimmed means for robustness
    nllsq_adc_values = [
        trimboth(adc_roi[mask], 0.05).mean()
        for adc_roi, mask in zip(nllsq_adc_rois, roi_masks)
    ]

    nllsq_adc_errors = [
        trimboth(adc_roi[mask], 0.05).std()
        for adc_roi, mask in zip(nllsq_adc_rois, roi_masks)
    ]

    # Signal to Noise Estimates for each tube at the maximum b value
    bmax_rois = [trace_roi[-1] for trace_roi in trace_rois]
    # TODO (RHD): see the best way to reduce the mask to just a central region
    # here we are using morphology, but a disc may be better
    bmax_signal_values = [
        bmax_roi[binary_erosion(mask, footprint=mdisk(5))].mean()
        for bmax_roi, mask in zip(bmax_rois, roi_masks)
    ]
    bmax_signal_errors = [
        bmax_roi[binary_erosion(mask, footprint=mdisk(5))].std()
        for bmax_roi, mask in zip(bmax_rois, roi_masks)
    ]

    # Summary DataFrame
    df = pd.DataFrame({
        'Concentration': roi_concentrations,
        'Nominal': nominal_adc_values,
        'NLLSQ_Mean': nllsq_adc_values,
        'NLLSQ_StdDev': nllsq_adc_errors,
        'BMax_Mean': bmax_signal_values,
        'BMax_StdDev': bmax_signal_errors,
    })

    # Weighted combination of values from multiple tubes with the same conc
    df['nllsq_weights'] = 1 / df['NLLSQ_StdDev'] ** 2
    df['nllsq_weighted_vals'] = df['NLLSQ_Mean'] * df['nllsq_weights']
    df['bmax_weights'] = 1 / df['BMax_StdDev'] ** 2
    df['bmax_weighted_vals'] = df['BMax_Mean'] * df['bmax_weights']

    df = df.groupby('Concentration').agg(
        Nominal=('Nominal', 'mean'),
        nllsq_sum_weighted=('nllsq_weighted_vals', 'sum'),
        nllsq_sum_weights=('nllsq_weights', 'sum'),
        bmax_sum_weighted=('bmax_weighted_vals', 'sum'),
        bmax_sum_weights=('bmax_weights', 'sum')
    )
    df['NLLSQ_Mean'] = df['nllsq_sum_weighted'] / df['nllsq_sum_weights']
    df['NLLSQ_StdDev'] = np.sqrt(1 / df['nllsq_sum_weights'])
    df['BMax_Mean'] = df['bmax_sum_weighted'] / df['bmax_sum_weights']
    df['BMax_StdDev'] = np.sqrt(1 / df['bmax_sum_weights'])
    df['BMax_SNR'] = df['BMax_Mean'] / df['BMax_StdDev']

    df = df.drop([
        'nllsq_sum_weighted', 'nllsq_sum_weights',
        'bmax_sum_weighted', 'bmax_sum_weights'
    ], axis=1)

    if manuf_adc_rois and 'manufacturer_adc' in ds:
        # Further refine mask to exclude crazy values in ge maps
        roi_masks = [
            roi_mask & (100 < manuf_adc_roi) & (manuf_adc_roi < 5000)
            for (manuf_adc_roi, roi_mask) in zip(manuf_adc_rois, roi_masks)
        ]

        manuf_adc_rois = [
            manuf_adc_roi * roi_mask
            for (manuf_adc_roi, roi_mask) in zip(manuf_adc_rois, roi_masks)
        ]

        manuf_adc_values = [
            trimboth(manuf_adc_roi[roi_mask], 0.05).mean()
            for manuf_adc_roi, roi_mask in zip(manuf_adc_rois, roi_masks)
        ]
        manuf_adc_errors = [
            trimboth(manuf_adc_roi[roi_mask], 0.05).std()
            for manuf_adc_roi, roi_mask in zip(manuf_adc_rois, roi_masks)
        ]

        # Summary DataFrame for manufacturers' adc values
        df_manuf = pd.DataFrame({
            'Concentration': roi_concentrations,
            'Manuf_Mean': manuf_adc_values,
            'Manuf_StdDev': manuf_adc_errors,
        })

        # Weighted combination of values from multiple tubes with the same conc
        df_manuf['adc_weights'] = 1 / df_manuf['Manuf_StdDev'] ** 2
        df_manuf['adc_weighted_vals'] = df_manuf['Manuf_Mean'] * df_manuf['adc_weights']
        df_manuf = df_manuf.groupby('Concentration').agg(
            adc_sum_weighted=('adc_weighted_vals', 'sum'),
            adc_sum_weights=('adc_weights', 'sum')
        )
        df_manuf['Manuf_Mean'] = df_manuf['adc_sum_weighted'] / df_manuf['adc_sum_weights']
        df_manuf['Manuf_StdDev'] = np.sqrt(1 / df_manuf['adc_sum_weights'])
        df_manuf = df_manuf.drop(['adc_sum_weighted', 'adc_sum_weights'], axis=1)
        df = pd.concat([df, df_manuf], axis=1)

    # Subplot grid layout including axis for adc colorbar
    nbvalues = len(bvalues)
    fig = plt.figure(figsize=(15, 12))
    imgcols = 5
    mrows, ncols = 3, imgcols*nbvalues + 1
    gs = plt.GridSpec(mrows, ncols, fig)
    axs = [
        # Trace images
        fig.add_subplot(gs[0, i*imgcols:(i+1)*imgcols])
        for i in range(nbvalues)
    ] + [
        # Calibration Plot
        fig.add_subplot(gs[1:, :imgcols*(nbvalues-1)]),
        # ADC images
        fig.add_subplot(gs[1, imgcols*(nbvalues-1):ncols-1]),
        fig.add_subplot(gs[2, imgcols*(nbvalues-1):ncols-1]),
        # ADC colorbar
        fig.add_subplot(gs[1:, ncols-1])
    ]

    # The trace (ie bvalue) images
    vmin, vmax = 0, np.percentile(traces[0], 98)
    for ax, trace, bvalue in zip(axs, traces, bvalues):
        ax.imshow(trace, vmin=vmin, vmax=vmax, cmap='bone')
        ax.axis(False)
        ax.set_title(f'b={int(bvalue)}')

    # Plot of ADC "calibration" curves
    ax = axs[-4]
    ax.set_title('ADC Calibration')
    ax.grid(True)
    ax.set_xlabel(r'Nominal ADC $(x 10^{-6} mm^2/s)$')
    ax.set_ylabel(r'Measured ADC $(x 10^{-6} mm^2/s)$')
    ax.set_ylim([250, 2250])
    concs = np.linspace(0, 50, 51)
    x = [nist_adc_k30(conc, phantom_temperature) for conc in concs]
    y_lower, y_upper = (
        [nist_adc_k30(conc, phantom_temperature-2) for conc in concs],
        [nist_adc_k30(conc, phantom_temperature+2) for conc in concs]
    )
    ax.fill_between(
        x, y_lower, y_upper,
        label=f'{phantom_temperature-2}-{phantom_temperature+2}' + r'$^{\circ}$C',
        alpha=0.25, color='C2'
    )
    ax.plot(
        x, x, linestyle='dotted', color='C3',
        label=f'Nominal ({phantom_temperature}$^{{\\circ}}$C)'
    )

    # Ordered points to plot
    x, y_nllsq, dy_nllsq = zip(
        *sorted(zip(nominal_adc_values, nllsq_adc_values, nllsq_adc_errors))
    )

    # Jittering to avoid overplotting results from similar tubes
    jittered_x = x + 0.5 * (np.random.uniform(size=len(x)) - 0.5)
    ax.errorbar(
        jittered_x, y_nllsq, yerr=dy_nllsq,
        fmt='+', color='C0', label='NLLSQ'
    )

    if manuf_adc_rois is not None:
        # Ordered points to plot
        _, y_manuf, dy_manuf = zip(*sorted(
            zip(nominal_adc_values, manuf_adc_values, manuf_adc_errors)
        ))
        ax.errorbar(
            jittered_x, y_manuf, yerr=dy_manuf, fmt='o', fillstyle='none',
            color='C1', label=f"{ds.attrs['manufacturer']}"
        )

    # Twiddle order of legend labels for aesthetic reasons
    hs, ls = ax.get_legend_handles_labels()
    label_reordering = [2, 3, 1, 0] if manuf_adc_rois is not None else [2, 1, 0]
    ax.legend(
        [hs[i] for i in label_reordering],
        [ls[i] for i in label_reordering]
    )

    # ADC maps
    vmin, vmax = 0, 2500
    im = axs[-3].imshow(nllsq_adc_image, vmin=vmin, vmax=vmax, cmap='cividis')
    axs[-3].set_title('ADC Map (NLLSQ)')
    if 'manufacturer_adc' in ds:
        # The additional mask here is to exclude pixels labelled as NA in
        # GE images using a large integer
        im = axs[-2].imshow(
            np.ma.masked_where(manuf_adc_image > 5000, manuf_adc_image),
            vmin=vmin, vmax=vmax, cmap='cividis'
        )
        axs[-2].set_title(f"ADC Map ({ds.attrs['manufacturer']})")
    for ax in axs[-3:-1]:
        ax.axis(False)

    fig.colorbar(im, cax=axs[-1], label=r'$(x 10^{-6} mm^2/s)$')
    fig.suptitle(
        f"NIST ADC Calibration [{ds.attrs['sequence']}:{ds.attrs['orientation']}]",
        fontsize=20
    )

    return df


def nist_dwi_fitting_report(
     trace_dobjs: Sequence[dcm.Dataset], slice_: int = SLICE,
     phantom: Dict[str, Any] = NISTDWI,
     phantom_temperature: float = 20,
     flip_rl: bool = False, flip_ud: bool = False
     ) -> pd.DataFrame:
    """
    NIST DWI Phantom ADC roi fitting report.

    Produce a report of the fitting of the per-pixel adc using nonlinear least squares.

    Parameters
    ----------
    trace_dobjs
        dicom objects with trace ("bvalue") images
    adc_objects
        icom objects with manufacturer's calculated adc maps
    slice_
        index of slice to use in analysis
    phantom
        phantom description
    phantom_temperature
        temperature of phantom at time of scan - unused in this report
    flip_rl
        correct for images flipped right-left
    flip_ud
        correct for images flipped up-down

    Notes
    -----
    Produces a matplotlib figure the can be shown with plt.show()

    Returns
    -------
    Pandas dataframe with results of region of interest analysis.

    """
    # Extract from dicom as an xarray dataset
    ds = diffn_to_xds(trace_dobjs=trace_dobjs, adc_dobjs=None)

    # Handle the phantom positioned in a non-standard orientation
    if flip_rl:
        ds.trace.data = np.flip(ds.trace.data, axis=-1)

    if flip_ud:
        ds.trace.data = np.flip(ds.trace.data, axis=-2)

    bvalues = ds.trace.coords['bval'].to_numpy()
    roi_concentrations = phantom['FeatureProperties']['Concentrations']
    ntubes = len(phantom['Features']['Tubes'])

    # Per tube ROI Analysis within phantom:
    #   Align phantom description to images and identify tubes
    #   nist_tube_segments returns rois for manufacturer adc only if available
    roi_masks, trace_rois, _ = nist_tube_segments(ds, slice_, phantom)

    # Fit the NLLSQ adc model to the trace rois on a pixel by pixel basis
    # The m0 values constitute a fitted "b0";
    # the adc values are already scaled by the conventional factor 10^6
    m0_rois, adc_rois = zip(*[
        adc_nllsq(bvalues, trace_roi, roi_mask)
        for (trace_roi, roi_mask) in zip(trace_rois, roi_masks)
    ])

    # Refine the masks based on both the adc_map and b0
    # TODO (RHD): maybe make refine_tube_mask() take the adc map as well?
    b0_rois = [trace_roi[0] for trace_roi in trace_rois]
    roi_masks = [
        roi_mask if adc_roi[roi_mask].std() < 0.075*adc_roi[roi_mask].mean() else refine_tube_mask(roi_mask, b0_roi)
        for (roi_mask, b0_roi, adc_roi) in zip(roi_masks, b0_rois, adc_rois)
    ]

    # ADC summary statistics of the ROIs; nb use refined mask and
    # trimmed means for robustness
    m0_values = [
        trimboth(m0_roi[mask], 0.05).mean()
        for m0_roi, mask in zip(m0_rois, roi_masks)
    ]
    adc_values = [
        trimboth(adc_roi[mask], 0.05).mean()
        for adc_roi, mask in zip(adc_rois, roi_masks)
    ]
    adc_errors = [
        trimboth(adc_roi[mask], 0.05).std()
        for adc_roi, mask in zip(adc_rois, roi_masks)
    ]

    # Collect trace valid trace values as vectors
    trace_scatters = [
        [np.ma.masked_where(~roi_mask, trace_roi_bval).compressed() for trace_roi_bval in trace_roi]
        for trace_roi, roi_mask in zip(trace_rois, roi_masks)
    ]

    # Collect the fitting parameters in all the valid pixels as vectors
    flat_m0_rois, flat_adc_rois = zip(*[
        (
            np.ma.masked_where(~roi_mask, m0_roi).compressed(),
            np.ma.masked_where(~roi_mask, adc_roi).compressed()
        )
        for m0_roi, adc_roi, roi_mask in zip(m0_rois, adc_rois, roi_masks)
    ])

    # An axis grid fine enough for different no. of tubes at each concentration
    nconcs = len(set(roi_concentrations))
    samples_per_conc = Counter(roi_concentrations)
    max_samples_per_conc = samples_per_conc.most_common(1)[0][1]
    nconcs = len(samples_per_conc)
    mrows, ncols = nconcs, np.lcm.reduce(list(samples_per_conc.values()))
    fig = plt.figure(figsize=(4*max_samples_per_conc, 4*nconcs))

    # Flat list of axes matching list of tubes
    gs = plt.GridSpec(mrows, ncols, fig)
    axs = []
    for row, (conc, nsamples) in enumerate(samples_per_conc.items()):
        width = ncols // nsamples
        axsrow = [
            fig.add_subplot(gs[row, i*width:(i+1)*width])
            for i in range(nsamples)
        ]
        for ax in axsrow[1:]:
            ax.sharey(axsrow[0])
            for tl in ax.get_yticklabels():
                tl.set_visible(False)

        axsrow[0].set_ylabel('Signal (log scale)')
        for ax in axsrow:
            ax.set_yscale('log')
            if row < nconcs - 1:
                for tl in ax.get_xticklabels():
                    tl.set_visible(False)
            else:
                ax.set_xlabel(r'b value $(s/mm^2)$')
        axs += axsrow

    # Choose reasonable y limits for a log scale common across all plots
    lower_ylim = 10 ** np.ceil(np.log10(
        np.clip(min(x.min() for ts in trace_scatters for x in ts), 1, 100)
    ))
    upper_ylim = np.clip(
        max(
            max(m0.max() for m0 in m0_values),
            max(x.max() for ts in trace_scatters for x in ts),
        ),
        100, 100_000
    )
    for ax in axs:
        ax.grid(True)
        ax.set_ylim([lower_ylim, upper_ylim])

    # Plot per pixel fits as pseudo "density" plots
    for ax, flat_m0_roi, flat_adc_roi in zip(axs, flat_m0_rois, flat_adc_rois):
        bs = np.arange(0, 1.05*bvalues[-1], 10, dtype=int)
        ax.plot(
            bs, flat_m0_roi[0]*np.exp(-flat_adc_roi[0]*bs*1e-6),
            alpha=0.05, color='indianred', label='Per-pixel Fits'
        )
        for m0, adc in zip(flat_m0_roi[1:], flat_adc_roi[1:]):
            # NB we have to undo the conventional factor of 10^6 at this point
            ax.plot(bs, m0*np.exp(-adc*bs*1e-6), alpha=0.05, color='indianred')

    # Plot trace pixel values
    for ax, trace_scatter, in zip(axs, trace_scatters):
        ax.boxplot(
            trace_scatter,
            positions=bvalues.astype(int), notch=False, widths=40,
            boxprops=dict(alpha=0.8),
            whiskerprops=dict(alpha=0.8),
            flierprops=dict(markeredgecolor='seagreen', alpha=0.15)
        )

    # Show inset image of fitted adc map
    for ax, adc_roi, mask in zip(axs, adc_rois, roi_masks):
        # Common colour scale: a plausible range of ADC values
        vmin, vmax = 0, 2500
        axins = ax.inset_axes([0.0, 0.15, 0.35, 0.35])
        axins.axis(False)
        # Square root normalization gives better visualisation of dynamic range of adc values
        axins.imshow(
            np.ma.masked_where(~mask, adc_roi),
            norm=PowerNorm(gamma=0.5, vmin=vmin, vmax=vmax), cmap='viridis'
        )

    # Title subplots by PVP concentration in the tubes
    for i, (ax, conc) in enumerate(zip(axs, roi_concentrations), 1):
        ax.set_title(f"Tube {i}: {str(conc) +'%PVP w/w' if conc > 0 else 'Water Only'}")

    # Draw the average fit line and label subplots with the average ADC estimates
    for ax, m0_value, adc_value, adc_error in zip(axs, m0_values, adc_values, adc_errors):
        bs = np.arange(0, 1.05*bvalues[-1], 10, dtype=int)
        ax.plot(
            bs, m0_value*np.exp(-adc_value*bs*1e-6), alpha=0.8,
            linestyle='dotted', color='black', label='Average Fit'
        )
        ax.text(
            0.05, 0.05,
            f"Mean ADC: ${int(adc_value)} \\pm {int(adc_error)}$", transform=ax.transAxes
        )
        # Fix legend placement on RHS avoiding data
        last_point = m0_value*np.exp(-adc_value*bs[-1]*1e-6)
        legend_loc = 'upper right' if (last_point**2 < lower_ylim*upper_ylim) else 'lower right'
        legend = ax.legend(loc=legend_loc)
        # Remove alpha from legend lines
        # NB: the name of this attribute changed over mpl 3.7-3.9 for pep8 conformance
        for lh in getattr(legend, 'legend_handles', getattr(legend, 'legendHandles', [])):
            lh.set_alpha(1)

    fig.suptitle(
        f"NIST ADC Fitting [{ds.attrs['sequence']}:{ds.attrs['orientation']}]",
        fontsize=20
    )

    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95])

    # Summary DataFrame
    df = pd.DataFrame({
        'Concentration': roi_concentrations,
        'NLLSQ_Mean': adc_values,
        'NLLSQ_StdDev': adc_errors,
    }, index=range(1, ntubes + 1))

    return df
