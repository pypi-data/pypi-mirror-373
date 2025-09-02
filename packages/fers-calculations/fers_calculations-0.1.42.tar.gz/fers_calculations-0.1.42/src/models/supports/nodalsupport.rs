use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use utoipa::ToSchema;

use crate::models::supports::supportcondition::SupportCondition;

#[derive(Serialize, Deserialize, ToSchema, Clone, Debug)]
pub struct NodalSupport {
    pub id: u32,
    pub classification: Option<String>,
    pub displacement_conditions: BTreeMap<String, SupportCondition>,
    pub rotation_conditions: BTreeMap<String, SupportCondition>,
}
