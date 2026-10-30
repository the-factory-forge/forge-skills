---
name: factories-sync
description: Synchronize multiple existing Forge customer projects from forge-template first, then forge-registry, assessing each project's own baseline, partial updates, customizations and local work. Use when updating all dependent sites or a named group of child projects; not for creating sites or updating forge-template from its starter upstream.
---

# Factories sync

Coordinate template and registry updates across the requested dependent Forge
projects. For each child, sync from `forge-template` first, then `forge-registry`:
the pinned template defines how registry items integrate with the host application.
`forge-skills` owns this bulk workflow and the shared
[per-project sync-template procedure](../sync-template/SKILL.md). Locate the
template, registry and
[forge-specs](https://github.com/the-factory-forge/forge-specs) (commonly checked out
as `forge-spec`) from the workspace and verified remotes. Shared-library
availability does not make this workflow applicable to non-Forge projects.

## Verify provider releases first

- Before starting the sync, check both `forge-template` and `forge-registry`.
  Read each provider's release/version conventions and fetch its canonical
  default branch and tags. Verify that its latest version tag is published on
  that remote and resolves to the latest commit on that branch, peeling annotated
  tags to their commits. A local-only tag or a tag on an earlier commit does not
  satisfy this check; a stale local checkout cannot establish the latest commit.
- If either provider's latest version tag does not resolve to its branch tip,
  is missing, or cannot be verified, warn the user. Show the affected
  repository, latest tag and tagged SHA, branch-tip SHA, and unreleased commits
  or verification failure as available. Ask for explicit confirmation to proceed
  with that state and wait before changing any child. Read-only inventory may
  continue while awaiting confirmation. A general sync request or an explicitly
  selected template target does not waive this check.
- Record both providers' release status and any confirmed exception in the run
  notes. If the user chooses to release first, recheck both providers afterward.
  Proceed when both checks pass or the user has explicitly accepted the reported
  exceptions; this check does not authorize creating releases or moving tags.

## Inventory first

- Discover dependent repositories in the requested workspace and any supplied
  project list. Confirm provenance from remotes, generation history, source and
  sync records. Do not classify the template, registry, specs, Harness or shared
  skills library as child websites.
  Report inaccessible or ambiguous dependents instead of silently excluding them.
- Honor an explicit template release, branch or commit; otherwise resolve the
  canonical template's default branch. Fetch and verify the requested target,
  recording one immutable SHA for the batch unless the user requests distinct
  targets. If remote verification fails, label the target as locally available
  only; do not silently substitute a different revision.
- Read the shared `sync-template` skill from this library and the template's
  `AGENTS.md` from the pinned target, together with relevant shared contracts
  and ADRs from `forge-specs`. Plugin behavior and
  ADRs belong to `forge-registry`; template application specs and ADRs belong to
  the pinned `forge-template`. Follow each owner's `AGENTS.md` to load relevant
  guidance instead of assuming these records live in the shared specs repository.
  Inspect template source at the same revision; a dirty or differently checked-out
  template is not the target.
  If required guidance is unavailable, continue inventory and report the blocker
  before integrating affected sites.
- Before changing any child, record its path, branch, starting SHA, dirty files,
  established template base and evidence, previous partial syncs, enabled modules,
  runtime/toolchain, customer-owned identity and required verification commands.
  Keep the working inventory in the run notes, not a permanent duplicate registry.

## Plan each child independently

**Children may be at different states, even when their last recorded target is
the same. A batch shares a destination, never an assumed starting state.**

- Read each child's instructions, manifests, source, `.sync-template/config.json`
  and `.sync-template/report.html`. Follow the shared skill's missing/copied-record
  initialization flow; an existing app without valid tracking receives analysis
  and a report on its first run, with application updates left for a subsequent run.
  Verify recorded claims against current files. A targeted Portless
  update, cherry-pick or partial sync does not establish a fully reconciled base.
- Determine a reliable comparison base separately for every child. Use recorded
  reconciliations, verified snapshot matches or actual ancestry as evidence.
  When no base is known, reconcile manually by concern; do not borrow a sibling's
  base, infer one from dates or package versions, or manufacture shared ancestry.
