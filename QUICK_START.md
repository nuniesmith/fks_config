# FKS Configuration System - Quick Start

## For Python Services

1. **Copy the configuration loader**:
   ```bash
   cp config/python/fks_config.py your_service/src/fks_config.py
   ```

2. **Install dependencies**:
   ```bash
   pip install pyyaml pydantic
   ```

3. **Create `config.yaml`**:
   ```yaml
   service:
     name: fks_your_service
     port: 8000
     environment: development
     log_level: INFO
   ```

4. **Use in your service**:
   ```python
   from fks_config import load_config
   
   config = load_config("config.yaml")
   print(config.service.name)  # fks_your_service
   print(config.service.port)  # 8000
   ```

## For Rust Services

1. **Add to `Cargo.toml`**:
   ```toml
   [dependencies]
   fks-config = { path = "../config/rust" }
   serde = { version = "1.0", features = ["derive"] }
   serde_yaml = "0.9"
   ```

2. **Create `config.yaml`** (same as Python)

3. **Use in your service**:
   ```rust
   use fks_config::load_config;
   
   let config = load_config("config.yaml")?;
   println!("Service: {}", config.service.name);
   println!("Port: {}", config.service.port);
   ```

## Environment Variable Overrides

```bash
export FKS_SERVICE_PORT=8001
export FKS_DATABASE_HOST=db.example.com
export FKS_REDIS_PASSWORD=secret123
```

## See Also

- `README.md` - Full documentation
- `IMPLEMENTATION_GUIDE.md` - Detailed implementation guide
- `examples/` - Service-specific examples
