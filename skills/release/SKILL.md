---
name: release
description: Prepare a repository release from an exact version or a major, minor, patch, or rc request. Follow .agents/.release.json for version files, notes, tagging, pushing and automatic GitHub publication; preserve existing CI and application release notes.
---

# Release

A release request authorizes its version/files and local commit, plus an annotated
tag unless repository configuration disables tagging. Read `.agents/.release.json`
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

## Require i-have-adhd

Before starting or resuming release preparation, locate the installed `i-have-adhd` skill in the active agent's project, user or plugin skill locations and read its `SKILL.md`. This is a required dependency for every release, including partially prepared releases.

If the skill is missing or cannot be read, refuse to prepare the release and leave release files, versions, commits and tags untouched. Explain that `i-have-adhd` is required and propose installing it from [its upstream repository](https://github.com/ayghri/i-have-adhd). Give the user this copyable command to run from the target repository, selecting their current agent when prompted:

```sh
npx skills add ayghri/i-have-adhd --skill i-have-adhd
```

Install only with the user's authorization, reusing any authorization already given. Recheck discovery and read the installed skill before continuing; an online copy does not satisfy the installed prerequisite. If the agent requires explicit activation, have the user invoke `i-have-adhd` using their agent's skill syntax. Apply its guidance to release communication and notes.

## Check the global release tool

Before resolving a version or editing release files, run `command -v commit-and-tag-version` in a normal shell and confirm it points to a global installation. Resolve the binary symlinks to its installed package, read that package's `package.json` version, and require `commit-and-tag-version --version` to match it. Some releases infer the current project's version or print `unknown`; neither verifies the tool. Report and repair a mismatch during authorized tool setup before continuing. Use that global CLI directly for every release command; repository-local binaries and `npx` or package-manager execution wrappers are not substitutes.

If the global tool is missing, warn the user that `commit-and-tag-version` must be installed globally before preparing the release. Provide the [upstream installation command](https://github.com/absolute-version/commit-and-tag-version#as-global-bin) and offer to run it:

```sh
npm install --global commit-and-tag-version
```

Install only with the user's authorization, reusing any authorization already given. If it is installed but unavailable on `PATH`, explain that issue instead of reinstalling it. Recheck the global command and its version after setup succeeds; until then, leave release files, commits and tags untouched.

## Check publication tools

For a requested direct GitHub phase, discover an authenticated connector with
release create/read/update support. A read-only GitHub connector is insufficient.
Otherwise check `command -v gh`, `gh --version`, `gh auth status` and access to
`gh repo view <owner/repository> --json nameWithOwner,viewerPermission` before
editing release files. Check `gh release create --help` and `gh release edit --help`
for `--verify-tag`, notes-file, draft, prerelease and latest controls. Never print
tokens. If unavailable, report the missing tool/access and offer official
[GitHub CLI setup](https://cli.github.com/); install only with authorization.
Local-only work does not require GitHub write access. For workflow publication,
verify access to the exact tag's workflow runs and release records instead.

## Establish the release

- Read the configuration, its guides, repository instructions, release guide, and copywriting guidance when present. Verify the configured repository against the destination remote before any release mutation. Inspect its scripts and configuration to identify version sources, release-note locations, tag conventions, and validation commands.
- Inspect the branch, worktree, current version, recent release tags, and commits since the previous release. Use the project's authoritative version source, such as `VERSION` or configured package files; private package versions and legacy tags may belong to a separate version sequence. An unpublished local candidate is not evidence of a completed release.
- Read `packageFiles` and `bumpFiles` when the project configures `commit-and-tag-version`. Otherwise follow its documented version files and manual release process; do not assume every package version tracks the repository release.
- Resolve missing or conflicting release metadata before choosing a base; inspect the last release commit and partial release changes. Inspect hooks for side effects and record native build counters, such as Android `versionCode`, only when the release updates them.
- Check whether the target version is already present before running a bump command. Never bump a second time just because a release commit or tag is missing.
- Identify which steps publish packages and which create the hosted release entry (such as GitHub Releases). A pushed tag or published npm version does not create that entry by itself; inspect the repository automation and any remaining manual steps.

## Resolve the target version

Accept bump names case-insensitively and strip an optional leading `v` from a version. Resolve one exact target before writing notes or changing files. Use the SemVer dependency from the same global `commit-and-tag-version` installation for validation and increments. Resolve it relative to that global package rather than the project's `node_modules`; do not install another version tool.

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

- For an RC, summarize changes since the previous release tag on this branch. For a stable release, summarize changes since the previous stable tag, including work delivered in RCs. If this is the first release in the project's version sequence, summarize the relevant history. Write for the project's users or consumers, including breaking integration changes and required migrations when relevant.
- Follow `notes.storage` and the configuration reference. GitHub-only notes stay in private Git metadata and never enter a release commit. Otherwise use the project's established release-note path and format, discovered from its release guide, existing notes, or release-note consumer. Update an index only if the project uses one, preserving its schema and ordering. Only when neither configuration nor an existing notes convention applies, use a root `CHANGELOG.md`. Let configured changelog tooling generate its version entry instead of adding a duplicate manually.
- Write the notes using the loaded `i-have-adhd` skill, preserving the project's required format, copywriting guidance and character limits; verify character limits with `wc -m`. Group detail for readability without omitting breaking changes, migrations, validation evidence or known limitations.
- Prepare store copy only for projects that require it or when requested. Follow their platform, format, and length requirements; omit RC store copy unless asked.

## Update and commit

Inspect release commands and hooks before running them; use only steps that stay within local preparation. Add `--skip.changelog` for GitHub-only notes and `--skip.tag` when `tag.create` is false, consistently in dry-run and actual commands below. Only repository-stored notes are staged. Run required candidate checks before the release commit/tag; hooks that increment native counters are not validation commands.

### Projects configured for commit-and-tag-version

If the configured package files still contain the previous version:

1. Run `commit-and-tag-version --dry-run --release-as <version> --commit-all` with the exact resolved target. This works for both stable and RC versions. Do not add `--prerelease rc`: it can silently advance an exact RC target when a tag already exists. Confirm the dry-run version matches the target.
2. Check staged and unstaged changes. Do not use `--commit-all` if unrelated staged files exist. Do not include unrelated edits in configured release files.
3. Stage only the prepared release-note artifacts.
4. Rerun the same command without `--dry-run`. This lets `commit-and-tag-version` update its configured files and changelog, commit the staged notes with them, and create the tag.

If unrelated files are staged, generate the release with `--release-as <version> --skip.commit --skip.tag` instead. Review the diff, stage only the exact release files, and use `git commit --only` with those paths before creating the annotated tag. Preserve unrelated staging. If unrelated edits share a release file, resolve how to isolate them before committing.

### Other projects and partially prepared releases

Follow the project's documented local release process to update its authoritative version files and notes. Do not add package files, release-tool configuration, or native application files solely to fit this workflow.

If the authoritative version already matches the target, skip the bump. Verify all release files and notes, and repair only missing updates. Preserve unrelated edits and staging; if unrelated edits share a release file, isolate them before committing. Where tooling has not already done so, commit only the exact release files with `git commit --only`, then create an annotated tag on that release commit when `tag.create` is true. Follow the project's commit and tag conventions, defaulting to `chore(release): <version>` and the configured prefix plus version (`v<version>` without configuration). If the release commit already exists, verify and reuse it. Do not replace an existing tag unless the user explicitly asks.

## Verify

- Confirm the release notes and any existing index contain the target once, in the project's expected order and format.
- Run `git diff --check` before committing.
- Confirm the authoritative version files contain the target version and any native build counters changed exactly as required, without a second increment.
- Run the project's relevant release checks. Inspect validation hooks and avoid commands that bump versions again, publish, or deploy.
- Confirm the release commit and, when tagging is enabled or an existing tag is being published, the annotated tag and its exact target locally. GitHub-only notes must include that full SHA before publication.
- Report any unrelated worktree changes and the actual completed phases. For local-only work, give the private notes path and state that nothing was pushed or published.

## Push when requested

After local verification succeeds, honor `--push`, an explicit publication request, or `push.automatic` automatically, including for an already prepared release. `--local` or an explicit preparation-only request wins. If tagging is disabled and no tag is being published, push only the exact commit refspec; direct GitHub publication still requires a verified existing tag. Resolve the destination remote and branch from the user's request or the repository's documented push configuration/upstream. If the destination is missing or ambiguous, ask only for that information.

Before pushing, inspect the remote branch and exact tag. If the tag already
resolves to the release commit and that commit is reachable from the destination
branch, skip the push and continue the missing publication phase. A newer remote
branch must not be rewound to repair an old release. If only the tag is missing
and the commit is already on the branch, push only that exact tag. Reject a
conflicting remote tag without moving it.

When both refs need publishing, push the verified release commit and its exact
tag together using explicit refspecs:

```sh
git -c push.followTags=false push --atomic <remote> <release-commit>:refs/heads/<destination-branch> refs/tags/<tag>:refs/tags/<tag>
```

This includes any unpushed ancestors required by the release commit. Do not push other branches or tags, force-push, or move an existing tag. If the push fails or the remote does not support atomic pushes, stop and report the failure while preserving the local release for retry. Do not bump, recommit, or retag to retry a push.

Verify a newly pushed branch points to the release commit and the remote tag matches the local tag and resolves to that commit. When reusing an already published commit on a newer branch, verify reachability instead of requiring the branch to move backward. Report the destination, commit and tag as pushed only after both are confirmed; if verification is unavailable, report the push result and uncertainty.

## Complete GitHub publication

Read `github.mode` and `github.automatic`. With an authorized push and automatic
publication enabled, continue through this phase without another confirmation.
An explicit publication request also authorizes it. `disabled` has no hosted
phase. A missing release is repaired at its existing version/tag, not by bumping.

### Existing workflow

For `workflow`, inspect the configured workflow at the tagged SHA and monitor
that exact tag/commit. Verify hosted release, package publication, deployment and
announcements separately; a successful push is not evidence for any of them.
Retain application-consumed Markdown/index files, native version counters and
project-specific note filtering. If a job partially succeeds, inspect its output
and remote state before retrying. Do not replay successful package publishing or
notifications to repair a missing release. Do not race CI with direct creation.
If the tagged source predates the workflow, use a direct repair only within the
existing publication authority and after verifying no workflow will create it.

### Direct creation

Use a capable connector when available, otherwise the authenticated GitHub CLI.
Read the release for the exact tag first, distinguishing an authenticated 404
from network/authentication errors. Preserve an existing published release; verify
it instead of overwriting it. Reuse a draft only when its repository/tag, source,
notes and assets match the prepared candidate. Conflicting data stops the attempt.

After verifying the remote tag's peeled full SHA equals the release commit,
create a draft with the reviewed body. The following is the RC form; for a stable
release use `--prerelease=false` and `--latest` according to repository policy.
Historical backfills always use `--latest=false`.

```sh
gh release create <tag> --repo <owner/repository> --verify-tag \
  --title <title> --notes-file <absolute-notes-path> \
  --draft --prerelease --latest=false
```

`--verify-tag` checks existence, not its resolved SHA. Do not pass `--target` to
silently create a missing tag. Read back the complete draft and attach only
required, authorized assets. Apply any project-specific stable-immutability gate.
Publish the verified draft with the same flags (shown for an RC):

```sh
gh release edit <tag> --repo <owner/repository> --verify-tag \
  --draft=false --prerelease --latest=false
```

On a timeout or failed creation, read remote state before retrying. Resume the
matching draft or verify the already published entry; never recreate a successful
release, bump again, move a tag, or rerun package publishing to repair metadata.
See [create](https://cli.github.com/manual/gh_release_create) and
[edit](https://cli.github.com/manual/gh_release_edit) for the official CLI contract.

### Verify the result

Read the exact release and remote tag again. Confirm repository, tag, peeled full
SHA, published (not draft) state, title, complete notes and asset inventory.
Every SemVer prerelease must be marked prerelease and must not replace the stable
latest release; verify the latest endpoint/state separately. Return the release
URL only as published after these checks. If automation is still running or a
check is unavailable, report that phase as pending or unverified. Publication
does not establish customer adoption or deployment.
