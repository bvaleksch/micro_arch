import time
import json
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def unique_name(prefix: str) -> str:
    """Generate a unique label/todo name for testing."""
    return f"{prefix}_{int(time.time() * 1000)}"


def post_json(path: str, payload: dict):
    return client.post(path, data=json.dumps(payload), headers={"Content-Type": "application/json"})


def patch_json(path: str, payload: dict):
    return client.patch(path, data=json.dumps(payload), headers={"Content-Type": "application/json"})


def test_create_label_and_conflict():
    name = unique_name("urgent")
    r1 = post_json("/labels", {"name": name})
    assert r1.status_code == 201, r1.text
    body = r1.json()
    assert body["name"] == name

    # Duplicate should 409
    r2 = post_json("/labels", {"name": name})
    assert r2.status_code == 409


def test_list_labels_contains_new_label():
    name = unique_name("lbl")
    post_json("/labels", {"name": name})
    r = client.get("/labels")
    assert r.status_code == 200
    labels = [l["name"] for l in r.json()]
    assert name in labels


def test_create_todo_with_labels():
    lbl1 = unique_name("school")
    lbl2 = unique_name("home")
    # ensure labels exist
    post_json("/labels", {"name": lbl1})
    post_json("/labels", {"name": lbl2})

    r = post_json("/todos", {
        "title": unique_name("Write homework"),
        "labels": [lbl1, lbl2]
    })
    assert r.status_code == 201, r.text
    todo = r.json()
    assert set(todo["labels"]) == {lbl1, lbl2}
    assert todo["done"] is False


def test_list_todos_and_filter_by_label():
    lbl = unique_name("filter")
    post_json("/labels", {"name": lbl})
    todo_title = unique_name("Buy milk")
    post_json("/todos", {"title": todo_title, "labels": [lbl]})

    r = client.get(f"/todos?label={lbl}")
    assert r.status_code == 200
    todos = r.json()
    assert any(t["title"] == todo_title for t in todos)


def test_patch_todo_toggle_done_and_replace_labels():
    # Create todo first
    lbl = unique_name("math")
    todo_title = unique_name("Solve task")
    todo = post_json("/todos", {"title": todo_title, "labels": [lbl]}).json()
    todo_id = todo["id"]

    # Update: mark done + change labels
    new_lbl = unique_name("updated")
    r2 = patch_json(f"/todos/{todo_id}", {"done": True, "labels": [new_lbl]})
    assert r2.status_code == 200, r2.text
    updated = r2.json()
    assert updated["done"] is True
    assert set(updated["labels"]) == {new_lbl}


def test_patch_nonexistent_returns_404():
    r = patch_json("/todos/999999999", {"done": True})
    assert r.status_code == 404

