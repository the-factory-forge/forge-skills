# The Forge Skills

Shared agent skills for every **The Corner Factory SA** project. This repository
is the canonical home for reusable workflows maintained across the company.

Status: active. Audience: contributors and AI agents working on Corner projects.

## Scope

- Keep reusable skills and their required resources here.
- Keep project-specific context, configuration, and workflows in their project.
- Keep company requirements in
  [the-corner-factory-specs](https://github.com/the-corner-inc/the-corner-factory-specs),
  Forge requirements in [forge-spec](https://github.com/the-factory-forge/forge-spec),
  and Up4it requirements in [up4it-spec](https://github.com/the-corner-inc/up4it-spec).
  Keep reusable prompts and agent roles in
  [Harness](https://github.com/the-corner-inc/harness).
- A product-specific skill can live here when several projects need it; its
  description must make that scope clear. Forge rules do not apply to every project.

## Layout

```text
AGENTS.md                     Instructions for maintaining this library
skills/README.md              Skill catalog
skills/<skill-name>/SKILL.md   One entry point per skill
```

See the [skill catalog](skills/README.md). Each skill may include `scripts/`,
`references/`, or `assets/` when its workflow needs them.

This is a Markdown skill library: there is no application to run, package to
build, or application test suite. It needs no `package.json`, `src/`, or runtime
dependencies. Executable helpers, when added, must include a runnable check.

## Use in a project

Install only the skills relevant to the destination project. With Node.js and
the [Skills CLI](https://github.com/vercel-labs/skills), run from that project's
root after the skills have been published to this repository:

```sh
npx skills add the-corner-inc/the-corner-factory-skills --list
npx skills add the-corner-inc/the-corner-factory-skills
```

The second command lets you select skills and agents. Installation is scoped to
the current project by default; omit `--global`. Prefer a project's existing
Skills CLI script when it already has one, and retain its generated skill source
lockfile and discovery paths according to that project's conventions.

For unpublished local changes, use a local checkout as the source:

```sh
npx skills add /path/to/the-corner-factory-skills --list
npx skills add /path/to/the-corner-factory-skills
```

The path above is a placeholder for your checkout. Without an installer, an agent
can read the chosen `skills/<skill-name>/SKILL.md` directly and follow its linked
resources. Cloning this library alone does not install skills into other projects.

Maintain shared instructions here and refresh consuming projects through their
existing skill tooling. Preserve local customizations when updating an installed
skill; project-specific instructions remain in the consuming repository.

## Migrating from Harness

`bulk-sync` now lives here under its original name. Harness no longer contains
a `skills/` directory. Update references and reinstall it from this source in
projects that use the batch workflow:

```sh
npx skills add the-corner-inc/the-corner-factory-skills --skill bulk-sync
```

Use the local checkout path instead of the GitHub source until these changes are
published. Select the project's existing agent targets. Before replacing an
installed skill, preserve and compare local customizations. Let the installer
update its source lockfile, then verify the source, discovery paths, and linked
resources. Run only the command for each skill the project needs. Moving the
library does not automatically migrate existing installations.

`update-dependencies` is maintained separately in
[forge-template](https://github.com/the-factory-forge/forge-template/blob/main/.agents/skills/update-dependencies/SKILL.md)
and [Up4it](https://github.com/the-corner-inc/up4it/blob/main/.agents/skills/update-dependencies/SKILL.md),
under each repository's `.agents/skills/`. Use the version for the destination's
stack. If an existing installation still names Harness or this shared library as
its dependency-skill source, migrate it to the matching product source through
the project's skill tooling, preserving local edits and checking the source lock.
These product-owned skills are no longer distributed by this shared repository.

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

Ownership: The Corner Factory SA. Proprietary by default; see [LICENSE](LICENSE).
