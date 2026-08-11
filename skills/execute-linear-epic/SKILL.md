---
name: execute-linear-epic
description: Coordinates a Linear epic end to end with isolated worktrees and implementation subagents. Use when the user asks to execute, implement, resume, or work through a Linear epic or project with subagents.
---

# Execute Linear Epic

Execute the child issues of a Linear epic with one fresh implementation subagent per task and integrate them through an aggregation branch.

## Input

`epic` is required. Accept a Linear issue ID, project name, URL, or other unambiguous identifier. Stop and ask when it is missing or ambiguous.

## Resolve context

1. Fetch the epic and its child issues through the Linear MCP or other available integration. Record identifiers, descriptions, acceptance criteria, statuses, priorities, dependencies, and links.
2. Inspect the repository before changing it: current branch, worktree status, remote, default branch, local instructions, contribution docs, package scripts, and CI checks.
3. Preserve unrelated local changes. Update the remote default branch without rewriting local work.
4. Create or resume an aggregation branch using repository conventions; fall back to `epic/<epic-slug>`.
5. Order unfinished tasks by dependency, then priority, then identifier. Skip only tasks proven complete or already integrated.

## Execute each task

1. Confirm dependencies are satisfied and move the Linear issue to the team's active-work status.
2. Create a uniquely named branch and isolated worktree from the aggregation branch. Reuse existing task state only after verifying that it belongs to the same issue.
3. Delegate the implementation to a fresh subagent with a self-contained prompt containing the task, acceptance criteria, relevant repository context, allowed scope, expected checks, base branch, and completion contract.
4. Inspect the subagent's result and diff. Send focused follow-up instructions to the same subagent when correction is needed.
5. Run the smallest relevant checks discovered from repository conventions. Distinguish static checks from live, integration, or deployment proof.
6. Commit only the task's changes and push its branch. Ask the user for explicit permission before merging it into the aggregation branch.
7. After permission, confirm the branch head and checks are unchanged, merge using repository conventions, update the Linear issue to its completed status, and remove the worktree only after confirming integration.

## Completion and failures

- After all tasks are integrated, summarize tasks, branches, checks, skipped work, and unresolved risks. Leave the aggregation branch ready for the user's next integration step.
- If a subagent fails or produces an invalid result twice for the same task, stop and report the evidence.
- Rebase task branches on the aggregation branch when safe. Ask before resolving non-trivial conflicts or changing another contributor's work.
- Never merge without explicit permission, force-push over unknown commits, run destructive commands, change production systems, or weaken required checks without explicit authorization.
