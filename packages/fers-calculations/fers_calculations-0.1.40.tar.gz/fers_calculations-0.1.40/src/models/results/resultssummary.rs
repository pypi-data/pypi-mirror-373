use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, ToSchema, Clone
, Debug)]
pub struct ResultsSummary {
    pub total_displacements: usize,
    pub total_reaction_forces: usize,
    pub total_member_forces: usize,
} 