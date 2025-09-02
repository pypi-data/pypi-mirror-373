use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub struct MemberRef {
    pub member_id: u32,
    pub memberset_id: Option<u32>,
}

#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub struct GoverningKey {
    pub member_id: Option<u32>,
    pub load_combination_id: Option<u32>,
    pub load_case_id: Option<u32>,
}

#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub struct UnityCheck {
    pub check_id: String,
    pub ok: bool,
    pub value: Option<f64>,
    pub limit: Option<f64>,
    pub message: Option<String>,
    pub governing: Option<GoverningKey>,
    pub details: serde_json::Value,
}

#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub struct UnityCheckOverview {
    pub check_id: String,
    pub aggregated_ok: bool,
    pub aggregated_value: Option<f64>,
    pub governing: Option<GoverningKey>,
    pub children: Vec<UnityCheck>,
}
