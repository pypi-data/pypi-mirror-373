from pytest import approx

import sys
from glob import glob
from os.path import join

import numpy as np
from hashlib import sha1

from pydicom import dcmread

sys.path.insert(0, '..')
from mriqa import fbirn


mosaic_test_file = 'test-data/fbirn/siemens/dicom/006D5BAD.dcm'
mosaic_test_series = 'test-data/fbirn/siemens/dicom'

hybrid_test_file = 'test-data/fbirn/siemensxa/dicom/00300.dcm'
hybrid_test_series = 'test-data/fbirn/siemensxa/dicom'

multiframe_test_file = 'test-data/fbirn/philips/dicom/MR098EEEC6.dcm'
multiframe_test_series = 'test-data/fbirn/philips/dicom'

singleframe_test_file = 'test-data/fbirn/ge/dicom/MR23AD61F1.dcm'
singleframe_test_series = 'test-data/fbirn/ge/dicom'


def read_dicom_objs_time_sorted(directory='.', filespecorlist='*'):
    """
    Read an fmri time series in mosaic/multiframe/single form from files.

    Each file is either one time point, the whole series or a single image.

    Returns a list of dicom objects (with only one item in case of multifame)
    sorted appropriately

    Parameters
    ----------
    directory :
        Name of directory containing dicom files.
    filespec :
        Glob specification (or list of specs) to match files to read

    Returns
    -------
    list : list of dicom objects soorted by acquisition time
    """

    # Allow single or multiple glob patterns
    if isinstance(filespecorlist, str):
        filespecorlist = [filespecorlist]

    # Remove any duplicates with set()
    files = set(
        f
        for pattern in filespecorlist
        for f in glob(join(directory, pattern))
    )
    if len(files) < 1:
        raise ValueError(
            "No files found for %s, %s", (directory, filespecorlist)
        )

    # Read files as a list of pydicom dicom objects
    dobjs = [dcmread(f) for f in files]
    assert len(dobjs) > 0

    try:
        return fbirn.dicom_objs_sorted_on_time(dobjs)
    except ValueError as e:
        raise ValueError(str(e) + '[%s, %s]' % (directory, filespecorlist))


def read_time_series(directory='.', filespecorlist='*'):
    dobjs = read_dicom_objs_time_sorted(directory, filespecorlist)
    return fbirn.time_series_generic(dobjs)


stacks_mosaic, dims_mosaic = read_time_series(mosaic_test_series, '*.dcm')


def test_multiframe_ndims():
    assert fbirn.multiframe_ndims(dcmread(multiframe_test_file)) == 3
    assert fbirn.multiframe_ndims(dcmread(hybrid_test_file)) == 3


def test_multiframe_shape():
    assert fbirn.multiframe_shape(dcmread(multiframe_test_file)) == (1, 27, 600)
    assert fbirn.multiframe_shape(dcmread(hybrid_test_file)) == (1, 31, 1)


def test_is_mosaic():
    assert fbirn.is_mosaic(dcmread(mosaic_test_file))
    assert not fbirn.is_mosaic(dcmread(multiframe_test_file))
    assert not fbirn.is_mosaic(dcmread(singleframe_test_file))
    assert not fbirn.is_mosaic(dcmread(hybrid_test_file))


def test_acquisition_time_seconds():
    assert fbirn.acquisition_time_seconds(dcmread(singleframe_test_file)) == approx(150558.0)
    assert fbirn.acquisition_time_seconds(dcmread(mosaic_test_file)) == approx(191123.0925)
    assert fbirn.acquisition_time_seconds(dcmread(multiframe_test_file)) == approx(417459833.26)
    assert fbirn.acquisition_time_seconds(dcmread(hybrid_test_file)) == approx(600785611.3175)


def test_stack_from_mosaic():
    dcmobj = dcmread(mosaic_test_file)
    _NumberOfImagesInMosaic = 0x0019, 0x100a
    nimages = int(dcmobj[_NumberOfImagesInMosaic].value)
    stack = fbirn.stack_from_mosaic(dcmobj, nimages)
    # Right shape
    assert stack.shape == (27, 64, 64)
    # No empty slices
    assert all(np.sum(np.abs(stack), axis=(1, 2)) > 0)


