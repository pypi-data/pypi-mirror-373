from . import controllers


def att(att_position):
    atten.bits = att_position


def ct(count_time: float = 1, *detectors, **kwargs):
    for detector in detectors:
        detector.ct(count_time, **kwargs)


def limatake(expotime: float, nbframes: int = 1):
    p3.ct(expotime * nbframes)


source = controllers.Source()
energy = controllers.Mono(parent=source)
ehss = controllers.Shutter()
atten = controllers.Attenuator(parent=energy)
sample = controllers.DiffractingSample(parent=atten)
p3 = controllers.LimaDetector(parent=sample)
