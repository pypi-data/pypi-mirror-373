"""
Configuration management for CloudOps Runbooks.

This module handles loading, saving, and managing configuration settings
for the runbooks package, including AWS profiles, regions, and assessment settings.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from loguru import logger

try:
    from pydantic import BaseModel, Field

    _HAS_PYDANTIC = True
except ImportError:
    _HAS_PYDANTIC = False

    # Fallback BaseModel
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def model_dump(self, exclude_none=True):
            result = {}
            for key, value in self.__dict__.items():
                if not exclude_none or value is not None:
                    result[key] = value
            return result

    def Field(default=None, default_factory=None, description=""):
        if default_factory:
            return default_factory()
        return default


from runbooks.utils import ensure_directory


class RunbooksConfig(BaseModel):
    """Configuration model for CloudOps Runbooks."""

    # AWS Configuration
    aws_profile: str = Field(default="default", description="Default AWS profile")
    aws_region: Optional[str] = Field(default=None, description="Default AWS region")

    # Assessment Configuration
    cfat_checks: Dict[str, bool] = Field(
        default_factory=lambda: {
            "cloudtrail": True,
            "config": True,
            "iam": True,
            "vpc": True,
            "ec2": True,
            "organizations": True,
            "control_tower": True,
            "kms": True,
        },
        description="CFAT checks to run by default",
    )
    cfat_severity_threshold: str = Field(default="WARNING", description="Minimum severity for CFAT reports")

    # Inventory Configuration
    inventory_parallel: bool = Field(default=True, description="Run inventory collection in parallel")
    inventory_cache_ttl: int = Field(default=3600, description="Inventory cache TTL in seconds")
    inventory_include_costs: bool = Field(default=False, description="Include cost data in inventory")

    # Output Configuration
    default_output_format: str = Field(default="console", description="Default output format")
    reports_directory: str = Field(default="reports", description="Directory for generated reports")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Default log level")
    log_file: Optional[str] = Field(default=None, description="Log file path")

    class Config:
        """Pydantic config."""

        extra = "allow"


def get_default_config_path() -> Path:
    """
    Get the default configuration file path.

    Returns:
        Path to the default config file
    """
    config_dir = Path.home() / ".runbooks"
    ensure_directory(config_dir)
    return config_dir / "config.yaml"


def load_config(config_path: Optional[Path] = None) -> RunbooksConfig:
    """
    Load configuration from file or return default configuration.

    Args:
        config_path: Path to configuration file

    Returns:
        Loaded configuration object
    """
    if config_path is None:
        config_path = get_default_config_path()

    if not config_path.exists():
        logger.info(f"Config file not found at {config_path}, using defaults")
        config = RunbooksConfig()
        save_config(config, config_path)
        return config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}

        # Handle environment variable substitution
        config_data = _substitute_env_vars(config_data)

        config = RunbooksConfig(**config_data)
        logger.debug(f"Loaded configuration from {config_path}")
        return config

    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        logger.info("Using default configuration")
        return RunbooksConfig()


def save_config(config: RunbooksConfig, config_path: Optional[Path] = None) -> None:
    """
    Save configuration to file.

    Args:
        config: Configuration object to save
        config_path: Path to save configuration file
    """
    if config_path is None:
        config_path = get_default_config_path()

    try:
        ensure_directory(config_path.parent)

        config_dict = config.model_dump(exclude_none=True)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2, sort_keys=True)

        logger.debug(f"Saved configuration to {config_path}")

    except Exception as e:
        logger.error(f"Error saving config to {config_path}: {e}")
        raise


def update_config(updates: Dict[str, Any], config_path: Optional[Path] = None) -> RunbooksConfig:
    """
    Update specific configuration values.

    Args:
        updates: Dictionary of configuration updates
        config_path: Path to configuration file

    Returns:
        Updated configuration object
    """
    config = load_config(config_path)

    # Update configuration
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            logger.warning(f"Unknown configuration key: {key}")

    save_config(config, config_path)
    return config


def _substitute_env_vars(data: Any) -> Any:
    """
    Recursively substitute environment variables in configuration data.

    Args:
        data: Configuration data

    Returns:
        Data with environment variables substituted
    """
    if isinstance(data, dict):
        return {key: _substitute_env_vars(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_substitute_env_vars(item) for item in data]
    elif isinstance(data, str):
        # Simple environment variable substitution ${VAR_NAME}
        if data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            return os.getenv(env_var, data)
        return data
    else:
        return data


def get_aws_session_config(config: RunbooksConfig) -> Dict[str, str]:
    """
    Get AWS session configuration from runbooks config.

    Args:
        config: Runbooks configuration

    Returns:
        Dictionary with AWS session parameters
    """
    session_config = {"profile_name": config.aws_profile}

    if config.aws_region:
        session_config["region_name"] = config.aws_region

    return session_config


def validate_config(config: RunbooksConfig) -> bool:
    """
    Validate configuration settings.

    Args:
        config: Configuration to validate

    Returns:
        True if configuration is valid
    """
    try:
        # Validate AWS profile if specified
        if config.aws_profile != "default":
            from runbooks.utils import validate_aws_profile

            if not validate_aws_profile(config.aws_profile):
                logger.warning(f"AWS profile '{config.aws_profile}' not found")

        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config.log_level not in valid_levels:
            logger.warning(f"Invalid log level '{config.log_level}', using INFO")
            config.log_level = "INFO"

        # Validate severity threshold
        valid_severities = ["INFO", "WARNING", "CRITICAL"]
        if config.cfat_severity_threshold not in valid_severities:
            logger.warning(f"Invalid CFAT severity '{config.cfat_severity_threshold}', using WARNING")
            config.cfat_severity_threshold = "WARNING"

        return True

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False
