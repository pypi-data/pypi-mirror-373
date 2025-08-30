from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from .utils import directories
from .utils import models
from .workflows import fluoxas_multi_detector
from .workflows import fluoxas_multi_detector_align
from .workflows import fluoxas_nofit_align
from .workflows import fluoxas_single_detector
from .workflows import fluoxas_single_detector_align


def fluoxas_workflow_inputs(
    filenames: Sequence[str],
    output_root_uri: str,
    scan_ranges: Sequence[Tuple[int, int]],
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
    exclude_scans: Optional[Sequence[Sequence[int]]] = None,
    resolution: Optional[Dict[str, Tuple[Union[int, float], str]]] = None,
    do_align: bool = True,
    align_counter: Optional[str] = None,
    align_crop: Optional[bool] = True,
    fast_align_counter_selection: Optional[bool] = False,
    virtual_axes: Optional[Dict[str, str]] = None,
    ignore_axes: Optional[List[str]] = None,
    axis_units: Optional[Dict[str, str]] = None,
) -> Tuple[str, List[dict]]:

    if len(filenames) != len(scan_ranges):
        raise ValueError(
            f"{len(filenames)} scan ranges (first, last) are needed for {len(filenames)} files"
        )

    if not exclude_scans:
        exclude_scans = [()] * len(filenames)

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
        True,
        virtual_axes,
        ignore_axes,
        axis_units,
    )

    parameters = models.FluoXasParameters(
        filenames=filenames,
        scan_ranges=scan_ranges,
        exclude_scans=exclude_scans,
        output_root_uri=output_root_uri,
        resolution=resolution,
        align_counter=align_counter,
        fast_align_counter_selection=fast_align_counter_selection,
        align_crop=align_crop,
        **parameters.model_dump(),
    )

    if parameters.no_fit:
        workflow = fluoxas_nofit_align.WORKFLOW
        inputs = fluoxas_nofit_align.workflow_inputs(parameters)
    elif parameters.fit_single_detector:
        if do_align:
            workflow = fluoxas_single_detector_align.WORKFLOW
            inputs = fluoxas_single_detector_align.workflow_inputs(parameters)
        else:
            workflow = fluoxas_single_detector.WORKFLOW
            inputs = fluoxas_single_detector.workflow_inputs(parameters)
    else:
        if parameters.sum_spectra:
            raise ValueError(
                f"Sum before fit is not supported yet for FluoXAS. Provide {len(detector_numbers)} config files."
            )
        if do_align:
            workflow = fluoxas_multi_detector_align.WORKFLOW
            inputs = fluoxas_multi_detector_align.workflow_inputs(parameters)
        else:
            workflow = fluoxas_multi_detector.WORKFLOW
            inputs = fluoxas_multi_detector.workflow_inputs(parameters)

    return workflow, inputs


def fluoxas_paths(
    session: str,
    sample: str,
    datasets: Sequence[str],
    scan_ranges: Sequence[Tuple[int, int]],
    config_filenames: Sequence[str],
    dirname: Optional[str] = None,
    demo: bool = False,
) -> models.FluoXasPaths:
    filenames = [
        directories.raw_directory(session, sample, dataset, demo=demo)
        for dataset in datasets
    ]

    first_dataset = datasets[0]
    first_scan_number = scan_ranges[0][0]

    output_filename = directories.processed_path(
        session,
        sample,
        first_dataset,
        dirname,
        f"{sample}_{first_dataset}.h5",
        demo=demo,
    )
    convert_destination = directories.processed_path(
        session,
        sample,
        first_dataset,
        dirname,
        f"{sample}_{first_dataset}_scan{first_scan_number:04d}.json",
        demo=demo,
    )

    output_root_uri = f"{output_filename}::/{first_scan_number}.1"
    config_filenames = [
        directories.pymca_config_path(session, s, demo=demo) for s in config_filenames
    ]

    workflow_path = directories.accessible_workflow_path(
        session, sample, first_dataset, dirname, demo=demo
    )

    return models.FluoXasPaths(
        filenames=filenames,
        output_root_uri=output_root_uri,
        convert_destination=convert_destination,
        workflow_path=workflow_path,
        config_filenames=config_filenames,
    )
