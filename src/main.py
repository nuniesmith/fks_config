"""
FKS Config Microservice
Centralized configuration management with secure API key storage
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import hashlib
from cryptography.fernet import Fernet
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FKS Config Service",
    description="Centralized configuration and API key management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Configuration
CONFIG_DIR = Path(os.getenv("CONFIG_DIR", "/app/config"))
SERVICES_DIR = CONFIG_DIR / "services"
SECRETS_FILE = CONFIG_DIR / ".secrets" / "api_keys.encrypted"
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
SERVICES_DIR.mkdir(parents=True, exist_ok=True)
SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Encryption setup
def get_encryption_key() -> bytes:
    """Get or generate encryption key."""
    if ENCRYPTION_KEY:
        # Use provided key (should be base64 encoded)
        try:
            return base64.b64decode(ENCRYPTION_KEY)
        except:
            # If not base64, use it directly (32 bytes required)
            key = ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
            return base64.urlsafe_b64encode(key)
    else:
        # Generate a key (for development only - should be set in production)
        logger.warning("ENCRYPTION_KEY not set - generating temporary key (not secure for production!)")
        key_file = CONFIG_DIR / ".secrets" / ".encryption_key"
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            os.chmod(key_file, 0o600)  # Secure permissions
            return key

fernet = Fernet(base64.urlsafe_b64encode(get_encryption_key()[:32].ljust(32, b'0')))

# Models
class ConfigValue(BaseModel):
    key: str
    value: Any
    service: Optional[str] = None

class SecretValue(BaseModel):
    service: str
    key_name: str
    value: str
    description: Optional[str] = None

class ConfigUpdate(BaseModel):
    path: str  # Dot-separated path like "service.port" or "service_specific.trading.leverage"
    value: Any

class SecretUpdate(BaseModel):
    service: str
    key_name: str
    value: str
    description: Optional[str] = None

# Helper functions
def load_config_file(service_name: str) -> Dict[str, Any]:
    """Load YAML config file for a service."""
    config_file = SERVICES_DIR / f"{service_name}.yaml"
    if not config_file.exists():
        raise HTTPException(status_code=404, detail=f"Config file not found for service: {service_name}")
    
    with open(config_file, 'r') as f:
        return yaml.safe_load(f) or {}

def save_config_file(service_name: str, config: Dict[str, Any]):
    """Save YAML config file for a service."""
    config_file = SERVICES_DIR / f"{service_name}.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    logger.info(f"Saved config for {service_name}")

def get_nested_value(data: Dict, path: str) -> Any:
    """Get nested value using dot notation."""
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current

def set_nested_value(data: Dict, path: str, value: Any):
    """Set nested value using dot notation."""
    keys = path.split('.')
    current = data
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value

def load_secrets() -> Dict[str, Dict[str, str]]:
    """Load encrypted secrets."""
    if not SECRETS_FILE.exists():
        return {}
    
    try:
        encrypted_data = SECRETS_FILE.read_bytes()
        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except Exception as e:
        logger.error(f"Error loading secrets: {e}")
        return {}

def save_secrets(secrets: Dict[str, Dict[str, str]]):
    """Save encrypted secrets."""
    try:
        data = json.dumps(secrets).encode()
        encrypted_data = fernet.encrypt(data)
        SECRETS_FILE.write_bytes(encrypted_data)
        os.chmod(SECRETS_FILE, 0o600)  # Secure permissions
        logger.info("Secrets saved")
    except Exception as e:
        logger.error(f"Error saving secrets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save secrets: {e}")

# API Endpoints
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "fks_config"}

@app.get("/api/v1/services")
def list_services():
    """List all available services."""
    services = []
    for config_file in SERVICES_DIR.glob("*.yaml"):
        service_name = config_file.stem
        services.append({
            "name": service_name,
            "config_file": str(config_file.relative_to(CONFIG_DIR))
        })
    return {"services": services}

@app.get("/api/v1/services/{service_name}/config")
def get_service_config(service_name: str):
    """Get full configuration for a service."""
    try:
        config = load_config_file(service_name)
        return {"service": service_name, "config": config}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading config for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/services/{service_name}/config/{path:path}")
def get_config_value(service_name: str, path: str):
    """Get a specific config value using dot notation."""
    try:
        config = load_config_file(service_name)
        value = get_nested_value(config, path)
        if value is None:
            raise HTTPException(status_code=404, detail=f"Config path not found: {path}")
        return {"service": service_name, "path": path, "value": value}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting config value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/services/{service_name}/config")
def update_service_config(service_name: str, update: ConfigUpdate):
    """Update a configuration value."""
    try:
        config = load_config_file(service_name)
        set_nested_value(config, update.path, update.value)
        save_config_file(service_name, config)
        return {"success": True, "message": f"Updated {update.path}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/secrets")
def list_secrets():
    """List all secrets (masked)."""
    secrets = load_secrets()
    masked = {}
    for service, keys in secrets.items():
        masked[service] = {}
        for key_name, value in keys.items():
            # Mask the value
            if len(value) > 8:
                masked[service][key_name] = f"{value[:4]}***{value[-4:]}"
            else:
                masked[service][key_name] = "***"
    return {"secrets": masked}

@app.get("/api/v1/secrets/{service}")
def get_service_secrets(service: str):
    """Get secrets for a service (masked)."""
    secrets = load_secrets()
    if service not in secrets:
        return {"service": service, "secrets": {}}
    
    masked = {}
    for key_name, value in secrets[service].items():
        if len(value) > 8:
            masked[key_name] = f"{value[:4]}***{value[-4:]}"
        else:
            masked[key_name] = "***"
    
    return {"service": service, "secrets": masked}

@app.post("/api/v1/secrets/{service}/{key_name}")
def set_secret(service: str, key_name: str, secret: SecretUpdate):
    """Set a secret value."""
    try:
        secrets = load_secrets()
        if service not in secrets:
            secrets[service] = {}
        secrets[service][key_name] = secret.value
        save_secrets(secrets)
        return {"success": True, "message": f"Secret {key_name} saved for {service}"}
    except Exception as e:
        logger.error(f"Error setting secret: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/secrets/{service}/{key_name}")
def delete_secret(service: str, key_name: str):
    """Delete a secret."""
    try:
        secrets = load_secrets()
        if service in secrets and key_name in secrets[service]:
            del secrets[service][key_name]
            if not secrets[service]:  # Remove empty service dict
                del secrets[service]
            save_secrets(secrets)
            return {"success": True, "message": f"Secret {key_name} deleted for {service}"}
        else:
            raise HTTPException(status_code=404, detail="Secret not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting secret: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/secrets/{service}/{key_name}/value")
def get_secret_value(service: str, key_name: str):
    """Get actual secret value (for services, not web UI)."""
    # In production, add authentication here
    secrets = load_secrets()
    if service in secrets and key_name in secrets[service]:
        return {"service": service, "key_name": key_name, "value": secrets[service][key_name]}
    else:
        raise HTTPException(status_code=404, detail="Secret not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", "8015"))
    uvicorn.run(app, host="0.0.0.0", port=port)

