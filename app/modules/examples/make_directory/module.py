import os

from .schemas import MakeDirectoryParams


async def handler(params: MakeDirectoryParams):
    full_path = os.path.join(params.path, params.name)
    os.makedirs(full_path, exist_ok=True)
    return {"status": "success", "created": full_path}
