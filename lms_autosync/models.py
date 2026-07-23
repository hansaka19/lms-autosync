from dataclasses import dataclass
from typing import Optional

@dataclass
class DeadlineItem:
    item_id: str
    course: str
    item_name: str
    item_type: str            # assignment | quiz | choice | other
    due_at: Optional[str]
    submission_url: Optional[str]
    status: str = "unknown"   # Submitted | Not submitted | Overdue | Due Soon

@dataclass
class SessionItem:
    item_id: str
    course: str
    title: str
    session_type: str         # lecture | lab
    scheduled_at: Optional[str]
    zoom_url: Optional[str]

@dataclass
class ResourceItem:
    item_id: str
    course: str
    name: str
    resource_type: str        # pdf | slides | link | other
    url: str