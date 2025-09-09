use crate::model::AppConfig;
use anyhow::{Context, Result};
use std::{fs, path::Path};
use serde_path_to_error::deserialize;

pub fn generate(input: &Path, output: &Path, runtime: Option<&str>) -> Result<()> {
    let raw = fs::read_to_string(input)
        .with_context(|| format!("reading input config: {}", input.display()))?;
    // Enhanced error location reporting
    let de = serde_yaml::Deserializer::from_str(&raw);
    // Use first document only (typical case)
    let mut docs = de.into_iter();
    let first = docs.next().ok_or_else(|| anyhow::anyhow!("empty yaml"))?;
    let cfg: AppConfig = deserialize(first).map_err(|e| {
        anyhow::anyhow!("parsing yaml at {}: {}", e.path().to_string(), e)
    })?;

    let max_loss = cfg.account.size * cfg.account.risk_per_trade;
    let mut env_lines = vec![
        format!("ACCOUNT_SIZE={}", cfg.account.size),
        format!("RISK_PER_TRADE={}", cfg.account.risk_per_trade),
        format!("MAX_LOSS_PER_TRADE={}", max_loss),
        format!("MASTER_PORT={}", cfg.network.master_port),
        format!(
            "SIM_LATENCY_MS={}",
            cfg.network.sim_latency_ms.map(|v| v.to_string()).unwrap_or_default()
        ),
    ];
    if let Some(vix) = cfg.vix_gate {
        env_lines.push(format!("VIX_GATE={}", vix));
    }
    if let Some(rt) = runtime {
        env_lines.push(format!("TARGET_RUNTIME={}", rt));
    }

    fs::write(output, env_lines.join("\n") + "\n")
        .with_context(|| format!("writing env output: {}", output.display()))?;
    Ok(())
}
