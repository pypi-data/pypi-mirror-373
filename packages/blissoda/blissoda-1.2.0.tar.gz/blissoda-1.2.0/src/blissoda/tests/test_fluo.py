import sys

import pytest

from ..fluo.parameters.offline import fluoxas_parameters
from ..fluo.parameters.offline import mosaic_xrfmap_parameters
from ..fluo.parameters.offline import xrfmap_parameters


@pytest.mark.skipif(
    sys.platform == "win32", reason="Skipping fluo path tests on windows"
)
def test_xrfmap_single_detector():
    workflow_path, inputs, convert_destination = xrfmap_parameters(
        session="/data/visitor/blc16198/id16b/20250527",
        sample="test",
        dataset="9147_136783",
        scan_number=30,
        config_filenames=["fit.cfg"],
        detector_numbers=[8],
        instrument_name="id16b",
        demo=False,
    )
    eworkflow_path = "/data/visitor/blc16198/id16b/20250527/SCRIPTS/ewoks_results/workflows/xrfmap_single_detector.ows"
    econvert_destination = "/data/visitor/blc16198/id16b/20250527/PROCESSED_DATA/ewoks_results/test_9147_136783_scan0030.json"
    einputs = [
        {
            "name": "filename",
            "value": "/data/visitor/blc16198/id16b/20250527/RAW_DATA/test/test_9147_136783/test_9147_136783.h5",
            "task_identifier": "PickScan",
        },
        {"name": "scan_number", "value": 30, "task_identifier": "PickScan"},
        {
            "name": "output_root_uri",
            "value": "/data/visitor/blc16198/id16b/20250527/PROCESSED_DATA/ewoks_results/test_9147_136783.h5::/30.1",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "config",
            "value": "/data/visitor/blc16198/id16b/20250527/SCRIPTS/pymca/fit.cfg",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "fast_fitting",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "quantification",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "diagnostics",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "detector_name",
            "value": "fxb_det8",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "energy_name",
            "value": "Edcm",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "counter_name",
            "value": None,
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "counter_normalization_template",
            "value": None,
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "detector_normalization_template",
            "value": "0.1/<instrument/{}/live_time>",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "axes_units",
            "value": {"samy": "mm", "samz": "mm", "sampy": "um", "sampz": "um"},
            "task_identifier": "RegridXrfResults",
        },
        {
            "name": "ignore_positioners",
            "task_identifier": "RegridXrfResults",
            "value": [],
        },
        {"name": "resolution", "value": None, "task_identifier": "RegridXrfResults"},
    ]

    assert workflow_path == eworkflow_path
    assert convert_destination == econvert_destination
    assert inputs == einputs


