// src/lib.rs

pub mod models;
pub mod functions;
pub mod analysis;

pub use crate::analysis::calculate_from_json_internal as calculate_from_json;
pub use crate::analysis::calculate_from_file_internal as calculate_from_file;
pub use crate::analysis::load_fers_from_file;

#[cfg(feature = "python")]
mod python_bindings;

#[cfg(feature = "wasm")]
mod wasm_bindings;
