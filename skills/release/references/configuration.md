# Repository release configuration

Read `.agents/.release.json` before any release mutation. This is an agent-readable
contract, not a command runner or a `commit-and-tag-version` configuration file.
Repository instructions still own validation, native counters and copywriting.

```json
{
  "schemaVersion": 1,
  "repository": "owner/repository",
  "versionFiles": ["package.json"],
  "tag": { "create": true, "prefix": "v" },
  "push": { "automatic": false, "remote": "origin", "branch": "main" },
  "notes": { "storage": "github" },
  "github": { "mode": "direct", "automatic": true, "latest": "stable" },
  "guides": ["AGENTS.md"]
}
```

## Fields and defaults

Require `schemaVersion: 1`, a GitHub `owner/repository` identity and nonempty
`versionFiles` when the file exists. Reject malformed JSON, unsupported fields,
wrong types or conflicting metadata before changing versions, commits or tags.
Paths are repository-relative and must stay inside it. Expand only `{version}`
and `{tag}` in note paths; do not execute configuration text as shell commands.

| Field | Meaning when present; default when omitted |
| --- | --- |
| `versionFiles` | Authoritative version sources. Read all of them and resolve disagreement. Additional bump files remain owned by the existing release tool/configuration. |
| `tag.create` | Create an annotated tag during preparation; defaults to `true`. If `false`, use `--skip.tag` with the release tool and do not create a tag manually. Publication needs an independently verified existing tag; never let GitHub create one implicitly. |
| `tag.prefix` | Prefix before the exact version; defaults to `v`. Must agree with existing tool configuration. |
| `push.automatic` | A release invocation also requests pushing after local checks; defaults to `false`. `--push` overrides this to true; `--local` or an explicit preparation-only request overrides it to false. |
| `push.remote`, `push.branch` | Exact push destination. Omission uses the documented upstream; resolve ambiguity before writing. Verify the remote matches `repository`. |
| `notes.storage` | `github` keeps notes out of tracked source; `repository` retains files consumed by the project. Omission preserves the existing convention. |
| `notes.path` | Required for `repository`, e.g. `docs/releases/{tag}.md` or `app/public/releases/{tag}.md`. Omit for `github`. |
| `notes.index` | Optional existing index to maintain for repository notes. Preserve its schema; do not create one for GitHub-only notes. |
| `github.mode` | `direct` creates/publishes through an available release tool; `workflow` observes the existing repository automation; `disabled` performs no hosted-release action. Defaults to `disabled`. |
| `github.automatic` | Complete the configured GitHub publication after an authorized push, without another confirmation; defaults to `false`. An explicit publication request also authorizes this phase. This never independently authorizes a push. |
| `github.workflow` | Required for `workflow`: the existing workflow path to inspect and monitor for the exact tag/SHA. Do not create a competing release workflow. |
| `github.latest` | `stable` allows a new stable release to become latest; `never` leaves latest unchanged. Defaults to `stable`. Every SemVer prerelease is always prerelease and never latest. Historical backfills must preserve the current stable latest release. |
| `guides` | Optional local paths or HTTPS links with required project release/check/copy guidance. Read them; they do not authorize extra publication destinations. |

`github.automatic: false` cannot suppress workflows triggered by a push. Inspect
actual triggers and disclose their effects before pushing. Do not claim this
configuration is enforced by CI or by the release CLI.

## Authorization and inherited configuration

The user's release request and matching repository configuration together define
the requested actions. Editing or merely discovering this file runs nothing.
Explicit user limits take precedence. Without configuration, preserve the skill's
legacy behavior: local commit/tag; `--push` pushes refs and observes existing CI,
but direct GitHub creation requires an explicit publication request.

Before preparation, compare `repository` with the actual destination remote,
normalizing HTTPS/SSH spelling and an optional `.git` suffix. A copied template
configuration must never publish into its parent's repository. On mismatch,
stop release mutations and resolve the destination with the user; do not silently
rewrite it or treat a parent remote as the destination. New customer setup removes
or replaces this source-only configuration. Template sync preserves the child's
own release policy and does not restore the parent's release history or identity.

## Notes that stay outside the repository

For `notes.storage: github`, keep the preparation copy in Git's private metadata:
resolve `git rev-parse --git-common-dir`, then use `release-notes/<tag>.md` there.
Keep the file through retries and report its absolute path for a local handoff.
Never stage it, recreate `docs/releases`, add a root changelog, or create a remote
draft during a local-only request. Suppress generated changelogs with
`--skip.changelog` in both dry-run and actual release commands; inspect hooks for
other note generation. An optional existing application changelog is not removed
without a migration request.

After committing, include the verified full source SHA in the prepared body.
Use absolute source links pinned to that commit; a local file's relative links
will not resolve correctly in a GitHub Release. Publication reads this exact body.
The published GitHub Release is the canonical note record; corrections there must
be explicit and retain source identity. GitHub notes remain editable even when
tags/assets are immutable. Do not promise an immutable note snapshot.

When migrating existing notes, map every file to its verified remote tag/SHA,
retain its validation limitations, and preserve existing releases. Inspect after
an ambiguous failure before retrying. Delete a tracked note only after reading
back its complete published replacement. Update live links; historical evidence
may link to the old file at a pinned commit. Do not rewrite tags or Git history.
