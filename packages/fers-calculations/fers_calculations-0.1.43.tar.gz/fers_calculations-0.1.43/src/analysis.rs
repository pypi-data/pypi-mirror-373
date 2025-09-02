// src/analysis.rs

use crate::models::fers::fers::FERS;
use serde_json;
use std::fs;
use std::path::Path;   
use std::io;     
use nalgebra::DMatrix;

/// Perform analysis on the given JSON input string.
///
/// This function handles:
/// 1) Parsing the JSON into a FERS struct.
/// 2) Identifying the first load case.
/// 3) Performing structural analysis (solve_for_load_case).
/// 4) Optionally printing results.
/// 5) Saving results to an output file (analysis_results.json).
///
/// Returns an `Ok(String)` with a success message, or an `Err(String)` on failure.
pub fn calculate_from_json_internal(json_data: &str) -> Result<String, String> {
    // 1) Parse
    let mut fers: FERS = serde_json::from_str(json_data)
        .map_err(|e| format!("Bad JSON input: {}", e))?;

    // 2) Options
    let opts = &fers.settings.analysis_option;
    let is_second = match opts.order.as_str() {
        "Linear"    => false,
        "Nonlinear" => true,
        other => return Err(format!("Unknown order `{}`", other)),
    };
    let tol    = opts.tolerance;
    let max_it = opts.max_iterations.unwrap_or(20) as usize;

    let mut all_results = Vec::new();

    // Collect IDs before any mutable operations
    let load_case_ids: Vec<_> = fers.load_cases.iter()
        .map(|lc| lc.id)
        .collect();
    
    let combo_ids: Vec<_> = fers.load_combinations.iter()
        .map(|combo| combo.load_combination_id)
        .collect();

    // 3) Solve load‐cases if requested
    if opts.solve_loadcases {
        for lc_id in load_case_ids {
            let res = if is_second {
                fers.solve_for_load_case_second_order(lc_id, max_it, tol)
                    .map_err(|e| format!("LC {} 2nd‑order error: {}", lc_id, e))?
            } else {
                fers.solve_for_load_case(lc_id)
                    .map_err(|e| format!("LC {} linear error: {}", lc_id, e))?
            };
            all_results.push(res);
        }
    }

    // 4) Always solve *all* load‐combinations
    
    for combo_id in combo_ids {
        let res = if is_second {
            fers.solve_for_load_combination_second_order(
                combo_id,
                max_it,
                tol,
            )
            .map_err(|e| format!(
                "Combo {} 2nd‑order error: {}",
                combo_id, e
            ))?
        } else {
            fers.solve_for_load_combination(combo_id)
                .map_err(|e| format!(
                    "Combo {} linear error: {}",
                    combo_id, e
                ))?
        };
        all_results.push(res);
    }

    // 5) Serialize the Vec<Results> to JSON
    if let Some(bundle) = fers.results.take() {
        serde_json::to_string(&bundle)
            .map_err(|e| format!("Failed to serialize ResultsBundle: {}", e))
    } else {
        Err("No results were generated".to_string())
    }
}


/// A small helper for printing displacement or reaction vectors more nicely.
#[allow(dead_code)]
fn print_readable_vector(vector: &DMatrix<f64>, label: &str) {
    let dof_labels = ["UX", "UY", "UZ", "RX", "RY", "RZ"];
    println!("{}:", label);

    // We assume 6 DOFs per node
    let num_nodes = vector.nrows() / 6;
    for node_index in 0..num_nodes {
        println!("  Node {}:", node_index + 1);
        for dof_index in 0..6 {
            let value = vector[(node_index * 6 + dof_index, 0)];
            println!("    {:<3}: {:10.4}", dof_labels[dof_index], value);
        }
    }
}

/// Convenience function for reading a file and passing its contents to `calculate_from_json_internal`.
pub fn calculate_from_file_internal(path: &str) -> Result<String, String> {
    let file_content = match fs::read_to_string(path) {
        Ok(content) => content,
        Err(e) => return Err(format!("Failed to read JSON file: {}", e)),
    };

    calculate_from_json_internal(&file_content)
}

pub fn load_fers_from_file<P: AsRef<Path>>(path: P) -> Result<FERS, io::Error> {
    let s = fs::read_to_string(path)?;
    let fers: FERS = serde_json::from_str(&s)
        .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
    Ok(fers)
}