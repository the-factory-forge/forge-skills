# Project records

Track `.agents/configs/.sync-template/config.json` and `.agents/configs/.sync-template/report.html` in the project.
Keep source checkouts, scratch input and caches outside this folder. The config
owns machine-readable provenance and durable decisions; the HTML owns the current
comparison, pending work, checks and preserved narrative history.

## Migrate legacy tracking

Before initialization or rendering, check the destination root's legacy
`.sync-template/` directory as well as `.agents/configs/.sync-template/`.

- If only the legacy directory exists, first verify that `.agents/`,
  `.agents/configs/`, the tracking directory and its files are not symlinks.
  Validate its config and repository identity and check the report's preserved
  history, then move the whole directory to `.agents/configs/.sync-template/`,
  creating missing parents. Preserve file bytes, additional records, revision
  markers and decisions. A copied parent record retains its inherited provenance;
  after relocation, follow the copied-identity procedure below before replacing it.
- If both locations exist, compare their provenance, decisions and report history.
  Reconcile them before writing; keep both intact while conflicts remain unresolved.
  Never select one silently or overwrite a report to make the move succeed.
- Update active links and path references in the destination, including ignore or
  tooling rules that would hide the new records. Verify the moved files and history
  before removing any superseded copies. Keep historical text and its original path
  labels unchanged. A path migration does not reset tracking or imply app updates.

The renderer writes only the new location and refuses to render while the legacy
directory remains, so a missed migration cannot silently discard report history.

## Config version 1

```json
{
  "schemaVersion": 1,
  "projectRepository": "https://github.com/owner/application",
  "template": { "url": "https://github.com/owner/template", "ref": "refs/heads/main" },
  "lastReconciled": null,
  "lastCompared": null,
  "deviations": []
}
```

`projectRepository` is the credential-free canonical origin URL, or null before
an origin exists. Compare equivalent HTTPS/SSH Git URLs after normalizing `.git`
and trailing slashes. Never store workstation paths or credentials. Ref names
come from discovery or user selection; `main` above is only an example.

Both revision fields accept null or an object with `commit` (full SHA), `version`
(verified tag or null), `date` (ISO date/time), and `evidence` (nonsecret explanation
or source reference). `lastCompared` also requires `remoteVerified` (boolean).
Retain the last good reconciliation after partial/failed work. A historical record
can establish a reconciled comparison point without shared Git ancestry, provided
its source revision, committed destination work and retained departures are verified.
Do not confuse this with deployment, byte-for-byte equality or a Git merge.

Each deviation has `area`, `paths` (project-relative paths/patterns), `decision`,
`reason`, and `evidence`. Include removed features even when their paths no longer
exist. Describe the behavior to retain and its integration boundaries. Existing
documents or explicit user decisions can confirm intent; unexplained differences
belong in the report's pending section until resolved.

When config identity mismatches the destination, copy its exact bytes to a temporary
project-relative record such as `.agents/configs/.sync-template/inherited-config.json`. After
confirming the mapping, establish the destination config, import that snapshot
with `--history .agents/configs/.sync-template/inherited-config.json`, verify preservation, and
remove the temporary snapshot. Only config and report remain maintained files.
Unknown schema versions or malformed records require investigation before writing.

## HTML input and generation

Prepare reviewed JSON in a temporary file with these fields:

```json
{
  "summary": "Initialization only; no application updates applied.",
  "status": "analyzed",
  "differences": [
    {
      "area": "Authentication",
      "decision": "Keep the public-only site",
      "detail": "Authentication and database integration were deliberately removed.",
      "files": ["absent: src/intranet/auth/auth.ts"]
    }
  ],
  "applied": ["Initialized tracking"],
  "pending": [],
  "checks": ["Remote target verified; application tests not run for metadata-only changes."],
  "deployment": ["No deployment performed."],
  "limitations": []
}
```

`status` is `analyzed`, `partial` or `reconciled`. Paths are relative to the project;
file lists describe added, absent, changed or relocated files without source diffs.
Use focused feature summaries and complete affected path lists. Keep uncertain
technical drift separate from confirmed deviations. Include dirty-worktree
qualification and binary paths, but exclude secrets, generated/runtime artifacts,
dependency trees and both tracking locations. `.env.schema` and sanitized examples
can be named; live env files must never be read or embedded.

Resolve the following script relative to the installed skill, not the destination:

```sh
python3 /path/to/skill/scripts/render_report.py --project /path/to/project --input /tmp/report-input.json
```

For the one-time legacy import, add repeated `--history` arguments with explicit
project-relative Markdown/JSON/JSONC paths, for example `--history docs/template-sync.md`.
The renderer stores original text and SHA-256 checksums inside the HTML and
preserves them on refresh. Reimporting identical text is a no-op; changed text
under an existing history name is rejected. Review imports for secrets first.
Verify history before deleting originals. Rewrite active links to the report's
`#history` section; immutable historical commit links remain valid as written.

The renderer only writes the report, atomically; it never edits config or source,
advances baselines, fetches repositories or decides which changes are safe.
Run `python3 -m unittest discover -s /path/to/skill/scripts -p 'test_*.py'`
after changing it.
