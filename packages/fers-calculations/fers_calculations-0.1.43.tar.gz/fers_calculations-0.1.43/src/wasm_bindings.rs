// only compiled when you do `--features wasm`
use wasm_bindgen::prelude::*;
use serde_json;
use crate::analysis::{ calculate_from_json_internal, load_fers_from_file as load_fers_from_file_internal };

#[wasm_bindgen]
pub fn calculate_from_json(json_data: &str) -> String {
    calculate_from_json_internal(json_data)
        .unwrap_or_else(|e| e)
}

#[wasm_bindgen]
pub fn load_fers_from_file(path: &str) -> String {
    load_fers_from_file_internal(path)
        .map(|fers| serde_json::to_string(&fers).unwrap_or_else(|e| e.to_string()))
        .unwrap_or_else(|e| e.to_string())
}
