# Configuration System Location

## Repository Location

The FKS standard configuration system is located in the **fks_main** repository at:

```
repo/main/config/
```

This location was chosen because:
1. **fks_main** is the orchestrator service that manages all other services
2. **fks_main** is version-controlled (unlike the top-level directory)
3. **fks_main** serves as the central hub for shared infrastructure
4. Other services can easily reference this location

## Accessing from Other Services

### Python Services

Copy the configuration loader to your service:

```bash
# From your service repository root (assuming services are in repo/ directory)
cp ../main/config/python/fks_config.py your_service/src/fks_config.py
```

### Rust Services

Reference the configuration crate in your `Cargo.toml`:

```toml
[dependencies]
fks-config = { path = "../main/config/rust" }
serde = { version = "1.0", features = ["derive"] }
serde_yaml = "0.9"
```

## Directory Structure

The FKS configuration system files are located in `repo/main/config/` alongside existing FKS Main configuration files:

```
repo/main/config/
├── fks-config-schema.json          # JSON Schema for validation (FKS Config System)
├── fks-config-base.yaml            # Base configuration template (FKS Config System)
├── python/                         # Python configuration loader (FKS Config System)
│   ├── fks_config.py
│   └── requirements.txt
├── rust/                           # Rust configuration loader (FKS Config System)
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       └── error.rs
├── examples/                       # Configuration examples (FKS Config System)
│   ├── python-service-example.yaml
│   ├── rust-service-example.yaml
│   └── service-specific-example.yaml
├── README.md                       # Main documentation (FKS Config System)
├── IMPLEMENTATION_GUIDE.md         # Implementation guide (FKS Config System)
├── QUICK_START.md                  # Quick start guide (FKS Config System)
├── SUMMARY.md                      # Summary document (FKS Config System)
├── LOCATION.md                     # This file (FKS Config System)
├── test_config.py                  # Test script (FKS Config System)
├── caching.json                    # Existing FKS Main config files
├── circuit_breakers.json
├── service_registry.json
└── ... (other existing FKS Main config files)
```

## Git Status

This configuration system is **version-controlled** in the `fks_main` repository. All changes to the configuration system should be committed to the `fks_main` repository.

## Migration Notes

If you were previously using a configuration system from a different location, update your references to point to `repo/main/config/`.

## See Also

- `README.md` - Full documentation
- `IMPLEMENTATION_GUIDE.md` - Detailed implementation guide
- `QUICK_START.md` - Quick start guide

