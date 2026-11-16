# Verification and server handoff

Read after shared-App registration or when adding/repairing a customer. Use current
[App authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app)
and [installation-token documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app).
Load credentials privately; emit only allowlisted non-secret IDs/status. Never
print raw API responses, keys, JWTs, tokens, webhook payloads or request headers.

## Verify GitHub and routing

1. With the centrally held App credentials, `GET /app` must match The Corner
   Support's verified owner, ID, slug, permissions and events. Numeric App ID and
   OAuth client ID differ. Resolve the numeric `[bot]` account and verify its type.
2. Inspect `GET /app/hook/config` and App settings privately: exact shared-service
   HTTPS URL, active delivery and SSL verification. Do not display the full response.
3. Verify `GET /repos/{owner}/{repo}/installation`, selected-repository mode,
   permissions and absence of suspension. Inspect the complete selection through
   settings or paginated repository results using an unrestricted installation
   token. Retain other approved customers; a token narrowed to one repository
   cannot establish the installation's full scope.
4. Verify the service mapping uses that installation, repository, owner/name and
   site's exact production webhook URL. Request a token through `/api/token` with
   the site's service credential and empty body. Privately check expiry and returned
   installation/repository/bot IDs, then read the repository through that token:
   private, unarchived, correct identity, Issues enabled. Check `/installation/repositories`
   using this token returns only that repository. Do not fall back to the shared
   PEM on the customer server if this fails.
5. Inspect safe webhook delivery statuses and host worker health. A successful ping
   or `/health` response does not prove customer routing, issue delivery or schedules.

Live issue/comment writes require an authorized staging repository or test
conversation. Never export real customer tickets merely to test setup. The shared
service's local tests cover cross-customer isolation without production writes.

## Produce a protected handoff

Follow the installed host's schema. For an older adapter, label shared fields as
a future handoff pending source adoption; keep a new host's entire GitHub group
unconfigured until then rather than applying pinned IDs piecemeal. The current
template uses:

| Field                            | Shared-service source                                                            |
| -------------------------------- | -------------------------------------------------------------------------------- |
| `SUPPORT_GITHUB_TOKEN_URL`       | Verified service endpoint; intended `https://support.the-corner.swiss/api/token` |
| `SUPPORT_GITHUB_SERVICE_TOKEN`   | Unique site credential; only its SHA-256 hash goes into central config           |
| `SUPPORT_GITHUB_INSTALLATION_ID` | Verified installation, shared by repositories in that organization               |
| `SUPPORT_GITHUB_REPOSITORY_ID`   | Exact private repository ID                                                      |
| `SUPPORT_GITHUB_BOT_USER_ID`     | Verified shared App bot ID                                                       |
| `SUPPORT_GITHUB_REPOSITORY`      | Override only when repository name differs from `SITE_NAME`                      |
| `SUPPORT_GITHUB_WEBHOOK_SECRET`  | Unique site's relay secret, matching its central mapping                         |
| `SUPPORT_MAINTENANCE_SECRET`     | Separate host worker bearer secret                                               |

The template fixes repository owner to `the-factory-forge` and uses shared-service
authentication only. Partial site configuration fails closed.

Use the user's secret store, or resolve
`git rev-parse --path-format=absolute --git-common-dir` for a private
`support-setup/` directory outside tracked source. Restrict directories to 0700 and
files to 0600, or equivalent ACLs. Preserve existing handoffs and configured
secrets; missing access does not authorize rotation. Never put real values in
tracked examples, command arguments, build variables, logs or chat.

For a new shared site, generate independent cryptographically random 32-byte
base64url service, relay and maintenance secrets. Hash the service credential with
SHA-256 for the central config. Preserve the shared App's existing key and webhook
secret. Merge one site entry without replacing other customers. Keep central and
customer handoffs separate; never copy the entire central config to a customer.
Serialize for the actual dotenv/Dokploy parser and verify parsing privately.

## Host completion within scope

For user-managed deployment, provide the protected file paths and pending actions.
For authorized deployment, follow the destination's procedure and verify:

- The shared service has the mapping, readable protected files and a completed
  restart; its actual runtime origin matches the handoff and App webhook.
- Variables reach the customer's runtime, not just a dashboard or browser build.
- The canonical HTTPS origin, raw webhook route, migrations and private image
  storage match the installed implementation. Preserve history and unrelated settings.
- Process, reconciliation, cleanup and health schedules use the separate worker
  secret in an authorization header. Workers do not start automatically at boot.
- Staging creation, replies and status changes work in both directions; signed
  relay delivery, backlog, failed/blocked work and missed-event reconciliation are checked.

Report GitHub access, shared-service readiness and live issue linkage separately.
Existing local-only tickets still require explicit **Send to GitHub**; setup never
bulk-exports them. Follow the shared runbook for revocation: rotating the service
credential stops new issuance, but existing GitHub tokens last until expiry unless
revoked or repository access is removed.
