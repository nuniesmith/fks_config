# FKS Services Central Configuration

**Date**: 2025-01-15  
**Location**: `repo/main/config/`  
**Purpose**: Central configuration management for all FKS microservices

---

## 📁 Configuration Structure

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
│   ├── monitoring.yaml            # Monitoring configuration
│   ├── database.yaml              # Database configuration
│   └── redis.yaml                 # Redis configuration
└── environments/                   # Environment-specific overrides
    ├── development.yaml
    ├── staging.yaml
    └── production.yaml
```

---

## 🔧 How Services Use Central Config

### Option 1: Mount Config Volume (Recommended)

In each service's `docker-compose.yml`:

```yaml
services:
  fks_app:
    volumes:
      - ../../main/config:/app/config:ro  # Read-only mount
    environment:
      - FKS_CONFIG_PATH=/app/config/services/fks_app.yaml
      - FKS_SHARED_CONFIG_PATH=/app/config/shared
```

### Option 2: Copy Config at Build Time

In each service's `Dockerfile`:

```dockerfile
# Copy central config
COPY --from=config-builder /config /app/config
ENV FKS_CONFIG_PATH=/app/config/services/fks_app.yaml
```

### Option 3: Environment Variables

Services can override config via environment variables:

```bash
FKS_SERVICE_PORT=8002
FKS_DATABASE_HOST=postgres
FKS_REDIS_URL=redis://redis:6379/0
```

---

## 📋 Service Configuration Files

Each service has a YAML config in `repo/main/config/services/` that includes:

- Service name, port, host
- Dependencies (from service_registry.json)
- Database connections
- Redis connections
- Logging configuration
- Monitoring configuration
- Service-specific settings

---

## 🔄 Configuration Updates

1. **Edit config in `repo/main/config/`**
2. **Restart affected services** (or use hot-reload if supported)
3. **Verify changes** via health checks

---

## 📝 Best Practices

1. **Never commit secrets** - Use environment variables
2. **Version control configs** - Track changes in git
3. **Test changes** - Validate before deploying
4. **Document service-specific configs** - In service READMEs

---

**Last Updated**: 2025-01-15

