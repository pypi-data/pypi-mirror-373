from .import_utils import UnavailableObject

# Proxy to the current Bliss session object (if any).
try:
    from bliss import current_session
except ImportError as ex:
    current_session = UnavailableObject(ex)

# Proxy to a namespace used by Bliss scripts to access objects
# and functions from the current Bliss session (if any).
try:
    from bliss import setup_globals
except ImportError as ex:
    setup_globals = UnavailableObject(ex)
