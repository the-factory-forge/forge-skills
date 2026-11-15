# Registration and recovery

Read only when bootstrapping The Corner Support shared App, repairing an existing
registration, or resuming an interrupted registration. Ordinary customer onboarding
reuses it and requires no App registration. Verify current
GitHub documentation before executing the selected registration method.

## Manifest registration

The [GitHub manifest flow](https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest)
creates the App and returns its ID, private key and webhook secret. Prefer it
when the available tooling can receive and store the response privately.

Verify the deployed service origin before using this template; `redirect_url` is the temporary
registration callback, distinct from the production webhook. Store generated credentials only for the
central service, never in a customer handoff:

```json
{
  "name": "The Corner Support",
  "url": "https://support.the-corner.swiss",
  "description": "Shared private issue synchronization for Forge Support",
  "hook_attributes": {
    "url": "https://support.the-corner.swiss/api/github/webhook",
    "active": true
  },
  "redirect_url": "http://127.0.0.1:LOCAL_PORT/callback",
  "public": false,
  "default_permissions": { "issues": "write", "metadata": "read" },
  "default_events": ["issues", "issue_comment"],
  "request_oauth_on_install": false
}
```

Submit JSON in the form field `manifest` to
`https://github.com/organizations/OWNER/settings/apps/new?state=RANDOM_STATE`,
or `https://github.com/settings/apps/new?state=RANDOM_STATE` for a personal owner.
GitHub redirects with a temporary code; exchange it with
`POST /app-manifests/{code}/conversions`. Complete the flow within one hour.

For a temporary callback receiver:

- Check that browser and receiver share the same loopback host before starting.
  Bind only `127.0.0.1` on an available port. If loopback is unavailable, use the
  manual route below rather than exposing a credential receiver publicly.
- Generate unpredictable state. Require exactly one matching state and one
  nonempty code, compare state in constant time, and encode/validate the code as
  one URL path segment. Reject invalid requests before any exchange. Accept only
  one successful conversion. Keep all callback query strings out of access logs.
- Preflight a private writable output directory and use exclusive file creation
  with mode `0600` (`0700` directory; equivalent ACLs on other platforms). Capture
  the conversion response directly into protected storage before further parsing
  or verification. Never print it, put it in command arguments, or embed it in the
  completion page. Keep its unused OAuth secret out of the final host handoff.
- Redirect to a clean completion URL, use a bounded lifetime, and stop the
  receiver on success or cancellation. Test any new callback helper with fake
  responses, including wrong/duplicate state, duplicate code and existing output;
  tests must not register an App or contact GitHub.

These callback precautions protect the generated credentials; the actual
registration and installation still pass through GitHub's authenticated flow.

## Manual registration fallback

Follow [Registering a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app)
under `the-factory-forge` using the settings from the entrypoint. Supply a freshly
generated App webhook secret meeting the shared service requirements. Generate a private key
only for the new shared App or an authorized rotation; retain it centrally. Route the downloaded PEM into the
protected handoff using supported tools, restrict its permissions immediately,
and remove incidental download copies after the handoff is verified. Do not
request an OAuth client secret for the current server integration.

If available tools cannot capture credentials privately, complete independent
non-secret setup and hand that credential step to the user. Never request the
PEM or webhook secret in chat.

## Resume without duplicating resources

| Observed state                                       | Next action                                                                                                                                                 |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Authentication interrupted before creation           | Re-read the browser and App list; resume the existing form if no App was created.                                                                           |
| App exists, conversion result uncertain              | Inspect protected output and registration first. Preserve any received credentials; do not repeat creation or blindly exchange a possibly consumed code.    |
| App exists, credentials unavailable                  | Report which credentials are missing. Recover through an authorized key/secret rotation and coordinate any host update; do not delete and recreate the App. |
| App exists, installation absent or pending           | Resume selected-repository installation/approval; preserve the registration and existing customer selections.                                               |
| Installation exists, webhook fails                   | Inspect configuration and safe delivery status. Missing host configuration is a host handoff item, not a reason to recreate the App.                        |
| Existing App has broader access or different purpose | Leave it unchanged. Locate The Corner Support or resolve the explicit architecture/scope decision.                                                          |
