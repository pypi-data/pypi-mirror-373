use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use utoipa::ToSchema;

use crate::models::unitychecks::unitycheck::UnityCheckOverview;
use crate::models::results::results::Results;

#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub struct ResultsBundle {
    pub loadcases: BTreeMap<String, Results>,
    pub loadcombinations: BTreeMap<String, Results>,
    pub unity_checks_overview: Option<BTreeMap<String, UnityCheckOverview>>,
}