@pytest.mark.skipif(
    sys.platform == "win32", reason="Skipping fluo path tests on windows"
)
def test_xrfmap_sum_spectra():
    workflow_path, inputs, convert_destination = xrfmap_parameters(
        session="/data/visitor/ls3288/id21/20240221",
        sample="DIV15_10uM_2",
        dataset="roi75698_90925",
        scan_number=1,
        config_filenames=["sample_10200ev_sheldon.cfg"],
        detector_numbers=[0, 1, 2, 3, 4],
        instrument_name="id21_nano",
        demo=False,
    )
    eworkflow_path = "/data/visitor/ls3288/id21/20240221/SCRIPTS/ewoks_results/workflows/xrfmap_multi_detector_sumspectra.ows"
    econvert_destination = "/data/visitor/ls3288/id21/20240221/PROCESSED_DATA/ewoks_results/DIV15_10uM_2_roi75698_90925_scan0001.json"
    einputs = [
        {
            "name": "filename",
            "value": "/data/visitor/ls3288/id21/20240221/RAW_DATA/DIV15_10uM_2/DIV15_10uM_2_roi75698_90925/DIV15_10uM_2_roi75698_90925.h5",
            "task_identifier": "PickScan",
        },
        {"name": "scan_number", "value": 1, "task_identifier": "PickScan"},
        {
            "name": "detector_names",
            "value": [
                "fx_nano_det0",
                "fx_nano_det1",
                "fx_nano_det2",
                "fx_nano_det3",
                "fx_nano_det4",
            ],
            "task_identifier": "SumXrfSpectra",
        },
        {
            "name": "output_root_uri",
            "value": "/data/visitor/ls3288/id21/20240221/PROCESSED_DATA/ewoks_results/DIV15_10uM_2_roi75698_90925.h5::/1.1",
            "task_identifier": "SumXrfSpectra",
        },
        {
            "name": "detector_normalization_template",
            "value": "0.1/<instrument/{}/live_time>",
            "task_identifier": "SumXrfSpectra",
        },
        {
            "name": "config",
            "value": "/data/visitor/ls3288/id21/20240221/SCRIPTS/pymca/sample_10200ev_sheldon.cfg",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "fast_fitting",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "quantification",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "diagnostics",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "energy_name",
            "value": "Edcm",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "counter_name",
            "value": "niodet",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "counter_normalization_template",
            "value": "np.nanmean(<instrument/{}/data>)/<instrument/{}/data>",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "axes_units",
            "value": {"nsy": "mm", "nsz": "mm", "nspy": "um", "nspz": "um"},
            "task_identifier": "RegridXrfResults",
        },
        {
            "name": "ignore_positioners",
            "value": ["nsz1", "nsz2", "nsz3"],
            "task_identifier": "RegridXrfResults",
        },
        {"name": "resolution", "value": None, "task_identifier": "RegridXrfResults"},
    ]

    assert workflow_path == eworkflow_path
    assert convert_destination == econvert_destination
    assert inputs == einputs


@pytest.mark.skipif(
    sys.platform == "win32", reason="Skipping fluo path tests on windows"
)
def test_xrfmap_sum_results():
    workflow_path, inputs, convert_destination = xrfmap_parameters(
        session="/data/visitor/ls3288/id21/20240221",
        sample="DIV15_10uM_2",
        dataset="roi75698_90925",
        scan_number=1,
        config_filenames=[
            "sample_10200ev_sheldon.cfg",
            "sample_10200ev_sheldon.cfg",
            "sample_10200ev_sheldon.cfg",
            "sample_10200ev_sheldon.cfg",
            "sample_10200ev_sheldon.cfg",
        ],
        detector_numbers=[0, 1, 2, 3, 4],
        instrument_name="id21_nano",
        demo=False,
    )

    eworkflow_path = "/data/visitor/ls3288/id21/20240221/SCRIPTS/ewoks_results/workflows/xrfmap_multi_detector.ows"
    econvert_destination = "/data/visitor/ls3288/id21/20240221/PROCESSED_DATA/ewoks_results/DIV15_10uM_2_roi75698_90925_scan0001.json"
    einputs = [
        {
            "name": "filename",
            "value": "/data/visitor/ls3288/id21/20240221/RAW_DATA/DIV15_10uM_2/DIV15_10uM_2_roi75698_90925/DIV15_10uM_2_roi75698_90925.h5",
            "task_identifier": "PickScan",
        },
        {"name": "scan_number", "value": 1, "task_identifier": "PickScan"},
        {
            "name": "output_root_uri",
            "value": "/data/visitor/ls3288/id21/20240221/PROCESSED_DATA/ewoks_results/DIV15_10uM_2_roi75698_90925.h5::/1.1",
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "configs",
            "value": [
                "/data/visitor/ls3288/id21/20240221/SCRIPTS/pymca/sample_10200ev_sheldon.cfg",
                "/data/visitor/ls3288/id21/20240221/SCRIPTS/pymca/sample_10200ev_sheldon.cfg",
                "/data/visitor/ls3288/id21/20240221/SCRIPTS/pymca/sample_10200ev_sheldon.cfg",
                "/data/visitor/ls3288/id21/20240221/SCRIPTS/pymca/sample_10200ev_sheldon.cfg",
                "/data/visitor/ls3288/id21/20240221/SCRIPTS/pymca/sample_10200ev_sheldon.cfg",
            ],
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "fast_fitting",
            "value": True,
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "quantification",
            "value": True,
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "diagnostics",
            "value": True,
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "detector_names",
            "value": [
                "fx_nano_det0",
                "fx_nano_det1",
                "fx_nano_det2",
                "fx_nano_det3",
                "fx_nano_det4",
            ],
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "energy_name",
            "value": "Edcm",
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "detector_normalization_template",
            "value": "0.1/<instrument/{}/live_time>",
            "task_identifier": "SumXrfResults",
        },
        {
            "name": "counter_name",
            "value": "niodet",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "counter_normalization_template",
            "value": "np.nanmean(<instrument/{}/data>)/<instrument/{}/data>",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "axes_units",
            "value": {"nsy": "mm", "nsz": "mm", "nspy": "um", "nspz": "um"},
            "task_identifier": "RegridXrfResults",
        },
        {
            "name": "ignore_positioners",
            "value": ["nsz1", "nsz2", "nsz3"],
            "task_identifier": "RegridXrfResults",
        },
        {"name": "resolution", "value": None, "task_identifier": "RegridXrfResults"},
    ]

    assert workflow_path == eworkflow_path
    assert convert_destination == econvert_destination
    assert inputs == einputs


