from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel


class ActivityLogSchema(BaseModel):
    bot: Optional[str] = None
    user: Optional[int] = None
    activity: Optional[str] = None
    activity_type: Optional[str] = None
    activity_time: Optional[str] = None
    request_id: Optional[str] = None
    draft: Optional[str] = None


class ServiceStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"
    RUNING = "running"
