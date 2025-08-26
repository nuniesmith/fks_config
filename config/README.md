# FKS Configuration System

## Overview

The FKS configuration system uses a master YAML file (`master.yaml`) as the single source of truth for all configuration settings. From this master file, we generate:

- Docker Compose files for different environments
- Environment variable files (.env)
- Kubernetes manifests
- Service-specific configuration files

## Master Configuration Structure

The `master.yaml` file is organized into the following sections:

### 1. System Configuration
```yaml
system:
  name: "FKS Trading Systems"
  version: "1.0.0"
  environments:
    development:
      debug: true
      log_level: DEBUG
    production:
      debug: false
      log_level: WARNING
```

### 2. Docker Configuration
```yaml
docker:
  registry: "${DOCKER_REGISTRY:-docker.io}"
  namespace: "${DOCKER_NAMESPACE:-nuniesmith}"
  networks:
    - name: "fks_network"
      driver: "bridge"
  volumes:
    - name: "postgres_data"
      driver: "local"
```

### 3. Service Definitions
```yaml
services:
  infrastructure:
    postgres:
      image: "postgres:16-alpine"
      ports:
        - "${POSTGRES_PORT:-5432}:5432"
  applications:
    api:
      type: "python-cpu"
      service_port: "${API_PORT:-8000}"
```

### 4. Kubernetes Configuration
```yaml
kubernetes:
  namespace_prefix: "fks"
  resources:
    development:
      replicas: 1
      cpu_limit: "500m"
```

## Using the Configuration System

### Building the Config Manager

```bash
cd src/rust/config
cargo build --release
```

### Generating Configurations

1. **Generate from master.yaml:**
```bash
./config-manager gen-from-master \
  --master-file config/master.yaml \
  --environment production \
  --output-dir ./generated/production
```

2. **Generate all configurations (legacy):**
```bash
./config-manager generate-all \
  --github-ref refs/heads/main \
  --github-sha abc123 \
  --output-dir ./config-output
```

3. **Generate Kubernetes manifests:**
```bash
./config-manager k8s-gen \
  --input ./config/k8s \
  --output ./k8s-manifests \
  --environment production
```

## Environment-Specific Configurations

The system supports three main environments:

- **development**: Local development with hot-reload and debug features
- **staging**: Pre-production environment with production-like settings
- **production**: Full production environment with optimized settings

Each environment can have different:
- Resource limits (CPU, memory)
- Replica counts
- Debug settings
- Log levels
- Service configurations

## GitHub Actions Integration

The configuration generation is automated via GitHub Actions:

1. **Automatic generation on push**: When YAML files in the `config/` directory are modified
2. **Manual workflow dispatch**: Allows generating configs for specific environments
3. **Pull request creation**: Automatically creates PRs with generated configurations

### Workflow Usage

```yaml
name: Generate Configurations
on:
  push:
    paths:
      - 'config/**/*.yaml'
```

## Testing Configuration Generation

Use the provided test script:

```bash
./scripts/test-config-generation.sh
```

This will:
1. Build the config manager
2. Generate configurations for all environments
3. Validate the generated docker-compose files
4. Display the generated file structure

## Adding New Services

To add a new service:

1. Add the service definition to `master.yaml`:
```yaml
services:
  applications:
    my_new_service:
      type: "python-cpu"
      container_name: "fks_my_new_service"
      service_port: "${MY_SERVICE_PORT:-8002}"
      environment:
        SERVICE_TYPE: "my_new_service"
      resources:
        development:
          cpu: "0.5"
          memory: "512M"
        production:
          cpu: "2"
          memory: "2048M"
```

2. Regenerate configurations:
```bash
./config-manager gen-from-master --environment development
```

## Environment Variables

Environment variables can be defined with defaults:

```yaml
environment_variables:
  API_PORT: "${API_PORT:-8000}"
  DEBUG_MODE: "${DEBUG_MODE:-false}"
```

These will be included in the generated `.env` files.

## Secrets Management

Secrets are defined per environment:

```yaml
secrets:
  production:
    - name: "postgres-password"
      key: "POSTGRES_PASSWORD"
      source: "vault"
      path: "/secret/data/fks/postgres"
  development:
    - name: "postgres-password"
      key: "POSTGRES_PASSWORD"
      source: "env-file"
      default: "dev_password"
```

## Best Practices

1. **Keep master.yaml as the single source of truth**
2. **Use environment variables for values that change between deployments**
3. **Define sensible defaults for all variables**
4. **Use the resource multiplier pattern for environment-specific scaling**
5. **Document any new configuration sections added to master.yaml**
6. **Test configuration generation locally before pushing**

## Troubleshooting

### Common Issues

1. **Build failures**: Ensure Rust toolchain is installed
2. **YAML parsing errors**: Validate YAML syntax using a linter
3. **Missing environment variables**: Check that all referenced variables have defaults
4. **Docker compose validation failures**: Run `docker-compose config` to debug

### Debug Mode

Enable debug output:
```bash
RUST_LOG=debug ./config-manager gen-from-master
```
