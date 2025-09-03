"""
Конфигурация поведения обработчиков для работы с настройками
"""
from enum import Enum
from typing import Union
from typing import Optional

from logging import Logger, getLogger


class ErrorHandling(Enum):
    """Перечисление методов обработки ошибок"""
    EXIT = 'exit'  # Остановить работу программы
    RAISE = 'raise'  # Вызывать исключение
    LOGGING = 'logging'  # Записать сообщение в logger
    PRINT = 'print'  # Вывести сообщение в консоль
    IGNORE = 'ignore'  # Не выполнять действий

    @classmethod
    def from_value(cls, value: Union[str, 'ErrorHandling']) -> 'ErrorHandling':
        """
        Преобразует строковое значение или экземпляр enum в элемент перечисления.
        Возвращает соответствующий элемент ErrorHandling.
        """
        if isinstance(value, ErrorHandling):
            return value
        try:
            return cls(value)
        except ValueError:
            valid_values = [e.value for e in cls]
            raise ValueError(f'Недопустимое значение: {value}'
                             f'Допустимые значения: {valid_values}') from None

    def __str__(self):
        return self.value


class _Config:
    def __init__(self):
        _msg_prefix = 'settings:'
        _err_msg_prefix = f'{_msg_prefix} Ошибка загрузки настроек! Параметр'
        # Параметры по умолчанию
        self._messages = {
            'log_value': f'{_msg_prefix} {"{}={}"}',
            'err_required': f'{_err_msg_prefix} {"{}"} должен быть задан!',
            'err_integer': f'{_err_msg_prefix} {"{}={}"}. Должен быть числом!',
            'err_float': f'{_err_msg_prefix} {"{}={}"}. Должен быть дробным числом (с разделителем точка: 0.0)!',
            'err_file': f'{_err_msg_prefix} {"{}={}"}. Не найден указанный файл!',
            'err_directory': f'{_err_msg_prefix} {"{}={}"}. Невозможно создать директорию! {"{}"}'
        }
        self._error_handling = ErrorHandling.RAISE
        self._logger = None
        self._do_value_logging = False
        self._env_generator_pattern = r'^(?:\s*(?:#.*)?\s*[\r\n]+)*\s*[A-Z0-9_-]+\s*=\s.*?param.*?\(.*?\).*$'

    @property
    def messages(self):
        return self._messages

    @property
    def error_handling(self):
        return self._error_handling

    @property
    def logger(self) -> Union[type[Logger], Logger]:
        return getLogger(self._logger)

    @property
    def do_value_logging(self):
        return self._do_value_logging

    @property
    def env_generator_pattern(self):
        return self._env_generator_pattern

    def configure(self, messages: Optional[dict] = None,
                  error_handling: Optional[Union[str, ErrorHandling]] = None, logger: Optional[str] = None,
                  do_value_logging: Optional[bool] = None, env_generator_pattern: Optional[str] = None):
        """Обновление параметров конфигурации"""
        if messages:
            if not isinstance(messages, dict):
                raise TypeError('messages должен быть словарем')
            self._messages.update(messages)

        if error_handling:
            self._error_handling = ErrorHandling.from_value(error_handling)

        if logger:
            self._logger = logger

        if do_value_logging:
            self._do_value_logging = do_value_logging

        if env_generator_pattern:
            self._env_generator_pattern = env_generator_pattern

    def reset(self):
        """Сброс настроек к значениям по умолчанию"""
        self.__init__()


# Экземпляр синглтона для глобального доступа
config = _Config()
