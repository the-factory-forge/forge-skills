#!/usr/bin/env python3
"""Render reviewed template-sync data as one portable HTML report. Python 3.9+."""

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import urlsplit


class ReportData(HTMLParser):
    def __init__(self):
        super().__init__()
        self.collect = False
        self.parts = []
        self.count = 0

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("id") == "sync-template-data":
            self.collect = True
            self.count += 1

    def handle_endtag(self, tag):
        if tag == "script":
            self.collect = False

    def handle_data(self, data):
        if self.collect:
            self.parts.append(data)


def read_report(path):
    parser = ReportData()
    parser.feed(path.read_text(encoding="utf-8"))
    if parser.count != 1:
        raise ValueError("Existing report has missing or ambiguous preserved data; repair it before writing")
    data = json.loads("".join(parser.parts))
    for name, entry in data["history"].items():
        if hashlib.sha256(entry["text"].encode()).hexdigest() != entry["sha256"]:
            raise ValueError("History checksum mismatch: " + name)
    return data


def repository_identity(value):
    if value.startswith("git@") and ":" in value:
        host, path = value[4:].split(":", 1)
    else:
        parsed = urlsplit(value)
        if parsed.scheme not in ("https", "http", "ssh") or not parsed.hostname:
            raise ValueError("Use a canonical HTTPS or SSH repository URL")
        if parsed.password or parsed.query or parsed.fragment or (parsed.username and parsed.scheme != "ssh"):
            raise ValueError("Repository URLs must not contain credentials, queries or fragments")
        host, path = parsed.hostname, parsed.path
        if ":" in host:
            host = "[" + host + "]"
        if parsed.port and parsed.port != {"https": 443, "http": 80, "ssh": 22}[parsed.scheme]:
            host += ":" + str(parsed.port)
    return host.lower() + "/" + path.strip("/").removesuffix(".git")


def project_root(start):
    start = start.resolve()
    if not start.is_dir():
        raise ValueError("Project must be an existing directory")
    repository = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                                capture_output=True, text=True, check=False)
    candidates = (Path(repository.stdout.strip()).resolve(),) if repository.returncode == 0 else (start, *start.parents)
    for path in candidates:
        if (path / ".sync-template/config.json").is_file():
            return path
        if (path / ".git").exists():
            break
    raise ValueError("Template tracking is missing; confirm the template URL and initialize first")


def load_config(root):
    if any(path.is_symlink() for path in (root / ".sync-template", root / ".sync-template/config.json", root / ".sync-template/report.html")):
        raise ValueError("Tracking paths must be regular project-owned files, not symlinks")
    config = json.loads((root / ".sync-template/config.json").read_text(encoding="utf-8"))
    if config["schemaVersion"] != 1:
        raise ValueError("Unsupported tracking schema version")
    repository_identity(config["template"]["url"])
    expected = config["projectRepository"]
    if expected is not None:
        expected = repository_identity(expected)
    origin = subprocess.run(["git", "-C", str(root), "config", "--get", "remote.origin.url"],
                            capture_output=True, text=True, check=False)
    if origin.returncode == 0:
        actual = repository_identity(origin.stdout.strip())
        if expected != actual:
            raise ValueError("Config belongs to a different or unbound repository; confirm the mapping before writing")
    for field in ("lastCompared", "lastReconciled"):
        revision = config[field]
        if revision is not None:
            if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", revision["commit"]):
                raise ValueError("Revision must be a full Git SHA: " + field)
            for key in ("version", "date", "evidence"):
                if key not in revision:
                    raise ValueError("Missing revision field: " + key)
    if config["lastCompared"] is not None and type(config["lastCompared"].get("remoteVerified")) is not bool:
        raise ValueError("lastCompared requires a boolean remoteVerified")
    return config


def esc(value):
    return html.escape(str(value), quote=True)


def items(values):
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ValueError("Report lists must contain text")
    return "<ul>" + "".join("<li>" + esc(value) + "</li>" for value in values) + "</ul>" if values else "<p>None recorded.</p>"


def revision_label(revision):
    if revision is None:
        return "Unknown — no verified revision recorded"
    label = revision["version"] or "No verified release tag"
    return f'{label} · {revision["commit"]} · {revision["date"]}'


