---
name: update-dependencies
description: Update package dependencies and project-installed agent skills in Forge repositories and customer websites. Use for targeted upgrades, routine maintenance, and security fixes with the destination project's tooling; not template synchronization or registry-source adoption.
---

# Update dependencies

Deliver a working, reviewable dependency update using the destination repository's package manager, version policy, and checks. Improve the application's use of updated libraries while preserving client customizations and behavior unless a change is explicitly approved.

The canonical source is `forge-skills/skills/update-dependencies/`. Read the destination's current instructions and scripts; preserve its application foundation and customer customizations. Template synchronization and registry-source adoption use their provider-owned sync skills when requested.

## Establish scope and baseline

1. Read the destination's `AGENTS.md`, relevant local guidelines, manifests, lockfiles, workspace configuration, update scripts, and CI checks. Identify the pinned package manager and runtime, overrides, patches, catalogs, private registries, release-age rules, and lifecycle scripts. Inventory project-installed skills, their sources and lockfiles, package-bundled guidance, and local skill customizations. Inspect configuration without exposing credentials or secret-bearing environment files.
2. Check Git status and preserve existing changes. Record current declared and resolved versions for the affected packages. If a user edit overlaps the update, incorporate it deliberately; do not reset, discard, or automatically stash their work.
3. Honor the requested packages, versions, workspace, and update mode:

   | Request                                       | Scope                                                                                                                                               |
   | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
   | Named package or target version               | Assess that package and its required migrations; apply breaking upgrades after the approval step below.                                             |
   | General maintenance, without a version target | Prefer stable patch/minor updates within current major versions; report excluded major upgrades. Treat `0.x` minor changes as potentially breaking. |
   | Latest versions or explicit major upgrade     | Evaluate current stable releases, including majors; explain breaking changes and obtain approval before applying them and their migrations.         |
   | Security fix                                  | Verify the advisory's affected and fixed versions, trace the dependency path, and choose a compatible fix. Avoid unrelated upgrades.                |

4. State the chosen scope briefly and proceed with investigation and nonbreaking updates. Follow the approval step below for breaking upgrades. Preserve existing prerelease tracks unless the task calls for changing them; do not introduce a prerelease or downgrade to a stable release just because its label looks preferable. Keep runtime, package-manager, CI-action, and container upgrades outside scope unless requested or required by the selected dependency update.
5. Run the smallest useful baseline checks before editing when feasible. Record existing failures so they are distinguishable from regressions; avoid requiring a full test suite twice for a routine bump.

## Choose versions from evidence

- Query the project's configured registry or existing updater for current versions. For every updated library, review official release notes and migration guides across the current-to-target version range, including breaking changes, deprecations, and new capabilities. Search the codebase for affected usages and relevant improvement opportunities. Do not infer “latest” from memory or another repository's manifest. If metadata is unavailable, disclose it and avoid claiming a latest-version update.
- Check runtime engines, peer constraints, framework/plugin support, and deployment compatibility before installing. Update coupled packages together when their compatibility contracts require it; packages sharing a namespace do not necessarily share a version number.
- Respect exact pins, range style, excluded packages, and release-age policies. A newly published release may be deferred by policy; report that explicitly. Do not silently disable these policies to reach a newer version. If a security fix conflicts with them, explain the conflict and seek a decision only for that unresolved exception.
- For a transitive vulnerability, inspect which direct dependency introduces it. Prefer updating its parent or resolving a fixed version within the supported range. Use a narrow override only when needed and compatible; document why it exists and when it can be removed. Do not add the transitive package as a direct dependency merely to silence an audit.

## Explain breaking changes and obtain approval

Before applying an upgrade with breaking changes, finish the release-note review and usage audit so the user can decide on a concrete migration. Explain the package and current-to-target versions, what changed, affected files and app behavior, required code/configuration/data migrations, expected benefit, and a compatible alternative or deferral when available. If upstream breaking changes do not affect this app's usage, say so explicitly.

Ask whether to proceed with the described upgrade and migration, then wait before changing the affected dependencies or application code. A generic request to “update everything” or use “latest” is not approval of newly identified breaking changes. Honor prior explicit approval of the same described migration without asking again. Continue independent nonbreaking updates while awaiting the decision; a decline or no response must not be treated as permission.

