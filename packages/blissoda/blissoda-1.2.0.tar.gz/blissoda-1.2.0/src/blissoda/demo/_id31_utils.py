from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

import numpy

from ..bliss_globals import current_session
from ..bliss_globals import setup_globals
from ..import_utils import unavailable_function
from ..utils import directories

try:
    from scipy.io import savemat
except ImportError as ex:
    savemat = unavailable_function(ex)


_logger = logging.getLogger(__name__)


def ensure_difflab6_id31_flats() -> Tuple[str, str]:
    """Create dummy flat field files for ID31 FlatFieldFromEnergy task"""
    difflab6_image_shape = (
        setup_globals.difflab6.image.height,
        setup_globals.difflab6.image.width,
    )

    processed_dir = directories.get_processed_dir(current_session.scan_saving.filename)

    newflat_path = Path(processed_dir, "config", "flats.mat")
    if not newflat_path.is_file():
        _logger.info(f"Create ID31 demo newflat file: {str(newflat_path)}")
        newflat_path.parent.mkdir(parents=True, exist_ok=True)
        savemat(
            newflat_path,
            {
                "E": numpy.array([65, 105], dtype=numpy.uint8),
                "F": numpy.ones(difflab6_image_shape + (2,), dtype=numpy.float64),
            },
        )

    oldflat_path = Path(processed_dir, "config", "flats_old.mat")
    if not oldflat_path.is_file():
        _logger.info(f"Create ID31 demo oldflat file: {str(oldflat_path)}")
        oldflat_path.parent.mkdir(parents=True, exist_ok=True)
        savemat(
            oldflat_path,
            {
                "Eold": numpy.array([15.77, 74.96], dtype=numpy.float64),
                "Fold": numpy.ones(difflab6_image_shape + (2,), dtype=numpy.float64),
            },
        )

    return str(newflat_path), str(oldflat_path)
