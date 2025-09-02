use crate::models::members::enums::MemberType;
use crate::models::nodes::node::Node;
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, ToSchema, Debug)]
pub struct Member {
    pub id: u32,
    pub start_node: Node,
    pub end_node: Node,
    pub section: Option<u32>,
    pub rotation_angle: f64,
    pub start_hinge: Option<u32>,
    pub end_hinge: Option<u32>,
    pub classification: String,
    pub weight: f64,
    pub chi: Option<f64>,
    pub reference_member: Option<u32>,
    pub reference_node: Option<u32>,
    pub member_type: MemberType,
}

use crate::models::members::{material::Material, section::Section};
use nalgebra::{DMatrix, Vector3};
use std::collections::HashMap;

impl Member {
    pub fn calculate_length(&self) -> f64 {
        self.start_node.distance_to(&self.end_node)
    }

    pub fn calculate_stiffness_matrix_2d(
        &self,
        material_map: &HashMap<u32, &Material>,
        section_map: &HashMap<u32, &Section>,
    ) -> Option<DMatrix<f64>> {
        let section_id = self.section.unwrap_or_else(|| {
            panic!(
                "Member {} ({:?}) missing section id required to compute axial force.",
                self.id, self.member_type
            )
        });

        let section = section_map.get(&section_id)?;
        let material = material_map.get(&section.material)?;

        let e = material.e_mod;
        let a = section.area;
        let i = section.i_y;
        let l = self.calculate_length();

        let axial = e * a / l;
        let bending = e * i / (l * l * l);

        Some(DMatrix::from_row_slice(
            6,
            6,
            &[
                axial,
                0.0,
                0.0,
                -axial,
                0.0,
                0.0,
                0.0,
                12.0 * bending,
                6.0 * l * bending,
                0.0,
                -12.0 * bending,
                6.0 * l * bending,
                0.0,
                6.0 * l * bending,
                4.0 * l * l * bending,
                0.0,
                -6.0 * l * bending,
                2.0 * l * l * bending,
                -axial,
                0.0,
                0.0,
                axial,
                0.0,
                0.0,
                0.0,
                -12.0 * bending,
                -6.0 * l * bending,
                0.0,
                12.0 * bending,
                -6.0 * l * bending,
                0.0,
                6.0 * l * bending,
                2.0 * l * l * bending,
                0.0,
                -6.0 * l * bending,
                4.0 * l * l * bending,
            ],
        ))
    }

