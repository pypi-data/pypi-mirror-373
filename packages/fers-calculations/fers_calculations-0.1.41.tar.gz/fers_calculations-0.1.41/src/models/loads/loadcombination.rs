use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use std::collections::HashMap;


#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub enum LimitState {
    SLS, // Serviceability Limit State
    ULS, // Ultimate Limit State
    FLS, // Fatigue Limit State
    ALS, // Accidental Limit State
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct LoadCombination {
    pub load_combination_id: u32,
    pub name: String,
    pub load_cases_factors: HashMap<u32, f64>,
    pub situation: Option<String>,
    pub check: String,
    pub limit_state: LimitState,  

}
