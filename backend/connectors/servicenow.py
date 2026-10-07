from typing import List, Dict


def get_mock_servicenow_items() -> List[Dict]:
    """
    Returns the ServiceNow items currently available to ContextFlow.

    This is the prototype connector.
    Later, this can be replaced with an approved
    enterprise ServiceNow API connector.
    """

    return [
        {
            "source": "ServiceNow",
            "source_id": "INC0012847",
            "title": "Infrastructure Access Request",
            "content": (
                "Infrastructure access is required for the new employee. "
                "Please complete the access request by October 14."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/servicenow?ticket=access"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/servicenow-form"
            ),
        },
        {
            "source": "ServiceNow",
            "source_id": "REQ0021745",
            "title": "Infrastructure Monitoring Access",
            "content": (
                "Please review and approve the infrastructure monitoring "
                "access request by October 16."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/servicenow?ticket=monitoring"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/servicenow-form"
            ),
        },
        {
            "source": "ServiceNow",
            "source_id": "CHG0009182",
            "title": "Cloud Operations Access",
            "content": (
                "Please complete the cloud operations access change "
                "request by October 20."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/servicenow?ticket=cloud"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/servicenow-form"
            ),
        },
        {
            "source": "ServiceNow",
            "source_id": "priority-demo",
            "title": "CRITICAL Production Infrastructure Incident",
            "content": (
                "A critical production infrastructure incident requires "
                "immediate action. Resolve the incident by October 8."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/servicenow?ticket=priority-demo"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/servicenow-form"
            ),
        },
        {
            "source": "ServiceNow",
            "source_id": "scheduler-servicenow-demo-001",
            "title": "Complete Cloud Infrastructure Change",
            "content": (
                "Please complete the cloud infrastructure change request "
                "by November 5. This change was newly assigned."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/servicenow?ticket=scheduler-servicenow-demo-001"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/servicenow-form"
            ),
        },
    ]


def get_new_servicenow_items() -> List[Dict]:
    """
    Returns ServiceNow items that ContextFlow can process.

    The synchronization layer prevents duplicate task creation
    using source + source_id.
    """

    return get_mock_servicenow_items()