#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""uniformity.py: graphical reports of QA uniformity parameters."""

from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt

from .. phantoms import OILSPHERE

from .. dcmio import (
    approx_phase_orientation, approx_slice_orientation, phase_enc_dirn,
    seq_name, protocol_name, series_number
)

from .. tools import (
    add_phase_encode_mark, uniformity_ipem80, uniformity_nema, mean_im, rx_coil_string
)


def uniformity_report(raw_dobjs, psn_dobjs=None, raw_dobjsb=None, psn_dobjsb=None, phantom=OILSPHERE, coil=None, frame=None):
    """
    Report on uniformity in head coil.

    Based on images of a spherical oil filled phantom.

    """
    raw_dobjs = sorted(raw_dobjs, key=approx_slice_orientation)
    orientations = [approx_slice_orientation(d) for d in raw_dobjs]
    if psn_dobjs is not None:
        assert len(raw_dobjs) == len(psn_dobjs)
        psn_dobjs = sorted(psn_dobjs, key=approx_slice_orientation)
        assert [approx_slice_orientation(d) for d in psn_dobjs] == orientations

    if raw_dobjsb is not None:
        assert len(raw_dobjsb) == len(raw_dobjs)
        raw_dobjsb = sorted(raw_dobjsb, key=approx_slice_orientation)
        assert [approx_slice_orientation(d) for d in raw_dobjsb] == orientations

        if psn_dobjsb is not None:
            assert len(psn_dobjsb) == len(raw_dobjsb)
            psn_dobjsb = sorted(psn_dobjsb, key=approx_slice_orientation)
            assert [approx_slice_orientation(d) for d in psn_dobjsb] == orientations

    if len(set(orientations)) < len(orientations):
        raise ValueError(f'Duplicate slice orientations not allowed: {dict(Counter(orientations))}')

    df = pd.DataFrame(index=pd.Index(orientations, name='Orientation'))

    if raw_dobjsb is not None:
        # Profiles and Uniformity
        # Pairs of images
        (
            df['XProfileRaw'],
            df['XUniformityRaw'],
            df['YProfileRaw'],
            df['YUniformityRaw']
        ) = zip(*[
            uniformity_ipem80(dobja, dobjb)
            for (dobja, dobjb) in zip(raw_dobjs, raw_dobjsb)
        ])
    else:
        # Profiles and Uniformity
        # Single images or multiframes
        (
            df['XProfileRaw'],
            df['XUniformityRaw'],
            df['YProfileRaw'],
            df['YUniformityRaw']
        ) = zip(*[uniformity_ipem80(dobj) for dobj in raw_dobjs])

    if psn_dobjs is not None and psn_dobjsb is not None:
        (
            df['XProfileNorm'],
            df['XUniformityNorm'],
            df['YProfileNorm'],
            df['YUniformityNorm']
        ) = zip(*[
            uniformity_ipem80(dobja, dobjb)
            for (dobja, dobjb) in zip(psn_dobjs, psn_dobjsb)
        ])
    elif psn_dobjs is not None:
        (
            df['XProfileNorm'],
            df['XUniformityNorm'],
            df['YProfileNorm'],
            df['YUniformityNorm']
        ) = zip(*[uniformity_ipem80(dobj) for dobj in psn_dobjs])

    # ACR Uniformity Figure
    if raw_dobjsb is not None:
        df['NEMAUniformityRaw'] = [
            uniformity_nema(dobja, dobjb)
            for (dobja, dobjb) in zip(raw_dobjs, raw_dobjsb)
        ]
    else:
        df['NEMAUniformityRaw'] = [uniformity_nema(dobj) for dobj in raw_dobjs]

    if psn_dobjs is not None and psn_dobjsb is not None:
        df['NEMAUniformityNorm'] = [
            uniformity_nema(dobja, dobjb)
            for (dobja, dobjb) in zip(psn_dobjs, psn_dobjsb)
        ]
    elif psn_dobjs is not None:
        df['NEMAUniformityNorm'] = [uniformity_nema(dobj) for dobj in psn_dobjs]

    # Series details (assume matched if second images specified)
    df['SeriesRaw'] = [series_number(dobj) for dobj in raw_dobjs]
    df['ProtocolRaw'] = [protocol_name(dobj) for dobj in raw_dobjs]
    df['SequenceRaw'] = [seq_name(dobj) for dobj in raw_dobjs]
    df['OrientRaw'] = [
        approx_slice_orientation(dobj) + '/' + approx_phase_orientation(dobj)
        for dobj in raw_dobjs
    ]
    df['CoilRaw'] = [rx_coil_string(dobj, coil) for dobj in raw_dobjs]

    if psn_dobjs is not None:
        df['SeriesNorm'] = [series_number(dobj) for dobj in psn_dobjs]
        df['ProtocolNorm'] = [protocol_name(dobj) for dobj in psn_dobjs]
        df['SequenceNorm'] = [seq_name(dobj) for dobj in psn_dobjs]
        df['OrientNorm'] = [
            approx_slice_orientation(dobj) + '/' + approx_phase_orientation(dobj)
            for dobj in psn_dobjs
        ]
        df['CoilNorm'] = [rx_coil_string(dobj, coil) for dobj in psn_dobjs]

    ncols = 4 if psn_dobjs is not None else 3
    fig, axs = plt.subplots(len(df), ncols, figsize=(4*ncols, 4*len(df)))
    if len(df) == 1:
        axs = axs[None, :]
    for i, (index, _) in enumerate(df.iterrows()):
        if raw_dobjsb is not None:
            axs[i, 0].imshow(mean_im(raw_dobjs[i], raw_dobjsb[i]), cmap='gray')
        else:
            axs[i, 0].imshow(mean_im(raw_dobjs[i], raw_dobjs[i]), cmap='gray')
        axs[i, 0].grid(False)
        axs[i, 0].axis('image')
        axs[i, 0].axis('off')
        axs[i, 0].set_title(
            r'Series %d, Image %d (Raw)' %
            (series_number(raw_dobjs[i]), raw_dobjs[i].InstanceNumber)
        )
        add_phase_encode_mark(axs[i, 0], phase_enc_dirn(raw_dobjs[i]))

        axs[i, 1].plot(
            df['XProfileRaw'][index],
            label='Raw (%3.0f%%)' % df['XUniformityRaw'][index]
        )
        if psn_dobjs is not None:
            axs[i, 1].plot(
                df['XProfileNorm'][index],
                label='Norm (%3.0f%%)' % df['XUniformityNorm'][index]
            )

        axs[i, 1].set_xlabel('Horizontal Pixel Position')
        axs[i, 1].set_ylabel('Image Brightness')
        axs[i, 1].legend()
        axs[i, 1].grid(True)
        axs[i, 1].set_title('%s (Horizontal)' % index)

        axs[i, 2].plot(
            df['YProfileRaw'][index],
            label='Raw (%3.0f%%)' % df['YUniformityRaw'][index]
        )
        if psn_dobjs is not None:
            axs[i, 2].plot(
                df['YProfileNorm'][index],
                label='Norm (%3.0f%%)' % df['YUniformityNorm'][index]
            )
        axs[i, 2].set_xlabel('Vertical Pixel Position')
        axs[i, 2].set_ylabel('Image Brightness')
        axs[i, 2].legend()
        axs[i, 2].grid(True)
        axs[i, 2].set_title('%s (Vertical)' % index)

        if psn_dobjs is not None:
            if psn_dobjsb is not None:
                axs[i, 3].imshow(mean_im(psn_dobjs[i], psn_dobjsb[i]), cmap='gray')
            else:
                axs[i, 3].imshow(mean_im(psn_dobjs[i], psn_dobjs[i]), cmap='gray')
            axs[i, 3].grid(False)
            axs[i, 3].axis('image')
            axs[i, 3].axis('off')
            axs[i, 3].set_title(
                'Series %d, Image %d (Normalised)' %
                (psn_dobjs[i].SeriesNumber, psn_dobjs[i].InstanceNumber)
            )
            add_phase_encode_mark(axs[i, 3], phase_enc_dirn(psn_dobjs[i]))

    fig.suptitle('%s Coil Uniformity' % df['CoilRaw'].iloc[0], fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    return df
