import json
import re
import shutil
from itertools import islice
from pathlib import Path
from typing import Any, Final, Optional

import tiktoken

from .. import ColumnStrings, logerr, pretty_print
from ..configs.system import AsisTobe
from ..logger import log, logsuc
from ..reader_controller.exceptions import EmptyIdfyNotNullDictException
from ..reader_controller.types import IdfyGoods, IndexedIdfyGoods

print = log


class Tools:
    # Глобальный паттерн всех Unicode-пробелов (включая zero-width)
    _UNICODE_SPACES_RE = re.compile(
        r"[\u0009\u000A\u000B\u000C\u000D\u0020\u0085\u00A0\u1680"
        r"\u180E\u2000-\u200A\u2028\u2029\u202F\u205F\u3000\u200B\u2060\uFEFF]+"
    )

    @staticmethod
    def semicolonizer(string: str) -> str:
        string = string.replace(",", ", ")
        return string.replace("  ", " ")

    @staticmethod
    def extract_digits_list(s: str) -> list[str]:
        """
        Извлекает все числа (последовательности цифр) из строки.
        Возвращает список строк (не int, чтобы сохранить ведущие нули, если нужно).
        """
        return re.findall(r'\d+', s)

    @staticmethod
    def get_dry_brand(brand: str):
        allowed_chars = (
            'abcdefghijklmnopqrstuvwxyz'
            'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
            '0123456789&!-\''
        )
        return Tools.get_dry_string(brand, allowed_chars)

    @staticmethod
    def get_dry_string(input_string: str, allows: Optional[str] = None) -> str:
        """Высушивает строку, оставляя только буквы и цифры в lower-формате"""
        allowed_chars = (
            'abcdefghijklmnopqrstuvwxyz'
            'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
            '0123456789'
        )
        if allows is not None:
            allowed_chars = allows
        return ''.join(
            c for c in input_string.lower()
            if c in allowed_chars
        )

    @staticmethod
    def get_dry_string_list(input_string: str) -> list[str]:
        """Высушивает строку, оставляя только буквы и цифры в lower-формате в списке"""
        result: list[str] = []
        for word in input_string.split():
            result.append(Tools.get_dry_string(word))
        return result

    @staticmethod
    def get_all_fields(fields: list[str]) -> list[str]:
        """
        Расширяет список полей, добавляя суффиксы _asis и _tobe
        :param fields: список базовых полей
        :return: список с расширенными названиями
        """
        if not fields:
            raise ValueError("Список полей не может быть пустым")
        extended_fields = []
        for field in fields:
            extended_fields.append(f"{field}_asis")
            extended_fields.append(f"{field}_tobe")
        return extended_fields

    @staticmethod
    def get_relay(fields: list[str]) -> dict[str, str]:
        """Генерирует словарь с asis->tobe связкой из fields"""
        if not len(fields):
            raise IndexError("СПИСОК ПОЛЕЙ ДЛЯ ФИНАЛИЗАЦИИ НЕ МОЖЕТ БЫТЬ ПУСТЫМ")
        result: dict[str, str] = {}
        for field in fields:
            result[f"{field}_asis"] = f"{field}_tobe"
        return result

    @staticmethod
    def normalize_spaces(text: str) -> str:
        """
        Заменяет все типы пробельных символов Unicode на обычный пробел.
        """
        return Tools._UNICODE_SPACES_RE.sub(' ', text)

    @staticmethod
    def string_stripper(text: str) -> str:
        """
        - Удаляет ведущие/конечные пробелы
        - Заменяет все невидимые и странные пробелы на обычные
        - Схлопывает многократные пробелы в один
        """
        if not text:
            return ""
        text = Tools.normalize_spaces(text)
        text = text.strip()
        text = re.sub(r' {2,}', ' ', text)
        return text.strip()

    @staticmethod
    def clean_field(string: str) -> str:
        """Комплексная очистка"""
        string = Tools.string_stripper(string)
        string = Tools.trim_spec(string)
        return Tools.string_stripper(string)

    @staticmethod
    def polysplit(
        text: str,
        separators: Optional[list[str]] = None,
        no_empty: bool = False
    ) -> list[str]:
        """
        Разбивает строку по нескольким разделителям с возможностью удаления пустых строк.

        :param text: Исходная строка
        :param separators: Список разделителей
        :param no_empty: Если True (по умолчанию), удаляет пустые строки из результата
        :return: Список частей строки
        """
        if separators is None:
            separators = ["/", "\\", "|", "-", "+", " "]
        if not text:
            return []

        result = [text]

        for sep in separators:
            temp = []
            for part in result:
                temp.extend(part.split(sep))
            result = temp

        if no_empty:
            return [part for part in result if part]  # Фильтруем пустые строки
        return result  # Возвращаем как есть

    @staticmethod
    def get_words(string: str, use_clean_strip: bool = False) -> list[str]:
        """
        Получает из строки список слов по пробелу

        use_clean_strip - если задан, возьмёт множество других символов
        """
        string = Tools.normalize_spaces(string)
        string_list = string.split(" ")
        if use_clean_strip:
            # УБРАЛИ "!"
            return [word.strip('.,?:;"\'()-_/|*<>#%^&+=~ ') for word in string_list]
        return string_list

    @staticmethod
    def get_lower_words(words: list[str]) -> list[str]:
        """Берет список строк, делает их lower"""
        return [word.lower() for word in words]

    @staticmethod
    def get_most_longer_word_of_list(words_list):
        """
        Метод, который выбирает самое длинное название из списка.
        Если таких несколько - сортируем по алфавиту.

        :param words_list: Список слов
        :return: Самое длинное слово или первое из самых длинных, если их несколько
        """
        if not words_list:
            return None

        # Находим максимальную длину слова
        max_length = max(len(word) for word in words_list)

        # Собираем список всех слов максимальной длины
        longest_words = [word for word in words_list if len(word) == max_length]

        # Если одно слово, возвращаем его
        if len(longest_words) == 1:
            return longest_words[0]
        else:
            # Если несколько слов одной длины, сортируем по алфавиту и берем первое
            return sorted(longest_words)[0]

    @staticmethod
    def get_first_of_dict(dictionary: dict, key: bool = False) -> Optional[Any]:
        """Возвращает первый элемент ключа"""
        priority_key = next(iter(dictionary), None)
        if priority_key is None:
            return None
        return priority_key if key else dictionary[priority_key]

    @staticmethod
    def trim_spec(word: str, is_brand: bool = False) -> str:
        """
        Очищает строку от спецсимволов по краям.
        При is_brand=True:
          - Если строка — одно слово в скобках (например, "(Samsung)") → удаляет скобки.
          - Если слов несколько или скобки не по краям → оставляет как есть.

        Args:
            word (str): Исходная строка.
            is_brand (bool): Флаг, указывающий, что строка — бренд (требует особой обработки скобок).

        Returns:
            str: Очищенная строка.
        """
        if not word or not isinstance(word, str):
            return word

        word = word.strip()

        # Базовая очистка краёв: удаляем всё, кроме букв, цифр, дефиса, апострофа, скобок
        cleaned = re.sub(r'^[^\w\(\)\[\]\{\}\'-]+|[^\w\(\)\[\]\{\}\'-]+$', '', word)

        if not is_brand:
            return cleaned

        # === Логика для брендов ===

        # Если строка уже не в скобках — просто возвращаем
        if not (cleaned.startswith('(') and cleaned.endswith(')')):
            return cleaned

        # Проверяем, является ли содержимое "одним словом"
        inner = cleaned[1:-1].strip()  # убираем скобки и пробелы

        # Разбиваем на "слова" (последовательности букв/цифр)
        inner_words = re.findall(r'[\w]+', inner, re.UNICODE)

        # Если внутри 2+ слов — оставляем скобки
        if len(inner_words) >= 2:
            return cleaned

        # Если внутри 1 слово — удаляем внешние скобки
        if len(inner_words) == 1:
            return inner

        # Если внутри 0 слов (пусто или только символы) — возвращаем без скобок
        return inner  # может быть пустым

    @staticmethod
    def get_most_popular(variants_list: list[str], variants_registry: dict[str, int]) -> list[str]:
        """
        Выбирает все самые популярные варианты из variants_list
        Популярность содержится в variants_registry в виде словаря: {
            "бренд1": <количество_повторений_в_документе>,
            "бренд2": <количество_повторений_в_документе>,
        }
        Если у одного из вариантов нет повторений в variants_registry, то приравнять популярность к 0
        Если у нескольких вариантов одинаковая максимальная популярность, вернуть все такие варианты
        :param variants_list: список брендов для анализа
        :param variants_registry: словарь популярности брендов
        :return: список самых популярных брендов
        """
        # Сначала найдем максимальную частоту
        max_frequency = -1
        for brand in variants_list:
            frequency = variants_registry.get(Tools.get_dry_brand(brand), 0)
            if frequency > max_frequency:
                max_frequency = frequency

        # print(f"{max_frequency=}")

        # Теперь соберем все бренды с максимальной частотой
        popular_brands = []
        for brand in variants_list:
            frequency = variants_registry.get(Tools.get_dry_brand(brand), 0)
            if frequency == max_frequency:
                popular_brands.append(brand)

        return popular_brands

    @staticmethod
    def get_threads_data_parts_by_dict(
        idfy_not_null_dict: IdfyGoods,
        threads: int,
        is_use_small_chunks: bool = False,
        small_chunk_size: int = 10
    ) -> IndexedIdfyGoods:
        """
        Разбивает список на N равных частей и возвращает словарь,
        где ключи — ID потоков (начиная с 1), а значения — части списка.

        :return: Словарь вида {1: [...], 2: [...], ...}
        :raises ValueError: Если n <= 0
        :raises EmptySourceNameListException: Если исходный список пуст
        """
        log("Генерирую словарь с данными для потоков")
        source_dict: dict = idfy_not_null_dict

        if threads <= 0:
            raise ValueError("Количество частей должно быть положительным числом")

        if not source_dict:
            raise EmptyIdfyNotNullDictException("Нет данных")

        if not is_use_small_chunks:
            items = list(source_dict.items())
        else:
            items = list(source_dict.items())[:small_chunk_size]
        total_items: Final[int] = len(items)
        base_size, remainder = divmod(total_items, threads)

        result: IndexedIdfyGoods = {}
        index = 0

        for thread_id in range(1, threads + 1):
            part_size = base_size + (1 if thread_id <= remainder else 0)
            chunk = dict(islice(items, index, index + part_size))
            result[thread_id] = chunk
            index += part_size
        logsuc(f"Генерация словаря завершена. ~ записей в потоке: {base_size}")
        return result

    @staticmethod
    def get_dict_filtered(
        data: dict[Any, dict[str, Any]],
        include_by_rules: list[dict[str, Any]],
        strict: bool = False
    ) -> dict[Any, dict[str, Any]]:
        """
        Фильтрует словарь словарей по правилам.
        Поддерживает:
          - Несколько условий на одно поле → объединяются как OR
          - Условия на разные поля → объединяются как AND

        Пример:
            rules = [
                {'status': 'active'},
                {'status': 'pending'},
                {'category': 'premium'}
            ]
            → (status == 'active' OR status == 'pending') AND category == 'premium'

        :param data: словарь, где значения — словари
        :param include_by_rules: список фильтров (условия на поля)
        :param strict: если True, отсутствие ключа = ошибка; иначе — несовпадение
        :return: отфильтрованный словарь
        """
        if not isinstance(data, dict):
            raise ValueError("data должен быть словарём")
        if not isinstance(include_by_rules, list):
            raise ValueError("include_by_rules должен быть списком")

        # Если нет правил — возвращаем все подходящие элементы
        if not include_by_rules:
            return {k: v for k, v in data.items() if isinstance(v, dict)}

        # Группируем правила по ключам: field -> set(expected_values)
        conditions: dict[str, set[Any]] = {}
        for rule in include_by_rules:
            if not isinstance(rule, dict):
                continue
            for key, value in rule.items():
                if key not in conditions:
                    conditions[key] = set()
                conditions[key].add(value)

        result = {}

        for key, item in data.items():
            if not isinstance(item, dict):
                continue

            match = True
            for field, allowed_values in conditions.items():
                if field not in item:
                    # Ключ отсутствует
                    if strict:
                        match = False
                    else:
                        match = False  # значение не совпадает (ключа нет)
                    break

                actual_value = item[field]
                if actual_value not in allowed_values:
                    match = False
                    break  # не прошло условие по полю

            if match:
                result[key] = item

        return result

    @staticmethod
    def skip_n_rows(data_dict: IdfyGoods, n_of_skip_rows: int) -> IdfyGoods:
        """Пропуск указанного количества чанков"""
        return dict(list(data_dict.items())[n_of_skip_rows:])

    @staticmethod
    def no_repeats_of_list(lst: list) -> list:
        """
        Удаляет дубликаты из списка, сохраняя порядок элементов.

        :param lst: Исходный список
        :return: Список без дубликатов
        """
        seen = set()
        filtered = [x for x in lst if not (x in seen or seen.add(x))]
        return [x for x in filtered if x is not None]

    @staticmethod
    def find_original_substring(source: str, word: str) -> Optional[str]:
        """
        Находит подстроку в исходной строке, соответствующую образцу (с учетом регистра и оригинального написания).

        :param source: Исходная строка для поиска
        :param word: Подстрока-образец (может быть в нижнем регистре)
        :return: Найденная подстрока в оригинальном виде или None
        """
        # Экранируем спецсимволы в образце и разбиваем на слова
        pattern_parts = [re.escape(part) for part in word.split()]

        # Создаем регулярное выражение:
        # - Ищем слова образца в любом порядке
        # - Между словами могут быть другие символы
        # - Регистронезависимый поиск
        regex_pattern = r'(?i)(?=.*?\b{}\b)'.format(r'\b)(?=.*?\b'.join(pattern_parts))
        regex_pattern += r'([^\n]*?{}[^\n]*)'.format(r'[^\n]*?'.join(pattern_parts))

        match = re.search(regex_pattern, source)
        if not match:
            return None

        # Находим точную подстроку, содержащую все слова образца
        matched_text = match.group(1)

        # Уточняем границы найденного текста
        words = word.lower().split()
        start_pos = 0
        end_pos = len(matched_text)

        # Находим первое вхождение первого слова
        first_word_pattern = re.compile(re.escape(words[0]), re.IGNORECASE)
        first_match = first_word_pattern.search(matched_text)
        if first_match:
            start_pos = first_match.start()

        # Находим последнее вхождение последнего слова
        last_word_pattern = re.compile(re.escape(words[-1]), re.IGNORECASE)
        last_matches = list(last_word_pattern.finditer(matched_text))
        if last_matches:
            end_pos = last_matches[-1].end()

        # Возвращаем подстроку с оригинальным написанием
        return matched_text[start_pos:end_pos].strip(" ,.-")

    @staticmethod
    def get_normal_word_from_source_by_castrat_word(
        source: str,
        word: str
    ):
        """
        Возвращает нормальное слово из источника по индексу, найденному по кастрату в источнике
        :param source: example = "Стиральная машина AEG L7WBE68SI White"
        :param word: example = "white"
        :return: example = "White"
        """
        # debug: bool = False
        _debug: bool = True

        if _debug: logerr("<get_normal_word_from_source_by_castrat_word>")
        if _debug: print(f"{source=}")
        if _debug: print(f"{word=}")
        source_list: list[str] = source.split()
        if _debug: pretty_print(source_list, title=f"source_list", m2d=False)
        source_lower: str = source.lower()
        if _debug: print(f"{source_lower=}")

        source_lower_list: list[str] = source_lower.split()
        source_lower_list = [Tools.trim_spec(color) for color in source_lower_list]
        if _debug: pretty_print(source_lower_list, title=f"source_lower_list", m2d=False)

        index_main: int = 0
        for index, word_part in enumerate(source_lower_list):
            if word not in word_part:
                continue
            else:
                index_main = index
                break
        if _debug: print(f"{index_main=}")

        if not index_main:
            return None
        return source_list[index_main]

    @staticmethod
    def completely_nulled(fields: list[str], data_dict: dict) -> bool:
        """
        Возвращает True, если все указанные поля в data_dict равны строке "0".
        :param fields: список ключей для проверки
        :param data_dict: словарь с данными
        :return: True, если все указанные поля равны "0", иначе False
        """
        return all(data_dict.get(field) == "0" for field in fields)

    @staticmethod
    def get_stripped_words(words: list[str], chars: int = 3) -> list[str]:
        """
        Получает список слов words и сколько нужно оставить в начале слова chars,
        возвращается список обрезанных слов
        :param words:
        :param chars:
        :return:
        """
        if chars < 0:
            raise ValueError("Количество символов не может быть отрицательным")
        return [word[:chars] for word in words]

    @classmethod
    def get_stripped_data_by_fields(cls, data: dict, required_fields: list[str]):
        """
        Получает словарь с полями. Пробегается по полю из required_field. Чистит от пробелов
        :param data:
        :param required_fields:
        :return:
        """
        result: dict[str, str] = {}
        for field, value in data.items():
            if field not in required_fields:
                result[field] = value
                continue
            result[field] = cls.string_stripper(data[field])

        return result

    @staticmethod
    def get_desymbolization_string(string: str, allowed_symbols: list):
        """Оставляем буквы-цифры и разрешенные символы"""
        # Экранируем спецсимволы для безопасного включения в регулярку
        escaped = ''.join(re.escape(sym) for sym in allowed_symbols)
        # Регулярка оставляет A-z, А-я, 0-9 и разрешённые символы
        allowed_pattern = fr"[^a-zA-Zа-яА-ЯёЁ0-9{escaped}]"
        return re.sub(allowed_pattern, " ", string)

    @staticmethod
    def ireplace(
        string: str,
        substr: str,
        value: str = ""
    ) -> str:
        """
        Удаляет все вхождения подстроки `substring` из строки `string` без учёта регистра.
        Например: string="HelloWorldWorld", substring="world" → "Hello"
        """
        pattern = re.compile(re.escape(substr), re.IGNORECASE)
        return pattern.sub(value, string)

    @staticmethod
    def get_sliced_after(string: str, phrase: str) -> str:
        """
        Метод ищет в строке string начало вхождения фразы phrase.
        Если находит — возвращает часть строки ДО фразы.
        Если не находит — возвращает исходную строку.

        Пример:
            string="abc", phrase="b" → return "a"

        :param string: Исходная строка
        :param phrase: Фраза, после которой нужно обрезать
        :return: Обрезанная строка
        """
        string_lower = string.lower()
        phrase_lower = phrase.lower()

        index = string_lower.find(phrase_lower)
        if index != -1:
            return string[:index]
        return string  # если phrase не найдено — вернуть оригинал без изменений

    @staticmethod
    def ifound(
        string: str, substring: str, is_all: bool = False
    ) -> bool | list[int]:
        """
        Выполняет регистронезависимый поиск подстроки `substring` в строке `string`.

        :param string: Строка, в которой происходит поиск
        :param substring: Подстрока, которую ищем
        :param is_all: Если True — возвращает список всех индексов вхождения;
                       Если False — возвращает True/False в зависимости от наличия вхождения
        :return: bool или list[int]
        """
        string_lower = string.lower()
        substring_lower = substring.lower()

        if not is_all:
            return substring_lower in string_lower

        # Поиск всех вхождений
        indices = []
        start = 0
        while True:
            index = string_lower.find(substring_lower, start)
            if index == -1:
                break
            indices.append(index)
            start = index + 1  # Продолжаем искать со следующего символа

        return indices

    @staticmethod
    def try_to_int(data: Optional) -> bool:
        try:
            int(data)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def get_all_files_from_dir(
        dir_path: Path,
        exts_list: list[str] | None = None,
        exclude_file_with_list: list[str] | None = None,
        sort_files: bool = True
    ) -> list[Path]:
        """
        Собирает и сортирует файлы из указанной директории

        :param dir_path: путь до папки
        :param exts_list: разрешенные расширения (без точки, например ['jpg', 'png'])
        :param exclude_file_with_list: исключить файлы, содержащие подстроки в имени
        :param sort_files: сортировать ли файлы по имени (по умолчанию True)
        :return: отсортированный список Path объектов файлов
        """
        exts_list = exts_list or ['*']
        exclude_file_with_list = exclude_file_with_list or ['~']

        if not dir_path.is_dir():
            raise NotADirectoryError(f"Путь не является директорией: {dir_path}")

        found_files: list[Path] = []

        for ext in exts_list:
            pattern = f"*.{ext}" if ext != '*' else "*"
            found_files.extend(
                file_path
                for file_path in dir_path.glob(pattern)
                if file_path.is_file()
                and not any(
                    exclude_str in file_path.name
                    for exclude_str in exclude_file_with_list
                )
            )

        # Удаляем дубликаты и сортируем при необходимости
        unique_files = list(set(found_files))
        return sorted(unique_files, key=lambda x: x.name) if sort_files else unique_files

    @staticmethod
    def sort_dict_by_keys(dictionary: dict, reverse=False):
        """
        Сортирует словарь по ключам.

        :param dictionary: Словарь для сортировки.
        :param reverse: Флаг для выбора направления сортировки (False - прямой порядок, True - обратный).
        :return: Отсортированный словарь.
        """
        sorted_items = sorted(dictionary.items(), key=lambda x: x[0], reverse=reverse)
        return dict(sorted_items)

    @staticmethod
    def sequential_combinations(
        words_list: list[str],
        use_dry: bool = True,
        get_string: bool = True,
        is_brand: bool = False
    ):
        """
        Составляет последовательные комбинации слов из списка и сортирует их по убыванию длины.
        Если get_string=True, возвращает строки вместо списков.

        :param is_brand:
        :param use_dry:
        :param words_list: Входной список слов
        :param get_string: Флаг, определяющий формат вывода (списки или строки)
        :return: Список последовательных комбинаций, отсортированных по убыванию длины
        """
        result = []
        length = len(words_list)

        # Генерация последовательных комбинаций
        for start_idx in range(length):
            for end_idx in range(start_idx + 1, length + 1):
                combo = words_list[start_idx:end_idx]
                result.append(combo)

        # Сортировка по убыванию длины
        result.sort(key=len, reverse=True)

        if get_string:
            result = [' '.join(combo) for combo in result]

        if use_dry:
            if is_brand:
                result = [Tools.get_dry_brand(combo) for combo in result]
            else:
                result = [Tools.get_dry_string(combo) for combo in result]

        return result

    @staticmethod
    def get_no_entity_no_brand_source_name(
        data_item: dict,
        no_entity: bool = True,
        no_brand: bool = True
    ) -> str:
        source_name: str = data_item.get(ColumnStrings.DATA_SOURCE_NAME)
        if no_entity:
            source_name = source_name.replace(data_item.get(ColumnStrings.DATA_ENTITY_ASIS), "")
        if no_brand:
            source_name = source_name.replace(data_item.get(ColumnStrings.DATA_BRAND_ASIS), "")
        return source_name.strip()

    @staticmethod
    def find_full_match(source_name: str, pattern: str) -> str:
        """
        Метод находит точное полное вхождение подстроки в исходной строке.
        Окончанием считается пробел, запятая, перенос строки или конец строки.

        :param source_name: Исходная строка
        :param pattern: Часть строки, по которой нужно искать
        :return: Полное вхождение искомой строки
        """
        pos = source_name.find(pattern)
        if pos == -1:
            return ""

        # Начинаем движение вправо от места нахождения паттерна
        end_pos = pos + len(pattern)
        while end_pos < len(source_name) and source_name[end_pos].isalnum():  # Пока буква или цифра
            end_pos += 1

        # Вырезаем найденное вхождение
        full_match = source_name[pos:end_pos].strip(", \n\r\t")
        return full_match

    @staticmethod
    def get_smallest(*lists):
        """Выбирает наименьшее ненулевое число из переданных списков.
        Если все значения нулевые или списки пусты, возвращает None."""
        # # Собираем все ненулевые элементы из всех списков
        # non_zero_values = []
        # for lst in lists:
        #     if lst:  # Проверяем, что список не пустой
        #         for value in lst:
        #             if value != 0:  # Игнорируем нули
        #                 non_zero_values.append(value)
        non_zero_values = [v for lst in lists if lst for v in lst if v != 0]
        return min(non_zero_values) if non_zero_values else None

    @staticmethod
    def get_chunks_data_by_dict(
        idfy_not_null_dict: dict,
        chunk_size: int,
        is_use_small_chunks: bool = False,
        small_chunk_size: int = 10
    ) -> list[dict[Any, Any]]:
        """Делит СЛОВАРЬ с данными на чанки с данными"""
        if chunk_size <= 0:
            raise ValueError("Размер чанка должен быть положительным")

        if is_use_small_chunks:
            chunk_size = small_chunk_size

        items = list(idfy_not_null_dict.items())
        return [
            dict(items[i:i + chunk_size])
            for i in range(0, len(items), chunk_size)
        ]

    @staticmethod
    def split_into_chunks(big_list, chunk_size=100):
        """
        Разделение большого СПИСКА на меньшие кусочки фиксированного размера.

        :param big_list: Основной список для деления.
        :param chunk_size: Размер каждого фрагмента (по умолчанию 100).
        :return: Список фрагментов.
        """
        return [big_list[i:i + chunk_size] for i in range(0, len(big_list), chunk_size)]

    @staticmethod
    def filter_list(a: list, b: list) -> list:
        """
        Оставляет в списке A только элементы, которых нет в списке B

        :param a: Основной список (будет изменен)
        :param b: Список элементов для исключения
        :return: Отфильтрованный список A
        """
        # Преобразуем в множества для быстрого поиска
        set_b = set(b)
        # Оставляем только элементы не из B
        return [x for x in a if x not in set_b]

    @staticmethod
    def get_field_structure(field: str):
        if AsisTobe.ASIS in field:
            return {
                "name": field.replace(f"_{AsisTobe.ASIS}", ""),
                "mod": AsisTobe.ASIS
            }
        elif AsisTobe.TOBE in field:
            return {
                "name": field.replace(f"_{AsisTobe.TOBE}", ""),
                "mod": AsisTobe.TOBE
            }
        else:
            return {
                "name": field,
                "mod": None
            }

    @staticmethod
    def num_tokens_from_messages(messages, model="gpt-4o-mini"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using o200k_base encoding.")
            encoding = tiktoken.get_encoding("o200k_base")
        if model in {
            "gpt-3.5-turbo-0125",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            "gpt-4o-mini-2024-07-18",
            "gpt-4o-2024-08-06"
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif "gpt-3.5-turbo" in model:
            print(
                "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0125."
            )
            return Tools.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0125")
        elif "gpt-4o-mini" in model:
            print(
                "Warning: gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-mini-2024-07-18."
            )
            return Tools.num_tokens_from_messages(messages, model="gpt-4o-mini-2024-07-18")
        elif "gpt-4o" in model:
            print(
                "Warning: gpt-4o and gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-2024-08-06."
            )
            return Tools.num_tokens_from_messages(messages, model="gpt-4o-2024-08-06")
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return Tools.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    @staticmethod
    def remove_duplicate_words(text: str) -> str:
        """
        Удаляет повторяющиеся слова в строке, сохраняя порядок и регистр первого вхождения.

        :param text: Исходная строка
        :return: Строка без повторяющихся слов
        """
        seen_words = set()
        result = []

        for word in text.split():
            # Приводим к нижнему регистру только для проверки дубликатов
            lower_word = word.lower()

            if lower_word not in seen_words:
                seen_words.add(lower_word)
                result.append(word)  # Сохраняем оригинальное слово с регистром

        return ' '.join(result)

    @staticmethod
    def clear_directory_contents(path: Path, with_dir: bool = False) -> None:
        """
        Полностью очищает содержимое указанной папки (включая подпапки и файлы).
        Не удаляет саму папку, только её содержимое.

        Args:
            path: Путь к папке, которую нужно очистить (Path объект)

        Raises:
            ValueError: Если переданный путь не является директорией
            OSError: При ошибках удаления файлов
            :param path:
            :param with_dir: вместе с папкой
        """
        if not path.is_dir():
            raise ValueError(f"Путь {path} не является директорией")

        # Удаляем все содержимое рекурсивно
        for item in path.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()  # Удаляем файлы и симлинки
                elif item.is_dir():
                    shutil.rmtree(item)  # Рекурсивно удаляем поддиректории
            except Exception as e:
                raise OSError(f"Ошибка при удалении {item}: {e}")

    @staticmethod
    def parse_filename(filename):
        """
        Парсит имя файла формата "2417_Лестницы_и_стремянки_20250529_на_разметку.xlsx"
        и возвращает категорию и название категории.

        Args:
            filename (str): Имя файла для парсинга

        Returns:
            tuple: (категория, название_категории)
        """
        # Удаляем расширение файла
        name_without_ext = filename.split('.')[0]

        # Разбиваем по символу подчеркивания
        parts = name_without_ext.split('_')

        # Категория - первая часть
        # parts[0] = "123dwd"
        category = parts[0]
        if not category.isdigit():
            raise ValueError("Категория должна состоять из цифр")

        category = int(category)

        # Название категории - все части между категорией и датой
        # Ищем индекс первой части, содержащей дату (формат YYYYMMDD)
        date_pattern = re.compile(r'^\d{8}$')
        date_index = None

        for i, part in enumerate(parts):
            if date_pattern.match(part):
                date_index = i
                break

        if date_index is None:
            # Если дата не найдена, берем все части после категории
            name_parts = parts[1:]
        else:
            name_parts = parts[1:date_index]

        # Собираем название категории, заменяя подчеркивания на пробелы
        category_name = ' '.join(name_parts)

        return category, category_name

    @staticmethod
    def idfy_by_field(
        data: dict | list,
        key_field: str,
        save_repeats: bool = True,
        repeat_char: str = "_"
    ):
        """
        Метод проводит словаризацию словаря/списка по данным из поля
        :param repeat_char: символ, который ставится после идентификатора поля, если такой элемент уже есть
        :param save_repeats: сохранять повторы?
        :param data:
        :param key_field: поле, из которого будет браться ключ для словаря
        :return:
        """
        if not isinstance(data, list):
            raise TypeError("Данные должны быть списком")

        result: dict[Any, Any] = {}
        item: dict
        for item in data:
            if not isinstance(item, dict):
                raise TypeError("Элемент должен быть словарём")
            if key_field not in item:
                raise AttributeError(f"Поле «{key_field}» отсутствует в элементе")

            key_value: Optional[Any] = item.get(key_field)
            if not key_value:
                raise ValueError(f"В качестве ключа должен быть хэшируемое значение: {key_value}")

            while True:
                if key_value not in result:
                    result[key_value] = item
                    break
                if save_repeats:
                    key_value = f"{repeat_char}{key_value}"
        return result

    @staticmethod
    def is_valid_json(s):
        """Проверка строки на валидное json-содержимое"""
        try:
            json.loads(s)
            return True
        except (json.JSONDecodeError, TypeError, ValueError):
            return False

    @staticmethod
    def str2json(text: str) -> Optional[list | dict]:
        try:
            json_data = json.loads(text)
        except json.JSONDecodeError:
            return None
        return json_data

    @staticmethod
    def get_clean_words(words: list[str]) -> list[str]:
        """Берет список строк, делает их lower"""
        words_lower = [word.lower() for word in words]
        return [Tools.clean_field(word) for word in words_lower]

    @staticmethod
    def get_fields_pairs(fields: list[str]) -> dict[str, dict[str, str]]:
        if not len(fields):
            raise IndexError("Список полей для парирации не может быть пустым")
        result: dict[str, dict[str, str]] = {}
        field: str
        for field in fields:
            result[field] = {
                AsisTobe.ASIS: f"{field}_{AsisTobe.ASIS}",
                AsisTobe.TOBE: f"{field}_{AsisTobe.TOBE}",
            }
        return result

    @staticmethod
    def get_word_by_index(
        words_list: list[str],
        words_indexes: list[int],
        *,
        ignore_errors: bool = True,
        unique_only: bool = True
    ) -> list[str]:
        """
        Усовершенствованная версия с поддержкой уникальных слов без потери порядка.
        ...
        """
        if not words_list or not words_indexes:
            return []

        result = []
        seen_words = set()

        for i in words_indexes:
            if 0 <= i < len(words_list):
                word = words_list[i]
                if unique_only:
                    if word not in seen_words:
                        result.append(word)
                        seen_words.add(word)
                else:
                    result.append(word)
            elif not ignore_errors:
                raise IndexError(f"Индекс {i} выходит за пределы списка (длина: {len(words_list)})")

        return result
