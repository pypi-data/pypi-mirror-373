// src/models/members/memberset.rs
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use crate::models::members::member::Member;


#[derive(Serialize, Deserialize, ToSchema
, Debug)]
pub struct MemberSet {
    pub id: u32,
    pub l_y: Option<f64>,
    pub l_z: Option<f64>,
    pub classification: Option<String>,
    pub members: Vec<Member>,
}





