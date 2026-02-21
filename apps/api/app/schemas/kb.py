from pydantic import BaseModel, Field

class KBCreateIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=20000)
    tags: list[str] = []

class KBOut(BaseModel):
    id: int
    title: str
    body: str
    tags: list[str]
