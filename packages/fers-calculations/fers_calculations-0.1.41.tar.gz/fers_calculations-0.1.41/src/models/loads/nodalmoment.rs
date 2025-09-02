// src/models/nodalmoment.rs

use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct NodalMoment {
    pub id: u32,
    pub node: u32,
    pub load_case: u32,
    pub magnitude: f64,
    pub direction: (f64, f64, f64),
    pub load_type: String,
}
