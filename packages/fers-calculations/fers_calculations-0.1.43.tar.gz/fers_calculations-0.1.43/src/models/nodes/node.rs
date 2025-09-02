use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[allow(non_snake_case)]
#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct Node {
    pub id: u32,
    pub X: f64,
    pub Y: f64,
    pub Z: f64,
    pub nodal_support: Option<u32>,
}
impl Node {
    pub fn distance_to(&self, other: &Node) -> f64 {
        let dx = self.X - other.X;
        let dy = self.Y - other.Y;
        let dz = self.Z - other.Z;
        (dx * dx + dy * dy + dz * dz).sqrt()
    }
}