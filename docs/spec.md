# Task Agent with MCP Server: Spec

## Goal
An agent that picks up GitHub issues labeled `agent-task`, looks up data through MCP tools, and comments back on the issue with its result.

## Components
1. API service (FastAPI + PostgreSQL): stores tasks and results, exposes REST endpoints and /health.
2. MCP server: exposes tools over the same data: list_open_tasks, get_task(task_id), mark_task_done(task_id, result).
3. Agent runner: polls GitHub for labeled issues, calls the LLM with the MCP tools, posts the answer as an issue comment.

## Data flow
GitHub issue (label: agent-task) -> agent runner -> LLM + MCP tools -> API/Postgres -> comment on the issue.

## Data model (tasks)
id, github_issue_id (unique), title, status (open / in_progress / done / failed), result, created_at, updated_at.

## Failure handling
- Tool call fails: log the error, mark the task failed after 3 retries, comment the failure on the issue.
- LLM returns invalid output: reject it, retry once, then mark failed.
- Same issue seen twice: github_issue_id is unique, so it is processed once.
- GitHub or API unavailable: back off and retry the next poll cycle.

## Security
- Tokens come from environment variables, never committed.
- MCP tools are least-privilege: no delete, only the three tools above.

## Acceptance checks
1. A labeled issue gets a comment within 1 minute.
2. A failing tool call is logged and not retried forever.
3. A duplicate issue does not create a second task.
4. GET /health returns OK after deployment on the VPS.
5. Automated tests cover the API, each MCP tool, and the duplicate case.

## Out of scope
UI, multi-user auth, other issue trackers.

## Build plan
- Task A: API service, database, tests.
- Task B: MCP server and its tests.
- Task C: agent runner, then Docker deployment.
