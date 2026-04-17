import subprocess
import sys
import toml
from packaging.version import Version, InvalidVersion

PYPROJECT = "pyproject.toml"


def get_latest_tag(repo_url: str):
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "--sort=v:refname", repo_url],
            capture_output=True,
            text=True,
            check=True,
        )

        tags = []
        for line in result.stdout.splitlines():
            ref = line.split("refs/tags/")[-1]
            ref = ref.replace("^{}", "")  # remove annotated tag suffix
            try:
                tags.append(Version(ref.lstrip("v")))
            except InvalidVersion:
                continue

        if not tags:
            return None

        latest = sorted(tags)[-1]
        return f"v{latest}"

    except subprocess.CalledProcessError as e:
        print(f"Error fetching tags for {repo_url}: {e}")
        return None


def main():
    data = toml.load(PYPROJECT)

    deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})

    failures = []

    for name, spec in deps.items():
        if not isinstance(spec, dict):
            continue

        if "git" not in spec:
            continue

        repo_url = spec["git"]
        current_tag = spec.get("tag")

        # skip unpinned deps
        if not current_tag:
            print(f"::warning::{name}: no tag specified (unpinned dependency)")
            continue

        latest_tag = get_latest_tag(repo_url)

        if not latest_tag:
            print(f"::warning::{name}: could not determine latest tag")
            continue

        if current_tag != latest_tag:
            failures.append((name, current_tag, latest_tag))
            print(
                f"::error::{name} is outdated (current={current_tag}, latest={latest_tag})"
            )
        else:
            print(
                f"::notice::{name} is up to date (tag={current_tag})"
            )

    if failures:
        print("\n❌ Outdated dependencies found:\n")
        for name, current, latest in failures:
            print(f"- {name}: {current} → {latest}")

        sys.exit(1)

    print("::notice::All git dependency tags are up to date!")


if __name__ == "__main__":
    main()