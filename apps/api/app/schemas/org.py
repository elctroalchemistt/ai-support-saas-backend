from pydantic import BaseModel, Field

class OrgCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)

class OrgOut(BaseModel):
    id: int
    name: str
