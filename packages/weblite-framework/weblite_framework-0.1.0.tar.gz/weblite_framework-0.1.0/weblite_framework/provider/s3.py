# TODO:
# В ручках FastAPI перехватывать ошибки валидации из провайдера
# и возвращать корректные HTTP-коды.

"""S3-провайдер на aioboto3: upload/get/delete/list."""

from typing import Any

import aioboto3
from botocore.config import Config

from weblite_framework.settings.s3 import S3Settings

__all__ = ['S3Provider']


class S3Provider:
    """Класс для работы с S3 через aioboto3.

    Note:
        Используйте провайдер только внутри блока ``async with``.

    Examples:
        async with S3Provider(settings) as s3p:
            await s3p.upload_file(filename="a.txt", data=b"...")
            data: bytes = await s3p.get_file(filename="a.txt")
    """

    def __init__(self, settings: S3Settings) -> None:
        """Создаёт провайдер с заданными настройками.

        Args:
            settings : S3Settings
        """
        self.settings = settings
        self._session = aioboto3.Session()

        self._config = Config(
            region_name=settings.region,
            signature_version=settings.signature_version,
            s3={
                'addressing_style': (
                    'path' if settings.path_style else 'virtual'
                ),
            },
            retries={
                'max_attempts': settings.max_attempts,
                'mode': 'standard',
            },
            connect_timeout=settings.connect_timeout,
            read_timeout=settings.read_timeout,
        )

        self._client_kwargs = {
            'endpoint_url': settings.endpoint_url,
            'aws_access_key_id': settings.access_key,
            'aws_secret_access_key': settings.secret_key,
            'config': self._config,
        }

        self._client_cm: Any = None
        self._client: Any = None

    async def __aenter__(self) -> 'S3Provider':
        """Открывает S3-клиент и возвращает провайдер.

        Returns:
            S3Provider: Экземпляр провайдера с открытым S3-клиентом.
        """
        self._client_cm = self._session.client(
            service_name='s3',
            **self._client_kwargs,
        )
        self._client = await self._client_cm.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        """Закрывает соединение с S3.

        Args:
            exc_type: Тип исключения, если оно возникло.
            exc: Экземпляр исключения, если он был.
            tb: Трейсбек исключения.

        Returns:
            None: Исключения не подавляются.
        """
        try:
            if self._client_cm is not None:
                await self._client_cm.__aexit__(
                    exc_type=exc_type,
                    exc_value=exc,
                    traceback=tb,
                )
        finally:
            self._client = None
            self._client_cm = None

    @classmethod
    def __validate_filename(cls, filename: str) -> None:  # noqa: ANN102
        """Проверяет, что имя файла непустое.

        Args:
            filename: Имя файла.

        Raises:
            ValueError: Если имя файла пустое.
        """
        if not filename:
            raise ValueError('filename is required')

    def _ensure_client(self) -> Any:  # noqa: ANN401
        """Возвращает активный S3-клиент или бросает исключение.

        Raises:
            RuntimeError: Если провайдер используется вне `async with`.
        """
        if self._client is None:
            raise RuntimeError(
                'S3Provider нужно использовать внутри'
                ' "async with S3Provider(...)"',
            )
        return self._client

    async def upload_file(self, filename: str, data: bytes) -> None:
        """Загружает байты в S3 под именем `filename`.

        Args:
            filename (str): Имя файла для сохранения в S3.
            data: Данные для загрузки.

        Raises:
            ValueError: Если имя файла или данные не указаны.
        """
        self.__validate_filename(filename=filename)
        if data is None:
            raise ValueError('data is required')

        s3 = self._ensure_client()
        await s3.put_object(
            Bucket=self.settings.bucket,
            Key=filename,
            Body=data,
        )

    async def get_file(self, filename: str) -> bytes:
        """Читает содержимое объекта и возвращает его как bytes.

        Args:
            filename: Имя файла в S3.

        Returns:
            bytes: Содержимое файла.

        Raises:
            ValueError: Если имя файла пустое.
        """
        self.__validate_filename(filename=filename)

        s3 = self._ensure_client()
        resp = await s3.get_object(
            Bucket=self.settings.bucket,
            Key=filename,
        )
        async with resp['Body'] as stream:
            content: bytes = await stream.read()
        return content

    async def delete_file(self, filename: str) -> None:
        """Удаляет объект из S3 (идемпотентно).

        Args:
            filename: Имя файла для удаления.

        Raises:
            ValueError: Если имя файла пустое.
        """
        self.__validate_filename(filename=filename)

        s3 = self._ensure_client()
        await s3.delete_object(
            Bucket=self.settings.bucket,
            Key=filename,
        )

    async def get_files_list(self, prefix: str = '') -> list[str]:
        """Возвращает список ключей, начинающихся с указанного префикса.

        Args:
            prefix: Префикс ключей. По умолчанию пустая строка.

        Returns:
            list: Список имён файлов (ключей).
        """
        keys: list[str] = []

        s3 = self._ensure_client()
        paginator = s3.get_paginator(operation_name='list_objects_v2')
        async for page in paginator.paginate(
            Bucket=self.settings.bucket,
            Prefix=prefix,
        ):
            for obj in page.get('Contents') or []:
                keys.append(obj['Key'])

        return keys
