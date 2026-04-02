from pydantic import BaseModel, Field


class ListDirectoryParams(BaseModel):
    path: str = Field(description="Directory path to list")
