import atexit

# Store the original atexit.register function
_original_atexit_register = atexit.register

def _filtered_atexit_register(func, *args, **kwargs):
    """
    Clean atexit interceptor that skips nanobind handlers to prevent segfaults due to MLX atexit cleanups.
    This should be registered early during Python runtime initialization.
    """
    # Skip nanobind handlers silently
    func_type_str = str(type(func))
    if 'nanobind' in func_type_str or func_type_str.startswith("<class 'nb_"):
        return lambda: None

    # Allow all other handlers to register normally
    return _original_atexit_register(func, *args, **kwargs)

def install_atexit_filter():
    """Install the atexit filter to prevent problematic nanobind registrations."""
    atexit.register = _filtered_atexit_register

def uninstall_atexit_filter():
    """Restore the original atexit.register function."""
    atexit.register = _original_atexit_register