    pub fn calculate_stiffness_matrix_3d(
        &self,
        material_map: &HashMap<u32, &Material>,
        section_map: &HashMap<u32, &Section>,
    ) -> Option<DMatrix<f64>> {
        let section_id = self.section.unwrap_or_else(|| {
            panic!(
                "Member {} ({:?}) missing section id required to compute axial force.",
                self.id, self.member_type
            )
        });

        let section = section_map.get(&section_id)?;
        let material = material_map.get(&section.material)?;

        let e = material.e_mod;
        let g = material.g_mod;
        let a = section.area;
        let i_y = section.i_y;
        let i_z = section.i_z;
        let j = section.j;
        let l = self.calculate_length();

        // Define stiffness terms based on the constants from Python
        let axial: f64 = e * a / l;
        let bending_y = 12.0 * e * i_y / (l * l * l);
        let bending_z = 12.0 * e * i_z / (l * l * l);
        let torsion = g * j / l;
        let bending_y_l = 6.0 * e * i_y / (l * l);
        let bending_z_l = 6.0 * e * i_z / (l * l);
        let bending_y_l2 = 4.0 * e * i_y / l;
        let bending_z_l2 = 4.0 * e * i_z / l;
        let half_bending_y_l2 = 2.0 * e * i_y / l;
        let half_bending_z_l2 = 2.0 * e * i_z / l;

        // Construct the stiffness matrix explicitly
        Some(DMatrix::from_row_slice(
            12,
            12,
            &[
                axial,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                -axial,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                bending_z,
                0.0,
                0.0,
                0.0,
                bending_z_l,
                0.0,
                -bending_z,
                0.0,
                0.0,
                0.0,
                bending_z_l,
                0.0,
                0.0,
                bending_y,
                0.0,
                -bending_y_l,
                0.0,
                0.0,
                0.0,
                -bending_y,
                0.0,
                -bending_y_l,
                0.0,
                0.0,
                0.0,
                0.0,
                torsion,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                -torsion,
                0.0,
                0.0,
                0.0,
                0.0,
                -bending_y_l,
                0.0,
                bending_y_l2,
                0.0,
                0.0,
                0.0,
                bending_y_l,
                0.0,
                half_bending_y_l2,
                0.0,
                0.0,
                bending_z_l,
                0.0,
                0.0,
                0.0,
                bending_z_l2,
                0.0,
                -bending_z_l,
                0.0,
                0.0,
                0.0,
                half_bending_z_l2,
                -axial,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                axial,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                -bending_z,
                0.0,
                0.0,
                0.0,
                -bending_z_l,
                0.0,
                bending_z,
                0.0,
                0.0,
                0.0,
                -bending_z_l,
                0.0,
                0.0,
                -bending_y,
                0.0,
                bending_y_l,
                0.0,
                0.0,
                0.0,
                bending_y,
                0.0,
                bending_y_l,
                0.0,
                0.0,
                0.0,
                0.0,
                -torsion,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                torsion,
                0.0,
                0.0,
                0.0,
                0.0,
                -bending_y_l,
                0.0,
                half_bending_y_l2,
                0.0,
                0.0,
                0.0,
                bending_y_l,
                0.0,
                bending_y_l2,
                0.0,
                0.0,
                bending_z_l,
                0.0,
                0.0,
                0.0,
                half_bending_z_l2,
                0.0,
                -bending_z_l,
                0.0,
                0.0,
                0.0,
                bending_z_l2,
            ],
        ))
    }

    pub fn calculate_truss_stiffness_matrix_3d(
        &self,
        material_map: &std::collections::HashMap<u32, &Material>,
        section_map: &std::collections::HashMap<u32, &Section>,
    ) -> Option<nalgebra::DMatrix<f64>> {
        let section_id = self.section.unwrap_or_else(|| {
            panic!(
                "Member {} ({:?}) missing section id required to compute axial force.",
                self.id, self.member_type
            )
        });

        let section: &&Section = section_map.get(&section_id)?;
        let material: &&Material = material_map.get(&section.material)?;
        let e_modulus: f64 = material.e_mod;
        let area: f64 = section.area;
        let length: f64 = self.calculate_length();

        if length <= 0.0 {
            return None;
        }

        let axial: f64 = e_modulus * area / length;

        let mut k_local = nalgebra::DMatrix::<f64>::zeros(12, 12);
        // Local translational x of start and end nodes (indices 0 and 6) couple axially
        k_local[(0, 0)] = axial;
        k_local[(0, 6)] = -axial;
        k_local[(6, 0)] = -axial;
        k_local[(6, 6)] = axial;

        let t = self.calculate_transformation_matrix_3d();
        let k_global = t.transpose() * k_local * t;
        Some(k_global)
    }

    pub fn calculate_transformation_matrix_2d(&self) -> DMatrix<f64> {
        let dx = self.end_node.X - self.start_node.X;
        let dy = self.end_node.Y - self.start_node.Y;
        let l = (dx.powi(2) + dy.powi(2)).sqrt();

        let c = dx / l;
        let s = dy / l;

        DMatrix::from_row_slice(
            6,
            6,
            &[
                c, s, 0.0, 0.0, 0.0, 0.0, -s, c, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, c, s, 0.0, 0.0, 0.0, 0.0, -s, c, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
            ],
        )
    }

