# 📘 Lab 1 – Todo API with Labels

This is the first lab assignment for the discipline **"Microservice Technologies and Architecture"**.
The task was to implement a **monolithic REST API** with at least **3 endpoints** and corresponding tests.

---

## 📂 Project Structure

```
lab1/
  ├── main.py          # FastAPI application
  ├── models.py        # SQLAlchemy models (Todo, Label, join table)
  ├── schemas.py       # Pydantic schemas (requests/responses)
  ├── database.py      # Database engine, session, Base
  ├── static/          # Static HTML frontend (index.html)
  └── db.db            # SQLite database (auto-created)
```

---

## 🚀 Features

* **Labels**: create and list labels
* **Todos**: create, list (with filters), update
* **Filters**: filter todos by `done`, `label`, and due date range
* **Frontend**: a minimal HTML/JS page in `/static/index.html` to interact with the API using `fetch`

---

## 🔗 Endpoints

### Labels

* `POST /labels` → create a new label
* `GET /labels` → list all labels (optional `q` filter)

### Todos

* `POST /todos` → create a new todo (with optional labels)
* `GET /todos` → list todos, supports query params:

  * `done=true|false`
  * `label=<label_name>`
  * `due_before=<datetime>`
  * `due_after=<datetime>`
* `PATCH /todos/{todo_id}` → update an existing todo (title, done, due\_date, labels)

---

---

## 📝 Notes

* SQLite is used for simplicity (`db.db` file).
* IDs are generated randomly in `main.py` (`random_id()`).
* The static page (`/static/index.html`) supports creating, editing, and filtering todos via API calls.
* This lab demonstrates a **monolithic REST API** architecture with FastAPI + SQLAlchemy + Pydantic.

