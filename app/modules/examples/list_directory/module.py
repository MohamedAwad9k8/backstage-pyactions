import os

from .schemas import ListDirectoryParams


async def handler(params: ListDirectoryParams):
    entries = os.listdir(params.path)
    return {"status": "success", "path": params.path, "entries": entries}
