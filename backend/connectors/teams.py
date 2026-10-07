from typing import List, Dict


def get_mock_teams_items() -> List[Dict]:
    """
    Returns the Microsoft Teams items currently available to ContextFlow.

    This is the prototype connector.
    Later, this function can be replaced with an approved
    Microsoft Graph / enterprise Teams connector without
    changing the ContextFlow task engine.
    """

    return [
        {
            "source": "Microsoft Teams",
            "source_id": "cloud",
            "title": "Cloud Fundamentals Assessment",
            "content": (
                "Please complete the Cloud Fundamentals assessment "
                "by October 18."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/teams?message=cloud"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/cloud-assessment"
            ),
        },
        {
            "source": "Microsoft Teams",
            "source_id": "welcome",
            "title": "Welcome to Cloud Operations Team",
            "content": (
                "Welcome to the Cloud Operations Team. "
                "Please review the onboarding information."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/teams?message=welcome"
            ),
            "action_url": None,
        },
        {
            "source": "Microsoft Teams",
            "source_id": "priority-demo",
            "title": "URGENT Production Access Issue",
            "content": (
                "Please resolve the production access issue "
                "by October 8. This is urgent and requires immediate action."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/teams?message=priority-demo"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/cloud-assessment"
            ),
        },
        {
            "source": "Microsoft Teams",
            "source_id": "scheduler-teams-demo-001",
            "title": "Complete Infrastructure Onboarding",
            "content": (
                "Please complete the Infrastructure Onboarding checklist "
                "by November 2. This task was newly assigned in Teams."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/teams?message=scheduler-teams-demo-001"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/cloud-assessment"
            ),
        },
    ]


def get_new_teams_items() -> List[Dict]:
    """
    Returns Teams items that ContextFlow can process.

    The synchronization layer prevents duplicate task creation
    using source + source_id.
    """

    return get_mock_teams_items()