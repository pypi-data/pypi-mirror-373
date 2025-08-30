from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from .utils import directories
from .utils import models
from .workflows import xrfmap_multi_detector
from .workflows import xrfmap_multi_detector_sumspectra
from .workflows import xrfmap_single_detector


def xrfmap_workflow_inputs(
    filename: str,
    output_root_uri: str,
    scan_number: int,
    config_filenames: Sequence[str],
    instrument_name: Optional[str] = None,
    detector_numbers: Optional[Sequence[int]] = None,
    detector_names: Optional[Sequence[str]] = None,
    fast_fitting: bool = True,
    quantification: bool = True,
    diagnostics: bool = True,
    livetime_ref_value: Union[str, int, float, None] = None,
    counter_ref_value: Union[str, int, float, None] = None,
    counter_name: Optional[str] = None,
    energy_name: Optional[str] = None,
    resolution: Optional[Dict[str, Tuple[Union[int, float], str]]] = None,
    virtual_axes: Optional[Dict[str, str]] = None,
    ignore_axes: Optional[List[str]] = None,
    axis_units: Optional[Dict[str, str]] = None,
) -> Tuple[str, List[dict]]:
    parameters = models.common_parameters_model(
        detector_numbers,
        detector_names,
        config_filenames,
        energy_name,
        counter_name,
        instrument_name,
        fast_fitting,
        quantification,
        diagnostics,
        livetime_ref_value,
        counter_ref_value,
        False,
        virtual_axes,
        ignore_axes,
        axis_units,
    )

    parameters = models.XrfMapParameters(
        filename=filename,
        scan_number=scan_number,
        output_root_uri=output_root_uri,
        resolution=resolution,
        **parameters.model_dump(),
    )

    if parameters.fit_single_detector:
        if parameters.sum_spectra:
            workflow = xrfmap_multi_detector_sumspectra.WORKFLOW
            inputs = xrfmap_multi_detector_sumspectra.workflow_inputs(parameters)
        else:
            workflow = xrfmap_single_detector.WORKFLOW
            inputs = xrfmap_single_detector.workflow_inputs(parameters)
    else:
        workflow = xrfmap_multi_detector.WORKFLOW
        inputs = xrfmap_multi_detector.workflow_inputs(parameters)

    return workflow, inputs


def xrfmap_paths(
    session: str,
    sample: str,
    dataset: str,
    scan_number: int,
    config_filenames: Sequence[str],
    dirname: Optional[str] = None,
    demo: bool = False,
) -> models.XrfMapPaths:
    filename = directories.raw_directory(session, sample, dataset, demo=demo)

    output_filename = directories.processed_path(
        session, sample, dataset, dirname, f"{sample}_{dataset}.h5", demo=demo
    )
    convert_destination = directories.processed_path(
        session,
        sample,
        dataset,
        dirname,
        f"{sample}_{dataset}_scan{scan_number:04d}.json",
        demo=demo,
    )

    output_root_uri = f"{output_filename}::/{scan_number}.1"
    config_filenames = [
        directories.pymca_config_path(session, s, demo=demo) for s in config_filenames
    ]

    workflow_path = directories.accessible_workflow_path(
        session, sample, dataset, dirname, demo=demo
    )
    return models.XrfMapPaths(
        filename=filename,
        output_root_uri=output_root_uri,
        convert_destination=convert_destination,
        workflow_path=workflow_path,
        config_filenames=config_filenames,
    )