@pytest.mark.skipif(
    sys.platform == "win32", reason="Skipping fluo path tests on windows"
)
def test_mosaic_xrfmap_single_detector():
    workflow_path, inputs, convert_destination = mosaic_xrfmap_parameters(
        session="/data/visitor/blc15972/id21/20250128",
        sample="Cd250",
        datasets=["roi106394_124471", "roi106393_124470"],
        scan_ranges=[(1, 1), (1, 1)],
        config_filenames=["config_9800ev.cfg"],
        detector_numbers=[0],
        instrument_name="id21_nano",
        resolution={"sy": (1, "um"), "sz": (1, "um")},
        demo=False,
    )

    eworkflow_path = "/data/visitor/blc15972/id21/20250128/SCRIPTS/ewoks_results/workflows/mosaic_single_detector.ows"
    econvert_destination = "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_scan0001.json"
    einputs = [
        {
            "name": "filenames",
            "value": [
                "/data/visitor/blc15972/id21/20250128/RAW_DATA/Cd250/Cd250_roi106394_124471/Cd250_roi106394_124471.h5",
                "/data/visitor/blc15972/id21/20250128/RAW_DATA/Cd250/Cd250_roi106393_124470/Cd250_roi106393_124470.h5",
            ],
            "task_identifier": "PickScans",
        },
        {
            "name": "scan_ranges",
            "value": [(1, 1), (1, 1)],
            "task_identifier": "PickScans",
        },
        {"name": "exclude_scans", "value": [(), ()], "task_identifier": "PickScans"},
        {
            "name": "bliss_scan_uri",
            "value": "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_concat.h5::/1.1",
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "output_root_uri",
            "value": "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_results.h5::/1.1",
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "output_root_uri",
            "value": "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_results.h5::/1.1",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "config",
            "value": "/data/visitor/blc15972/id21/20250128/SCRIPTS/pymca/config_9800ev.cfg",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "fast_fitting",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "quantification",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "diagnostics",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "detector_name",
            "value": "fx_nano_det0",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "energy_name",
            "value": "Edcm",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "counter_name",
            "value": "niodet",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "counter_normalization_template",
            "value": "np.nanmean(<instrument/{}/data>)/<instrument/{}/data>",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "detector_normalization_template",
            "value": "0.1/<instrument/{}/live_time>",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "axes_units",
            "value": {"nsy": "mm", "nsz": "mm", "nspy": "um", "nspz": "um"},
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "virtual_axes",
            "value": {"sy": "<nsy>+<nspy>", "sz": "<nsz>+<nspz>"},
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "positioners",
            "value": ["sz", "sy"],
            "task_identifier": "RegridXrfResults",
        },
        {
            "name": "resolution",
            "value": {"sy": (1, "um"), "sz": (1, "um")},
            "task_identifier": "RegridXrfResults",
        },
    ]

    assert workflow_path == eworkflow_path
    assert convert_destination == econvert_destination
    assert inputs == einputs


