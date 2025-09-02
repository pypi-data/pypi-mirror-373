use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::models::members::memberset::MemberSet;

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct RotationImperfection {
    pub memberset: Vec<MemberSet>,
    pub magnitude: f64,
    pub axis: (f64, f64, f64),
    pub axis_only: bool,
    pub point: (f64, f64, f64),
}
