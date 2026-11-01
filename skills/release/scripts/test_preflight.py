import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from preflight import CONFIG, LEGACY_CONFIG, inspect, load_config, repository_identity


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "repo"
        self.root.mkdir()
        self.git("init", "--initial-branch=main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Release test")
        self.git("config", "commit.gpgsign", "false")
        self.git("remote", "add", "origin", "https://github.com/example/project.git")
        self.write("package.json", json.dumps({"private": True, "version": "1.2.3"}))
        self.git("add", "package.json")
        self.git("commit", "-m", "Initial fixture")
        self.config = {
            "schemaVersion": 1, "repository": "example/project", "versionFiles": ["package.json"],
            "push": {"remote": "origin", "branch": "main"},
        }
        self.save()

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.root), *args], capture_output=True, text=True, check=True,
        ).stdout.strip()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def save(self, config=None, path=CONFIG):
        self.write(path, json.dumps(self.config if config is None else config))

    def run_cli(self, *args, repo=None, env=None):
        environment = dict(os.environ)
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
            environment.pop(name, None)
        environment.update(env or {})
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("preflight.py")),
             "--repo", str(repo or self.root), *args],
            capture_output=True, text=True, env=environment, check=False,
        )
        self.assertEqual(result.stderr, "")
        return result.returncode, json.loads(result.stdout)

    def test_reports_local_evidence_and_keeps_review_explicit(self):
        report = inspect(self.root)
        self.assertEqual(report["status"], "review-required")
        self.assertEqual(report["versions"], [{"path": "package.json", "version": "1.2.3"}])
        self.assertEqual(report["destination"], {
            "remote": "origin", "branch": "main", "repository": "example/project",
        })
        self.assertEqual(report["phases"], {"push": False, "github": "disabled"})
        self.assertEqual(report["process"], "discover")
        self.assertEqual(report["git"]["head"], self.git("rev-parse", "HEAD"))
        self.assertIn("i-have-adhd", " ".join(report["reviewRequired"]))

    def test_current_and_legacy_discovery_and_conflict(self):
        (self.root / CONFIG).unlink()
        self.save(path=LEGACY_CONFIG)
        self.assertEqual(load_config(self.root)[0], LEGACY_CONFIG)
        self.save()
        with self.assertRaisesRegex(ValueError, "Both current and legacy"):
            load_config(self.root)

    def test_absent_config_preserves_local_default_and_explicit_publication(self):
        (self.root / CONFIG).unlink()
        self.git("remote", "remove", "origin")
        report = inspect(self.root, local=True)
        self.assertEqual(report["status"], "review-required")
        self.assertIsNone(report["configuration"])
        self.assertEqual(report["versions"], [])
        self.assertEqual(report["process"], "discover")
        self.git("remote", "add", "origin", "https://github.com/example/project")
        report = inspect(self.root, remote="origin", branch="main", push=True)
        self.assertEqual(report["phases"], {"push": True, "github": "disabled"})
        report = inspect(self.root, remote="origin", branch="main", publish=True)
        self.assertEqual(report["phases"], {"push": True, "github": "direct"})

    def test_schema_rejects_invalid_types_fields_and_required_values(self):
        cases = [
            {"schemaVersion": True}, {"schemaVersion": 2}, {"unknown": True},
            {"repository": "https://github.com/example/project"}, {"versionFiles": []},
            {"versionFiles": "package.json"}, {"tag": {"create": "false"}},
            {"tag": {"typo": True}}, {"push": {"automatic": 1}}, {"push": []},
            {"notes": {"storage": "unknown"}}, {"notes": {"storage": "repository"}},
            {"notes": {"storage": "github", "path": "notes.md"}},
            {"notes": {"storage": "github", "index": "package.json"}},
            {"github": {"mode": "workflow"}}, {"github": {"latest": "yes"}},
            {"github": {"mode": "other"}}, {"guides": "AGENTS.md"},
            {"process": []}, {"process": [{"type": "other"}]},
            {"process": [{"type": "skill"}]}, {"process": [{"type": "skill", "name": ""}]},
            {"process": [{"type": "script", "command": "echo unsafe"}]},
            {"process": [{"type": "script", "command": []}]},
            {"process": [{"type": "script", "command": ["node", 3]}]},
            {"process": [{"type": "script", "command": ["node", "{unknown}"]}]},
            {"process": [{"type": "script", "command": ["{version}"]}]},
        ]
        for update in cases:
            with self.subTest(update=update):
                self.save({**self.config, **update})
                with self.assertRaises(ValueError):
                    load_config(self.root)

    def test_no_config_keeps_non_github_local_and_push_workflows_available(self):
        (self.root / CONFIG).unlink()
        self.git("remote", "set-url", "origin", "ssh://git@example.invalid/example/project.git")
        for options in ({"local": True}, {"push": True}, {"local": True, "publish": True}):
            report = inspect(self.root, remote="origin", branch="main", **options)
            self.assertEqual(report["status"], "review-required")
        report = inspect(self.root, remote="origin", branch="main", publish=True)
        self.assertEqual(report["status"], "blocked")

    def test_malformed_and_duplicate_json_fail_with_json_cli_error(self):
        for contents in ("{invalid", '{"schemaVersion":1,"schemaVersion":1}', "[]", "{}"):
            with self.subTest(contents=contents):
                self.write(CONFIG, contents)
                status, report = self.run_cli()
                self.assertEqual(status, 1)
                self.assertEqual(report["status"], "blocked")

    def test_missing_or_escaping_resources_stop_preflight(self):
        cases = [
            {"versionFiles": ["missing.json"]}, {"versionFiles": ["../outside.json"]},
            {"versionFiles": [str(self.root / "package.json")]},
            {"guides": ["missing.md"]}, {"guides": ["http://example.invalid/guide"]},
            {"notes": {"path": "../{version}.md"}}, {"notes": {"path": "{other}.md"}},
            {"notes": {"index": "missing.json"}},
            {"github": {"mode": "workflow", "workflow": "missing.yml"}},
            {"process": [{"type": "instructions", "path": "missing.md"}]},
        ]
        for update in cases:
            with self.subTest(update=update):
                self.save({**self.config, **update})
                with self.assertRaises(ValueError):
                    load_config(self.root)

    def test_symlink_containment_including_uncreated_notes_and_configuration(self):
        outside = self.root.parent / "outside"
        outside.mkdir()
        (outside / "version.json").write_text('{"version":"1.2.3"}')
        (self.root / "escape").symlink_to(outside, target_is_directory=True)
        for update in (
            {"versionFiles": ["escape/version.json"]},
            {"notes": {"storage": "repository", "path": "escape/{tag}.md"}},
        ):
            self.save({**self.config, **update})
            with self.assertRaisesRegex(ValueError, "inside the repository"):
                load_config(self.root)
        (self.root / CONFIG).unlink()
        (self.root / CONFIG).symlink_to(outside / "missing.json")
        with self.assertRaisesRegex(ValueError, "inside the repository"):
            load_config(self.root)

    def test_supported_note_templates_and_internal_symlinks(self):
        (self.root / "version-link.json").symlink_to(self.root / "package.json")
        self.config.update({"versionFiles": ["version-link.json"], "tag": {"prefix": ""},
                            "notes": {"storage": "repository", "path": "notes/{tag}/{version}.md"},
                            "guides": ["https://example.invalid/guide#releases"]})
        self.save()
        self.assertEqual(inspect(self.root)["status"], "review-required")
        self.assertFalse((self.root / "notes").exists())

    def test_remote_normalization_and_credential_redaction(self):
        for url in ("https://github.com/Example/Project.git", "git@github.com:example/project.git",
                    "ssh://git@github.com/example/project", "https://github.com/example/project/"):
            with self.subTest(url=url):
                self.assertEqual(repository_identity(url), "example/project")
        self.git("remote", "set-url", "origin", "https://secret-token@github.com/example/project.git")
        status, report = self.run_cli()
        self.assertEqual(status, 1)
        self.assertNotIn("secret-token", json.dumps(report))
        self.assertIn("credentials", report["blockers"][0])

    def test_push_url_identity_and_multiple_destinations(self):
        self.git("remote", "set-url", "--push", "origin", "git@github.com:parent/template.git")
        self.assertIn("does not match", " ".join(inspect(self.root)["blockers"]))
        self.git("remote", "set-url", "--add", "--push", "origin", "git@github.com:example/project.git")
        self.assertIn("multiple push URLs", " ".join(inspect(self.root)["blockers"]))

    def test_aliases_nonstandard_hosts_and_invalid_refs_require_resolution(self):
        for url in ("git@github-work:example/project", "ssh://git@example.invalid/example/project",
                    "https://github.com:8443/example/project", "/local/repository"):
            with self.subTest(url=url):
                self.git("remote", "set-url", "origin", url)
                self.assertTrue(inspect(self.root)["blockers"])
        self.git("remote", "set-url", "origin", "https://github.com/example/project")
        self.assertTrue(inspect(self.root, remote="unknown")["blockers"])
        self.assertTrue(inspect(self.root, branch="bad..branch")["blockers"])
        self.config["tag"] = {"prefix": "bad..prefix"}
        self.save()
        self.assertTrue(inspect(self.root)["blockers"])

    def test_upstream_and_explicit_destination_override(self):
        self.config["push"] = {}
        self.save()
        self.git("config", "branch.main.remote", "origin")
        self.git("config", "branch.main.merge", "refs/heads/releases")
        self.assertEqual(inspect(self.root)["destination"]["branch"], "releases")
        self.git("remote", "add", "release", "git@github.com:example/project.git")
        report = inspect(self.root, remote="release", branch="stable")
        self.assertEqual(report["destination"]["remote"], "release")
        self.assertEqual(report["destination"]["branch"], "stable")

    def test_local_overrides_all_automatic_and_explicit_remote_phases(self):
        self.config["push"]["automatic"] = True
        self.config["github"] = {"mode": "direct", "automatic": True}
        self.save()
        self.assertEqual(inspect(self.root)["phases"], {"push": True, "github": "direct"})
        status, report = self.run_cli("--local", "--push", "--publish")
        self.assertEqual(status, 0)
        self.assertEqual(report["phases"], {"push": False, "github": "disabled"})

    def test_github_automatic_never_independently_authorizes_push(self):
        self.config["github"] = {"mode": "direct", "automatic": True}
        self.save()
        self.assertEqual(inspect(self.root)["phases"], {"push": False, "github": "disabled"})
        self.assertEqual(inspect(self.root, push=True)["phases"], {"push": True, "github": "direct"})
        self.config["github"] = {"mode": "disabled", "automatic": True}
        self.save()
        self.assertEqual(inspect(self.root, publish=True)["phases"], {"push": True, "github": "disabled"})

    def test_workflow_is_reported_for_inspection_without_running_it(self):
        self.write(".github/workflows/release.yml", "name: Existing release\n")
        self.config["github"] = {"mode": "workflow", "automatic": True,
                                 "workflow": ".github/workflows/release.yml"}
        self.save()
        report = inspect(self.root, push=True)
        self.assertEqual(report["phases"]["github"], "workflow")
        self.assertIn(".github/workflows/release.yml", report["read"])

    def test_custom_process_is_preserved_without_executing_or_selecting_tooling(self):
        self.write("process.md", "Use project tooling.\n")
        self.config["process"] = [
            {"type": "instructions", "path": "process.md"},
            {"type": "script", "command": ["sh", "-c", "touch should-not-exist", "{version}", "{tag}"]},
            {"type": "skill", "name": "project:release-checks"},
        ]
        self.save()
        report = inspect(self.root)
        self.assertEqual(report["process"], "configured")
        self.assertIn("process.md", report["read"])
        self.assertIn({"readInstalledSkill": "project:release-checks"}, report["reviewRequired"])
        self.assertFalse((self.root / "should-not-exist").exists())
        self.assertNotIn("commit-and-tag-version", json.dumps(report))

    def test_disagreement_and_unrecognized_version_formats_are_not_guessed(self):
        self.write("VERSION", "1.2.4-rc.0\n")
        self.write("version.toml", 'version = "1.2.3"\n')
        self.config["versionFiles"] += ["VERSION", "version.toml"]
        self.save()
        report = inspect(self.root)
        self.assertEqual(report["status"], "blocked")
        self.assertIn("partial release", " ".join(report["blockers"]))
        self.assertEqual(report["versions"][-1], {"path": "version.toml", "version": None})
        self.assertIn("project format", " ".join(report["reviewRequired"]))

    def test_staged_rename_newline_paths_and_truncation_are_explicit(self):
        self.git("mv", "package.json", "renamed.json")
        self.config["versionFiles"] = ["renamed.json"]
        self.save()
        self.write("line\nbreak.txt", "Unrelated work")
        report = inspect(self.root)
        self.assertIn({"status": "R ", "path": "renamed.json", "from": "package.json"}, report["git"]["changes"])
        self.assertIn({"status": "??", "path": "line\nbreak.txt"}, report["git"]["changes"])
        for number in range(35):
            self.write(f"untracked/{number}.txt", "Unrelated")
        report = inspect(self.root)
        self.assertTrue(report["git"]["changesTruncated"])
        self.assertGreater(report["git"]["changeCount"], len(report["git"]["changes"]))

    def test_recent_tags_are_bounded_and_never_claimed_complete(self):
        for number in range(12):
            self.git("tag", f"v1.2.4-rc.{number}")
        report = inspect(self.root)
        self.assertEqual(len(report["git"]["recentTags"]), 10)
        self.assertFalse(report["git"]["tagsAreCompleteReleaseSequence"])

    def test_nested_directory_and_linked_worktree_use_repository_metadata(self):
        nested = self.root / "nested"
        nested.mkdir()
        self.assertEqual(inspect(nested)["root"], str(self.root))
        worktree = self.root.parent / "worktree"
        self.git("add", CONFIG)
        self.git("commit", "-m", "Fixture config")
        self.git("worktree", "add", "--detach", str(worktree))
        report = inspect(worktree)
        self.assertIsNone(report["git"]["branch"])
        self.assertEqual(report["git"]["commonDir"], str(self.root / ".git"))
        self.assertEqual(report["root"], str(worktree))

    def test_unborn_and_shallow_repositories_are_explicit(self):
        unborn = self.root.parent / "unborn"
        subprocess.run(["git", "init", str(unborn)], capture_output=True, check=True)
        report = inspect(unborn, local=True)
        self.assertIsNone(report["git"]["head"])
        shallow = self.root.parent / "shallow"
        subprocess.run(["git", "clone", "--depth=1", self.root.as_uri(), str(shallow)],
                       capture_output=True, check=True)
        report = inspect(shallow, local=True)
        self.assertTrue(report["git"]["shallow"])
        self.assertIn("History is shallow", " ".join(report["reviewRequired"]))

    def test_cli_leaves_files_index_refs_and_staging_unchanged(self):
        self.write("staged.txt", "keep staged\n")
        self.git("add", "staged.txt")
        self.write("package.json", '{"version":"1.2.4-rc.0"}\n')
        self.git("tag", "-a", "v1.2.3", "-m", "Release fixture")
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        status, report = self.run_cli("--push", "--publish")
        self.assertEqual(status, 0)
        self.assertEqual(report["versions"][0]["version"], "1.2.4-rc.0")
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_cli_reports_non_repository_and_environment_overrides(self):
        status, report = self.run_cli(repo=self.root.parent)
        self.assertEqual(status, 1)
        self.assertEqual(report["status"], "blocked")
        status, report = self.run_cli(env={"GIT_INDEX_FILE": "/tmp/other-index"})
        self.assertEqual(status, 1)
        self.assertIn("overrides", report["blockers"][0])

    def test_status_does_not_execute_active_content_filters(self):
        self.git("config", "filter.sideeffect.clean", "touch filter-ran; cat")
        self.write(".gitattributes", "filtered.txt filter=sideeffect\n")
        filtered = self.write("filtered.txt", "Original\n")
        self.git("add", ".gitattributes", "filtered.txt")
        self.git("commit", "-m", "Fixture filter")
        (self.root / "filter-ran").unlink()
        filtered.write_text("Modified\n")
        os.utime(filtered, (1000000000, 1000000000))
        for kind in ("clean", "process"):
            with self.subTest(kind=kind):
                if kind == "process":
                    self.git("config", "--unset", "filter.sideeffect.clean")
                    self.git("config", "filter.sideeffect.process", "touch filter-ran; cat")
                status, report = self.run_cli()
                self.assertEqual(status, 0)
                self.assertFalse((self.root / "filter-ran").exists())
                self.assertFalse(report["git"]["statusCollected"])
                self.assertIsNone(report["git"]["changeCount"])
                self.assertIn("Worktree status omitted", " ".join(report["reviewRequired"]))

    def test_unused_filters_and_fsmonitor_do_not_execute_or_hide_status(self):
        self.git("config", "filter.unused.clean", "touch filter-ran; cat")
        self.git("config", "core.fsmonitor", "touch fsmonitor-ran")
        self.write("untracked.txt", "Unrelated")
        report = inspect(self.root)
        self.assertTrue(report["git"]["statusCollected"])
        self.assertIn({"status": "??", "path": "untracked.txt"}, report["git"]["changes"])
        self.assertFalse((self.root / "filter-ran").exists())
        self.assertFalse((self.root / "fsmonitor-ran").exists())

    def test_submodule_content_filters_are_not_executed(self):
        self.git("-c", "protocol.file.allow=always", "submodule", "add", self.root.as_uri(), "modules/fixture")
        module = self.root / "modules/fixture"
        self.git("-C", str(module), "config", "filter.sideeffect.clean", "touch filter-ran; cat")
        (module / ".gitattributes").write_text("package.json filter=sideeffect\n")
        package = module / "package.json"
        package.write_text(package.read_text().replace("1.2.3", "1.2.4"))
        os.utime(package, (1000000000, 1000000000))
        status, report = self.run_cli()
        self.assertEqual(status, 0)
        self.assertFalse((module / "filter-ran").exists())
        self.assertFalse(report["git"]["submodulesInspected"])
        self.assertIn("Submodule worktrees were not inspected", " ".join(report["reviewRequired"]))

    def test_process_execution_is_limited_to_local_git_queries(self):
        run = subprocess.run
        calls = []

        def local_query(command, **kwargs):
            self.assertEqual(command[:6], ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(self.root)])
            self.assertIn(command[6], {"rev-parse", "symbolic-ref", "config", "remote",
                                       "check-ref-format", "status", "for-each-ref", "ls-files", "check-attr"})
            if command[6] == "remote" and len(command) > 7:
                self.assertEqual(command[7:10], ["get-url", "--push", "--all"])
            if command[6] == "config":
                self.assertIn(command[7], ("--get", "--name-only"))
            if command[6] == "status":
                self.assertIn("--ignore-submodules=all", command)
            self.assertFalse(kwargs.get("shell"))
            calls.append(command)
            return run(command, **kwargs)

        with patch("preflight.subprocess.run", side_effect=local_query):
            inspect(self.root, push=True, publish=True)
        self.assertTrue(calls)


if __name__ == "__main__":
    unittest.main()
