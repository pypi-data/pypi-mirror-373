from pytest import fixture
from pydicom import dcmread
import sys
sys.path.insert(0, '..')

from mriqa import ghosting

scans = {}


@fixture(scope='module', autouse=True)
def setup_function():
    # global ge_scout, philips_se, philips_tse, philips_epi, philips_epse, siemens_scout
    global scans
    scans['ge_scout'] = dcmread('test-data/ge-scout.dcm')

    scans['philips_se'] = dcmread('test-data/philips-se.dcm')
    scans['philips_tse'] = dcmread('test-data/philips-tse.dcm')
    scans['philips_epi'] = dcmread('test-data/philips-epi.dcm')
    scans['philips_epse'] = dcmread('test-data/philips-epse.dcm')

    scans['siemens_scout'] = dcmread('test-data/siemens-scout.dcm')


def test_phantom_mask_2d():
    pass
    # phantom_mask_2d(imagei, dilate=False)


def test_ghost_mask():
    pass


def test_slice_ghostiness():
    pass
