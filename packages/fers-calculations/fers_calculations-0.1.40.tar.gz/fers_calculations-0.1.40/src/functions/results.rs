use crate::models::fers::fers::FERS;
use crate::models::members::enums::MemberType;
use crate::models::results::displacement::NodeDisplacement;
use crate::models::results::forces::NodeForces;
use crate::models::results::memberresult::MemberResult;
use crate::models::results::results::ResultType;
use nalgebra::{DMatrix, DVector};
use std::collections::{BTreeMap, HashSet};

pub fn compute_component_extrema(
    start_forces: &NodeForces,
    end_forces: &NodeForces,
) -> (NodeForces, NodeForces) {
    let maximums = NodeForces {
        fx: start_forces.fx.max(end_forces.fx),
        fy: start_forces.fy.max(end_forces.fy),
        fz: start_forces.fz.max(end_forces.fz),
        mx: start_forces.mx.max(end_forces.mx),
        my: start_forces.my.max(end_forces.my),
        mz: start_forces.mz.max(end_forces.mz),
    };
    let minimums = NodeForces {
        fx: start_forces.fx.min(end_forces.fx),
        fy: start_forces.fy.min(end_forces.fy),
        fz: start_forces.fz.min(end_forces.fz),
        mx: start_forces.mx.min(end_forces.mx),
        my: start_forces.my.min(end_forces.my),
        mz: start_forces.mz.min(end_forces.mz),
    };
    (maximums, minimums)
}

pub fn extract_displacements(
    fers: &FERS,
    global_displacement_vector: &DMatrix<f64>,
) -> BTreeMap<u32, NodeDisplacement> {
    let mut unique_node_identifiers: HashSet<u32> = HashSet::new();

    for member_set in &fers.member_sets {
        for member in &member_set.members {
            unique_node_identifiers.insert(member.start_node.id);
            unique_node_identifiers.insert(member.end_node.id);
        }
    }

    unique_node_identifiers
        .into_iter()
        .map(|node_identifier| {
            let degree_of_freedom_start = (node_identifier as usize - 1) * 6;
            (
                node_identifier,
                NodeDisplacement {
                    dx: global_displacement_vector[(degree_of_freedom_start + 0, 0)],
                    dy: global_displacement_vector[(degree_of_freedom_start + 1, 0)],
                    dz: global_displacement_vector[(degree_of_freedom_start + 2, 0)],
                    rx: global_displacement_vector[(degree_of_freedom_start + 3, 0)],
                    ry: global_displacement_vector[(degree_of_freedom_start + 4, 0)],
                    rz: global_displacement_vector[(degree_of_freedom_start + 5, 0)],
                },
            )
        })
        .collect()
}

