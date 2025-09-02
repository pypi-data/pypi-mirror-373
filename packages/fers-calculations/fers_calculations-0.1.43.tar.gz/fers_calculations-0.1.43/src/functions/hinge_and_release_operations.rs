use crate::models::members::memberhinge::{AxisMode, MemberHinge};
use nalgebra::DMatrix;

fn submatrix_by_indices(k: &DMatrix<f64>, rows: &[usize], cols: &[usize]) -> DMatrix<f64> {
    let mut out = DMatrix::<f64>::zeros(rows.len(), cols.len());
    for (i_out, &i_in) in rows.iter().enumerate() {
        for (j_out, &j_in) in cols.iter().enumerate() {
            out[(i_out, j_out)] = k[(i_in, j_in)];
        }
    }
    out
}

/// Utility: selection/embedding matrix P (size: n_full × n_keep)
fn selection_matrix(n_full: usize, keep: &[usize]) -> DMatrix<f64> {
    let mut p = DMatrix::<f64>::zeros(n_full, keep.len());
    for (j, &i_full) in keep.iter().enumerate() {
        p[(i_full, j)] = 1.0;
    }
    p
}

/// Local 12-DOF index helper.
/// Local ordering: [uX,uY,uZ,thX,thY,thZ]_A, then [uX,uY,uZ,thX,thY,thZ]_B
fn local_dof_index(is_end_b: bool, is_rot: bool, axis: usize) -> usize {
    let base = if is_end_b { 6 } else { 0 };
    if is_rot {
        base + 3 + axis
    } else {
        base + axis
    }
}

/// Convert Option<f64> to AxisMode (Rigid / Release / Spring(k))
pub fn axis_mode_from_option(value: Option<f64>) -> AxisMode {
    match value {
        None => AxisMode::Rigid,
        Some(k) if k > 0.0 => AxisMode::Spring(k),
        Some(_) => AxisMode::Release,
    }
}

/// Per-end modes (LOCAL axes) directly from hinges.
/// Returns (A_trans, A_rot, B_trans, B_rot).
pub fn modes_from_single_ends(
    a: Option<&MemberHinge>,
    b: Option<&MemberHinge>,
) -> ([AxisMode; 3], [AxisMode; 3], [AxisMode; 3], [AxisMode; 3]) {
    let (vx_a, vy_a, vz_a, mx_a, my_a, mz_a) = a
        .map(|h| {
            (
                h.translational_release_vx,
                h.translational_release_vy,
                h.translational_release_vz,
                h.rotational_release_mx,
                h.rotational_release_my,
                h.rotational_release_mz,
            )
        })
        .unwrap_or((None, None, None, None, None, None));

    let (vx_b, vy_b, vz_b, mx_b, my_b, mz_b) = b
        .map(|h| {
            (
                h.translational_release_vx,
                h.translational_release_vy,
                h.translational_release_vz,
                h.rotational_release_mx,
                h.rotational_release_my,
                h.rotational_release_mz,
            )
        })
        .unwrap_or((None, None, None, None, None, None));

    let a_trans = [
        axis_mode_from_option(vx_a),
        axis_mode_from_option(vy_a),
        axis_mode_from_option(vz_a),
    ];
    let a_rot = [
        axis_mode_from_option(mx_a),
        axis_mode_from_option(my_a),
        axis_mode_from_option(mz_a),
    ];
    let b_trans = [
        axis_mode_from_option(vx_b),
        axis_mode_from_option(vy_b),
        axis_mode_from_option(vz_b),
    ];
    let b_rot = [
        axis_mode_from_option(mx_b),
        axis_mode_from_option(my_b),
        axis_mode_from_option(mz_b),
    ];

    (a_trans, a_rot, b_trans, b_rot)
}

