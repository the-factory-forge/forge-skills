# AI agent start here

This repository owns shared agent skills for The Corner Factory SA projects.
Read [README.md](README.md) and the [catalog](skills/README.md), then load only
the skill and resources relevant to the task.

## Ownership and navigation

Registry synchronization belongs to `forge-registry`; template synchronization,
batch synchronization, dependency updates and releases belong here. Each project
owns its `.sync-template/` source, decisions and reports. Follow the shared
[provider-owned skills contract](https://github.com/the-factory-forge/forge-specs/blob/main/openspec/specs/the-forge/spec.md#requirement-provider-owned-skills).

Resolve actual checkouts from the workspace or Git remotes; the `forge-specs`
checkout may be named `forge-spec`. Use canonical links when local sources are
unavailable and report inaccessible context. For specs and ADRs, follow the
[Registry guide](https://github.com/the-factory-forge/forge-registry/blob/main/AGENTS.md#shared-forge-specifications)
for plugins, the [Template guide](https://github.com/the-factory-forge/forge-template/blob/main/AGENTS.md#shared-forge-specifications)
for applications, and [Forge Specs](https://github.com/the-factory-forge/forge-specs/blob/main/AGENTS.md)
for contracts constraining both providers. Reference their records here.

## Editing skills

Follow [Add or change a skill](README.md#add-or-change-a-skill) for naming,
frontmatter, portable resources, catalog updates and publication metadata.
Preserve workflow intent, applicability and authorization boundaries. Read each
consuming project's instructions, scripts and configuration before operating on it.
Before moving a skill, check references and consumers and preserve installed customizations.
Validate changed frontmatter, links and discovery; safely exercise changed helpers
and review a representative request when behavior changes. Report actual checks and limits.
Keep secrets, customer data and generated output out of this library. Markdown
skills need no application scaffolding or runtime dependencies.
