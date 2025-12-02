# FKS Configuration System Implementation Guide

This guide explains how to implement the standard FKS configuration system in your service.

## Quick Start

### For Python Services

1. **Copy the configuration loader**:
   ```bash
   cp config/python/fks_config.py your_service/src/fks_config.py
   ```

2. **Install dependencies**:
   ```bash
   pip install pyyaml pydantic
   # Or add to requirements.txt:
   # pyyaml>=6.0
   # pydantic>=2.0
   ```

3. **Create a configuration file**:
   ```bash
   cp config/fks-config-base.yaml your_service/config.yaml
   # Edit config.yaml with your service-specific settings
   ```

4. **Load configuration in your service**:
   ```python
   from fks_config import load_config
   
   # Load configuration
   config = load_config("config.yaml")
   
   # Use configuration
   print(f"Starting {config.service.name} on port {config.service.port}")
   ```

### For Rust Services

1. **Add dependency to Cargo.toml**:
   ```toml
   [dependencies]
   fks-config = { path = "../config/rust" }
   serde = { version = "1.0", features = ["derive"] }
   serde_yaml = "0.9"
   ```

2. **Create a configuration file**:
   ```bash
   cp config/fks-config-base.yaml your_service/config.yaml
   # Edit config.yaml with your service-specific settings
   ```

3. **Load configuration in your service**:
   ```rust
   use fks_config::load_config;
   
   fn main() -> Result<(), Box<dyn std::error::Error>> {
       let config = load_config("config.yaml")?;
       println!("Starting {} on port {}", config.service.name, config.service.port);
       Ok(())
   }
   ```

## Step-by-Step Implementation

### Step 1: Create Configuration File

Create a `config.yaml` file in your service root directory:

```yaml
service:
  name: fks_your_service
  port: 8000
  environment: development
  log_level: INFO

# Add other sections as needed
database:
  host: localhost
  port: 5432
  name: fks_db

# Add service-specific configuration
service_specific:
  your_option: value
```

### Step 2: Update Service Code

#### Python

Replace environment variable reading with configuration loading:

**Before**:
```python
import os

service_port = int(os.getenv("SERVICE_PORT", "8000"))
service_name = os.getenv("SERVICE_NAME", "fks_service")
```

**After**:
```python
from fks_config import load_config

config = load_config("config.yaml")
service_port = config.service.port
service_name = config.service.name
```

#### Rust

Replace environment variable reading with configuration loading:

**Before**:
```rust
use std::env;

let service_port = env::var("SERVICE_PORT")
    .unwrap_or_else(|_| "8000".to_string())
    .parse()
    .unwrap_or(8000);
```

**After**:
```rust
use fks_config::load_config;

let config = load_config("config.yaml")?;
let service_port = config.service.port;
```

### Step 3: Handle Environment Variable Overrides

The configuration system automatically supports environment variable overrides:

```bash
# Override service port
export FKS_SERVICE_PORT=8001

# Override database host
export FKS_DATABASE_HOST=db.example.com

# Override Redis password
export FKS_REDIS_PASSWORD=secret123
```

### Step 4: Add Service-Specific Configuration

Add service-specific configuration in the `service_specific` section:

```yaml
service_specific:
  your_option: value
  nested:
    option: value
```

Access it in your code:

#### Python
```python
if config.service_specific:
    your_option = config.service_specific.get("your_option")
```

#### Rust
```rust
if let Some(service_specific) = &config.service_specific {
    // Access service_specific values
    // Note: This requires parsing the Value type
}
```

### Step 5: Validate Configuration

#### Python

Validation is automatic when loading configuration. Invalid configurations will raise `ValidationError`:

```python
from fks_config import load_config
from pydantic import ValidationError

try:
    config = load_config("config.yaml")
except ValidationError as e:
    print(f"Configuration validation failed: {e}")
    # Handle error
```

#### Rust

Validation is automatic when loading configuration. Invalid configurations will return `ConfigError`:

```rust
use fks_config::{load_config, ConfigError};

match load_config("config.yaml") {
    Ok(config) => {
        // Use config
    }
    Err(ConfigError::ValidationError(msg)) => {
        eprintln!("Configuration validation failed: {}", msg);
        // Handle error
    }
    Err(e) => {
        eprintln!("Failed to load configuration: {}", e);
        // Handle error
    }
}
```

### Step 6: Use Configuration in Your Service

#### Python Example (FastAPI)

```python
from fastapi import FastAPI
from fks_config import load_config

# Load configuration
config = load_config("config.yaml")

# Create FastAPI app
app = FastAPI(title=config.service.name)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": config.service.name}

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.service.host,
        port=config.service.port
    )
```

#### Rust Example (Actix Web)

```rust
use actix_web::{web, App, HttpServer, HttpResponse};
use fks_config::load_config;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Load configuration
    let config = load_config("config.yaml")
        .expect("Failed to load configuration");

    // Create HTTP server
    HttpServer::new(|| {
        App::new()
            .route("/health", web::get().to(health))
    })
    .bind((config.service.host.as_str(), config.service.port))?
    .run()
    .await
}

async fn health() -> HttpResponse {
    HttpResponse::Ok().json(serde_json::json!({
        "status": "healthy"
    }))
}
```

## Migration Checklist

- [ ] Copy configuration loader to your service
- [ ] Install dependencies (Python: pyyaml, pydantic; Rust: serde, serde_yaml)
- [ ] Create `config.yaml` file
- [ ] Update service code to use `load_config()`
- [ ] Replace environment variable reading with configuration access
- [ ] Add service-specific configuration if needed
- [ ] Test configuration loading
- [ ] Test environment variable overrides
- [ ] Update documentation
- [ ] Update Docker/Kubernetes configurations if needed

## Common Issues

### Configuration file not found

**Problem**: `FileNotFoundError` or `ConfigError::FileError`

**Solution**: 
- Check that `config.yaml` exists in the expected location
- Set `FKS_CONFIG_PATH` environment variable to specify the path
- Check file permissions

### Validation errors

**Problem**: `ValidationError` or `ConfigError::ValidationError`

**Solution**:
- Check that your configuration matches the schema
- Verify that required fields are present
- Check that values match the expected types (string, integer, boolean)
- Review error messages for specific validation failures

### Environment variable overrides not working

**Problem**: Environment variables are not overriding YAML values

**Solution**:
- Check that environment variable names match the format: `FKS_<SECTION>_<KEY>`
- Ensure environment variables are set before loading configuration
- Check that value types match (string, integer, boolean)

## Next Steps

1. **Review examples**: See `config/examples/` for service-specific examples
2. **Customize configuration**: Add service-specific configuration options
3. **Test thoroughly**: Test configuration loading in different environments
4. **Update documentation**: Document service-specific configuration options
5. **Deploy**: Deploy your service with the new configuration system

## Support

For questions or issues:
- Review the main README: `config/README.md`
- Check examples: `config/examples/`
- Review the schema: `config/fks-config-schema.json`

