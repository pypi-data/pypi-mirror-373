use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap};
use utoipa::ToSchema;
use crate::models::results::memberresult::MemberResult;
use crate::models::results::reaction::ReactionNodeResult;
use crate::models::results::resultssummary::ResultsSummary;
use crate::models::unitychecks::unitycheck::UnityCheck;

use super::displacement::NodeDisplacement;

#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub enum ResultType {
    Loadcase(u32),
    Loadcombination(u32),
}




#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub struct Results {
    pub name: String,
    pub result_type: ResultType,
    pub displacement_nodes: BTreeMap<u32, NodeDisplacement>,
    pub reaction_nodes: BTreeMap<u32, ReactionNodeResult>,
    pub member_results: BTreeMap<u32, MemberResult>,
    pub summary: ResultsSummary,
    pub unity_checks: Option<BTreeMap<String, UnityCheck>>,
}


