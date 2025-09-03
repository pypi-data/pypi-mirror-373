"""Модуль с родительской Pydantic схемой."""

from typing import Any, Final, Type, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar('T', bound='CustomBaseModel')

__all__ = ['CustomBaseModel']

REQUIRED_FIELD_ATTRIBUTES: Final[tuple[str, ...]] = (
    'alias',
    'description',
    'examples',
)


class CustomBaseModel(BaseModel):
    """Родительская кастомная Pydantic BaseModel схема.

    Данная схема имеет встроенные проверки и расширенную функциональность.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    @classmethod
    def __check_required_fields(cls) -> list[str]:
        """Проверяет обязательные поля для заполнения.

        Данные метод проверяет поля, обязательные для заполнения
        в Pydantic схеме и возвращает список ошибок.
        Если ошибки не найдены, будет возвращен пустой список.

        Args:
            cls

        Returns:
            errors: Список возникших ошибок
        """
        errors = []
        for field_name, field_info in cls.model_fields.items():
            for attr_name in REQUIRED_FIELD_ATTRIBUTES:
                attr_value = getattr(field_info, attr_name, None)
                if attr_value is None:
                    errors.append(f'{field_name}: отсутствует {attr_name}')
                elif attr_name == 'examples' and len(attr_value) != 1:
                    errors.append(
                        f'{field_name}: '
                        f'{attr_name} должен содержать ровно одно значение',
                    )
        return errors

    @classmethod
    def __pydantic_init_subclass__(
        cls,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Инициализация схемы после загрузки данных из атрибутов класса.

        Данный метод проверяет все поля схемы Pydantic на
        наличие alias, description и example.

        Args:
            cls
            kwargs: Дополнительные передаваемые именованные аргументы

        Raises:
            TypeError: Ошибка при валидации полей схемы
        """
        super().__pydantic_init_subclass__(**kwargs)

        errors = cls.__check_required_fields()
        if errors:
            fields_str = '\n'.join(errors)
            raise TypeError(
                f'Модель {cls.__name__} не прошла проверку документации: '
                f'\n{fields_str}',
            )

    @classmethod
    def generate_example(cls: Type[T]) -> T:
        """Автоматическая генерация примера на основе alias и example.

        Args:
            cls

        Returns:
            CustomBaseModel
        """
        example = {}

        for field_name, field_info in cls.model_fields.items():
            if field_info.examples is not None:
                key = field_info.alias or field_name
                example[key] = field_info.examples[0]

        return cls.model_validate(
            obj=example,
            from_attributes=False,
        )
