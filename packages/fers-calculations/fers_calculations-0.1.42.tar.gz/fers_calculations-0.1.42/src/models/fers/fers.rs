use crate::functions::results::{compute_member_results_from_displacement, extract_displacements};
use crate::models::members::memberhinge::{classify_from_hinges, AxisMode, AxisModes};
use nalgebra::DMatrix;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, HashMap, HashSet};
use utoipa::ToSchema;
// use csv::Writer;
// use std::error::Error;
use crate::models::imperfections::imperfectioncase::ImperfectionCase;
use crate::models::loads::loadcase::LoadCase;
use crate::models::loads::loadcombination::LoadCombination;
use crate::models::members::enums::MemberType;
use crate::models::members::memberset::MemberSet;
use crate::models::members::{
    material::Material, memberhinge::MemberHinge, section::Section, shapepath::ShapePath,
};
use crate::models::results::resultbundle::ResultsBundle;
use crate::models::results::results::{ResultType, Results};
use crate::models::results::resultssummary::ResultsSummary;
use crate::models::settings::settings::Settings;
use crate::models::supports::nodalsupport::NodalSupport;
use crate::models::supports::supportconditiontype::SupportConditionType;

use crate::functions::hinge_and_release_operations::{
    apply_end_releases_to_local_beam_k, build_local_truss_translational_spring_k,
    modes_from_single_ends,
};
use crate::functions::load_assembler::{
    assemble_distributed_loads, assemble_nodal_loads, assemble_nodal_moments,
};
use crate::functions::reactions::extract_reaction_nodes;

#[derive(Serialize, Deserialize, ToSchema, Debug)]
pub struct FERS {
    pub member_sets: Vec<MemberSet>,
    pub load_cases: Vec<LoadCase>,
    pub load_combinations: Vec<LoadCombination>,
    pub imperfection_cases: Vec<ImperfectionCase>,
    pub settings: Settings,
    pub results: Option<ResultsBundle>,
    pub memberhinges: Option<Vec<MemberHinge>>,
    pub materials: Vec<Material>,
    pub sections: Vec<Section>,
    pub nodal_supports: Vec<NodalSupport>,
    pub shape_paths: Option<Vec<ShapePath>>,
}

const AXIAL_SLACK_TOLERANCE_DEFAULT: f64 = 1.0e-6;

struct RigidElimination {
    s: DMatrix<f64>,
    full_to_red: HashMap<usize, usize>,
}

pub struct AssemblyContext<'a> {
    pub material_by_id: HashMap<u32, &'a Material>,
    pub section_by_id: HashMap<u32, &'a Section>,
    pub hinge_by_id: HashMap<u32, &'a MemberHinge>,
    pub support_by_id: HashMap<u32, &'a NodalSupport>,
}

impl<'a> AssemblyContext<'a> {
    pub fn new(model: &'a FERS) -> Self {
        let (material_by_id, section_by_id, hinge_by_id, support_by_id) = model.build_lookup_maps();
        Self {
            material_by_id,
            section_by_id,
            hinge_by_id,
            support_by_id,
        }
    }
}

const TRANSLATION_AXES: [(&str, usize); 3] = [("X", 0), ("Y", 1), ("Z", 2)];
const ROTATION_AXES: [(&str, usize); 3] = [("X", 3), ("Y", 4), ("Z", 5)];

macro_rules! get_case_insensitive {
    ($map:expr, $key:expr) => {
        $map.get($key)
            .or_else(|| $map.get(&$key.to_ascii_lowercase()))
    };
}

impl FERS {
    fn compute_full_residual_with_rigid_constraints(
        &self,
        active_member_map: &std::collections::HashMap<u32, bool>,
        displacement_vector_full: &nalgebra::DMatrix<f64>,
        external_load_vector_full: &nalgebra::DMatrix<f64>,
    ) -> Result<nalgebra::DMatrix<f64>, String> {
        // Build unconstrained full operator (material + support springs; no geometric part here)
        let stiffness_matrix_full = self.build_operator_with_supports(active_member_map, None)?;

        // Build the same elimination used during the solve (rigid links → MPC)
        let elimination = self.build_rigid_elimination_partial_using_hinges()?;

        // Reduce
        let displacement_vector_reduced = elimination.s.transpose() * displacement_vector_full;
        let external_load_vector_reduced = elimination.s.transpose() * external_load_vector_full;
        let stiffness_matrix_reduced =
            elimination.s.transpose() * stiffness_matrix_full * &elimination.s;

        // Residual in reduced coordinates
        let residual_vector_reduced =
            stiffness_matrix_reduced * displacement_vector_reduced - external_load_vector_reduced;

        // Map residual back to full space
        let residual_vector_full = &elimination.s * residual_vector_reduced;
        Ok(residual_vector_full)
    }

    fn visit_unique_supported_nodes<F>(&self, mut visitor: F) -> Result<(), String>
    where
        F: FnMut(u32, usize, &NodalSupport) -> Result<(), String>,
    {
        use std::collections::{HashMap, HashSet};

        let support_by_id: HashMap<u32, &NodalSupport> =
            self.nodal_supports.iter().map(|s| (s.id, s)).collect();

        let mut visited_node_ids: HashSet<u32> = HashSet::new();

        for member_set in &self.member_sets {
            for member in &member_set.members {
                for node in [&member.start_node, &member.end_node] {
                    if !visited_node_ids.insert(node.id) {
                        continue;
                    }
                    if let Some(support_id) = node.nodal_support {
                        if let Some(nodal_support) = support_by_id.get(&support_id) {
                            let base_index = (node.id as usize - 1) * 6;
                            visitor(node.id, base_index, *nodal_support)?; // propagate
                        }
                    }
                }
            }
        }
        Ok(())
    }