def test_quadratic_trend():
    x = np.linspace(-10, 10, 100)
    y = 3.0 * x**2 + 4.0 * x + 2.0 + np.random.normal(loc=0.0, scale=0.1, size=len(x))
    y_orig = y.copy()

    yy = fbirn.quadratic_trend(y)
    assert np.abs(np.mean(yy - y)) < 0.01
    assert 0.05 < np.std(yy - y) < 0.2
    assert np.allclose(y, y_orig)


def test_detrend_quadratic0():
    x = np.linspace(-10, 10, 100)
    y = -5.0 * x**2 + 3.0 * x + 2.0 + np.random.normal(loc=0.0, scale=0.1, size=len(x))
    y_orig = y.copy()

    yy = fbirn.detrend_quadratic(y)
    assert np.abs(np.mean(yy)) < 0.01
    assert 0.05 < np.std(yy) < 0.2
    assert np.allclose(y, y_orig)


def test_detrend_quadratic1():
    def _detrend_quadratic_simple(y):
        x = np.arange(len(y))
        return y - np.polyval(np.polyfit(x, y, deg=2), x)

    x = np.linspace(-10, 10, 100)
    y = -5.0 * x**2 + 3.0 * x + 2.0 + np.random.normal(loc=0.0, scale=0.1, size=len(x))
    y_orig = y.copy()
    yyref = _detrend_quadratic_simple(y)
    yy = fbirn.detrend_quadratic(y)
    assert yy.shape == yyref.shape
    assert yy.dtype == yyref.dtype
    assert np.allclose(yy, yyref)
    assert np.allclose(y, y_orig)


def test_detrend_quadratic2():
    def _detrend_quadratic_simple(y):
        x = np.arange(len(y))
        return y - np.polyval(np.polyfit(x, y, deg=2), x)

    x = np.linspace(-10, 10, 100)

    y = np.array([
        ((-5.0 + 0.1 * k) * x**2 + 3.0 * x + 2.0)
        for k in range(5)
    ]).T
    y += np.random.normal(loc=0.0, scale=0.1, size=y.shape)
    y_orig = y.copy()

    yyref = np.zeros_like(y)
    for i in range(5):
        yyref[:, i] = _detrend_quadratic_simple(y[:, i])

    yy = fbirn.detrend_quadratic(y)
    assert yy.shape == yyref.shape
    assert yy.dtype == yyref.dtype
    assert np.allclose(yy, yyref)
    assert np.allclose(y, y_orig)


def test_detrend_quadratic3():
    def _detrend_quadratic_simple(y):
        x = np.arange(len(y))
        return y - np.polyval(np.polyfit(x, y, deg=2), x)

    x = np.linspace(-10, 10, 100)
    y = np.array([
        [((-5.0 + 0.1 * k) * x**2 + (3.0 + 0.1 * j) * x + 2.0) for k in range(5)]
        for j in range(5)
    ]).T

    y += np.random.normal(loc=0.0, scale=0.1, size=y.shape)
    y_orig = y.copy()

    yyref = np.zeros_like(y)
    for i in range(5):
        for j in range(5):
            yyref[:, i, j] = _detrend_quadratic_simple(y[:, i, j])

    yy = fbirn.detrend_quadratic(y)
    assert yy.shape == yyref.shape
    assert yy.dtype == yyref.dtype
    assert np.allclose(yy, yyref)
    assert np.allclose(y, y_orig)


def test_detrend_quadratic4():
    def _detrend_quadratic_simple(y):
        x = np.arange(len(y))
        return y - np.polyval(np.polyfit(x, y, deg=2), x)

    x = np.linspace(-10, 10, 100)
    x = np.linspace(-10, 10, 100)
    y = np.array([
        [[((-5.0 + 0.1 * k) * x**2 + (3.0 + 0.1 * j) * x + (2.0 + i)) for k in range(5)] for j in range(5)]
        for i in range(5)
    ]).T
    y += np.random.normal(loc=0.0, scale=0.1, size=y.shape)
    y_orig = y.copy()

    yyref = np.zeros_like(y)
    for i in range(5):
        for j in range(5):
            for k in range(5):
                yyref[:, i, j, k] = _detrend_quadratic_simple(y[:, i, j, k])

    yy = fbirn.detrend_quadratic(y)
    assert yy.shape == yyref.shape
    assert yy.dtype == yyref.dtype
    assert np.allclose(yy, yyref)
    assert np.allclose(y, y_orig)


