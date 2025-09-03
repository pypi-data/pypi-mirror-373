# Enterprise Logger - Common Interface
# Re-export logger functionality for consistent imports

from runbooks.utils.logger import configure_logger


# Standard interface for enterprise logging
def get_logger(module_name: str):
    """Get configured logger for module - enterprise standard interface."""
    return configure_logger(module_name)


# Backward compatibility exports
__all__ = ["get_logger", "configure_logger"]
