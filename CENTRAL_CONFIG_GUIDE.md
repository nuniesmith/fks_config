# FKS Central Configuration Guide

**Date**: 2025-01-15  
**Location**: `repo/main/config/`  
**Purpose**: Guide for managing central configuration across all microservices

---

## 🎯 Overview

All FKS microservices now use centralized configuration stored in `repo/main/config/`. This ensures:
- **Single source of truth** for service configuration
- **Consistent settings** across all services
- **Easy updates** - change once, apply everywhere
- **Version control** - track all config changes

---

## 📁 Directory Structure

```
repo/main/config/
├── service_registry.json          # Service discovery (ports, URLs, dependencies)
├── services/                       # Service-specific configs
│   ├── fks_web.yaml
│   ├── fks_api.yaml
│   ├── fks_app.yaml
│   ├── fks_data.yaml
│   ├── fks_execution.yaml
│   ├── fks_ai.yaml
│   ├── fks_analyze.yaml
│   ├── fks_auth.yaml
│   ├── fks_main.yaml
│   ├── fks_meta.yaml
│   ├── fks_monitor.yaml
│   ├── fks_training.yaml
│   └── fks_portfolio.yaml
├── shared/                         # Shared configuration
│   ├── logging.yaml                # Logging configuration
│   ├── monitoring.yaml             # Monitoring configuration
│   ├── database.yaml               # Database configuration
│   └── redis.yaml                  # Redis configuration
└── environments/                   # Environment-specific overrides
    ├── development.yaml
    ├── staging.yaml
    └── production.yaml
```

---

## 🔧 Service Registry

**File**: `service_registry.json`

**Purpose**: Single source of truth for:
- Service names
- Ports
- Base URLs
- Health URLs
- Dependencies

**Usage**: All services reference this for service discovery.

**Update Process**:
1. Edit `service_registry.json`
2. Update affected service configs
3. Restart services

---

## 📋 Service Configuration Files

Each service has a YAML config in `repo/main/config/services/`:

**Structure**:
```yaml
service:
  name: fks_app
  port: 8002
  host: 0.0.0.0
  environment: development
  log_level: INFO

dependencies:
  fks_data:
    base_url: http://fks_data:8003
    health_url: http://fks_data:8003/health

database:
  host: postgres
  port: 5432
  name: trading_db

paths:
  logs: /app/logs  # Inside container, not mounted
```

---

## 🔄 How Services Access Config

### Method 1: Volume Mount (Recommended)

Mount central config as read-only volume:

```yaml
# In service docker-compose.yml
volumes:
  - ../../main/config:/app/config:ro
environment:
  - FKS_CONFIG_PATH=/app/config/services/fks_app.yaml
```

### Method 2: Copy at Build Time

Copy config during Docker build:

```dockerfile
# In service Dockerfile
COPY ../main/config /app/config
ENV FKS_CONFIG_PATH=/app/config/services/fks_app.yaml
```

### Method 3: Environment Variables

Override config via environment variables:

```bash
FKS_SERVICE_PORT=8002
FKS_DATABASE_HOST=postgres
```

---

## 📝 Logging Configuration

**Important**: Logs are now stored **inside containers** at `/app/logs`, not mounted externally.

**Shared Config**: `repo/main/config/shared/logging.yaml`

**Features**:
- JSON or text format
- Automatic rotation (10MB, 5 backups)
- 7-day retention
- Docker logging driver (json-file, 10MB max, 3 files)

**Access Logs**:
```bash
# View logs via Docker
docker logs fks_app
docker logs -f fks_app  # Follow

# Or exec into container
docker exec -it fks_app cat /app/logs/app.log
```

---

## 🔍 Configuration Validation

### Python Services

```python
from fks_config import load_config

config = load_config("/app/config/services/fks_app.yaml")
# Config is automatically validated
```

### Rust Services

```rust
use fks_config::load_config;

let config = load_config("/app/config/services/fks_meta.yaml")?;
config.validate()?;
```

---

## 🚀 Updating Configuration

### Step 1: Edit Config

Edit the appropriate file in `repo/main/config/`:
- Service-specific: `services/fks_app.yaml`
- Shared: `shared/logging.yaml`
- Registry: `service_registry.json`

### Step 2: Restart Services

```bash
# Restart specific service
docker-compose -f repo/app/docker-compose.yml restart

# Or rebuild if config copied at build time
docker-compose -f repo/app/docker-compose.yml up -d --build
```

### Step 3: Verify

```bash
# Check health
curl http://localhost:8002/health

# Check logs
docker logs fks_app
```

---

## ⚠️ Important Notes

### Logs Location

**Old (Monorepo)**: `./logs/` mounted externally  
**New (Microservices)**: `/app/logs/` inside container

**Why**: Each service is now independent. Logs stay in container and are accessed via `docker logs`.

### Secrets

**Never commit secrets** to config files. Use:
- Environment variables
- Docker secrets
- Kubernetes secrets
- `.env` files (gitignored)

### Environment Overrides

Use environment-specific configs in `environments/`:
- `development.yaml` - Local development
- `staging.yaml` - Staging environment
- `production.yaml` - Production environment

---

## 📚 Related Documentation

- `README.md` - Config system overview
- `QUICK_START.md` - Quick start guide
- `IMPLEMENTATION_GUIDE.md` - Implementation details
- `service_registry.json` - Service discovery

---

**Last Updated**: 2025-01-15

