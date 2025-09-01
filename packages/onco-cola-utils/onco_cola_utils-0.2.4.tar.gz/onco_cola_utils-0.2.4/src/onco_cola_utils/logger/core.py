"""ЯДРО"""

import sys
from typing import Any, Callable

from loguru import logger

logger.remove()

# Добавляем новый обработчик с цветами как в стандартном debug
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <level>{message}</level>",
    level="DEBUG",
    filter=lambda record: record["level"].name == "DEBUG",
    colorize=True  # Включаем цветной вывод
)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <level>{message}</level>",
    level="ERROR",
    filter=lambda record: record["level"].name == "ERROR",
    colorize=True  # Включаем цветной вывод
)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <level>{message}</level>",
    level="INFO",
    filter=lambda record: record["level"].name == "INFO",
    colorize=True  # Включаем цветной вывод
)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <level>{message}</level>",
    level="SUCCESS",
    filter=lambda record: record["level"].name == "SUCCESS",
    colorize=True  # Включаем цветной вывод
)
log = logger.debug
logerr = logger.error
loginf: Callable[[str, tuple[Any, ...], dict[str, Any]], None] | Callable[[Any], None] = logger.info
logsuc = logger.success
