# FKS Standard Configuration System

This directory contains the standard configuration system for FKS microservices, supporting both Python and Rust services with YAML configuration files and schema validation.

## Overview

The FKS configuration system provides:
- **Standardized YAML configuration format** across all services
- **Schema validation** using JSON Schema
- **Environment variable overrides** for sensitive values
- **Type-safe configuration loading** in both Python and Rust
- **Service-specific configuration** support

## Directory Structure

```
config/
├── fks-config-schema.json          # JSON Schema for validation
├── fks-config-base.yaml            # Base configuration template
├── python/
│   └── fks_config.py               # Python configuration loader
├── rust/
│   ├── Cargo.toml                  # Rust crate configuration
│   └── src/
│       ├── lib.rs                  # Rust configuration loader
│       └── error.rs                # Error types
├── examples/
│   ├── python-example.yaml         # Python service example
│   ├── rust-example.yaml           # Rust service example
│   └── service-specific.yaml       # Service-specific example
└── README.md                       # This file
```

## Configuration Schema

The FKS configuration schema defines the following sections:

### Required Sections
- `service`: Service configuration (name, port, host, environment, log_level)

### Optional Sections
- `database`: Database configuration (PostgreSQL, etc.)
- `redis`: Redis configuration
- `api`: API configuration (timeouts, retries, etc.)
- `auth`: Authentication configuration (JWT, etc.)
- `monitoring`: Monitoring configuration (Prometheus, health checks)
- `paths`: Paths configuration (data, logs, cache, models)
- `features`: Feature flags
- `service_specific`: Service-specific configuration (varies by service)

## Usage

### Python Services

1. **Install dependencies**:
   ```bash
   pip install pyyaml pydantic
   ```

2. **Copy the configuration loader**:
   ```bash
   cp config/python/fks_config.py your_service/src/fks_config.py
   ```

3. **Create a configuration file** (e.g., `config.yaml`):
   ```yaml
   service:
     name: fks_api
     port: 8000
     environment: development
     log_level: INFO
   
   database:
     host: localhost
     port: 5432
     name: fks_db
   ```

4. **Load configuration in your service**:
   ```python
   from fks_config import load_config
   
   config = load_config("config.yaml")
   print(config.service.name)  # fks_api
   print(config.service.port)  # 8000
   print(config.database.host if config.database else None)  # localhost
   ```

### Rust Services

1. **Add dependency to `Cargo.toml`**:
   ```toml
   [dependencies]
   fks-config = { path = "../config/rust" }
   # Or if published to crates.io:
   # fks-config = "0.1.0"
   serde = { version = "1.0", features = ["derive"] }
   serde_yaml = "0.9"
   ```

2. **Create a configuration file** (e.g., `config.yaml`):
   ```yaml
   service:
     name: fks_meta
     port: 8005
     environment: development
     log_level: INFO
   
   service_specific:
     mt5_terminal_path: /path/to/mt5
     mt5_account_number: 12345
   ```

3. **Load configuration in your service**:
   ```rust
   use fks_config::load_config;
   
   fn main() -> Result<(), Box<dyn std::error::Error>> {
       let config = load_config("config.yaml")?;
       println!("Service: {}", config.service.name);
       println!("Port: {}", config.service.port);
       Ok(())
   }
   ```

## Environment Variable Overrides

Configuration values can be overridden using environment variables with the format:
`FKS_<SECTION>_<KEY>`

Examples:
- `FKS_SERVICE_PORT=8001` - Override service port
- `FKS_DATABASE_HOST=db.example.com` - Override database host
- `FKS_REDIS_PASSWORD=secret` - Override Redis password

**Note**: Environment variables take precedence over YAML values. This is useful for:
- Secrets (passwords, API keys)
- Environment-specific settings (dev, staging, production)
- Docker/Kubernetes deployments

## Configuration File Locations

The configuration loader looks for configuration files in the following order:

1. Path specified in `FKS_CONFIG_PATH` environment variable
2. `config.yaml` in current directory
3. `config.yml` in current directory
4. `config/config.yaml` in current directory
5. `config/config.yml` in current directory

## Validation

### Python (Pydantic)
Configuration is automatically validated when loaded using Pydantic models. Invalid configurations will raise `ValidationError` with detailed error messages.

### Rust (serde)
Configuration is validated during deserialization and by calling `config.validate()`. Invalid configurations will return `ConfigError::ValidationError`.

### JSON Schema
You can also validate YAML files against the JSON Schema using tools like:
- `yamllint` (syntax validation)
- `jsonschema` (schema validation)
- VS Code extensions (real-time validation)

## Service-Specific Configuration

Services can add service-specific configuration in the `service_specific` section. This section is not validated by the base schema, allowing each service to define its own structure.

Example for `fks_meta`:
```yaml
service_specific:
  mt5_terminal_path: /path/to/mt5
  mt5_account_number: 12345
  mt5_password: ""  # Use env var
  mt5_server: "MetaQuotes-Demo"
```

Example for `fks_execution`:
```yaml
service_specific:
  exchanges:
    - name: binance
      api_key: ""  # Use env var
      api_secret: ""  # Use env var
    - name: kraken
      api_key: ""  # Use env var
      api_secret: ""  # Use env var
```

## Best Practices

1. **Use environment variables for secrets**: Never commit passwords, API keys, or other secrets to version control. Use environment variables instead.

2. **Use different config files for different environments**: Create `config.dev.yaml`, `config.staging.yaml`, and `config.prod.yaml` files, and select the appropriate one based on the environment.

3. **Validate configuration on startup**: Always validate configuration when the service starts to catch errors early.

4. **Document service-specific configuration**: Document any service-specific configuration options in your service's README.

5. **Use feature flags**: Use the `features` section to enable/disable features without code changes.

## Examples

See the `examples/` directory for example configuration files for different service types.

## Migration Guide

### Migrating from Environment-Only Configuration

If your service currently uses only environment variables:

1. Create a `config.yaml` file based on `fks-config-base.yaml`
2. Move non-sensitive configuration to YAML
3. Keep sensitive values (passwords, API keys) as environment variables
4. Update your service to use `load_config()` instead of reading env vars directly

### Migrating from Existing Config Managers

If your service uses an existing config manager (e.g., `FKSConfigManager`):

1. Review your current configuration structure
2. Map it to the FKS standard schema
3. Create a `config.yaml` file
4. Update your service to use `load_config()`
5. Test thoroughly before deploying

## Troubleshooting

### Configuration file not found
- Check that the file exists in one of the expected locations
- Set `FKS_CONFIG_PATH` environment variable to specify the path explicitly

### Validation errors
- Check that your configuration matches the schema
- Use a YAML validator to check for syntax errors
- Review the error messages for specific validation failures

### Environment variable overrides not working
- Check that the environment variable name matches the format: `FKS_<SECTION>_<KEY>`
- Ensure the environment variable is set before loading the configuration
- Check that the value type matches the expected type (string, integer, boolean)

## Contributing

When adding new configuration options:
1. Update the JSON Schema (`fks-config-schema.json`)
2. Update the Python models (`python/fks_config.py`)
3. Update the Rust models (`rust/src/lib.rs`)
4. Update this README
5. Add examples if needed

## License

MIT License - See LICENSE file for details

