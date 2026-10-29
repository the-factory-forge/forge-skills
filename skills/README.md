# Skill Catalog

The **Forge Skills** Codex plugin bundles the skills below. Add new skills as
`<skill-name>/SKILL.md` and list them here; the plugin discovers them automatically.

| Skill                                               | Purpose                                                                                                                                    | Scope                                                                                                                             |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| [update-dependencies](update-dependencies/SKILL.md) | Update packages and installed skills using destination tooling and validation.                                                             | Forge repositories and customer sites.                                                                                            |
| [release](release/SKILL.md)                         | Prepare an exact, major, minor, patch or RC release with notes, a commit and tag; `--push` pushes both automatically.                      | Repositories using SemVer releases; requires installed `i-have-adhd` and follows each project's version sources and notes format. |
| [factories-sync](factories-sync/SKILL.md)           | Check provider releases, then synchronize multiple sites with a pinned template revision, preserving customizations and recording results. | Existing Forge customer sites only; requires `forge-template`, `forge-registry` and `forge-specs`.                                |
| [sync-template](sync-template/SKILL.md) | Initialize template tracking, preserve intentional differences and reconcile later updates with one HTML report. | Projects with a confirmed Git template; first adoption in existing apps is analysis-only. |
| [push-design](push-design/SKILL.md) | Sync implemented UI into editable Penpot boards, organize plugin pages, and verify rendered results and component links. | Any project with a Penpot destination in `.structures/design.json`; implementation-to-design only. |

`factories-sync` was formerly named `bulk-sync` in Harness.
This repository owns its maintained source.

Registry synchronization stays in its source repository:

- [Registry updates](https://github.com/the-factory-forge/forge-registry/blob/main/.agents/skills/sync-from-forge-registry/SKILL.md): selected registry source into a site.

See the [repository README](../README.md) for installation and contribution rules.
