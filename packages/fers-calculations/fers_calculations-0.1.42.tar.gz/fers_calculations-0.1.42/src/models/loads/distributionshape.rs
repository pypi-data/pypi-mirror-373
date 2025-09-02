use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Debug, Serialize, Deserialize, ToSchema, Clone, Copy)]
pub enum DistributionShape {
    Uniform,
    Triangular,
    InverseTriangular,
}