def render(root, report, history_paths=()):
    config = load_config(root)
    if report["status"] not in ("analyzed", "partial", "reconciled"):
        raise ValueError("Unknown report status")
    output = root / ".sync-template/report.html"
    history = read_report(output)["history"] if output.exists() else {}
    for relative in history_paths:
        source = (root / relative).resolve()
        source.relative_to(root)
        if source.suffix not in (".md", ".json", ".jsonc") or source.name.startswith(".env"):
            raise ValueError("History imports must be reviewed Markdown, JSON or JSONC records")
        with source.open(encoding="utf-8", newline="") as stream:
            entry = {"text": stream.read()}
        entry["sha256"] = hashlib.sha256(entry["text"].encode()).hexdigest()
        if relative in history and history[relative] != entry:
            raise ValueError("History already exists with different contents: " + relative)
        history[relative] = entry

    sections = []
    for concern in report["differences"]:
        sections.append(f'<article><h3>{esc(concern["area"])}</h3><p><strong>{esc(concern["decision"])}</strong></p>'
                        f'<p>{esc(concern["detail"])}</p><details><summary>Affected files ({len(concern["files"])})</summary>'
                        f'{items(concern["files"])}</details></article>')
    deviations = "".join(f'<tr><th scope="row">{esc(d["area"])}</th><td>{esc(d["decision"])}<p>{esc(d["reason"])}</p></td>'
                         f'<td>{items(d["paths"])}</td><td>{esc(d["evidence"])}</td></tr>' for d in config["deviations"])
    history_html = "".join(f'<details><summary>{esc(name)}</summary><p>Original text · SHA-256 {esc(entry["sha256"])}</p>'
                           f'<pre>{esc(entry["text"])}</pre></details>' for name, entry in history.items())
    result_sections = "".join(f'<section id="{key}"><h2>{title}</h2>{items(report.get(key, []))}</section>' for key, title in (
        ("applied", "Changes in this run"), ("pending", "Pending decisions and work"),
        ("checks", "Validation"), ("deployment", "Deployment follow-up"), ("limitations", "Comparison limits")))
    data = json.dumps({"report": report, "history": history}, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    compared = config["lastCompared"]
    verified = "Remote verified" if compared and compared["remoteVerified"] else "Remote not verified; latest status unknown"
    document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>{esc(root.name)} — Template comparison</title><style>
:root{{color-scheme:light dark;--bg:#f5f4ef;--ink:#172d30;--card:#fff;--line:#c4cfcb;--accent:#176254}}
@media(prefers-color-scheme:dark){{:root{{--bg:#142326;--ink:#e2ece7;--card:#203237;--line:#52706b;--accent:#b4e4d2}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}}
main{{max-width:1120px;margin:auto;padding:48px 24px}}h1{{font-size:clamp(2rem,5vw,3.4rem);line-height:1.1;margin:12px 0}}
h2{{font-size:1.45rem;margin:0 0 16px}}h3{{margin:0;font-size:1.1rem}}section{{margin-top:36px}}p{{margin:8px 0 16px}}
a{{color:var(--accent)}}nav{{display:flex;gap:18px;flex-wrap:wrap;padding:18px 0;border-block:1px solid var(--line)}}
article,details,header .metadata{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:18px;margin:12px 0}}
article details{{margin:16px 0 0}}summary{{cursor:pointer;font-weight:600}}summary:focus-visible,a:focus-visible{{outline:3px solid var(--accent);outline-offset:4px}}
dl{{margin:0;display:grid;grid-template-columns:170px 1fr;gap:8px 20px}}dt{{font-weight:650}}dd{{margin:0;overflow-wrap:anywhere}}
table{{width:100%;border-collapse:collapse;background:var(--card);font-size:.92rem}}th,td{{text-align:left;vertical-align:top;padding:14px;border:1px solid var(--line)}}
th{{font-weight:650}}td p{{margin-bottom:0}}ul{{padding-left:22px;margin:8px 0}}li,td,pre{{overflow-wrap:anywhere}}pre{{white-space:pre-wrap;font:13px/1.65 ui-monospace,monospace}}
.scroll{{overflow-x:auto}}.status{{font-size:.85rem;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);font-weight:700}}
@media(max-width:640px){{main{{padding:24px 16px}}dl{{grid-template-columns:1fr;gap:3px}}dd{{margin-bottom:12px}}}}
@media print{{details{{break-inside:avoid}}main{{max-width:none}}}}
</style></head><body><main><header><div class="status">{esc(report["status"])} · {esc(verified)}</div>
<h1>{esc(root.name)}</h1><p>Template comparison</p><p>{esc(report["summary"])}</p>
<div class="metadata"><dl><dt>Project</dt><dd>{esc(config["projectRepository"] or "Origin not configured")}</dd>
<dt>Template</dt><dd>{esc(config["template"]["url"])}</dd><dt>Selected ref</dt><dd>{esc(config["template"]["ref"])}</dd>
<dt>Compared revision</dt><dd>{esc(revision_label(compared))}</dd>
<dt>Last reconciliation</dt><dd>{esc(revision_label(config["lastReconciled"]))}</dd></dl></div></header>
<nav aria-label="Report sections"><a href="#differences">Differences</a><a href="#decisions">Intentional departures</a><a href="#pending">Pending work</a><a href="#checks">Validation</a><a href="#history">History</a></nav>
<section id="differences"><h2>Current differences</h2>{''.join(sections) or '<p>No differences recorded.</p>'}</section>
<section id="decisions"><h2>Intentional departures</h2><div class="scroll"><table><caption>Project decisions carried into the next sync</caption><thead><tr><th scope="col">Concern</th><th scope="col">Decision and reason</th><th scope="col">Paths</th><th scope="col">Evidence</th></tr></thead><tbody>{deviations}</tbody></table></div></section>
{result_sections}<section id="history"><h2>Historical records</h2><p>Preserved original notes describe their own date and repository. Their old commands and validation results are historical evidence.</p>{history_html or '<p>No legacy records imported.</p>'}</section>
<script type="application/json" id="sync-template-data">{data}</script></main></body></html>
'''
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(document)
        temporary.replace(output)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True, help="Reviewed temporary report JSON")
    parser.add_argument("--history", action="append", default=[], help="Reviewed project-relative legacy record")
    args = parser.parse_args()
    try:
        result = render(project_root(args.project), json.loads(args.input.read_text(encoding="utf-8")), args.history)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"Cannot write report: {error}\n")
    print(result)


if __name__ == "__main__":
    main()