def test_time_series_generic():
    stacks, (dx, dy, dz, dt) = fbirn.time_series_generic(
        read_dicom_objs_time_sorted(singleframe_test_series, '*.dcm')
    )
    assert stacks.shape == (512, 19, 64, 64)
    assert stacks.dtype == np.float64
    assert dx == approx(3.4375, abs=1e-5)
    assert dy == approx(3.4375, abs=1e-5)
    assert dz == approx(8.0, abs=1e-5)
    assert dt == approx(2.0, abs=1e-5)

    stacks, (dx, dy, dz, dt) = fbirn.time_series_generic(
        read_dicom_objs_time_sorted(mosaic_test_series, '*.dcm')
    )
    assert stacks.shape == (512, 27, 64, 64)
    assert stacks.dtype == np.float64
    assert dx == approx(3.4375, abs=1e-5)
    assert dy == approx(3.4375, abs=1e-5)
    assert dz == approx(5.0,    abs=1e-5)
    assert dt == approx(2.0,    abs=1e-5)

    stacks, (dx, dy, dz, dt) = fbirn.time_series_generic(
        read_dicom_objs_time_sorted(multiframe_test_series, '*.dcm')
    )
    assert stacks.shape == (600, 27, 64, 64)
    assert stacks.dtype == np.float64
    assert dx == approx(3.4375, abs=1e-5)
    assert dy == approx(3.4375, abs=1e-5)
    assert dz == approx(5.5,    abs=1e-5)
    assert dt == approx(2.0,    abs=1e-5)

    stacks, (dx, dy, dz, dt) = fbirn.time_series_generic(
        read_dicom_objs_time_sorted(hybrid_test_series, '*.dcm')
    )
    assert stacks.shape == (600, 31, 64, 64)
    assert stacks.dtype == np.float64
    assert dx == approx(3.4375, abs=1e-5)
    assert dy == approx(3.4375, abs=1e-5)
    assert dz == approx(5.0,    abs=1e-5)
    assert dt == approx(2.0,    abs=1e-5)


# TODO: how do we test we've got the right bit in the phantom?
def test_get_roi():
    roisize = 21
    stacks = stacks_mosaic
    central_slice_time_series = stacks[:, 20, :, :]
    roi = fbirn.get_roi(central_slice_time_series, roisize)
    nt, ny, nx = len(stacks), roisize, roisize
    assert roi.shape == (nt, ny, nx)


def test_signal_image():
    stacks = stacks_mosaic
    central_slice_time_series = stacks[:, 25, :, :]
    signal = fbirn.signal_image(central_slice_time_series)
    assert sha1(signal).hexdigest() == '674bc8c72749a271ec103ab1ff5100e266957301'


"""
def test_temporalnoise_fluct_image():
    stacks = stacks_mosaic
    central_slice_time_series = stacks[:, 25, :, :]
    tnf = fbirn.temporalnoise_fluct_image(central_slice_time_series)
    assert sha1(tnf).hexdigest() == '026bd055d4178d7c55ee32b574403be49b985560'


def test_sfnr_image():
    stacks = stacks_mosaic
    central_slice_time_series = stacks[:, 25, :, :]
    sfnr = fbirn.sfnr_image(central_slice_time_series)
    assert sha1(sfnr).hexdigest() == 'a638597afaee858c50158a421e355bcb90948867'
"""


def test_sfnr_summary():
    stacks = stacks_mosaic
    central_slice_time_series = stacks[:, 25, :, :]
    sfnr = fbirn.sfnr_summary(central_slice_time_series)
    assert sfnr == approx(719.805593640793)


"""
def test_static_spatial_noise_image():
    stacks = stacks_mosaic
    central_slice_time_series = stacks[:, 25, :, :]
    diff_image = fbirn.static_spatial_noise_image(central_slice_time_series, mask_background=True)
    assert sha1(diff_image).hexdigest() == '03912ce66c0751e170f43892f91f2964be9376f2'
"""


