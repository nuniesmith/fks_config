"""
FKS Standard Configuration Loader for Python Services

This module provides a standardized way to load and validate YAML configuration
files for FKS microservices using Pydantic for validation.

Usage:
    from fks_config import load_config, FKSConfig

    # Load configuration
    config = load_config("config.yaml")
    
    # Access configuration values
    print(config.service.name)
    print(config.service.port)
    print(config.database.host if config.database else None)
"""

import os
from pathlib import Path
from typing import Any, Optional, Union

import yaml
from pydantic import BaseModel, Field, field_validator, ValidationError


class ServiceConfig(BaseModel):
    """Service configuration."""
    name: str = Field(..., pattern=r"^fks_[a-z]+$", description="Service name")
    port: int = Field(..., ge=1024, le=65535, description="Service port")
    host: str = Field(default="0.0.0.0", description="Service host")
    environment: str = Field(
        default="development",
        pattern="^(development|staging|production|test)$",
        description="Environment name"
    )
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level"
    )


class DatabaseConfig(BaseModel):
    """Database configuration."""
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    name: Optional[str] = Field(default=None, description="Database name")
    user: Optional[str] = Field(default=None, description="Database user")
    password: Optional[str] = Field(default=None, description="Database password")
    pool_size: int = Field(default=10, ge=1, description="Connection pool size")
    max_overflow: int = Field(default=20, ge=0, description="Max pool overflow")


class RedisConfig(BaseModel):
    """Redis configuration."""
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    db: int = Field(default=0, ge=0, description="Redis database number")
    password: Optional[str] = Field(default=None, description="Redis password")
    decode_responses: bool = Field(default=True, description="Decode responses")


class APIConfig(BaseModel):
    """API configuration."""
    base_url: Optional[str] = Field(default=None, description="Base URL")
    timeout: int = Field(default=30, ge=1, description="Timeout in seconds")
    retry_attempts: int = Field(default=3, ge=0, description="Retry attempts")
    retry_delay: int = Field(default=1, ge=0, description="Retry delay in seconds")


class AuthConfig(BaseModel):
    """Authentication configuration."""
    secret_key: Optional[str] = Field(default=None, description="Secret key")
    token_expiry: int = Field(default=3600, ge=1, description="Token expiry in seconds")
    algorithm: str = Field(
        default="HS256",
        pattern="^(HS256|HS384|HS512)$",
        description="JWT algorithm"
    )


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""
    enabled: bool = Field(default=True, description="Enable monitoring")
    prometheus_port: int = Field(default=9090, ge=1024, le=65535, description="Prometheus port")
    health_check_interval: int = Field(default=30, ge=1, description="Health check interval")


class PathsConfig(BaseModel):
    """Paths configuration."""
    data_dir: str = Field(default="./data", description="Data directory")
    logs_dir: str = Field(default="./logs", description="Logs directory")
    cache_dir: str = Field(default="./cache", description="Cache directory")
    models_dir: str = Field(default="./models", description="Models directory")


class FKSConfig(BaseModel):
    """FKS configuration model."""
    service: ServiceConfig
    database: Optional[DatabaseConfig] = None
    redis: Optional[RedisConfig] = None
    api: Optional[APIConfig] = None
    auth: Optional[AuthConfig] = None
    monitoring: Optional[MonitoringConfig] = None
    paths: Optional[PathsConfig] = None
    features: Optional[dict] = None
    service_specific: Optional[dict] = None

    @field_validator("service", mode="before")
    @classmethod
    def validate_service(cls, v):
        """Ensure service config is present."""
        if not v:
            raise ValueError("service configuration is required")
        return v

    class Config:
        """Pydantic configuration."""
        extra = "forbid"  # Don't allow extra fields
        validate_assignment = True  # Validate on assignment


def load_yaml(file_path: Union[str, Path]) -> dict:
    """
    Load YAML file and apply environment variable overrides.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Dictionary containing configuration
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)
    
    if config is None:
        config = {}
    
    # Apply environment variable overrides
    # Format: FKS_<SECTION>_<KEY> (e.g., FKS_SERVICE_PORT, FKS_DATABASE_HOST)
    env_prefix = "FKS_"
    
    def apply_env_overrides(data: dict, prefix: str = ""):
        """Recursively apply environment variable overrides."""
        for key, value in data.items():
            env_key = f"{env_prefix}{prefix}{key.upper()}"
            
            if isinstance(value, dict):
                apply_env_overrides(value, f"{prefix}{key.upper()}_")
            else:
                # Check for environment variable override
                env_value = os.getenv(env_key)
                if env_value is not None:
                    # Try to parse as appropriate type
                    if isinstance(value, bool):
                        data[key] = env_value.lower() in ("true", "1", "yes")
                    elif isinstance(value, int):
                        try:
                            data[key] = int(env_value)
                        except ValueError:
                            pass
                    elif isinstance(value, float):
                        try:
                            data[key] = float(env_value)
                        except ValueError:
                            pass
                    else:
                        data[key] = env_value
    
    apply_env_overrides(config)
    
    return config


def load_config(
    config_path: Union[str, Path, None] = None,
    validate: bool = True,
) -> FKSConfig:
    """
    Load and validate FKS configuration from YAML file.
    
    Args:
        config_path: Path to configuration file. If None, looks for:
                    1. FKS_CONFIG_PATH environment variable
                    2. config.yaml in current directory
                    3. config/config.yaml in current directory
        validate: Whether to validate configuration against schema
        
    Returns:
        FKSConfig instance
        
    Raises:
        FileNotFoundError: If configuration file not found
        ValidationError: If configuration validation fails
    """
    # Determine config path
    if config_path is None:
        config_path = os.getenv("FKS_CONFIG_PATH")
        if config_path is None:
            # Try common locations
            current_dir = Path.cwd()
            for path in [
                current_dir / "config.yaml",
                current_dir / "config.yml",
                current_dir / "config" / "config.yaml",
                current_dir / "config" / "config.yml",
            ]:
                if path.exists():
                    config_path = path
                    break
            
            if config_path is None:
                raise FileNotFoundError(
                    "Configuration file not found. Set FKS_CONFIG_PATH environment variable "
                    "or place config.yaml in current directory or config/ subdirectory."
                )
    
    # Load YAML
    config_data = load_yaml(config_path)
    
    # Validate and create config object
    if validate:
        try:
            config = FKSConfig(**config_data)
        except ValidationError as e:
            raise ValidationError(
                f"Configuration validation failed for {config_path}",
                e.errors(),
            ) from e
    else:
        # Create config without validation (not recommended)
        config = FKSConfig(**config_data)
    
    return config


def get_config_value(config: FKSConfig, key_path: str, default: Any = None) -> Any:
    """
    Get configuration value by dot-separated key path.
    
    Args:
        config: FKSConfig instance
        key_path: Dot-separated key path (e.g., "service.port", "database.host")
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    keys = key_path.split(".")
    value = config
    
    for key in keys:
        if hasattr(value, key):
            value = getattr(value, key)
        elif isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


# Convenience function for quick access
def get_config(config_path: Union[str, Path, None] = None) -> FKSConfig:
    """
    Get FKS configuration (convenience function).
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        FKSConfig instance
    """
    return load_config(config_path)

