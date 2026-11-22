import os

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("task-api")


def make_client() -> httpx.Client:
    base_url = os.environ.get("TASK_API_URL", "http://127.0.0.1:8000")
    # 60s because the free Render instance can take ~50s to wake up
    return httpx.Client(base_url=base_url.rstrip("/"), timeout=60.0)


def _call(method: str, path: str, **kwargs):
    with make_client() as client:
        response = client.request(method, path, **kwargs)
    if response.status_code == 404:
        raise ValueError("task not found")
    if response.status_code == 409:
        raise ValueError("task already finished")
    response.raise_for_status()
    return response.json()


@mcp.tool()
def list_tasks(status: str | None = None) -> list[dict]:
    """List tasks, optionally filtered by status (for example 'open')."""
    params = {"status": status} if status else None
    return _call("GET", "/tasks", params=params)


@mcp.tool()
def get_task(task_id: int) -> dict:
    """Get one task by its id."""
    return _call("GET", f"/tasks/{task_id}")


@mcp.tool()
def update_task(
    task_id: int, status: str | None = None, result: str | None = None
) -> dict:
    """Update a task's status and/or result text."""
    payload = {}
    if status is not None:
        payload["status"] = status
    if result is not None:
        payload["result"] = result
    if not payload:
        raise ValueError("nothing to update")
    return _call("PATCH", f"/tasks/{task_id}", json=payload)


if __name__ == "__main__":
    mcp.run()