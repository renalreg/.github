#!/usr/bin/env python3
import os
import re
import argparse
from pathlib import Path
from typing import Dict, List

import click
import yaml

README_FILE = Path("README.md")
BADGES_CONFIG_FILE = Path("badges.yml")
WORKFLOWS_DIR = Path(".github/workflows")
BADGES_TAG_RE = re.compile(r"<div class=\"badges\">.*?</div>", re.DOTALL)
PYPI_PACKAGE_NAME = os.environ.get("PYPI_PACKAGE_NAME")

def badge_registry(repo: str, visibility: str) -> Dict[str, str]:
    base = {
        "issues": f"[![Issues](https://img.shields.io/github/issues/{repo})](https://github.com/{repo}/issues)",
        "license": f"[![License](https://img.shields.io/github/license/{repo})](https://github.com/{repo}/blob/main/LICENSE)",
        "stars": f"[![Stars](https://img.shields.io/github/stars/{repo})](https://github.com/{repo}/stargazers)",
        "forks": f"[![Forks](https://img.shields.io/github/forks/{repo})](https://github.com/{repo}/network/members)",
        "dependencies": f"[![Dependencies](https://img.shields.io/librariesio/github/{repo})](https://libraries.io/github/{repo})",
        "vulnerabilities": f"[![Vulnerabilities](https://img.shields.io/snyk/vulnerabilities/github/{repo})](https://snyk.io/test/github/{repo})",
        "codecov": f"[![Coverage](https://codecov.io/gh/{repo}/branch/main/graph/badge.svg)](https://codecov.io/gh/{repo})",
    }

    # Default sets differ by visibility
    if visibility == "private":
        defaults = ["issues", "license"]
    else:  # public
        defaults = ["issues", "license", "stars", "dependencies", "vulnerabilities"]

    return {k: v for k, v in base.items() if k in defaults}



def detect_workflows(repo: str) -> Dict[str, str]:
    badges = {}
    if not WORKFLOWS_DIR.exists():
        return badges

    for wf in WORKFLOWS_DIR.glob("*.yml"):
        name = wf.stem
        badges[f"workflow:{name}"] = (
            f"[![{name}](https://github.com/{repo}/actions/workflows/{wf.name}/badge.svg)]"
            f"(https://github.com/{repo}/actions/workflows/{wf.name})"
        )
    return badges


def load_config() -> Dict:
    if not BADGES_CONFIG_FILE.exists():
        return {}

    with BADGES_CONFIG_FILE.open() as f:
        return yaml.safe_load(f) or {}


def build_badges(repo: str, visibility: str) -> List[str]:
    config = load_config()

    registry = badge_registry(repo, visibility)
    workflow_badges = detect_workflows(repo)

    # Merge registries
    registry.update(workflow_badges)

    # Apply disables
    for key in config.get("disable", []):
        registry.pop(key, None)

    # Apply enables (things not in defaults)
    for key in config.get("enable", []):
        if key in workflow_badges:
            registry[key] = workflow_badges[key]
        elif key in badge_registry(repo, "public"):
            registry[key] = badge_registry(repo, "public")[key]

    badges = list(registry.values())

    # Hardcoded custom badges
    for custom in config.get("badges", []):
        badges.append(custom)

    # PyPI badges
    if PYPI_PACKAGE_NAME:
        badges.extend(
            [
                f"[![PyPI Version](https://img.shields.io/pypi/v/{PYPI_PACKAGE_NAME})](https://pypi.org/project/{PYPI_PACKAGE_NAME})",
                f"[![Python Versions](https://img.shields.io/pypi/pyversions/{PYPI_PACKAGE_NAME})](https://pypi.org/project/{PYPI_PACKAGE_NAME})",
            ]
        )

    return badges


def update_readme(repo: str, visibility: str):
    badge_lines = "\n".join(build_badges(repo, visibility))
    new_block = f'<div class="badges">\n\n{badge_lines}\n\n</div>'

    if README_FILE.exists():
        content = README_FILE.read_text()
    else:
        content = ""

    if BADGES_TAG_RE.search(content):
        updated = BADGES_TAG_RE.sub(new_block, content)
    else:
        updated = new_block + "\n\n" + content

    README_FILE.write_text(updated)


@click.command()
@click.option(
    "--visibility",
    type=click.Choice(["public", "private"]),
    default="private",
    show_default=True,
    help="Controls which default badges are included.",
)
def main(visibility: str):
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        raise RuntimeError("GITHUB_REPOSITORY not set")

    update_readme(repo, visibility)


if __name__ == "__main__":
    main()