    fn spring_stiffness_or_error(
        owner_id: u32,
        axis_label: &str,
        kind_label: &str,
        stiffness: Option<f64>,
    ) -> Result<f64, String> {
        let k = stiffness.ok_or_else(|| {
            format!(
                "Support {} {} {} is Spring but stiffness is missing.",
                owner_id, kind_label, axis_label
            )
        })?;
        if k <= 0.0 {
            return Err(format!(
                "Support {} {} {} Spring stiffness must be positive.",
                owner_id, kind_label, axis_label
            ));
        }
        Ok(k)
    }

    fn compute_support_spring_reaction_vector_verbose(
        &self,
        displacement_vector_full: &nalgebra::DMatrix<f64>,
    ) -> Result<nalgebra::DMatrix<f64>, String> {
        let number_of_degrees_of_freedom = self.compute_num_dofs();
        let mut spring_reaction_vector_full =
            nalgebra::DMatrix::<f64>::zeros(number_of_degrees_of_freedom, 1);

        self.visit_unique_supported_nodes(|_node_id, base_index, nodal_support| {
            // Translational springs
            for (axis_label, local_dof) in TRANSLATION_AXES {
                if let Some(condition) =
                    get_case_insensitive!(nodal_support.displacement_conditions, axis_label)
                {
                    if let SupportConditionType::Spring = condition.condition_type {
                        let stiffness = Self::spring_stiffness_or_error(
                            nodal_support.id,
                            axis_label,
                            "displacement",
                            condition.stiffness,
                        )?;
                        let u = displacement_vector_full[(base_index + local_dof, 0)];
                        spring_reaction_vector_full[(base_index + local_dof, 0)] += stiffness * u;
                    }
                }
            }

            // Rotational springs
            for (axis_label, local_dof) in ROTATION_AXES {
                if let Some(condition) =
                    get_case_insensitive!(nodal_support.rotation_conditions, axis_label)
                {
                    if let SupportConditionType::Spring = condition.condition_type {
                        let stiffness = Self::spring_stiffness_or_error(
                            nodal_support.id,
                            axis_label,
                            "rotation",
                            condition.stiffness,
                        )?;
                        let r = displacement_vector_full[(base_index + local_dof, 0)];
                        spring_reaction_vector_full[(base_index + local_dof, 0)] += stiffness * r;
                    }
                }
            }
            Ok(())
        })?; // propagate visitor errors

        Ok(spring_reaction_vector_full)
    }

    /// Compose a support reaction vector with the following semantics:
    /// - Fixed  DOFs: reaction = residual = (K u − f) at that DOF
    /// - Spring DOFs: reaction = k * dof_value
    /// - Free   DOFs: reaction = 0
    /// - PositiveOnly: clamp to ≥ 0
    /// - NegativeOnly: clamp to ≤ 0
    fn compose_support_reaction_vector(
        &self,
        active_member_map: &std::collections::HashMap<u32, bool>,
        displacement_vector_full: &nalgebra::DMatrix<f64>,
        external_load_vector_full: &nalgebra::DMatrix<f64>,
    ) -> Result<nalgebra::DMatrix<f64>, String> {
        // Operator without geometric part
        let linear_operator_full = self.build_operator_with_supports(active_member_map, None)?;
        let residual_vector_full = self.compute_full_residual_with_rigid_constraints(
            active_member_map,
            displacement_vector_full,
            external_load_vector_full,
        )?;

        // Spring contributions
        let spring_reaction_vector_full =
            self.compute_support_spring_reaction_vector_verbose(displacement_vector_full)?;

        // (Optional) keep your debug blocks; consider gating them behind a feature flag.
        for node_id in 1..=3 {
            let base_index = (node_id - 1) * 6;
            let mut row_abs_sums = [0.0; 6];
            for local_dof in 0..6 {
                let row = linear_operator_full.row(base_index + local_dof);
                row_abs_sums[local_dof] = row.iter().map(|value| value.abs()).sum::<f64>();
            }
            log::debug!("K row-abs-sums @ node {} = {:?}", node_id, row_abs_sums);
        }
        let base_index_node1 = (1usize - 1) * 6;
        log::debug!(
            "node 1 residual Fx..Mz = {:?}",
            residual_vector_full.view((base_index_node1, 0), (6, 1))
        );
        log::debug!(
            "node 1 spring   Fx..Mz = {:?}",
            spring_reaction_vector_full.view((base_index_node1, 0), (6, 1))
        );

        let total_number_of_degrees_of_freedom = self.compute_num_dofs();
        let mut composed_reaction_vector_full =
            nalgebra::DMatrix::<f64>::zeros(total_number_of_degrees_of_freedom, 1);

        self.visit_unique_supported_nodes(|_node_id, base_index, support| {
            // Translations
            for (axis_label, local_dof) in TRANSLATION_AXES {
                let value = match get_case_insensitive!(support.displacement_conditions, axis_label)
                    .map(|condition| &condition.condition_type)
                {
                    Some(SupportConditionType::Free) => 0.0,
                    Some(SupportConditionType::Spring) => {
                        spring_reaction_vector_full[(base_index + local_dof, 0)]
                    }
                    Some(SupportConditionType::PositiveOnly) => {
                        residual_vector_full[(base_index + local_dof, 0)].max(0.0)
                    }
                    Some(SupportConditionType::NegativeOnly) => {
                        residual_vector_full[(base_index + local_dof, 0)].min(0.0)
                    }
                    None | Some(SupportConditionType::Fixed) => {
                        residual_vector_full[(base_index + local_dof, 0)]
                    }
                };
                composed_reaction_vector_full[(base_index + local_dof, 0)] = value;
            }

            // Rotations
            for (axis_label, local_dof) in ROTATION_AXES {
                let value = match get_case_insensitive!(support.rotation_conditions, axis_label)
                    .map(|condition| &condition.condition_type)
                {
                    Some(SupportConditionType::Free) => 0.0,
                    Some(SupportConditionType::Spring) => {
                        spring_reaction_vector_full[(base_index + local_dof, 0)]
                    }
                    Some(SupportConditionType::PositiveOnly) => {
                        residual_vector_full[(base_index + local_dof, 0)].max(0.0)
                    }
                    Some(SupportConditionType::NegativeOnly) => {
                        residual_vector_full[(base_index + local_dof, 0)].min(0.0)
                    }
                    None | Some(SupportConditionType::Fixed) => {
                        residual_vector_full[(base_index + local_dof, 0)]
                    }
                };
                composed_reaction_vector_full[(base_index + local_dof, 0)] = value;
            }

            Ok(())
        })?; // <- propagate visitor result

        Ok(composed_reaction_vector_full)
    }

