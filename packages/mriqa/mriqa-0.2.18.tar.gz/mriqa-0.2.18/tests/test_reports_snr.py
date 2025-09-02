from pytest import fixture, approx
import sys
from glob import glob

from pydicom import dcmread
import matplotlib as mpl

mpl.use("Agg")
sys.path.append('..')

from mriqa.tools import rx_coil_string
from mriqa.reports import snr

scans = {}


@fixture(scope='module', autouse=True)
def setup_function():
    global scans
    scans['signal_combined_a'] = [
        dcmread(f) for f in glob('test-data/longbottle/signal_combined/a/*.dcm')
        ]
    scans['signal_combined_b'] = [
        dcmread(f) for f in glob('test-data/longbottle/signal_combined/b/*.dcm')
    ]
    scans['signal_per_element_a'] = [
        dcmread(f) for f in glob('test-data/longbottle/signal_per_element/a/*.dcm')
    ]
    scans['signal_per_element_b'] = [
        dcmread(f) for f in glob('test-data/longbottle/signal_per_element/b/*.dcm')
    ]
    scans['noise_combined_a'] = [
        dcmread(f) for f in glob('test-data/longbottle/noise_combined/a/*.dcm')
        ]
    scans['noise_combined_b'] = [
        dcmread(f) for f in glob('test-data/longbottle/noise_combined/b/*.dcm')
    ]
    scans['noise_per_element_a'] = [
        dcmread(f) for f in glob('test-data/longbottle/noise_per_element/a/*.dcm')
    ]
    scans['noise_per_element_b'] = [
        dcmread(f) for f in glob('test-data/longbottle/noise_per_element/b/*.dcm')
    ]


def test_snr_report():
    df_1 = snr.snr_report(scans['signal_combined_a'], scans['signal_combined_b'])
    df_2 = snr.snr_report(scans['signal_combined_a'] + scans['signal_combined_b'])
    assert all(s_1 == s_2 for s_1, s_2 in zip(df_1, df_2))
    coil = rx_coil_string(scans['signal_combined_a'][0])
    assert coil == 'Head_32'
    assert tuple(df_1[coil]) == approx((422.0443844834035, 514.1391410142088))


def test_noise_correlation_report():
    df_1 = snr.noise_correlation_report(scans['noise_per_element_a'], scans['noise_per_element_b'])
    assert df_1.MinCorrelation.iloc[0] == approx(-58.029201, abs=0.1)
    assert df_1.MaxCorrelation.iloc[0] == approx(4355.434911, abs=0.1)
    assert df_1.DiagonalVariance.iloc[0] == approx(0.007191, abs=1e-3)
    assert df_1.MaximumOffDiagonal.iloc[0] == approx(0.239197, abs=1e-3)


def test_noise_statistics_report_multichannel():
    df_1 = snr.noise_statistics_report_multichannel(scans['noise_per_element_a'])
    df_2 = snr.noise_statistics_report_multichannel(scans['noise_per_element_b'])
    assert df_1.Channels.iloc[0] == 32
    assert df_2.Channels.iloc[0] == 32
    assert df_1.DegreesOfFreedom.iloc[0] == approx(63.17, abs=0.1)
    assert df_2.DegreesOfFreedom.iloc[0] == approx(63.56, abs=0.1)
    assert df_1.Scale.iloc[0] == approx(70.82, abs=0.1)
    assert df_2.Scale.iloc[0] == approx(70.58, abs=0.1)


def test_noise_statistics_report_combined():
    df_1 = snr.noise_statistics_report_combined(scans['noise_combined_a'][0])
    df_2 = snr.noise_statistics_report_combined(scans['noise_combined_b'][0])
    assert df_1.DegreesOfFreedom.iloc[0] == approx(59.82, abs=0.1)
    assert df_2.DegreesOfFreedom.iloc[0] == approx(58.01, abs=0.1)
    assert df_1.Scale.iloc[0] == approx(73.05, abs=0.1)
    assert df_2.Scale.iloc[0] == approx(74.16, abs=0.1)


def test_snr_report_multi():
    df_1 = snr.snr_report_multi(scans['signal_per_element_a'], scans['signal_per_element_b'])
    coil = rx_coil_string(scans['signal_combined_a'][0])
    assert coil == 'Head_32'
    assert tuple(df_1[coil]) == approx((422.2387292673857, 514.5961138829922))
