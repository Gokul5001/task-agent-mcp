from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Task, TaskStatus
from app.schemas import TaskCreate, TaskOut, TaskUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Task API", lifespan=lifespan)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok"}


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.scalar(select(Task).where(Task.github_issue_id == payload.github_issue_id))
    if existing:
        # Duplicate issue: return the existing task instead of creating a second one.
        response.status_code = 200
        return existing

    task = Task(github_issue_id=payload.github_issue_id, title=payload.title)
    db.add(task)
    try:
        db.commit()
    except IntegrityError:
        # Two requests raced and the other one won: return the row it created.
        db.rollback()
        existing = db.scalar(select(Task).where(Task.github_issue_id == payload.github_issue_id))
        response.status_code = 200
        return existing
    db.refresh(task)
    return task


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(status: TaskStatus | None = None, db: Session = Depends(get_db)):
    query = select(Task).order_by(Task.id)
    if status is not None:
        query = query.where(Task.status == status.value)
    return db.scalars(query).all()


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if payload.status is not None and task.status in (
        TaskStatus.done.value,
        TaskStatus.failed.value,
    ):
        raise HTTPException(status_code=409, detail="task already finished")
    if payload.status is not None:
        task.status = payload.status.value
    if payload.result is not None:
        task.result = payload.result
    db.commit()
    db.refresh(task)
    return task
