from pydantic import BaseModel, Field


class PrintWorkingDirParams(BaseModel):
    path: str = Field(description="Path to check")
