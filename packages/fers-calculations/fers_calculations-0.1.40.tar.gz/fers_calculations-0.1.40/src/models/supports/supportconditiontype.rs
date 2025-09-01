use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Debug, Serialize, Deserialize, Clone, ToSchema)]
pub enum SupportConditionType {
    Fixed,
    Free,
    Spring,
    PositiveOnly,
    NegativeOnly,
}
