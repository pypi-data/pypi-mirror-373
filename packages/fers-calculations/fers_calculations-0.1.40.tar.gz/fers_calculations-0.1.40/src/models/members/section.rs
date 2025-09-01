use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, ToSchema
, Debug)]
pub struct Section {
    pub id: u32,
    pub name: String,
    pub material: u32,
    pub h: Option<f64>,
    pub b: Option<f64>,
    pub i_y: f64,
    pub i_z: f64,
    pub j: f64,  
    pub area: f64,
    pub shape_path: Option<u32>,
}
