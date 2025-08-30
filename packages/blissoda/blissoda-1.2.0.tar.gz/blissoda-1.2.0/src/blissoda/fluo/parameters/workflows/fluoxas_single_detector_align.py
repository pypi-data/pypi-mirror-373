from typing import List

from ..utils import defaults
from ..utils.models import FluoXasParameters

WORKFLOW = "fluoxas_single_detector_align"


def workflow_inputs(parameters: FluoXasParameters) -> List[dict]:
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
            "task_identifier": "RegridXrfResultsStack",
        },
        {
            "name": "ignore_positioners",
            "value": (
                parameters.ignore_axes
                if parameters.ignore_axes is not None
                else defaults.IGNORE_AXES[parameters.instrument_name]
            ),
            "task_identifier": "RegridXrfResultsStack",
        },
        {
            "name": "resolution",
            "value": parameters.resolution,
            "task_identifier": "RegridXrfResultsStack",
        },
        {
            "name": "reference_stack",
            "value": parameters.align_counter,
            "task_identifier": "Reg2DPreEvaluation",
        },
        {
            "name": "skip",
            "value": not parameters.align_counter
            and not parameters.fast_align_counter_selection,
            "task_identifier": "Reg2DPreEvaluation",
        },
        {
            "name": "skip",
            "value": not parameters.align_counter
            and parameters.fast_align_counter_selection,
            "task_identifier": "Reg2DPostEvaluation",
        },
        {
            "name": "crop",
            "value": parameters.align_crop,
            "task_identifier": "Reg2DTransform",
        },
    ]

    return inputs
