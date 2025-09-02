use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::models::loads::distributionshape::DistributionShape;



#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct DistributedLoad {
    pub member: u32,
    pub load_case: u32,
    pub distribution_shape: DistributionShape,
    pub magnitude: f64,
    pub direction: (f64, f64, f64),
    pub start_frac: f64,
    pub end_frac: f64,
    pub end_magnitude: f64, 
}
