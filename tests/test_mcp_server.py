import json

import httpx
import pytest

from mcp_server import server

TASK = {
    "id": 1,
    "github_issue_id": 1,
    "title": "deploy check",
    "status": "open",
    "result": None,
}


def fake_api(handler):
    """Replace the real HTTP client with one that calls `handler` instead of the network."""

    def make_client():
        return httpx.Client(
            base_url="http://fake", transport=httpx.MockTransport(handler)
        )

    return make_client


def test_list_tasks_returns_api_data(monkeypatch):
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/tasks"
        return httpx.Response(200, json=[TASK])

    monkeypatch.setattr(server, "make_client", fake_api(handler))
    assert server.list_tasks() == [TASK]


def test_list_tasks_passes_status_filter(monkeypatch):
    def handler(request):
        assert request.url.params["status"] == "open"
        return httpx.Response(200, json=[TASK])

    monkeypatch.setattr(server, "make_client", fake_api(handler))
    assert server.list_tasks(status="open") == [TASK]


def test_get_task_returns_api_data(monkeypatch):
    def handler(request):
        assert request.url.path == "/tasks/1"
        return httpx.Response(200, json=TASK)

    monkeypatch.setattr(server, "make_client", fake_api(handler))
    assert server.get_task(1) == TASK


def test_get_unknown_task_says_not_found(monkeypatch):
    def handler(request):
        return httpx.Response(404, json={"detail": "task not found"})

    monkeypatch.setattr(server, "make_client", fake_api(handler))
    with pytest.raises(ValueError, match="task not found"):
        server.get_task(9999)


def test_update_finished_task_says_already_finished(monkeypatch):
    def handler(request):
        return httpx.Response(409, json={"detail": "task already finished"})

    monkeypatch.setattr(server, "make_client", fake_api(handler))
    with pytest.raises(ValueError, match="task already finished"):
        server.update_task(1, status="open")


def test_update_task_sends_only_given_fields(monkeypatch):
    def handler(request):
        assert request.method == "PATCH"
        assert request.url.path == "/tasks/1"
        assert json.loads(request.content) == {"status": "done", "result": "ok"}
        return httpx.Response(200, json={**TASK, "status": "done", "result": "ok"})

    monkeypatch.setattr(server, "make_client", fake_api(handler))
    updated = server.update_task(1, status="done", result="ok")
    assert updated["status"] == "done"


def test_update_with_nothing_makes_no_request(monkeypatch):
    def handler(request):
        raise AssertionError("no request should be sent")

    monkeypatch.setattr(server, "make_client", fake_api(handler))
    with pytest.raises(ValueError, match="nothing to update"):
        server.update_task(1)




def test_update_with_invalid_status_says_invalid_input(monkeypatch):
    def handler(request):
        return httpx.Response(422, json={"detail": "invalid status"})

    monkeypatch.setattr(server, "make_client", fake_api(handler))
    with pytest.raises(ValueError, match="invalid input"):
        server.update_task(1, status="nonsense")

        