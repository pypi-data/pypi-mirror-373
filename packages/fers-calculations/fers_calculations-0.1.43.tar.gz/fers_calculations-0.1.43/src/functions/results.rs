use crate::functions::hinge_and_release_operations::modes_from_single_ends;
use crate::models::fers::fers::FERS;
use crate::models::members::enums::MemberType;
use crate::models::members::memberhinge::AxisMode;
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

fn build_elimination_from_modes(
    a_trans: &[AxisMode; 3],
    a_rot: &[AxisMode; 3],
    b_trans: &[AxisMode; 3],
    b_rot: &[AxisMode; 3],
) -> (Vec<usize>, Vec<f64>) {
    let mut elim_idx: Vec<usize> = Vec::new();
    let mut kdiag: Vec<f64> = Vec::new();

    let mut push_mode = |local_index: usize, mode: &AxisMode| {
        match *mode {
            AxisMode::Rigid => { /* retained; nothing to eliminate */ }
            AxisMode::Release => {
                elim_idx.push(local_index);
                kdiag.push(0.0);
            }
            AxisMode::Spring(k) => {
                elim_idx.push(local_index);
                kdiag.push(k.max(0.0));
            }
        }
    };

    // DOF ordering for displacements in local member vector:
    // start: [ux, uy, uz, rx, ry, rz] => indices 0..=5
    // end:   [ux, uy, uz, rx, ry, rz] => indices 6..=11
    for i in 0..3 {
        push_mode(i, &a_trans[i]); // start translations: 0,1,2
        push_mode(3 + i, &a_rot[i]); // start rotations:    3,4,5
        push_mode(6 + i, &b_trans[i]); // end translations:    6,7,8
        push_mode(9 + i, &b_rot[i]); // end rotations:       9,10,11
    }

    (elim_idx, kdiag)
}

/// Recover member-side end forces with semi-rigid ends (and perfect releases)
/// by re-introducing the eliminated DOFs and solving the small interface system.
fn recover_member_end_forces_local(
    k_local_base: &DMatrix<f64>, // 12x12
    u_local_node: &DVector<f64>, // 12x1 (node-side DoFs)
    f_eq_local: &DVector<f64>,   // 12x1 (eq. nodal loads from distributed loads) in LOCAL axes
    a_trans: &[AxisMode; 3],
    a_rot: &[AxisMode; 3],
    b_trans: &[AxisMode; 3],
    b_rot: &[AxisMode; 3],
) -> DVector<f64> {
    // Build elimination set and the corresponding spring stiffness diag
    let (elim_idx, kdiag) = build_elimination_from_modes(a_trans, a_rot, b_trans, b_rot);

    // P u := keep retained components from u_node, zero on eliminated positions
    let mut u_p = u_local_node.clone();
    for &idx in &elim_idx {
        u_p[idx] = 0.0;
    }

    if elim_idx.is_empty() {
        // no semi-rigid / release => classic q = K u − f_eq
        return k_local_base * u_p - f_eq_local;
    }

    // Build A = K_rr + diag(k)
    let m = elim_idx.len();
    let mut a_mat = DMatrix::<f64>::zeros(m, m);

    for (ri, &i_idx) in elim_idx.iter().enumerate() {
        for (rj, &j_idx) in elim_idx.iter().enumerate() {
            a_mat[(ri, rj)] = k_local_base[(i_idx, j_idx)];
        }
        a_mat[(ri, ri)] += kdiag[ri];
    }

    // Build RHS: diag(k)*u_J − (K_rQ * (P u) − f_eq_J)
    let mut rhs = DVector::<f64>::zeros(m);
    for (ri, &i_idx) in elim_idx.iter().enumerate() {
        // t1 = K[i_idx, :] * (P u)
        let mut t1 = 0.0;
        for j in 0..12 {
            t1 += k_local_base[(i_idx, j)] * u_p[j];
        }
        let f_eq_i = f_eq_local[i_idx];
        rhs[ri] = kdiag[ri] * u_local_node[i_idx] - (t1 - f_eq_i);
    }

    // Solve for r (eliminated member end DoFs)
    let r = match a_mat.lu().solve(&rhs) {
        Some(sol) => sol,
        None => {
            log::warn!("Semi-rigid recovery: (K_rr + diag(k)) is singular. Falling back to r = 0.");
            DVector::<f64>::zeros(m)
        }
    };

    // Assemble full member DoF vector: u_member = P u + S r
    let mut u_member = u_p;
    for (ri, &i_idx) in elim_idx.iter().enumerate() {
        u_member[i_idx] = r[ri];
    }

    // Member-side end forces
    k_local_base * u_member - f_eq_local
}

