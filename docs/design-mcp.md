# Task B: MCP server design

## Goal
Let an AI agent read and update tasks through MCP tools instead of raw HTTP calls.

## Components
- Task API (existing, deployed on Render + Supabase): the source of truth.
- MCP server (new, Python, official `mcp` SDK, stdio transport): a thin wrapper around the API.
- Agent (Task C, later): calls the MCP tools.

## Tools
- list_tasks(status?) -> GET /tasks
- get_task(task_id) -> GET /tasks/{id}
- update_task(task_id, status?, result?) -> PATCH /tasks/{id}

## Data flow
Agent -> MCP tool call -> MCP server -> HTTPS request to the Task API -> Postgres.
The API address comes from the TASK_API_URL environment variable (not hard-coded).

## Failure handling
- 404 from the API becomes a clear "task not found" tool error.
- 409 from the API becomes a clear "task already finished" tool error.
- Request timeout of 60 seconds, because the free Render instance can take about 50 seconds to wake up.
- The server contains no LLM, so every tool is deterministic.

## Acceptance checks
1. Each tool returns the API's data in a readable form.
2. update_task on a done or failed task returns the "task already finished" error.
3. An unknown task id returns "task not found".
4. Tests run with the API mocked, so no network is needed.

## Out of scope
Authentication, creating tasks, and deleting tasks.