/// Apply end releases and semi-rigid springs to a LOCAL 12x12 beam stiffness.
/// Static condensation on the released DOFs (with optional node-to-ground spring).
pub fn apply_end_releases_to_local_beam_k(
    k_local_in: &DMatrix<f64>, // 12x12
    a_trans: [AxisMode; 3],
    a_rot: [AxisMode; 3],
    b_trans: [AxisMode; 3],
    b_rot: [AxisMode; 3],
) -> Result<DMatrix<f64>, String> {
    if k_local_in.nrows() != 12 || k_local_in.ncols() != 12 {
        return Err("apply_end_releases_to_local_beam_k: matrix must be 12x12".to_string());
    }

    let mut rel_indices: Vec<usize> = Vec::new();
    let mut rel_spring_diag: Vec<f64> = Vec::new();

    let mut consider = |is_end_b: bool, is_rot: bool, modes: [AxisMode; 3]| {
        for axis in 0..3 {
            match modes[axis] {
                AxisMode::Rigid => {}
                AxisMode::Release => {
                    rel_indices.push(local_dof_index(is_end_b, is_rot, axis));
                    rel_spring_diag.push(0.0);
                }
                AxisMode::Spring(k) => {
                    rel_indices.push(local_dof_index(is_end_b, is_rot, axis));
                    rel_spring_diag.push(k.max(0.0));
                }
            }
        }
    };

    consider(false, false, a_trans);
    consider(false, true, a_rot);
    consider(true, false, b_trans);
    consider(true, true, b_rot);

    if rel_indices.is_empty() {
        return Ok(k_local_in.clone());
    }

    let universe: Vec<usize> = (0..12).collect();
    let rel_set: std::collections::HashSet<usize> = rel_indices.iter().copied().collect();
    let keep_indices: Vec<usize> = universe
        .into_iter()
        .filter(|i| !rel_set.contains(i))
        .collect();

    let k_kk = submatrix_by_indices(k_local_in, &keep_indices, &keep_indices);
    let k_kr = submatrix_by_indices(k_local_in, &keep_indices, &rel_indices);
    let k_rk = submatrix_by_indices(k_local_in, &rel_indices, &keep_indices);
    let mut k_rr = submatrix_by_indices(k_local_in, &rel_indices, &rel_indices);

    for (i, ks) in rel_spring_diag.iter().enumerate() {
        k_rr[(i, i)] += *ks;
    }

    let try_solve = |m: &DMatrix<f64>, rhs: &DMatrix<f64>| -> Option<DMatrix<f64>> {
        m.clone().lu().solve(rhs)
    };

    let x_opt = try_solve(&k_rr, &k_rk).or_else(|| {
        let mut k_rr_reg = k_rr.clone();
        let eps = 1.0e-12;
        for i in 0..k_rr_reg.nrows() {
            k_rr_reg[(i, i)] += eps;
        }
        k_rr_reg.lu().solve(&k_rk)
    });

    let x = x_opt
        .ok_or_else(|| "apply_end_releases_to_local_beam_k: (K_rr) is singular".to_string())?;
    let k_eff = &k_kk - &(k_kr * x);

    let p = selection_matrix(12, &keep_indices);
    let k_local_out = &p * k_eff * p.transpose();

    Ok(k_local_out)
}

/// LOCAL 12x12 matrix for node-to-ground translational springs at ends A and B (trusses).
/// Only translations are considered; rotations are ignored.
pub fn build_local_truss_translational_spring_k(
    a_trans: [AxisMode; 3],
    b_trans: [AxisMode; 3],
) -> DMatrix<f64> {
    let mut k = DMatrix::<f64>::zeros(12, 12);
    for axis in 0..3 {
        if let AxisMode::Spring(ka) = a_trans[axis] {
            let i = local_dof_index(false, false, axis);
            k[(i, i)] += ka.max(0.0);
        }
        if let AxisMode::Spring(kb) = b_trans[axis] {
            let i = local_dof_index(true, false, axis);
            k[(i, i)] += kb.max(0.0);
        }
    }
    k
}
