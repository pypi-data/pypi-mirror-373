use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct AnalysisOption {
    pub id: u32,
    pub solve_loadcases: bool,
    pub solver: String,
    pub tolerance: f64,
    pub max_iterations: Option<u32>,
    pub dimensionality: String,
    pub order: String,
}
