from pydantic import BaseModel
from typing import Optional

class TaskInfo(BaseModel):
    task_id:     str
    provider:    Optional[str] = None
    city:        Optional[str] = None
    url:         Optional[str] = None
    status:      str
    queued_at:   Optional[str] = None
    started_at:  Optional[str] = None
    finished_at: Optional[str] = None
    result:      Optional[dict] = None
    error:       Optional[str] = None

class TriggerResponse(BaseModel):
    message:     str
    total_tasks: int
    tasks:       list[TaskInfo]