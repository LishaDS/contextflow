from typing import List, Dict


def get_mock_outlook_items() -> List[Dict]:
    return [
        {
            "source": "Outlook",
            "source_id": "security",
            "title": "Mandatory Security Training",
            "content": (
                "You must complete the mandatory security training "
                "by October 10. This training is required for all employees."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/outlook?email=security"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/security-training"
            ),
        },
        {
            "source": "Outlook",
            "source_id": "epfo",
            "title": "EPFO Nominee Declaration Required",
            "content": (
                "Please complete your EPFO nominee declaration "
                "by October 12."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/outlook?email=epfo"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/epfo"
            ),
        },
        {
            "source": "Outlook",
            "source_id": "access",
            "title": "Application Access Request",
            "content": (
                "Please complete the application access request "
                "by October 15."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/outlook?email=access"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/access-request-form"
            ),
        },
        {
            "source": "Outlook",
            "source_id": "benefits",
            "title": "Employee Benefits Enrollment",
            "content": (
                "Please complete your employee benefits enrollment "
                "by October 15."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/outlook?email=benefits"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/benefits-form"
            ),
        },
        {
            "source": "Outlook",
            "source_id": "demo-new-task",
            "title": "Complete Cloud Security Workshop",
            "content": (
                "Please complete the cloud security workshop "
                "by October 20."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/outlook?email=demo-new-task"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/security-training"
            ),
        },
        {
            "source": "Outlook",
            "source_id": "priority-demo",
            "title": "URGENT Security Access Request",
            "content": (
                "Please complete this security access request "
                "by October 8. This is urgent and required immediately."
            ),
            "priority": "critical",
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/outlook?email=priority-demo"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/access-request-form"
            ),
        },
        {
            "source": "Outlook",
            "source_id": "automatic-demo-001",
            "title": "Complete Zero Trust Security Workshop",
            "content": (
                "Please complete the Zero Trust Security Workshop "
                "by October 25. This training is required for the "
                "Cloud Operations onboarding process."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/outlook?email=automatic-demo-001"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/security-training"
            ),
        },
        {
            "source": "Outlook",
            "source_id": "scheduler-demo-002",
            "title": "Complete Cloud Operations Training",
            "content": (
                "Please complete the Cloud Operations Training "
                "by October 30. This task was newly assigned."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/outlook?email=scheduler-demo-002"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/security-training"
            ),
        },
        {
            "source": "Outlook",
            "source_id": "notification-test-003",
            "title": "Complete New Employee Setup",
            "content": (
                "Please complete the New Employee Setup "
                "by November 10. This is a newly assigned onboarding task."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/outlook?email=notification-test-003"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/security-training"
            ),
        },
        {
            "source": "Outlook",
            "source_id": "scheduler-final-004",
            "title": "Complete Final Automation Test",
            "content": (
                "Please complete the Final Automation Test "
                "by November 15. This is a newly assigned task."
            ),
            "source_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/outlook?email=scheduler-final-004"
            ),
            "action_url": (
                "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/"
                "mock/security-training"
            ),
        },
    ]


def get_new_outlook_items() -> List[Dict]:
    return get_mock_outlook_items()