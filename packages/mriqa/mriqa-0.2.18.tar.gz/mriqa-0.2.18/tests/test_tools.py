from pytest import fixture, raises

from pydicom import dcmread

from mriqa import tools, __version__

import numpy as np

import sys
sys.path.append('..')
from mriqa import tools

scans = {}


@fixture(scope='module', autouse=True)
def setup():
    # global scans, ge_scans, philips_scans, siemens_scans
    scans['ge_scout'] = dcmread('test-data/ge-scout.dcm')
    scans['ge_memp'] = dcmread('test-data/ge-memp.dcm')
    scans['ge_fgre'] = dcmread('test-data/ge-fgre.dcm')
    scans['ge_efgre3d'] = dcmread('test-data/ge-efgre3d.dcm')

    scans['philips_se'] = dcmread('test-data/philips-se.dcm')
    scans['philips_tse'] = dcmread('test-data/philips-tse.dcm')
    scans['philips_epi'] = dcmread('test-data/philips-epi.dcm')
    scans['philips_epse'] = dcmread('test-data/philips-epse.dcm')
    scans['philips_std'] = dcmread('test-data/philips-se-std.dcm')

    scans['siemens_scout'] = dcmread('test-data/siemens-scout.dcm')
    scans['siemens_se'] = dcmread('test-data/siemens-se.dcm')
    scans['siemens_vb17_single'] = dcmread('test-data/siemens-vb17-single.dcm')
    scans['siemens_ve11_noise'] = dcmread('test-data/siemens-ve11-noise.dcm')
    scans['siemens_vb17_pca_phase'] = dcmread('test-data/siemens-vb17-pca-phase.dcm')
    scans['siemens_vb17_pca_magn'] = dcmread('test-data/siemens-vb17-pca-magn.dcm')
    scans['siemens_se_dis2d'] = dcmread('test-data/siemens-se-dis2d.dcm')
    scans['siemens_ve11_fid'] = dcmread('test-data/siemens-ve11-fid.dcm')
    scans['siemens_ve11_svs_se'] = dcmread('test-data/siemens-ve11-svs-se.dcm')
    scans['siemens_xa11a_enhanced_se'] = dcmread('test-data/siemens-xa11a-enhanced-se.dcm')
    scans['siemens_xa11a_interop_se'] = dcmread('test-data/siemens-xa11a-interop-se.dcm')


def test_all_ims():
    pass


def test_single_im():
    pass


def test_im_pair_1():
    pair = tools.im_pair(scans['siemens_scout'], scans['siemens_scout'])
    assert len(pair) == 2
    assert all(isinstance(i, np.ndarray) for i in pair)
    assert pair[0].dtype == pair[1].dtype
    assert pair[0].dtype == np.uint16
    assert pair[0].shape == pair[1].shape
    assert pair[0].shape == (512, 512)


def test_im_pair_2():
    with raises(ValueError):
        tools.im_pair(scans['siemens_scout'])


def test_im_pair_3():
    pair = tools.im_pair(scans['philips_epi'])
    assert len(pair) == 2
    assert all(isinstance(i, np.ndarray) for i in pair)
    assert pair[0].dtype == pair[1].dtype
    assert pair[0].dtype == np.uint16
    assert pair[0].shape == pair[1].shape
    assert pair[0].shape == (64, 64)


def test_im_pair_4():
    pair = tools.im_pair(scans['siemens_xa11a_interop_se'], scans['siemens_xa11a_interop_se'])
    assert len(pair) == 2
    assert all(isinstance(i, np.ndarray) for i in pair)
    assert pair[0].dtype == pair[1].dtype
    assert pair[0].dtype == np.uint16
    assert pair[0].shape == pair[1].shape
    assert pair[0].shape == (256, 256)


