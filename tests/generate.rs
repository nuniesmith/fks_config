use std::{path::PathBuf, fs};
use tempfile::tempdir;

#[test]
fn generates_env_from_yaml() {
    let dir = tempdir().unwrap();
    let config_path = dir.path().join("config.yaml");
    let out_path = dir.path().join(".env.out");
    let yaml = "account:\n  size: 100000\n  risk_per_trade: 0.02\nnetwork:\n  master_port: 9000\nruntimes:\n  - python\n";
    fs::write(&config_path, yaml).unwrap();
    fks_config::generate(&config_path, &out_path, Some("python")).unwrap();
    let env_body = fs::read_to_string(&out_path).unwrap();
    assert!(env_body.contains("ACCOUNT_SIZE=100000"));
    assert!(env_body.contains("MAX_LOSS_PER_TRADE=2000"));
    assert!(env_body.contains("TARGET_RUNTIME=python"));
}

#[test]
fn error_on_missing_file() {
    let missing = PathBuf::from("/this/should/not/exist/never.yaml");
    let out = PathBuf::from("/tmp/ignore");
    let err = fks_config::generate(&missing, &out, None).unwrap_err();
    assert!(err.to_string().contains("reading input config"));
}
