use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::models::results::forces::{NodeForces};


#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub struct MemberResult {
    pub start_node_forces: NodeForces,
    pub end_node_forces: NodeForces,
    pub maximums: NodeForces,
    pub minimums: NodeForces,
}