pub fn compute_member_results_from_displacement(
    fers: &FERS,
    result_type: &ResultType,
    global_displacement_vector: &DMatrix<f64>,
) -> BTreeMap<u32, MemberResult> {
    let (material_map, section_map, hinge_map, _support_map) = fers.build_lookup_maps();
    let mut results_by_member_identifier: BTreeMap<u32, MemberResult> = BTreeMap::new();

    for member_set in &fers.member_sets {
        for member in &member_set.members {
            if matches!(member.member_type, MemberType::Rigid) {
                continue;
            }

            let start_node_dof_index = (member.start_node.id as usize - 1) * 6;
            let end_node_dof_index = (member.end_node.id as usize - 1) * 6;

            let mut u_member_global = DVector::<f64>::zeros(12);
            for dof in 0..6 {
                u_member_global[dof] = global_displacement_vector[(start_node_dof_index + dof, 0)];
                u_member_global[dof + 6] =
                    global_displacement_vector[(end_node_dof_index + dof, 0)];
            }

            // Base local K (BEFORE releases)
            let k_local_base =
                match member.calculate_stiffness_matrix_3d(&material_map, &section_map) {
                    Some(k) => k,
                    None => {
                        // For non-beam elements (e.g., truss), you may want a separate path.
                        // For now, skip cleanly.
                        continue;
                    }
                };

            let t = member.calculate_transformation_matrix_3d();
            let u_local_node = &t * &u_member_global; // node-side DoFs (what the solver sees)

            // Equivalent nodal loads in LOCAL axes (only distributed loads contribute here)
            let mut f_eq_local = DVector::<f64>::zeros(12);

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

                            // end intensities (same convention as in assembler)
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

                            let a = distributed_load.start_frac;
                            let b = distributed_load.end_frac;
                            let d1 = b - a;
                            if d1.abs() < 1e-14 {
                                continue;
                            }
                            let d2 = b * b - a * a;
                            let d3 = b.powi(3) - a.powi(3);
                            let d4 = b.powi(4) - a.powi(4);
                            let d5 = b.powi(5) - a.powi(5);

                            let int_n1 = d1 - d3 + 0.5 * d4;
                            let int_xn1 = 0.5 * d2 - 0.75 * d4 + 0.4 * d5;

                            let int_n3 = d3 - 0.5 * d4;
                            let int_xn3 = 0.75 * d4 - 0.4 * d5;

                            let int_n2 = 0.5 * d2 - (2.0 / 3.0) * d3 + 0.25 * d4;
                            let int_xn2 = (1.0 / 3.0) * d3 - 0.5 * d4 + 0.2 * d5;

                            let int_n4 = (1.0 / 3.0) * d3 - 0.25 * d4;
                            let int_xn4 = 0.25 * d4 - 0.2 * d5;

                            let inv_d1 = 1.0 / d1;

                            let f_s = length
                                * (w1 * int_n1 + (w2 - w1) * inv_d1 * (int_xn1 - a * int_n1));
                            let f_e = length
                                * (w1 * int_n3 + (w2 - w1) * inv_d1 * (int_xn3 - a * int_n3));
                            let m_s = length
                                * length
                                * (w1 * int_n2 + (w2 - w1) * inv_d1 * (int_xn2 - a * int_n2));
                            let m_e = -length
                                * length
                                * (w1 * int_n4 + (w2 - w1) * inv_d1 * (int_xn4 - a * int_n4));

                            // Axis mapping: dir.x -> Mx, dir.y -> Mz, dir.z -> My  (matches your assembler)
                            let (dx, dy, dz) = distributed_load.direction;

                            // start node (local dof order: Fx,Fy,Fz,Mx,My,Mz)
                            f_eq_local[0] += f_s * dx;
                            f_eq_local[1] += f_s * dy;
                            f_eq_local[2] += f_s * dz;
                            f_eq_local[3] += m_s * dx; // Mx
                            f_eq_local[5] += m_s * dy; // Mz
                            f_eq_local[4] += m_s * dz; // My

                            // end node
                            f_eq_local[6] += f_e * dx;
                            f_eq_local[7] += f_e * dy;
                            f_eq_local[8] += f_e * dz;
                            f_eq_local[9] += m_e * dx; // Mx
                            f_eq_local[11] += m_e * dy; // Mz
                            f_eq_local[10] += m_e * dz; // My
                        }
                    }
                }
                ResultType::Loadcombination(load_combination_id) => {
                    if let Some(lc) = fers
                        .load_combinations
                        .iter()
                        .find(|c| c.load_combination_id == *load_combination_id)
                    {
                        for (case_id, factor) in &lc.load_cases_factors {
                            if let Some(load_case) =
                                fers.load_cases.iter().find(|x| x.id == *case_id)
                            {
                                let mut v_case = DVector::<f64>::zeros(12);

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

                                    let a = distributed_load.start_frac;
                                    let b = distributed_load.end_frac;
                                    let d1 = b - a;
                                    if d1.abs() < 1e-14 {
                                        continue;
                                    }
                                    let d2 = b * b - a * a;
                                    let d3 = b.powi(3) - a.powi(3);
                                    let d4 = b.powi(4) - a.powi(4);
                                    let d5 = b.powi(5) - a.powi(5);

                                    let int_n1 = d1 - d3 + 0.5 * d4;
                                    let int_xn1 = 0.5 * d2 - 0.75 * d4 + 0.4 * d5;

                                    let int_n3 = d3 - 0.5 * d4;
                                    let int_xn3 = 0.75 * d4 - 0.4 * d5;

                                    let int_n2 = 0.5 * d2 - (2.0 / 3.0) * d3 + 0.25 * d4;
                                    let int_xn2 = (1.0 / 3.0) * d3 - 0.5 * d4 + 0.2 * d5;

                                    let int_n4 = (1.0 / 3.0) * d3 - 0.25 * d4;
                                    let int_xn4 = 0.25 * d4 - 0.2 * d5;

                                    let inv_d1 = 1.0 / d1;

                                    let f_s = length
                                        * (w1 * int_n1
                                            + (w2 - w1) * inv_d1 * (int_xn1 - a * int_n1));
                                    let f_e = length
                                        * (w1 * int_n3
                                            + (w2 - w1) * inv_d1 * (int_xn3 - a * int_n3));
                                    let m_s = length
                                        * length
                                        * (w1 * int_n2
                                            + (w2 - w1) * inv_d1 * (int_xn2 - a * int_n2));
                                    let m_e = -length
                                        * length
                                        * (w1 * int_n4
                                            + (w2 - w1) * inv_d1 * (int_xn4 - a * int_n4));

                                    let (dx, dy, dz) = distributed_load.direction;

                                    v_case[0] += f_s * dx;
                                    v_case[1] += f_s * dy;
                                    v_case[2] += f_s * dz;
                                    v_case[3] += m_s * dx;
                                    v_case[5] += m_s * dy;
                                    v_case[4] += m_s * dz;

                                    v_case[6] += f_e * dx;
                                    v_case[7] += f_e * dy;
                                    v_case[8] += f_e * dz;
                                    v_case[9] += m_e * dx;
                                    v_case[11] += m_e * dy;
                                    v_case[10] += m_e * dz;
                                }

                                f_eq_local += v_case * (*factor);
                            }
                        }
                    }
                }
            }

            // Hinge modes (per end, local axes)
            let a_h = member
                .start_hinge
                .and_then(|id| hinge_map.get(&id).copied());
            let b_h = member.end_hinge.and_then(|id| hinge_map.get(&id).copied());
            let (a_trans, a_rot, b_trans, b_rot) = modes_from_single_ends(a_h, b_h);

            // --- Semi-rigid recovery ---
            let q_local_member = recover_member_end_forces_local(
                &k_local_base,
                &u_local_node,
                &f_eq_local,
                &a_trans,
                &a_rot,
                &b_trans,
                &b_rot,
            );

            // Report in GLOBAL
            let global_force_vector = t.transpose() * q_local_member;

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
