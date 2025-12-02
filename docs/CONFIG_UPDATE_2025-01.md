# Configuration Update - 2025-01-XX

## Summary

Added missing configuration files for new services and updated existing configs to reflect new features.

---

## ✅ New Configuration Files Created

### 1. `fks_futures.yaml` (NEW)
- **Service**: fks_futures
- **Port**: 8015
- **Purpose**: Futures trading service for CME Group futures contracts
- **Dependencies**: fks_data, fks_app, fks_execution, fks_ninja, fks_auth
- **Key Features**:
  - Futures signal generation
  - Futures market analysis (market, volatility, correlation)
  - NinjaTrader8 integration
  - Hardcoded CME Group futures assets (equities, energy, metals, agriculture, FX, crypto)
- **Redis DB**: 15 (unique)

### 2. `fks_ninja.yaml` (NEW)
- **Service**: fks_ninja
- **Port**: 8006
- **Purpose**: Plugin service for NinjaTrader8 integration
- **Dependencies**: fks_execution, fks_data
- **Key Features**:
  - NinjaTrader8 TCP socket connection (100.80.141.117:8080)
  - Signal reception and management
  - Order execution via NT8 API
  - Execution status reporting
  - Symbol mapping and normalization
- **Redis DB**: 6 (unique)
- **Note**: Shorter timeouts and higher rate limits for real-time trading

---

## 🔄 Updated Configuration Files

### 1. `fks_crypto.yaml` (UPDATED)
**Added Features**:
- `crypto_analysis: true` - Enable crypto market analysis
- `market_analysis: true` - Market trend analysis
- `volatility_analysis: true` - Volatility analysis
- `correlation_analysis: true` - Crypto correlation analysis
- `regime_detection: true` - Market regime detection
- `sentiment_analysis: true` - Crypto sentiment analysis

**New Configuration Section**:
```yaml
analysis:
  market_analyzer:
    enabled: true
    update_interval: 300  # 5 minutes
    lookback_periods: 100
  volatility_analyzer:
    enabled: true
    lookback_periods: 20
    window_size: 24  # hours
  correlation_analyzer:
    enabled: true
    correlation_window: 30  # days
    min_correlation: 0.3
  regime_detector:
    enabled: true
    update_interval: 600  # 10 minutes
    regimes:
      - bull
      - bear
      - sideways
      - volatile
  sentiment_analyzer:
    enabled: true
    data_sources:
      - social_media
      - news
      - on_chain
    update_interval: 900  # 15 minutes
```

---

## 📋 Configuration File Inventory

All services in `service_registry.json` now have corresponding config files:

| Service | Config File | Port | Status |
|---------|-------------|------|--------|
| fks_web | ✅ fks_web.yaml | 3001/8000 | Existing |
| fks_api | ✅ fks_api.yaml | 8001 | Existing |
| fks_app | ✅ fks_app.yaml | 8002 | Existing |
| fks_data | ✅ fks_data.yaml | 8003 | Existing |
| fks_execution | ✅ fks_execution.yaml | 8004 | Existing |
| fks_meta | ✅ fks_meta.yaml | 8005 | Existing |
| fks_ninja | ✅ fks_ninja.yaml | 8006 | **NEW** |
| fks_ai | ✅ fks_ai.yaml | 8007 | Existing |
| fks_analyze | ✅ fks_analyze.yaml | 8008 | Existing |
| fks_auth | ✅ fks_auth.yaml | 8009 | Existing |
| fks_main | ✅ fks_main.yaml | 8010 | Existing |
| fks_training | ✅ fks_training.yaml | 8011 | Existing |
| fks_portfolio | ✅ fks_portfolio.yaml | 8012 | Existing |
| fks_monitor | ✅ fks_monitor.yaml | 8013 | Existing |
| fks_crypto | ✅ fks_crypto.yaml | 8014 | **UPDATED** |
| fks_futures | ✅ fks_futures.yaml | 8015 | **NEW** |

**Total**: 16 services, all have config files ✅

---

## 🔍 Key Configuration Details

### Redis Database Allocation
Each service uses a unique Redis database number:
- fks_app: DB 1
- fks_ninja: DB 6
- fks_futures: DB 15
- (Other services have their own DB numbers)

### Environment Variables
All sensitive values use environment variables:
- Database passwords: `POSTGRES_PASSWORD`
- API keys: Service-specific (e.g., `BINANCE_API_KEY`)
- NT8 connection: `NT8_HOST`, `NT8_PORT`, `NT8_ACCOUNT_NUMBER`
- Discord webhooks: `DISCORD_WEBHOOK_URL`

### Service-Specific Features

**fks_futures**:
- Hardcoded CME Group futures assets by category
- NinjaTrader8 integration settings
- Futures analysis modules configuration

**fks_ninja**:
- TCP socket connection to NT8 Windows desktop
- Signal polling configuration (5-second intervals)
- Symbol mapping and normalization
- Execution reporting settings

**fks_crypto**:
- Crypto analysis modules (market, volatility, correlation, regime, sentiment)
- Update intervals for each analyzer
- Data source configuration for sentiment analysis

---

## 📝 Documentation Updates

- ✅ Updated `SERVICES_CONFIG.md` to include new services
- ✅ Created this update document

---

## ✅ Verification Checklist

- [x] All services in `service_registry.json` have config files
- [x] All config files follow the template structure
- [x] Dependencies match `service_registry.json`
- [x] Ports match `service_registry.json`
- [x] Redis DB numbers are unique
- [x] Environment variables used for secrets
- [x] Documentation updated

---

**Date**: 2025-01-XX  
**Status**: Complete ✅
