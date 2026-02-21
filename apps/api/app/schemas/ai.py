from pydantic import BaseModel, Field

class DraftReplyIn(BaseModel):
    ticket_id: int
    tone: str = Field(default="friendly")  # friendly | formal

class DraftReplyOut(BaseModel):
    draft: str
