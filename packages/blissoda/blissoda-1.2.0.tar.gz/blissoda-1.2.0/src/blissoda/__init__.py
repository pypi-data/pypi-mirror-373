try:
    from gevent.monkey import is_anything_patched
    from gevent.monkey import is_module_patched
except ImportError:
    pass
else:
    if is_anything_patched() and not is_module_patched("threading"):
        try:
            # comes with ewoksjob (celery):
            from kombu.utils import compat
        except ImportError:
            pass
        else:
            # Make Celery use `celery.backends.asynchronous.Drainer`
            # instead of `celery.backends.asynchronous.geventDrainer`.
            # The later causes CTRL-C to not be raised and other things
            # like Bliss scans to hang when calling `AsyncResult.get`.

            compat._environment = "default"

            # The real solution is to patch threads.
