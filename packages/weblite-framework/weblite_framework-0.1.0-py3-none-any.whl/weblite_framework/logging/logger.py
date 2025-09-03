"""Модуль логирования для weblite-framework."""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

__all__ = [
    'JsonFormatter',
    'get_logger',
]


class JsonFormatter(logging.Formatter):
    """Класс для преобразования записей логов в JSON-строки с полями."""

    def format(self, record: logging.LogRecord) -> str:
        """Форматирует запись лога в JSON строку.

        Поля:
        timestamp: Временная метка
        level: Уровень логирования
        source: Источник сообщения (модуль)
        message: Текст сообщения

        Args:
            record: Запись лога для форматирования

        Returns:
              JSON-строка с отформатированным логом
        """
        log_record = {
            'timestamp': datetime.fromtimestamp(record.created)
            .astimezone()
            .isoformat(),
            'level': record.levelname,
            'source': record.module,
            'message': record.getMessage(),
        }
        return json.dumps(log_record, ensure_ascii=False)


_loggers: dict[str, logging.Logger] = {}
_handler: logging.Handler | None = None


def get_handler() -> logging.Handler:
    """Создает и возвращает обработчик логов.

    Обработчик использует очередь и listener для асинхронного логирования
    во всех логгерах.

    Returns:
        logging.Handler: Настроенный обработчик логов
    """
    global _handler

    if _handler is not None:
        return _handler

    log_queue: Queue[logging.LogRecord] = Queue()

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(fmt=JsonFormatter())

    listener = QueueListener(log_queue, stream_handler)
    listener.start()

    _handler = QueueHandler(queue=log_queue)

    return _handler


def get_logger(name: str) -> logging.Logger:
    """Создает и возвращает логгер.

    Логирование происходит в отдельном потоке через QueueHandler.

    Args:
        name: str

    Returns:
        logging.Logger: Настроенный логгер
    """
    if name in _loggers:
        return _loggers[name]

    logger: logging.Logger = logging.getLogger(name=name)
    logger.setLevel(level=logging.INFO)
    logger.addHandler(hdlr=get_handler())

    _loggers[name] = logger

    return logger
