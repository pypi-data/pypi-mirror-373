from collections import namedtuple

Image = namedtuple("Image", "array")


def read_video_last_image(proxy):
    return Image(array=proxy.video_last_image)
