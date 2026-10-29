---
name: push-design
description: Sync implemented UI into editable Penpot designs, including a first repository sync, scoped UI updates, and requested page organization. Resolve the destination from .structures/design.json and verify rendered boards and component links.
---

# Push design

Apply the requested implementation or recent UI change to the project's Penpot
design. With no argument, use the UI task just completed in this conversation;
accept a repository, route, screenshot, source file, or commit to set the scope.
This is implementation-to-design synchronization. Creating or editing this skill
or its configuration does not run a sync, change application code, or authorize
a Git commit or push.

## Establish the change

- Resolve the consuming project's root and read its instructions, design guidance,
  and relevant validation commands. Use its own tokens, typography, spacing,
  icons, component conventions, and test data; assume no framework or file layout.
- Identify the affected screens, components, states, and intended visual difference.
  Read their source, callers, and scoped diff, including staged changes or the
  task's commit. A clean worktree can still contain the completed change;
  unrelated dirty files are outside this sync. For an explicit first repository
  sync, inventory the requested UI instead of requiring a recent diff. Distinguish
  reusable components and plugin screens from the website that demonstrates them.
  Record the selected screens, states, themes, and viewport sizes; ask only when
  the intended scope cannot be inferred from the request or conversation.
- Inspect the resulting UI when available using the project's browser workflow.
  Use synthetic examples in Penpot. If the app cannot run, use source and available
  screenshots and report that limitation. For an explicit visual correction, use
  the user's requested result. Changes with no visible effect need no design edit.
- When building boards from rendered UI or correcting status badges, read
  [rendering guidance](references/rendering.md) for capture boundaries, native
  controls, clipping, fonts, text bounds, and asset handling.
  Verify one representative board before repeating the approach across the scope.

## Resolve the destination

Read `.structures/design.json` at the consuming project's root. It is a JSON file
inside the `.structures` directory, with these required fields:

```json
{
  "name": "Example design project",
  "url": "https://design.example.com/#/dashboard/files?team-id=11111111-1111-4111-8111-111111111111&project-id=22222222-2222-4222-8222-222222222222"
}
```

`name` is the Penpot project or file's display name; `url` is its full project
dashboard or workspace file URL. Keep actual hosts, names, and IDs in each
consuming repository, never in the shared skill. Keep credentials out of this file.

- Validate that the JSON is an object with non-empty string `name` and `url`
  fields. Parse the URL and its fragment query: Penpot's `team-id`, `project-id`,
  and `file-id` commonly occur after `#`, outside the normal URL query. Require
  an HTTP(S) URL with a host, no embedded credentials, and the destination IDs
  appropriate to the project or file link. A server homepage alone is insufficient.
- If the file is missing and the user supplied the destination name and URL,
  create it there. Otherwise ask only for missing destination details. Preserve
  unknown fields and other `.structures` files; report malformed configuration
  instead of replacing it with guesses. An explicit destination overrides the
  saved one for this run; persist a replacement only when requested.
- Prefer Penpot MCP. Read `high_level_overview` once per conversation and consult
  `penpot_api_info` for the API members needed. Copy any initial `penpot.selection`
  into `storage` before navigating. If the tools or connection are unavailable,
  explain how to connect the intended file through the Penpot MCP plugin and
  continue source inspection while waiting.
- For a workspace URL, compare the connected `penpot.currentFile.id` with the
  supplied `file-id` and verify the host/team context. For a project URL, resolve
  an existing file within that project first. The MCP connection exposes the
  current file; do not assume it enumerates dashboard projects or proves project
  membership. Use available project-aware tools or the authenticated dashboard
  to verify membership and obtain the file URL, then match the connected file ID.
  A matching display name or an already connected file alone is insufficient.
- If the project contains several plausible files, ask which one to update. If
  access, membership, or identity cannot be verified, pause design writes and
  report what is needed. An empty project needs a user-selected or explicitly
  requested new file; do not create one just because no match was found.

Proceed when the scoped UI change and the exact destination file are established.

## Find the boards and reuse components

- Use `penpotUtils.getPages()` to find the relevant page by route or screen name.
  Locate boards with `findShape` or `findShapes` rooted at that page. Inspect the
  relevant branch with `shapeStructure` and export it before editing. Match names,
  content, dimensions, and surrounding elements together; ask about unresolved
  ambiguity. Reuse existing boards. Create one only for a requested screen or
  state with no counterpart, following the file's organization and naming. For
  a first sync of a plugin or module library, use one page per plugin or module.
  Keep its desktop, mobile, theme, and interaction-state boards together, with
  the state in each board's name. Shared components, tokens, layouts, and public
  pages can have dedicated pages. Honor explicit organization preferences.
