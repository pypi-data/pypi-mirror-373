import numpy


def energy_wavelength(x):
    """keV to m and vice versa"""
    return 12.398419843320026 * 1e-10 / x


DEFAULT_CALIB = {
    "dist": 5e-2,  # 5 cm
    "poni1": 10e-2,  # 10 cm
    "poni2": 10e-2,  # 10 cm
    "rot1": numpy.radians(10),  # 10 deg
    "rot2": 0,  # 0 deg
    "rot3": 0,  # 0 deg
    "energy": 12,  # 12 keV
    "detector": "Pilatus1M",
}