def test_im_pair_5():
    pair = tools.im_pair(scans['siemens_xa11a_enhanced_se'], scans['siemens_xa11a_enhanced_se'])
    assert len(pair) == 2
    assert all(isinstance(i, np.ndarray) for i in pair)
    assert pair[0].dtype == pair[1].dtype
    assert pair[0].dtype == np.uint16
    assert pair[0].shape == pair[1].shape
    assert pair[0].shape == (256, 256)


def test_mean_im():
    pass


def test_im_at_index():
    pass


def test_diff_im():
    pass


def test_snr_im():
    pass


def test_snr():
    pass


def test_uniformity_ipem80():
    pass


def test__mosaic_single():
    pass


def test_show_mosaic_single():
    # graphical - difficult to test
    pass


def test__mosaic():
    pass


def test_show_mosaic():
    # graphical - difficult to test
    pass


def test__basic_montage():
    pass


def test__philips_multiframe_montage():
    pass


def test__siemens_multiframe_montage():
    pass


def test__montage():
    pass


def test_show_montage():
    # graphical - difficult to test
    pass


def test_normalized_profile():
    pass


def test_profile_params():
    pass


def test_peakdet():
    pass


def test__gaussian_fit():
    pass


def test__refine_peak():
    pass


def test_positive_gradient():
    pass


def test_radial_profiles():
    pass


def test_profile_edges():
    pass


def test_profile_diameters():
    pass


def test_fit_diameters():
    pass


def test_edges_and_diameters():
    pass


def test_naad():
    pass


def test_image_uniformity_nema():
    pass


def test_uniformity_nema():
    pass


def test_watermark():
    wm = tools.watermark()
    expected_keys = [
        'CalculationTime', 'User',
        'PythonVersion', 'Platform',
        'mriqa', 'dcmextras', 'pydicom', 'scipy', 'numpy', 'skimage', 'matplotlib'
    ]
    assert all(k in wm for k in expected_keys)
    assert all(wm.values())
    assert wm['mriqa'] == __version__


def test_rx_coil_string():
    assert tools.rx_coil_string(scans['ge_scout']) == 'C-GE_HEAD'
    assert tools.rx_coil_string(scans['ge_memp']) == 'C-GE_HNS Head'
    assert tools.rx_coil_string(scans['ge_fgre']) == 'C-GE_HNS Head'
    assert tools.rx_coil_string(scans['ge_efgre3d']) == 'C-GE_HNS Head'
    # TODO: Really want to try harder to get something sensible for philips.
    assert tools.rx_coil_string(scans['philips_se']) == 'MULTI COIL'
    assert tools.rx_coil_string(scans['philips_tse']) == 'MULTI COIL'
    assert tools.rx_coil_string(scans['philips_epi']) == 'MULTI COIL'
    assert tools.rx_coil_string(scans['philips_epse']) == 'MULTI COIL'
    assert tools.rx_coil_string(scans['siemens_scout']) == 'Head_32'
    assert tools.rx_coil_string(scans['siemens_se']) == 'Head_32'
    assert tools.rx_coil_string(scans['siemens_vb17_single']) == 'HeadMatrix'
    assert tools.rx_coil_string(scans['siemens_ve11_noise']) == 'HeadNeck_20'
    assert tools.rx_coil_string(scans['siemens_vb17_pca_phase']) == 'C:BO1,2;SP5-7'
    assert tools.rx_coil_string(scans['siemens_vb17_pca_magn']) == 'C:BO1,2;SP5-7'
    assert tools.rx_coil_string(scans['siemens_ve11_fid']) == 'HeadNeck_20'
    assert tools.rx_coil_string(scans['siemens_ve11_svs_se']) == 'HeadNeck_20'
    assert tools.rx_coil_string(scans['siemens_xa11a_enhanced_se']) == 'HeadNeck_20_TCS'
    assert tools.rx_coil_string(scans['siemens_xa11a_interop_se']) == 'HeadNeck_20_TCS'
    assert tools.rx_coil_string(scans['siemens_xa11a_interop_se'], 'OVERRIDE') == 'OVERRIDE'
