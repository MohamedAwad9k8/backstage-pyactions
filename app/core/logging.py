import logging
import sys


def setup_logging(debug: bool = False) -> logging.Logger:
    level = logging.DEBUG if debug else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    # Quiet noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return logging.getLogger("backstage_pyactions")


logger = setup_logging()


class ActionLogger:
    """Logs to stdout AND collects messages for the API response."""

    def __init__(self, logs: list[str] | None = None, name: str = "backstage_pyactions"):
        self._logger = logging.getLogger(name)
        self.logs = logs if logs is not None else []

    def append(self, message: str, level: str = "info"):
        getattr(self._logger, level)(message)
        self.logs.append(message)
