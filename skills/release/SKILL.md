---
name: release
description: Prepare a repository release from an exact version or a major, minor, patch, or rc request. Use the project process from .agents/configs/.release/config.json or existing release guidance before the commit-and-tag-version default; preserve existing CI and application release notes.
---

# Release

A release request authorizes its version/files and local commit, plus an annotated
tag unless repository configuration disables tagging. Read `.agents/configs/.release/config.json`
using [the configuration contract](references/configuration.md) before mutations.
It controls the destination, note storage and automatic push/GitHub phases.
Explicit preparation-only requests and `--local` keep all remote phases off.

Accept exact versions or `major`, `minor`, `patch`, `rc`, `next rc`, and a stable
version or bump followed by `rc`. `--push` authorizes the verified commit/tag push
and configured automatic GitHub publication without another confirmation.
An explicit request to publish also authorizes those necessary phases. Treat
these as skill options, never version inputs or release-CLI flags. Creating or
editing the skill/configuration does not run a release.

Inspect and disclose tag-triggered publishing, deployment and announcements.
An authorized push may run existing CI; do not add separate deployment, package
publication, notification or store-upload commands without matching authority.
Without configuration, preserve local preparation and the existing `--push`
behavior; direct GitHub creation needs an explicit publication request.

## Inspect local state

Run the bundled read-only preflight from any directory, using the installed skill's
absolute script path and the target repository:

```sh
python3 <skill-directory>/scripts/preflight.py --repo <repository>
```

Pass `--local` for preparation-only, `--push` for a push request, and `--publish`
for explicit publication; `--local` wins. Pass `--remote`/`--branch` only for an
explicit destination override. These flags describe authority already given;
the helper grants none and performs no release actions.

Resolve `blockers` before mutations and complete `reviewRequired` alongside the
steps below. Exit zero means local evidence collected, not release readiness.
Read the reported configuration and guides; inspect custom scripts and installed
skills. The snapshot does not replace target resolution, complete release history,
partial-release inspection, live remote verification or required checks. Rerun on
resumption. Read [preflight details](references/preflight.md) for unavailable Python,
unsupported formats/destinations, truncated output, errors, or helper maintenance.

## Select the local release process

Read the configuration contract and repository release guidance before checking
tool dependencies. Select exactly one local preparation process:

1. A configured nonempty `process` list, in order: load its instructions and
   skills and inspect every script before resolving the target or mutating files.
2. Otherwise, an existing documented project release procedure or release script.
   Inspect its entrypoint and hooks; a version-tool dependency alone is not a process.
3. Otherwise, the [default process](references/default-process.md), which requires
   the verified global `commit-and-tag-version` installation described there.

A custom process uses its own prerequisites and version tooling; it does not need
Forge's global release CLI. An unavailable or invalid declared process stops
preparation rather than falling back. The selected process owns local version
updates, checks, commit and tag. The shared version rules, notes, verification and
authorized publication below still apply; configuration does not authorize extra
remote actions. Inspect custom commands for publishing hooks before running them.

## Require i-have-adhd

Before starting or resuming release preparation, locate the installed `i-have-adhd` skill in the active agent's project, user or plugin skill locations and read its `SKILL.md`. This is a required dependency for every release, including partially prepared releases.

