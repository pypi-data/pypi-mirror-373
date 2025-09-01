use nalgebra::DMatrix;
use crate::models::loads::distributionshape::DistributionShape;
use crate::models::loads::loadcase::LoadCase;
use crate::models::members::memberset::MemberSet;
use crate::functions::geometry::get_dof_indices;  

/// Assembles the nodal loads into the global load vector.
pub fn assemble_nodal_loads(load_case: &LoadCase, f: &mut DMatrix<f64>) {
    for nodal_load in &load_case.nodal_loads {
        let node_id = nodal_load.node as usize;
        let (fx_index, fy_index, fz_index, _, _, _) = get_dof_indices(node_id);
        if nodal_load.direction.0 != 0.0 {
            f[(fx_index, 0)] += nodal_load.magnitude * nodal_load.direction.0;
        }
        if nodal_load.direction.1 != 0.0 {
            f[(fy_index, 0)] += nodal_load.magnitude * nodal_load.direction.1;
        }
        if nodal_load.direction.2 != 0.0 {
            f[(fz_index, 0)] += nodal_load.magnitude * nodal_load.direction.2;
        }
    }
}

/// Assembles the nodal moments into the global load vector.
pub fn assemble_nodal_moments(load_case: &LoadCase, f: &mut DMatrix<f64>) {
    for nodal_moment in &load_case.nodal_moments {
        let node_id = nodal_moment.node as usize;
        let (_, _, _, rx_index, ry_index, rz_index) = get_dof_indices(node_id);
        if nodal_moment.direction.0 != 0.0 {
            f[(rx_index, 0)] += nodal_moment.magnitude * nodal_moment.direction.0;
        }
        if nodal_moment.direction.1 != 0.0 {
            f[(ry_index, 0)] += nodal_moment.magnitude * nodal_moment.direction.1;
        }
        if nodal_moment.direction.2 != 0.0 {
            f[(rz_index, 0)] += nodal_moment.magnitude * nodal_moment.direction.2;
        }
    }
}

/// Assembles the distributed loads into the global load vector.
/// The function uses member sets to locate the member for each distributed load.
pub fn assemble_distributed_loads(
    load_case: &LoadCase,
    member_sets: &[MemberSet],
    f: &mut DMatrix<f64>,
    load_case_id: u32,
) {
    for distributed_load in &load_case.distributed_loads {
        if distributed_load.load_case != load_case_id {
            continue;
        }

        // Find the member corresponding to the distributed load
        let member_id = distributed_load.member;        // grab the u32
        let member_opt = member_sets.iter()
            .flat_map(|ms| ms.members.iter())
            .find(|member| member.id == member_id);

        if let Some(member) = member_opt {
            let length = member.calculate_length() as f64;

            // pick w1, w2 based on distribution_shape
            let (w1, w2) = match distributed_load.distribution_shape {
                DistributionShape::Uniform => {
                    (distributed_load.magnitude, distributed_load.end_magnitude)
                }
                DistributionShape::Triangular => {
                    ( distributed_load.magnitude, 0.0)
                }
                DistributionShape::InverseTriangular => {
                    (0.0, distributed_load.end_magnitude)
                }
            };

            // consistent‐load formulas for linearly varying w(x)
            // 1) pull out your fractions, length, and end‐point intensities
            let a    = distributed_load.start_frac;  // s0
            let b    = distributed_load.end_frac;    // s1

            // 2) precompute the “power‐differences” Δn = bⁿ − aⁿ
            let d1 =   b     -   a;
            let d2 =  b*b   -  a*a;
            let d3 =  b*b*b -  a*a*a;
            let d4 =  b.powi(4) - a.powi(4);
            let d5 =  b.powi(5) - a.powi(5);

            // 3) build the four “base” integrals of N_k and ξ·N_k
            let i_n1  =   d1      -   d3      + 0.5   * d4;  // ∫N1 dξ
            let i_xn1 = 0.5*d2   - 0.75   * d4 + 0.4   * d5;  // ∫ξ·N1 dξ

            let i_n3   = d3 - 0.5    * d4;                // ∫N3 dξ  
            let i_x_n3 = 0.75 * d4 - 0.4    * d5;         // ∫ξ·N3 dξ

            let i_n2  = 0.5*d2   - (2.0/3.0)*d3 + 0.25  * d4;   // ∫N2 dξ
            let i_x_n2 = (1.0/3.0)*d3 - 0.5    * d4 + 0.2   * d5; // ∫ξ·N2 dξ

            let i_n4  = (1.0/3.0)*d3 - 0.25   * d4;             // ∫N4 dξ
            let i_x_n4 = 0.25   * d4    - 0.2    * d5;            // ∫ξ·N4 dξ

            // 4) form the weighted integrals over [a,b]:
            //    ∫Nk·w dξ = w1*Ik  +  (w2-w1)/(b-a) * (Ixk  -  a*Ik)
            let inv_d1 = 1.0 / d1;
            let f_i = length * (
                w1*i_n1
            + (w2 - w1)*inv_d1*(i_xn1 - a*i_n1)
            );
            let f_j = length * (
                w1*i_n3
            + (w2 - w1)*inv_d1*(i_x_n3 - a*i_n3)
            );
            let m_i = length*length* (
                w1*i_n2
            + (w2 - w1)*inv_d1*(i_x_n2 - a*i_n2)
            );
            let m_j = -length*length* (
                w1*i_n4
            + (w2 - w1)*inv_d1*(i_x_n4 - a*i_n4)
            );

            // Apply loads for start node
            let start_node_id = member.start_node.id as usize;
            let (start_fx, start_fy, start_fz, start_mx, start_my, start_mz) = get_dof_indices(start_node_id);
            f[(start_fx, 0)] += f_i * distributed_load.direction.0;
            f[(start_fy, 0)] += f_i * distributed_load.direction.1;
            f[(start_fz, 0)] += f_i * distributed_load.direction.2;
            f[(start_mx, 0)] += m_i * distributed_load.direction.0;
            f[(start_mz, 0)] += m_i * distributed_load.direction.1; 
            f[(start_my, 0)] += m_i * distributed_load.direction.2;

            // apply at end node
            let end_node_id = member.end_node.id as usize;
            let (end_fx, end_fy, end_fz, end_mx, end_my, end_mz) = get_dof_indices(end_node_id);
            f[(end_fx, 0)] += f_j * distributed_load.direction.0;
            f[(end_fy, 0)] += f_j * distributed_load.direction.1;
            f[(end_fz, 0)] += f_j * distributed_load.direction.2;
            f[(end_mx, 0)] += m_j * distributed_load.direction.0;
            f[(end_mz, 0)] += m_j * distributed_load.direction.1;
            f[(end_my, 0)] += m_j * distributed_load.direction.2;
        }
    }
}