    pub fn calculate_transformation_matrix_3d(&self) -> DMatrix<f64> {
        // Local x: along the member
        let dx = self.end_node.X - self.start_node.X;
        let dy = self.end_node.Y - self.start_node.Y;
        let dz = self.end_node.Z - self.start_node.Z;
        let length = (dx * dx + dy * dy + dz * dz).sqrt();
        if length < 1e-12 {
            panic!("Start and end nodes are the same or too close to define a direction.");
        }
        let local_x = Vector3::new(dx / length, dy / length, dz / length);

        let mut reference_vector = Vector3::new(0.0, 1.0, 0.0);
        let dot = local_x.dot(&reference_vector);
        if dot.abs() > 1.0 - 1e-6 {
            reference_vector = Vector3::new(0.0, 0.0, 1.0);
        }

        // Build right-handed frame
        let mut local_z = local_x.cross(&reference_vector);
        let norm_z = local_z.norm();
        if norm_z < 1e-12 {
            // Extremely unlikely with the fallback above
            reference_vector = Vector3::new(1.0, 0.0, 0.0);
            local_z = local_x.cross(&reference_vector);
            if local_z.norm() < 1e-12 {
                panic!("Cannot define a valid local_z axis.");
            }
        }
        let local_z = local_z.normalize();
        let local_y = local_z.cross(&local_x).normalize();

        // Apply roll about local_x by rotation_angle (radians)
        let mut y_axis = local_y;
        let mut z_axis = local_z;
        let phi = self.rotation_angle;
        if phi.abs() > 0.0 {
            let c = phi.cos();
            let s = phi.sin();
            let y_rot = y_axis * c + z_axis * s;
            let z_rot = -y_axis * s + z_axis * c;
            y_axis = y_rot;
            z_axis = z_rot;
        }

        // Rotation R with rows [x; y; z] (global → local)
        let r = DMatrix::from_row_slice(
            3,
            3,
            &[
                local_x.x, local_x.y, local_x.z, y_axis.x, y_axis.y, y_axis.z, z_axis.x, z_axis.y,
                z_axis.z,
            ],
        );

        // Block-diagonal T = diag(R, R, R, R)
        let mut transformation = DMatrix::<f64>::zeros(12, 12);
        for b in 0..4 {
            for i in 0..3 {
                for j in 0..3 {
                    transformation[(b * 3 + i, b * 3 + j)] = r[(i, j)];
                }
            }
        }
        transformation
    }

    pub fn calculate_axial_force_3d(
        &self,
        global_displacement: &DMatrix<f64>,
        material_map: &HashMap<u32, &Material>,
        section_map: &HashMap<u32, &Section>,
    ) -> f64 {
        // 1) Look up E and A
        let section_id = self.section.unwrap_or_else(|| {
            panic!(
                "Member {} ({:?}) missing section id required to compute axial force.",
                self.id, self.member_type
            )
        });
        let section: &&Section = section_map.get(&section_id).unwrap_or_else(|| {
            panic!(
                "Missing section data: member_id={}, section_id={}",
                self.id, section_id
            )
        });

        let material = material_map.get(&section.material).unwrap_or_else(|| {
            panic!(
                "Missing material for section: member_id={}, section_id={}, material_id={}",
                self.id, section_id, section.material
            )
        });
        let e_mod = material.e_mod;
        let area = section.area;

        // 2) Length and transformation
        let length = self.calculate_length();
        let t = self.calculate_transformation_matrix_3d(); // 12×12

        // 3) Extract the 12 global DOFs for this member
        let start_index = (self.start_node.id as usize - 1) * 6;
        let end_index = (self.end_node.id as usize - 1) * 6;
        let mut u_elem = DMatrix::<f64>::zeros(12, 1);
        // start node displacements
        for i in 0..6 {
            u_elem[(i, 0)] = global_displacement[(start_index + i, 0)];
        }
        // end node displacements
        for i in 0..6 {
            u_elem[(i + 6, 0)] = global_displacement[(end_index + i, 0)];
        }

        // 4) Transform to local coords: u_local = T * u_elem
        let u_local = &t * &u_elem;

        // 5) Axial extension = u_local[x_end] - u_local[x_start]
        let extension = u_local[(6, 0)] - u_local[(0, 0)];

        // 6) Axial force = (E·A/L) · extension
        e_mod * area / length * extension
    }