- Review that child's base-to-target delta, including deletions and renames, and
  revisit earlier unresolved changes. Classify each concern as already present,
  applicable, intentionally different, or blocked. Trace callers and related
  configuration before choosing an adaptation.
- Carry the child's expected plugin capabilities into the registry stage. A
  template contains only its own installed subset; its registry provenance does
  not establish adoption of customer-only plugins. Verify earlier exclusions
  against customer decisions rather than treating an agent's omission as intent.
- Preserve client content, routes/locales, domains, package identity, assets,
  styles, custom modules, service configuration and migration history. A site
  that removed the intranet must remain public-only. A site with blog, Drive or
  other modules must retain them even if the template no longer includes them.
- Reconcile the toolchain and installed auth flow with the target template,
  honoring confirmed departures in the project's config. An unexplained difference
  alone does not establish intentional customization. Migrate outdated login/signup/session
  and
  intranet integration to the current flow, preserving accounts, applied migrations
  and custom modules by default. If the user confirms databases are disposable,
  use a fresh schema baseline instead of compatibility migrations, retain required
  module tables and shipped seed content (including SQL-embedded assets), and record
  who will reset which environments. Inspect data inserts before replacing migration
  chains; an empty schema alone may lose content that the site ships with. Authorization to
  prepare a reset does not mean it has been executed. Retain a divergent auth/toolchain behavior only with evidence
  of an explicit customer requirement; do not invent an exception to avoid migration.
- Inspect uncommitted work before editing. Prefer isolation when independent;
  account explicitly for excluded changes. If the sync depends on local work,
  merge compatible changes deliberately without stashing, discarding or committing
  it. Stop only the overlapping change if its intended result cannot be determined.
- Use the shared `sync-template` procedure and a dedicated sync branch. Keep existing
  authorized branch/worktree choices. Do not reset a client to the template,
  copy entire trees or lockfiles, resolve conflicts wholesale, or run the same
  patch blindly across every child. Reuse a transformation only after verifying
  its preconditions independently in every destination; already-applied work is
  a no-op, and unexpected source must be reported rather than overwritten.

## Integrate related changes together

Inspect the pinned target's implementation rather than freezing package versions
or field names into this workflow. For identity and development-origin changes:

- Distinguish the environment's infrastructure slug from the public display name.
  Inspect actual consumers: `ENV.SITE_NAME` can name a Docker container and S3
  prefix while a separate `SITE_NAME` constant owns branding/auth/email/metadata.
  Preserve both identities. For renamed storage settings, retain existing object
  prefixes or provide a compatible transition; never strand uploaded objects by
  silently substituting the package name. Update examples and deployment guidance.
- Keep each package name unique for Portless; preserve any existing correct slug.
  Adapt development scripts, environment defaults and site-specific launchers
  together. Preserve explicit deployment origins and existing test-server ports.
  Do not read or rewrite local secret-bearing env files; use Varlock's agent-safe
  validation and report stale override setup needs without exposing values.
- Apply related template fixes in tooling, routing, security, optional services
  and documentation when applicable. Preserve custom integrations and reconcile
  manifests before regenerating lockfiles with each site's pinned package manager.
  Verify the build/start boundary: runtime auth, mail and storage configuration must
  still work when absent during the image build. In Varlock, nonsecret server fields
  may need dynamic resolution as well as the correct SSR injection mode.
  Do not turn a template sync into an unrelated latest-dependency upgrade.

## Sync registry after template integration

- Complete and verify each child's applicable template changes before starting
  its registry sync. If template work is analysis-only or blocked, leave that
  child's registry stage pending and continue with independent children.