@pytest.mark.skipif(
    sys.platform == "win32", reason="Skipping fluo path tests on windows"
)
def test_mosaic_xrfmap_sum_results():
    workflow_path, inputs, convert_destination = mosaic_xrfmap_parameters(
        session="/data/visitor/blc15972/id21/20250128",
        sample="Cd250",
        datasets=["roi106394_124471", "roi106393_124470"],
        scan_ranges=[(1, 1), (1, 1)],
        config_filenames=["config_9800ev.cfg", "config_9800ev.cfg"],
        detector_numbers=[0, 1],
        instrument_name="id21_nano",
        resolution={"sy": (1, "um"), "sz": (1, "um")},
        demo=False,
    )

    eworkflow_path = "/data/visitor/blc15972/id21/20250128/SCRIPTS/ewoks_results/workflows/mosaic_multi_detector.ows"
    econvert_destination = "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_scan0001.json"
    einputs = [
        {
            "name": "filenames",
            "value": [
                "/data/visitor/blc15972/id21/20250128/RAW_DATA/Cd250/Cd250_roi106394_124471/Cd250_roi106394_124471.h5",
                "/data/visitor/blc15972/id21/20250128/RAW_DATA/Cd250/Cd250_roi106393_124470/Cd250_roi106393_124470.h5",
            ],
            "task_identifier": "PickScans",
        },
        {
            "name": "scan_ranges",
            "value": [(1, 1), (1, 1)],
            "task_identifier": "PickScans",
        },
        {"name": "exclude_scans", "value": [(), ()], "task_identifier": "PickScans"},
        {
            "name": "bliss_scan_uri",
            "value": "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_concat.h5::/1.1",
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "output_root_uri",
            "value": "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_results.h5::/1.1",
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "output_root_uri",
            "value": "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_results.h5::/1.1",
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "configs",
            "value": [
                "/data/visitor/blc15972/id21/20250128/SCRIPTS/pymca/config_9800ev.cfg",
                "/data/visitor/blc15972/id21/20250128/SCRIPTS/pymca/config_9800ev.cfg",
            ],
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "fast_fitting",
            "value": True,
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "quantification",
            "value": True,
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "diagnostics",
            "value": True,
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "detector_names",
            "value": ["fx_nano_det0", "fx_nano_det1"],
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "energy_name",
            "value": "Edcm",
            "task_identifier": "FitSingleScanMultiDetector",
        },
        {
            "name": "detector_normalization_template",
            "value": "0.1/<instrument/{}/live_time>",
            "task_identifier": "SumXrfResults",
        },
        {
            "name": "counter_name",
            "value": "niodet",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "counter_normalization_template",
            "value": "np.nanmean(<instrument/{}/data>)/<instrument/{}/data>",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "axes_units",
            "value": {"nsy": "mm", "nsz": "mm", "nspy": "um", "nspz": "um"},
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "virtual_axes",
            "value": {"sy": "<nsy>+<nspy>", "sz": "<nsz>+<nspz>"},
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "positioners",
            "value": ["sz", "sy"],
            "task_identifier": "RegridXrfResults",
        },
        {
            "name": "resolution",
            "value": {"sy": (1, "um"), "sz": (1, "um")},
            "task_identifier": "RegridXrfResults",
        },
    ]

    assert workflow_path == eworkflow_path
    assert convert_destination == econvert_destination
    assert inputs == einputs


