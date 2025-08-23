use clap::{Parser, Subcommand};
use std::path::PathBuf;
use fks_config::generate;
use schemars::schema_for;
use std::fs;
use anyhow::Result;
use tracing::{info, error};

#[cfg(feature = "server")]
use axum::{routing::get, Router};
#[cfg(feature = "server")]
use std::net::SocketAddr;

#[derive(Parser, Debug)]
#[command(version, about = "FKS Config Generator")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    Generate {
        #[arg(short, long, default_value = "config/sim.yaml")] input: PathBuf,
        #[arg(short, long, default_value = ".env.generated")] output: PathBuf,
        #[arg(long)] runtime: Option<String>,
    },
    /// Output JSON Schema for the configuration model
    Schema {
        #[arg(short, long, default_value = "config.schema.json")] output: PathBuf,
    },
    /// Validate a configuration file (YAML) without generating outputs
    Validate {
        #[arg(short, long, default_value = "config/sim.yaml")] input: PathBuf,
    },
    /// Run lightweight HTTP server exposing /health (requires --features server)
    Serve {
        /// Port to bind (default 9000)
        #[arg(short, long, default_value_t = 9000)]
        port: u16,
    },
}

fn main() -> Result<()> {
    tracing_subscriber::fmt::init();
    let cli = Cli::parse();
    match cli.command {
        Commands::Generate { input, output, runtime } => {
            generate(&input, &output, runtime.as_deref())?;
            info!(input=%input.display(), output=%output.display(), "generated env");
            println!("Generated {} from {}", output.display(), input.display());
        }
        Commands::Schema { output } => {
            let schema = schema_for!(fks_config::AppConfig);
            let json = serde_json::to_string_pretty(&schema)?;
            fs::write(&output, json)?;
            println!("Wrote schema to {}", output.display());
        }
        Commands::Validate { input } => {
            let tmp_out = PathBuf::from("/dev/null");
            // perform full parse + derived computations but discard env
            fks_config::generate(&input, &tmp_out, None).map_err(|e| {
                error!(input=%input.display(), error=%e, "validation failed");
                e
            })?;
            println!("Validation OK: {}", input.display());
        }
        Commands::Serve { port } => {
            #[cfg(feature = "server")]
            {
                let rt = tokio::runtime::Runtime::new()?;
                rt.block_on(async move {
                    let app = Router::new().route("/health", get(|| async { axum::Json(serde_json::json!({"status":"ok"})) }));
                    let addr = SocketAddr::from(([0,0,0,0], port));
                    info!(addr=%addr, "starting server");
                    println!("Config service listening on http://{}", addr);
                    axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), app).await.unwrap();
                });
            }
            #[cfg(not(feature = "server"))]
            {
                eprintln!("Serve feature not enabled. Rebuild with --features server");
            }
        }
    }
    Ok(())
}
