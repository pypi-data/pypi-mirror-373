"""Модуль моделей SQLAlchemy."""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

__all__ = ['BaseModel']


class BaseModel(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    pass
