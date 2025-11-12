//! FKS Standard Configuration Loader for Rust Services
//!
//! This crate provides a standardized way to load and validate YAML configuration
//! files for FKS microservices using serde and serde_yaml.
//!
//! # Usage
//!
//! ```rust
//! use fks_config::load_config;
//! use fks_config::FKSConfig;
//!
//! // Load configuration
//! let config = load_config("config.yaml").expect("Failed to load config");
//!
//! // Access configuration values
//! println!("Service: {}", config.service.name);
//! println!("Port: {}", config.service.port);
//! ```

use serde::{Deserialize, Serialize};
use std::env;
use std::fs::File;
use std::io::BufReader;
use std::path::{Path, PathBuf};

pub mod error;
pub use error::{ConfigError, ConfigResult};

/// Service configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceConfig {
    /// Service name (e.g., fks_api, fks_data)
    pub name: String,
    /// Service port (1024-65535)
    #[serde(default = "default_port")]
    pub port: u16,
    /// Service host address
    #[serde(default = "default_host")]
    pub host: String,
    /// Environment name
    #[serde(default = "default_environment")]
    pub environment: String,
    /// Logging level
    #[serde(default = "default_log_level")]
    pub log_level: String,
}

fn default_port() -> u16 {
    8000
}

fn default_host() -> String {
    "0.0.0.0".to_string()
}

fn default_environment() -> String {
    "development".to_string()
}

fn default_log_level() -> String {
    "INFO".to_string()
}

/// Database configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    /// Database host
    #[serde(default = "default_db_host")]
    pub host: String,
    /// Database port
    #[serde(default = "default_db_port")]
    pub port: u16,
    /// Database name
    pub name: Option<String>,
    /// Database user
    pub user: Option<String>,
    /// Database password
    pub password: Option<String>,
    /// Connection pool size
    #[serde(default = "default_pool_size")]
    pub pool_size: u32,
    /// Max connection pool overflow
    #[serde(default = "default_max_overflow")]
    pub max_overflow: u32,
}

fn default_db_host() -> String {
    "localhost".to_string()
}

fn default_db_port() -> u16 {
    5432
}

fn default_pool_size() -> u32 {
    10
}

fn default_max_overflow() -> u32 {
    20
}

/// Redis configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RedisConfig {
    /// Redis host
    #[serde(default = "default_redis_host")]
    pub host: String,
    /// Redis port
    #[serde(default = "default_redis_port")]
    pub port: u16,
    /// Redis database number
    #[serde(default)]
    pub db: u8,
    /// Redis password
    pub password: Option<String>,
    /// Decode responses as strings
    #[serde(default = "default_decode_responses")]
    pub decode_responses: bool,
}

fn default_redis_host() -> String {
    "localhost".to_string()
}

fn default_redis_port() -> u16 {
    6379
}

fn default_decode_responses() -> bool {
    true
}

/// API configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct APIConfig {
    /// Base URL for API endpoints
    pub base_url: Option<String>,
    /// API request timeout in seconds
    #[serde(default = "default_timeout")]
    pub timeout: u64,
    /// Number of retry attempts
    #[serde(default = "default_retry_attempts")]
    pub retry_attempts: u32,
    /// Retry delay in seconds
    #[serde(default = "default_retry_delay")]
    pub retry_delay: u64,
}

fn default_timeout() -> u64 {
    30
}

fn default_retry_attempts() -> u32 {
    3
}

fn default_retry_delay() -> u64 {
    1
}

/// Authentication configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthConfig {
    /// Authentication secret key
    pub secret_key: Option<String>,
    /// Token expiry time in seconds
    #[serde(default = "default_token_expiry")]
    pub token_expiry: u64,
    /// JWT algorithm
    #[serde(default = "default_algorithm")]
    pub algorithm: String,
}

fn default_token_expiry() -> u64 {
    3600
}

fn default_algorithm() -> String {
    "HS256".to_string()
}

/// Monitoring configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MonitoringConfig {
    /// Enable monitoring
    #[serde(default = "default_enabled")]
    pub enabled: bool,
    /// Prometheus metrics port
    #[serde(default = "default_prometheus_port")]
    pub prometheus_port: u16,
    /// Health check interval in seconds
    #[serde(default = "default_health_check_interval")]
    pub health_check_interval: u64,
}

fn default_enabled() -> bool {
    true
}

fn default_prometheus_port() -> u16 {
    9090
}

fn default_health_check_interval() -> u64 {
    30
}

/// Paths configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PathsConfig {
    /// Data directory path
    #[serde(default = "default_data_dir")]
    pub data_dir: String,
    /// Logs directory path
    #[serde(default = "default_logs_dir")]
    pub logs_dir: String,
    /// Cache directory path
    #[serde(default = "default_cache_dir")]
    pub cache_dir: String,
    /// Models directory path
    #[serde(default = "default_models_dir")]
    pub models_dir: String,
}

fn default_data_dir() -> String {
    "./data".to_string()
}

fn default_logs_dir() -> String {
    "./logs".to_string()
}

fn default_cache_dir() -> String {
    "./cache".to_string()
}

fn default_models_dir() -> String {
    "./models".to_string()
}

