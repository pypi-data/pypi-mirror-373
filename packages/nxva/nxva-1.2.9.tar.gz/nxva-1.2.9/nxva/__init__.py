from .logger import ensure_default_logging

# When using streaming alone, provide a default console output with namespace "nxva".
# If an external configuration is present, this default will automatically be silenced/removed.
ensure_default_logging('nxva')