    /// Build the local geometric stiffness matrix for this member, given its axial force.
    pub fn calculate_geometric_stiffness_matrix_3d(&self, axial_force: f64) -> DMatrix<f64> {
        let l = self.calculate_length();
        let p = axial_force;
        let p_over_l = p / l;
        let p_times_l = p * l;

        let mut k_geo = DMatrix::<f64>::zeros(12, 12);

        // --- Axial terms ---
        k_geo[(0, 0)] = p_over_l;
        k_geo[(0, 6)] = -p_over_l;
        k_geo[(6, 0)] = -p_over_l;
        k_geo[(6, 6)] = p_over_l;

        // --- Bending about local z (deflection in y) ---
        // Indices: 1,5,7,11
        k_geo[(1, 1)] = 6.0 / 5.0 * p_over_l;
        k_geo[(1, 5)] = 1.0 / 10.0 * p_times_l;
        k_geo[(1, 7)] = -6.0 / 5.0 * p_over_l;
        k_geo[(1, 11)] = 1.0 / 10.0 * p_times_l;

        k_geo[(5, 1)] = 1.0 / 10.0 * p_times_l;
        k_geo[(5, 5)] = 4.0 / 15.0 * p_times_l;
        k_geo[(5, 7)] = -1.0 / 10.0 * p_times_l;
        k_geo[(5, 11)] = 2.0 / 15.0 * p_times_l;

        k_geo[(7, 1)] = -6.0 / 5.0 * p_over_l;
        k_geo[(7, 5)] = -1.0 / 10.0 * p_times_l;
        k_geo[(7, 7)] = 6.0 / 5.0 * p_over_l;
        k_geo[(7, 11)] = -1.0 / 10.0 * p_times_l;

        k_geo[(11, 1)] = 1.0 / 10.0 * p_times_l;
        k_geo[(11, 5)] = 2.0 / 15.0 * p_times_l;
        k_geo[(11, 7)] = -1.0 / 10.0 * p_times_l;
        k_geo[(11, 11)] = 4.0 / 15.0 * p_times_l;

        // --- Bending about local y (deflection in z) ---
        // Indices: 2,4,8,10
        k_geo[(2, 2)] = 6.0 / 5.0 * p_over_l;
        k_geo[(2, 4)] = 1.0 / 10.0 * p_times_l;
        k_geo[(2, 8)] = -6.0 / 5.0 * p_over_l;
        k_geo[(2, 10)] = 1.0 / 10.0 * p_times_l;

        k_geo[(4, 2)] = 1.0 / 10.0 * p_times_l;
        k_geo[(4, 4)] = 4.0 / 15.0 * p_times_l;
        k_geo[(4, 8)] = -1.0 / 10.0 * p_times_l;
        k_geo[(4, 10)] = 2.0 / 15.0 * p_times_l;

        k_geo[(8, 2)] = -6.0 / 5.0 * p_over_l;
        k_geo[(8, 4)] = -1.0 / 10.0 * p_times_l;
        k_geo[(8, 8)] = 6.0 / 5.0 * p_over_l;
        k_geo[(8, 10)] = -1.0 / 10.0 * p_times_l;

        k_geo[(10, 2)] = 1.0 / 10.0 * p_times_l;
        k_geo[(10, 4)] = 2.0 / 15.0 * p_times_l;
        k_geo[(10, 8)] = -1.0 / 10.0 * p_times_l;
        k_geo[(10, 10)] = 4.0 / 15.0 * p_times_l;

        k_geo
    }
}
