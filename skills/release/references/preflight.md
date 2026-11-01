# Read-only release preflight

Use `scripts/preflight.py` to collect repeatable local evidence before selecting
the release process. Python 3.9+ and Git are its only dependencies. It neither
requires nor selects a release CLI, executes configured commands, discovers
installed skills, contacts remotes, or writes release files or Git metadata.
The [configuration contract](configuration.md) remains authoritative.

## Invocation and result

```sh
python3 <skill-directory>/scripts/preflight.py --repo <repository> [--local] [--push] [--publish]
```

Supply an explicit destination with `--remote <name> --branch <branch>` only when
the user has selected it. Otherwise the helper uses configuration, then the
current branch's configured upstream. `--publish` represents an explicit
publication request; `--local` represents any preparation-only limit and wins
over every remote option and automatic setting. The flags describe the request,
never authorize work themselves. Natural-language constraints still apply.

The single JSON result contains:

- `blockers`: deterministic configuration or destination problems. Exit 1 means
  stop preparation and resolve them; never fall back from an invalid custom process.
- `reviewRequired`: remaining inspection, including scripts/hooks, installed
  skills, version formats, partial candidates and remote checks. Exit 0 always
  reports `review-required`, never approval to bump, commit, tag or publish.
- `read`: configuration, configured guides, preparation instructions and workflow
  paths. Read them and the repository instructions. Script argument arrays and
  required skill names appear in `reviewRequired`; their resources are not validated
  automatically because interpreting arbitrary commands would require execution.
- `destination` and `phases`: locally derived destination and requested phases.
  Git's effective **push** URL is checked against configured repository identity;
  raw URLs and Git error output are withheld to avoid exposing credentials.
- `versions`: top-level JSON `version` fields and plain `VERSION` contents.
  Unrecognized formats report `null` and require the project's reader. No SemVer
  validation, target resolution, bump or native-counter inference is performed.
- `git`: branch, full HEAD SHA, common metadata directory, shallow-history flag,
  staged/unstaged paths and ten recent local tags. Active clean/process filters
  cause status collection to be skipped: `statusCollected: false` and a null
  `changeCount` mean unknown worktree state, never a clean tree. Inspect those
  filters before running status manually. Submodule worktrees are always excluded
  and require separate inspection when present. `changesTruncated` means inspect
  the complete `git status --porcelain=v1` output. Recent tags are navigation hints;
  always inspect the complete relevant release sequence when resolving an RC or
  history base. A matching version or a local tag never proves release completion.

Only `{version}` and `{tag}` placeholders are accepted in note paths and command
arguments. Paths are checked before expansion, including symlinks; verify the
expanded note paths and actual custom script resources before mutation. Resolve
version disagreements from history and the partial diff before selecting a base.

## Manual checks and unsupported environments

If Python is unavailable, perform the same read-only checks using existing tools
and the configuration contract; installing Python is not a release prerequisite.
For unknown version formats, use the selected process's reader. For SSH aliases
or GitHub Enterprise destinations, verify the actual host/repository manually;
the helper recognizes canonical `github.com` HTTPS and SSH URLs. A helper
limitation can be resolved with equivalent verified evidence; malformed config,
missing resources, conflicting metadata or a genuine destination mismatch remain
blockers. Record any manual verification rather than treating a failed check as passed.

Configuration may be absent, or use the legacy path when the new one is absent.
Both paths present is an error. Missing configuration still requires discovering
project guidance before choosing the default process. Git repository overrides
such as `GIT_DIR` or `GIT_INDEX_FILE` must be unset for a reliable `--repo` snapshot.

Run preflight again when resuming or after configuration/destination changes.
It cannot establish that a custom command is safe, required checks passed, the
installed `i-have-adhd` was read, or remote refs/releases match. Complete those
skill steps before their corresponding actions. Local-only preparation loads
neither publication tooling nor remote phase references.

## Maintaining the helper

Run from the Forge Skills repository:

```sh
python3 -m unittest discover -s skills/release/scripts -p 'test_*.py'
```

Tests use temporary Git repositories and local fixtures, with no network or real
publication. Keep the schema, output interpretation and configuration contract in
agreement. Test invalid input, local-only precedence, resumptions and unchanged
files/index/refs whenever extending the helper. Inspect its source when changing
it; normal invocation needs only the JSON report and relevant project resources.
