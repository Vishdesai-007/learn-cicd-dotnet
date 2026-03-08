#!/usr/bin/env python3
"""
Claude PR Code Review
- Gets the diff for the current PR
- Sends it to Claude for review
- Posts the review as a comment on the Azure DevOps PR
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from base64 import b64encode


# ── Azure DevOps context (injected by pipeline) ──────────────────────────────
ORG_URI    = os.environ["SYSTEM_TEAMFOUNDATIONCOLLECTIONURI"].rstrip("/")
PROJECT    = os.environ["SYSTEM_TEAMPROJECT"]
REPO_ID    = os.environ["BUILD_REPOSITORY_ID"]
PR_ID      = os.environ.get("SYSTEM_PULLREQUEST_PULLREQUESTID")
ADO_TOKEN  = os.environ["SYSTEM_ACCESSTOKEN"]

# ── Anthropic ─────────────────────────────────────────────────────────────────
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL  = "claude-sonnet-4-6"


def get_diff() -> str:
    """Return the git diff between the PR branch and its target."""
    target = os.environ.get("SYSTEM_PULLREQUEST_TARGETBRANCH", "main").replace("refs/heads/", "")
    result = subprocess.run(
        ["git", "diff", f"origin/{target}...HEAD", "--", "*.cs", "*.csproj"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def call_claude(diff: str) -> str:
    """Send the diff to Claude and return the review text."""
    prompt = f"""You are a senior .NET engineer reviewing a pull request.
Review the following diff and provide concise, actionable feedback.

Focus on:
- Bugs or logic errors
- Missing error handling
- Security issues
- Code clarity and naming
- Test coverage gaps

Be direct and specific. Reference file names and line numbers where relevant.
If the code looks good, say so briefly.

<diff>
{diff[:12000]}
</diff>

Provide your review in markdown format."""

    payload = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
    )
    with urllib.request.urlopen(req) as resp:
        body = json.load(resp)
    return body["content"][0]["text"]


def post_pr_comment(text: str) -> None:
    """Post a thread comment on the Azure DevOps PR."""
    url = (
        f"{ORG_URI}/{PROJECT}/_apis/git/repositories/{REPO_ID}"
        f"/pullRequests/{PR_ID}/threads?api-version=7.1"
    )
    token_b64 = b64encode(f":{ADO_TOKEN}".encode()).decode()
    payload = json.dumps({
        "comments": [{"parentCommentId": 0, "content": text, "commentType": 1}],
        "status": 1
    }).encode()

    req = urllib.request.Request(
        url, data=payload,
        headers={
            "Authorization": f"Basic {token_b64}",
            "Content-Type": "application/json",
        }
    )
    with urllib.request.urlopen(req) as resp:
        if resp.status not in (200, 201):
            print(f"Warning: comment post returned {resp.status}", file=sys.stderr)
        else:
            print("PR comment posted.")


def main():
    if not PR_ID:
        print("Not a PR build — skipping Claude review.")
        return

    print("Getting diff...")
    diff = get_diff()
    if not diff:
        print("No .cs/.csproj changes in this PR — skipping review.")
        return

    print(f"Sending {len(diff)} chars to Claude ({CLAUDE_MODEL})...")
    review = call_claude(diff)

    header = "## Claude Code Review\n\n"
    full_comment = header + review
    print("\n--- Review ---")
    print(full_comment)
    print("--------------\n")

    post_pr_comment(full_comment)


if __name__ == "__main__":
    main()
