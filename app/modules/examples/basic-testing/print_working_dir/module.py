import os

from .schemas import PrintWorkingDirParams


async def handler(params: PrintWorkingDirParams):
    abs_path = os.path.abspath(params.path)
    exists = os.path.isdir(abs_path)
    return {"status": "success", "path": abs_path, "exists": exists}
