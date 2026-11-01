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
remain unverified concerns in the report until resolved.

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
  "inspection": {
    "date": "2026-11-01",
    "commit": "0123456789abcdef0123456789abcdef01234567",
    "workingTree": "clean",
    "dirtyPaths": []
  },
  "differences": [
    {
      "area": "Authentication",
      "classification": "intentional-departure",
      "decision": "Keep the public-only site",
      "detail": "Authentication and database integration were deliberately removed.",
      "evidence": "Confirmed project decision; inspected routes contain only public pages.",
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
Use focused feature summaries and complete affected path lists, including binary
paths. Exclude secrets, generated/runtime artifacts,
dependency trees and both tracking locations. `.env.schema` and sanitized examples
can be named; live env files must never be read or embedded.

### Release evidence for Forge children

Use the existing report fields; no extra manifest or upstream changelog is needed:

- `summary`: identify the verified before/after foundation tags and full SHAs,
  canonical release URLs and whether this run reconciled or only compared them.
  Use an explicit unknown/unreleased label where no release was verified.
- `applied`: summarize changes actually adopted in this run, with affected paths
  and source release references. Compare upstream notes with the child diff;
  skip already-present or omitted features. Link separately verified registry
  adoption rather than inferring it from a template version.
- `differences`: retain intentional departures and applicable unresolved work
  under the existing classifications. Partial adoption leaves `lastReconciled`
  at its last verified baseline.
- `deployment`, `checks`, `limitations`: record child-specific migration/setup
  actions, actual checks and missing upstream note metadata. Source notes never
  establish completed customer migration, validation or deployment.

Read the relevant upstream notes again on each sync. Use canonical credential-free
URLs as narrative text; preserve imported historical text unchanged. Before
refreshing, inspect the previous report and retain still-relevant unresolved
actions. This report describes one inspection, not the entire next child release.
The [release procedure](../../release/references/child-sites.md#prepare-child-notes)
reviews previous child tags, Git history and the full child diff to cover several
syncs, including changes made between uncommitted report refreshes.

### Classify remaining concerns

For new inputs, give every difference a `classification` and nonempty `evidence`.
Use `detail` to explain applicability to this project's installed features and
`decision` for the next action or behavior to retain. Evidence cites inspected
destination/target paths, a reproduced check, or a verified project decision;
an old failure alone does not confirm a current defect.

| Classification | Evidence needed | Pending section |
| --- | --- | --- |
| `confirmed-defect` | A current reproduced failure or demonstrably incorrect behavior | Confirmed defects |
| `applicable-update` | A specific pinned-source change, absent locally and relevant to an installed feature | Applicable missing updates |
| `intentional-departure` | A confirmed project decision and its current scope | Omitted; retained under differences and config decisions |
| `unverified-history` | What is unknown and the evidence needed to resolve it | Separate investigation group |

Missing files alone do not establish an update gap. For example, an intentional
public-only site does not need the template's intranet restored. An unknown
baseline stays null; inherited notes, package versions and dates cannot establish
how far behind the site is. Reclassify a concern only after checking its evidence.

The renderer derives pending groups from these concerns. Leave `pending` empty
in new inputs. For compatibility, existing free-text pending items and differences
without a classification still render as **unclassified follow-up**, requiring
fresh verification before action. Their embedded data is retained unchanged;
refresh current findings without rewriting preserved history.

### Record the inspected checkout

Classified input requires `inspection`: the ISO date (`YYYY-MM-DD`), destination
`commit` (full SHA or null if unverified), `workingTree` (`clean`, `modified`, or
`unverified`), and `dirtyPaths` (project-relative paths, excluding the records and
artifacts above). Capture this from the actual checkout being reported. Recheck
Git status before rendering; qualify excluded original-checkout work in
`limitations` when using an isolated worktree. Record starting-state details in
the run summary/checks if they differ from this inspection snapshot.

The displayed snapshot describes that inspection, not a live worktree status.
Older input without a snapshot is explicitly marked as needing fresh verification.
Historical dirty-state claims remain in history with their original provenance.

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
