# Verification and server handoff

Read after registration or when checking an existing installation. Use current
[App authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app)
and [installation authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation)
documentation for request authentication and the supported API version.

## Verify the GitHub side

Load credentials privately in the verification process; emit only allowlisted
non-secret identity/status fields. Do not log raw API responses, request headers,
JWTs, installation tokens or webhook payloads. Keep temporary tokens in memory.

1. Parse the PEM and sign an App JWT. `GET /app` must match the intended App ID,
   slug and owner, with only the requested permissions and events. The numeric
   App ID differs from its OAuth client ID.
2. Read `GET /app/hook/config`: check the exact HTTPS destination, SSL
   verification, and active webhook configuration in the App settings. Do not
   display the returned configuration wholesale. GitHub's
   [webhook guide](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/using-webhooks-with-github-apps)
   describes production webhook settings.
3. Read `GET /repos/{owner}/{repo}/installation`. Verify the expected App and
   owning account, selected repository mode, effective permissions and absence
   of suspension. Inspect the installation's **complete** repository selection
   in its settings: it must contain exactly the intended repository. If using
   the API instead, paginate all repository results under an installation token
   without a repository filter. A token narrowed to one repository cannot prove
   that the installation itself has access to only that repository.
4. Request an installation token with `repository_ids` restricted to the verified
   repository ID and the required permissions. Read the repository through that
   token and verify its ID, owner/name, private visibility, active state and Issues
   availability. Resolve the numeric bot user ID from the verified App slug's
   `[bot]` account; confirm its type is Bot.
5. Inspect recent delivery event names and HTTP statuses without copying payloads.
   A failed initial ping can result from missing server configuration. Record the
   observed status and pending host work; a successful ping alone does not prove
   issue/comment synchronization or worker operation.

Do not create issues or comments merely to test access. End-to-end writes need a
staging destination or a test discussion within the user's authorized scope.

## Produce a protected environment handoff

Use the destination's environment schema and adapter as the authority. The current
[template Support guide](https://github.com/the-factory-forge/forge-template/blob/main/docs/supports.md)
uses the following fields; compare them with the installed host before exporting:

| Field | Source |
| --- | --- |
| `SUPPORT_GITHUB_APP_ID` | Verified numeric App ID |
| `SUPPORT_GITHUB_PRIVATE_KEY` | App's PEM signing key |
| `SUPPORT_GITHUB_INSTALLATION_ID` | Verified numeric installation ID |
| `SUPPORT_GITHUB_REPOSITORY_ID` | Verified numeric private repository ID |
| `SUPPORT_GITHUB_BOT_USER_ID` | Verified numeric App bot user ID |
| `SUPPORT_GITHUB_OWNER` | Exact repository owner login |
| `SUPPORT_GITHUB_REPOSITORY` | Repository name without owner prefix |
| `SUPPORT_GITHUB_WEBHOOK_SECRET` | Same secret configured for the App webhook |
| `SUPPORT_MAINTENANCE_SECRET` | Separate host worker bearer secret |

Resolve `git rev-parse --path-format=absolute --git-common-dir` for a suitable
private `support-setup/` directory outside tracked source, including in linked
worktrees. Use the user's approved secret store instead when specified. Create
directories with mode `0700` and files with mode `0600` or equivalent ACLs. Do not
overwrite an existing handoff; compare identity privately and preserve existing
values. Never commit a credential file, including an encrypted or example copy
containing real credentials.

For a new setup, generate distinct cryptographically random webhook and worker
secrets meeting the host's minimum length (currently 32 characters). Preserve the
manifest-generated webhook secret when it meets that requirement. For an existing
host, reuse the configured worker secret; lack of access does not justify rotation.
If a required existing value is unavailable, identify the missing merge step.

The current adapter accepts PEM newlines or literal `\n` escapes. Serialize for
the actual dotenv/Dokploy parser, then verify privately that parsing recovers the
same key and all IDs. Do not use the file as a shell script or print its contents.
Export App credentials, not a temporary installation token or OAuth client secret.

## Complete the host step within scope

For a user-managed VPS, give the protected file path and these remaining actions.
For authorized server setup, perform them through the destination's documented
deployment process and verify the result:

- Merge variables into the correct Dokploy application or service. Check runtime
  injection for that deployment type; saving dashboard variables alone may not
  pass them to the container. Keep secrets out of client-exposed/build variables.
- Verify the canonical HTTPS origin, documented webhook route, existing database
  migrations and any required private image storage. Preserve ticket history,
  credentials, migration journals and unrelated application settings.
- Configure the host's documented process, reconciliation, cleanup and health
  jobs with the worker secret in an authorization header, never a URL. Check the
  installed host's routes and intervals; workers do not necessarily start at boot.
- After the normal authorized deployment, inspect signed webhook delivery and
  worker health, including failed/blocked/backlog counts. Use the host's staging
  acceptance test for outbound issues, inbound replies and status synchronization.

A partial GitHub environment group fails closed in the current template. Existing
local tickets require the explicit **Send to GitHub** action; setup must not bulk
export them. If server setup or acceptance testing is pending, report GitHub
access as verified and live issue linkage as pending.
