use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, ToSchema
, Debug)]
#[serde(rename_all = "PascalCase")] 
pub enum MemberType {
    Normal,
    Truss,
    Tension,
    Compression,
    Rigid,
}
