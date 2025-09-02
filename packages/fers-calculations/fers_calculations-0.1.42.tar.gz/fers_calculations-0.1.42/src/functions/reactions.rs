use std::collections::{BTreeMap, HashMap};

use nalgebra::DMatrix;

use crate::models::fers::fers::FERS;
use crate::models::results::forces::NodeForces;
use crate::models::results::reaction::{NodeLocation, ReactionNodeResult};

pub fn build_support_to_node_identifier_map(fers: &FERS) -> HashMap<u32, u32> {
    let mut support_to_node_identifier: HashMap<u32, u32> = HashMap::new();
    for member_set in &fers.member_sets {
        for member in &member_set.members {
            if let Some(support_identifier) = member.start_node.nodal_support {
                support_to_node_identifier.insert(support_identifier, member.start_node.id);
            }
            if let Some(support_identifier) = member.end_node.nodal_support {
                support_to_node_identifier.insert(support_identifier, member.end_node.id);
            }
        }
    }
    support_to_node_identifier
}

/// Get the coordinates for a node identifier by looking it up in the members.
/// If the node is not found, returns (0,0,0). You can change this to return Result if you prefer strictness.
pub fn get_node_location_for_node_identifier(fers: &FERS, node_identifier: u32) -> NodeLocation {
    for member_set in &fers.member_sets {
        for member in &member_set.members {
            if member.start_node.id == node_identifier {
                return NodeLocation { X: member.start_node.X, Y: member.start_node.Y, Z: member.start_node.Z };
            }
            if member.end_node.id == node_identifier {
                return NodeLocation { X: member.end_node.X, Y: member.end_node.Y, Z: member.end_node.Z };
            }
        }
    }
    NodeLocation { X: 0.0, Y: 0.0, Z: 0.0 }
}


fn node_location(fers: &FERS, node_id: u32) -> NodeLocation {
    for ms in &fers.member_sets {
        for m in &ms.members {
            if m.start_node.id == node_id {
                return NodeLocation { X: m.start_node.X, Y: m.start_node.Y, Z: m.start_node.Z };
            }
            if m.end_node.id == node_id {
                return NodeLocation { X: m.end_node.X, Y: m.end_node.Y, Z: m.end_node.Z };
            }
        }
    }
    NodeLocation { X: 0.0, Y: 0.0, Z: 0.0 }
}

/// Build reactions keyed by node_id. This handles multiple nodes sharing the same support_id.
pub fn extract_reaction_nodes(
    fers: &FERS,
    global_reaction_vector: &DMatrix<f64>,
) -> BTreeMap<u32, ReactionNodeResult> {

    // Collect unique nodes (since nodes are embedded in members)
    let mut out: BTreeMap<u32, ReactionNodeResult> = BTreeMap::new();

    for ms in &fers.member_sets {
        for m in &ms.members {
            for n in [&m.start_node, &m.end_node] {
                if let Some(support_id) = n.nodal_support {
                    // Use node_id as the key
                    let node_id = n.id;
                    let dof0 = (node_id as usize - 1) * 6;

                    let nodal_forces = NodeForces {
                        fx: global_reaction_vector[(dof0 + 0, 0)],
                        fy: global_reaction_vector[(dof0 + 1, 0)],
                        fz: global_reaction_vector[(dof0 + 2, 0)],
                        mx: global_reaction_vector[(dof0 + 3, 0)],
                        my: global_reaction_vector[(dof0 + 4, 0)],
                        mz: global_reaction_vector[(dof0 + 5, 0)],
                    };


                    out.insert(
                        node_id,
                        ReactionNodeResult {
                            nodal_forces,
                            location: node_location(fers, node_id),
                            support_id,
                        },
                    );
                }
            }
        }
    }

    out
}