If the skill is missing or cannot be read, refuse to prepare the release and leave release files, versions, commits and tags untouched. Explain that `i-have-adhd` is required and propose installing it from [its upstream repository](https://github.com/ayghri/i-have-adhd). Give the user this copyable command to run from the target repository, selecting their current agent when prompted:

```sh
npx skills add ayghri/i-have-adhd --skill i-have-adhd
```

Install only with the user's authorization, reusing any authorization already given. Recheck discovery and read the installed skill before continuing; an online copy does not satisfy the installed prerequisite. If the agent requires explicit activation, have the user invoke `i-have-adhd` using their agent's skill syntax. Apply its guidance to release communication and notes.

## Check publication tools

Before editing release files, load the checks for the planned hosted phase:

- Direct publication: [tool and access checks](references/github-direct.md#check-publication-tools).
- Workflow publication: [workflow access checks](references/github-workflow.md#check-publication-tools).
- Local-only preparation: no publication tools or GitHub write access required.

## Establish the release

- Read the configuration, its guides, repository instructions, release guide, and copywriting guidance when present. Verify the configured repository against the destination remote before any release mutation. Inspect its scripts and configuration to identify version sources, release-note locations, tag conventions, and validation commands.
- Inspect the branch, worktree, current version, recent release tags, and commits since the previous release. Use the project's authoritative version source, such as `VERSION` or configured package files; private package versions and legacy tags may belong to a separate version sequence. An unpublished local candidate is not evidence of a completed release.
- Read `packageFiles` and `bumpFiles` when the project configures `commit-and-tag-version`. Otherwise follow its documented version files and manual release process; do not assume every package version tracks the repository release.
- Resolve missing or conflicting release metadata before choosing a base; inspect the last release commit and partial release changes. Inspect hooks for side effects and record native build counters, such as Android `versionCode`, only when the release updates them.
- Check whether the target version is already present before running a bump command. Never bump a second time just because a release commit or tag is missing.
- Identify which steps publish packages and which create the hosted release entry (such as GitHub Releases). A pushed tag or published npm version does not create that entry by itself; inspect the repository automation and any remaining manual steps.

## Resolve the target version

For a project tracking Forge Template, read the [child-release guide](references/child-sites.md)
for adoption-aware notes. Apply its version constraints before the rules below
only when the project's release guides or instructions select that policy.
Other projects retain their existing version sequence. Inspect and reuse a
matching partially prepared candidate before deriving a new target on resumption.

Accept bump names case-insensitively and strip an optional leading `v` from a version. Resolve one exact target before writing notes or changing files. Use the selected project process's version tooling for validation and increments. Only the default process uses the SemVer dependency resolved from its verified global `commit-and-tag-version` installation; do not install another version tool.

| Request                                          | Target                                                                               |
| ------------------------------------------------ | ------------------------------------------------------------------------------------ |
| Exact version, such as `3.0.0` or `3.0.0-rc.2`   | Use that version exactly.                                                            |
| `major`, `minor`, or `patch`                     | Apply the corresponding SemVer increment to the authoritative current version.       |
| `rc` or `next rc`, while already on `X.Y.Z-rc.N` | Keep `X.Y.Z` and advance the RC number.                                              |
| `rc`, while on a stable version                  | Start the next patch candidate, such as `2.2.3` to `2.2.4-rc.0`. State this default. |
| A stable version plus `rc`, such as `3.0.0 rc`   | Start or continue candidates for that exact base, such as `3.0.0-rc.0`.              |
| A bump plus `rc`, such as `minor rc`             | Resolve the stable target with that bump, then start or continue its RC sequence.    |

For a derived RC, use one more than the highest RC number for that base in the current version and local release tags for this version sequence, or `0` if none exists. Never renumber an explicitly supplied RC version. A stable SemVer increment can finish an active prerelease: `minor` or `patch` on `2.2.0-rc.8` yields `2.2.0`; `major` yields `3.0.0`.

Reject malformed versions, conflicting inputs, and downgrades. If the target already has a tag, verify whether the local release is complete and reuse it instead of moving the tag or choosing a different version; with `--push`, continue through verification and pushing below. If no target or bump was supplied, ask for one. Otherwise state the resolved target and continue without another confirmation.

## Prepare the notes

- For Forge Template children, follow the [child note procedure](references/child-sites.md#prepare-child-notes): review the entire child release interval and reread relevant upstream releases, including RCs. Summarize only verified adopted changes and retain customer changes and checks.
- For an RC, summarize changes since the previous release tag on this branch. For a stable release, summarize changes since the previous stable tag, including work delivered in RCs. If this is the first release in the project's version sequence, summarize the relevant history. Write for the project's users or consumers, including breaking integration changes and required migrations when relevant.
- Follow `notes.storage` and the configuration reference. GitHub-only notes stay in private Git metadata and never enter a release commit. Otherwise use the project's established release-note path and format, discovered from its release guide, existing notes, or release-note consumer. Update an index only if the project uses one, preserving its schema and ordering. Only when neither configuration nor an existing notes convention applies, use a root `CHANGELOG.md`. Let configured changelog tooling generate its version entry instead of adding a duplicate manually.
- Write the notes using the loaded `i-have-adhd` skill, preserving the project's required format, copywriting guidance and character limits; verify character limits with `wc -m`. Group detail for readability without omitting breaking changes, migrations, validation evidence or known limitations.
- Prepare store copy only for projects that require it or when requested. Follow their platform, format, and length requirements; omit RC store copy unless asked.

## Update and commit

Run the selected project process in its declared order, or use the
[default process](references/default-process.md#update-and-commit) when no project
process exists. Custom preparation replaces the default bump/commit/tag commands;
never run both. Run required candidate checks before committing/tagging, then
verify the created commit and tag under Verify below.

On resumption, inspect completed artifacts and perform only missing steps. A
script that always bumps cannot repair an already matching version: use its
repair mode or the documented manual repair. Stop on failure and preserve the
candidate; a failed custom process does not authorize switching to the default.

## Verify

- Confirm the release notes and any existing index contain the target once, in the project's expected order and format.
- Run `git diff --check` before committing.
- Confirm the authoritative version files contain the target version and any native build counters changed exactly as required, without a second increment.
- Run the project's relevant release checks. Inspect validation hooks and avoid commands that bump versions again, publish, or deploy.
- Confirm the release commit and, when tagging is enabled or an existing tag is being published, the annotated tag and its exact target locally. GitHub-only notes must include that full SHA before publication.
- Report any unrelated worktree changes and the actual completed phases. For local-only work, give the prepared notes path and state that nothing was pushed or published.

## Push when requested

After local verification, honor `--push`, an explicit publication request, or
`push.automatic`; `--local` and explicit preparation-only requests take precedence.
For an authorized push, follow [push verification and retry rules](references/push.md),
including when the local release is already prepared. Then complete any authorized
GitHub phase below, even when the refs were already published.

## Complete GitHub publication

With an authorized push and `github.automatic`, or an explicit publication request,
follow [GitHub publication](references/github.md) for the configured mode.
`github.mode: disabled` has no hosted phase. Without configuration, direct creation
requires an explicit publication request. Repair a missing release at its existing
version/tag. Report only verified phases; keep pending or unavailable checks explicit.
