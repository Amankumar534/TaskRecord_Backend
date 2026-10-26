import uuid
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.models import TaskStatus, TaskPriority

# ----------------- Subtask Schemas -----------------
class SubtaskBase(BaseModel):
    title: str
    is_completed: bool = False

class SubtaskCreate(SubtaskBase):
    pass

class SubtaskUpdate(BaseModel):
    title: str | None = None
    is_completed: bool | None = None

class SubtaskResponse(SubtaskBase):
    id: uuid.UUID
    task_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------- Task Schemas -----------------
class TaskBase(BaseModel):
    name: str
    description: str | None = None
    start_date: date
    end_date: date
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    category: str = "General"

class TaskCreate(TaskBase):
    subtasks: list[SubtaskCreate] = []

class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    category: str | None = None

class TaskResponse(TaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    subtasks: list[SubtaskResponse] = []
    model_config = ConfigDict(from_attributes=True)

# ----------------- User & Auth Schemas -----------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    avatar_url: str | None = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: str | None = None

# ----------------- Dashboard & Analytics Schemas -----------------
class TaskStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    blocked_tasks: int
    completion_rate: int
    total_subtasks: int
    completed_subtasks: int
    urgent_count: int
    tasks_by_category: dict[str, int]
    tasks_by_priority: dict[str, int]
