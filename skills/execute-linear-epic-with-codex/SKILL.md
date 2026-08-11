---
name: execute-linear-epic-with-codex
description: Coordinates a Linear epic through the Codex plugin for Claude Code, GitHub pull requests, and continuous review monitoring. Use when the user asks to execute or resume a Linear epic specifically with the Claude Code Codex plugin and PR babysitting.
---

# Execute Linear Epic with Codex

Execute the child issues of a Linear epic with the Codex plugin for Claude Code, isolated worktrees, GitHub PRs, and continuous review monitoring.

## Input

`epic` is required. Accept a Linear issue ID, project name, URL, or other unambiguous identifier. Stop and ask when it is missing or ambiguous.

## Requirements

- Require the Codex plugin for Claude Code and an authenticated GitHub CLI.
- Invoke the `codex:codex-rescue` agent or `/codex:rescue` for implementation and review fixes. If neither is available, stop and report the missing requirement.

## Resolve context

1. Fetch the epic and its child issues through the Linear MCP or other available integration. Record identifiers, descriptions, acceptance criteria, statuses, priorities, dependencies, and links.
2. Inspect the repository before changing it: current branch, worktree status, remote, default branch, local instructions, contribution docs, package scripts, and CI checks.
3. Preserve unrelated local changes. Update the remote default branch without rewriting local work.
4. Create or resume an aggregation branch using repository conventions; fall back to `epic/<epic-slug>`.
5. Order unfinished tasks by dependency, then priority, then identifier. Skip only tasks proven complete or already merged.

## Execute each task

1. Confirm dependencies are satisfied and move the Linear issue to the team's active-work status.
2. Create a uniquely named branch and isolated worktree from the aggregation branch. Reuse existing task state only after verifying that it belongs to the same issue.
3. Invoke Codex with a self-contained prompt containing the task, acceptance criteria, relevant repository context, allowed scope, expected checks, base branch, and completion contract. Start the executor monitoring loop below immediately.
4. After Codex completes, inspect its result and diff. Send focused follow-up instructions through the plugin when correction is needed, and monitor every follow-up invocation the same way.
5. Run the smallest relevant checks discovered from repository conventions. Distinguish static checks from live, integration, or deployment proof.
6. Commit only the task's changes, push its branch, and open a GitHub PR targeting the aggregation branch. Include the Linear link, scope, verification, and limitations; link the PR back to Linear.
7. Keep the review monitoring loop below active until the PR is merged or the user interrupts the workflow.
8. When a merge condition fires, ask the user for explicit permission to merge that PR. After permission, re-check its head revision and required checks, merge using the repository's required method, update Linear, and remove the worktree only after confirming integration.

## Codex executor monitoring

Monitor every Codex invocation at fixed 5-minute intervals until it completes, fails, or requests input. Use whichever task, thread, process, terminal, wait, or scheduling tools you have available.

On every executor check:

1. Confirm that the Codex execution still exists and determine whether it is running, blocked, completed, or failed.
2. Inspect its latest progress or output. Respond to actionable input and surface approval requests to the user when required.
3. If it is still running, schedule the next check for 5 minutes later before ending the turn. Never leave an active execution without another check scheduled.
4. Do not infer completion from silence. Continue only after retrieving a completed result; count an execution that stopped without a usable result as a failed attempt.

## Review monitoring

The polling loop must stay active for the entire time a PR is open. Use whichever wait, scheduling, task, thread, or automation mechanism you have available. Never end a turn or go idle without scheduling the next poll unless the PR was merged or the user interrupted the workflow. If a poll fails, still schedule the next one.

On every poll:

1. Fetch comments and reviews with `gh pr view <number> --comments` and `gh api repos/{owner}/{repo}/pulls/<number>/comments`.
2. Fetch reactions on the PR description with `gh api repos/{owner}/{repo}/issues/<number>/reactions` and inspect required checks.
3. Reproduce every actionable claim against the current diff before changing code, including bot feedback.
4. Apply these decision rules in order:
   - A thumbs-up reaction on the PR description or a thumbs-up comment is a merge condition: ask the user for permission and keep polling while awaiting the answer.
   - Valid findings are fixed through Codex in the same worktree, pushed, answered, and followed by another polling round.
   - If most new comments in a round are proven invalid, out of scope, or harmful, the review has degenerated: ask the user for permission to merge and explain why each dismissed comment was inadequate. Do not keep implementing bad feedback.
   - With no new comments, schedule another poll after 20-30 minutes. Silence never ends the loop.
5. Never merge without a fresh, explicit user confirmation for that PR. A merge condition only triggers the request for permission.

## Completion and failures

- After all task PRs are merged, summarize tasks, PRs, checks, skipped work, dismissed feedback, and unresolved risks. Leave the aggregation branch ready for final integration; do not open or merge its final PR unless asked.
- If Codex fails or produces an invalid result twice for the same task, stop and report the evidence.
- Rebase task branches on the aggregation branch when safe. Ask before resolving non-trivial conflicts or changing another contributor's work.
- Never merge without explicit permission, force-push over unknown commits, run destructive commands, change production systems, or weaken required checks without explicit authorization.
