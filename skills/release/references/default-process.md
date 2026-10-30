# Default local release process

Read this only when no configured or documented project release process exists.
Projects with their own process use its tooling and do not run these commands.

## Check the global release tool

Only after selecting the default process, and before resolving a version or editing release files, run `command -v commit-and-tag-version` in a normal shell and confirm it points to a global installation. Resolve the binary symlinks to its installed package, read that package's `package.json` version, and require `commit-and-tag-version --version` to match it. Some releases infer the current project's version or print `unknown`; neither verifies the tool. Report and repair a mismatch during authorized tool setup before continuing. Use that global CLI directly for every release command; repository-local binaries and `npx` or package-manager execution wrappers are not substitutes.

If the global tool is missing, warn the user that `commit-and-tag-version` must be installed globally before preparing the release. Provide the [upstream installation command](https://github.com/absolute-version/commit-and-tag-version#as-global-bin) and offer to run it:

```sh
npm install --global commit-and-tag-version
```

Install only with the user's authorization, reusing any authorization already given. If it is installed but unavailable on `PATH`, explain that issue instead of reinstalling it. Recheck the global command and its version after setup succeeds; until then, leave release files, commits and tags untouched.

## Update and commit

Inspect commands and hooks before running them; use only local preparation.
For GitHub-only notes add `--skip.changelog` to dry-run and actual commands.
Keep their notes outside tracked source. Preserve required local validation
hooks skipped by manual committing/tagging; run them against the candidate first.
Native-counter hooks are not checks.

Use existing `commit-and-tag-version` configuration, or its standard package-file
defaults when they match the project. For an untouched previous version:

1. Run `commit-and-tag-version --dry-run --release-as <version> --skip.commit --skip.tag`.
   Confirm the exact target. Do not add `--prerelease rc`, which can advance an
   already resolved RC target.
2. Repeat without `--dry-run` to generate the candidate. Review all changes and
   run required checks and `git diff --check` against those generated files.
3. Stage only exact release files and repository-stored notes. Commit only those
   paths with `git commit --only`, preserving unrelated staging. Isolate unrelated
   edits sharing a release file before committing. Create the annotated tag only
   when `tag.create` is true, after the candidate passes verification.

For other authoritative version formats, update the exact target manually; use
the verified global tool's SemVer dependency for version resolution. Do not add
package files, tool configuration or native files just to fit the default.

If any version file or native counter already changed for this candidate, skip
the bump. Verify all release artifacts and repair only missing updates manually,
then check and commit/tag only if missing. Reuse an existing matching release
commit/tag; do not replace it or repeat native-counter increments. If the expected
counter cannot be recovered from the prior release or partial diff, resolve that
before editing it.

Follow project commit/tag conventions, defaulting to `chore(release): <version>`
and the configured prefix plus version (`v<version>` without configuration).
Return to the shared skill for final verification and authorized publication.
