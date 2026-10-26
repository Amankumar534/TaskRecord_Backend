import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Task, Subtask, User, TaskStatus, TaskPriority
from app.schemas.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    SubtaskCreate,
    SubtaskUpdate,
    SubtaskResponse,
)

router = APIRouter()

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    priority_filter: Annotated[TaskPriority | None, Query(alias="priority")] = None,
    category_filter: Annotated[str | None, Query(alias="category")] = None,
    search: Annotated[str | None, Query()] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Task)
        .where(Task.user_id == current_user.id)
        .options(selectinload(Task.subtasks))
        .order_by(Task.created_at.desc())
    )

    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority_filter:
        query = query.where(Task.priority == priority_filter)
    if category_filter:
        query = query.where(Task.category.ilike(f"%{category_filter}%"))
    if search:
        query = query.where(
            (Task.name.ilike(f"%{search}%")) | (Task.description.ilike(f"%{search}%"))
        )

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if task_in.start_date > task_in.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date.",
        )

    task = Task(
        user_id=current_user.id,
        name=task_in.name,
        description=task_in.description,
        start_date=task_in.start_date,
        end_date=task_in.end_date,
        status=task_in.status,
        priority=task_in.priority,
        category=task_in.category,
    )
    db.add(task)
    await db.flush()  # assign task.id

    for sub_in in task_in.subtasks:
        subtask = Subtask(
            task_id=task.id,
            title=sub_in.title,
            is_completed=sub_in.is_completed,
        )
        db.add(subtask)

    await db.commit()
    await db.refresh(task)
    return task

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Task)
        .where(Task.id == task_id, Task.user_id == current_user.id)
        .options(selectinload(Task.subtasks))
    )
    result = await db.execute(query)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Task)
        .where(Task.id == task_id, Task.user_id == current_user.id)
        .options(selectinload(Task.subtasks))
    )
    result = await db.execute(query)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    start_date = update_data.get("start_date", task.start_date)
    end_date = update_data.get("end_date", task.end_date)
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date.",
        )

    for field, val in update_data.items():
        setattr(task, field, val)

    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await db.execute(query)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return None

# ----------------- Subtask Endpoints -----------------

@router.post("/{task_id}/subtasks", response_model=SubtaskResponse, status_code=status.HTTP_201_CREATED)
async def add_subtask(
    task_id: uuid.UUID,
    subtask_in: SubtaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify task ownership
    query = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await db.execute(query)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    subtask = Subtask(
        task_id=task.id,
        title=subtask_in.title,
        is_completed=subtask_in.is_completed,
    )
    db.add(subtask)
    await db.commit()
    await db.refresh(subtask)
    return subtask

@router.patch("/{task_id}/subtasks/{subtask_id}", response_model=SubtaskResponse)
async def update_subtask(
    task_id: uuid.UUID,
    subtask_id: uuid.UUID,
    subtask_in: SubtaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify task ownership
    t_query = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    t_res = await db.execute(t_query)
    if not t_res.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    s_query = select(Subtask).where(Subtask.id == subtask_id, Subtask.task_id == task_id)
    s_res = await db.execute(s_query)
    subtask = s_res.scalars().first()
    if not subtask:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtask not found")

    update_data = subtask_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(subtask, field, val)

    await db.commit()
    await db.refresh(subtask)
    return subtask

@router.delete("/{task_id}/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtask(
    task_id: uuid.UUID,
    subtask_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t_query = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    t_res = await db.execute(t_query)
    if not t_res.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    s_query = select(Subtask).where(Subtask.id == subtask_id, Subtask.task_id == task_id)
    s_res = await db.execute(s_query)
    subtask = s_res.scalars().first()
    if not subtask:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtask not found")

    await db.delete(subtask)
    await db.commit()
    return None
