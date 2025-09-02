use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, ToSchema, Debug)]
pub struct ShapeCommand {
    pub command: String,
    pub y: Option<f64>,
    pub z: Option<f64>,
    pub r: Option<f64>,
    pub control_y1: Option<f64>,
    pub control_z1: Option<f64>,
    pub control_y2: Option<f64>,
    pub control_z2: Option<f64>,
}