// CHANGED: add `result_type` arg
pub fn compute_member_results_from_displacement(
    fers: &FERS,
    result_type: &ResultType, // <--
    global_displacement_vector: &DMatrix<f64>,
) -> BTreeMap<u32, MemberResult> {
    let (material_map, section_map, _hinge_map, _support_map) = fers.build_lookup_maps();
    let mut results_by_member_identifier: BTreeMap<u32, MemberResult> = BTreeMap::new();

    for member_set in &fers.member_sets {
        for member in &member_set.members {
            if matches!(member.member_type, MemberType::Rigid) {
                continue;
            }
            let start_node_dof_index = (member.start_node.id as usize - 1) * 6;
            let end_node_dof_index = (member.end_node.id as usize - 1) * 6;

            let mut member_displacement_vector = DVector::<f64>::zeros(12);
            for degree_of_freedom_offset in 0..6 {
                member_displacement_vector[degree_of_freedom_offset] = global_displacement_vector
                    [(start_node_dof_index + degree_of_freedom_offset, 0)];
                member_displacement_vector[degree_of_freedom_offset + 6] =
                    global_displacement_vector[(end_node_dof_index + degree_of_freedom_offset, 0)];
            }

            let local_stiffness_matrix = member
                .calculate_stiffness_matrix_3d(&material_map, &section_map)
                .expect("Failed to compute local stiffness matrix");
            let transformation_matrix = member.calculate_transformation_matrix_3d();

            let local_displacement_vector = &transformation_matrix * &member_displacement_vector;

            let mut local_equivalent_end_load_vector = DVector::<f64>::zeros(12);

            match result_type {
                ResultType::Loadcase(load_case_id) => {
                    if let Some(load_case) =
                        fers.load_cases.iter().find(|lc| lc.id == *load_case_id)
                    {
                        for distributed_load in &load_case.distributed_loads {
                            if distributed_load.member != member.id
                                || distributed_load.load_case != *load_case_id
                            {
                                continue;
                            }

                            let length = member.calculate_length() as f64;

                            // end intensities based on distribution_shape (same as in assembler)
                            let (w1, w2) = match distributed_load.distribution_shape {
                                crate::models::loads::distributionshape::DistributionShape::Uniform => {
                                    (distributed_load.magnitude, distributed_load.end_magnitude)
                                }
                                crate::models::loads::distributionshape::DistributionShape::Triangular => {
                                    (distributed_load.magnitude, 0.0)
                                }
                                crate::models::loads::distributionshape::DistributionShape::InverseTriangular => {
                                    (0.0, distributed_load.end_magnitude)
                                }
                            };

                            let start_fraction = distributed_load.start_frac;
                            let end_fraction = distributed_load.end_frac;

                            let delta_1 = end_fraction - start_fraction;
                            if delta_1.abs() < 1e-14 {
                                continue;
                            }
                            let delta_2 =
                                end_fraction * end_fraction - start_fraction * start_fraction;
                            let delta_3 = end_fraction.powi(3) - start_fraction.powi(3);
                            let delta_4 = end_fraction.powi(4) - start_fraction.powi(4);
                            let delta_5 = end_fraction.powi(5) - start_fraction.powi(5);

                            // identical primitives as your assembler
                            let integral_n1 = delta_1 - delta_3 + 0.5 * delta_4;
                            let integral_x_n1 = 0.5 * delta_2 - 0.75 * delta_4 + 0.4 * delta_5;

                            let integral_n3 = delta_3 - 0.5 * delta_4;
                            let integral_x_n3 = 0.75 * delta_4 - 0.4 * delta_5;

                            let integral_n2 =
                                0.5 * delta_2 - (2.0 / 3.0) * delta_3 + 0.25 * delta_4;
                            let integral_x_n2 =
                                (1.0 / 3.0) * delta_3 - 0.5 * delta_4 + 0.2 * delta_5;

                            let integral_n4 = (1.0 / 3.0) * delta_3 - 0.25 * delta_4;
                            let integral_x_n4 = 0.25 * delta_4 - 0.2 * delta_5;

                            let inverse_delta_1 = 1.0 / delta_1;

                            let force_component_start = length
                                * (w1 * integral_n1
                                    + (w2 - w1)
                                        * inverse_delta_1
                                        * (integral_x_n1 - start_fraction * integral_n1));
                            let force_component_end = length
                                * (w1 * integral_n3
                                    + (w2 - w1)
                                        * inverse_delta_1
                                        * (integral_x_n3 - start_fraction * integral_n3));
                            let moment_component_start = length
                                * length
                                * (w1 * integral_n2
                                    + (w2 - w1)
                                        * inverse_delta_1
                                        * (integral_x_n2 - start_fraction * integral_n2));
                            let moment_component_end = -length
                                * length
                                * (w1 * integral_n4
                                    + (w2 - w1)
                                        * inverse_delta_1
                                        * (integral_x_n4 - start_fraction * integral_n4));

                            // NOTE: keep your axis mapping exactly as in assembler:
                            //   direction.x -> Mx
                            //   direction.y -> Mz
                            //   direction.z -> My
                            let (direction_x, direction_y, direction_z) =
                                distributed_load.direction;

                            // start node (local dof order: Fx,Fy,Fz,Mx,My,Mz)
                            local_equivalent_end_load_vector[0] +=
                                force_component_start * direction_x;
                            local_equivalent_end_load_vector[1] +=
                                force_component_start * direction_y;
                            local_equivalent_end_load_vector[2] +=
                                force_component_start * direction_z;
                            local_equivalent_end_load_vector[3] +=
                                moment_component_start * direction_x; // Mx
                            local_equivalent_end_load_vector[5] +=
                                moment_component_start * direction_y; // Mz
                            local_equivalent_end_load_vector[4] +=
                                moment_component_start * direction_z; // My

                            // end node
                            local_equivalent_end_load_vector[6] +=
                                force_component_end * direction_x;
                            local_equivalent_end_load_vector[7] +=
                                force_component_end * direction_y;
                            local_equivalent_end_load_vector[8] +=
                                force_component_end * direction_z;
                            local_equivalent_end_load_vector[9] +=
                                moment_component_end * direction_x; // Mx
                            local_equivalent_end_load_vector[11] +=
                                moment_component_end * direction_y; // Mz
                            local_equivalent_end_load_vector[10] +=
                                moment_component_end * direction_z; // My
                        }
                    }
                }
                ResultType::Loadcombination(load_combination_id) => {
                    if let Some(load_combination) = fers
                        .load_combinations
                        .iter()
                        .find(|c| c.load_combination_id == *load_combination_id)
                    {
                        for (case_id, factor) in &load_combination.load_cases_factors {
                            if let Some(load_case) =
                                fers.load_cases.iter().find(|lc| lc.id == *case_id)
                            {
                                // accumulate this case’s contribution first, then scale by its factor
                                let mut local_equivalent_end_load_vector_for_this_case =
                                    DVector::<f64>::zeros(12);

                                for distributed_load in &load_case.distributed_loads {
                                    if distributed_load.member != member.id
                                        || distributed_load.load_case != *case_id
                                    {
                                        continue;
                                    }

                                    let length = member.calculate_length() as f64;

                                    let (w1, w2) = match distributed_load.distribution_shape {
                                        crate::models::loads::distributionshape::DistributionShape::Uniform => {
                                            (distributed_load.magnitude, distributed_load.end_magnitude)
                                        }
                                        crate::models::loads::distributionshape::DistributionShape::Triangular => {
                                            (distributed_load.magnitude, 0.0)
                                        }
                                        crate::models::loads::distributionshape::DistributionShape::InverseTriangular => {
                                            (0.0, distributed_load.end_magnitude)
                                        }
                                    };

                                    let start_fraction = distributed_load.start_frac;
                                    let end_fraction = distributed_load.end_frac;

                                    let delta_1 = end_fraction - start_fraction;
                                    if delta_1.abs() < 1e-14 {
                                        continue;
                                    }
                                    let delta_2 = end_fraction * end_fraction
                                        - start_fraction * start_fraction;
                                    let delta_3 = end_fraction.powi(3) - start_fraction.powi(3);
                                    let delta_4 = end_fraction.powi(4) - start_fraction.powi(4);
                                    let delta_5 = end_fraction.powi(5) - start_fraction.powi(5);

                                    let integral_n1 = delta_1 - delta_3 + 0.5 * delta_4;
                                    let integral_x_n1 =
                                        0.5 * delta_2 - 0.75 * delta_4 + 0.4 * delta_5;

                                    let integral_n3 = delta_3 - 0.5 * delta_4;
                                    let integral_x_n3 = 0.75 * delta_4 - 0.4 * delta_5;

                                    let integral_n2 =
                                        0.5 * delta_2 - (2.0 / 3.0) * delta_3 + 0.25 * delta_4;
                                    let integral_x_n2 =
                                        (1.0 / 3.0) * delta_3 - 0.5 * delta_4 + 0.2 * delta_5;

                                    let integral_n4 = (1.0 / 3.0) * delta_3 - 0.25 * delta_4;
                                    let integral_x_n4 = 0.25 * delta_4 - 0.2 * delta_5;

                                    let inverse_delta_1 = 1.0 / delta_1;

                                    let force_component_start = length
                                        * (w1 * integral_n1
                                            + (w2 - w1)
                                                * inverse_delta_1
                                                * (integral_x_n1 - start_fraction * integral_n1));
                                    let force_component_end = length
                                        * (w1 * integral_n3
                                            + (w2 - w1)
                                                * inverse_delta_1
                                                * (integral_x_n3 - start_fraction * integral_n3));
                                    let moment_component_start = length
                                        * length
                                        * (w1 * integral_n2
                                            + (w2 - w1)
                                                * inverse_delta_1
                                                * (integral_x_n2 - start_fraction * integral_n2));
                                    let moment_component_end = -length
                                        * length
                                        * (w1 * integral_n4
                                            + (w2 - w1)
                                                * inverse_delta_1
                                                * (integral_x_n4 - start_fraction * integral_n4));

                                    let (direction_x, direction_y, direction_z) =
                                        distributed_load.direction;

                                    // start node (local)
                                    local_equivalent_end_load_vector_for_this_case[0] +=
                                        force_component_start * direction_x;
                                    local_equivalent_end_load_vector_for_this_case[1] +=
                                        force_component_start * direction_y;
                                    local_equivalent_end_load_vector_for_this_case[2] +=
                                        force_component_start * direction_z;
                                    local_equivalent_end_load_vector_for_this_case[3] +=
                                        moment_component_start * direction_x; // Mx
                                    local_equivalent_end_load_vector_for_this_case[5] +=
                                        moment_component_start * direction_y; // Mz
                                    local_equivalent_end_load_vector_for_this_case[4] +=
                                        moment_component_start * direction_z; // My

                                    // end node (local)
                                    local_equivalent_end_load_vector_for_this_case[6] +=
                                        force_component_end * direction_x;
                                    local_equivalent_end_load_vector_for_this_case[7] +=
                                        force_component_end * direction_y;
                                    local_equivalent_end_load_vector_for_this_case[8] +=
                                        force_component_end * direction_z;
                                    local_equivalent_end_load_vector_for_this_case[9] +=
                                        moment_component_end * direction_x; // Mx
                                    local_equivalent_end_load_vector_for_this_case[11] +=
                                        moment_component_end * direction_y; // Mz
                                    local_equivalent_end_load_vector_for_this_case[10] +=
                                        moment_component_end * direction_z; // My
                                }

                                // scale this case’s contribution and add it
                                local_equivalent_end_load_vector +=
                                    local_equivalent_end_load_vector_for_this_case * (*factor);
                            }
                        }
                    }
                }
            }

            let local_end_forces_vector = &local_stiffness_matrix * &local_displacement_vector
                - &local_equivalent_end_load_vector;

            let global_force_vector = transformation_matrix.transpose() * local_end_forces_vector;

            let start_node_forces = NodeForces {
                fx: global_force_vector[0],
                fy: global_force_vector[1],
                fz: global_force_vector[2],
                mx: global_force_vector[3],
                my: global_force_vector[4],
                mz: global_force_vector[5],
            };
            let end_node_forces = NodeForces {
                fx: global_force_vector[6],
                fy: global_force_vector[7],
                fz: global_force_vector[8],
                mx: global_force_vector[9],
                my: global_force_vector[10],
                mz: global_force_vector[11],
            };

            let (maximums, minimums) =
                compute_component_extrema(&start_node_forces, &end_node_forces);

            results_by_member_identifier.insert(
                member.id,
                MemberResult {
                    start_node_forces,
                    end_node_forces,
                    maximums,
                    minimums,
                },
            );
        }
    }

    results_by_member_identifier
}
