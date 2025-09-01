try:
    from ._version import __version__
except ImportError:
    import warnings
    warnings.warn("Could not import version info")
    __version__ = "unknown"

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "pantheon-notebook"
    }]

# Server extension entry points
def _jupyter_server_extension_points():
    return [{
        "module": "pantheon_notebook",
    }]

def _load_jupyter_server_extension(server_app):
    """Load the extension"""
    from .server import _load_jupyter_server_extension as load_ext
    load_ext(server_app)

# Make the extension discoverable
load_jupyter_server_extension = _load_jupyter_server_extension