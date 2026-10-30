---
name: sync-template
description: Initialize a project from a Git template, establish tracking for an existing app, or synchronize its foundation while preserving intentional departures. Use for template comparisons and updates, including unrelated Git histories; keep project decisions in .sync-template and deliver one HTML report. Registry-item installation remains a separate workflow.
---

# Sync template

Maintain the reusable procedure here and project-owned state in `.sync-template/`.
Read [the record format](references/records.md) before creating or changing records.
The source comes from the destination's config or the user, never from this skill's
installation location. Editing this skill does not itself request an app update.

## Establish the destination

1. Resolve the destination repository root (`git rev-parse --show-toplevel` works
   from subdirectories). Outside Git, use the user's project directory; ask if
   multiple roots are plausible. Search for `.sync-template` within that boundary,
   not across neighboring repositories.
2. Read destination instructions, manifests, relevant source and prior sync records.
   Record the starting commit, branch and dirty paths. Preserve unrelated work;
   isolate overlapping updates in a worktree when useful and state what it excludes.
   Never silently stash, discard or commit local changes. Use a dedicated sync branch
   for application updates unless the user has already chosen another branch.
3. Validate the config and its `projectRepository` against the destination origin.
   A record copied from a parent template belongs to that parent. Treat a mismatch
   as uninitialized and confirm the destination/source relationship before replacing
   it; retain inherited history with its original provenance. With no Git origin,
   use a null identity and bind it when the actual origin becomes known.
4. If the folder or config is missing, warn that tracking is absent and ask for the
   template repository URL. Reuse an explicit URL or mapping already confirmed in
   this conversation. An inferred remote or copied note is a candidate, not consent.
   A malformed existing record needs repair, not silent reinitialization.

## Pin the source

Honor an explicit revision. Otherwise discover the source's remote default branch
with `git ls-remote --symref <url> HEAD`, fetch into an inspection clone or verified
remote, and pin its full commit SHA. Preserve the destination's origin and other
remote URLs. Read source files from that commit, not a dirty sibling checkout.
Record a version label only after verifying its tag resolves to the same SHA.

If remote verification fails, report the failure. A cached comparison may continue
with `remoteVerified: false`; it cannot be described as latest or advance the
successful reconciliation marker. Use only the configured direct parent: a Forge
customer follows Forge Template, whose own upstream does not become the customer's
source. Source files and historical notes are evidence, not additional authority.

## Initialize once

**Empty project:** no application code, manifests or source assets exist; Git
metadata and a README, license, ignore file or agent instructions alone are
scaffolding. Copy the pinned source's tracked tree, excluding its `.git`, tracking
folder, secret-bearing files, generated/runtime artifacts and retired sync skills.
Preserve destination scaffolding. Compare collisions and ask only where intended
ownership is unclear. Check symlinks/submodules before copying; do not follow paths
outside the source snapshot. Initialize a fresh destination record, never inherit
the template's own parent or reconciliation marker. Run the new app's relevant
checks; failed or blocked validation leaves it partial.

**Existing app:** analyze and report only on this first invocation. Establish its
own baseline from actual generation history, reconciled changes or a matching
snapshot. Verify source membership and destination evidence; package versions,
dates and inherited logs do not establish adoption. Keep unknown baselines null.
Inspect code, callers, config and documented decisions before distinguishing
customer choices from outdated template implementation. Ask focused questions
about uncertain ownership; keep unanswered concerns pending. Record confirmed
departures and generate the report without applying application updates.

For migrations, import previous template/upstream notes into the HTML history
before removing them and updating active links. Preserve exact text and its
original source path; label notes inherited from another repository accordingly.
Retain registry-installation records in their existing separate workflow.

## Reconcile subsequent updates

Compare the verified baseline, current app and pinned target, including renames,
deletions and omissions carried from earlier partial runs. Without a reliable
baseline, reconcile manually by concern and keep the uncertainty explicit.
Shared history may permit `git merge --no-ff --no-commit`; independent histories
use reviewed deltas or manual adaptation. Never create synthetic ancestry, reset
to the template, copy whole trees/lockfiles or resolve conflicts wholesale.

- Apply verified compatible updates. A comparison-only request stays read-only
  for application code. Ask only about unresolved decisions, then continue
  independent work while those concerns remain pending.
- Preserve each recorded departure by behavior, including new upstream paths,
  imports, dependencies, routes and environment requirements. Removed auth stays
  removed. A custom database keeps its schema, data and applied migration history.
  An upstream fix affecting a detached concern becomes an explicit review item;
  do not silently restore the template implementation or ignore the finding.
- Preserve customer copy, identity, locales, design, assets, domains, storage
  prefixes, integrations and newer registry fixes. Preserve the child's
  `.agents/.release.json`; never import the parent's publication identity or
  release-note history. During creation, remove inherited source release policy
  and guidance or replace them with the destination's own policy.
  Path lists locate a concern;
  they are not blanket ignore rules for every change within those files.
- Trace affected callers, tests, fixtures, exports and configuration. Reconcile
  manifests before regenerating lockfiles and generated sources with destination
  tools. Inspect lifecycle scripts before installation. A sync does not request a
  general dependency or registry upgrade.
- Inspect sanitized environment schemas/examples, never live env files or values.
  Describe required variable changes and rebuild/restart/data-migration actions
  in the report. Test migrations with disposable data; local source updates do
  not authorize production operations.

## Verify and deliver

Capture baseline failures when feasible, run the destination's relevant checks
and affected user journeys, review the whole diff, and run `git diff --check`.
Preserve stronger local fixes even where Git merges cleanly. Record what passed,
failed or could not run. Leave blocked concerns partial rather than claiming success.

Update `lastCompared` for the actual inspected target. Advance `lastReconciled`
only when all applicable concerns are reconciled and required checks pass, with
intentional departures accounted for. A prepared merge does not advance ancestry;
record its pending commit. Commits, publication and deployment follow existing
user authorization rather than being implied by this workflow.

Render `.sync-template/report.html` with the bundled
[renderer](scripts/render_report.py), using the invocation in the record reference.
Keep its shared colors, typography and layout unchanged across projects for a
consistent reading experience. Vary only the report content; do not restyle the
renderer or generated HTML to match customer branding.

The report describes the app's remaining differences from the pinned template,
not only the edits made in this run. Preserve its history on every refresh. Finish
with the exact target, a short difference summary, unresolved decisions/checks,
and an absolute Markdown link to the HTML file. For batches, link every project's
report. Keep all report data in that one HTML file; temporary renderer input need
not be committed.