- Reorganize existing pages when requested. Save a version before a bulk import
  or reorganization when supported. Inventory boards, main components, and links
  before moving anything. Use a supported move operation; if it requires copying,
  verify the editable copy, component references, overrides, layer order, and
  dimensions before removing its exact source board. Track replacement IDs and
  arrange boards within each destination page without overlap. Remove a vacated
  page only after confirming it is empty and belongs to this reorganization.
- Preserve existing compact board spacing on subsequent syncs. For new or
  explicitly rearranged screen pages, use independent column stacks with 120 px
  vertical gaps unless the project or user specifies otherwise. Place each next
  board at the preceding board's bottom plus the gap in that column, using its
  actual height; a tall board in another column must not create empty rows.
  After a height change, adjust following boards as needed to retain the gap.
  Move each board with its contents, preserving internal geometry and component
  links. Keep shared component and token pages in their established arrangement.
- Before each page's mutations, await `penpot.openPage(targetPage)` and resolve
  its shapes again. Browser navigation and the MCP active page can differ;
  exporting another page does not make it active for editing. Page summaries
  returned by `getPages()` are lookup metadata; use the active Page object for
  shape access. Do not assume cloning or reparenting supports cross-page moves.
- Inspect local and connected libraries, tokens, and the file's component pages.
  Check component links and main instances: visually identical imported groups
  can be detached copies. Find matching occurrences throughout the affected flow.
- Reuse linked component instances. Before changing a shared main component,
  inspect its consumers and confirm the correction belongs to those uses. If
  it would alter unrelated flows or unverified library consumers, use an existing
  variant or a scoped composition instead. Preserve intentional content overrides;
  remove only overrides that block the intended shared correction.
- When an element repeats in the affected flow and has no suitable component,
  create one main component on the established component page; create that page
  if absent. Compose existing assets where possible. Support only needed sizes
  and states; keep unique elements local. Replace every matching detached copy
  in scope with a linked instance,
  preserving position, layer order, and content. Remove only superseded layers.

## Apply the visual difference

- Edit existing shapes and linked instances in place. Keep unrelated designer
  edits, copy, board dimensions, and surrounding layout. Build editable elements;
  screenshots are reference evidence, not replacements for the design.
- Store target IDs and snapshots of properties to change in `storage` before
  writing. Check flex/grid layout before moving children: adjust the layout when
  it owns positioning. Use `penpotUtils` for lookup and relative positioning.
- Inspect overlapping layers, clipping, fills, and imported SVG groups so the
  correction reaches the visible element. Reuse the project's icon family and
  vector paths. Keep badges and glyphs separate with appropriate padding.
- Use `resize(width, height)` for dimensions; width, height, and bounds are
  read-only. Use `x`/`y` or `setParentXY` for positioning. Replace whole fills or
  strokes arrays while preserving unrelated properties. Preserve existing token
  bindings unless the requested change replaces them; assigning literal values
  can remove those bindings.
- Preserve text sizing behavior: `resize()` sets text `growType` to `fixed` and
  does not scale its font size. Restore the intended growth behavior and check
  font size and alignment after resizing text or a component instance.
- Keep output to changed IDs, properties, and concise diagnostics. Export shapes
  instead of dumping SVG. After a failed mutation, inspect the actual state before
  retrying to avoid duplicating partial changes. Stop and report partial work if
  the cause cannot be resolved safely; do not replace entire pages as recovery.

## Verify and finish

- Export affected boards and inspect the requested change, alignment, board gaps,
  clipping, icon legibility, text, and neighboring elements. Check status labels
  against their pill, dot, and chevron centers using rendered bounds. Check
  responsive, state, or theme variants where the change applies. Fix observed
  defects and inspect again;
  a successful API call alone does not prove visual correctness.
- Re-read changed properties. Confirm migrated elements, including nested ones,
  reference the intended main components, inherit shared styles, retain intentional
  content overrides, and have no superseded layers covering them. Matching visuals
  and required component links constitute a successful no-op on repeated runs.
  Include descendants of clipped boards in link checks. Reconcile the board
  inventory after moves and check file validation when available. Save a named
  completion version after a verified bulk sync or reorganization.
- Clean up only task-owned browser tabs and test servers. Preserve the user's
  design tabs and work. Report updated pages/boards, the verified Penpot file link,
  configuration changes, and any verification limits or partial work. Distinguish
  design changes from application changes; a design-only sync needs no Git push.
  State omitted states, font substitutions, embeds, or interactions explicitly;
  selected variants do not establish exhaustive coverage.
