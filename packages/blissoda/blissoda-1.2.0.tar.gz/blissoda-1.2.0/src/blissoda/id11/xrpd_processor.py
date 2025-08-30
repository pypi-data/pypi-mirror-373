"""Automatic pyfai integration for every scan with saving and plotting with pdf extraction"""

import configparser
import os
import tempfile
from glob import glob
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..persistent.parameters import ParameterInfo
from ..resources import resource_filename
from ..utils.pyfai import read_config
from ..xrpd.processor import XrpdProcessor


class Id11XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("pyfai_config_directory", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
        ParameterInfo("pdf_enable", category="PDF"),
        ParameterInfo("pdf_options", category="PDF"),
        ParameterInfo("pdf_config_file", category="PDF"),
        ParameterInfo("pdf_average_every", category="PDF"),
    ],
):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("pyfai_config_directory", tempfile.gettempdir())
        defaults.setdefault("pdf_config_file", tempfile.gettempdir())

        super().__init__(config=config, defaults=defaults)

    def _info_categories(self) -> Dict[str, dict]:
        categories = super()._info_categories()
        if not self.lima_names:
            return categories
        categories["PyFai"]["integration_options"] = "... (see below)"
        lima_name = self.lima_names[0]
        categories["PyFai integration"] = {
            "1. JSON file": self._detector_config_filename(lima_name, ".json"),
            "2. PONI file": self._detector_config_filename(lima_name, ".poni"),
            "3. User": self.integration_options,
            "Merged": self.get_integration_options(lima_name),
        }
        categories["PDF"] = {
            "PDF Enable": self.pdf_enable,
            "PDF Config File Path": self.pdf_config_file,
            "PDF Average Every N points": self.pdf_average_every,
            "PDF Config From User": self.pdf_options,
            "PDFGetX Config Parameters Merged": self.get_pdfgetx_options(lima_name),
        }
        return categories

    def _set_parameter(self, name, value):
        super()._set_parameter(name, value)
        if name == "pdf_enable":
            self._update_pdfgetx_status()

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return None

    def get_average_every(self) -> Optional[str]:
        return self.pdf_average_every

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        options = self._default_azint_options(lima_name)
        options.update(self._default_calib_options(lima_name))
        integration_options = self.integration_options
        if integration_options:
            options.update(integration_options.to_dict())
        return options

    def _default_azint_options(self, lima_name: str) -> dict:
        filename = self._detector_config_filename(lima_name, ".json")
        return read_config(filename)

    def _default_calib_options(self, lima_name: str) -> dict:
        filename = self._detector_config_filename(lima_name, ".poni")
        return read_config(filename)

    def _detector_config_filename(self, lima_name: str, ext: str) -> Optional[str]:
        pyfai_config_directory = self.pyfai_config_directory
        if not pyfai_config_directory:
            pyfai_config_directory = tempfile.gettempdir()
        pattern = os.path.join(pyfai_config_directory, lima_name, f"*{ext}")
        files = sorted(glob(pattern))
        if not files:
            return
        return files[-1]

    def get_inputs(self, scan, lima_name: str) -> List[dict]:
        inputs = super().get_inputs(scan, lima_name)
        if self.pdf_enable:
            inputs += self._get_pdfgetx_config_inputs(lima_name)
            inputs += self._get_pdfgetx_save_inputs(scan, lima_name)
        return inputs

    def _update_pdfgetx_status(self):
        if self.pdf_enable:
            self.workflow_with_saving = resource_filename(
                "id11", "integrate_scan_with_saving_pdf.json"
            )
        else:
            self.workflow_with_saving = resource_filename(
                "id11", "integrate_scan_with_saving.json"
            )
        return self.pdf_enable

    def get_pdfgetx_options(self, lima_name: str) -> Optional[dict]:
        config = configparser.ConfigParser()
        config.read(self.pdf_config_file)
        options = dict(config["DEFAULT"])
        for key in options.keys():  # Patch config parser str -> float
            if options[key].replace(".", "").isnumeric():
                options[key] = float(options[key])
        pdf_options = self.pdf_options
        if pdf_options:
            options.update(pdf_options.to_dict())
        return options

    def _get_pdfgetx_config_inputs(self, lima_name: str) -> List[dict]:
        inputs = [
            {
                "task_identifier": "PdfGetXConfig",
                "name": "pdfgetx_options_dict",
                "value": self.get_pdfgetx_options(lima_name),
            },
            {
                "task_identifier": "PdfGetXAverage",
                "name": "average_every",
                "value": self.get_average_every(),
            },
        ]
        return inputs

    def _get_pdfgetx_save_inputs(self, scan, lima_name: str) -> List[dict]:
        # Save PDF data in the same Nxentry as the PyFAI results
        # pyfai_filename = self.master_output_filename(scan)

        # Save PDF data in ascii files as well
        ascii_filename = self._get_pdfgetx_ascii_filename(scan, lima_name)

        inputs = [
            {
                "task_identifier": "PdfGetXSaveAscii",
                "name": "filename",
                "value": ascii_filename,
            },
            {
                "task_identifier": "PdfGetXSaveNexus",
                "name": "pdfgetx_options",
                "value": self.get_pdfgetx_options(lima_name),
            },
        ]
        return inputs

    def _get_pdfgetx_ascii_filename(self, scan, lima_name: str) -> str:
        """Unique name per scan and per detector when more than one."""
        filename = self.get_filename(scan)
        root = self.scan_processed_directory(scan)
        basename = os.path.basename(filename)

        stem, _ = os.path.splitext(basename)
        stem_parts = [stem]
        if len(self.lima_names) > 1:
            stem_parts.append(lima_name)
        scan_nb = scan.scan_info.get("scan_nb")
        stem_parts.append(f"{scan_nb:04d}")
        basename = "_".join(stem_parts)

        # PdfGetXSaveAscii expects a name with the .h5 extension
        return os.path.join(root, f"{basename}.h5")