    pub fn build_lookup_maps(
        &self,
    ) -> (
        HashMap<u32, &Material>,
        HashMap<u32, &Section>,
        HashMap<u32, &MemberHinge>,
        HashMap<u32, &NodalSupport>,
    ) {
        let material_map: HashMap<u32, &Material> =
            self.materials.iter().map(|m| (m.id, m)).collect();
        let section_map: HashMap<u32, &Section> = self.sections.iter().map(|s| (s.id, s)).collect();
        let memberhinge_map: HashMap<u32, &MemberHinge> = self
            .memberhinges
            .iter()
            .flatten()
            .map(|mh| (mh.id, mh))
            .collect();
        let support_map: HashMap<u32, &NodalSupport> =
            self.nodal_supports.iter().map(|s| (s.id, s)).collect();

        (material_map, section_map, memberhinge_map, support_map)
    }

    fn add_support_springs_to_operator(
        &self,
        global_stiffness_matrix: &mut nalgebra::DMatrix<f64>,
    ) -> Result<(), String> {
        self.visit_unique_supported_nodes(|_node_id, base_index, support| {
            // Translational springs
            for (axis_label, local_dof) in TRANSLATION_AXES {
                if let Some(condition) =
                    get_case_insensitive!(support.displacement_conditions, axis_label)
                {
                    if let SupportConditionType::Spring = condition.condition_type {
                        let stiffness = Self::spring_stiffness_or_error(
                            support.id,
                            axis_label,
                            "displacement",
                            condition.stiffness,
                        )?;
                        global_stiffness_matrix
                            [(base_index + local_dof, base_index + local_dof)] += stiffness;
                    }
                }
            }

            // Rotational springs
            for (axis_label, local_dof) in ROTATION_AXES {
                if let Some(condition) =
                    get_case_insensitive!(support.rotation_conditions, axis_label)
                {
                    if let SupportConditionType::Spring = condition.condition_type {
                        let stiffness = Self::spring_stiffness_or_error(
                            support.id,
                            axis_label,
                            "rotation",
                            condition.stiffness,
                        )?;
                        global_stiffness_matrix
                            [(base_index + local_dof, base_index + local_dof)] += stiffness;
                    }
                }
            }
            Ok(())
        })
    }

    fn build_operator_with_supports(
        &self,
        active_map: &std::collections::HashMap<u32, bool>,
        displacement: Option<&nalgebra::DMatrix<f64>>,
    ) -> Result<nalgebra::DMatrix<f64>, String> {
        let mut k = self.assemble_global_stiffness_matrix(active_map)?;
        if let Some(u) = displacement {
            let k_geo = self.assemble_geometric_stiffness_matrix_with_active(u, active_map)?;
            k += k_geo;
        }
        self.add_support_springs_to_operator(&mut k)?;
        Ok(k)
    }

