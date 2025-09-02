from pytest import fixture, approx
import numpy as np
from pydicom import dcmread

import sys
sys.path.append('..')

from mriqa import phantoms
from mriqa.dcmio import pix_spacing_yx, phase_enc_dirn

scans = {}


@fixture(scope='module', autouse=True)
def setup():
    global scans
    scans['ge_scout'] = dcmread('test-data/ge-scout.dcm')

    scans['philips_se'] = dcmread('test-data/philips-se.dcm')
    scans['philips_tse'] = dcmread('test-data/philips-tse.dcm')
    scans['philips_epi'] = dcmread('test-data/philips-epi.dcm')
    scans['philips_epse'] = dcmread('test-data/philips-epse.dcm')

    scans['siemens_scout'] = dcmread('test-data/siemens-scout.dcm')

    scans['longbottle_uniform'] = dcmread('test-data/longbottle/signal_normalised/a/00001.dcm')


def test_find_phantom():
    dobj = scans['longbottle_uniform']
    image = dobj.pixel_array & 0x0fff
    pix_dims = pix_spacing_yx(dobj)
    expected_diameter = phantoms.SIEMENSLONGBOTTLE['Diameter'] / 2 / pix_dims[0]
    centre_x, centre_y, radius = phantoms.find_phantom(image, expected_diameter)

    assert (centre_x, centre_y) == (128, 126)
    assert radius == approx(68, abs=1e-7)

    # check find correct radius and centre for long bottle, acr nema and doh


def test_phantom_mask_2d():
    dobj = scans['longbottle_uniform']
    image = dobj.pixel_array & 0x0fff
    ny, nx = image.shape

    mode_none_mask = phantoms.phantom_mask_2d(image)
    mode_erode_mask = phantoms.phantom_mask_2d(image, mode='Erode')
    mode_dilate_mask = phantoms.phantom_mask_2d(image, mode='Dilate')

    # erosion/dilation work
    assert np.sum(mode_erode_mask) < np.sum(mode_none_mask) < np.sum(mode_dilate_mask)
    # centre in
    assert mode_erode_mask[ny//2, nx//2]
    # edges out
    assert ~mode_dilate_mask[0, 0]
    assert ~mode_dilate_mask[0, -1]
    assert ~mode_dilate_mask[-1, 0]
    assert ~mode_dilate_mask[-1, -1]

    # most of image intensity in phantom mask
    assert np.sum(mode_none_mask * image) > 0.95 * np.sum(image)


def test_noise_background_mask_2d():
    dobj = scans['longbottle_uniform']
    image = dobj.pixel_array & 0x0fff
    ny, nx = image.shape
    mask = phantoms.noise_background_mask_2d(image, phase_encoding=phase_enc_dirn(dobj))

    # check mask is False in centre of image
    assert ~mask[ny//2, nx//2]

    # check mask includes only a small fraction of intensity in image
    assert np.sum(mask * image) < 0.025 * np.sum(image)

    # check mask is false in a central strip along the phase encoding axis
    pestrip = mask[ny//2-5:ny//2+5, :] if phase_enc_dirn(dobj) == 'ROW' else mask[:, nx//2-5:nx//2+5]
    assert np.sum(pestrip) == 0


def test_circular_mask():
    dobj = scans['longbottle_uniform']
    image = dobj.pixel_array
    ny, nx = image.shape
    centre_x, centre_y = nx/2, ny/2
    radius = 0.75 * (nx + ny) / 4
    mask = phantoms.circular_mask(image, radius, centre_x, centre_y)
    assert mask[ny//2-2:ny//2+2, nx//2-2:nx//2+2].all()
    assert not mask[:2, :].any()
    assert not mask[-2:, :].any()
    assert not mask[:, :2].any()
    assert not mask[:, -2:].any()


def test_rectangular_mask():
    dobj = scans['longbottle_uniform']
    image = dobj.pixel_array
    ny, nx = image.shape
    xa, xb = 0.25 * nx, 0.75 * nx
    ya, yb = 0.25 * ny, 0.75 * ny
    mask = phantoms.rectangular_mask(image, xa, xb, ya, yb)
    assert mask[ny//2-2:ny//2+2, nx//2-2:nx//2+2].all()
    assert not mask[:2, :].any()
    assert not mask[-2:, :].any()
    assert not mask[:, :2].any()
    assert not mask[:, -2:].any()
