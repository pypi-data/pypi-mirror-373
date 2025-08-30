from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from .utils import directories
from .utils import models
from .workflows import mosaic_multi_detector
from .workflows import mosaic_multi_detector_sumspectra
from .workflows import mosaic_single_detector


def mosaic_xrfmap_workflow_inputs(
    filenames: Sequence[str],
    output_root_uri: str,
    concat_bliss_scan_uri: str,
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
    virtual_axes: Optional[Dict[str, str]] = None,
    ignore_axes: Optional[List[str]] = None,
    axis_units: Optional[Dict[str, str]] = None,
) -> Tuple[str, List[dict]]:
    if not exclude_scans:
        exclude_scans = [()] * len(filenames)

    if len(filenames) != len(scan_ranges):
        raise ValueError(
            f"{len(filenames)} scan ranges (first, last) are needed for {len(filenames)} files"
        )

    if len(filenames) != len(exclude_scans):
        raise ValueError(
            f"{len(filenames)} exclude scan list are needed for {len(filenames)} files"
        )

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

    parameters = models.MosaicXrfMapParameters(
        filenames=filenames,
        scan_ranges=scan_ranges,
        exclude_scans=exclude_scans,
        output_root_uri=output_root_uri,
        bliss_scan_uri=concat_bliss_scan_uri,
        resolution=resolution,
        **parameters.model_dump(),
    )

    if parameters.fit_single_detector:
        if parameters.sum_spectra:
            workflow = mosaic_multi_detector_sumspectra.WORKFLOW
            inputs = mosaic_multi_detector_sumspectra.workflow_inputs(parameters)
        else:
            workflow = mosaic_single_detector.WORKFLOW
            inputs = mosaic_single_detector.workflow_inputs(parameters)
    else:
        workflow = mosaic_multi_detector.WORKFLOW
        inputs = mosaic_multi_detector.workflow_inputs(parameters)

    return workflow, inputs


def mosaic_xrfmap_paths(
    session: str,
    sample: str,
    datasets: Sequence[str],
    scan_ranges: Sequence[Tuple[int, int]],
    config_filenames: Sequence[str],
    dirname: Optional[str] = None,
    demo: bool = False,
) -> models.MosaicXrfMapPaths:
    filenames = [
        directories.raw_directory(session, sample, dataset, demo=demo)
        for dataset in datasets
    ]

    first_dataset = datasets[0]
    first_scan_number = scan_ranges[0][0]

    concat_filename = directories.processed_path(
        session,
        sample,
        first_dataset,
        dirname,
        f"{sample}_{first_dataset}_concat.h5",
        demo=demo,
    )
    output_filename = directories.processed_path(
        session,
        sample,
        first_dataset,
        dirname,
        f"{sample}_{first_dataset}_results.h5",
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

    concat_bliss_scan_uri = f"{concat_filename}::/{first_scan_number}.1"
    output_root_uri = f"{output_filename}::/{first_scan_number}.1"
    config_filenames = [
        directories.pymca_config_path(session, s, demo=demo) for s in config_filenames
    ]

    workflow_path = directories.accessible_workflow_path(
        session, sample, first_dataset, dirname, demo=demo
    )

    return models.MosaicXrfMapPaths(
        filenames=filenames,
        output_root_uri=output_root_uri,
        concat_bliss_scan_uri=concat_bliss_scan_uri,
        convert_destination=convert_destination,
        workflow_path=workflow_path,
        config_filenames=config_filenames,
    )
