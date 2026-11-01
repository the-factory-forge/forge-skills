# Forge child releases

Use the note procedure below for a project whose verified direct parent is Forge
Template. Apply the version policy only when this guide is selected in the
child's release `guides`, or its own instructions explicitly adopt this policy.
Sync records alone do not opt an existing site into different versioning.
Read the sync report for pending new-site release setup before preparation. An
explicitly recorded setup blocker must be resolved even when no release config
exists; absence of that config is not a fallback to inherited source versioning.
The [shared contract](https://github.com/the-factory-forge/forge-specs/blob/main/openspec/specs/child-site-releases/spec.md)
owns this behavior. Resolve that checkout locally when available.

## Configure a new child

Replace inherited template publication settings with the child's verified GitHub
repository, version files and destination branch. Use the existing configuration
schema; this example assumes a `main` branch and `package.json` version:

```json
{
  "schemaVersion": 1,
  "repository": "owner/customer-site",
  "versionFiles": ["package.json"],
  "tag": { "create": true, "prefix": "v" },
  "push": { "automatic": false, "remote": "origin", "branch": "main" },
  "notes": { "storage": "github" },
  "github": { "mode": "direct", "automatic": true, "latest": "stable" },
  "guides": [
    "AGENTS.md",
    "https://github.com/the-factory-forge/forge-skills/blob/main/skills/release/references/child-sites.md"
  ]
}
```

Verify the repository/remote/branch rather than copying the example identity.
For a newly generated site with no child version history, initialize its version
to `M.m.0-rc.0` after verifying the reconciled foundation line below. This is an
unpublished child candidate, not an inherited Forge RC. If the origin or baseline
is unknown, remove inherited source publication settings, record setup as pending
and defer child release preparation; never invent a destination or foundation.

Existing sites adopt this policy only in an explicitly scoped migration. Preserve
their process, note storage/index, tags, publication settings and version files;
append this guide instead of replacing their configuration with the example.
Resolve conflicting project guidance or a version ahead of the foundation before
enabling it. Configuration edits do not request a release, push or deployment.

## Resolve the child version

Before applying the generic release increments:

1. Read the child's sync config and report using the
   [tracking contract](../../sync-template/references/records.md). Verify project
   identity and the configured direct parent. Use `lastReconciled`, with its
   current source evidence and intentional departures; `lastCompared` is not an
   adopted version. Partial work retains the last verified reconciled baseline.
2. Verify that baseline's release tag against its full source SHA and published
   GitHub Release, including prereleases. Read exact release records, not only
   GitHub's stable latest endpoint. A missing version, untagged/unreleased source,
   inaccessible metadata or mismatched tag blocks version preparation. A source
   package version, nearest ancestor tag or copied tracking record is insufficient.
3. Take `M.m` from that verified release. Read the child's authoritative current
   version and its own release tags, including remote tags. Inspect partial
   candidates first and reuse a matching candidate on resumption. Never import
   template patch/RC counters or reuse tags copied from the parent as child history.
4. Resolve one exact target using the selected project's version tooling and the
   rules below. Validate it before invoking that process; pass the exact version
   rather than letting a bump command recalculate it. A custom process that cannot
   honor the target needs repair before release mutation, not a fallback process.

| Child state and request                                                                          | Exact target rule                                                                                                                                                  |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Verified new-site initialization at `M.m.0-rc.0`, no child release tags; first `rc` or `next rc` | Keep `M.m.0-rc.0`. A first `patch` finishes `M.m.0`; later candidates use the normal child RC rules.                                                               |
| Current version already has adopted `M.m`; `patch`, `rc`, or an exact version                    | Use the shared release rules, constrained to `M.m`. Advance RCs from this child's highest candidate for the same base.                                             |
| Adopted `M.m` is newer; `patch`                                                                  | `M.m.0`, without another patch increment.                                                                                                                          |
| Adopted `M.m` is newer; `rc` or `next rc`                                                        | `M.m.0-rc.N`, starting at zero or following this child's highest existing RC for that base.                                                                        |
| Adopted `M.m` is newer; explicit version                                                         | Require `M.m.0` or an RC of that base for the first release in the new series. Preserve an explicitly requested valid RC number.                                   |
| `major`, `minor`, or either followed by `rc`                                                     | Resolve the requested SemVer increment from the child first; its major/minor must equal the adopted line. Then apply the new-series rules when entering that line. |
| Stable version or `patch` followed by `rc`                                                       | Resolve the stable base under these same constraints, then use the child's RC sequence for that base.                                                              |

Reject conflicting major/minor requests and downgrades; do not silently select a
different version or move a tag. Same-series patch requests can finish a child RC
as usual. A child may publish stable after its own required checks even when its
foundation remains an RC. Shared major/minor identifies the foundation, not
identical features or compatibility; disclose child-specific breaking changes.

For example: child `1.2.7` on Forge `1.2.9` releases patch `1.2.8`; after fully
adopting Forge `1.3.0-rc.8`, its next RC starts at `1.3.0-rc.0`. Its next candidate
is `1.3.0-rc.1`, and its stable release is `1.3.0` after child checks pass.

## Prepare child notes

Use the release skill's RC/stable comparison rule to select the previous **child**
release. Inspect its sync config/report from that tag, the candidate's records,
intermediate Git history and the full child source diff. The current report's
`applied` entries cover one run; they do not replace this release interval.
For a first release, describe the verified current baseline, customer capabilities
and omissions. If earlier adoption evidence is missing, review source to establish
what changed and disclose uncertainty rather than inventing a previous baseline.

Read the current bodies of relevant upstream releases across the verified source
interval, including RCs and release corrections. Resolve their tags to source
SHAs; select by source history and actual adopted scope, not publication dates or
version numbers alone. Check selective backports separately. If notes are
unavailable, report the missing evidence and leave the affected preparation
pending; sync may have recorded this limitation without blocking source work.

Write customer changes plus an **Updated Forge foundation** section when the
foundation changed (or a **Forge foundation** baseline for the first release):

- Identify the fully reconciled source tag, full SHA and upstream release link;
  describe selective changes beyond it separately without advancing that baseline.
- Summarize changes verified in the child diff once, deduplicating overlapping RC
  and stable notes. Skip features the child omits, unchanged/already-present work
  and reverted changes. Name applicable migrations, setup actions, checks and limits.
- Use child verification evidence. Upstream validation is context, not proof that
  this site passed. Registry changes require their separate adoption record.

Keep upstream history on GitHub and child notes in the child's configured store.
Rereading corrected upstream notes informs this candidate; it never authorizes
rewriting previously published child releases. With no foundation change, omit
the update section rather than repeating earlier changes.

Return to the release skill for checks, commit/tag, publication and retry handling.
All existing prerequisites apply, including installed `i-have-adhd`. `--local`
keeps remote phases off; a sync alone never invokes this release procedure.
