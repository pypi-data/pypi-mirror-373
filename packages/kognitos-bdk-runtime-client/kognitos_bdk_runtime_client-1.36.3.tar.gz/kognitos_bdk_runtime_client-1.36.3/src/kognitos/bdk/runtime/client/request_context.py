from dataclasses import dataclass
from typing import Optional


@dataclass
class RequestContext:
    trace_id: Optional[int] = None
    span_id: Optional[int] = None
    worker_id: Optional[str] = None
    department_id: Optional[str] = None
    knowledge_id: Optional[str] = None
    line_id: Optional[str] = None
