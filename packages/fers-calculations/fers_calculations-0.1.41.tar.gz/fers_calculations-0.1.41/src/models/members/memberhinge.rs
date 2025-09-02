use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct MemberHinge {
    pub id: u32,
    pub hinge_type: String,
    pub translational_release_vx: Option<f64>,
    pub translational_release_vy: Option<f64>,
    pub translational_release_vz: Option<f64>,
    pub rotational_release_mx: Option<f64>,
    pub rotational_release_my: Option<f64>,
    pub rotational_release_mz: Option<f64>,
    pub max_tension_vx: Option<f64>,
    pub max_tension_vy: Option<f64>,
    pub max_tension_vz: Option<f64>,
    pub max_moment_mx: Option<f64>,
    pub max_moment_my: Option<f64>,
    pub max_moment_mz: Option<f64>,
}

#[derive(Clone, Copy, Debug)]
pub enum AxisMode {
    Rigid,       // exact constraint (use elimination)
    Release,     // perfect release (no K contribution)
    Spring(f64), // finite stiffness (add connector term)
}

fn combine_axis(a: Option<f64>, b: Option<f64>) -> AxisMode {
    match (a, b) {
        (None, None) => AxisMode::Rigid, // both rigid => rigid
        (Some(ka), None) | (None, Some(ka)) => {
            // one-sided spring
            if ka > 0.0 {
                AxisMode::Spring(ka)
            } else {
                AxisMode::Release
            }
        }
        (Some(ka), Some(kb)) => {
            let k = ka.max(0.0) + kb.max(0.0);
            if k == 0.0 {
                AxisMode::Release
            } else {
                AxisMode::Spring(k)
            }
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct AxisModes {
    pub trans: [AxisMode; 3], // Vx, Vy, Vz
    pub rot: [AxisMode; 3],   // Mx, My, Mz
}

pub fn classify_from_hinges(a: Option<&MemberHinge>, b: Option<&MemberHinge>) -> AxisModes {
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

    AxisModes {
        trans: [
            combine_axis(vx_a, vx_b),
            combine_axis(vy_a, vy_b),
            combine_axis(vz_a, vz_b),
        ],
        rot: [
            combine_axis(mx_a, mx_b),
            combine_axis(my_a, my_b),
            combine_axis(mz_a, mz_b),
        ],
    }
}

fn skew_matrix(r_x: f64, r_y: f64, r_z: f64) -> nalgebra::Matrix3<f64> {
    nalgebra::Matrix3::<f64>::new(0.0, -r_z, r_y, r_z, 0.0, -r_x, -r_y, r_x, 0.0)
}

pub fn build_connector_springs_12x12(
    pos_a: (f64, f64, f64),
    pos_b: (f64, f64, f64),
    modes: &AxisModes,
) -> nalgebra::DMatrix<f64> {
    use nalgebra::{DMatrix, Matrix3};

    // Collect stiffness only for SPRING modes; others = 0 (Rigid handled by elimination, Release has no K)
    let mut k_t = [0.0; 3];
    let mut k_r = [0.0; 3];
    for i in 0..3 {
        if let AxisMode::Spring(k) = modes.trans[i] {
            k_t[i] = k;
        }
        if let AxisMode::Spring(k) = modes.rot[i] {
            k_r[i] = k;
        }
    }
    if k_t == [0.0; 3] && k_r == [0.0; 3] {
        return DMatrix::<f64>::zeros(12, 12);
    }

    let (xa, ya, za) = pos_a;
    let (xb, yb, zb) = pos_b;
    let rx = xb - xa;
    let ry = yb - ya;
    let rz = zb - za;

    let i3 = Matrix3::<f64>::identity();
    let skew_r = skew_matrix(rx, ry, rz);

    // alpha=1.0 (pivot at A) to match elimination rows
    let alpha = 1.0;

    let mut b = DMatrix::<f64>::zeros(6, 12);
    // t_rel rows
    b.view_mut((0, 0), (3, 3)).copy_from(&(-i3)); // u_A
    b.view_mut((0, 3), (3, 3)).copy_from(&(-alpha * skew_r)); // th_A
    b.view_mut((0, 6), (3, 3)).copy_from(&i3); // u_B
    b.view_mut((0, 9), (3, 3))
        .copy_from(&(-(1.0 - alpha) * skew_r)); // th_B (zero here)

    // r_rel rows
    b.view_mut((3, 3), (3, 3)).copy_from(&(-i3)); // th_A
    b.view_mut((3, 9), (3, 3)).copy_from(&i3); // th_B

    // Diagonal Kc with only the spring axes
    let mut kc = DMatrix::<f64>::zeros(6, 6);
    kc[(0, 0)] = k_t[0];
    kc[(1, 1)] = k_t[1];
    kc[(2, 2)] = k_t[2];
    kc[(3, 3)] = k_r[0];
    kc[(4, 4)] = k_r[1];
    kc[(5, 5)] = k_r[2];

    b.transpose() * kc * b
}
