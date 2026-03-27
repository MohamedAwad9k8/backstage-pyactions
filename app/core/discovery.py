import importlib
from pathlib import Path

import yaml
from fastapi import Depends, FastAPI

from app.core.logging import logger
from app.core.security import verify_api_token


def register_modules(app: FastAPI, config_path: str = "modules.yaml") -> None:
    path = Path(config_path)
    if not path.exists():
        logger.warning("modules.yaml not found — no modules registered")
        return

    config = yaml.safe_load(path.read_text())
    modules = config.get("modules", [])

    for module_cfg in modules:
        name = module_cfg["name"]
        module_path = module_cfg["path"]
        route = module_cfg["route"]
        description = module_cfg.get("description", "")

        try:
            mod = importlib.import_module(f"{module_path}.module")
            handler = getattr(mod, "handler")
        except (ModuleNotFoundError, AttributeError) as e:
            logger.error(f"Failed to load module '{name}' from '{module_path}': {e}")
            continue

        app.add_api_route(
            route,
            handler,
            methods=["POST"],
            name=name,
            description=description,
            dependencies=[Depends(verify_api_token)],
        )
        logger.info(f"Registered module: {name} -> POST {route}")
