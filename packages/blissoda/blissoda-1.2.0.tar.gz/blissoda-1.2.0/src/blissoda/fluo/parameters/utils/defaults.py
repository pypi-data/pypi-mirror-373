REAL_DATA_ROOT = "/data/visitor"

DEMO_DATA_ROOT = "/data/scisoft/ewoks"

DEFAULT_OUT_DIRNAME = "ewoks_results"

# Fast scanning: not all motors have units
AXES_UNITS = {
    "id21_sxm": {
        "samy": "mm",
        "samz": "mm",
        "sampy": "um",
        "sampz": "um",
    },
    "id21_nano": {
        "nsy": "mm",
        "nsz": "mm",
        "nspy": "um",
        "nspz": "um",
    },
    "id16b": {
        "samy": "mm",
        "samz": "mm",
        "sampy": "um",
        "sampz": "um",
    },
}

# Mosaic XRF mapping
VIRTUAL_AXES = {
    "id21_sxm": {
        "sy": "<samy>+<sampy>",
        "sz": "<samz>+<sampz>",
    },
    "id21_nano": {
        "sy": "<nsy>+<nspy>",
        "sz": "<nsz>+<nspz>",
    },
    "id16b": {
        "sy": "<samy>+<sampy>",
        "sz": "<samz>+<sampz>",
    },
}

IGNORE_AXES = {
    "id21_sxm": [],
    "id21_nano": ["nsz1", "nsz2", "nsz3"],
    "id16b": [],
}

ENERGY_COUNTER = {
    "id21_sxm": "Edcm",
    "id21_nano": "Edcm",
    "id16b": "Edcm",
}

I0_COUNTER = {
    "id21_sxm": "iodet",
    "id21_nano": "niodet",
    "id16b": None,
}

MCA_NAME_FORMAT = {
    "id21_sxm": "fx_sxm_det{}",
    "id21_nano": "fx_nano_det{}",
    "id16b": "fxb_det{}",
}

DEFAULT_LIVETIME_REF_VALUE = "0.1"

DEFAULT_COUNTER_REF_VALUE = "np.nanmean(<instrument/{}/data>)"

DO_PROFILE = False