    fn build_rigid_elimination_partial_using_hinges(&self) -> Result<RigidElimination, String> {
        use crate::models::members::enums::MemberType;
        use nalgebra::DMatrix;
        use std::collections::{HashMap, HashSet};

        // Discover rigid links and collect hinge classification for each
        let assembly_context = AssemblyContext::new(self);

        // Keep your cycle/chain checks
        let mut parent: HashMap<u32, (u32, (f64, f64, f64))> = HashMap::new();

        #[derive(Clone, Copy)]
        struct RigidInfo {
            a: u32,
            b: u32,
            r: (f64, f64, f64),
            modes: AxisModes,
        }
        let mut rigid_elems: Vec<RigidInfo> = Vec::new();

        for set in &self.member_sets {
            for m in &set.members {
                if !matches!(m.member_type, MemberType::Rigid) {
                    continue;
                }

                let a = m.start_node.id; // master (this edge)
                let b = m.end_node.id; // slave  (this edge)

                // Edge vector r = x_b - x_a
                let r = (
                    m.end_node.X - m.start_node.X,
                    m.end_node.Y - m.start_node.Y,
                    m.end_node.Z - m.start_node.Z,
                );
                let l2 = r.0 * r.0 + r.1 * r.1 + r.2 * r.2;
                if l2 < 1.0e-24 {
                    return Err(format!("Rigid member {} has zero length.", m.id));
                }

                // 1) A node can be slave only once (unique master)
                if parent.contains_key(&b) {
                    return Err(format!("Node {} is slave in multiple rigid links.", b));
                }

                // 2) Cycle detection: does 'a' already (transitively) depend on 'b'?
                let mut p = a;
                let mut guard = 0;
                while let Some(&(pp, _)) = parent.get(&p) {
                    if pp == b {
                        return Err(format!("Rigid cycle detected involving node {}.", b));
                    }
                    p = pp;
                    guard += 1;
                    if guard > 100000 {
                        return Err("Rigid chain too long (suspected loop).".to_string());
                    }
                }

                parent.insert(b, (a, r));

                // --- classify hinges for this edge as you already do ---
                let a_h = m
                    .start_hinge
                    .and_then(|id| assembly_context.hinge_by_id.get(&id).copied());
                let b_h = m
                    .end_hinge
                    .and_then(|id| assembly_context.hinge_by_id.get(&id).copied());
                let modes = classify_from_hinges(a_h, b_h);

                rigid_elems.push(RigidInfo { a, b, r, modes });
            }
        }
        // After you have collected `rigid_elems` and built `parent: slave -> (master, r)`
        let n_full = self.compute_num_dofs();

        // Decide which full DOFs are eliminated (only rigid axes at slaves)
        let mut eliminated: HashSet<usize> = HashSet::new();
        for info in &rigid_elems {
            for ax in 0..3 {
                if matches!(info.modes.trans[ax], AxisMode::Rigid) {
                    eliminated.insert(FERS::dof_index(info.b, ax));
                }
                if matches!(info.modes.rot[ax], AxisMode::Rigid) {
                    eliminated.insert(FERS::dof_index(info.b, 3 + ax));
                }
            }
        }

        // Build mapping for retained DOFs (compact)
        let mut full_to_red: HashMap<usize, usize> = HashMap::new();
        let mut red_to_full: Vec<usize> = Vec::new();
        let mut seen: HashSet<usize> = HashSet::new();
        for set in &self.member_sets {
            for m in &set.members {
                for node in [&m.start_node, &m.end_node] {
                    for d in 0..6 {
                        let fi = FERS::dof_index(node.id, d);
                        if eliminated.contains(&fi) {
                            continue;
                        }
                        if seen.insert(fi) {
                            full_to_red.insert(fi, red_to_full.len());
                            red_to_full.push(fi);
                        }
                    }
                }
            }
        }

        let n_red = red_to_full.len();
        let mut s = DMatrix::<f64>::zeros(n_full, n_red);

        // Identity for retained DOFs
        for (fi, &col) in &full_to_red {
            s[(*fi, col)] = 1.0;
        }

        // ---------- NEW: process edges in topological order ----------
        fn depth_of(node: u32, parent: &HashMap<u32, (u32, (f64, f64, f64))>) -> usize {
            let mut d = 0usize;
            let mut p = node;
            while let Some(&(pp, _)) = parent.get(&p) {
                d += 1;
                p = pp;
            }
            d
        }

        // Sort so that masters come before slaves
        let mut edges = rigid_elems.clone();
        edges.sort_by_key(|e| depth_of(e.a, &parent));

        // ---------- NEW: fill eliminated rows by composing MASTER ROWS ----------
        for info in &edges {
            let c = FERS::rigid_map_c(info.r.0, info.r.1, info.r.2);
            for i in 0..6 {
                let is_trans = i < 3;
                let ax = if is_trans { i } else { i - 3 };
                let rigid_here = if is_trans {
                    matches!(info.modes.trans[ax], AxisMode::Rigid)
                } else {
                    matches!(info.modes.rot[ax], AxisMode::Rigid)
                };
                if !rigid_here {
                    continue;
                }

                let row_b = FERS::dof_index(info.b, i);

                // Compose: S[row_b, :] += sum_j C[i,j] * S[row_a_j, :]
                for j in 0..6 {
                    let row_a_j = FERS::dof_index(info.a, j);
                    let coeff = c[(i, j)];
                    if coeff == 0.0 {
                        continue;
                    }
                    for col in 0..n_red {
                        s[(row_b, col)] += coeff * s[(row_a_j, col)];
                    }
                }
            }
        }

        Ok(RigidElimination { s, full_to_red })
    }

    pub fn get_member_count(&self) -> usize {
        self.member_sets.iter().map(|ms| ms.members.len()).sum()
    }

    fn assemble_element_into_global_12(
        global: &mut nalgebra::DMatrix<f64>,
        i0: usize,
        j0: usize,
        ke: &nalgebra::DMatrix<f64>,
    ) {
        debug_assert_eq!(ke.nrows(), 12);
        debug_assert_eq!(ke.ncols(), 12);
        for i in 0..6 {
            for j in 0..6 {
                global[(i0 + i, i0 + j)] += ke[(i, j)];
                global[(i0 + i, j0 + j)] += ke[(i, j + 6)];
                global[(j0 + i, i0 + j)] += ke[(i + 6, j)];
                global[(j0 + i, j0 + j)] += ke[(i + 6, j + 6)];
            }
        }
    }

