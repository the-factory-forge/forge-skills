#!/usr/bin/env python3
"""Read-only release evidence. Python 3.9+ and Git; no release commands or network."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit


CONFIG = ".agents/configs/.release/config.json"
LEGACY_CONFIG = ".agents/.release.json"


def git(root, *args, optional=False, input_text=None):
    result = subprocess.run(
        ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(root), *args],
        capture_output=True, text=True, check=False, input=input_text,
    )
    if result.returncode and not optional:
        # Git errors can contain credential-bearing remote URLs.
        raise ValueError(f"Git {args[0]} failed (exit {result.returncode}); inspect locally")
    return result.stdout.rstrip("\n") if result.returncode == 0 else None


def fields(value, label, allowed, required=()):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    if set(value) - set(allowed):
        raise ValueError(f"{label} contains unsupported fields")
    if set(required) - set(value):
        raise ValueError(f"{label} is missing required fields: {', '.join(sorted(set(required) - set(value)))}")


def string(value, label, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()) or "\0" in value:
        raise ValueError(f"{label} must be {'a' if empty else 'a nonempty'} string without NULs")
    return value


def placeholders(value, label):
    remaining = value.replace("{version}", "").replace("{tag}", "")
    if "{" in remaining or "}" in remaining:
        raise ValueError(f"{label} contains an unsupported placeholder")


def local_path(root, value, label, existing=True, template=False):
    string(value, label)
    if template:
        placeholders(value, label)
    path = Path(value)
    if path.is_absolute() or not (root / path).resolve().is_relative_to(root):
        raise ValueError(f"{label} must stay inside the repository, including symlinks")
    path = root / path
    if existing and not path.is_file():
        raise ValueError(f"{label} must name an existing file")
    return path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON contains duplicate keys")
        result[key] = value
    return result


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (json.JSONDecodeError, UnicodeError) as error:
        raise ValueError("Invalid JSON in " + path.name) from error


def load_config(root):
    candidates = [name for name in (CONFIG, LEGACY_CONFIG)
                  if (root / name).exists() or (root / name).is_symlink()]
    if len(candidates) == 2:
        raise ValueError("Both current and legacy release configurations exist; resolve the duplicate source")
    if not candidates:
        return None, {}
    name = candidates[0]
    config = read_json(local_path(root, name, "configuration"))
    fields(config, "configuration", (
        "schemaVersion", "repository", "versionFiles", "tag", "push", "notes", "github", "guides", "process",
    ), ("schemaVersion", "repository", "versionFiles"))
    if type(config["schemaVersion"]) is not int or config["schemaVersion"] != 1:
        raise ValueError("schemaVersion must be 1")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", string(config["repository"], "repository")):
        raise ValueError("repository must be a GitHub owner/repository identity")
    versions = config["versionFiles"]
    if not isinstance(versions, list) or not versions:
        raise ValueError("versionFiles must be a nonempty array")
    for value in versions:
        local_path(root, value, "versionFiles entry")

    for section, allowed in (
        ("tag", ("create", "prefix")),
        ("push", ("automatic", "remote", "branch")),
        ("notes", ("storage", "path", "index")),
        ("github", ("mode", "automatic", "workflow", "latest")),
    ):
        data = config.get(section, {})
        fields(data, section, allowed)
        for key, value in data.items():
            if key in ("create", "automatic"):
                if type(value) is not bool:
                    raise ValueError(f"{section}.{key} must be a boolean")
            else:
                string(value, f"{section}.{key}", empty=key == "prefix")
    for section, key, choices in (
        ("notes", "storage", ("github", "repository")),
        ("github", "mode", ("disabled", "direct", "workflow")),
        ("github", "latest", ("stable", "never")),
    ):
        if key in config.get(section, {}) and config[section][key] not in choices:
            raise ValueError(f"{section}.{key} must be one of: {', '.join(choices)}")
    notes = config.get("notes", {})
    if notes.get("storage") == "repository" and "path" not in notes:
        raise ValueError("notes.path is required for repository storage")
    if notes.get("storage") == "github" and any(key in notes for key in ("path", "index")):
        raise ValueError("GitHub-only notes must omit notes.path and notes.index")
    if "path" in notes:
        local_path(root, notes["path"], "notes.path", existing=False, template=True)
    if "index" in notes:
        local_path(root, notes["index"], "notes.index")
    github = config.get("github", {})
    if github.get("mode") == "workflow" and "workflow" not in github:
        raise ValueError("github.workflow is required for workflow mode")
    if "workflow" in github:
        local_path(root, github["workflow"], "github.workflow")
    guides = config.get("guides", [])
    if not isinstance(guides, list):
        raise ValueError("guides must be an array")
    for guide in guides:
        string(guide, "guide")
        if guide.startswith("https://"):
            url = urlsplit(guide)
            if not url.hostname or url.username or url.password:
                raise ValueError("HTTPS guides must have a host and no credentials")
        else:
            local_path(root, guide, "guide")

    if "process" in config:
        if not isinstance(config["process"], list) or not config["process"]:
            raise ValueError("process must be a nonempty array")
        for step in config["process"]:
            if not isinstance(step, dict) or step.get("type") not in ("instructions", "script", "skill"):
                raise ValueError("Unknown process entry type")
            key = {"instructions": "path", "script": "command", "skill": "name"}[step["type"]]
            fields(step, "process entry", ("type", key), ("type", key))
            if key == "path":
                local_path(root, step[key], "process instructions")
            elif key == "name":
                string(step[key], "process skill name")
            else:
                if not isinstance(step[key], list) or not step[key]:
                    raise ValueError("process command must be a nonempty argument array")
                for argument in step[key]:
                    string(argument, "process command argument", empty=True)
                    placeholders(argument, "process command argument")
                string(step[key][0], "process executable")
                if any(marker in step[key][0] for marker in ("{version}", "{tag}")):
                    raise ValueError("Process executable must be inspectable before resolving the target")
    return name, config


def repository_identity(value):
    if re.match(r"^[^/@:]+@[^/:]+:", value):
        host, path = value.split("@", 1)[1].split(":", 1)
    else:
        url = urlsplit(value)
        if url.scheme not in ("https", "ssh") or not url.hostname or url.query or url.fragment:
            raise ValueError("Destination must be a canonical GitHub HTTPS or SSH URL; verify aliases manually")
        if url.password or (url.username and url.scheme != "ssh"):
            raise ValueError("Destination URL contains credentials; inspect locally without printing it")
        if url.port not in (None, 443 if url.scheme == "https" else 22):
            raise ValueError("Destination uses a nonstandard port; verify it manually")
        host, path = url.hostname, url.path
    identity = path.strip("/").removesuffix(".git")
    if host.lower() != "github.com" or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", identity):
        raise ValueError("Destination is not a canonical github.com repository; verify its identity manually")
    return identity.lower()


def inspect(repo, remote=None, branch=None, local=False, push=False, publish=False):
    root = Path(git(repo, "rev-parse", "--show-toplevel")).resolve()
    name, config = load_config(root)
    blockers = []
    review = ["Read repository guidance and inspect the selected process, scripts and hooks",
              "Locate and read installed i-have-adhd before preparation or resumption",
              "Resolve the exact target, full release-tag sequence and partial release artifacts"]
    branch_name = git(root, "symbolic-ref", "--quiet", "--short", "HEAD", optional=True)
    head = git(root, "rev-parse", "--verify", "HEAD", optional=True)
    destination = config.get("push", {})
    should_push = not local and (push or publish or destination.get("automatic", False))
    remote = remote or destination.get("remote") or (git(
        root, "config", "--get", f"branch.{branch_name}.remote", optional=True) if branch_name else None)
    branch = branch or destination.get("branch") or (git(
        root, "config", "--get", f"branch.{branch_name}.merge", optional=True) if branch_name else None)
    if branch and branch.startswith("refs/heads/"):
        branch = branch[len("refs/heads/"):]
    identity = None
    if not remote or not branch:
        (blockers if name or should_push else review).append(
            "Resolve destination remote and branch from the request or documented upstream")
    if branch and git(root, "check-ref-format", "refs/heads/" + branch, optional=True) is None:
        blockers.append("Destination branch is not a valid Git branch ref")
    if remote:
        if remote not in git(root, "remote").splitlines():
            blockers.append("Destination must identify an existing named remote; resolve it before preparation")
        else:
            urls = git(root, "remote", "get-url", "--push", "--all", remote).splitlines()
            if len(urls) != 1:
                blockers.append("Destination has multiple push URLs; resolve the ambiguity before preparation")
            else:
                try:
                    identity = repository_identity(urls[0])
                except ValueError as error:
                    (blockers if name or (publish and not local) else review).append(str(error))
            if identity and config and identity != config["repository"].lower():
                blockers.append("Configured repository does not match the destination push URL")

    versions = []
    for value in config.get("versionFiles", []):
        path = root / value
        if path.suffix == ".json":
            data = read_json(path)
            version = data.get("version") if isinstance(data, dict) else None
        elif path.name == "VERSION":
            version = path.read_text(encoding="utf-8").strip()
        else:
            version = None
        if not isinstance(version, str) or not version or "\n" in version:
            review.append("Read authoritative version using its project format: " + value)
            versions.append({"path": value, "version": None})
        else:
            versions.append({"path": value, "version": version})
    if len({item["version"] for item in versions if item["version"] is not None}) > 1:
        blockers.append("Version files disagree; inspect partial release changes before choosing a base or bumping")
    if not name:
        review.append("Discover authoritative versions, note convention and documented release process; configuration is absent")
    for step in config.get("process", []):
        if step["type"] == "script":
            review.append({"inspectCommand": step["command"],
                           "check": "Resolve executable and script resources, path containment, placeholders and hooks; never execute during preflight"})
        elif step["type"] == "skill":
            review.append({"readInstalledSkill": step["name"]})
    if config.get("notes", {}).get("path"):
        review.append("Recheck expanded note path containment after resolving the exact version and tag")
    tag_prefix = config.get("tag", {}).get("prefix", "v")
    if git(root, "check-ref-format", "refs/tags/" + tag_prefix + "0.0.0", optional=True) is None:
        blockers.append("Tag prefix cannot form a valid release tag")

    filter_keys = git(root, "config", "--name-only", "--get-regexp", r"^filter\..*\.(clean|process)$", optional=True)
    active_filters = False
    if filter_keys:
        paths = git(root, "ls-files", "-z")
        attributes = git(root, "check-attr", "-z", "--stdin", "filter", input_text=paths)
        active_filters = any(f"filter.{driver}.{kind}" in filter_keys.splitlines()
                             for driver in attributes.split("\0")[2::3] for kind in ("clean", "process"))
    # Status can execute clean/process filters even with optional locks disabled.
    status = None if active_filters else git(
        root, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignore-submodules=all")
    if active_filters:
        review.append("Worktree status omitted: inspect active Git content filters before running git status")
    if (root / ".gitmodules").exists():
        review.append("Submodule worktrees were not inspected; inspect their configuration and state before release")
    entries = iter((status or "").split("\0"))
    changes = []
    for entry in entries:
        if not entry:
            continue
        change = {"status": entry[:2], "path": entry[3:]}
        if "R" in entry[:2] or "C" in entry[:2]:
            change["from"] = next(entries)
        changes.append(change)
    if changes:
        review.append("Preserve unrelated staged/unstaged edits and inspect overlaps with release files")
    tags = git(root, "for-each-ref", "--sort=-creatordate", "--count=10",
               "--format=%(refname:strip=2)", "refs/tags/").splitlines()
    shallow = git(root, "rev-parse", "--is-shallow-repository") == "true"
    if shallow:
        review.append("History is shallow; establish complete release history before selecting a base")
    github = config.get("github", {})
    mode = github.get("mode", "disabled") if name else ("direct" if publish else "disabled")
    hosted = mode if should_push and (publish or github.get("automatic", False)) else "disabled"
    if should_push:
        review.append("Inspect tag-triggered CI effects and verify live remote refs before pushing; local state is not remote verification")
    if hosted != "disabled":
        review.append("Check publication access before editing release files; follow the selected GitHub reference")
    common_dir = Path(git(root, "rev-parse", "--git-common-dir"))
    read = ([name] if name else []) + config.get("guides", [])
    read += [step["path"] for step in config.get("process", []) if step["type"] == "instructions"]
    if "workflow" in github:
        read.append(github["workflow"])
    return {
        "status": "blocked" if blockers else "review-required", "root": str(root),
        "configuration": name, "process": "configured" if "process" in config else "discover",
        "destination": {"remote": remote, "branch": branch, "repository": identity},
        "phases": {"push": should_push, "github": hosted}, "versions": versions,
        "git": {"branch": branch_name, "head": head, "shallow": shallow,
                "commonDir": str((root / common_dir).resolve()), "changes": changes[:30],
                "statusCollected": status is not None, "submodulesInspected": False,
                "changeCount": len(changes) if status is not None else None, "changesTruncated": len(changes) > 30,
                "recentTags": tags, "tagsAreCompleteReleaseSequence": False},
        "read": list(dict.fromkeys(read)), "blockers": blockers, "reviewRequired": review,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--remote", help="Explicit destination named remote")
    parser.add_argument("--branch", help="Explicit destination branch")
    parser.add_argument("--local", action="store_true", help="Preparation-only; overrides all remote phase flags")
    parser.add_argument("--push", action="store_true", help="Reflect the user's push request; never performs a push")
    parser.add_argument("--publish", action="store_true", help="Reflect explicit publication authority; never publishes")
    args = parser.parse_args()
    try:
        if any(os.environ.get(key) for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE")):
            raise ValueError("Git repository overrides are set; rerun with them unset to inspect --repo reliably")
        report = inspect(**vars(args))
    except (ValueError, OSError, RuntimeError) as error:
        report = {"status": "blocked", "blockers": [str(error)]}
    print(json.dumps(report, ensure_ascii=True, separators=(",", ":")))
    return 1 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