Apply this rule to breaking changes discovered in any release, including minor/patch versions and security fixes. If further breaking changes emerge during implementation, pause the affected work and present the new impact before continuing it.

## Adopt relevant library improvements

For every update, actively look for ways the new library version can improve the target app, even when the old code still compiles. Inspect existing usage for deprecated patterns, redundant wrappers or workarounds, weaker typing, and performance-sensitive paths that the library now handles better.

Implement applicable, focused improvements using supported APIs and documented migration guidance: simplify code with new built-in capabilities, replace deprecated APIs, strengthen types, or adopt relevant rendering, caching, batching, or loading improvements. Keep each change tied to an actual library change and a concrete benefit for this application. Follow the approval rule above if the improvement changes an existing contract or behavior incompatibly.

Do not stop at version bumps when a useful code adaptation is available. Equally, do not force a rewrite or adopt a new feature that the app does not need. Record when no useful adaptation was found, or why an identified improvement was deferred.

## Apply the update

1. Use the repository's existing update command when it matches the scope. Inspect its flags and configuration first: some updaters write files, install packages, or update runtime and CI versions automatically. Preview candidates before mutation where supported. In an unattended session, use a verified noninteractive equivalent with explicit scope instead of accepting every interactive choice.
2. Edit the authoritative dependency declarations and regenerate the lockfile with the pinned package manager. For catalogs, update the catalog entry while preserving consumers' `catalog:` references. Retain aliases, workspace links, overrides, patches, and dependency categories unless the migration requires a change. Do not hand-edit or delete a lockfile to bypass a resolver failure, and do not introduce a second package manager's lockfile.
3. Refresh and read relevant library skills as described below before adapting code to the newly installed versions. Resolve compatibility problems through supported versions and necessary source/configuration migrations. Recheck package patches against the new release; remove a patch only when its purpose is obsolete. Preserve library peer ranges unless compatibility has actually changed and been validated.
4. Review install/prepare hooks and existing build-script approvals before execution. Preserve the repository's lifecycle policy. Do not use blanket force options, `audit fix --force`, broad peer-rule relaxations, or globally allowed build scripts to mask incompatibility.
5. Include focused code-quality and performance improvements identified above, together with required generated files according to repository conventions. Keep changes attributable to the library update; avoid unrelated refactors, component regeneration, or template/registry pulls. For large updates, apply and validate coherent groups so failures can be isolated.

Prepare required schema or configuration migrations as part of the code change. A dependency-update request alone does not authorize executing migrations against production data, publishing a package, or deploying the application. Continue local work under existing authorization.

## Update the project's skills

Skill maintenance is part of every dependency update, including targeted updates. Check all existing project-installed skills and update them from their configured sources to the newest revisions compatible with the resulting dependency versions.

- Use the project's existing skill manager or scripts and preserve installation scope, agent targets, source pins, and intentional exclusions. Inspect supported update flags first; explicitly select project scope. Do not update global skills or install unrelated skills as a side effect.
- Compare upstream changes with local customizations before replacement. Merge necessary changes into customized skills instead of overwriting them. Refresh skill lockfiles and source revisions through the existing tooling, and preserve working symlinks and agent discovery paths.
- For skills shipped inside library packages, reinstalling the updated package refreshes their source. Rediscover and load the guidance matching the installed version; refresh existing generated indexes or loading instructions when required. Do not substitute guidance for an unapproved or deferred library version.
- Update project-authored skills and their relevant examples, references, or helper scripts when dependency changes make them stale. Apply the breaking-change approval rule to incompatible changes in skill workflows or required tooling. Preserve the previous compatible skill revision while approval is pending.
- If no skills are installed, record that the check found none. If a skill cannot be refreshed because its source is unavailable, compatibility is unclear, or local edits cannot be reconciled, report that specific incomplete step instead of claiming the skill update succeeded.

## Validate the result

