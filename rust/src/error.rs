//! Configuration error types

use std::fmt;

/// Configuration result type
pub type ConfigResult<T> = Result<T, ConfigError>;

/// Configuration error
#[derive(Debug)]
pub enum ConfigError {
    /// File error (not found, permission denied, etc.)
    FileError(String),
    /// Parse error (invalid YAML, etc.)
    ParseError(String),
    /// Validation error (invalid values, missing required fields, etc.)
    ValidationError(String),
    /// Other errors
    Other(String),
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            ConfigError::FileError(msg) => write!(f, "File error: {}", msg),
            ConfigError::ParseError(msg) => write!(f, "Parse error: {}", msg),
            ConfigError::ValidationError(msg) => write!(f, "Validation error: {}", msg),
            ConfigError::Other(msg) => write!(f, "Error: {}", msg),
        }
    }
}

impl std::error::Error for ConfigError {}

