use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::models::supports::supportconditiontype::SupportConditionType;

#[derive(Debug, Serialize, Deserialize, ToSchema, Clone)]
pub struct SupportCondition {
    pub condition_type: SupportConditionType,
    pub stiffness: Option<f64>,
}
