# Complete GitHub publication

Read `github.mode` and `github.automatic`. With an authorized push and automatic
publication enabled, continue through this phase without another confirmation.
An explicit publication request also authorizes it. `disabled` has no hosted
phase. A missing release is repaired at its existing version/tag, not by bumping.

Load only the selected mode:

- `workflow`: [observe the existing workflow](github-workflow.md).
- `direct`: [create or resume the release](github-direct.md).

## Verify the result

Read the exact release and remote tag again. Confirm repository, tag, peeled full
SHA, published (not draft) state, title, complete notes and asset inventory.
Every SemVer prerelease must be marked prerelease and must not replace the stable
latest release; verify the latest endpoint/state separately. Return the release
URL only as published after these checks. If automation is still running or a
check is unavailable, report that phase as pending or unverified. Publication
does not establish customer adoption or deployment.
