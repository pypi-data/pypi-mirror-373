import os
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from .fluoxas import fluoxas_paths
from .fluoxas import fluoxas_workflow_inputs
from .mosaic_xrfmap import mosaic_xrfmap_paths
from .mosaic_xrfmap import mosaic_xrfmap_workflow_inputs
from .utils.execute import execute_graph
from .xrfmap import xrfmap_paths
from .xrfmap import xrfmap_workflow_inputs


def xrfmap(*args, **kargs):
    workflow_filename, inputs, convert_destination = xrfmap_parameters(*args, **kargs)
    execute_graph(
        workflow_filename, inputs=inputs, convert_destination=convert_destination
    )


def mosaic_xrfmap(*args, **kargs):
    workflow_filename, inputs, convert_destination = mosaic_xrfmap_parameters(
        *args, **kargs
    )
    execute_graph(
        workflow_filename, inputs=inputs, convert_destination=convert_destination
    )


def fluoxas(*args, **kargs):
    workflow_filename, inputs, convert_destination = fluoxas_parameters(*args, **kargs)
    execute_graph(
        workflow_filename, inputs=inputs, convert_destination=convert_destination
    )


def xrfmap_parameters(
    session: str,
    sample: str,
    dataset: str,
    scan_number: int,
    config_filenames: Sequence[str],
    detector_numbers: Sequence[int],
    instrument_name: str = None,
    fast_fitting: bool = True,
    quantification: bool = True,
    diagnostics: bool = True,
    livetime_ref_value: Union[str, int, float, None] = None,
    counter_ref_value: Union[str, int, float, None] = None,
    counter_name: Optional[str] = None,
    energy_name: Optional[str] = None,
    dirname: Optional[str] = None,
    resolution: Optional[Dict[str, Tuple[Union[int, float], str]]] = None,
    demo: bool = False,
) -> Tuple[str, List[dict], str]:
    paths = xrfmap_paths(
        session,
        sample,
        dataset,
        scan_number,
        config_filenames,
        dirname=dirname,
        demo=demo,
    )

    workflow, inputs = xrfmap_workflow_inputs(
        paths.filename,
        paths.output_root_uri,
        scan_number,
        paths.config_filenames,
        instrument_name=instrument_name,
        detector_numbers=detector_numbers,
        detector_names=None,
        fast_fitting=fast_fitting,
        quantification=quantification,
        diagnostics=diagnostics,
        livetime_ref_value=livetime_ref_value,
        counter_ref_value=counter_ref_value,
        counter_name=counter_name,
        energy_name=energy_name,
        resolution=resolution,
    )

    workflow_filename = os.path.join(paths.workflow_path, workflow + ".ows")

    return workflow_filename, inputs, paths.convert_destination


def mosaic_xrfmap_parameters(
    session: str,
    sample: str,
    datasets: Sequence[str],
    scan_ranges: Sequence[Tuple[int, int]],
    config_filenames: Sequence[str],
    detector_numbers: Sequence[int],
    instrument_name: str = None,
    fast_fitting: bool = True,
    quantification: bool = True,
    diagnostics: bool = True,
    livetime_ref_value: Union[str, int, float, None] = None,
    counter_ref_value: Union[str, int, float, None] = None,
    counter_name: Optional[str] = None,
    energy_name: Optional[str] = None,
    dirname: Optional[str] = None,
    exclude_scans: Optional[Sequence[Sequence[int]]] = None,
    resolution: Optional[Dict[str, Tuple[Union[int, float], str]]] = None,
    demo: bool = False,
):
    paths = mosaic_xrfmap_paths(
        session,
        sample,
        datasets,
        scan_ranges,
        config_filenames,
        dirname=dirname,
        demo=demo,
    )

    workflow, inputs = mosaic_xrfmap_workflow_inputs(
        paths.filenames,
        paths.output_root_uri,
        paths.concat_bliss_scan_uri,
        scan_ranges,
        paths.config_filenames,
        instrument_name=instrument_name,
        detector_numbers=detector_numbers,
        detector_names=None,
        fast_fitting=fast_fitting,
        quantification=quantification,
        diagnostics=diagnostics,
        livetime_ref_value=livetime_ref_value,
        counter_ref_value=counter_ref_value,
        counter_name=counter_name,
        energy_name=energy_name,
        exclude_scans=exclude_scans,
        resolution=resolution,
    )

    workflow_filename = os.path.join(paths.workflow_path, workflow + ".ows")

    return workflow_filename, inputs, paths.convert_destination


def fluoxas_parameters(
    session: str,
    sample: str,
    datasets: Sequence[str],
    scan_ranges: Sequence[Tuple[int, int]],
    config_filenames: Sequence[str],
    detector_numbers: Sequence[int],
    instrument_name: str = None,
    fast_fitting: bool = True,
    quantification: bool = True,
    diagnostics: bool = True,
    livetime_ref_value: Union[str, int, float, None] = None,
    counter_ref_value: Union[str, int, float, None] = None,
    counter_name: Optional[str] = None,
    energy_name: Optional[str] = None,
    dirname: Optional[str] = None,
    exclude_scans: Optional[Sequence[Sequence[int]]] = None,
    resolution: Optional[Dict[str, Tuple[Union[int, float], str]]] = None,
    do_align: bool = True,
    align_counter: Optional[str] = None,
    align_crop: Optional[bool] = True,
    fast_align_counter_selection: Optional[bool] = False,
    demo: bool = False,
):
    paths = fluoxas_paths(
        session,
        sample,
        datasets,
        scan_ranges,
        config_filenames,
        dirname=dirname,
        demo=demo,
    )

    workflow, inputs = fluoxas_workflow_inputs(
        paths.filenames,
        paths.output_root_uri,
        scan_ranges,
        paths.config_filenames,
        instrument_name=instrument_name,
        detector_numbers=detector_numbers,
        detector_names=None,
        fast_fitting=fast_fitting,
        quantification=quantification,
        diagnostics=diagnostics,
        livetime_ref_value=livetime_ref_value,
        counter_ref_value=counter_ref_value,
        counter_name=counter_name,
        energy_name=energy_name,
        exclude_scans=exclude_scans,
        resolution=resolution,
        do_align=do_align,
        align_counter=align_counter,
        align_crop=align_crop,
        fast_align_counter_selection=fast_align_counter_selection,
    )

    workflow_filename = os.path.join(paths.workflow_path, workflow + ".ows")

    return workflow_filename, inputs, paths.convert_destination
