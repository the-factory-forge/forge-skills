---
name: setup-github-access
description: Connect a Forge customer's private Support repository to The Corner Support shared GitHub App, verify scoped access, and prepare protected service credentials for the host. Also repairs existing dedicated-App installations; excludes Git login, collaborator invitations and deployment-only Apps.
---

# Set up customer GitHub access

New customers reuse **The Corner Support**, owned by `the-factory-forge`.
Its shared service holds the App key, issues repository-scoped tokens and routes
webhooks. Customer hosts receive a unique service credential and relay secret.
An explanation-only request stays read-only. Distinguish source setup, verified
GitHub access and working issue delivery.

## Resolve the customer and compatibility

Read the destination's `AGENTS.md`, Support guide, environment schema and server
adapter. Resolve its checkout, exact repository, private visibility, active Issues
and production HTTPS origin from remotes and connected sources. Customer names,
repository names and App slugs can differ. Ask only for undiscoverable facts,
never credentials in chat.

Use the installed adapter as the compatibility baseline. Consult the
[shared service runbook](https://github.com/the-factory-forge/forge-registry/blob/main/docs/corner-support.md),
[connector contract](https://github.com/the-factory-forge/forge-registry/blob/main/docs/supports-github.md)
and [template host guide](https://github.com/the-factory-forge/forge-template/blob/main/docs/supports.md)
in actual local checkouts or their canonical links. Older hosts need the shared
token adapter before activating delivery. Independent GitHub inspection and
repository selection may proceed within scope; copying the shared App key to an
older host is not a compatibility fix. Report unavailable context or required source adoption.

Carry forward user scope and existing authorization. “Only GitHub; I'll configure
the VPS” ends with a protected handoff and pending shared-service/host steps. App
setup does not authorize repository creation, invitations, historical export,
customer migration, release or deployment. Keep unrelated configuration intact.

## Reuse the shared App

Inspect [organization registrations](https://github.com/organizations/the-factory-forge/settings/apps),
installations and non-secret operational records. Verify the intended App owner,
name, numeric ID and bot ID; a display name alone does not establish identity.
The registered [The Corner Support App](https://github.com/organizations/the-factory-forge/settings/apps/the-corner-support)
has App ID `5774442`; verify its current installation and readiness before reuse.
Reuse existing keys and secrets. Read [registration and recovery](references/registration.md)
only when the shared App is absent, registration was interrupted, or an existing
App requires an authorized repair.

| Setting                          | Shared App value                                                                |
| -------------------------------- | ------------------------------------------------------------------------------- |
| Name / owner                     | The Corner Support / `the-factory-forge`                                        |
| Availability                     | Private while repositories belong to the owning organization                    |
| Repository permissions           | Issues read/write; Metadata read; no others                                     |
| Organization/account permissions | None                                                                            |
| Events                           | `issues`, `issue_comment`                                                       |
| App webhook                      | `https://support.the-corner.swiss/api/github/webhook`, SSL verification enabled |
| User OAuth                       | Not requested; no OAuth secret is needed                                        |
| Installation                     | Only select repositories; retain all approved customer selections               |

Use the verified deployed service origin if it differs from the intended origin.
Public installation availability is needed for repositories in other accounts;
it does not make their repositories public. The current template fixes the owner
to `the-factory-forge`; a different owner needs an explicitly scoped host change.
Keep deployment Apps with broader permissions separate from Support.

For a customer in the same organization, add its repository to the existing App
installation's selected set. Preserve all existing selections. Never narrow a
shared installation to just the new customer or accept an All repositories default.
An organization approval request is pending, not completed access.

Use connected tools or authenticated CLI when they support the action; otherwise
use the supported browser. Read the current state after interrupted authentication
before retrying. Let the user handle passkeys/SSO. Make owner, App, repository,
permissions and credential destination concrete before mutation; proceed within
authorization, asking only for a missing decision or a required tool approval.

## Onboard the site and verify

Follow [verification and handoff](references/handoff.md). Verify selected repository
access, private identity, effective permissions, App bot and scoped token issuance.
In the shared service's protected configuration, bind a unique site credential's
SHA-256 hash to exactly one installation/repository pair and a fixed HTTPS host
webhook URL. Give the site its own relay secret, distinct from the App webhook
secret and every other site's secrets. Read the runbook's actual config schema;
configuration changes require a service restart within the authorized scope.

The App PEM and App-level webhook secret stay on the shared service. Put only
this site's credential, relay secret, pinned IDs and host settings in its protected
handoff. A temporary GitHub installation token is not a usable long-term handoff.
When the shared service cannot be configured or reached, prepare independent
GitHub setup and report token issuance/webhook routing as pending.

## Existing installations

Preserve working dedicated-App credentials when repairing an existing site.
Migrate to the shared App only when included in scope, following the runbook's
migration procedure: resolve uncertain writes with the old identity, preserve
bindings and replay receipts, then verify old echoes and new delivery. A source
update does not authorize migration or retirement of customer Apps. Do not
change a deployed site's App ID, bot ID or stored installation IDs as a shortcut.

Finish with App/installation links, verified repository and permission scope,
protected handoff path, shared-service mapping/restart status and host prerequisites.
Report whether staging issue/comment/status delivery was actually tested. Keep
credentials out of the answer and remove scratch copies only after a durable
handoff is verified. A pending step should identify the existing resources and
next action so setup resumes without recreating them.
