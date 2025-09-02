from pytest import fixture, raises, approx
from pydicom import dcmread
from pydicom.datadict import get_private_entry

import numpy as np
import sys

sys.path.append('..')
from mriqa import dcmio


SCANS = {
    'ge_efgre3d': {
        'filename': 'test-data/ge-efgre3d.dcm',
        # Seems to be a bug in pydicom for old GE with explicit group lengths
        # misidentifies group length tag as Private Creator
        # and the real PrivateCreator as unknown "private tag data"
        # 'private_creator': "GEMS_IDEN_01",
        'private_creator': None,
        'version': '24:LX:MR Software release:DV24.0_R01_1344.a',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20180205',
        'seriesnumber': 6,
        'instancenumber': 54,
        'acquisitionnumber': 1,
        'sequence': 'efgre3d',
        'protocol': 'Physics: Ghosting',
        'rxcoilname': 'C-GE_HNS Head',
        'tr': 1.368,
        'te': 0.5,
        'flipangle': 1.0,  # RHD: [sic] must be a ge oddity
        'pixspacingyx': (3.9063, 3.9063),
        'matrixyx': (64, 64),
        'phaseencdirn': 'COL',
        'slicethickness': 9.4,
        'slicelocation': 105.4999924,
        'numberofaverages': 2,
        'numberofphaseencodingsteps': 32,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-124.531, -174.185, 105.5),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 1953.12,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 63.860822,
        'readoutsensitivity': 0.12772361,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1, 0)
    },
    'ge_fgre':  {
        'filename': 'test-data/ge-fgre.dcm',
        # 'private_creator': "GEMS_ACQU_01",
        'private_creator': None,
        'version': '24:LX:MR Software release:DV24.0_R01_1344.a',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20180205',
        'seriesnumber': 2,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': 'fgre',
        'protocol': 'Physics: Ghosting',
        'rxcoilname': 'C-GE_HNS Head',
        'tr': 4.864,
        'te': 1.316,
        'flipangle': 30,
        'pixspacingyx': (1.1719, 1.1719),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 10.0,
        'slicelocation': -20,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 128,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-149.414, -149.414, -20),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 244.141,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 63.860737,
        'readoutsensitivity': 0.30653761,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1, 0)
    },
    'ge_memp':  {
        'filename': 'test-data/ge-memp.dcm',
        # 'private_creator': "GEMS_ACQU_01",
        'private_creator': None,
        'version': '24:LX:MR Software release:DV24.0_R01_1344.a',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20180205',
        'seriesnumber': 4,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': 'memp',
        'protocol': 'Physics: Ghosting',
        'rxcoilname': 'C-GE_HNS Head',
        'tr': 1000,
        'te': 30,
        'flipangle': 90,
        'pixspacingyx': (0.9766,  0.9766),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 5.0,
        'slicelocation': 28.71155167,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 256,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-126.266, -177.244, 28.7116),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 122.109,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 63.860752,
        'readoutsensitivity': 0.51074377,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1, 0)
    },
    'ge_scout':  {
        'filename': 'test-data/ge-scout.dcm',
        'private_creator': "GEMS_ACQU_01",
        'version': '24:LX:MR Software release:DV24.0_R01_1344.a',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20140709',
        'seriesnumber': 1,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': 'fgre',
        'protocol': 'Brain: Routine',
        'rxcoilname': 'C-GE_HEAD',
        'tr': 4.864,
        'te': 1.316,
        'flipangle': 30,
        'pixspacingyx': (1.1719, 1.1719),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 10,
        'slicelocation': -20,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 128,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-149.414, -149.414, -20),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 244.141,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 63.862709,
        'readoutsensitivity': 0.30654707,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1, 0)
    },
    'ge_diffusion_dwi':  {
        'filename': 'test-data/diffusion/ge_1/dicom/traces/00039.dcm',
        'private_creator': "GEMS_ACQU_01",
        'version': '27:LX:MR Software release:DV25.1_R03_1802.a',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20200202',
        'seriesnumber': 28,
        'instancenumber': 26,
        'acquisitionnumber': 1,
        'sequence': 'epi2',
        'protocol': 'ACR pirad QA',
        'rxcoilname': 'C-GE_HNS Head',
        'tr': 10000,
        'te': 58.5,
        'flipangle': 90,
        'pixspacingyx': (0.8594, 0.8594),
        'matrixyx': (256, 256),
        'phaseencdirn': 'COL',
        'slicethickness': 4,
        'slicelocation': -79.53125,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 128,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-108.008, -140.039, -79.5312),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 1953.12,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 63.860806,
        'readoutsensitivity': 0.0280996,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1, 0)
    },
    'ge_diffusion_adc': {
        'filename': 'test-data/diffusion/ge_1/dicom/adc/00025.dcm',
        'private_creator': "GEMS_IDEN_01",
        'version': '27:LX:MR Software release:DV25.1_R03_1802.a',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20200202',
        'seriesnumber': 2800,
        'instancenumber': 6,
        'acquisitionnumber': 1,
        'sequence': 'epi2',
        'protocol': 'ACR pirad QA',
        'rxcoilname': 'HNS Head',
        'tr': 10000,
        'te': 58.5,
        'flipangle': 90,
        'pixspacingyx': (0.8594, 0.8594),
        'matrixyx': (256, 256),
        'phaseencdirn': 'COL',
        'slicethickness': 4,
        'slicelocation': -54.53125,
        'numberofaverages': KeyError,
        'numberofphaseencodingsteps': 128,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-108.008, -140.039, -54.5312),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 1953.12,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 63.860806,
        'readoutsensitivity': 0.0280996,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1, 0)
    },
    'philips_epi': {
        'filename': 'test-data/philips-epi.dcm',
        'private_creator': "Philips MR Imaging DD 005",
        'version': '5.1.2:5.1.2.0',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20140709',
        'seriesnumber': 1001,
        'instancenumber': 1,
        'acquisitionnumber': 10,
        'sequence': 'FEEPI',
        'protocol': 'EP2D_AXIAL_RL_GHOST_HEAD_GE10CM CLEAR',
        'rxcoilname': 'MULTI COIL',
        'tr': 2000,
        'te': 30,
        'flipangle': 90,
        'pixspacingyx': (3.90625, 3.90625),
        'matrixyx': (64, 64),
        'phaseencdirn': 'ROW',
        'slicethickness': 5,
        'slicelocation': 0,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 63,
        'numberofframes': 3,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-123.046875, -125.55523610115, 0.0),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 3179,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 127.752145,
        'readoutsensitivity': 0.156977608,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (0.73699633699633, 0)
    },
    'philips_epse': {
        'filename': 'test-data/philips-epse.dcm',
        'private_creator': "Philips MR Imaging DD 005",
        'version': '5.1.2:5.1.2.0',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20140709',
        'seriesnumber': 1601,
        'instancenumber': 1,
        'acquisitionnumber': 16,
        'sequence': 'SEEPI',
        'protocol': 'EPSE_AXIAL_AP_GHOST_HEAD_GE10CM_NFS',
        'rxcoilname': 'MULTI COIL',
        'tr': 750,
        'te': 185,
        'flipangle': 90,
        'pixspacingyx': (1.953125, 1.953125),
        'matrixyx': (128, 128),
        'phaseencdirn': 'COL',
        'slicethickness': 10,
        'slicelocation': 0,
        'numberofaverages': 32,
        'numberofphaseencodingsteps': 127,
        'numberofframes': 1,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-121.94985890388, -127.88631415367, 0.0),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 2267,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 127.752151,
        'readoutsensitivity': 0.11006437,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1.3023199023199, 0)
    },
    'philips_se': {
        'filename': 'test-data/philips-se.dcm',
        'private_creator': "Philips MR Imaging DD 005",
        'version': '5.1.2:5.1.2.0',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20140626',
        'seriesnumber': 201,
        'instancenumber': 1,
        'acquisitionnumber': 2,
        'sequence': 'SE',
        'protocol': 'SE_AXIAL_RL_SNR_UNIF_HEAD15_OIL20CM_CLASSIC',
        'rxcoilname': 'MULTI COIL',
        'tr': 1000,
        'te': 30,
        'flipangle': 90,
        'pixspacingyx': (0.96875, 0.96875),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 5,
        'slicelocation': 4.18060207366943,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 256,
        'numberofframes': 1,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-119.75308322906, -123.515625, 4.18060207366943),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 130,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 127.751988,
        'readoutsensitivity': 0.9519979875,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1.67155067155067, 0)
    },
    'philips_std': {
        'filename': 'test-data/philips-se-std.dcm',
        'private_creator': "Philips MR Imaging DD 005",
        'version': '2.6.3:2.6.3.9',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20140811',
        'seriesnumber': 401,
        'instancenumber': 1,
        'acquisitionnumber': 4,
        'sequence': 'SE',
        'protocol': 'SE_AXIAL_RL_SNR_HEAD8_OIL20CM_CLASSIC',
        'rxcoilname': 'SENSE-Head-8',
        'tr': 1000,
        'te': 30,
        'flipangle': 90,
        'pixspacingyx': (0.9765625, 0.9765625),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 5.0,
        'slicelocation': 0,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 250,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-117.63164234161, -138.27187156677, 2.58002877235412),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 130,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 63.907989,
        'readoutsensitivity': 0.48007804,
        'coilelements': [0],
        'rescaleslopeandintercept': (1.39072039072039, 0)
    },
    'philips_survey': {
        'filename': 'test-data/philips-survey.dcm',
        'private_creator': "Philips MR Imaging DD 005",
        'version': '5.3.1:5.3.1.3',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20210706',
        'seriesnumber': 101,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': 'T1TFE',
        'protocol': 'Survey',
        'rxcoilname': 'MULTI COIL',
        'tr': 11,
        'te': 4.603,
        'flipangle': 15,
        'pixspacingyx': (0.9765625, 0.9765625),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 10,
        'slicelocation': -20.0,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 128,
        'numberofframes': 9,
        'isenhancedmr': True,
        'imageorientationpat': (0, 1, 0, 0, 0, -1),
        'imagepositionpat': (20, -124.51171875, 124.51171875),
        'approxsliceorientation': 'Sagittal',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 140,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 127.749316,
        'readoutsensitivity': 0.8911085100446428,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1.24786324786324, 0)
    },
    'philips_tse': {
        'filename': 'test-data/philips-tse.dcm',
        'private_creator': "Philips MR Imaging DD 005",
        'version': '5.1.2:5.1.2.0',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20140709',
        'seriesnumber': 601,
        'instancenumber': 1,
        'acquisitionnumber': 6,
        'sequence': 'TSE',
        'protocol': 'TSE_AXIAL_RL_GHOST_HEAD_GE10CM',
        'rxcoilname': 'MULTI COIL',
        'tr': 6000,
        'te': 102,
        'flipangle': 90,
        'pixspacingyx': (0.96875, 0.96875),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 5,
        'slicelocation': -0.4180599749088,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 252,
        'numberofframes': 1,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-123.93368506431, -126.02398586273, -0.4180599749088),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 218,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 127.7521,
        'readoutsensitivity': 0.56770572,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1.38754578754578, 0)
    },
    'philips_un_vr': {
        'filename': 'test-data/philips-un-vr.dcm',
        'private_creator': "Philips MR Imaging DD 005",
        'version': '5.3.0:5.3.0.3',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20171120',
        'seriesnumber': 403,
        'instancenumber': 1,
        'acquisitionnumber': 4,
        'sequence': 'SE',
        'protocol': 'DelRec - AX T1W TEST BREAST',
        'rxcoilname': 'SENSE_BREAST_7M_',
        'tr': 500.000610351562,
        'te': 10,
        'flipangle': 90,
        'pixspacingyx': (1.40625, 1.40625),
        'matrixyx': (192, 192),
        'phaseencdirn': 'ROW',
        'slicethickness': 3,
        'slicelocation': -48,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 140,
        'numberofframes': 231,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-134.296875, -172.5934677124, -48),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 217,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 127.750188,
        'readoutsensitivity': 0.8278742,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (1.45372405372405, 0)
    },
    'philips_diffusion_dwi': {
        'filename': 'test-data/diffusion/philips_2/dicom/traces/00001.dcm',
        'private_creator': "Philips MR Imaging DD 005",
        'version': '5.3.1:5.3.1.3',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20201212',
        'seriesnumber': 1101,
        'instancenumber': 1,
        'acquisitionnumber': 11,
        'sequence': 'DwiSE',
        'protocol': 'NIST_AX1',
        'rxcoilname': 'MULTI COIL',
        'tr': 10000,
        'te': 109.083,
        'flipangle': 90,
        'pixspacingyx': (0.859375, 0.859375),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 4,
        'slicelocation': -64.509010314941,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 126,
        'numberofframes': 300,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-112.57632374763, -115.58232021331, -64.509010314941),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 1420,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 63.88915,
        'readoutsensitivity': 0.03866531,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (8.77875457875458, 0)
    },
    'philips_diffusion_adc': {
        'filename': 'test-data/diffusion/philips_2/dicom/adc/00001.dcm',
        'private_creator': "Philips MR Imaging DD 005",
        'version': '5.3.1:5.3.1.3',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20201212',
        'seriesnumber': 1102,
        'instancenumber': 1,
        'acquisitionnumber': 11,
        'sequence': 'DwiSE',
        'protocol': 'dNIST_COR1_ADC',
        'rxcoilname': 'MULTI COIL',
        'tr': 10000,
        'te': 109.083,
        'flipangle': 90,
        'pixspacingyx': (0.859375, 0.859375),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 4,
        'slicelocation': -64.509010314941,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 126,
        'numberofframes': 25,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-112.57632374763, -115.58232021331, -64.509010314941),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 1420,
        'epiphaseencodebandwidth': KeyError,
        'larmorfrequency': 63.88915,
        'readoutsensitivity': 0.03866531,
        'coilelements': KeyError,
        'rescaleslopeandintercept': (0.00098461308516, 0)
    },
    'siemens_scout': {
        'filename': 'test-data/siemens-scout.dcm',
        'private_creator': "SIEMENS MR HEADER",
        'version': 'syngo MR D13',
        'operator': 'RHD',
        'operator_with_default': 'RHD',
        'qadate': '20140718',
        'seriesnumber': 1,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*fl2d1',
        'protocol': 'localizer',
        'rxcoilname': 'HEA;HEP',
        'tr': 8.6,
        'te': 4,
        'flipangle': 20,
        'pixspacingyx': (0.48828125, 0.48828125),
        'matrixyx': (512, 512),
        'phaseencdirn': 'ROW',
        'slicethickness': 7,
        'slicelocation': 0,
        'numberofaverages': 2,
        'numberofphaseencodingsteps': 231,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (0, 1, 0, 0, 0, -1),
        'imagepositionpat': (0, -125, 125),
        'approxsliceorientation': 'Sagittal',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 320,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.259373,
        'readoutsensitivity': 0.18807888,
        'coilelements': list(range(32)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_se': {
        'filename': 'test-data/siemens-se.dcm',
        'private_creator': "SIEMENS MR HEADER",
        'version': 'syngo MR E11',
        'operator': 'JD',
        'operator_with_default': 'JD',
        'qadate': '20161215',
        'seriesnumber': 26,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*se2d1',
        'protocol': 'QUARTERLY_QA_SNR',
        'rxcoilname': 'H13',
        'tr': 500,
        'te': 20,
        'flipangle': 90,
        'pixspacingyx': (0.9765625, 0.9765625),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 5,
        'slicelocation': 0,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 256,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-124.99999999939, -125.00000000061, 0),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 260,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.256491,
        'readoutsensitivity': 0.46295256,
        'coilelements': [0],
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_se_dis2d': {
        'filename': 'test-data/siemens-se-dis2d.dcm',
        'private_creator': "SIEMENS MR HEADER",
        'version': 'syngo MR E11',
        'operator': 'SC',
        'operator_with_default': 'SC',
        'qadate': '20180118',
        'seriesnumber': 34,
        'instancenumber': 3,
        'acquisitionnumber': 1,
        'sequence': '*se2d1',
        'protocol': 'SE_AXIAL_RL_T02_SL3_HEAD_PSN_512',
        'rxcoilname': 'HE1-4',
        'tr': 500,
        'te': 30,
        'flipangle': 90,
        'pixspacingyx': (0.48828125, 0.48828125),
        'matrixyx': (512, 512),
        'phaseencdirn': 'ROW',
        'slicethickness': 3,
        'slicelocation': 11.39999961853,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 512,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-120.99999999939, -117.00000000061, 11.39999961853),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 130,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 63.667593,
        'readoutsensitivity': 0.23913609,
        'coilelements': list(range(16)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_vb17_pca_magn': {
        'filename': 'test-data/siemens-vb17-pca-magn.dcm',
        'private_creator': "SIEMENS MR HEADER",
        'version': 'syngo MR B17',
        'operator': 'JD/RHD/HE',
        'operator_with_default': 'JD/RHD/HE',
        'qadate': '20190206',
        'seriesnumber': 5,
        'instancenumber': 7,
        'acquisitionnumber': 1,
        'sequence': '*fl2d1_5',
        'protocol': 'AorticPlaneZM50',
        'rxcoilname': 'C:BO1,2;SP5-7',
        'tr': 47.75,
        'te': 2.07,
        'flipangle': 30,
        'pixspacingyx': (1.25, 1.25),
        'matrixyx': (176, 256),
        'phaseencdirn': 'COL',
        'slicethickness': 6,
        'slicelocation': -35.355339752803,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 90,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (0.70710679505606, 0, 0.70710676731704, 0, 1, 0),
        'imagepositionpat': (-113.13708720897, -110, -163.13708277073),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 558,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 63.680124,
        'readoutsensitivity': 0.14265261,
        'coilelements':  list(range(5)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_vb17_pca_phase': {
        'filename': 'test-data/siemens-vb17-pca-phase.dcm',
        'private_creator': "SIEMENS MR HEADER",
        'version': 'syngo MR B17',
        'operator': 'JD/RHD/HE',
        'operator_with_default': 'JD/RHD/HE',
        'qadate': '20190206',
        'seriesnumber': 6,
        'instancenumber': 7,
        'acquisitionnumber': 1,
        'sequence': '*fl2d1_v200in',
        'protocol': 'AorticPlaneZM50',
        'rxcoilname': 'C:BO1,2;SP5-7',
        'tr': 47.75,
        'te': 2.07,
        'flipangle': 30,
        'pixspacingyx': (1.25, 1.25),
        'matrixyx': (176, 256),
        'phaseencdirn': 'COL',
        'slicethickness': 6,
        'slicelocation': -35.355339752803,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 90,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (0.70710679505606, 0, 0.70710676731704, 0, 1, 0),
        'imagepositionpat': (-113.13708720897, -110, -163.13708277073),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 558,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 63.680124,
        'readoutsensitivity': 0.14265261,
        'coilelements':  list(range(5)),
        'rescaleslopeandintercept': (2, -4096)
    },
    'siemens_vb17_single': {
        'filename': 'test-data/siemens-vb17-single.dcm',
        'private_creator': "SIEMENS MR HEADER",
        'version': 'syngo MR B17',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20180406',
        'seriesnumber': 9,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*se2d1',
        'protocol': 'QUARTERLY_QA_SNR',
        'rxcoilname': 'HE3',
        'tr': 500,
        'te': 20,
        'flipangle': 90,
        'pixspacingyx': (0.9765625, 0.9765625),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 5,
        'slicelocation': 0.34384867548943,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 256,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-126.00000002564, -142.99999997436, 0.34384867548943),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 130,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 63.679602,
        'readoutsensitivity': 0.47836239,
        'coilelements': [3],
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_ve11_noise': {
        'filename': 'test-data/siemens-ve11-noise.dcm',
        'private_creator': "SIEMENS MR HEADER",
        'version': 'syngo MR E11',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20180419',
        'seriesnumber': 11,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*se2d1',
        'protocol': 'QQA_SE_NOISE',
        'rxcoilname': 'H13',
        'tr': 500,
        'te': 20,
        'flipangle': 90,
        'pixspacingyx': (0.9765625, 0.9765625),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 5,
        'slicelocation': 0,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 256,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-117.09999990402, -116.50000000061, 0),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 130,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 63.667222,
        'readoutsensitivity': 0.47826940,
        'coilelements': [0],
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_ve11_fid': {
        'filename': 'test-data/siemens-ve11-fid.dcm',
        'private_creator': "SIEMENS CSA NON-IMAGE",
        'version': 'syngo MR E11',
        'operator': 'RHD',
        'operator_with_default': 'RHD',
        'qadate': '20181212',
        'seriesnumber': 57,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*fid',
        'protocol': 'qa_fid',
        'rxcoilname': 'HE1-4;NE1,2;SP1',
        'tr': 2000,
        'te': 0.35,
        'flipangle': KeyError,
        'pixspacingyx': KeyError,
        'matrixyx': KeyError,
        'phaseencdirn': KeyError,
        'slicethickness': KeyError,
        'slicelocation': KeyError,
        'numberofaverages': 16,
        'numberofphaseencodingsteps': KeyError,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': KeyError,
        'imagepositionpat': KeyError,
        'approxsliceorientation': KeyError,
        'approxphaseorientation': KeyError,
        'readoutbandwidth': KeyError,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.25786,
        'readoutsensitivity': KeyError,
        'coilelements': KeyError,  # TODO: should be able to get this, but UsedChannel string missing from csa
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_ve11_svs_se': {
        'filename': 'test-data/siemens-ve11-svs-se.dcm',
        'private_creator': "SIEMENS CSA NON-IMAGE",
        'version': 'syngo MR E11',
        'operator': 'RHD',
        'operator_with_default': 'RHD',
        'qadate': '20181212',
        'seriesnumber': 58,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*svs_se',
        'protocol': 'qa_svs_se_30',
        'rxcoilname': 'HE1-4',
        'tr': 2020,
        'te': 30,
        'flipangle': KeyError,
        'pixspacingyx': KeyError,
        'matrixyx': KeyError,
        'phaseencdirn': KeyError,
        'slicethickness': KeyError,
        'slicelocation': KeyError,
        'numberofaverages': 16,
        'numberofphaseencodingsteps': KeyError,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': KeyError,
        'imagepositionpat': KeyError,
        'approxsliceorientation': KeyError,
        'approxphaseorientation': KeyError,
        'readoutbandwidth': KeyError,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.257844,
        'readoutsensitivity': KeyError,
        'coilelements': KeyError,  # TODO: should be able to get this, but UsedChannel string missing from csa
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_ve_diffusion_dwi': {
        'filename': 'test-data/diffusion/siemens_ve/dicom/traces/00100.dcm',
        'private_creator': "SIEMENS MR HEADER",
        'version': 'syngo MR E11',
        'operator': 'RHD',
        'operator_with_default': 'RHD',
        'qadate': '20200129',
        'seriesnumber': 8,
        'instancenumber': 79,
        'acquisitionnumber': 1,
        'sequence': '*ep_b2000t',
        'protocol': 'EPDIFF_NIST_HEAD64_COR_1',
        'rxcoilname': 'HC1-7;NC1,2',
        'tr': 10000,
        'te': 101,
        'flipangle': 90,
        'pixspacingyx': (1.125, 1.125),
        'matrixyx': (192, 192),
        'phaseencdirn': 'ROW',
        'slicethickness': 4,
        'slicelocation': -55.0,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 143,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 0, -1),
        'imagepositionpat': (-108, -55, 108),
        'approxsliceorientation': 'Coronal',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 1130,
        'epiphaseencodebandwidth': 9.645,
        'larmorfrequency': 123.247954,
        'readoutsensitivity': 0.1227026,
        'coilelements': list(range(64)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_ve_diffusion_adc': {
        'filename': 'test-data/diffusion/siemens_ve/dicom/adc/00025.dcm',
        'private_creator': "SIEMENS MR HEADER",
        'version': 'syngo MR E11',
        'operator': 'RHD',
        'operator_with_default': 'RHD',
        'qadate': '20200129',
        'seriesnumber': 9,
        'instancenumber': 2,
        'acquisitionnumber': 1,
        'sequence': '*ep_b0_2000',
        'protocol': 'EPDIFF_NIST_HEAD64_COR_1',
        'rxcoilname': 'HC1-7;NC1,2',
        'tr': 10000,
        'te': 101,
        'flipangle': 90,
        'pixspacingyx': (1.125, 1.125),
        'matrixyx': (192, 192),
        'phaseencdirn': 'ROW',
        'slicethickness': 4,
        'slicelocation': -65,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 143,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 0, -1),
        'imagepositionpat': (-108, -65, 108),
        'approxsliceorientation': 'Coronal',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 1130,
        'epiphaseencodebandwidth': 9.645,
        'larmorfrequency': 123.247954,
        'readoutsensitivity': 0.1227026,
        'coilelements': list(range(64)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_xa11a_enhanced_se': {
        'filename': 'test-data/siemens-xa11a-enhanced-se.dcm',
        'private_creator': "SIEMENS MR SDR 01",
        'version': 'syngo MR XA11',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20200115',
        'seriesnumber': 2,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*se2d1',
        'protocol': 'QQA_SE_SIGNAL',
        'rxcoilname': 'HeadNeck_20_TCS',
        'tr': 500,
        'te': 30,
        'flipangle': 90,
        'pixspacingyx': (0.976562, 0.976562),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 5,
        'slicelocation': 0,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 256,
        'numberofframes': 1,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-125, -125, 0),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 260,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.257793,
        'readoutsensitivity': 0.4629572,
        'coilelements': [0],
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_xa11a_enhanced_se_norm_dc': {
        'filename': 'test-data/siemens-xa11a-enhanced-se-norm-dc.dcm',
        'private_creator': "SIEMENS MR SDR 01",
        'version': 'syngo MR XA11',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20200116',
        'seriesnumber': 4,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*se2d1',
        'protocol': 'QQA_SE_SIGNAL',
        'rxcoilname': 'HeadNeck_20_TCS',
        'tr': 500,
        'te': 20,
        'flipangle': 90,
        'pixspacingyx': (0.976562, 0.976562),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 5,
        'slicelocation': 0,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 256,
        'numberofframes': 1,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-125, -125, 0),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 260,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.257773,
        'readoutsensitivity': 0.4629571435,
        'coilelements': list(range(20)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_xa11a_interop_se': {
        'filename': 'test-data/siemens-xa11a-interop-se.dcm',
        'private_creator': "SIEMENS MR SDS 01",
        'version': 'syngo MR XA11',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20200115',
        'seriesnumber': 2001,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*se2d1',
        'protocol': 'QQA_SE_SIGNAL',
        'rxcoilname': 'HeadNeck_20_TCS',
        'tr': 500,
        'te': 30,
        'flipangle': 90,
        'pixspacingyx': (0.976562, 0.976562),
        'matrixyx': (256, 256),
        'phaseencdirn': 'ROW',
        'slicethickness': 5,
        'slicelocation': 0,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 256,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-125, -125, 0),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 260,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.257793,
        'readoutsensitivity': 0.4629572186,
        'coilelements': [0],
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_xa_diffusion_dwi': {
        'filename': 'test-data/diffusion/siemens_xa/dicom/traces/00004.dcm',
        'private_creator': "SIEMENS MR SDR 01",
        'version': 'syngo MR XA20',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20200926',
        'seriesnumber': 14,
        'instancenumber': 3,
        'acquisitionnumber': 1,
        'sequence': '*epse2d1_160',
        'protocol': 'NIST_COR_1',
        'rxcoilname': 'HeadNeck_20_TCS',
        'tr': 10000,
        'te': 101,
        'flipangle': 90,
        'pixspacingyx': (1.35, 1.35),
        'matrixyx': (160, 160),
        'phaseencdirn': 'ROW',
        'slicethickness': 4,
        'slicelocation': -47.9811,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 160,
        'numberofframes': 25,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 0, -1),
        'imagepositionpat': (-106.333, -47.9811, 108.097),
        'approxsliceorientation': 'Coronal',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 762,
        'epiphaseencodebandwidth': 8.929,
        'larmorfrequency': 63.679663,
        'readoutsensitivity': 0.1128183,
        'coilelements': list(range(20)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_xa_diffusion_adc': {
        'filename': 'test-data/diffusion/siemens_xa/dicom/adc/00001.dcm',
        'private_creator': "SIEMENS MR SDR 01",
        'version': 'syngo MR XA20',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20200926',
        'seriesnumber': 15,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*epse2d1_160',
        'protocol': 'NIST_COR_1',
        'rxcoilname': 'HeadNeck_20_TCS',
        'tr': 10000,
        'te': 101,
        'flipangle': 90,
        'pixspacingyx': (1.35, 1.35),
        'matrixyx': (160, 160),
        'phaseencdirn': 'ROW',
        'slicethickness': 4,
        'slicelocation': -47.9811,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 160,
        'numberofframes': 25,
        'isenhancedmr': True,
        'imageorientationpat': (1, 0, 0, 0, 0, -1),
        'imagepositionpat': (-106.333, -47.9811, 108.097),
        'approxsliceorientation': 'Coronal',
        'approxphaseorientation': 'RL',
        'readoutbandwidth': 762,
        'epiphaseencodebandwidth': 8.929,
        'larmorfrequency': 63.679663,
        'readoutsensitivity': 0.1128183,
        'coilelements': list(range(20)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_xa20_fid': {
        'filename': 'test-data/siemens-xa20-fid.dcm',
        'private_creator': "SIEMENS MR MRS 05",
        'version': 'syngo MR XA20',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20210303',
        'seriesnumber': 108,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*fid',
        'protocol': 'qa_fid',
        'rxcoilname': 'HeadNeck_20_TCS',
        'tr': 1500,
        'te': 0.35,
        'flipangle': 90,
        'pixspacingyx': KeyError,
        'matrixyx': (1, 1),
        'phaseencdirn': KeyError,
        'slicethickness': KeyError,
        'slicelocation': KeyError,
        'numberofaverages': 16,
        'numberofphaseencodingsteps': KeyError,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (-1, 0, 0, 0, 1, 0),
        'imagepositionpat': (0, 0, 0),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': KeyError,
        'readoutbandwidth': KeyError,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 63.680642,
        'readoutsensitivity': KeyError,
        'coilelements': list(range(16)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_xa20_pca_magn': {
        'filename': 'test-data/siemens-xa20-pca-magn.dcm',
        'private_creator': "SIEMENS MR SDR 01",
        'version': 'syngo MR XA20',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20210304',
        'seriesnumber': 172,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*fl2d1r5',
        'protocol': 'AorticPlane Z0',
        'rxcoilname': 'Body_18',
        'tr': 52.7,
        'te': 3.07,
        'flipangle': 30,
        'pixspacingyx': (1.25, 1.25),
        'matrixyx': (256, 176),
        'phaseencdirn': 'ROW',
        'slicethickness': 6,
        'slicelocation': 0.0003826819999963507,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 88,
        'numberofframes': 18,
        'isenhancedmr': True,
        'imageorientationpat': (0, 1, 0, -0.64679, 0, -0.762668),
        'imagepositionpat': (103.486, -60.0, 122.027),
        'approxsliceorientation': 'Sagittal',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 501,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 63.680633,
        'readoutsensitivity': 0.15888381,
        'coilelements': list(range(26)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens_xa20_pca_phase': {
        'filename': 'test-data/siemens-xa20-pca-phase.dcm',
        'private_creator': "SIEMENS MR SDR 01",
        'version': 'syngo MR XA20',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20210304',
        'seriesnumber': 174,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*fl2d1r5',
        'protocol': 'AorticPlane Z0',
        'rxcoilname': 'Body_18',
        'tr': 52.7,
        'te': 3.07,
        'flipangle': 30,
        'pixspacingyx': (1.25, 1.25),
        'matrixyx': (256, 176),
        'phaseencdirn': 'ROW',
        'slicethickness': 6,
        'slicelocation': 0.0003826819999963507,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 88,
        'numberofframes': 18,
        'isenhancedmr': True,
        'imageorientationpat': (0, 1, 0, -0.64679, 0, -0.762668),
        'imagepositionpat': (103.486, -60.0, 122.027),
        'approxsliceorientation': 'Sagittal',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 501,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 63.680633,
        'readoutsensitivity': 0.15888381,
        'coilelements': list(range(26)),
        'rescaleslopeandintercept': (2, -4096)
    },
    'siemens_xa20_svs': {
        'filename': 'test-data/siemens-xa20-svs.dcm',
        'private_creator': "SIEMENS MR MRS 05",
        'version': 'syngo MR XA20',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20210303',
        'seriesnumber': 101,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*svs_se',
        'protocol': 'qa_svs_se_30',
        'rxcoilname': 'HeadNeck_20_TCS',
        'tr': 1500,
        'te': 30,
        'flipangle': 90,
        'pixspacingyx': KeyError,
        'matrixyx': (1, 1),
        'phaseencdirn': KeyError,
        'slicethickness': KeyError,
        'slicelocation': KeyError,
        'numberofaverages': 16,
        'numberofphaseencodingsteps': KeyError,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (-1, 0, 0, 0, 1, 0),
        'imagepositionpat': (0, -0.998081, -10.8038),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': KeyError,
        'readoutbandwidth': KeyError,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 63.680641,
        'readoutsensitivity': KeyError,
        'coilelements': list(range(16)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens-xa30-mfsplit-pca-magn': {
        'filename': 'test-data/siemens-xa30-mfsplit-pca-magn.dcm',
        'private_creator': "SIEMENS MR SDR 01",
        'version': 'syngo MR XA30',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20250127',
        'seriesnumber': 58,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*fl2d1r5',
        'protocol': 'AorticPlane Z-50',
        'rxcoilname': 'Body_18',
        'tr': 52.7,
        'te': 3.07,
        'flipangle': 30,
        'pixspacingyx': (1.25, 1.25),
        'matrixyx': (256, 176),
        'phaseencdirn': 'ROW',
        'slicethickness': 6,
        'slicelocation': 32.3395,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 88,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (0, 1, 0, -0.64679, 0, -0.762668),
        'imagepositionpat': (103.486, -110.0, 72.0269),
        'approxsliceorientation': 'Sagittal',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 501,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.163704,
        'readoutsensitivity': 0.30729467,
        'coilelements': list(range(26)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens-xa30-mfsplit-pca-phase': {
        'filename': 'test-data/siemens-xa30-mfsplit-pca-phase.dcm',
        'private_creator': "SIEMENS MR SDR 01",
        'version': 'syngo MR XA30',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20250127',
        'seriesnumber': 60,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*fl2d1_v200in',
        'protocol': 'AorticPlane Z-50',
        'rxcoilname': 'Body_18',
        'tr': 52.7,
        'te': 3.07,
        'flipangle': 30,
        'pixspacingyx': (1.25, 1.25),
        'matrixyx': (256, 176),
        'phaseencdirn': 'ROW',
        'slicethickness': 6,
        'slicelocation': 32.3395,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 88,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (0, 1, 0, -0.64679, 0, -0.762668),
        'imagepositionpat': (103.486, -110.0, 72.0269),
        'approxsliceorientation': 'Sagittal',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 501,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.163704,
        'readoutsensitivity': 0.30729467,
        'coilelements': list(range(26)),
        'rescaleslopeandintercept': (2, -4096)
    },
    'siemens-xa30-mfsplit-se-norm-dis2d': {
        'filename': 'test-data/siemens-xa30-mfsplit-se-norm-dis2d.dcm',
        'private_creator': "SIEMENS MR SDR 01",
        'version': 'syngo MR XA30',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20250127',
        'seriesnumber': 6,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*se2d1',
        'protocol': 'SE_AXIAL_AP_PIQT_SL3_HEAD_512',
        'rxcoilname': 'HeadNeck_20',
        'tr': 500,
        'te': 30,
        'flipangle': 90,
        'pixspacingyx': (0.488281, 0.488281),
        'matrixyx': (512, 512),
        'phaseencdirn': 'COL',
        'slicethickness': 3,
        'slicelocation': -29.1835,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 512,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-122.017, -109.487, -29.1835),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 257,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.163847,
        'readoutsensitivity': 0.2340022,
        'coilelements': list(range(16)),
        'rescaleslopeandintercept': (1, 0)
    },
    'siemens-xa30-mfsplit-se-norm-nd': {
        'filename': 'test-data/siemens-xa30-mfsplit-se-norm-nd.dcm',
        'private_creator': "SIEMENS MR SDR 01",
        'version': 'syngo MR XA30',
        'operator': '',
        'operator_with_default': 'BIRCH',
        'qadate': '20250127',
        'seriesnumber': 5,
        'instancenumber': 1,
        'acquisitionnumber': 1,
        'sequence': '*se2d1',
        'protocol': 'SE_AXIAL_AP_PIQT_SL3_HEAD_512',
        'rxcoilname': 'HeadNeck_20',
        'tr': 500,
        'te': 30,
        'flipangle': 90,
        'pixspacingyx': (0.488281, 0.488281),
        'matrixyx': (512, 512),
        'phaseencdirn': 'COL',
        'slicethickness': 3,
        'slicelocation': -29.1835,
        'numberofaverages': 1,
        'numberofphaseencodingsteps': 512,
        'numberofframes': 1,
        'isenhancedmr': False,
        'imageorientationpat': (1, 0, 0, 0, 1, 0),
        'imagepositionpat': (-122.017, -109.487, -29.1835),
        'approxsliceorientation': 'Axial',
        'approxphaseorientation': 'AP',
        'readoutbandwidth': 257,
        'epiphaseencodebandwidth': 0,
        'larmorfrequency': 123.163847,
        'readoutsensitivity': 0.2340022,
        'coilelements': list(range(16)),
        'rescaleslopeandintercept': (1, 0)
    }
}


@fixture(scope='module', autouse=True)
def setup():
    global SCANS
    for value in SCANS.values():
        value['dobj'] = dcmread(value['filename'])


def test_load_series():
    dobjs = dcmio.load_series(patid='PQACRK20161215', sernos=26, directory='DICOMDIR')
    assert len(dobjs) == 32

    dobjs = dcmio.load_series(patid='PQACRK20161215', sernos=26, directory='DICOMDIR', studydate='latest')
    assert len(dobjs) == 32

    dobjs = dcmio.load_series(patid='PQACRK20161215', sernos=26, directory='DICOMDIR', studydate='20191231')
    assert len(dobjs) == 32

    dobjs = dcmio.load_series(patid='PQACRK20161215', sernos=26, directory='DICOMDIR', imagesonly=True)
    assert len(dobjs) == 32

    dobjs = dcmio.load_series(patid='PQACRK20161215', sernos=26, directory='test-data/longbottle')
    assert len(dobjs) == 32

    dobjs = dcmio.load_series(patid='PQACRK20161215', sernos=26, directory='test-data', globpattern='*.dcm')
    assert len(dobjs) == 32

    dobjs = dcmio.load_series(patid='PQACRK20161215', sernos=27, directory='DICOMDIR')
    assert len(dobjs) == 1
    dobj = dobjs[0]
    assert dobj.PatientID == 'PQACRK20161215'
    assert dobj.StudyID == '1'
    assert int(dobj.SeriesNumber) == 27

    with raises(OSError):
        dcmio.load_series(patid='PQACRK20161215', sernos=27, directory='NOSUCHFILE')


def test_has_private_section():
    for scan, info in SCANS.items():
        dobj, section = info['dobj'], info['private_creator']
        if section:
            assert dcmio.has_private_section(dobj, section), scan
            assert not dcmio.has_private_section(dobj, "No Such Creator"), scan


def test_has_sds():
    for scan, info in SCANS.items():
        dobj = info['dobj']
        assert (
            dcmio.has_sds(dobj) ==
            (dcmio.manufacturer(dobj) == 'Siemens' and 'MR XA' in dcmio.software_versions(dobj))
        ), scan


def test_has_sdi():
    for scan, info in SCANS.items():
        dobj = info['dobj']
        assert (
            dcmio.has_sdi(dobj) ==
            (dcmio.manufacturer(dobj) == 'Siemens' and 'MR XA' in dcmio.software_versions(dobj))
        ), scan


def test_has_csa():
    for scan, info in SCANS.items():
        dobj = info['dobj']
        assert (
            dcmio.has_csa(dobj) ==
            (
                dcmio.manufacturer(dobj) == 'Siemens' and
                any(v in dcmio.software_versions(dobj) for v in ['MR A', 'MR B', 'MR D', 'MR E'])
            )
        ), scan


def test_get_private_tag():
    pass


def test_get_sds_tag():
    pass


def test_get_sdi_tag():
    pass


def test_scanner_operator():
    for scan, info in SCANS.items():
        assert (
            dcmio.scanner_operator(info['dobj']) ==
            info['operator']
        ), scan


def test_scanner_operator_with_default():
    for scan, info in SCANS.items():
        assert (
            dcmio.scanner_operator(info['dobj'], 'BIRCH') ==
            info['operator_with_default']
        ), scan


def test_qa_date():
    for scan, info in SCANS.items():
        assert (
            dcmio.qa_date(info['dobj']) ==
            info['qadate']
        ), scan


def test_manufacturer():
    for scan, info in SCANS.items():
        if scan.startswith('ge'):
            assert (
                dcmio.manufacturer(info['dobj']) == 'GE'
            ), scan
        elif scan.startswith('philips'):
            assert (
                dcmio.manufacturer(info['dobj']) == 'Philips'
            ), scan
        elif scan.startswith('siemens'):
            assert (
                dcmio.manufacturer(info['dobj']) == 'Siemens'
            ), scan


def test_series_number():
    for scan, info in SCANS.items():
        assert (
            dcmio.series_number(info['dobj']) == info['seriesnumber']
        ), scan


def test_instance_number():
    for scan, info in SCANS.items():
        assert (
            dcmio.instance_number(info['dobj']) == info['instancenumber']
        ), scan


def test_acquisition_number():
    for scan, info in SCANS.items():
        assert (
            dcmio.acquisition_number(info['dobj']) == info['acquisitionnumber']
        ), scan


def test_software_versions():
    for scan, info in SCANS.items():
        assert (
            dcmio.software_versions(info['dobj']) == info['version']
        ), scan


def test_seq_name():
    for scan, info in SCANS.items():
        assert (
            dcmio.seq_name(info['dobj']) ==
            info['sequence']
        ), scan


def test_protocol_name():
    for scan, info in SCANS.items():
        assert (
            dcmio.protocol_name(info['dobj']) == info['protocol']
        ), scan


def test_rx_coil_name():
    for scan, info in SCANS.items():
        assert (
            dcmio.rx_coil_name(info['dobj']) == info['rxcoilname']
        ), scan


def test_t_r():
    for scan, info in SCANS.items():
        assert (
            dcmio.t_r(info['dobj']) == approx(info['tr'], abs=1e-7)
        ), scan


def test_t_e():
    for scan, info in SCANS.items():
        assert (
            dcmio.t_e(info['dobj']) == approx(info['te'], abs=1e-7)
        ), scan


def test_flip_angle():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['flipangle']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.flip_angle(dobj)
        else:
            assert dcmio.flip_angle(dobj) == approx(value, abs=1e-7), scan


def test_pix_spacing_yx():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['pixspacingyx']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.pix_spacing_yx(dobj)
        else:
            assert dcmio.pix_spacing_yx(dobj) == approx(value), scan


def test_matrix_yx():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['matrixyx']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.matrix_yx(dobj)
        else:
            assert dcmio.matrix_yx(dobj) == value, scan


def test_phase_enc_dirn():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['phaseencdirn']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.phase_enc_dirn(dobj)
        else:
            assert dcmio.phase_enc_dirn(dobj) == value, scan


def test_slice_thickness():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['slicethickness']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.slice_thickness(dobj)
        else:
            assert dcmio.slice_thickness(dobj) == approx(value, abs=1e-7), scan


def test_slice_location():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['slicelocation']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.slice_location(dobj)
        else:
            assert dcmio.slice_location(dobj) == approx(value, abs=1e-7), scan


def test_number_of_averages():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['numberofaverages']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.number_of_averages(dobj)
        else:
            assert dcmio.number_of_averages(dobj) == value, scan


def test_number_of_phase_encoding_steps():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['numberofphaseencodingsteps']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.number_of_phase_encoding_steps(dobj)
        else:
            assert dcmio.number_of_phase_encoding_steps(dobj) == value, scan


def test_number_of_frames():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['numberofframes']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.number_of_frames(dobj)
        else:
            assert dcmio.number_of_frames(dobj) == value, scan


def test_is_multiframe():
    for scan, info in SCANS.items():
        assert (
            dcmio.is_multiframe(info['dobj']) == (info['numberofframes'] > 1)
        ), scan


def test_is_enhancedmr():
    for scan, info in SCANS.items():
        assert (
            dcmio.is_enhancedmr(info['dobj']) == info['isenhancedmr']
        ), scan


def test_image_orientation_pat():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['imageorientationpat']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.image_orientation_pat(dobj)
        else:
            assert dcmio.image_orientation_pat(dobj) == approx(value, abs=1e-6), scan


def test_image_position_pat():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['imagepositionpat']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.image_position_pat(dobj)
        else:
            assert dcmio.image_position_pat(dobj) == approx(value), scan


def test_approx_slice_orientation():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['approxsliceorientation']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.approx_slice_orientation(dobj)
        else:
            assert dcmio.approx_slice_orientation(dobj) == value, scan


def test_approx_phase_orientation():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['approxphaseorientation']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.approx_phase_orientation(dobj)
        else:
            assert dcmio.approx_phase_orientation(dobj) == value, scan


def test_readout_bandwidth():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['readoutbandwidth']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.readout_bandwidth(dobj)
        else:
            assert dcmio.readout_bandwidth(dobj) == approx(value, abs=1e-7), scan


def test_epi_phase_encode_bandwidth():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['epiphaseencodebandwidth']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.epi_phase_encode_bandwidth(dobj)
        else:
            assert dcmio.epi_phase_encode_bandwidth(dobj) == approx(value, abs=1e-7), scan


def test_larmor_frequency():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['larmorfrequency']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.larmor_frequency(dobj)
        else:
            assert dcmio.larmor_frequency(dobj) == approx(value, abs=1e-7), scan


def test_readout_sensitivity():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['readoutsensitivity']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.readout_sensitivity(dobj)
        else:
            assert dcmio.readout_sensitivity(dobj) == approx(value, abs=1e-7), scan


def test_coil_elements():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['coilelements']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.coil_elements(dobj)
        else:
            assert dcmio.coil_elements(dobj) == value, scan


def test_rescale_slope_and_intercept():
    for scan, info in SCANS.items():
        dobj, value = info['dobj'], info['rescaleslopeandintercept']
        if isinstance(value, type) and isinstance(value(), Exception):
            with raises(value):
                dcmio.rescale_slope_and_intercept(dobj)
        else:
            assert dcmio.rescale_slope_and_intercept(dobj) == approx(value), scan


def test_rx_coil_id():
    with raises(KeyError):
        dcmio.rx_coil_id(SCANS['ge_scout']['dobj'])
    with raises(KeyError):
        dcmio.rx_coil_id(SCANS['philips_se']['dobj'])

    assert dcmio.rx_coil_id(SCANS['siemens_scout']['dobj']) == 'Head_32'
    assert dcmio.rx_coil_id(SCANS['siemens_se']['dobj']) == 'Head_32'
    assert dcmio.rx_coil_id(SCANS['siemens_se_dis2d']['dobj']) == 'HeadNeck_20'
    assert dcmio.rx_coil_id(SCANS['siemens_ve11_noise']['dobj']) == 'HeadNeck_20'
    assert dcmio.rx_coil_id(SCANS['siemens_vb17_single']['dobj']) == 'HeadMatrix'
    assert dcmio.rx_coil_id(SCANS['siemens_vb17_pca_phase']['dobj']) == ''
    assert dcmio.rx_coil_id(SCANS['siemens_vb17_pca_magn']['dobj']) == ''
    assert dcmio.rx_coil_id(SCANS['siemens_xa11a_enhanced_se']['dobj']) == 'HeadNeck_20_TCS'
    assert dcmio.rx_coil_id(SCANS['siemens_xa11a_enhanced_se_norm_dc']['dobj']) == 'HeadNeck_20_TCS'
    assert dcmio.rx_coil_id(SCANS['siemens_xa11a_interop_se']['dobj']) == 'HeadNeck_20_TCS'
    assert dcmio.rx_coil_id(SCANS['siemens_xa20_pca_phase']['dobj']) == 'Body_18'
    assert dcmio.rx_coil_id(SCANS['siemens_xa20_pca_magn']['dobj']) == 'Body_18'
    assert dcmio.rx_coil_id(SCANS['siemens_xa20_fid']['dobj']) == 'HeadNeck_20_TCS'
    assert dcmio.rx_coil_id(SCANS['siemens_xa20_svs']['dobj']) == 'HeadNeck_20_TCS'
    assert dcmio.rx_coil_id(SCANS['siemens-xa30-mfsplit-pca-phase']['dobj']) == 'Body_18'
    assert dcmio.rx_coil_id(SCANS['siemens-xa30-mfsplit-pca-magn']['dobj']) == 'Body_18'
    assert dcmio.rx_coil_id(SCANS['siemens-xa30-mfsplit-se-norm-dis2d']['dobj']) == 'HeadNeck_20'
    assert dcmio.rx_coil_id(SCANS['siemens-xa30-mfsplit-se-norm-nd']['dobj']) == 'HeadNeck_20'


def test_is_distortion_corrected():
    with raises(KeyError):
        dcmio.is_distortion_corrected(SCANS['ge_scout']['dobj'])
    with raises(KeyError):
        dcmio.is_distortion_corrected(SCANS['ge_memp']['dobj'])
    with raises(KeyError):
        dcmio.is_distortion_corrected(SCANS['ge_fgre']['dobj'])
    with raises(KeyError):
        dcmio.is_distortion_corrected(SCANS['ge_efgre3d']['dobj'])

    assert dcmio.is_distortion_corrected(SCANS['philips_se']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['philips_tse']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['philips_epi']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['philips_epse']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['philips_std']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['philips_survey']['dobj']) is True

    assert dcmio.is_distortion_corrected(SCANS['siemens_scout']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['siemens_se']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['siemens_se_dis2d']['dobj']) is True
    assert dcmio.is_distortion_corrected(SCANS['siemens_ve11_noise']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['siemens_vb17_single']['dobj']) is False

    assert dcmio.is_distortion_corrected(SCANS['siemens_vb17_pca_phase']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['siemens_vb17_pca_magn']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['siemens_xa11a_enhanced_se']['dobj']) is False
    assert dcmio.is_distortion_corrected(SCANS['siemens_xa11a_enhanced_se_norm_dc']['dobj']) is True
    assert dcmio.is_distortion_corrected(SCANS['siemens_xa11a_interop_se']['dobj']) is False

    assert dcmio.is_distortion_corrected(SCANS['siemens_xa20_pca_phase']['dobj']) is True
    assert dcmio.is_distortion_corrected(SCANS['siemens_xa20_pca_magn']['dobj']) is True

    assert dcmio.is_distortion_corrected(SCANS['siemens-xa30-mfsplit-pca-phase']['dobj']) is True
    assert dcmio.is_distortion_corrected(SCANS['siemens-xa30-mfsplit-pca-magn']['dobj']) is True
    assert dcmio.is_distortion_corrected(SCANS['siemens-xa30-mfsplit-se-norm-dis2d']['dobj']) is True
    assert dcmio.is_distortion_corrected(SCANS['siemens-xa30-mfsplit-se-norm-nd']['dobj']) is False


def test_is_uniformity_corrected():
    with raises(KeyError):
        dcmio.is_uniformity_corrected(SCANS['ge_scout']['dobj'])
    with raises(KeyError):
        dcmio.is_uniformity_corrected(SCANS['philips_se']['dobj'])

    assert dcmio.is_uniformity_corrected(SCANS['siemens_scout']['dobj']) is True
    assert dcmio.is_uniformity_corrected(SCANS['siemens_se']['dobj']) is False
    assert dcmio.is_uniformity_corrected(SCANS['siemens_se_dis2d']['dobj']) is True
    assert dcmio.is_uniformity_corrected(SCANS['siemens_ve11_noise']['dobj']) is False
    assert dcmio.is_uniformity_corrected(SCANS['siemens_vb17_single']['dobj']) is False

    assert dcmio.is_uniformity_corrected(SCANS['siemens_vb17_pca_phase']['dobj']) is False
    assert dcmio.is_uniformity_corrected(SCANS['siemens_vb17_pca_magn']['dobj']) is False
    assert dcmio.is_uniformity_corrected(SCANS['siemens_xa11a_enhanced_se']['dobj']) is False
    assert dcmio.is_uniformity_corrected(SCANS['siemens_xa11a_enhanced_se_norm_dc']['dobj']) is True
    assert dcmio.is_uniformity_corrected(SCANS['siemens_xa11a_interop_se']['dobj']) is False
    assert dcmio.is_uniformity_corrected(SCANS['siemens_xa20_pca_phase']['dobj']) is False
    assert dcmio.is_uniformity_corrected(SCANS['siemens_xa20_pca_magn']['dobj']) is False

    assert dcmio.is_uniformity_corrected(SCANS['siemens-xa30-mfsplit-pca-phase']['dobj']) is False
    assert dcmio.is_uniformity_corrected(SCANS['siemens-xa30-mfsplit-pca-magn']['dobj']) is False
    assert dcmio.is_uniformity_corrected(SCANS['siemens-xa30-mfsplit-se-norm-dis2d']['dobj']) is False
    assert dcmio.is_uniformity_corrected(SCANS['siemens-xa30-mfsplit-se-norm-nd']['dobj']) is False


def test_flow_venc():
    with raises(KeyError):
        dcmio.flow_venc(SCANS['ge_scout']['dobj'])
    with raises(KeyError):
        dcmio.flow_venc(SCANS['ge_memp']['dobj'])
    with raises(KeyError):
        dcmio.flow_venc(SCANS['ge_fgre']['dobj'])
    with raises(KeyError):
        dcmio.flow_venc(SCANS['ge_efgre3d']['dobj'])

    assert dcmio.flow_venc(SCANS['philips_se']['dobj']) == 0
    assert dcmio.flow_venc(SCANS['philips_tse']['dobj']) == 0
    assert dcmio.flow_venc(SCANS['philips_epi']['dobj']) == 0
    assert dcmio.flow_venc(SCANS['philips_epse']['dobj']) == 0
    with raises(KeyError):
        dcmio.flow_venc(SCANS['philips_std']['dobj'])

    assert dcmio.flow_venc(SCANS['siemens_scout']['dobj']) == 0
    assert dcmio.flow_venc(SCANS['siemens_se']['dobj']) == 0
    assert dcmio.flow_venc(SCANS['siemens_se_dis2d']['dobj']) == 0
    assert dcmio.flow_venc(SCANS['siemens_ve11_noise']['dobj']) == 0
    assert dcmio.flow_venc(SCANS['siemens_vb17_single']['dobj']) == 0

    assert dcmio.flow_venc(SCANS['siemens_vb17_pca_phase']['dobj']) == 200
    assert dcmio.flow_venc(SCANS['siemens_vb17_pca_magn']['dobj']) == 0

    assert dcmio.flow_venc(SCANS['siemens_xa20_pca_phase']['dobj']) == 200
    assert dcmio.flow_venc(SCANS['siemens_xa20_pca_magn']['dobj']) == 0
    assert dcmio.flow_venc(SCANS['siemens-xa30-mfsplit-pca-phase']['dobj']) == 200
    assert dcmio.flow_venc(SCANS['siemens-xa30-mfsplit-pca-magn']['dobj']) == 200


def test_trigger_time():
    with raises(KeyError):
        dcmio.trigger_time(SCANS['ge_scout']['dobj'])
    with raises(KeyError):
        dcmio.trigger_time(SCANS['ge_memp']['dobj'])
    with raises(KeyError):
        dcmio.trigger_time(SCANS['ge_fgre']['dobj'])
    with raises(KeyError):
        dcmio.trigger_time(SCANS['ge_efgre3d']['dobj'])
    with raises(KeyError):
        dcmio.trigger_time(SCANS['philips_se']['dobj'])
    with raises(KeyError):
        dcmio.trigger_time(SCANS['philips_tse']['dobj'])
    with raises(KeyError):
        dcmio.trigger_time(SCANS['philips_epi']['dobj'])
    with raises(KeyError):
        dcmio.trigger_time(SCANS['philips_epse']['dobj'])
    with raises(KeyError):
        dcmio.trigger_time(SCANS['philips_std']['dobj'])

    assert dcmio.trigger_time(SCANS['siemens_scout']['dobj']) == 0
    assert dcmio.trigger_time(SCANS['siemens_se']['dobj']) == 0
    assert dcmio.trigger_time(SCANS['siemens_se_dis2d']['dobj']) == 0
    assert dcmio.trigger_time(SCANS['siemens_ve11_noise']['dobj']) == 0
    assert dcmio.trigger_time(SCANS['siemens_vb17_single']['dobj']) == 0

    assert dcmio.trigger_time(SCANS['siemens_vb17_pca_phase']['dobj']) == 400
    assert dcmio.trigger_time(SCANS['siemens_vb17_pca_magn']['dobj']) == 400

    mf_times = [
        0.0, 55.55555725097656, 111.11111450195312,
        166.6666717529297, 222.22222900390625, 277.77777099609375,
        333.3333435058594, 388.888916015625, 444.4444580078125,
        500.0, 555.5555419921875, 611.1111450195312,
        666.6666870117188, 722.2222290039062, 777.77783203125,
        833.3333740234375, 888.888916015625, 944.4444580078125
    ]
    assert dcmio.trigger_time(SCANS['siemens_xa20_pca_phase']['dobj']) == mf_times
    assert dcmio.trigger_time(SCANS['siemens_xa20_pca_magn']['dobj']) == mf_times


def test_spectroscopy_data():
    fid_data = dcmio.spectroscopy_data(SCANS['siemens_ve11_fid']['dobj'])
    assert len(fid_data) == 2048
    assert fid_data.dtype == np.complex128

    svs_data = dcmio.spectroscopy_data(SCANS['siemens_ve11_svs_se']['dobj'])
    assert len(svs_data) == 2048
    assert svs_data.dtype == np.complex128

    fid_data = dcmio.spectroscopy_data(SCANS['siemens_xa20_fid']['dobj'])
    assert len(fid_data) == 1024
    assert fid_data.dtype == np.complex128

    svs_data = dcmio.spectroscopy_data(SCANS['siemens_xa20_svs']['dobj'])
    assert len(svs_data) == 1024
    assert svs_data.dtype == np.complex128

    with raises(KeyError):
        dcmio.spectroscopy_data(SCANS['ge_memp']['dobj'])
    with raises(KeyError):
        dcmio.spectroscopy_data(SCANS['philips_se']['dobj'])
    with raises(KeyError):
        dcmio.spectroscopy_data(SCANS['siemens_se']['dobj'])


def test_dwell_time():
    with raises(KeyError):
        dcmio.dwell_time(SCANS['ge_memp']['dobj'])
    with raises(KeyError):
        dcmio.dwell_time(SCANS['philips_se']['dobj'])

    assert (
        dcmio.dwell_time(SCANS['siemens_se']['dobj']) == approx(0.0075, abs=1e-7)
    )

    assert (
        dcmio.dwell_time(SCANS['siemens_ve11_fid']['dobj']) == approx(0.8334, abs=1e-7)
    )
    assert (
        dcmio.dwell_time(SCANS['siemens_ve11_svs_se']['dobj']) == approx(0.8334, abs=1e-7)
    )

    assert (
        dcmio.dwell_time(SCANS['siemens_xa20_fid']['dobj']) == approx(1.0, abs=1e-7)
    )
    assert (
        dcmio.dwell_time(SCANS['siemens_xa20_svs']['dobj']) == approx(1.0, abs=1e-7)
    )


def test_gradient_sensitivities():
    with raises(KeyError):
        dcmio.gradient_sensitivities(SCANS['ge_memp']['dobj'])
    with raises(KeyError):
        dcmio.gradient_sensitivities(SCANS['philips_se']['dobj'])

    assert (
        dcmio.gradient_sensitivities(SCANS['siemens_se']['dobj']) ==
        approx((89.481596660e-6, 89.0809023986e-6, 89.18689854910001e-6))
    )

    assert (
        dcmio.gradient_sensitivities(SCANS['siemens_ve11_fid']['dobj']) ==
        approx((89.3965989235e-6, 88.6356720002e-6, 87.5303812791e-6))
    )

    assert (
        dcmio.gradient_sensitivities(SCANS['siemens_ve11_svs_se']['dobj']) ==
        approx((89.3965989235e-6, 88.6356720002e-6, 87.5303812791e-6))
    )

    assert (
        dcmio.gradient_sensitivities(SCANS['siemens_xa20_fid']['dobj']) ==
        approx((90.4085973161e-6, 92.1746031963e-6, 92.16739999832e-6))
    )

    assert (
        dcmio.gradient_sensitivities(SCANS['siemens_xa20_svs']['dobj']) ==
        approx((90.4085973161e-6, 92.1746031963e-6, 92.16739999832e-6))
    )


def test_transmitter_calibration():
    with raises(KeyError):
        dcmio.transmitter_calibration(SCANS['ge_memp']['dobj'])
    with raises(KeyError):
        dcmio.transmitter_calibration(SCANS['philips_se']['dobj'])

    assert (
        dcmio.transmitter_calibration(SCANS['siemens_se']['dobj']) ==
        approx(341.94665, abs=1e-7)
    )

    assert (
        dcmio.transmitter_calibration(SCANS['siemens_ve11_fid']['dobj']) ==
        approx(346.419373, abs=1e-7)
    )
    assert (
        dcmio.transmitter_calibration(SCANS['siemens_ve11_svs_se']['dobj']) ==
        approx(353.213106, abs=1e-7)
    )

    assert (
        dcmio.transmitter_calibration(SCANS['siemens_xa20_fid']['dobj']) ==
        approx(292.073, abs=1e-7)
    )
    assert (
        dcmio.transmitter_calibration(SCANS['siemens_xa20_svs']['dobj']) ==
        approx(292.073, abs=1e-7)
    )


def test_tales_reference_power():
    with raises(KeyError):
        dcmio.tales_reference_power(SCANS['ge_memp']['dobj'])
    with raises(KeyError):
        dcmio.tales_reference_power(SCANS['philips_se']['dobj'])

    assert (
        dcmio.tales_reference_power(SCANS['siemens_se']['dobj']) ==
        approx(1637.857225, abs=1e-7)
    )
    assert (
        dcmio.tales_reference_power(SCANS['siemens_ve11_fid']['dobj']) ==
        approx(1869.31369534, abs=1e-7)
    )
    assert (
        dcmio.tales_reference_power(SCANS['siemens_ve11_svs_se']['dobj']) ==
        approx(1951.20987, abs=1e-7)
    )

    assert (
        dcmio.tales_reference_power(SCANS['siemens_xa20_fid']['dobj']) ==
        approx(1245.87, abs=1e-7)
    )
    assert (
        dcmio.tales_reference_power(SCANS['siemens_xa20_svs']['dobj']) ==
        approx(1245.87, abs=1e-7)
    )


def test_diffusion_bvalue():
    assert (
        dcmio.diffusion_bvalue(SCANS['siemens_ve_diffusion_dwi']['dobj']) ==
        approx(2000, abs=1e-7)
    )
    assert (
        dcmio.diffusion_bvalue(SCANS['siemens_ve_diffusion_adc']['dobj']) ==
        approx(2000, abs=1e-7)
    )
    assert (
        dcmio.diffusion_bvalue(SCANS['siemens_xa_diffusion_dwi']['dobj']) ==
        approx(900, abs=1e-7)
    )
    with raises(KeyError):
        dcmio.diffusion_bvalue(SCANS['siemens_xa_diffusion_adc']['dobj'])

    assert (
        dcmio.diffusion_bvalue(SCANS['ge_diffusion_dwi']['dobj']) ==
        approx(900, abs=1e-7)
    )
    with raises(KeyError):
        dcmio.diffusion_bvalue(SCANS['ge_diffusion_adc']['dobj'])

    assert (
        dcmio.diffusion_bvalue(SCANS['philips_diffusion_dwi']['dobj']) ==
        approx(2000, abs=1e-7)
    )
    with raises(KeyError):
        dcmio.diffusion_bvalue(SCANS['philips_diffusion_adc']['dobj'])


def test_recon_scale_factor():
    with raises(KeyError):
        dcmio.recon_scale_factor(SCANS['ge_scout']['dobj'])
    with raises(KeyError):
        dcmio.recon_scale_factor(SCANS['ge_memp']['dobj'])
    with raises(KeyError):
        dcmio.recon_scale_factor(SCANS['ge_fgre']['dobj'])
    with raises(KeyError):
        dcmio.recon_scale_factor(SCANS['ge_efgre3d']['dobj'])

    with raises(KeyError):
        dcmio.recon_scale_factor(SCANS['philips_se']['dobj'])
    with raises(KeyError):
        dcmio.recon_scale_factor(SCANS['philips_tse']['dobj'])
    with raises(KeyError):
        dcmio.recon_scale_factor(SCANS['philips_epi']['dobj'])
    with raises(KeyError):
        dcmio.recon_scale_factor(SCANS['philips_epse']['dobj'])
    with raises(KeyError):
        dcmio.recon_scale_factor(SCANS['philips_std']['dobj'])

    assert dcmio.recon_scale_factor(SCANS['siemens_scout']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens_se']['dobj']) == 2.0
    assert dcmio.recon_scale_factor(SCANS['siemens_se_dis2d']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens_vb17_single']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens_ve11_noise']['dobj']) == 40.0
    assert dcmio.recon_scale_factor(SCANS['siemens_vb17_pca_phase']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens_vb17_pca_magn']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens_xa11a_enhanced_se']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens_xa11a_enhanced_se_norm_dc']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens_xa11a_interop_se']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens_xa20_pca_phase']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens_xa20_pca_magn']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens-xa30-mfsplit-pca-phase']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens-xa30-mfsplit-pca-magn']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens-xa30-mfsplit-se-norm-dis2d']['dobj']) == 1.0
    assert dcmio.recon_scale_factor(SCANS['siemens-xa30-mfsplit-se-norm-nd']['dobj']) == 1.0


def test_update_unknown_vrs():
    dobj = SCANS['philips_un_vr']['dobj']
    dcmio.update_unknown_vrs(dobj)
    pffgs = dobj.PerFrameFunctionalGroupsSequence[0]
    assert pffgs[0x2005, 0x140F].VR == 'SQ'
    priv_sequence = pffgs[0x2005, 0x140F].value
    assert len(priv_sequence) == 1
    chem_shift_tag = priv_sequence[0][0x2001, 0x1001]
    assert chem_shift_tag.VR == 'FL'
    assert chem_shift_tag.value == 1.0


def test_augment_private_dictionaries():
    dcmio.augment_private_dictionaries()
    assert (
        get_private_entry(0x00211033, private_creator='SIEMENS MR SDS 01') ==
        ('SH', '1', 'CoilForGradient2', '')
    )
    assert (
        get_private_entry(0x00211148, private_creator='SIEMENS MR SDI 02') ==
        ('IS', '1', 'EchoPartitionPosition', '')
    )
    assert (
        get_private_entry(0x20051553, private_creator='Philips MR Imaging DD 006') ==
        ('FL', '1', 'MREFrequency', '')
    )