@pytest.mark.skipif(
    sys.platform == "win32", reason="Skipping fluo path tests on windows"
)
def test_mosaic_xrfmap_sum_spectra():
    workflow_path, inputs, convert_destination = mosaic_xrfmap_parameters(
        session="/data/visitor/blc15972/id21/20250128",
        sample="Cd250",
        datasets=["roi106394_124471", "roi106393_124470"],
        scan_ranges=[(1, 1), (1, 1)],
        config_filenames=["config_9800ev.cfg"],
        detector_numbers=[0, 1],
        instrument_name="id21_nano",
        resolution={"sy": (1, "um"), "sz": (1, "um")},
        demo=False,
    )

    eworkflow_path = "/data/visitor/blc15972/id21/20250128/SCRIPTS/ewoks_results/workflows/mosaic_multi_detector_sumspectra.ows"
    econvert_destination = "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_scan0001.json"
    einputs = [
        {
            "name": "filenames",
            "value": [
                "/data/visitor/blc15972/id21/20250128/RAW_DATA/Cd250/Cd250_roi106394_124471/Cd250_roi106394_124471.h5",
                "/data/visitor/blc15972/id21/20250128/RAW_DATA/Cd250/Cd250_roi106393_124470/Cd250_roi106393_124470.h5",
            ],
            "task_identifier": "PickScans",
        },
        {
            "name": "scan_ranges",
            "value": [(1, 1), (1, 1)],
            "task_identifier": "PickScans",
        },
        {"name": "exclude_scans", "value": [(), ()], "task_identifier": "PickScans"},
        {
            "name": "bliss_scan_uri",
            "value": "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_concat.h5::/1.1",
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "output_root_uri",
            "value": "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_results.h5::/1.1",
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "output_root_uri",
            "value": "/data/visitor/blc15972/id21/20250128/PROCESSED_DATA/ewoks_results/Cd250_roi106394_124471_results.h5::/1.1",
            "task_identifier": "SumXrfSpectra",
        },
        {
            "name": "detector_names",
            "value": ["fx_nano_det0", "fx_nano_det1"],
            "task_identifier": "SumXrfSpectra",
        },
        {
            "name": "detector_normalization_template",
            "value": "0.1/<instrument/{}/live_time>",
            "task_identifier": "SumXrfSpectra",
        },
        {
            "name": "config",
            "value": "/data/visitor/blc15972/id21/20250128/SCRIPTS/pymca/config_9800ev.cfg",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "fast_fitting",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "quantification",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "diagnostics",
            "value": True,
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "energy_name",
            "value": "Edcm",
            "task_identifier": "FitSingleScanSingleDetector",
        },
        {
            "name": "counter_name",
            "value": "niodet",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "counter_normalization_template",
            "value": "np.nanmean(<instrument/{}/data>)/<instrument/{}/data>",
            "task_identifier": "NormalizeXrfResults",
        },
        {
            "name": "axes_units",
            "value": {"nsy": "mm", "nsz": "mm", "nspy": "um", "nspz": "um"},
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "virtual_axes",
            "value": {"sy": "<nsy>+<nspy>", "sz": "<nsz>+<nspz>"},
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "positioners",
            "value": ["sz", "sy"],
            "task_identifier": "RegridXrfResults",
        },
        {
            "name": "resolution",
            "value": {"sy": (1, "um"), "sz": (1, "um")},
            "task_identifier": "RegridXrfResults",
        },
    ]

    assert workflow_path == eworkflow_path
    assert convert_destination == econvert_destination
    assert inputs == einputs


