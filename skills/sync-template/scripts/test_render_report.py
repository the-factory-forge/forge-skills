from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from render_report import load_config, project_root, read_report, render, repository_identity


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.external = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            self.scripts.append(attrs)
        if attrs.get("src") or (attrs.get("href") and not attrs["href"].startswith("#")):
            self.external.append(attrs)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / ".agents/configs/.sync-template").mkdir(parents=True)
        self.config = {
            "schemaVersion": 1, "projectRepository": None,
            "template": {"url": "https://github.com/example/template", "ref": "refs/heads/main"},
            "lastReconciled": None, "lastCompared": None,
            "deviations": [{"area": "Auth", "paths": ["src/auth"], "decision": "Keep auth removed",
                            "reason": "Public site", "evidence": "Confirmed by owner"}],
        }
        self.report = {"status": "analyzed", "summary": "Initialization only", "differences": [],
                       "pending": ["Unknown baseline"], "checks": ["Application tests not run"]}
        self.write_config()

    def write_config(self):
        (self.root / ".agents/configs/.sync-template/config.json").write_text(json.dumps(self.config), encoding="utf-8")

    def test_missing_tracking_and_subdirectory_discovery(self):
        nested = self.root / "src/deep"
        nested.mkdir(parents=True)
        self.assertEqual(project_root(nested), self.root)
        (nested / ".git").mkdir()
        with self.assertRaisesRegex(ValueError, "tracking is missing"):
            project_root(nested)

    def test_preserves_history_and_idempotent_reimport(self):
        (self.root / "docs").mkdir()
        original = "# Earlier sync\n\nCafé <tag> & decisions\n"
        path = self.root / "docs/template-sync.md"
        path.write_text(original, encoding="utf-8")
        output = render(self.root, self.report, ["docs/template-sync.md"])
        first = output.read_bytes()
        render(self.root, self.report, ["docs/template-sync.md"])
        self.assertEqual(first, output.read_bytes())
        path.unlink()
        self.report["summary"] = "Later comparison"
        render(self.root, self.report)
        self.assertEqual(read_report(output)["history"]["docs/template-sync.md"]["text"], original)

    def test_non_git_discovery_from_tracking_directories(self):
        for relative in (".agents", ".agents/configs", ".agents/configs/.sync-template"):
            with self.subTest(path=relative):
                self.assertEqual(project_root(self.root / relative), self.root)

    def test_legacy_migration_preserves_config_and_history(self):
        self.config["lastReconciled"] = {"commit": "a" * 40, "version": None, "date": "2026-10-29",
                                         "evidence": "Verified adoption"}
        self.write_config()
        (self.root / "old.md").write_text("Keep the original decisions.\n", encoding="utf-8")
        output = render(self.root, self.report, ["old.md"])
        tracking = self.root / ".agents/configs/.sync-template"
        self.assertEqual(output, tracking / "report.html")
        before_config = (tracking / "config.json").read_bytes()
        before_report = output.read_bytes()
        before_history = read_report(output)["history"]
        legacy = self.root / ".sync-template"
        tracking.rename(legacy)
        nested = self.root / "src"
        nested.mkdir()
        self.assertEqual(project_root(nested), self.root)
        with self.assertRaisesRegex(ValueError, "Legacy .* migrate"):
            render(self.root, self.report)
        self.assertFalse(tracking.exists())
        self.assertEqual((legacy / "config.json").read_bytes(), before_config)
        self.assertEqual((legacy / "report.html").read_bytes(), before_report)
        legacy.rename(tracking)
        self.assertEqual(output.read_bytes(), before_report)
        self.report["summary"] = "Comparison after relocation"
        render(project_root(nested), self.report)
        self.assertEqual((tracking / "config.json").read_bytes(), before_config)
        self.assertEqual(read_report(output)["history"], before_history)
        self.assertFalse(legacy.exists())

    def test_coexisting_tracking_directories_require_reconciliation(self):
        output = render(self.root, self.report)
        legacy = self.root / ".sync-template"
        legacy.mkdir()
        (legacy / "config.json").write_text(json.dumps(self.config), encoding="utf-8")
        (legacy / "report.html").write_text("Unreconciled legacy history", encoding="utf-8")
        paths = [output, output.parent / "config.json", legacy / "config.json", legacy / "report.html"]
        before = {path: path.read_bytes() for path in paths}
        with self.assertRaisesRegex(ValueError, "both directories exist"):
            render(project_root(self.root), self.report)
        self.assertEqual({path: path.read_bytes() for path in paths}, before)

    def test_git_root_wins_over_misplaced_nested_tracking(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        nested = self.root / "src"
        (nested / ".agents/configs/.sync-template").mkdir(parents=True)
        (nested / ".agents/configs/.sync-template/config.json").write_text(json.dumps(self.config))
        self.assertEqual(project_root(nested), self.root)
        (self.root / ".agents/configs/.sync-template/config.json").unlink()
        with self.assertRaisesRegex(ValueError, "tracking is missing"):
            project_root(nested)

    def test_changed_or_corrupt_history_never_overwrites_report(self):
        path = self.root / "old.md"
        path.write_text("original", encoding="utf-8")
        output = render(self.root, self.report, ["old.md"])
        before = output.read_bytes()
        path.write_text("replacement", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "different contents"):
            render(self.root, self.report, ["old.md"])
        self.assertEqual(output.read_bytes(), before)
        output.write_text("<html>unrecognized existing report</html>", encoding="utf-8")
        before = output.read_bytes()
        with self.assertRaisesRegex(ValueError, "preserved data"):
            render(self.root, self.report)
        self.assertEqual(output.read_bytes(), before)

    def test_escapes_content_and_embedded_data(self):
        attack = '</script><script src="https://bad.example">alert(1)</script>'
        self.report["summary"] = attack
        self.report["differences"] = [{"area": attack, "decision": attack, "detail": attack, "files": [attack]}]
        output = render(self.root, self.report)
        parsed = Elements()
        parsed.feed(output.read_text(encoding="utf-8"))
        self.assertEqual(parsed.scripts, [{"type": "application/json", "id": "sync-template-data"}])
        self.assertEqual(parsed.external, [])
        self.assertEqual(read_report(output)["report"]["summary"], attack)

    def test_unknown_release_partial_and_offline_do_not_advance_config(self):
        self.config["lastCompared"] = {"commit": "a" * 40, "version": None, "date": "2026-10-29",
                                       "evidence": "Cached inspection", "remoteVerified": False}
        self.write_config()
        before = (self.root / ".agents/configs/.sync-template/config.json").read_bytes()
        self.report["status"] = "partial"
        output = render(self.root, self.report)
        self.assertIn("Remote not verified; latest status unknown", output.read_text())
        self.assertIn("No verified release tag", output.read_text())
        self.assertEqual((self.root / ".agents/configs/.sync-template/config.json").read_bytes(), before)

    def test_copied_identity_is_rejected_without_touching_source(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "remote", "add", "origin", "git@github.com:example/customer.git"], check=True)
        self.config["projectRepository"] = "https://github.com/example/template"
        self.write_config()
        with self.assertRaisesRegex(ValueError, "different or unbound"):
            render(self.root, self.report)
        self.assertFalse((self.root / ".agents/configs/.sync-template/report.html").exists())
        self.config["projectRepository"] = "https://github.com/example/customer"
        self.write_config()
        (self.root / "work.txt").write_text("uncommitted work")
        render(self.root, self.report)
        self.assertEqual((self.root / "work.txt").read_text(), "uncommitted work")

    def test_invalid_schema_and_sha_are_rejected(self):
        self.config["schemaVersion"] = 2
        self.write_config()
        with self.assertRaisesRegex(ValueError, "schema version"):
            load_config(self.root)
        self.config["schemaVersion"] = 1
        self.config["lastCompared"] = {"commit": "main"}
        self.write_config()
        with self.assertRaisesRegex(ValueError, "full Git SHA"):
            load_config(self.root)

    def test_history_path_must_stay_in_project_and_be_a_record(self):
        with self.assertRaises(ValueError):
            render(self.root, self.report, ["../outside.md"])
        with self.assertRaises(ValueError):
            render(self.root, self.report, [".env.local"])

    def test_normalizes_git_urls_and_rejects_credentials(self):
        self.assertEqual(repository_identity("git@github.com:example/repo.git"), repository_identity("https://github.com/example/repo/"))
        with self.assertRaises(ValueError):
            repository_identity("https://token@github.com/example/repo")

    def test_repository_identity_preserves_nondefault_ports(self):
        self.assertNotEqual(repository_identity("ssh://git@example.com:2222/team/app.git"),
                            repository_identity("ssh://git@example.com:2223/team/app.git"))
        self.assertEqual(repository_identity("ssh://git@example.com:22/team/app.git"),
                         repository_identity("git@example.com:team/app.git"))

    def test_history_retains_original_line_endings_and_copied_config(self):
        original = b'# Earlier sync\r\n\r\nKeep these decisions.\r\n'
        (self.root / "old.md").write_bytes(original)
        copied = self.root / ".agents/configs/.sync-template/inherited-config.json"
        copied.write_bytes(b'{"projectRepository":"https://github.com/example/parent"}\r\n')
        output = render(self.root, self.report, ["old.md", ".agents/configs/.sync-template/inherited-config.json"])
        data = read_report(output)
        self.assertEqual(data["history"]["old.md"]["text"].encode(), original)
        self.assertEqual(data["history"][".agents/configs/.sync-template/inherited-config.json"]["text"].encode(), copied.read_bytes())
        copied.unlink()
        render(self.root, self.report)
        self.assertEqual(data["history"], read_report(output)["history"])

    def test_symlinked_output_is_rejected(self):
        other = self.root / "other.html"
        other.write_text("keep")
        (self.root / ".agents/configs/.sync-template/report.html").symlink_to(other)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            render(self.root, self.report)
        self.assertEqual(other.read_text(), "keep")

    def test_symlinked_tracking_ancestors_and_config_are_rejected(self):
        for relative in (".agents", ".agents/configs", ".agents/configs/.sync-template",
                         ".agents/configs/.sync-template/config.json"):
            with self.subTest(path=relative):
                path = self.root / relative
                real = self.root / "real-tracking"
                path.rename(real)
                path.symlink_to(real)
                try:
                    with self.assertRaisesRegex(ValueError, "symlinks"):
                        render(self.root, self.report)
                    self.assertFalse((self.root / ".agents/configs/.sync-template/report.html").exists())
                finally:
                    path.unlink()
                    real.rename(path)


if __name__ == "__main__":
    unittest.main()
