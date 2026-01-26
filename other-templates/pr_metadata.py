#!/usr/bin/env python3

import os
import re
import subprocess
import sys
from typing import Dict, List, Tuple


def _run_git(args: List[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.exit(result.returncode)
    return result.stdout


def _parse_priorities(raw: str) -> Dict[str, int]:
    priorities: Dict[str, int] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k or not v:
            continue
        try:
            priorities[k] = int(v)
        except ValueError:
            continue
    return priorities


def _write_output(key: str, value: str) -> None:
    out_path = os.environ.get("GITHUB_OUTPUT")
    if not out_path:
        print(f"GITHUB_OUTPUT not set; cannot write output {key}")
        sys.exit(1)

    with open(out_path, "a", encoding="utf-8") as f:
        if "\n" in value:
            f.write(f"{key}<<EOF\n{value}\nEOF\n")
        else:
            f.write(f"{key}={value}\n")


def _best_title(commit_messages: List[str], priorities: Dict[str, int]) -> Tuple[str, bool]:
    best_msg = ""
    best_p = None
    count_best = 0

    for msg in commit_messages:
        m = re.match(r"^(feat!|feat|fix|refactor|ci|docs|chore)(\([^)]*\))?:", msg)
        if not m:
            continue
        p = priorities.get(m.group(1))
        if p is None:
            continue

        if best_p is None or p < best_p:
            best_p = p
            best_msg = msg
            count_best = 1
        elif p == best_p:
            count_best += 1

    return best_msg, count_best > 1


def main() -> int:
    base_branch = os.environ.get("BASE_BRANCH", "")
    pr_branch = os.environ.get("PR_BRANCH", "")
    raw_priorities = os.environ.get("COMMIT_PRIORITIES", "")

    commit_range = f"remotes/origin/{base_branch}..{pr_branch}"

    conventional_re = re.compile(r"^(feat!|feat|fix|refactor|ci|docs|chore)(\(.+\))?:")
    feature_re = re.compile(r"^(feat!|feat|fix|refactor|ci|docs|chore)(:|\([^)]*\))")

    priorities = _parse_priorities(raw_priorities)

    subjects_raw = _run_git(["log", commit_range, "--pretty=format:%s"])
    subjects = subjects_raw.splitlines()

    feature_commits = "\n".join([s for s in subjects if feature_re.search(s)])
    print(feature_commits)
    _write_output("pr_features", feature_commits)

    bodies_raw = _run_git(["log", commit_range, "--pretty=format:%s%n%b"])
    lines = bodies_raw.splitlines()

    in_body = False
    body_lines: List[str] = []
    for line in lines:
        if re.match(r"^(feat!|feat|fix|refactor|ci|docs|chore)", line):
            in_body = True
            continue
        if in_body:
            body_lines.append(line)

    commit_bodies = "\n".join(body_lines)
    print(commit_bodies)
    _write_output("pr_notes", commit_bodies)

    conventional_subjects = [s for s in subjects if conventional_re.search(s)]
    if not conventional_subjects:
        print("No conventional commits found, unable to build pull request for you")
        return 0

    title, has_tie = _best_title(conventional_subjects, priorities)
    if has_tie:
        print("::notice::Multiple commits share the highest priority.")
        print("::notice::Unable to determine a single PR title automatically.")
        print("::notice::Please squash or reword commits so one clear highest-priority commit exists.")
        return 0

    _write_output("pr_title", title)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
