"""
Генерация .env файла по файлам настроек

Содержит функции для автоматического создания .env-файла
на основе анализа файлов настроек
"""
from os import path, walk
from pathlib import Path
from re import MULTILINE
from re import compile

from .config import config


def _get_settings_values(settings_file, exclude_params: tuple[str] = None) -> list[str]:
    """
    Извлекает параметры переменных окружения из файла настроек.

    Анализирует Python-файл настроек, находит все объявления переменных,
    соответствующие заданному шаблону и формирует строки для .env-файла.

    1. Использует регулярное выражение из *config.env_generator_pattern*
    2. Находит все совпадения в файле настроек
    3. Для каждого совпадения:
        - Разделяет текст на последний перенос строки
        - Извлекает имя переменной (часть до '=')
        - Исключает переменные входящие в exclude_params
        - Форматирует результат

    :`example:
    >>> пример результата\n
    *# Database host*\n
    *DB_HOST=*\n
    *# API key*\n
    *API_KEY=*\n

    :param settings_file: str: Наименование файла настроек (например, 'settings.py')
    :param exclude_params: tuple[str], optional: Кортеж имен параметров, которые следует исключить из результата
    :return: list[str]: Список строк
    """
    param_pattern = compile(config.env_generator_pattern, MULTILINE)

    result = []
    with open(settings_file, mode='r', encoding='utf-8') as py_file:
        file_content = py_file.read()

        matches = param_pattern.findall(file_content)

        for match in matches:
            last_n = match.rfind('\n')
            first_row = match[:last_n] if last_n >= 0 else ''
            last_row = match[last_n:] if last_n >= 0 else match
            param_name = last_row[:last_row.find('=') - 1].strip()
            if not exclude_params or param_name not in exclude_params:
                result.append((first_row + '\n' + param_name + '=' + '\n').lstrip())

    return result


def generate_env_file(new_env_filename: str, settings_filename: str = 'settings.py', modules_path: str = '.',
                      sub_modules_path: str = None, include_sub_modules: tuple[str] = None,
                      exclude_params: tuple[str] = None):
    """
    Генерирует .env-файл на основе файлов настроек в указанных директориях.

    Рекурсивно ищет файлы настроек в заданной структуре директорий,
    извлекает параметры переменных окружения и объединяет их в один файл.

    1. Рекурсивно обходит директории, начиная с modules_path
    2. Для каждого найденного файла настроек:
        - Проверяет, находится ли файл в разрешенной поддиректории (если заданы sub_modules_path/include_sub_modules)
        - Извлекает параметры
    3. Объединяет все найденные параметры\n
    4. Записывает результат в указанный .env-файл\n

    :examples:
    >>> пример вызова\n
    generate_env_file(
                new_env_filename='.env.template',
                settings_filename='app_settings.py',
                modules_path='src',
                sub_modules_path='modules',
                include_sub_modules=('auth', 'payment'),
                exclude_params=('SECRET_KEY',))

    :param new_env_filename: str: Имя генерируемого .env-файла (например, '.env.template')
    :param settings_filename: str, default='settings.py': Имя файла настроек для поиска
    :param modules_path: str, default='.': Корневая директория для поиска
    :param sub_modules_path: str, optional: Специфическая поддиректория для поиска модулей (например, 'modules')
    :param include_sub_modules, optional: Кортеж имен подмодулей для включения в поиск (например, ('auth', 'payment'))
    :param exclude_params, optional: Кортеж имен параметров для исключения из результата
    """
    def get_settings(dirname):
        result_values = []
        for root, _, files in walk(dirname, topdown=True):
            for name in [n for n in files if n == settings_filename]:
                _dirs = [x for x in str(root).split(path.sep) if x not in str(dirname).split(path.sep)]
                if sub_modules_path and include_sub_modules:
                    if len(_dirs) > 1 and _dirs[0] == sub_modules_path and not _dirs[1] in include_sub_modules:
                        continue
                elif include_sub_modules:
                    if len(_dirs) > 0 and not _dirs[0] in include_sub_modules:
                        continue
                result_values.extend(_get_settings_values(path.join(path.curdir, root, name), exclude_params))
        return result_values

    settings_values = get_settings(Path(modules_path))

    with open(new_env_filename, mode='w', encoding='utf-8') as env_file:
        for index, value in enumerate(settings_values):
            is_last_iteration = (index == len(settings_values) - 1)
            new_line = '\n'
            env_file.write(f"{value}{new_line if not is_last_iteration else ''}")