    pub fn assemble_global_stiffness_matrix(
        &self,
        active_map: &std::collections::HashMap<u32, bool>,
    ) -> Result<nalgebra::DMatrix<f64>, String> {
        use crate::models::members::enums::MemberType;

        self.validate_node_ids()?;
        let assembly_context = AssemblyContext::new(self);

        let number_of_dofs: usize = self.compute_num_dofs();

        let mut global_stiffness_matrix =
            nalgebra::DMatrix::<f64>::zeros(number_of_dofs, number_of_dofs);

        for member_set in &self.member_sets {
            for member in &member_set.members {
                // Build a 12x12 GLOBAL element matrix according to the member behavior
                let element_global_opt: Option<nalgebra::DMatrix<f64>> = match member.member_type {
                    MemberType::Normal => {
                        let Some(_) = member.section else {
                            return Err(format!(
                                "Member {} (Normal) is missing a section id.",
                                member.id
                            ));
                        };

                        // 1) Local base K
                        let k_local_base = member
                            .calculate_stiffness_matrix_3d(
                                &assembly_context.material_by_id,
                                &assembly_context.section_by_id,
                            )
                            .ok_or_else(|| {
                                format!("Member {} failed to build local stiffness.", member.id)
                            })?;

                        // 2) Per-end modes from hinges (LOCAL axes)
                        let a_h = member
                            .start_hinge
                            .and_then(|id| assembly_context.hinge_by_id.get(&id).copied());
                        let b_h = member
                            .end_hinge
                            .and_then(|id| assembly_context.hinge_by_id.get(&id).copied());
                        let (a_trans, a_rot, b_trans, b_rot) = modes_from_single_ends(a_h, b_h);

                        // 3) Apply releases & semi-rigid springs (condensation in LOCAL)
                        let k_local_mod = apply_end_releases_to_local_beam_k(
                            &k_local_base,
                            a_trans,
                            a_rot,
                            b_trans,
                            b_rot,
                        )?;

                        // 4) Transform to GLOBAL
                        let t = member.calculate_transformation_matrix_3d();
                        let k_global = t.transpose() * k_local_mod * t;
                        Some(k_global)
                    }

                    MemberType::Truss => {
                        let mut k_global: nalgebra::Matrix<
                            f64,
                            nalgebra::Dyn,
                            nalgebra::Dyn,
                            nalgebra::VecStorage<f64, nalgebra::Dyn, nalgebra::Dyn>,
                        > = member
                            .calculate_truss_stiffness_matrix_3d(
                                &assembly_context.material_by_id,
                                &assembly_context.section_by_id,
                            )
                            .ok_or_else(|| {
                                format!(
                                    "Member {} (Truss) failed to build truss stiffness.",
                                    member.id
                                )
                            })?;

                        // Optional: translational node-to-ground springs from hinges (LOCAL → GLOBAL)
                        let a_h = member
                            .start_hinge
                            .and_then(|id| assembly_context.hinge_by_id.get(&id).copied());
                        let b_h = member
                            .end_hinge
                            .and_then(|id| assembly_context.hinge_by_id.get(&id).copied());
                        let (a_trans, _a_rot, b_trans, _b_rot) = modes_from_single_ends(a_h, b_h);

                        let k_s_local = build_local_truss_translational_spring_k(a_trans, b_trans);
                        if k_s_local.iter().any(|v| *v != 0.0) {
                            let t = member.calculate_transformation_matrix_3d();
                            let k_s_global = t.transpose() * k_s_local * t;
                            k_global += k_s_global;
                        }

                        Some(k_global)
                    }

                    MemberType::Tension | MemberType::Compression => {
                        let is_active: bool = *active_map.get(&member.id).unwrap_or(&true);
                        if is_active {
                            member.calculate_truss_stiffness_matrix_3d(
                                &assembly_context.material_by_id,
                                &assembly_context.section_by_id,
                            )
                        } else {
                            None
                        }
                    }
                    MemberType::Rigid => None,
                };

                if let Some(element_global) = element_global_opt {
                    let start_index = (member.start_node.id as usize - 1) * 6;
                    let end_index = (member.end_node.id as usize - 1) * 6;

                    Self::assemble_element_into_global_12(
                        &mut global_stiffness_matrix,
                        start_index,
                        end_index,
                        &element_global,
                    );
                }
            }
        }

        Ok(global_stiffness_matrix)
    }

    fn assemble_geometric_stiffness_matrix_with_active(
        &self,
        displacement: &nalgebra::DMatrix<f64>,
        active_map: &std::collections::HashMap<u32, bool>,
    ) -> Result<nalgebra::DMatrix<f64>, String> {
        use crate::models::members::enums::MemberType;
        let assembly_context: AssemblyContext<'_> = AssemblyContext::new(self);
        let n = self.compute_num_dofs();
        let mut k_geo = nalgebra::DMatrix::<f64>::zeros(n, n);

        for member_set in &self.member_sets {
            for member in &member_set.members {
                // Skip rigid: enforced by MPC; contributes no element geometry
                if matches!(member.member_type, MemberType::Rigid) {
                    continue;
                }
                // Skip deactivated tension/compression
                if matches!(
                    member.member_type,
                    MemberType::Tension | MemberType::Compression
                ) && !*active_map.get(&member.id).unwrap_or(&true)
                {
                    continue;
                }

                let n_axial = member.calculate_axial_force_3d(
                    displacement,
                    &assembly_context.material_by_id,
                    &assembly_context.section_by_id,
                );
                let k_g_local_base = member.calculate_geometric_stiffness_matrix_3d(n_axial);

                // Apply same end releases/semi-rigid springs as for material stiffness
                let a_h = member
                    .start_hinge
                    .and_then(|id| assembly_context.hinge_by_id.get(&id).copied());
                let b_h = member
                    .end_hinge
                    .and_then(|id| assembly_context.hinge_by_id.get(&id).copied());
                let (a_trans, a_rot, b_trans, b_rot) = modes_from_single_ends(a_h, b_h);

                let k_g_local_mod = apply_end_releases_to_local_beam_k(
                    &k_g_local_base,
                    a_trans,
                    a_rot,
                    b_trans,
                    b_rot,
                )?;

                // Transform to GLOBAL
                let t = member.calculate_transformation_matrix_3d();
                let k_g_global = t.transpose() * k_g_local_mod * t;

                let i0 = (member.start_node.id as usize - 1) * 6;
                let j0 = (member.end_node.id as usize - 1) * 6;
                Self::assemble_element_into_global_12(&mut k_geo, i0, j0, &k_g_global);
            }
        }
        Ok(k_geo)
    }

    pub fn validate_node_ids(&self) -> Result<(), String> {
        // Collect all node IDs in a HashSet for quick lookup
        let mut node_ids: HashSet<u32> = HashSet::new();

        // Populate node IDs from all members
        for member_set in &self.member_sets {
            for member in &member_set.members {
                node_ids.insert(member.start_node.id);
                node_ids.insert(member.end_node.id);
            }
        }

        // Ensure IDs start at 1 and are consecutive
        let max_id = *node_ids.iter().max().unwrap_or(&0);
        for id in 1..=max_id {
            if !node_ids.contains(&id) {
                return Err(format!(
                    "Node ID {} is missing. Node IDs must be consecutive starting from 1.",
                    id
                ));
            }
        }

        Ok(())
    }