- Then follow the registry-owned
  [sync-from-forge-registry procedure](https://github.com/the-factory-forge/forge-registry/blob/main/.agents/skills/sync-from-forge-registry/SKILL.md)
  from the verified registry checkout. Use the pinned template's `AGENTS.md`,
  linked integration guidance and implementation to reconcile registry items with
  the updated host. Honor an explicit registry target; otherwise use the verified
  release or explicitly accepted unreleased revision. Record its immutable SHA
  and any accepted release exception.
- Refresh only the child's applicable installed items and required dependencies,
  preserving its exclusions and custom integrations. Keep registry adoption
  evidence in the registry procedure's separate record. Report both stages and
  link that record from the child's template report; a template sync alone does
  not establish registry adoption. Mark the registry stage not applicable when
  no registry items are installed.
- For a catch-up after an earlier registry-first batch, inspect the final child
  tree before proposing more changes. Preserve compatible completed work and
  repair demonstrated source or host-integration gaps. Do not rebuild the branch
  stack merely to reproduce the preferred order. Keep the selected provider SHAs
  and existing authorization unless the user changes the target or scope.

## Report environment changes for VPS migration

For every child whose environment contract, sanitized example, Compose settings,
build arguments or runtime consumption changes, print a per-project migration
table in the handoff and save it in that child's sync record. Do not hide these
actions behind a generic “environment updated” summary or a link alone.

Include the variable name, change (added/renamed/removed/default or meaning changed),
old-to-new mapping, required VPS/Dokploy action, and whether the change needs an
image rebuild, service restart/recreation, or an explicitly separate data migration.
Distinguish development-only variables such as `PORTLESS_URL` from production
requirements. For `VITE_*` settings, inspect build arguments and browser bundling;
a runtime restart alone may not update the public bundle.

Derive this report from each child's own before/after files and consumers, not
another child's delta. Show variable names, confirmed nonsecret defaults and
placeholders only. Never read or print live env files or secret values. Say when
deployed values are unverified. For renamed settings, state compatibility fallbacks
and when the old key can be removed. Preserve S3 prefixes and existing container
identities where required; never suggest changing a storage prefix without an
explicit data-migration plan. Code completion does not mean VPS actions are done.

## Verify and record separately

- Capture relevant baseline failures before edits when feasible. Run each child's
  own lint/type checks, applicable unit tests, environment validation and affected
  browser journeys. Retain stronger local correctness/security fixes when updating
  shared code; document them so a later sync does not reintroduce the defect. A passing sibling proves nothing about another child's state.
- Let existing E2E commands own their production build/server lifecycle. Serialize
  suites that share a port or database resource. Do not stop another site's server
  or proxy. Use disposable local services when a test needs a database or storage;
  never run migrations or send real email against production as validation.
- Check customer identity, localized public URLs, metadata, enabled/removed modules
  and changed auth/storage flows. Review the whole diff against the child's
  starting state, including cleanly applied changes, and run `git diff --check`.
- Verify the final combined child revision after both stages. Use the registry
  procedure's per-capability evidence to distinguish installed source, connected
  host integration, verified journeys, confirmed exclusions and pending work.
  Passing source tests or migration checks alone does not prove an exposed host
  feature. Record the tested revision and actual skipped/blocked checks; rerun
  affected journeys after later runtime edits, while documentation-only changes
  may reuse results with evidence that the relevant runtime files are unchanged.
- Update each child's `.sync-template/config.json` and render its single
  `.sync-template/report.html` through the shared skill. Include source/target,
  starting SHA, baseline evidence, remaining differences, applied changes,
  preserved local work, unresolved items and actual check results. Preserve
  historical notes already embedded in the report.
- Mark incomplete children **partial**. Do not advance a fully-synchronized marker
  past unresolved work or treat a compared target as proof of integration. Carry
  intentional differences and outstanding omissions into the next reconciliation.
- Link every child's HTML report in the handoff. Report a compact per-project
  result, including any skipped or inaccessible
  project and its reason. One blocked child must not prevent independent work on
  the others. Respect existing authorization for commits, pushes, PRs, deployment
  and production changes; the bulk scope alone does not authorize publication.
  Show missing expected capabilities and data-preparation steps directly in the
  handoff, even when source installation passed. Keep evidence in the existing
  template report and linked registry receipt; do not add a parallel inventory.
