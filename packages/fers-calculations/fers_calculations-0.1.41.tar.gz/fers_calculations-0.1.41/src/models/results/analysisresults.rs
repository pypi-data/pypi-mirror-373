use serde::{Deserialize, Serialize};

use super::results::Results;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct LoadCaseResult {
    pub name: String,
    pub result: Results,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct LoadCombinationResult {
    pub name: String,
    pub result: Results,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct AnalysisResults {
    pub load_cases: Vec<LoadCaseResult>,
    pub load_combinations: Vec<LoadCombinationResult>,
}