    fn update_active_set(
        &self,
        displacement: &nalgebra::DMatrix<f64>,
        active_map: &mut std::collections::HashMap<u32, bool>,
        axial_slack_tolerance: f64,
        material_map: &std::collections::HashMap<u32, &Material>,
        section_map: &std::collections::HashMap<u32, &Section>,
    ) -> bool {
        use crate::models::members::enums::MemberType;

        let mut changed = false;
        for member_set in &self.member_sets {
            for member in &member_set.members {
                match member.member_type {
                    MemberType::Tension => {
                        let n = member.calculate_axial_force_3d(
                            displacement,
                            material_map,
                            section_map,
                        );
                        let should_be_active = n >= -axial_slack_tolerance;
                        if active_map.get(&member.id).copied().unwrap_or(true) != should_be_active {
                            active_map.insert(member.id, should_be_active);
                            changed = true;
                        }
                    }
                    MemberType::Compression => {
                        let n = member.calculate_axial_force_3d(
                            displacement,
                            material_map,
                            section_map,
                        );
                        let should_be_active = n <= axial_slack_tolerance;
                        if active_map.get(&member.id).copied().unwrap_or(true) != should_be_active {
                            active_map.insert(member.id, should_be_active);
                            changed = true;
                        }
                    }
                    _ => {}
                }
            }
        }
        changed
    }

    fn compute_num_dofs(&self) -> usize {
        let max_node = self
            .member_sets
            .iter()
            .flat_map(|ms| ms.members.iter())
            .flat_map(|m| vec![m.start_node.id, m.end_node.id])
            .max()
            .unwrap_or(0) as usize;
        max_node * 6
    }

    pub fn assemble_load_vector_for_combination(
        &self,
        combination_id: u32,
    ) -> Result<DMatrix<f64>, String> {
        let num_dofs = self.compute_num_dofs();
        let mut f_comb = DMatrix::<f64>::zeros(num_dofs, 1);

        // Find the combination by its load_combination_id field
        let combo = self
            .load_combinations
            .iter()
            .find(|lc| lc.load_combination_id == combination_id)
            .ok_or_else(|| format!("LoadCombination {} not found.", combination_id))?;

        // Now iterate the HashMap<u32, f64>
        for (&case_id, &factor) in &combo.load_cases_factors {
            let f_case = self.assemble_load_vector_for_case(case_id);
            f_comb += f_case * factor;
        }

        Ok(f_comb)
    }

    fn dof_index(node_id: u32, local_dof: usize) -> usize {
        (node_id as usize - 1) * 6 + local_dof
    }

    fn rigid_map_c(r_x: f64, r_y: f64, r_z: f64) -> nalgebra::SMatrix<f64, 6, 6> {
        use nalgebra::{Matrix3, SMatrix};

        let i3 = Matrix3::<f64>::identity();
        let skew = Matrix3::<f64>::new(0.0, -r_z, r_y, r_z, 0.0, -r_x, -r_y, r_x, 0.0);

        // Top-left I, top-right Skew(r); bottom-left 0, bottom-right I
        let mut c = SMatrix::<f64, 6, 6>::zeros();
        c.fixed_view_mut::<3, 3>(0, 0).copy_from(&i3);
        c.fixed_view_mut::<3, 3>(0, 3).copy_from(&(-skew));
        c.fixed_view_mut::<3, 3>(3, 3).copy_from(&i3);
        c
    }

    fn reduce_system(
        k_full: &DMatrix<f64>,
        f_full: &DMatrix<f64>,
        elim: &RigidElimination,
    ) -> (DMatrix<f64>, DMatrix<f64>) {
        let k_red = elim.s.transpose() * k_full * &elim.s;
        let f_red = elim.s.transpose() * f_full;
        (k_red, f_red)
    }

    fn expand_solution(elim: &RigidElimination, u_red: &DMatrix<f64>) -> DMatrix<f64> {
        &elim.s * u_red
    }

    fn constrain_single_dof(
        &self,
        k_global: &mut DMatrix<f64>,
        rhs: &mut DMatrix<f64>,
        dof_index: usize,
        prescribed: f64,
    ) {
        for j in 0..k_global.ncols() {
            k_global[(dof_index, j)] = 0.0;
        }
        for i in 0..k_global.nrows() {
            k_global[(i, dof_index)] = 0.0;
        }
        k_global[(dof_index, dof_index)] = 1.0;
        rhs[(dof_index, 0)] = prescribed;
    }

