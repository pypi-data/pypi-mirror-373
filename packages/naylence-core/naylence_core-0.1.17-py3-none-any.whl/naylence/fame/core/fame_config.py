from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class FameConfig(BaseModel):
    fabric: Optional[Any] = Field(None, description="Fame fabric config")
