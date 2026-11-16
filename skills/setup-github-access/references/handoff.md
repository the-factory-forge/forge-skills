# Verification and server handoff

Use current [App authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app)
and [installation-token documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app).
Load credentials privately and emit only allowlisted non-secret IDs/status.
Never print raw responses, PEMs, JWTs, tokens, webhook payloads or request headers.

## Verify GitHub access

1. Authenticate with this customer's App key. `GET /app` must match the intended
   owner, App ID, slug, Issues write/Metadata read permissions and subscribed events.
   Resolve and verify the numeric `[bot]` user ID independently.
2. Inspect the App webhook configuration privately: exact customer HTTPS origin
   plus `/api/supports/github-webhook`, active delivery and SSL verification.
   Use the same webhook secret in GitHub and this customer's backend.
3. Verify `GET /repos/{owner}/{repo}/installation`, selected-repository mode,
   permissions and absence of suspension. Inspect the complete selection in App
   installation settings or through paginated installation repository results.
   It must contain exactly this customer's repository. A token already narrowed
   to one repository cannot prove the installation's full scope.
4. Request an installation token with the pinned repository ID and explicit Issues
   write/Metadata read permissions. Privately check expiry and returned scope.
   Read the repository using that token and verify private visibility, exact ID
   and owner/name, unarchived state and active Issues. No other customer's key or
   repository access may be used as a fallback.

Live issue/comment writes require an authorized staging repository or test
conversation. A successful webhook ping does not establish issue delivery.

## Produce a protected handoff

Follow the installed host's schema. If it still uses shared-service authentication,
label the handoff as pending source adoption rather than placing a private key in
an unsupported runtime.

| Field | Source |
| --- | --- |
| `SUPPORT_GITHUB_APP_ID` | Customer App's numeric ID from the verified registration |
| `SUPPORT_GITHUB_PRIVATE_KEY` | That App's RSA PEM; real line breaks or literal `\n` sequences |
| `SUPPORT_GITHUB_INSTALLATION_ID` | Verified dedicated App installation |
| `SUPPORT_GITHUB_REPOSITORY_ID` | Exact private repository ID |
| `SUPPORT_GITHUB_BOT_USER_ID` | Verified numeric customer App bot ID |
| `SUPPORT_GITHUB_REPOSITORY` | Override when repository name differs from stable `SITE_NAME` |
| `SUPPORT_GITHUB_WEBHOOK_SECRET` | Same unique secret configured on this App's direct webhook |

The current host fixes the owner to `the-factory-forge`. A different owner needs
an explicitly scoped host change. App, installation and bot IDs are customer-specific;
remove inherited shared App defaults. A temporary installation token cannot replace
the long-lived App credential handoff.

Use the user's secret store, or resolve
`git rev-parse --path-format=absolute --git-common-dir` for a private
`support-setup/` directory outside tracked source. Restrict directories to 0700 and
files to 0600, or equivalent ACLs. Preserve existing credentials and handoffs;
missing access does not authorize rotation. Never put real values in tracked
examples, command arguments, build variables, logs or chat.

For a manifest-created App, preserve the returned private key and webhook secret.
For manual registration, generate a cryptographically random 32-byte base64url
webhook secret and set that same value in GitHub and the handoff. Serialize the PEM
for the actual dotenv or Dokploy parser and verify parsing privately. The original `SUPPORT_GITHUB_SERVICE_TOKEN`
and `SUPPORT_GITHUB_TOKEN_URL` are obsolete after source adoption. No token hash,
`CORNER_SUPPORT_CONFIG`, shared relay secret or separate service deployment is needed.

## Host completion within scope

For user-managed deployment, provide the protected paths and remaining steps.
For authorized deployment, follow the destination's procedure and verify:

- Credentials reach the site's server runtime. The private key and webhook secret
  remain server-only; the production build must not embed them in public output.
- The HTTPS origin, raw webhook route, migrations and private image storage match
  the installed adapter. Preserve data and unrelated deployment configuration.
- Internal process, reconciliation and cleanup tasks run with sanitized outcomes.
  Older HTTP-based hosts remove external schedules and `SUPPORT_MAINTENANCE_SECRET`
  only after adopting internal tasks.
- Authorized staging creation, replies and status changes work both ways; direct
  signatures, replay handling, failed work and missed-event reconciliation are checked.

Existing local-only tickets still require explicit **Send to GitHub**. Existing
bindings from a different App require a reviewed migration before cutover; never
clear receipts, reset jobs or re-export discussions to make a check pass.
On revocation, account for already-issued tokens until expiry or separate revocation.
Report source adoption, App access, runtime deployment and delivery separately.
