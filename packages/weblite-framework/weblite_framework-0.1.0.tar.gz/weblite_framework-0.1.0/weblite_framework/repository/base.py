"""Модуль базового репозитория для работы с БД."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy import Executable, Result
from sqlalchemy.ext.asyncio import AsyncSession

from weblite_framework.database.models import BaseModel

__all__ = [
    'BaseRepositoryClass',
]

DTO = TypeVar('DTO')
SQLModel = TypeVar('SQLModel', bound=BaseModel)


class BaseRepositoryClass(Generic[DTO, SQLModel], ABC):
    """Базовый репозиторий с общим контролем выполняемых транзакций."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует экземпляр репозитория.

        Args:
            session: AsyncSession
        """
        self.__session = session

    def _get_session_for_testing(self) -> AsyncSession:
        """Возвращает сессию для тестирования.

        Returns:
            AsyncSession: Сессия для тестирования
        """
        return self.__session

    @abstractmethod
    def _model_to_dto(self, model: SQLModel) -> DTO:
        """Производит маппинг данных из ORM модели в класс DTO.

        Args:
            model: ORM модель

        Returns:
            DTO: объект dataclass
        """
        pass

    @abstractmethod
    def _dto_to_model(self, dto: DTO) -> SQLModel:
        """Производит маппинг данных из DTO класса в ORM модель.

        Args:
            dto: объект dataclass

        Returns:
            SQLModel: ORM модель
        """
        pass

    async def _add_record(
        self,
        model: SQLModel,
    ) -> SQLModel:
        """Создает запись в БД.

        Данный метод создает запись в БД
        и обновляет поля модели без коммита.

        Args:
            model: ORM модель

        Returns:
            SQLModel: ORM модель с присвоенным идентификатором
        """
        try:
            self.add(model)
            await self.flush()
            return model
        except Exception as e:
            await self.__session.rollback()
            raise e

    def _prepare_ignore_fields(
        self,
        ignore_fields: list[str] | None = None,
    ) -> list[str]:
        """Подготавливает список игнорируемых полей.

        Args:
            ignore_fields: Список игнорируемых полей

        Returns:
            list[str]: Подготовленный список игнорируемых полей
        """
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.append('_sa_instance_state')
        return ignore_fields

    def _update_model_fields(
        self,
        existing_model: SQLModel,
        new_data: SQLModel,
        ignore_fields: list[str],
    ) -> None:
        """Обновляет поля модели.

        Args:
            existing_model: Существующая модель
            new_data: Новые данные
            ignore_fields: Список игнорируемых полей
        """
        for key, value in new_data.__dict__.items():
            if key not in ignore_fields:
                setattr(existing_model, key, value)

    async def _update(
        self,
        existing_model: SQLModel,
        new_data: SQLModel,
        ignore_fields: list[str] | None = None,
    ) -> SQLModel:
        """Обновляет существующую запись в БД.

        Данный метод обновляет данные в существующей записи в БД,
        при этом коммит не производится.

        Args:
            existing_model: ORM модель с информацией, связанная с записью в БД
            new_data: ORM модель с данными для обновления
            ignore_fields: Список игнорируемых полей

        Returns:
            SQLModel: ORM модель, связанная с БД с обновленными полями
        """
        try:
            prepared_ignore_fields = self._prepare_ignore_fields(ignore_fields)
            self._update_model_fields(
                existing_model=existing_model,
                new_data=new_data,
                ignore_fields=prepared_ignore_fields,
            )
            await self.flush()
            return existing_model
        except Exception as e:
            await self.__session.rollback()
            raise e

    def add(self, instance: SQLModel) -> None:
        """Выполняет добавление в сессию переданного instance.

        Args:
            instance: ORM модель
        """
        self.__session.add(instance)

    async def commit(self) -> None:
        """Выполняет коммит в текущей сессии."""
        try:
            await self.__session.commit()
        except Exception as e:
            await self.__session.rollback()
            raise e

    async def execute(
        self,
        statement: Executable,
        is_use_active_transaction: bool = True,
    ) -> Result[Any]:
        """Выполняет переданный SQL-запрос с учетом активной транзакции.

        Данный метод выполняет переданный запрос, при этом:
            Если передать is_use_active_transaction=True,
                новая транзакция создана не будет.
                Используется для связки методов,
                которые должны выполняться атомарно.
                Такие методы в дочерних классах должны
                быть объявлены как _protected.
            Если передать is_use_active_transaction=False,
                будет создана новая временная транзакция.
                Используется для отдельно взятых запросов,
                не связанных между собой. Такие методы в
                дочерних классах должны быть объявлены как public.

        Args:
            statement: SQL-запрос
            is_use_active_transaction: Флаг на использование
                активной транзакции

        Returns:
            Result: Результат выполнения запроса в БД
        """
        try:
            if is_use_active_transaction:
                return await self.__session.execute(statement)
            else:
                async with self.__session.begin():
                    result = await self.__session.execute(statement)
                    await self.__session.commit()
                    return result
        except Exception as e:
            await self.__session.rollback()
            raise e

    async def refresh(self, instance: SQLModel) -> None:
        """Выполняет обновление модели, обращаясь к БД.

        Args:
            instance: ORM модель, состояние которой обновляется из БД
        """
        try:
            await self.__session.refresh(instance)
        except Exception as e:
            await self.__session.rollback()
            raise e

    async def flush(self) -> None:
        """Сбрасывает изменения в базу данных без коммита."""
        try:
            await self.__session.flush()
        except Exception as e:
            await self.__session.rollback()
            raise e
