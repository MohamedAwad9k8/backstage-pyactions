from pydantic import BaseModel, Field


class MakeDirectoryParams(BaseModel):
    path: str = Field(description="Parent directory path")
    name: str = Field(description="Name of the new folder")