    fn apply_boundary_conditions_reduced(
        &self,
        elim: &RigidElimination,
        k_red: &mut DMatrix<f64>,
        rhs_red: &mut DMatrix<f64>,
    ) -> Result<(), String> {
        let support_map: HashMap<u32, &NodalSupport> =
            self.nodal_supports.iter().map(|s| (s.id, s)).collect();

        for ms in &self.member_sets {
            for m in &ms.members {
                for node in [&m.start_node, &m.end_node] {
                    let Some(sid) = node.nodal_support else {
                        continue;
                    };
                    let Some(s) = support_map.get(&sid) else {
                        continue;
                    };

                    let base_full = (node.id as usize - 1) * 6;

                    for (axis, dof) in TRANSLATION_AXES {
                        let cond = s
                            .displacement_conditions
                            .get(axis)
                            .or_else(|| s.displacement_conditions.get(&axis.to_ascii_lowercase()));
                        let is_fixed = cond
                            .map(|c| matches!(c.condition_type, SupportConditionType::Fixed))
                            .unwrap_or(true);
                        if is_fixed {
                            let fi = base_full + dof;
                            let Some(ri) = elim.full_to_red.get(&fi).copied() else {
                                return Err(format!(
                                    "Support at slave node {} (DOF {}). Not supported yet.",
                                    node.id, axis
                                ));
                            };
                            self.constrain_single_dof(k_red, rhs_red, ri, 0.0);
                        }
                    }

                    for (axis, dof) in ROTATION_AXES {
                        let cond = s
                            .rotation_conditions
                            .get(axis)
                            .or_else(|| s.rotation_conditions.get(&axis.to_ascii_lowercase()));
                        let is_fixed = cond
                            .map(|c| matches!(c.condition_type, SupportConditionType::Fixed))
                            .unwrap_or(true);
                        if is_fixed {
                            let fi = base_full + dof;
                            let Some(ri) = elim.full_to_red.get(&fi).copied() else {
                                return Err(format!(
                                    "Support at slave node {} (Rot {}). Not supported yet.",
                                    node.id, axis
                                ));
                            };
                            self.constrain_single_dof(k_red, rhs_red, ri, 0.0);
                        }
                    }
                }
            }
        }
        Ok(())
    }

    pub fn assemble_load_vector_for_case(&self, load_case_id: u32) -> DMatrix<f64> {
        let num_dofs = self.compute_num_dofs();
        let mut f = DMatrix::<f64>::zeros(num_dofs, 1);

        if let Some(load_case) = self.load_cases.iter().find(|lc| lc.id == load_case_id) {
            assemble_nodal_loads(load_case, &mut f);
            assemble_nodal_moments(load_case, &mut f);
            assemble_distributed_loads(load_case, &self.member_sets, &mut f, load_case_id);
        }
        f
    }

    fn init_active_map_tie_comp(&self) -> HashMap<u32, bool> {
        let mut map = HashMap::new();
        for ms in &self.member_sets {
            for member in &ms.members {
                if matches!(
                    member.member_type,
                    MemberType::Tension | MemberType::Compression
                ) {
                    map.insert(member.id, true);
                }
            }
        }
        map
    }

    fn solve_first_order_common(
        &mut self,
        load_vector_full: nalgebra::DMatrix<f64>,
        name: String,
        result_type: ResultType,
    ) -> Result<Results, String> {
        let tolerance: f64 = self.settings.analysis_option.tolerance;
        let max_it: usize = self.settings.analysis_option.max_iterations.unwrap_or(20) as usize;
        let axial_slack_tolerance: f64 = AXIAL_SLACK_TOLERANCE_DEFAULT;

        let mut active_map = self.init_active_map_tie_comp();
        let mut u_full = nalgebra::DMatrix::<f64>::zeros(self.compute_num_dofs(), 1);

        let assembly_context: AssemblyContext<'_> = AssemblyContext::new(self);

        let elim = self.build_rigid_elimination_partial_using_hinges()?;

        let mut converged = false;
        for _iter in 0..max_it {
            let k_full = self.build_operator_with_supports(&active_map, None)?;

            let (mut k_red, mut f_red) = Self::reduce_system(&k_full, &load_vector_full, &elim);

            // apply BCs on the REDUCED system
            self.apply_boundary_conditions_reduced(&elim, &mut k_red, &mut f_red)?;

            // solve reduced system and expand to full DOFs
            let u_red = k_red.lu().solve(&f_red).ok_or_else(|| {
                "Reduced stiffness matrix is singular or near-singular".to_string()
            })?;
            let u_full_new = Self::expand_solution(&elim, &u_red);

            // active-set update (Tension/Compression) uses FULL displacement
            let delta = &u_full_new - &u_full;
            u_full = u_full_new;

            let changed = self.update_active_set(
                &u_full,
                &mut active_map,
                axial_slack_tolerance,
                &assembly_context.material_by_id,
                &assembly_context.section_by_id,
            );

            if delta.norm() < tolerance && !changed {
                converged = true;
                break;
            }
        }

        if !converged {
            return Err(format!(
                "Active-set iteration did not converge within {} iterations",
                max_it
            ));
        }

        // reactions from the linear operator in FULL space
        let composed_support_reaction_vector_full =
            self.compose_support_reaction_vector(&active_map, &u_full, &load_vector_full)?;

        let results = self
            .build_and_store_results(
                name.clone(),
                result_type.clone(),
                &u_full,
                &composed_support_reaction_vector_full,
            )?
            .clone();
        Ok(results)
    }