def test_snr_summary():
    stacks = stacks_mosaic
    snr = fbirn.snr_summary(stacks[:, 25, :, :])
    assert snr == approx(818.186281422362)


def test_fluctuation_and_drift():
    stacks = stacks_mosaic
    sd_resids, percent_fluct, drift_raw, drift_fit = fbirn.fluctuation_and_drift(stacks[:, 25, :, :])
    assert sd_resids == approx(0.8377229909631426)
    assert percent_fluct == approx(0.030419931156640368)
    assert drift_raw == approx(0.519740060879808)
    assert drift_fit == approx(0.4068364561641941)


def test_magnitude_spectrum():
    stacks = stacks_mosaic
    fbirn.magnitude_spectrum(stacks[:, 25, :, :])


def test_weisskoff():
    stacks = stacks_mosaic
    roc, covs = fbirn.weisskoff(stacks[:, 25, :, :])


def test_centre_of_mass():
    stacks = stacks_mosaic
    c_of_ms = fbirn.centre_of_mass(stacks)

    assert tuple(np.mean(c_of_ms, axis=0)) == approx((32.187927, 32.35453, 13.748175), rel=1e-3)
    assert tuple(np.std(c_of_ms, axis=0)) == approx((0.005507, 0.011421, 0.006574), rel=1e-3)


def test_phantom_mask_2d():
    image = dcmread(mosaic_test_file).pixel_array
    mask = fbirn.phantom_mask_2d(image)
    assert mask.dtype == bool
    assert mask.shape == image.shape


def test_ghost_mask():
    mask = fbirn.phantom_mask_2d(dcmread(mosaic_test_file).pixel_array)
    gmask = fbirn.ghost_mask(mask)
    assert gmask.dtype == bool
    assert gmask.shape == mask.shape
    gmask = fbirn.ghost_mask(mask, pe_axis='row')
    assert gmask.dtype == bool
    assert gmask.shape == mask.shape


def test_volume_ghostiness():
    timeseries = stacks_mosaic
    pmean, gmean, bright_gmean, snr = fbirn.volume_ghostiness(timeseries[0])
    pmean, gmean, bright_gmean, snr = fbirn.volume_ghostiness(timeseries[0], pe_axis='row')


def test_ghostiness_trends():
    timeseries = stacks_mosaic
    pmeans, gmeans, bright_gmeans, snrs = fbirn.ghostiness_trends(timeseries)
    """
    timeseries, (dx, dy, dz, dt) = read_time_series(multiframe_test_series, '*.dcm')
    pmeans, gmeans, bright_gmeans, snrs = fbirn.ghostiness_trends(timeseries)

    timeseries, (dx, dy, dz, dt) = read_time_series(singleframe_test_series, ['*'])
    pmeans, gmeans, bright_gmeans, snrs = fbirn.ghostiness_trends(timeseries)

    timeseries, (dx, dy, dz, dt) = read_time_series(hybrid_test_series, ['*'])
    pmeans, gmeans, bright_gmeans, snrs = fbirn.ghostiness_trends(timeseries)
    """


def test_phantom_mask_3d():
    # timeseries, (dx, dy, dz, dt) = read_time_series(hybrid_test_series, '*.dcm')
    timeseries = stacks_mosaic
    mask = fbirn.phantom_mask_3d(np.sum(timeseries, axis=0))
    assert mask.dtype == bool
    assert mask.shape == timeseries.shape[1:]


