# The Forge Skills

Shared agent skills for **Forge** projects, maintained by **The Corner Factory SA**.
This repository packages our own workflows as an installable Codex plugin.

Status: active. Audience: contributors and AI agents working on Corner projects.

## Scope

- Keep reusable skills and their required resources here.
- Keep project-specific context, configuration, and workflows in their project.
- Keep company requirements in
  [the-corner-factory-specs](https://github.com/the-corner-inc/the-corner-factory-specs),
  shared Forge contracts and ADRs in [forge-specs](https://github.com/the-factory-forge/forge-specs),
  and Up4it requirements in [up4it-spec](https://github.com/the-corner-inc/up4it-spec).
  Plugin behavior, showroom rules and their ADRs belong to
  [forge-registry](https://github.com/the-factory-forge/forge-registry/blob/main/AGENTS.md#shared-forge-specifications);
  application, stack and website-creation specs and their ADRs belong to
  [forge-template](https://github.com/the-factory-forge/forge-template/blob/main/AGENTS.md#shared-forge-specifications).
  Keep reusable prompts and agent roles in
  [Harness](https://github.com/the-corner-inc/harness).
- A product-specific skill can live here when several projects need it; its
  description must make that scope clear. Forge rules do not apply to every project.

## Layout

```text
AGENTS.md                           Instructions for maintaining this library
.agents/plugins/marketplace.json     Codex marketplace catalog
.codex-plugin/plugin.json            Forge Skills plugin metadata and version
assets/forge-logo.png               Forge logo for the plugin listing and composer
skills/README.md                    Skill catalog
skills/<skill-name>/SKILL.md         One entry point per skill
```

See the [skill catalog](skills/README.md). Each skill may include `scripts/`,
`references/`, or `assets/` when its workflow needs them.

This is a Markdown skill library: there is no application to run, package to
build, or application test suite. It needs no `package.json`, `src/`, or runtime
dependencies. Executable helpers, when added, must include a runnable check.

## Install in Codex

Once these files are published to GitHub, add the marketplace and install the
plugin:

```sh
codex plugin marketplace add the-factory-forge/forge-skills
codex plugin add forge-skills@forge
```

For unpublished changes, run from this checkout instead:

```sh
codex plugin marketplace add .
codex plugin add forge-skills@forge
```

Restart the Codex app, then look for **Forge** in the Plugins marketplace picker
and **Forge Skills** in its plugin list. GitHub installation requires read access
to this repository.

The plugin bundles every skill under `skills/`; each skill's description defines
when it applies. Codex installs a cached copy, so source edits require a plugin
refresh or reinstall before testing them in a new chat.

The packaging follows the single-bundle approach in
[Matt Pocock's skills](https://github.com/mattpocock/skills), using the supported
[Codex plugin and marketplace formats](https://developers.openai.com/plugins/build/plugins).

## Install individual skills in a project

Install only the skills relevant to the destination project. With Node.js and
the [Skills CLI](https://github.com/vercel-labs/skills), run from that project's
root after the skills have been published to this repository:

```sh
npx skills add the-factory-forge/forge-skills --list
npx skills add the-factory-forge/forge-skills
```

The second command lets you select skills and agents. Installation is scoped to
the current project by default; omit `--global`. Prefer a project's existing
Skills CLI script when it already has one, and retain its generated skill source
lockfile and discovery paths according to that project's conventions.

For unpublished local changes, use a local checkout as the source:

```sh
npx skills add /path/to/forge-skills --list
npx skills add /path/to/forge-skills
```

The path above is a placeholder for your checkout. Without an installer, an agent
can read the chosen `skills/<skill-name>/SKILL.md` directly and follow its linked
resources. Cloning this library alone does not install skills into other projects.

Maintain shared instructions here and refresh consuming projects through their
existing skill tooling. Preserve local customizations when updating an installed
skill; project-specific instructions remain in the consuming repository.

## Migrating from Harness

`factories-sync` (formerly `bulk-sync`) now lives here. Harness no longer contains
a `skills/` directory. Update references and reinstall it from this source in
projects that use the batch workflow:

```sh
npx skills add the-factory-forge/forge-skills --skill factories-sync
```

Use the local checkout path instead of the GitHub source until these changes are
published. Select the project's existing agent targets. Before replacing an
installed skill, preserve and compare local customizations. Let the installer
update its source lockfile, then verify the source, discovery paths, and linked
resources. Run only the command for each skill the project needs. Moving the
library does not automatically migrate existing installations.

`update-dependencies` is maintained here for Forge projects. It reads the
destination's tooling, compatibility rules and checks.
`release` replaces `release-version` and generalizes Up4it's `release-preparation`
workflow: version selection, release notes, a local commit and tag. Add `--push`
to push the release commit and tag and complete configured GitHub publication after verification.
Repository-owned `.agents/.release.json` selects version files, tagging, note storage
and publication through the agent or existing CI; `--local` keeps preparation local.
See the [configuration contract](skills/release/references/configuration.md).
It follows each destination's version sources and release-note conventions,
including repositories such as `forge-template` without a mobile application layout.
The original Up4it skill remains in place pending separate cleanup.

`sync-template` replaces the old repository-local `sync-template` and
`sync-forge-template` procedures. It reads the destination's `.sync-template/config.json`
and maintains one `.sync-template/report.html` with current differences and history.
It initializes an empty project from its chosen source; the first run in an existing
app establishes tracking without updating application code. Later runs reconcile
safe changes while preserving confirmed departures. `factories-sync` uses this
same procedure for each child while retaining its provider-release checks.

Use the shared [sync-template skill](skills/sync-template/SKILL.md) directly from
this checkout until publication and plugin refresh. Keep project-specific decisions
in the destination; do not recreate repository-local copies. Registry synchronization
remains in `forge-registry`. Up4it's existing dependency skill is outside this migration.

After publication, use this repository as the source when reinstalling the common
skills, preserving local edits and letting the installer update source locks and
discovery paths. Until then, use the actual local checkout path as shown above.
Existing customer and global installations are not changed by moving the source.

## Add or change a skill

1. Check the catalog for an existing workflow to extend.
2. Create `skills/<skill-name>/SKILL.md`, with a lowercase hyphenated name under
   64 characters. The frontmatter name must match the folder:

   ```markdown
   ---
   name: skill-name
   description: Describe the task this skill handles and when to use it.
   ---

   # Skill title

   Write the workflow, its required inputs, and how to verify the result.
   ```

3. Keep the skill portable: use the destination's own instructions and tooling,
   discover repository paths, and link authoritative specifications instead of
   duplicating them. Do not include credentials or customer data.
4. Add the skill to the catalog. Validate frontmatter, relative links, and
   installer discovery; exercise changed helpers with safe inputs. For a workflow
   change, check a representative request and report anything untested.
5. Bump `version` in `.codex-plugin/plugin.json` when publishing skill changes.
   The plugin already discovers `skills/`; adding a skill does not require another
   marketplace entry. Keep the plugin name and marketplace name stable for updates.

Copyright (c) 2026 The Corner Factory SA. Licensed under the [MIT License](LICENSE).
Free to use, modify, and redistribute, including commercially, provided the
copyright and permission notices are retained. Provided "as is", without warranty;
see the license for the liability disclaimer.
