use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use crate::models::members::memberset::MemberSet;

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct TranslationImperfection {
    pub memberset: Vec<MemberSet>,
    pub magnitude: f64,
    pub axis: (f64, f64, f64),
}

impl TranslationImperfection {
    pub fn new(memberset: Vec<MemberSet>, magnitude: f64, axis: (f64, f64, f64)) -> Self {
        TranslationImperfection {
            memberset,
            magnitude,
            axis,
        }
    }
}
