import numpy


def SiO2trans(E, att_position):
    """
    :param E: energy in keV
    :param att_position: attenuator position (raw bits field value)
    :returns: oyield
    """
    coeff = [-0.0030624, 0.16457, -2.708, 20.659, -80.612, 153.42, -109.27]
    ln_E = numpy.log(numpy.asarray(E))
    muL = 0.0
    for c in coeff:
        muL = muL * ln_E + c
    muL = numpy.exp(muL)  # 1/cm
    thickness = numpy.asarray(att_position) * 1.25  # cm
    return numpy.exp(-thickness * muL)
