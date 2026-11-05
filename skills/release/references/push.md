# Push verified release refs

Read when pushing is authorized, including retries of an already prepared release.
Complete local verification before these steps.

After local verification succeeds, honor `--push`, an explicit publication request, or `push.automatic` automatically, including for an already prepared release. `--local` or an explicit preparation-only request wins. If tagging is disabled and no tag is being published, push only the exact commit refspec; direct GitHub publication still requires a verified existing tag. Resolve the destination remote and branch from the user's request or the repository's documented push configuration/upstream. If the destination is missing or ambiguous, ask only for that information.

Before pushing, inspect the remote branch and exact tag. If the tag already
resolves to the release commit and that commit is reachable from the destination
branch, skip the push and continue the missing publication phase. A newer remote
branch must not be rewound to repair an old release. If only the tag is missing
and the commit is already on the branch, push only that exact tag. Reject a
conflicting remote tag without moving it.

When both refs need publishing, push the verified release commit and its exact
tag together using explicit refspecs:

```sh
git -c push.followTags=false push --atomic <remote> <release-commit>:refs/heads/<destination-branch> refs/tags/<tag>:refs/tags/<tag>
```

This includes any unpushed ancestors required by the release commit. Do not push other branches or tags, force-push, or move an existing tag. If the push fails or the remote does not support atomic pushes, stop and report the failure while preserving the local release for retry. Do not bump, recommit, or retag to retry a push.

Verify a newly pushed branch points to the release commit and the remote tag matches the local tag and resolves to that commit. When reusing an already published commit on a newer branch, verify reachability instead of requiring the branch to move backward. Report the destination, commit and tag as pushed only after both are confirmed; if verification is unavailable, report the push result and uncertainty.
