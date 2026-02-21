from pydantic import BaseModel
from typing import Literal

TicketStatus = Literal["open", "closed"]

class TicketStatusUpdate(BaseModel):
    status: TicketStatus