def test_smoothness_along_axis():
    # timeseries, (dx, dy, dz, dt) = read_time_series(mosaic_test_series, ['*'])
    timeseries, (dx, dy, dz, _) = stacks_mosaic, dims_mosaic
    fwhmx = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 2, dx)
    fwhmy = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 1, dy)
    fwhmz = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 0, dz)
    assert fwhmx == approx(8.65145, rel=1e-3)
    assert fwhmy == approx(9.20998, rel=1e-3)
    assert fwhmz == approx(37.8051, rel=1e-3)

    """
    timeseries, (dx, dy, dz, _) = read_time_series(multiframe_test_series, ['*'])
    fwhmx = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 2, dx)
    fwhmy = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 1, dy)
    fwhmz = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 0, dz)
    assert fwhmx == approx(11.34925, rel=1e-3)
    assert fwhmy == approx(11.53056, rel=1e-3)
    assert fwhmz == approx(14.16524, rel=1e-3)

    timeseries, (dx, dy, dz, _) = read_time_series(singleframe_test_series, ['*'])
    fwhmx = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 2, dx)
    fwhmy = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 1, dy)
    fwhmz = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 0, dz)
    assert fwhmx == approx(12.75856, rel=1e-3)
    assert fwhmy == approx(12.89833, rtel=1e-3)
    assert fwhmz == approx(fwhmz, 16.42438, rel=1e-3)
    """
    # Currently broken with existing test data
    """
    timeseries, (dx, dy, dz, dt) = read_time_series(hybrid_test_series, ['*'])
    fwhmx = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 2, dx)
    fwhmy = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 1, dy)
    fwhmz = fbirn.smoothness_along_axis(timeseries[len(timeseries)//2], 0, dz)
    assert fwhmx == approx(0, abs=1e-3)
    assert fwhmy == approx(0, abs=1e-3)
    assert fwhmz == approx(0, abs=1e-3)
    """


def test_fwhm_smoothness_xyz():
    timeseries, (dx, dy, dz, _) = stacks_mosaic, dims_mosaic
    fwhmx, fwhmy, fwhmz = fbirn.fwhm_smoothness_xyz(timeseries, (dx, dy, dz))

    """
    timeseries, (dx, dy, dz, _) = read_time_series(multiframe_test_series, ['*'])
    fwhmx, fwhmy, fwhmz = fbirn.fwhm_smoothness_xyz(timeseries, (dx, dy, dz))

    timeseries, (dx, dy, dz, _) = read_time_series(singleframe_test_series, ['*'])
    fwhmx, fwhmy, fwhmz = fbirn.fwhm_smoothness_xyz(timeseries, (dx, dy, dz))
    """
    # Currently broken with existing test data
    """
    timeseries, (dx, dy, dz, _) = read_time_series(hybrid_test_series, ['*'])
    fwhmx, fwhmy, fwhmz = fbirn.fwhm_smoothness_xyz(timeseries, (dx ,dy, dz))
    """


def test_fwhm_smoothness_xyz_preprocessed():
    timeseries, (dx, dy, dz, _) = stacks_mosaic, dims_mosaic
    fwhmx, fwhmy, fwhmz = fbirn.fwhm_smoothness_xyz_preprocessed(timeseries, (dx, dy, dz))
    assert sum(fwhmx > 0) > 0.98 * len(fwhmx)
    assert sum(fwhmy > 0) > 0.90 * len(fwhmy)
    assert sum(fwhmz > 0) > 0.80 * len(fwhmz)

    """
    timeseries, (dx, dy, dz, _) = read_time_series(multiframe_test_series, ['*'])
    fwhmx, fwhmy, fwhmz = fbirn.fwhm_smoothness_xyz_preprocessed(timeseries, (dx, dy, dz))
    assert sum(fwhmx > 0) > 0.98 * len(fwhmx))
    assert sum(fwhmy > 0) > 0.90 * len(fwhmy))
    # NB TODO: something odd at the start and the end in the Philips data
    assert sum(fwhmz > 0) > 0.50 * len(fwhmz))

    timeseries, (dx, dy, dz, _) = read_time_series(singleframe_test_series, ['*'])
    fwhmx, fwhmy, fwhmz = fbirn.fwhm_smoothness_xyz_preprocessed(timeseries, (dx, dy, dz))
    assert sum(fwhmx > 0) > 0.98 * len(fwhmx))
    assert sum(fwhmy > 0) > 0.90 * len(fwhmy))

    # NB TODO: lots of erratic drop out in the GE data
    assert sum(fwhmz > 0) > 0.35 * len(fwhmz))
    """
    # Currently broken with existing test data
    """
    timeseries, (dx, dy, dz, _) = read_time_series(hybrid_test_series, ['*'])
    fwhmx, fwhmy, fwhmz = fbirn.fwhm_smoothness_xyz_preprocessed(timeseries, (dx ,dy, dz))
    assert sum(fwhmx > 0) > 0.98 * len(fwhmx)
    assert sum(fwhmy > 0) > 0.98 * len(fwhmy)
    assert sum(fwhmz > 0) > 0.90 * len(fwhmz)
    """
