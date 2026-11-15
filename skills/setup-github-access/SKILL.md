---
name: setup-github-access
description: Create or repair a customer's dedicated GitHub App for Forge Support issue linkage, verify repository access, and prepare a protected VPS or Dokploy handoff. Use for customer GitHub access setup; excludes Git login, collaborator invitations and deployment-only Apps.
---

# Set up customer GitHub access

Provision the GitHub side of a customer's Support integration and make the server
handoff usable. Distinguish verified GitHub access from working issue delivery.
An explanation-only request stays read-only.

## Resolve the customer and scope

Read the destination's `AGENTS.md`, Support guide, environment schema and server
adapter. Resolve its checkout and exact GitHub owner/repository from remotes or
connected sources; customer names, repository spellings and App slugs can differ.
Confirm the repository is private, unarchived and has Issues enabled. Resolve the
canonical production HTTPS origin and webhook route from the project. Ask only
for missing facts that cannot be discovered, never for credentials in chat.

Use the installed implementation as the compatibility baseline, then consult the
[registry connector contract](https://github.com/the-factory-forge/forge-registry/blob/main/docs/supports-github.md)
and [template host setup](https://github.com/the-factory-forge/forge-template/blob/main/docs/supports.md)
in their actual local checkouts, or through these canonical links. Report missing
context rather than assuming every customer has the latest adapter.

Carry forward the user's App name and authorized scope. “Only GitHub; I'll add
the token on the VPS” ends with a protected local handoff: no server edits,
scheduler changes or deployment. App setup alone does not authorize repository
creation, customer invitations, historical ticket export or a release.

## Choose the App

Inspect existing registrations, installations and non-secret project records
before creating anything. Reuse an App already dedicated to this customer's
Support bridge when its identity and credentials can be verified. Preserve
existing keys and secrets; generating replacements is a rotation, not a retry.

The current connector requires a dedicated App for this bridge and repository:
it treats that App's status changes as its own echoes. A deployment App with
Contents or Administration access does not meet this contract. Leave unrelated
Apps and installations alone.

For a new App, use the repository owner's account or organization and the user's
chosen available name. A private App can only be installed on its owning account.
For a shared-App request, explain the separate design work: one App webhook URL
needs routing to customer hosts, App identity affects echo handling, and copying
one signing key to several servers expands access across customers. Follow the
user's architecture decision before provisioning a shared alternative.

## Register and install

Use connected GitHub tools or an authenticated CLI where they support the action;
fall back to the supported browser for registration and installation. Inspect
capabilities rather than assuming a repository connector can manage Apps. Prefer
an isolated tab/session where available. If the user changes the browser, read
its current state before continuing. Let the user complete passkey, SSO or other
authentication checks, then resume from the observed state.

Before a mutation, make the intended App owner/name, target repository,
permissions and credential destination concrete. Continue under existing task
authorization; ask only for a missing scope decision or an approval required by
the active tool policy, explaining its source.

For a new or interrupted registration, read
[registration and recovery](references/registration.md).
Use these settings for the current connector:

| Setting | Value |
| --- | --- |
| Availability | Private, owned by the target repository's account |
| Repository permissions | Issues: read/write; Metadata: read |
| Organization/account permissions | None |
| Subscribed events | `issues`, `issue_comment` |
| Webhook | Active; verified production HTTPS endpoint; SSL verification enabled |
| User OAuth authorization | Not requested; no OAuth client secret needed by this host |
| Installation access | **Only select repositories**, selecting the exact customer repository |

Check the install page before submitting: it may default to **All repositories**.
After an ambiguous result or interrupted authentication, inspect existing App and
installation state before retrying. An organization approval request is pending,
not a completed installation. Stop dependent work if permission is denied or the
requested identity cannot be verified.

## Verify access and hand off

Follow [verification and server handoff](references/handoff.md). Verify the App's
identity, effective permissions, event subscriptions, webhook configuration and
complete installation repository selection. Test authentication with the App key
and an installation token; keep secret-bearing responses out of tool output.
Record numeric App, installation, repository and bot user IDs from GitHub.

Prepare the exact environment fields consumed by this customer's adapter in a
protected location outside tracked source. Preserve existing server values when
repairing setup. A long-lived App key enables the host to refresh short-lived
installation tokens; handing over a temporary token alone is insufficient.

When server configuration is in scope, follow the destination's deployment
procedure and current Dokploy documentation for its application type. Merge the
required variables, check they reach the runtime, and configure the documented
workers and monitoring. Use staging or an explicitly authorized test discussion
for end-to-end issue/comment/status checks; never export real customer tickets as
a setup probe. When the user owns the server step, provide that checklist without
performing it.

Finish with the App and installation links, verified repository/permissions,
protected handoff file path, and observed webhook status. State separately what
remains on the host and whether end-to-end delivery was tested. Keep secrets out
of the response. Stop temporary receivers and remove scratch credential copies
only after verifying a durable handoff. If blocked, report existing resources and
the exact remaining step so the next attempt resumes safely.