@pytest.mark.skipif(
    sys.platform == "win32", reason="Skipping fluo path tests on windows"
)
def test_fluoxas_single_detector():
    workflow_path, inputs, convert_destination = fluoxas_parameters(
        session="/data/visitor/ma5958/id21/20250207",
        sample="BaCrO4-com-o-aged-thin",
        datasets=["roi107244_125314"],
        scan_ranges=[[2, 3]],
        exclude_scans=[[]],
        config_filenames=["config_nano_6_3.cfg"],
        detector_numbers=[0],
        instrument_name="id21_nano",
        demo=False,
    )

    eworkflow_path = "/data/visitor/ma5958/id21/20250207/SCRIPTS/ewoks_results/workflows/fluoxas_single_detector_align.ows"
    econvert_destination = "/data/visitor/ma5958/id21/20250207/PROCESSED_DATA/ewoks_results/BaCrO4-com-o-aged-thin_roi107244_125314_scan0002.json"
    einputs = [
        {
            "name": "filenames",
            "value": [
                "/data/visitor/ma5958/id21/20250207/RAW_DATA/BaCrO4-com-o-aged-thin/BaCrO4-com-o-aged-thin_roi107244_125314/BaCrO4-com-o-aged-thin_roi107244_125314.h5"
            ],
            "task_identifier": "PickScans",
        },
        {"name": "scan_ranges", "value": [(2, 3)], "task_identifier": "PickScans"},
        {"name": "exclude_scans", "value": [[]], "task_identifier": "PickScans"},
        {
            "name": "output_root_uri",
            "value": "/data/visitor/ma5958/id21/20250207/PROCESSED_DATA/ewoks_results/BaCrO4-com-o-aged-thin_roi107244_125314.h5::/2.1",
            "task_identifier": "FitStackSingleDetector",
        },
        {
            "name": "config",
            "value": "/data/visitor/ma5958/id21/20250207/SCRIPTS/pymca/config_nano_6_3.cfg",
            "task_identifier": "FitStackSingleDetector",
        },
        {
            "name": "fast_fitting",
            "value": True,
            "task_identifier": "FitStackSingleDetector",
        },
        {
            "name": "quantification",
            "value": True,
            "task_identifier": "FitStackSingleDetector",
        },
        {
            "name": "diagnostics",
            "value": True,
            "task_identifier": "FitStackSingleDetector",
        },
        {
            "name": "detector_name",
            "value": "fx_nano_det0",
            "task_identifier": "FitStackSingleDetector",
        },
        {
            "name": "energy_name",
            "value": "Edcm",
            "task_identifier": "FitStackSingleDetector",
        },
        {
            "name": "counter_name",
            "value": "niodet",
            "task_identifier": "NormalizeXrfResultsStack",
        },
        {
            "name": "counter_normalization_template",
            "value": "np.nanmean(<instrument/{}/data>)/<instrument/{}/data>",
            "task_identifier": "NormalizeXrfResultsStack",
        },
        {
            "name": "detector_normalization_template",
            "value": "0.1/<instrument/{}/live_time>",
            "task_identifier": "NormalizeXrfResultsStack",
        },
        {
            "name": "axes_units",
            "value": {"nsy": "mm", "nsz": "mm", "nspy": "um", "nspz": "um"},
            "task_identifier": "RegridXrfResultsStack",
        },
        {
            "name": "ignore_positioners",
            "value": ["nsz1", "nsz2", "nsz3"],
            "task_identifier": "RegridXrfResultsStack",
        },
        {
            "name": "resolution",
            "value": None,
            "task_identifier": "RegridXrfResultsStack",
        },
        {
            "name": "reference_stack",
            "value": None,
            "task_identifier": "Reg2DPreEvaluation",
        },
        {"name": "skip", "value": True, "task_identifier": "Reg2DPreEvaluation"},
        {"name": "skip", "value": False, "task_identifier": "Reg2DPostEvaluation"},
        {"name": "crop", "value": True, "task_identifier": "Reg2DTransform"},
    ]

    assert workflow_path == eworkflow_path
    assert convert_destination == econvert_destination
    assert inputs == einputs


