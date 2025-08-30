from contextlib import ExitStack
from contextlib import contextmanager
from unittest.mock import patch

from . import attenuator
from . import setup_globals

try:
    import blissdata.lima.image_utils  # noqa F401

    from . import image_utils

    lima_image = None
except ImportError:
    from . import lima_image

    image_utils = None


@contextmanager
def mock_id31():
    with ExitStack() as stack:
        ctx = patch("blissoda.id31.optimize_exposure.setup_globals", new=setup_globals)
        stack.enter_context(ctx)
        ctx = patch("blissoda.id31.utils.setup_globals", new=setup_globals)
        stack.enter_context(ctx)
        ctx = patch("blissoda.id31.optimize_exposure.id31_attenuator", new=attenuator)
        stack.enter_context(ctx)
        if image_utils is None:
            ctx = patch("blissoda.id31.optimize_exposure.lima_image", new=lima_image)
            stack.enter_context(ctx)
        else:
            ctx = patch("blissoda.id31.optimize_exposure.image_utils", new=image_utils)
            stack.enter_context(ctx)
        yield
