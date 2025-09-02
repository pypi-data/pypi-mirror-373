use crate::models::members::member::Member;
use crate::models::nodes::node::Node;

#[cfg(test)]
mod member_tests {
    use super::*;

    fn create_test_member() -> Member {
        let start_node = Node {
            X: 0.0,
            Y: 0.0,
            Z: 0.0,
            // Add other required fields
        };
        let end_node = Node {
            X: 3.0,
            Y: 4.0,
            Z: 0.0,
            // Add other required fields
        };
        
        Member {
            id: 1,
            start_node,
            end_node,
            section: 1,
            rotation_angle: 0.0,
            start_hinge: None,
            end_hinge: None,
            classification: "test".to_string(),
            weight: 0.0,
            chi: None,
            reference_member: None,
            reference_node: None,
            member_type: MemberType::Beam, // Make sure to import MemberType
        }
    }

    #[test]
    fn test_calculate_length() {
        let member = create_test_member();
        assert_eq!(member.calculate_length(), 5.0);
    }


}