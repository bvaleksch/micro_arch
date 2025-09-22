import random
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import engine, Base, get_db
from models import Todo, Label
from schemas import TodoCreate, TodoUpdate, TodoOut, LabelCreate, LabelOut

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API with Labels")


# ---------- Utility ----------
def random_id():
    return random.randint(0, 2**32 - 1)

def todo_to_out(todo: Todo) -> TodoOut:
    """Convert SQLAlchemy Todo to Pydantic schema with label names."""
    return TodoOut(
        id=todo.id,
        title=todo.title,
        done=todo.done,
        due_date=todo.due_date,
        labels=[lbl.name for lbl in todo.labels],
        created_at=todo.created_at,
        updated_at=todo.updated_at,
    )


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=RedirectResponse)
def root():
    return RedirectResponse(url="/static/index.html", status_code=307)


# ---------- Labels ----------

@app.post("/labels", response_model=LabelOut, status_code=201)
def create_label(payload: LabelCreate, db: Session = Depends(get_db)):
    existing = db.query(Label).filter(Label.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Label '{payload.name}' already exists")
    lbl = Label(id=random_id(), name=payload.name)
    db.add(lbl)
    db.commit()
    db.refresh(lbl)
    return lbl


@app.get("/labels", response_model=List[LabelOut])
def list_labels(q: Optional[str] = Query(None), db: Session = Depends(get_db)):
    qset = db.query(Label)
    if q:
        qset = qset.filter(Label.name.ilike(f"%{q.lower()}%"))
    return qset.order_by(Label.id).all()


# ---------- Todos ----------

@app.post("/todos", response_model=TodoOut, status_code=201)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    labels = []
    for name in payload.labels or []:
        lbl = db.query(Label).filter(Label.name == name).first()
        if not lbl:
            lbl = Label(id=random_id(), name=name)
            db.add(lbl)
            db.flush()  # ensures lbl.id is populated
        labels.append(lbl)

    todo = Todo(
        id=random_id(),
        title=payload.title,
        due_date=payload.due_date,
        labels=labels,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo_to_out(todo)


@app.get("/todos", response_model=List[TodoOut])
def list_todos(
    done: Optional[bool] = None,
    label: Optional[str] = None,
    due_before: Optional[str] = None,
    due_after: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Todo)
    if done is not None:
        q = q.filter(Todo.done == done)
    if label:
        q = q.join(Todo.labels).filter(Label.name == label.lower())
    if due_before:
        q = q.filter(Todo.due_date <= due_before)
    if due_after:
        q = q.filter(Todo.due_date >= due_after)

    todos = q.order_by(Todo.created_at.desc()).all()
    return [todo_to_out(t) for t in todos]


@app.patch("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)):
    todo = db.query(Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")

    if payload.title is not None:
        todo.title = payload.title
    if payload.due_date is not None:
        todo.due_date = payload.due_date
    if payload.done is not None:
        todo.done = payload.done
    if payload.labels is not None:
        new_labels = []
        for name in payload.labels:
            lbl = db.query(Label).filter(Label.name == name).first()
            if not lbl:
                lbl = Label(id=random_id(), name=name)
                db.add(lbl)
                db.flush()
            new_labels.append(lbl)
        todo.labels = new_labels

    db.commit()
    db.refresh(todo)
    return todo_to_out(todo)

