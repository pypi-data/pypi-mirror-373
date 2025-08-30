from typing import List

from ..utils import defaults
from ..utils.models import FluoXasParameters

WORKFLOW = "fluoxas_nofit_align"


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
            "task_identifier": "ExtractRawCountersStack",
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
    ]

    return inputs
