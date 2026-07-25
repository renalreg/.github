import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser


def required_environment(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not set")
    return value


def load_event(path):
    with open(path, encoding="utf-8") as event_file:
        return json.load(event_file)


def text_node(value, marks=None):
    node = {"type": "text", "text": value}
    if marks:
        node["marks"] = marks
    return node


def inline_content(value):
    content = []
    position = 0
    pattern = re.compile(r"!?\[([^]]*)\]\((https?://[^)\s]+)(?:\s+\"[^\"]*\")?\)")

    for match in pattern.finditer(value):
        before = value[position:match.start()]
        if before:
            content.append(text_node(before.replace("**", "").replace("__", "")))

        label = match.group(1) or match.group(2)
        content.append(
            text_node(label, [{"type": "link", "attrs": {"href": match.group(2)}}])
        )
        position = match.end()

    remaining = value[position:]
    if remaining:
        content.append(text_node(remaining.replace("**", "").replace("__", "")))

    return content or [text_node(value)]


def paragraph(value):
    return {"type": "paragraph", "content": inline_content(value)}


class GithubBodyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.links = []

    def newline(self):
        if self.parts and not self.parts[-1].endswith("\n"):
            self.parts.append("\n")

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag in {"p", "div", "blockquote", "details"}:
            self.newline()
        elif tag == "br":
            self.newline()
        elif tag == "li":
            self.newline()
            self.parts.append("- ")
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.newline()
            self.parts.append(f"{'#' * int(tag[1])} ")
        elif tag == "summary":
            self.newline()
            self.parts.append("### ")
        elif tag == "a":
            self.parts.append("[")
            self.links.append(attributes.get("href", ""))
        elif tag == "img":
            alt = attributes.get("alt", "Image")
            source = attributes.get("src", "")
            self.parts.append(f"![{alt}]({source})" if source else alt)
        elif tag == "code":
            self.parts.append("`")

    def handle_endtag(self, tag):
        if tag in {"p", "div", "blockquote", "details", "li"}:
            self.newline()
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6", "summary"}:
            self.newline()
        elif tag == "a":
            href = self.links.pop() if self.links else ""
            self.parts.append(f"]({href})" if href else "]")
        elif tag == "code":
            self.parts.append("`")

    def handle_data(self, data):
        self.parts.append(data)

    def text(self):
        return "".join(self.parts)


def body_to_adf(body):
    parser = GithubBodyParser()
    parser.feed(body)
    nodes = []
    bullet_items = []

    def flush_bullets():
        if bullet_items:
            nodes.append({"type": "bulletList", "content": list(bullet_items)})
            bullet_items.clear()

    for raw_line in parser.text().replace("\r", "").split("\n"):
        line = raw_line.strip()
        if not line:
            flush_bullets()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_bullets()
            nodes.append(
                {
                    "type": "heading",
                    "attrs": {"level": len(heading.group(1))},
                    "content": inline_content(heading.group(2)),
                }
            )
        elif line.startswith(("- ", "* ")):
            bullet_items.append(
                {
                    "type": "listItem",
                    "content": [paragraph(line[2:].strip())],
                }
            )
        elif re.fullmatch(r"[-*_]{3,}", line):
            flush_bullets()
            nodes.append({"type": "rule"})
        else:
            flush_bullets()
            nodes.append(paragraph(line.removeprefix("> ")))

    flush_bullets()
    return nodes or [paragraph("No pull request description was provided.")]


def build_description(repository, pull_request):
    body = pull_request.get("body") or "No pull request description was provided."
    pull_request_url = pull_request["html_url"]
    return {
        "type": "doc",
        "version": 1,
        "content": [
            paragraph(f"Dependabot opened pull request #{pull_request['number']} in {repository}."),
            {
                "type": "paragraph",
                "content": [
                    text_node("Pull request: "),
                    text_node(
                        pull_request_url,
                        [{"type": "link", "attrs": {"href": pull_request_url}}],
                    ),
                ],
            },
            paragraph(f"Dependency update: {pull_request['title']}"),
            {"type": "rule"},
            *body_to_adf(body),
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
