# Skill Catalog

The **Forge Skills** Codex plugin bundles the skills below. Add new skills as
`<skill-name>/SKILL.md` and list them here; the plugin discovers them automatically.

| Skill | Purpose | Scope |
| --- | --- | --- |
| [update-dependencies](update-dependencies/SKILL.md) | Update packages and installed skills using destination tooling and validation. | Forge repositories and customer sites. |
| [release](release/SKILL.md) | Prepare an exact, major, minor, patch or RC release with notes, a local commit and tag, without pushing. | Repositories using SemVer releases; follows each project's version sources and notes format. |
| [factories-sync](factories-sync/SKILL.md) | Synchronize multiple sites with a pinned template revision, preserving each site's customizations and recording its result. | Existing Forge customer sites only; requires `forge-template` and `forge-spec`. |

`factories-sync` was formerly named `bulk-sync` in Harness.
This repository owns its maintained source.

Provider-owned synchronization skills stay in their source repositories:

- [Registry updates](https://github.com/the-factory-forge/forge-registry/blob/main/.agents/skills/sync-from-forge-registry/SKILL.md): selected registry source into a site.
- [Template synchronization](https://github.com/the-factory-forge/forge-template/blob/main/.agents/skills/sync-forge-template/SKILL.md): template foundation into a site.

See the [repository README](../README.md) for installation and contribution rules.
