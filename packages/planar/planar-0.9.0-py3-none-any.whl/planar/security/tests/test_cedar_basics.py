from cedarpy import Decision, format_policies, is_authorized


def test_cedar_permissions():
    # Define entities
    entities = [
        {
            "uid": {"__entity": {"type": "Principal", "id": "alice"}},
            "attrs": {},
            "parents": [],
        },
        {
            "uid": {"__entity": {"type": "Document", "id": "doc1"}},
            "attrs": {},
            "parents": [],
        },
    ]

    # Initialize the Cedar policy service
    policy = """
    permit (
        principal,
        action == Action::"Run",
        resource
    );
    """
    formatted_policy = format_policies(policy)
    print(formatted_policy)

    # Create a simple request
    request = {
        "principal": 'Principal::"alice"',
        "action": 'Action::"Run"',
        "resource": 'Document::"doc1"',
    }

    # Test the authorization
    result = is_authorized(request, policy, entities)
    assert result.decision == Decision.Allow, (
        "Cedar works and basic permission should be allowed"
    )
