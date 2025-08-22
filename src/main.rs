use clap::{Parser, Subcommand};
use std::path::PathBuf;
use fks_config::generate;
use schemars::schema_for;
use std::fs;

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
}

fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();
    let cli = Cli::parse();
    match cli.command {
        Commands::Generate { input, output, runtime } => {
            generate(&input, &output, runtime.as_deref())?;
            println!("Generated {} from {}", output.display(), input.display());
        }
        Commands::Schema { output } => {
            let schema = schema_for!(fks_config::AppConfig);
            let json = serde_json::to_string_pretty(&schema)?;
            fs::write(&output, json)?;
            println!("Wrote schema to {}", output.display());
        }
    }
    Ok(())
}