@pytest.mark.skipif(
    sys.platform == "win32", reason="Skipping fluo path tests on windows"
)
def test_fluoxas_sum_results():
    workflow_path, inputs, convert_destination = fluoxas_parameters(
        session="/data/visitor/ma5958/id21/20250207",
        sample="BaCrO4-com-o-aged-thin",
        datasets=["roi107244_125314"],
        scan_ranges=[[2, 3]],
        exclude_scans=[[]],
        config_filenames=["config_nano_6_3.cfg", "config_nano_6_3.cfg"],
        detector_numbers=[0, 1],
        instrument_name="id21_nano",
        demo=False,
    )

    eworkflow_path = "/data/visitor/ma5958/id21/20250207/SCRIPTS/ewoks_results/workflows/fluoxas_multi_detector_align.ows"
    econvert_destination = "/data/visitor/ma5958/id21/20250207/PROCESSED_DATA/ewoks_results/BaCrO4-com-o-aged-thin_roi107244_125314_scan0002.json"
    einputs = [
        {
            "name": "filenames",
            "value": [
                "/data/visitor/ma5958/id21/20250207/RAW_DATA/BaCrO4-com-o-aged-thin/BaCrO4-com-o-aged-thin_roi107244_125314/BaCrO4-com-o-aged-thin_roi107244_125314.h5"
            ],
            "task_identifier": "PickScans",
        },
        {"name": "scan_ranges", "value": [(2, 3)], "task_identifier": "PickScans"},
        {"name": "exclude_scans", "value": [[]], "task_identifier": "PickScans"},
        {
            "name": "output_root_uri",
            "value": "/data/visitor/ma5958/id21/20250207/PROCESSED_DATA/ewoks_results/BaCrO4-com-o-aged-thin_roi107244_125314.h5::/2.1",
            "task_identifier": "FitStackMultiDetector",
        },
        {
            "name": "configs",
            "value": [
                "/data/visitor/ma5958/id21/20250207/SCRIPTS/pymca/config_nano_6_3.cfg",
                "/data/visitor/ma5958/id21/20250207/SCRIPTS/pymca/config_nano_6_3.cfg",
            ],
            "task_identifier": "FitStackMultiDetector",
        },
        {
            "name": "fast_fitting",
            "value": True,
            "task_identifier": "FitStackMultiDetector",
        },
        {
            "name": "quantification",
            "value": True,
            "task_identifier": "FitStackMultiDetector",
        },
        {
            "name": "diagnostics",
            "value": True,
            "task_identifier": "FitStackMultiDetector",
        },
        {
            "name": "detector_names",
            "value": ["fx_nano_det0", "fx_nano_det1"],
            "task_identifier": "FitStackMultiDetector",
        },
        {
            "name": "energy_name",
            "value": "Edcm",
            "task_identifier": "FitStackMultiDetector",
        },
        {
            "name": "detector_normalization_template",
            "value": "0.1/<instrument/{}/live_time>",
            "task_identifier": "SumXrfResultsStack",
        },
        {
            "name": "counter_name",
            "value": "niodet",
            "task_identifier": "NormalizeXrfResultsStack",
        },
        {
            "name": "counter_normalization_template",
            "value": "np.nanmean(<instrument/{}/data>)/<instrument/{}/data>",
            "task_identifier": "NormalizeXrfResultsStack",
        },
        {
            "name": "axes_units",
            "value": {"nsy": "mm", "nsz": "mm", "nspy": "um", "nspz": "um"},
            "task_identifier": "RegridXrfResultsStack",
        },
        {
            "name": "ignore_positioners",
            "value": ["nsz1", "nsz2", "nsz3"],
            "task_identifier": "RegridXrfResultsStack",
        },
        {
            "name": "resolution",
            "value": None,
            "task_identifier": "RegridXrfResultsStack",
        },
        {
            "name": "reference_stack",
            "value": None,
            "task_identifier": "Reg2DPreEvaluation",
        },
        {"name": "skip", "value": True, "task_identifier": "Reg2DPreEvaluation"},
        {"name": "skip", "value": False, "task_identifier": "Reg2DPostEvaluation"},
        {"name": "crop", "value": True, "task_identifier": "Reg2DTransform"},
    ]

    assert workflow_path == eworkflow_path
    assert convert_destination == econvert_destination
    assert inputs == einputs
