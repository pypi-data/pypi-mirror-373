use dotenv::dotenv;
use env_logger::Builder;
use log::{debug, LevelFilter};
use std::env;

/// Initializes the logger based on the ENABLE_LOGGER environment variable.
pub fn init_logger() {
    dotenv().ok(); // Load .env file

    let enable_logger = env::var("ENABLE_LOGGER")
        .unwrap_or_else(|_| "false".into()) // Default to false if the variable is not set
        .to_lowercase() == "true";

    if enable_logger {
        Builder::new()
            .filter(None, LevelFilter::Debug) 
            .init();
        debug!("Logger is enabled!");
    } else {
        // Configure a minimal logger to suppress debug logs
        Builder::new()
            .filter(None, LevelFilter::Off) // Suppress all logs globally
            .filter(Some("main"), LevelFilter::Off) // Disable logs for main module
            .filter(Some("analysis"), LevelFilter::Off) // Disable logs for main module
            .filter(Some("fers"), LevelFilter::Off) // Disable logs for main module
            .filter(Some("fers_calculations"), LevelFilter::Off) // Disable logs for other module
            .init();
    }
}