    fn solve_second_order_common(
        &mut self,
        load_vector_full: nalgebra::DMatrix<f64>,
        name: String,
        result_type: ResultType,
        max_iterations: usize,
        tolerance: f64,
    ) -> Result<Results, String> {
        let axial_slack_tolerance: f64 = AXIAL_SLACK_TOLERANCE_DEFAULT;

        let mut active_map = self.init_active_map_tie_comp();
        let n_full = self.compute_num_dofs();
        let mut u_full = nalgebra::DMatrix::<f64>::zeros(n_full, 1);

        let assembly_context: AssemblyContext<'_> = AssemblyContext::new(self);

        let elim = self.build_rigid_elimination_partial_using_hinges()?;

        let mut converged = false;
        for _iter in 0..max_iterations {
            let k_tangent_full = self.build_operator_with_supports(&active_map, Some(&u_full))?;

            let (k_red, f_red) = Self::reduce_system(&k_tangent_full, &load_vector_full, &elim);

            // Current reduced displacement u_r = Sᵀ u
            let mut u_red = elim.s.transpose() * &u_full;

            // Residual in reduced space: r_r = K_r u_r − f_r
            let mut r_red = &k_red * &u_red - &f_red;

            // Apply BCs in REDUCED space, then solve for Δu_r from K_r Δu_r = −r_r
            let mut k_treated = k_red.clone();
            self.apply_boundary_conditions_reduced(&elim, &mut k_treated, &mut r_red)?;
            let delta_red = k_treated
                .lu()
                .solve(&(-&r_red))
                .ok_or_else(|| "Tangent stiffness singular.".to_string())?;

            // Update and expand back to full space
            u_red += &delta_red;
            let u_full_new = Self::expand_solution(&elim, &u_red);

            let delta_full = &u_full_new - &u_full;
            u_full = u_full_new;

            // Active-set update (Tension/Compression) using FULL displacement
            let changed = self.update_active_set(
                &u_full,
                &mut active_map,
                axial_slack_tolerance,
                &assembly_context.material_by_id,
                &assembly_context.section_by_id,
            );

            if delta_full.norm() < tolerance && !changed {
                converged = true;
                break;
            }
        }

        if !converged {
            return Err(format!(
                "Newton–Raphson with active set did not converge in {} iterations",
                max_iterations
            ));
        }

        // Reactions from the linear operator (no geometric part), FULL space
        let composed_support_reaction_vector_full =
            self.compose_support_reaction_vector(&active_map, &u_full, &load_vector_full)?;

        let results = self
            .build_and_store_results(
                name.clone(),
                result_type.clone(),
                &u_full,
                &composed_support_reaction_vector_full,
            )?
            .clone();
        Ok(results)
    }

    pub fn solve_for_load_case(&mut self, load_case_id: u32) -> Result<Results, String> {
        let load_vector = self.assemble_load_vector_for_case(load_case_id);
        let load_case = self
            .load_cases
            .iter()
            .find(|lc| lc.id == load_case_id)
            .ok_or_else(|| format!("LoadCase {} not found.", load_case_id))?;
        self.solve_first_order_common(
            load_vector,
            load_case.name.clone(),
            ResultType::Loadcase(load_case_id),
        )
    }
    pub fn solve_for_load_case_second_order(
        &mut self,
        load_case_id: u32,
        max_iterations: usize,
        tolerance: f64,
    ) -> Result<Results, String> {
        let load_vector = self.assemble_load_vector_for_case(load_case_id);
        let load_case = self
            .load_cases
            .iter()
            .find(|lc| lc.id == load_case_id)
            .ok_or_else(|| format!("LoadCase {} not found.", load_case_id))?;
        self.solve_second_order_common(
            load_vector,
            load_case.name.clone(),
            ResultType::Loadcase(load_case_id),
            max_iterations,
            tolerance,
        )
    }
    pub fn solve_for_load_combination(&mut self, combination_id: u32) -> Result<Results, String> {
        let load_vector = self.assemble_load_vector_for_combination(combination_id)?;
        let combo = self
            .load_combinations
            .iter()
            .find(|lc| lc.load_combination_id == combination_id)
            .ok_or_else(|| format!("LoadCombination {} not found.", combination_id))?;
        self.solve_first_order_common(
            load_vector,
            combo.name.clone(),
            ResultType::Loadcombination(combination_id),
        )
    }

    pub fn solve_for_load_combination_second_order(
        &mut self,
        combination_id: u32,
        max_iterations: usize,
        tolerance: f64,
    ) -> Result<Results, String> {
        let load_vector = self.assemble_load_vector_for_combination(combination_id)?;
        let combo = self
            .load_combinations
            .iter()
            .find(|lc| lc.load_combination_id == combination_id)
            .ok_or_else(|| format!("LoadCombination {} not found.", combination_id))?;
        self.solve_second_order_common(
            load_vector,
            combo.name.clone(),
            ResultType::Loadcombination(combination_id),
            max_iterations,
            tolerance,
        )
    }

    pub fn build_and_store_results(
        &mut self,
        name: String,
        result_type: ResultType,
        displacement_vector: &DMatrix<f64>,
        global_reaction_vector: &DMatrix<f64>,
    ) -> Result<&Results, String> {
        // Build the three main maps
        let member_results =
            compute_member_results_from_displacement(self, &result_type, displacement_vector);
        let displacement_nodes = extract_displacements(self, displacement_vector);
        let reaction_nodes = extract_reaction_nodes(self, global_reaction_vector);

        // Summaries
        let total_members: usize = self.member_sets.iter().map(|set| set.members.len()).sum();
        let total_supports: usize = self.nodal_supports.len();

        let results = Results {
            name: name.clone(),
            result_type: result_type.clone(),
            displacement_nodes,
            reaction_nodes,
            member_results,
            summary: ResultsSummary {
                total_displacements: total_members,
                total_reaction_forces: total_supports,
                total_member_forces: total_members,
            },
            unity_checks: None,
        };

        // Insert into bundle
        let bundle = self.results.get_or_insert_with(|| ResultsBundle {
            loadcases: BTreeMap::new(),
            loadcombinations: BTreeMap::new(),
            unity_checks_overview: None,
        });

        match result_type {
            ResultType::Loadcase(_) => {
                if bundle.loadcases.insert(name.clone(), results).is_some() {
                    return Err(format!("Duplicate load case name `{}`", name));
                }
                Ok(bundle.loadcases.get(&name).unwrap())
            }
            ResultType::Loadcombination(_) => {
                if bundle
                    .loadcombinations
                    .insert(name.clone(), results)
                    .is_some()
                {
                    return Err(format!("Duplicate load combination name `{}`", name));
                }
                Ok(bundle.loadcombinations.get(&name).unwrap())
            }
        }
    }

    pub fn save_results_to_json(fers_data: &FERS, file_path: &str) -> Result<(), std::io::Error> {
        let json = serde_json::to_string_pretty(fers_data)?;
        std::fs::write(file_path, json)
    }
}
