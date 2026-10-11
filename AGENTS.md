# AI Agent Start Here

This repository owns the shared agent skills used across The Corner Factory SA
projects. Read [README.md](README.md) and the [catalog](skills/README.md), then
load only the skill and supporting resources relevant to the task.

Provider-specific synchronization stays with its provider: registry updates in
`forge-registry`, template synchronization in `forge-template`. This library owns
common maintenance such as dependency updates and releases. Shared ownership
requirements live in [forge-spec](https://github.com/the-factory-forge/forge-spec/blob/main/openspec/specs/the-forge/spec.md#requirement-provider-owned-skills).

## Editing skills

- Put each skill in `skills/<skill-name>/SKILL.md`. Use lowercase hyphenated
  names under 64 characters and matching `name` and meaningful `description`
  fields in YAML frontmatter. Keep the conventional `SKILL.md` filename.
- Preserve the workflow's intent and authorization boundaries. Explain when the
  skill applies; company-wide availability does not make every skill universal.
- Read a consuming project's own instructions, scripts, and configuration before
  operating on it. Avoid fixed workstation paths, assumed package managers, and
  unconditional product-specific rules.
- Keep shared requirements in their owning specs repository and project facts in
  the destination project. Reference them rather than copying them into skills.
- Add supporting files only when the workflow needs them. Resolve skill resources
  relative to the skill directory, including after installation elsewhere.
- Check references and consumers before renaming or moving a skill. Update the
  catalog and affected references together; preserve installed customizations.
- Validate changed frontmatter, references, and discovery. Run a safe check for
  changed executable helpers and review a representative workflow when behavior
  changes. Report checks actually run and any limitations.

No application scaffolding or runtime dependencies are needed for Markdown skills.
Do not store secrets, customer-specific data, or generated output in this library.
