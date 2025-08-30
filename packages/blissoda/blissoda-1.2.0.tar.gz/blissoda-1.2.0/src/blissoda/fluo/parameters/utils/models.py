from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from pydantic import BaseModel

from . import defaults


class XrfMapPaths(BaseModel):
    filename: str
    output_root_uri: str
    convert_destination: str
    workflow_path: str
    config_filenames: List[str]


class MosaicXrfMapPaths(BaseModel):
    filenames: List[str]
    output_root_uri: str
    concat_bliss_scan_uri: str
    convert_destination: str
    workflow_path: str
    config_filenames: List[str]


class FluoXasPaths(BaseModel):
    filenames: List[str]
    output_root_uri: str
    convert_destination: str
    workflow_path: str
    config_filenames: List[str]


class CommonParameters(BaseModel):
    instrument_name: Optional[str]
    detector_names: List[str]
    detector_normalization_template: str
    counter_name: Optional[str]
    counter_normalization_template: Optional[str]
    config_filenames: List[str]
    energy_name: str
    fast_fitting: bool
    quantification: bool
    diagnostics: bool
    no_fit: bool
    fit_single_detector: Optional[bool]
    sum_spectra: Optional[bool]
    norm_identifier: str
    fit_identifier: str
    virtual_axes: Optional[Dict[str, str]]
    ignore_axes: Optional[List[str]]
    axis_units: Optional[Dict[str, str]]


class XrfMapParameters(CommonParameters):
    filename: str
    scan_number: int
    output_root_uri: str
    resolution: Optional[Dict[str, Tuple[Union[int, float], str]]]


class MosaicXrfMapParameters(CommonParameters):
    filenames: List[str]
    scan_ranges: Sequence[Tuple[int, int]]
    exclude_scans: Sequence[Sequence[int]]
    output_root_uri: str
    bliss_scan_uri: str
    resolution: Optional[Dict[str, Tuple[Union[int, float], str]]]


class FluoXasParameters(CommonParameters):
    filenames: List[str]
    scan_ranges: Sequence[Tuple[int, int]]
    exclude_scans: Sequence[Sequence[int]]
    output_root_uri: str
    resolution: Optional[Dict[str, Tuple[Union[int, float], str]]]
    align_counter: Optional[str]
    align_crop: Optional[bool]
    fast_align_counter_selection: Optional[bool]


def common_parameters_model(
    detector_numbers: Optional[Sequence[int]],
    detector_names: Optional[Sequence[str]],
    config_filenames: Sequence[str],
    energy_name: Optional[str],
    counter_name: Optional[str],
    instrument_name: Optional[str],
    fast_fitting: bool,
    quantification: bool,
    diagnostics: bool,
    livetime_ref_value: Union[str, int, float, None],
    counter_ref_value: Union[str, int, float, None],
    stack: bool,
    virtual_axes: Optional[Dict[str, str]],
    ignore_axes: Optional[List[str]],
    axis_units: Optional[Dict[str, str]],
) -> Tuple[Sequence[dict], Optional[bool]]:
    detector_names = detector_names or [
        defaults.MCA_NAME_FORMAT[instrument_name].format(i) for i in detector_numbers
    ]
    counter_name = counter_name or defaults.I0_COUNTER[instrument_name]
    if counter_name:
        counter_normalization_template = f"{counter_ref_value or defaults.DEFAULT_COUNTER_REF_VALUE}/<instrument/{{}}/data>"
    else:
        counter_normalization_template = None
    energy_name = energy_name or defaults.ENERGY_COUNTER[instrument_name]
    detector_normalization_template = f"{livetime_ref_value or defaults.DEFAULT_LIVETIME_REF_VALUE}/<instrument/{{}}/live_time>"

    if len(detector_names) == 0 or len(config_filenames) == 0:
        no_fit = True
        sum_spectra = None
        fit_single_detector = None
    elif len(detector_names) == 1:
        # Only one detector
        if len(config_filenames) != 1:
            raise ValueError("Only one pymca configuration is needed for one detector")
        no_fit = False
        sum_spectra = None
        fit_single_detector = True
    elif len(config_filenames) == 1:
        # More than one detector and fit the sum
        no_fit = False
        sum_spectra = True
        fit_single_detector = True
    else:
        # More than one detector and fit each detector separately
        if len(detector_names) != len(config_filenames):
            raise ValueError(
                f"{len(detector_names)} pymca configurations are needed for {len(detector_names)} detectors"
            )
        no_fit = False
        sum_spectra = False
        fit_single_detector = False

    if stack:
        norm_identifier = "NormalizeXrfResultsStack"
        if fit_single_detector:
            fit_identifier = "FitStackSingleDetector"
        else:
            fit_identifier = "FitStackMultiDetector"
    else:
        norm_identifier = "NormalizeXrfResults"
        if fit_single_detector:
            fit_identifier = "FitSingleScanSingleDetector"
        else:
            fit_identifier = "FitSingleScanMultiDetector"

    return CommonParameters(
        instrument_name=instrument_name,
        detector_names=detector_names,
        detector_normalization_template=detector_normalization_template,
        counter_name=counter_name,
        counter_normalization_template=counter_normalization_template,
        energy_name=energy_name,
        fast_fitting=fast_fitting,
        quantification=quantification,
        diagnostics=diagnostics,
        no_fit=no_fit,
        fit_single_detector=fit_single_detector,
        config_filenames=config_filenames,
        sum_spectra=sum_spectra,
        norm_identifier=norm_identifier,
        fit_identifier=fit_identifier,
        virtual_axes=virtual_axes,
        ignore_axes=ignore_axes,
        axis_units=axis_units,
    )
