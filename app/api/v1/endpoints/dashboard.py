from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Task, User, TaskStatus, TaskPriority
from app.schemas.schemas import TaskStats

router = APIRouter()

@router.get("/stats", response_model=TaskStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Task)
        .where(Task.user_id == current_user.id)
        .options(selectinload(Task.subtasks))
    )
    result = await db.execute(query)
    tasks = result.scalars().all()

    total_tasks = len(tasks)
    completed_tasks = 0
    in_progress_tasks = 0
    pending_tasks = 0
    blocked_tasks = 0
    urgent_count = 0
    total_subtasks = 0
    completed_subtasks = 0

    category_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {
        TaskPriority.LOW.value: 0,
        TaskPriority.MEDIUM.value: 0,
        TaskPriority.HIGH.value: 0,
        TaskPriority.URGENT.value: 0,
    }

    for t in tasks:
        # Status counting
        if t.status == TaskStatus.COMPLETED:
            completed_tasks += 1
        elif t.status == TaskStatus.IN_PROGRESS:
            in_progress_tasks += 1
        elif t.status == TaskStatus.PENDING:
            pending_tasks += 1
        elif t.status == TaskStatus.BLOCKED:
            blocked_tasks += 1

        # Priority counting
        priority_val = t.priority.value if hasattr(t.priority, "value") else str(t.priority)
        priority_counts[priority_val] = priority_counts.get(priority_val, 0) + 1
        if t.priority in (TaskPriority.URGENT, TaskPriority.HIGH):
            urgent_count += 1

        # Category counting
        cat = t.category or "General"
        category_counts[cat] = category_counts.get(cat, 0) + 1

        # Subtasks
        for s in t.subtasks:
            total_subtasks += 1
            if s.is_completed:
                completed_subtasks += 1

    completion_rate = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    return TaskStats(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        pending_tasks=pending_tasks,
        blocked_tasks=blocked_tasks,
        completion_rate=completion_rate,
        total_subtasks=total_subtasks,
        completed_subtasks=completed_subtasks,
        urgent_count=urgent_count,
        tasks_by_category=category_counts,
        tasks_by_priority=priority_counts,
    )
