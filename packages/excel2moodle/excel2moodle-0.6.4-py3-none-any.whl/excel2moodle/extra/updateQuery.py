"""This module provides functions to query the GitLab API for project information."""

import json
import sys
import urllib.request


def get_latest_tag(project_id: str) -> str | None:
    """Queries the GitLab API for the latest tag of a project.

    Args:
        project_id: The URL-encoded project ID (e.g., 'jbosse3%2Fexcel2moodle').

    Returns:
        The name of the latest tag.

    """
    url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/tags"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                if data:
                    return data[0]["name"]
    except urllib.error.URLError as e:
        print(f"Error fetching latest tag: {e}", file=sys.stderr)
    return None


def get_changelog(project_id: str, branch: str = "master") -> str:
    """Queries the GitLab API for the content of the CHANGELOG.md file.

    Args:
        project_id: The URL-encoded project ID (e.g., 'jbosse3%2Fexcel2moodle').
        branch: The branch to get the file from.

    Returns:
        The content of the CHANGELOG.md file.

    """
    url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/files/CHANGELOG.md/raw?ref={branch}"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return response.read().decode()
    except urllib.error.URLError as e:
        print(f"Error fetching changelog: {e}", file=sys.stderr)
    return ""