/// FKS configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FKSConfig {
    /// Service configuration (required)
    pub service: ServiceConfig,
    /// Database configuration (optional)
    pub database: Option<DatabaseConfig>,
    /// Redis configuration (optional)
    pub redis: Option<RedisConfig>,
    /// API configuration (optional)
    pub api: Option<APIConfig>,
    /// Authentication configuration (optional)
    pub auth: Option<AuthConfig>,
    /// Monitoring configuration (optional)
    pub monitoring: Option<MonitoringConfig>,
    /// Paths configuration (optional)
    pub paths: Option<PathsConfig>,
    /// Feature flags (optional)
    pub features: Option<std::collections::HashMap<String, bool>>,
    /// Service-specific configuration (optional)
    #[serde(flatten)]
    pub service_specific: Option<serde_yaml::Value>,
}

impl FKSConfig {
    /// Validate configuration
    pub fn validate(&self) -> ConfigResult<()> {
        // Validate service name pattern
        if !self.service.name.starts_with("fks_") {
            return Err(ConfigError::ValidationError(
                "Service name must start with 'fks_'".to_string(),
            ));
        }

        // Validate port range
        if self.service.port < 1024 || self.service.port > 65535 {
            return Err(ConfigError::ValidationError(
                "Service port must be between 1024 and 65535".to_string(),
            ));
        }

        // Validate environment
        let valid_environments = ["development", "staging", "production", "test"];
        if !valid_environments.contains(&self.service.environment.as_str()) {
            return Err(ConfigError::ValidationError(format!(
                "Invalid environment: {}. Must be one of: {:?}",
                self.service.environment, valid_environments
            )));
        }

        // Validate log level
        let valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];
        if !valid_log_levels.contains(&self.service.log_level.as_str()) {
            return Err(ConfigError::ValidationError(format!(
                "Invalid log level: {}. Must be one of: {:?}",
                self.service.log_level, valid_log_levels
            )));
        }

        Ok(())
    }
}

/// Load YAML configuration file
pub fn load_yaml<P: AsRef<Path>>(file_path: P) -> ConfigResult<serde_yaml::Value> {
    let file = File::open(file_path.as_ref())
        .map_err(|e| ConfigError::FileError(format!("Failed to open file: {}", e)))?;

    let reader = BufReader::new(file);
    let config: serde_yaml::Value = serde_yaml::from_reader(reader)
        .map_err(|e| ConfigError::ParseError(format!("Failed to parse YAML: {}", e)))?;

    // Apply environment variable overrides
    let config = apply_env_overrides(config);

    Ok(config)
}

/// Apply environment variable overrides to configuration
fn apply_env_overrides(config: serde_yaml::Value) -> serde_yaml::Value {
    // This is a simplified implementation
    // In practice, you might want to use a more sophisticated approach
    // that handles nested structures and type conversions
    
    // For now, we'll just return the config as-is
    // Environment variables can be applied during deserialization
    // by checking env vars in the deserialize functions
    
    config
}

/// Load FKS configuration from YAML file
pub fn load_config<P: AsRef<Path>>(config_path: P) -> ConfigResult<FKSConfig> {
    // If config_path is None, try to find config file
    let path = if config_path.as_ref().to_string_lossy().is_empty() {
        find_config_file()?
    } else {
        config_path.as_ref().to_path_buf()
    };

    // Load YAML
    let config_data = load_yaml(&path)?;

    // Deserialize into FKSConfig
    let config: FKSConfig = serde_yaml::from_value(config_data)
        .map_err(|e| ConfigError::ParseError(format!("Failed to deserialize config: {}", e)))?;

    // Validate configuration
    config.validate()?;

    Ok(config)
}

/// Find configuration file in common locations
fn find_config_file() -> ConfigResult<PathBuf> {
    // Check environment variable
    if let Ok(path) = env::var("FKS_CONFIG_PATH") {
        let path = PathBuf::from(path);
        if path.exists() {
            return Ok(path);
        }
    }

    // Try common locations
    let current_dir = env::current_dir()
        .map_err(|e| ConfigError::FileError(format!("Failed to get current directory: {}", e)))?;

    let candidates = [
        current_dir.join("config.yaml"),
        current_dir.join("config.yml"),
        current_dir.join("config").join("config.yaml"),
        current_dir.join("config").join("config.yml"),
    ];

    for candidate in &candidates {
        if candidate.exists() {
            return Ok(candidate.clone());
        }
    }

    Err(ConfigError::FileError(
        "Configuration file not found. Set FKS_CONFIG_PATH environment variable \
         or place config.yaml in current directory or config/ subdirectory."
            .to_string(),
    ))
}

/// Get configuration value by key path (dot-separated)
pub fn get_config_value(config: &FKSConfig, key_path: &str) -> Option<serde_yaml::Value> {
    // Simplified implementation
    // In practice, you might want to use a more sophisticated approach
    // that handles nested structures
    
    let keys: Vec<&str> = key_path.split('.').collect();
    
    // This is a placeholder - actual implementation would traverse the config
    // based on the key path
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_config() {
        // This would require a test config file
        // For now, we'll just test that the function compiles
        let result = load_config("nonexistent.yaml");
        assert!(result.is_err());
    }
}

