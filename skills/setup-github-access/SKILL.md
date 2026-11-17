---
name: setup-github-access
description: Create or repair a dedicated GitHub App for one Forge customer's Support repository, verify restricted access and direct webhooks, and prepare protected VPS or Dokploy credentials. Excludes Git login, collaborator invitations and deployment-only Apps.
metadata:
  author: The Corner Factory SA <support@the-corner.swiss>
---

# Set up customer GitHub access

Each customer uses a dedicated GitHub App installed on exactly its own private
Support repository. The customer's existing API holds that App's private key,
refreshes repository-scoped tokens and receives GitHub webhooks directly. No
shared support service, service token or central configuration is required.
An explanation-only request stays read-only.

## Resolve the customer and installed adapter

Read the destination's `AGENTS.md`, Support guide, environment schema, server
adapter and existing protected handoff metadata. Resolve its checkout, exact
repository, private visibility, active Issues and production HTTPS origin from
remotes and connected sources. Site names, repository names and App slugs may
have different spellings; preserve storage prefixes and repository overrides.

Use the [template host guide](https://github.com/the-factory-forge/forge-template/blob/main/docs/supports.md)
and [connector contract](https://github.com/the-factory-forge/forge-registry/blob/main/docs/supports-github.md)
from actual local checkouts or their canonical links. A shared-service-only host
needs source adoption before these credentials can work. Keep a new site's entire
GitHub credential group empty until ready; partial configuration fails closed.

Carry forward authorization. “Only GitHub; I'll configure the VPS” ends with a
protected handoff and pending host steps. App setup does not authorize repository
creation, invitations, historical ticket export, data migration or deployment.
Source implementation, GitHub access and working delivery are separate outcomes.

## Register or reuse this customer's App

Inspect organization registrations and existing handoffs before creating anything.
Reuse only an App already dedicated to this customer with the expected scope.
Do not copy a shared App's key or narrow an existing multi-customer installation;
preserve other customer Apps and repository selections. Verify current GitHub
registration/authentication documentation when operating on GitHub.

| Setting | Customer App value |
| --- | --- |
| Owner | `the-factory-forge`, matching the current host adapter |
| Name | Unique customer-specific Support name; verify available slug |
| Availability | Private to the owning account |
| Repository permissions | Issues read/write and Metadata read only |
| Organization/account permissions | None |
| Installation | Only select repositories: exactly this customer's private repository |
| Events | `issues`, `issue_comment` |
| Webhook | Customer's verified HTTPS origin + `/api/supports/github-webhook`; SSL verification enabled |
| User OAuth | Not requested; no OAuth client secret in the host handoff |

Read [registration and recovery](references/registration.md) when creating or
repairing the App. Use connected tools or authenticated CLI when sufficient;
otherwise use the supported browser. Let the user handle passkeys/SSO. Re-read
state after interrupted authentication to avoid duplicate resources.

## Verify and hand off

Follow [verification and handoff](references/handoff.md). Verify the App, numeric
bot ID, selected-repository installation, permissions and restricted token scope.
The numeric App ID differs from its OAuth client ID. Prepare this customer's
private key and webhook secret for only this customer's backend.

For sites previously connected through another App, inspect whether stored ticket
bindings pin the old installation or bot. Preserve tickets, jobs, mappings and
replay receipts. A new credential group does not migrate existing bindings;
report any required data migration separately and obtain its authorization.

Finish with App/installation links, verified repository and permission scope,
protected handoff path, and pending runtime/deployment actions. Name missing env
keys without values. The production API runs internal maintenance; no HTTP
maintenance schedules or scheduler credential are needed. Report whether direct
webhook acceptance and staging issue/comment/status delivery were actually tested.
Never export real customer tickets to test setup, and never request secrets in chat.
