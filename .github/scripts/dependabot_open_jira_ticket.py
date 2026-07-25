import base64
import json
import os
import sys
import urllib.error
import urllib.request


def required_environment(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not set")
    return value


def load_event(path):
    with open(path, encoding="utf-8") as event_file:
        return json.load(event_file)


def text_node(value):
    return {"type": "text", "text": value}


def paragraph(value):
    return {"type": "paragraph", "content": [text_node(value)]}


def build_description(repository, pull_request):
    body = pull_request.get("body") or "No pull request description was provided."
    return {
        "type": "doc",
        "version": 1,
        "content": [
            paragraph(f"Dependabot opened pull request #{pull_request['number']} in {repository}."),
            paragraph(f"Pull request: {pull_request['html_url']}"),
            paragraph(f"Dependency update: {pull_request['title']}"),
            {"type": "rule"},
            {"type": "codeBlock", "content": [text_node(body)]},
        ],
    }


def build_issue(event, project_code, issue_type, component):
    pull_request = event.get("pull_request")
    if not pull_request:
        raise RuntimeError("The GitHub event does not contain pull_request data")

    actor = pull_request.get("user", {}).get("login")
    if actor != "dependabot[bot]":
        raise RuntimeError(f"Pull request author is {actor!r}, not dependabot[bot]")

    action = event.get("action")
    if action and action != "opened":
        raise RuntimeError(f"Pull request action is {action!r}, not 'opened'")

    repository = event.get("repository", {}).get("full_name") or required_environment(
        "GITHUB_REPOSITORY"
    )
    number = pull_request.get("number") or event.get("number")
    pull_request["number"] = number
    summary = f"[Dependabot] {repository}#{number}: {pull_request['title']}"[:255]

    fields = {
        "project": {"key": project_code},
        "summary": summary,
        "description": build_description(repository, pull_request),
        "issuetype": {"name": issue_type},
    }
    if component:
        fields["components"] = [{"name": component}]

    return {"fields": fields}


def create_jira_issue(base_url, email, api_token, issue):
    credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/rest/api/3/issue",
        data=json.dumps(issue).encode(),
        headers={
            "Accept": "application/json",
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Jira returned HTTP {error.code} while creating the issue: {response_body}"
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Unable to connect to Jira: {error.reason}") from error


def main():
    event = load_event(required_environment("GITHUB_EVENT_PATH"))
    action = event.get("action")
    if action != "opened":
        print(f"::notice::Skipping pull request action {action!r}; only 'opened' creates a Jira issue")
        return

    base_url = required_environment("JIRA_BASE_URL")
    issue = build_issue(
        event,
        required_environment("JIRA_PROJECT_CODE"),
        os.environ.get("JIRA_ISSUE_TYPE", "Bug").strip() or "Bug",
        os.environ.get("JIRA_COMPONENT", "Dependabot").strip(),
    )
    result = create_jira_issue(
        base_url,
        required_environment("JIRA_USER_EMAIL"),
        required_environment("JIRA_API_TOKEN"),
        issue,
    )

    issue_key = result.get("key")
    if not issue_key:
        raise RuntimeError(f"Jira response did not contain an issue key: {result}")

    print(f"::notice::Created Jira issue {issue_key}")
    print(f"{base_url.rstrip('/')}/browse/{issue_key}")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"::error::{error}", file=sys.stderr)
        sys.exit(1)
