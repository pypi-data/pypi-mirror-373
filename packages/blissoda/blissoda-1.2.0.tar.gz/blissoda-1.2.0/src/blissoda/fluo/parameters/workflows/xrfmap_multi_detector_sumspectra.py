from typing import List

from ..utils import defaults
from ..utils.models import XrfMapParameters

WORKFLOW = "xrfmap_multi_detector_sumspectra"


def workflow_inputs(
    parameters: XrfMapParameters,
) -> List[dict]:
    inputs = [
        {
            "name": "filename",
            "value": parameters.filename,
            "task_identifier": "PickScan",
        },
        {
            "name": "scan_number",
            "value": parameters.scan_number,
            "task_identifier": "PickScan",
        },
        {
            "name": "detector_names",
            "value": parameters.detector_names,
            "task_identifier": "SumXrfSpectra",
        },
        {
            "name": "output_root_uri",
            "value": parameters.output_root_uri,
            "task_identifier": "SumXrfSpectra",
        },
        {
            "name": "detector_normalization_template",
            "value": parameters.detector_normalization_template,
            "task_identifier": "SumXrfSpectra",
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
            "name": "axes_units",
            "value": parameters.axis_units
            or defaults.AXES_UNITS[parameters.instrument_name],
            "task_identifier": "RegridXrfResults",
        },
        {
            "name": "ignore_positioners",
            "value": (
                parameters.ignore_axes
                if parameters.ignore_axes is not None
                else defaults.IGNORE_AXES[parameters.instrument_name]
            ),
            "task_identifier": "RegridXrfResults",
        },
        {
            "name": "resolution",
            "value": parameters.resolution,
            "task_identifier": "RegridXrfResults",
        },
    ]

    return inputs
