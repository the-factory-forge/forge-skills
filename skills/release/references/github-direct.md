# Direct GitHub publication

Read the tool checks before editing release files when direct publication is planned.
Execute publication only under the [shared GitHub phase](github.md).

## Check publication tools

For a requested direct GitHub phase, discover an authenticated connector with
release create/read/update support. A read-only GitHub connector is insufficient.
Otherwise check `command -v gh`, `gh --version`, `gh auth status` and access to
`gh repo view <owner/repository> --json nameWithOwner,viewerPermission` before
editing release files. Check `gh release create --help` and `gh release edit --help`
for `--verify-tag`, notes-file, draft, prerelease and latest controls. Never print
tokens. If unavailable, report the missing tool/access and offer official
[GitHub CLI setup](https://cli.github.com/); install only with authorization.
Local-only work does not require GitHub write access.

## Create or resume the release

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

After publication, complete [result verification](github.md#verify-the-result).
