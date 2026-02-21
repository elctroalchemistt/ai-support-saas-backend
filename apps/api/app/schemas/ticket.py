from pydantic import BaseModel, Field

class TicketCreateIn(BaseModel):
    org_id: int
    subject: str = Field(min_length=1, max_length=200)
    priority: str = "medium"  # low/medium/high

class TicketOut(BaseModel):
    id: int
    org_id: int
    subject: str
    status: str
    priority: str

class MessageCreateIn(BaseModel):
    author_type: str = "user"  # user/agent/system
    body: str = Field(min_length=1, max_length=4000)

class MessageOut(BaseModel):
    id: int
    ticket_id: int
    author_type: str
    body: str