- Confirm manifests and lockfiles agree using the package manager's frozen/immutable install or equivalent CI check. Use an isolated environment if a clean-install check would disrupt the user's running setup. Check for unexpected dependency removals, duplicate versions, lockfile format churn, or new peer/engine warnings.
- Verify refreshed skills are discoverable, their references and symlinks resolve, and their instructions match the installed dependency APIs. Review skill/source-lock diffs for lost customizations; validate changed skill metadata and run changed helper scripts with safe inputs where applicable.
- Run the repository's required checks and tests relevant to the changed packages. Exercise affected behavior: for example, production rendering for a framework upgrade, session flows for auth changes, or queries against a disposable database for ORM changes. Include a production build when the existing test workflow does not already cover it and the change warrants it.
- Verify adopted library capabilities preserve intended behavior and deliver the stated code-quality benefit. For performance-focused changes, capture a relevant baseline before editing and compare under equivalent conditions, using measures such as bundle size, render time, query count, or request latency. Report measured results separately from expected benefits; do not claim a speedup from release notes alone.
- Follow repository environment/test setup; do not use production credentials or weaken tests, type checking, or security settings to obtain a pass. Add or adjust tests only when changed behavior warrants coverage.
- For security work, rerun the relevant audit and verify the resolved dependency path no longer contains the affected version. Distinguish unfixed findings, registry/network failures, and untested behavior from successful validation.
- If an update cannot be completed, identify the exact compatibility or environment blocker. Retain a coherent, reviewable result; revert only your unsuccessful changes when needed, preserving user work. Do not repeat forced installs or claim completion with a broken dependency graph.

## Registry source repositories

When updated packages are used by distributed registry items, update their dependency declarations as well as the root package manifest. Regenerate published endpoints through the repository's official builder; never hand-edit generated registry JSON. Validate affected items in a disposable consumer, since a passing showroom build does not prove installation completeness.

Update linked consumer checkouts only within the user's authorized scope. Otherwise report required consumer follow-up. Preserve the configured namespace after temporary local testing; rebuilding endpoints does not update consumers. Pulling installed registry source is a separate provider-owned sync workflow, not an automatic package-maintenance step.

## Forge tooling

- Where Vite+ is configured, `vpr` is shorthand for `vp run`. Inspect `package.json`'s `deps` script before running it. A Taze-based script may be interactive and include exact-pinned packages. Keep its maturity filter and intentional exclusions when selecting a noninteractive command. Check the installed tool's help and [Taze documentation](https://github.com/antfu-collective/taze) for current flags and possible writes outside package manifests.
- Where `skills` and `intent` scripts expose the corresponding CLIs, use `vpr skills update --project` for project-installed skills and `vpr intent list` followed by the relevant `load` commands for package-bundled guidance. Confirm the scripts and flags against the installed versions first. See the [Skills CLI](https://github.com/vercel-labs/skills#skills-update) and [TanStack Intent](https://tanstack.com/intent/latest/docs/overview) documentation; preserve the project's existing Intent allowlist.
- Inspect `pnpm-workspace.yaml` alongside `package.json`. Vite may use a catalog alias to Vite+; preserve that relationship and check the pair's compatibility instead of replacing the alias with standalone Vite. Use the pinned version's [pnpm update documentation](https://pnpm.io/cli/update) and [settings reference](https://pnpm.io/settings) when resolving catalog or release-age behavior.
- When present, `vpr lint` includes type checking, and `vpr test:e2e` owns its production build/server lifecycle. Follow local test guidance and avoid duplicating that build. Use the destination's designated agent/test port and leave other running servers intact.
- Read `.env.schema` for the environment contract. Where configured, validate through `vp exec varlock load --agent`; preserve Varlock code generation and prepare hooks. Keep optional auth/database features in their current enabled or disabled state.

When updating Better Auth, inspect the pinned CLI versions in `auth`, `auth:generate`, and related scripts alongside the SDK dependency. Keep schema generation compatible and preserve the distinction between generating a migration and applying it.

## Handoff

Report the packages or coherent groups updated, their previous and resulting versions, breaking changes and approval status, required migrations, and the checks actually run with outcomes. Explain which library improvements were adopted, their code-quality benefits, and any measured performance results or measurement limits. List deferred upgrades or adaptations and their concrete reasons, including pending or declined approval, major-version scope, maturity policy, or compatibility constraints. Link relevant migration guides or advisories for consequential changes. Identify any deployment follow-up without implying it has already happened.

Include skills refreshed, their source/version changes when available, local guidance adapted, and skill validation results. Distinguish unchanged compatible skills, absent skills, and blocked skill updates.

Propose a commit title using the destination's conventions and any user-requested title.

Commit, push, or open a pull request only when the user's task or established workflow includes that action.
