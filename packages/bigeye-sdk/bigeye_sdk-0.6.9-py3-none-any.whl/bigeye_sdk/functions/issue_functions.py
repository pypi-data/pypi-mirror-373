from datetime import datetime

from bigeye_sdk.generated.com.bigeye.models.generated import Issue


def get_issue_first_detected_at(issue: Issue) -> str:
    """
    Returns the time the issue was first detected.
    Args:
        issue: an Issue object

    Returns: a datetime object created from the Issue.

    """
    return datetime.fromtimestamp(issue.opened_time_seconds).strftime('%Y-%m-%d %H:%M:%S')
