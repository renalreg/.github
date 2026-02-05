#!/usr/bin/env python3
import os
import re
from pathlib import Path
import yaml

# -----------------------
# Config
# -----------------------
README_FILE = Path(r".\README.md")
# Look for <badges> ... </badges> block in README
BADGES_TAG_RE = re.compile(r"<div class=\"badges\">.*?</div>", re.DOTALL)
BADGES_CONFIG_FILE = Path(r".\badges.yml")

WORKFLOWS_DIR = Path(r".\.github\workflows")
PYPI_PACKAGE_NAME = os.environ.get("PYPI_PACKAGE_NAME", None)


def detect_workflows():
    if not WORKFLOWS_DIR.exists():
        return []

    workflows = []
    for wf in WORKFLOWS_DIR.glob("*.yml"):
        name = wf.stem
        workflows.append(name)
    return workflows


def load_optional_badges():
    if not BADGES_CONFIG_FILE.exists():
        return [], None

    with BADGES_CONFIG_FILE.open("r") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing {BADGES_CONFIG_FILE}: {e}")
            return [], None

    # Expecting a list of badge strings under "badges"
    if isinstance(data, dict) and "badges" in data and isinstance(data["badges"], list):
        return data["badges"], data
    return [], data


def build_badge_block(repo_full_name):
    badges = []

    workflows = detect_workflows()
    for wf_name in workflows:
        if wf_name == "python_test.yml":
            badge_html = ""
        else:
            continue

        badges.append(badge_html)

    # Add static badges

    hardcoded_badges, data = load_optional_badges()
    standard_badges = {
        "issues": f"[![Issues](https://img.shields.io/github/issues/{repo_full_name})](https://github.com/{repo_full_name}/issues)",
        "dependencies": f"[![Dependencies](https://img.shields.io/librariesio/github/{repo_full_name})](https://libraries.io/github/{repo_full_name})",
        "vulnerabilities": f"[![Vulnerabilities](https://img.shields.io/snyk/vulnerabilities/github/{repo_full_name})](https://snyk.io/test/github/{repo_full_name})",
        "license": f"[![License](https://img.shields.io/github/license/{repo_full_name})](https://github.com/{repo_full_name}/blob/main/LICENSE)",
        "stars": f"[![Stars](https://img.shields.io/github/stars/{repo_full_name})](https://github.com/{repo_full_name}/stargazers)",
        "codecov": f"[![Coverage](https://codecov.io/gh/{repo_full_name}/branch/main/graph/badge.svg)](https://codecov.io/gh/{repo_full_name})",
    }
    if data:
        selected_standard_badges = [
            value
            for key, value in standard_badges.items()
            if key not in data.get("disable", [])
        ]

        selectable_badges = {
            "forks": f"[![Forks](https://img.shields.io/github/forks/{repo_full_name})](https://github.com/{repo_full_name}/network/members)",
        }

        enabled_badges = [
            value
            for key, value in selectable_badges.items()
            if key in data.get("enable", [])
        ]

        badges.extend(selected_standard_badges)
        badges.extend(enabled_badges)
    else:
        badges.extend([value for key, value in standard_badges.items()])
    badges.extend(hardcoded_badges)

    # pypi badges
    if PYPI_PACKAGE_NAME:
        badges.append(
            f"[![PyPI Version](https://img.shields.io/pypi/v/{PYPI_PACKAGE_NAME})](https://pypi.org/project/{PYPI_PACKAGE_NAME})"
        )
        badges.append(
            f"[![Python Versions](https://img.shields.io/pypi/pyversions/{PYPI_PACKAGE_NAME})](https://pypi.org/project/{PYPI_PACKAGE_NAME})"
        )

    # Join all badges with a space
    return "\n".join(badges)


def update_readme(repo_full_name):
    if not README_FILE.exists():
        readme_content = '<div class="badges">\n</div>\n'
    else:
        readme_content = README_FILE.read_text()

    badge_block = build_badge_block(repo_full_name)
    new_block = f'<div class="badges">\n\n{badge_block}\n\n</div>'

    if BADGES_TAG_RE.search(readme_content):
        updated_content = BADGES_TAG_RE.sub(new_block, readme_content)
    else:
        # If no <badges> tag exists, append it at the top
        updated_content = new_block + "\n\n" + readme_content

    README_FILE.write_text(updated_content)


# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    # Infer repository name from environment if running in GitHub Actions
    GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
    if GITHUB_REPOSITORY:
        update_readme(GITHUB_REPOSITORY)
    else:
        raise Exception("GITHUB_REPOSITORY environment variable not set")
