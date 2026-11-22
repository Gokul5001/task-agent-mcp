def make_task(client, issue_id=1, title="Fix login bug"):
    return client.post("/tasks", json={"github_issue_id": issue_id, "title": title})


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task(client):
    response = make_task(client)
    assert response.status_code == 201
    body = response.json()
    assert body["github_issue_id"] == 1
    assert body["title"] == "Fix login bug"
    assert body["status"] == "open"
    assert body["result"] is None


def test_duplicate_issue_returns_existing_task(client):
    first = make_task(client, issue_id=7, title="First title")
    second = make_task(client, issue_id=7, title="Different title")
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["title"] == "First title"
    assert len(client.get("/tasks").json()) == 1


def test_create_task_validation(client):
    assert client.post("/tasks", json={"github_issue_id": 0, "title": "x"}).status_code == 422
    assert client.post("/tasks", json={"github_issue_id": 1, "title": ""}).status_code == 422
    assert client.post("/tasks", json={"title": "no id"}).status_code == 422


def test_list_tasks_and_filter_by_status(client):
    a = make_task(client, 1, "A").json()
    make_task(client, 2, "B")
    client.patch(f"/tasks/{a['id']}", json={"status": "done"})

    assert len(client.get("/tasks").json()) == 2
    done = client.get("/tasks", params={"status": "done"}).json()
    assert [t["github_issue_id"] for t in done] == [1]
    opened = client.get("/tasks", params={"status": "open"}).json()
    assert [t["github_issue_id"] for t in opened] == [2]


def test_list_tasks_invalid_status(client):
    assert client.get("/tasks", params={"status": "nonsense"}).status_code == 422


def test_get_task(client):
    created = make_task(client).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_task_not_found(client):
    assert client.get("/tasks/999").status_code == 404


def test_patch_task_status_and_result(client):
    created = make_task(client).json()
    response = client.patch(
        f"/tasks/{created['id']}", json={"status": "done", "result": "Fixed in PR #12"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "done"
    assert body["result"] == "Fixed in PR #12"


def test_patch_invalid_status(client):
    created = make_task(client).json()
    response = client.patch(f"/tasks/{created['id']}", json={"status": "banana"})
    assert response.status_code == 422


def test_patch_not_found(client):
    assert client.patch("/tasks/999", json={"status": "done"}).status_code == 404
