/// Returns the six degrees of freedom indices for the given node.
/// The first three are for translational DOFs (X, Y, Z) and the next three for rotational DOFs (RX, RY, RZ).
pub fn get_dof_indices(node_id: usize) -> (usize, usize, usize, usize, usize, usize) {
    let base_index = (node_id - 1) * 6;
    (
        base_index,         // X translation
        base_index + 1,     // Y translation
        base_index + 2,     // Z translation
        base_index + 3,     // X rotation
        base_index + 4,     // Y rotation
        base_index + 5      // Z rotation
    )
}

