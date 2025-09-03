from enum import IntFlag
from typing import Literal

from pydantic import BaseModel, Field


class CreditUpdateFrame(BaseModel):
    type: Literal["CreditUpdate"] = "CreditUpdate"
    flow_id: str = Field(..., description="Which flow to refill")
    credits: int = Field(..., description="Number of new credits granted")


class FlowFlags(IntFlag):
    NONE = 0
    SYN = 1 << 0  # initial window open
    ACK = 1 << 1  # credit update
    RESET = 1 << 2  # flow teardown
