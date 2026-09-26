import logging

from core.config import settings


def setup_logging() -> None:
    level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("radar").info(
        "Logging configured. app=%s debug=%s", settings.app_name, settings.debug
    )
