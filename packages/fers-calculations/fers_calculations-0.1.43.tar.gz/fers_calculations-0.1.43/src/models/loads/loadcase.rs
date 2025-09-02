// src/models/loads/loadcase.rs
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use crate::models::loads::distributedload::DistributedLoad;
use crate::models::imperfections::rotationimperfection::RotationImperfection;
use crate::models::imperfections::translationimperfection::TranslationImperfection;

use super::nodalload::NodalLoad;
use super::nodalmoment::NodalMoment;

#[derive(Serialize, Deserialize, ToSchema, Debug)]
pub struct LoadCase {
    pub id: u32,
    pub name: String,
    pub nodal_loads: Vec<NodalLoad>,
    pub nodal_moments: Vec<NodalMoment>,
    pub distributed_loads: Vec<DistributedLoad>,
    pub rotation_imperfections: Vec<RotationImperfection>,
    pub translation_imperfections: Vec<TranslationImperfection>,
}
