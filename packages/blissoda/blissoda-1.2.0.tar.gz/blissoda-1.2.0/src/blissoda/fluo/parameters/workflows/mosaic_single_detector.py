from typing import List

from ..utils import defaults
from ..utils.models import MosaicXrfMapParameters

WORKFLOW = "mosaic_single_detector"


def workflow_inputs(parameters: MosaicXrfMapParameters) -> List[dict]:
    inputs = [
        {
            "name": "filenames",
            "value": parameters.filenames,
            "task_identifier": "PickScans",
        },
        {
            "name": "scan_ranges",
            "value": parameters.scan_ranges,
            "task_identifier": "PickScans",
        },
        {
            "name": "exclude_scans",
            "value": parameters.exclude_scans,
            "task_identifier": "PickScans",
        },
        {
            "name": "bliss_scan_uri",
            "value": parameters.bliss_scan_uri,
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "output_root_uri",
            "value": parameters.output_root_uri,
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "output_root_uri",
            "value": parameters.output_root_uri,
            "task_identifier": parameters.fit_identifier,
        },
        {
            "name": "config",
            "value": parameters.config_filenames[0],
            "task_identifier": parameters.fit_identifier,
        },
        {
            "name": "fast_fitting",
            "value": parameters.fast_fitting,
            "task_identifier": parameters.fit_identifier,
        },
        {
            "name": "quantification",
            "value": parameters.quantification,
            "task_identifier": parameters.fit_identifier,
        },
        {
            "name": "diagnostics",
            "value": parameters.diagnostics,
            "task_identifier": parameters.fit_identifier,
        },
        {
            "name": "detector_name",
            "value": parameters.detector_names[0],
            "task_identifier": parameters.fit_identifier,
        },
        {
            "name": "energy_name",
            "value": parameters.energy_name,
            "task_identifier": parameters.fit_identifier,
        },
        {
            "name": "counter_name",
            "value": parameters.counter_name,
            "task_identifier": parameters.norm_identifier,
        },
        {
            "name": "counter_normalization_template",
            "value": parameters.counter_normalization_template,
            "task_identifier": parameters.norm_identifier,
        },
        {
            "name": "detector_normalization_template",
            "value": parameters.detector_normalization_template,
            "task_identifier": parameters.norm_identifier,
        },
        {
            "name": "axes_units",
            "value": parameters.axis_units
            or defaults.AXES_UNITS[parameters.instrument_name],
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "virtual_axes",
            "value": parameters.virtual_axes
            or defaults.VIRTUAL_AXES[parameters.instrument_name],
            "task_identifier": "ConcatBliss",
        },
        {
            "name": "positioners",
            "value": sorted(
                parameters.virtual_axes
                or defaults.VIRTUAL_AXES[parameters.instrument_name]
            )[::-1],
            "task_identifier": "RegridXrfResults",
        },
        {
            "name": "resolution",
            "value": parameters.resolution,
            "task_identifier": "RegridXrfResults",
        },
    ]

    return inputs
