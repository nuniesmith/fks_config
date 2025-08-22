use serde::{Deserialize, Serialize};
use schemars::JsonSchema;

#[derive(Debug, Deserialize, Serialize, Clone, JsonSchema)]
pub struct AccountConfig {
    pub size: f64,
    pub risk_per_trade: f64,
}

#[derive(Debug, Deserialize, Serialize, Clone, JsonSchema)]
pub struct NetworkConfig {
    pub master_port: u16,
    #[serde(default)]
    pub sim_latency_ms: Option<u64>,
}

#[derive(Debug, Deserialize, Serialize, Clone, JsonSchema)]
#[serde(rename_all = "lowercase")]
pub enum RuntimeKind {
    Python,
    Rust,
    Node,
}

#[derive(Debug, Deserialize, Serialize, Clone, JsonSchema)]
pub struct AppConfig {
    pub account: AccountConfig,
    pub network: NetworkConfig,
    pub runtimes: Vec<RuntimeKind>,
    #[serde(default)]
    pub vix_gate: Option<f64>,
}
