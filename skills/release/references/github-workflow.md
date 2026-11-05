# Existing release workflow

## Check publication tools

Before editing release files for workflow publication, verify access to the exact
tag's workflow runs and release records.

## Observe the workflow

For `workflow`, inspect the configured workflow at the tagged SHA and monitor
that exact tag/commit. Verify hosted release, package publication, deployment and
announcements separately; a successful push is not evidence for any of them.
Retain application-consumed Markdown/index files, native version counters and
project-specific note filtering. If a job partially succeeds, inspect its output
and remote state before retrying. Do not replay successful package publishing or
notifications to repair a missing release. Do not race CI with direct creation.
If the tagged source predates the workflow, read [direct publication](github-direct.md) and use a direct repair only within the
existing publication authority and after verifying no workflow will create it.

Complete [result verification](github.md#verify-the-result).
