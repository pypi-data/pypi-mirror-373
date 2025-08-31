"""ЯДРО"""

import warnings
from pathlib import Path
from typing import Optional

import pandas as pd
from deprecated import deprecated
from pandas import DataFrame, read_excel

from ..configs.column_strings import ColumnStrings
from ..configs.system import System
from ..logger.core import log, logerr, loginf, logsuc
from ..pretty_print.core import pretty_print
from ..reader_controller.exceptions import ContentLengthError, WrongSheetListError
from ..reader_controller.types import DFType, IdfyGoods, XLSGood

print = log


class ReaderController:
    """Контроллер для управления XLS(X) файлами"""

    def __init__(self, file_path, file_output, is_new: bool = False, skip_rows: int = 0):
        self._is_new: bool = is_new
        self._file_path: Path = file_path
        self.check_exists()
        self._file_output: Path = file_output
        self._skip_rows: int = skip_rows
        self._dataframe: list[dict] = []
        self._idfy_dataframe: dict = {}
        self._local_idfy_dataframe: dict = {}

        self.check_writable()

    def read_data(self, sheet_name: Optional[str] = None):
        """Чтение файла"""
        self._dataframe = self._sheet_read(sheet_name=sheet_name)

    def filtered_data(self):
        """
        Фильтрованными по 0 значениями - нули не включать
        исходник - 1000
        на обработку ai_asis - 900
        :return:
        """
        return self._dataframe

    @classmethod
    def get_not_nulled_data(cls, data_dict: dict):
        """Получает ненульные строки"""
        not_nulled_dict = {}
        data: dict
        for index, data in data_dict.items():
            # print(f"{index=} ({type(index)})")
            if data.get(ColumnStrings.DATA_ENTITY_TOBE) in System.NULLED:
                continue
            not_nulled_dict[index] = data
        return not_nulled_dict

    @classmethod
    def get_data_for_remark(cls, data_dict: dict):
        """Получаем данные для переразметки"""
        result = {}
        data_item: dict
        for local_id, data_item in data_dict.items():
            remark: Optional[str] = data_item.get(ColumnStrings.RMK)
            if remark is None:
                continue

            if str(remark) == "1":
                result[local_id] = data_item
                continue

        return result

    @classmethod
    def data_with_only_source_name(cls, data_list: DFType):
        """Получить только local_id и source_name"""
        new_list: DFType = []
        item: XLSGood
        for item in data_list:
            new_list.append(
                {
                    ColumnStrings.DATA_LOCAL_ID: item.get(ColumnStrings.DATA_LOCAL_ID, ''),
                    ColumnStrings.DATA_SOURCE_NAME: item.get(ColumnStrings.DATA_SOURCE_NAME, ''),
                }
            )
        return new_list

    @classmethod
    def valid_no_empty_source_name(cls, data_list: DFType):
        """Проверяет сурснеймы на пустоту"""
        result = True
        item: XLSGood
        for item in data_list:
            source_name: Optional[str] = item.get(ColumnStrings.DATA_SOURCE_NAME)
            if not source_name or source_name in System.FULL_SKIP:
                result = False
                break
        return result

    def _remove_first_sheet_and_rewrite(self):
        """
        Удаляет первый лист из Excel-файла и пересохраняет файл без него.
        Использует pandas и openpyxl для записи.
        """
        sheet_names = self._get_excel_sheet_names()

        if len(sheet_names) <= 1:
            raise ValueError("Невозможно удалить единственный лист")

        try:
            # Читаем все листы, кроме первого
            new_sheets = {}
            for name in sheet_names[1:]:
                df = read_excel(self._file_path, sheet_name=name)
                new_sheets[name] = df.fillna('').map(self._convert_to_string, na_action='ignore')

            # Перезаписываем файл, используя существующую логику записи
            # Временно меняем путь, чтобы не сломать update_file
            temp_df = DataFrame()  # заглушка
            temp_df.to_excel(
                self._file_path, index=False, sheet_name=sheet_names[1]
            )  # костыль для очистки

            with pd.ExcelWriter(self._file_path, engine='openpyxl') as writer:
                for sheet_name, data in new_sheets.items():
                    data.to_excel(writer, sheet_name=sheet_name, index=False)

            logsuc(f"Лист '{sheet_names[0]}' удалён. Файл пересохранён.")
        except PermissionError:
            raise PermissionError("Файл открыт в Excel — невозможно пересохранить.")
        except Exception as e:
            logerr(f"Ошибка при удалении листа: {e}")
            raise

    def _get_excel_sheet_names(self) -> list[str]:
        """
        Возвращает список имён листов в Excel-файле.
        Использует pandas.ExcelFile для безопасного чтения метаданных.
        """
        try:
            with pd.ExcelFile(self._file_path) as xls:
                return xls.sheet_names
        except Exception as e:
            logerr(f"Не удалось прочитать структуру Excel-файла: {e}")
            raise ValueError("Ошибка при чтении списка листов") from e

    def check_writable(self, same_file: bool = True):
        """
        Проверить, не открыт ли файл
        :param same_file:
        :return:
        """
        check_writable: bool = self.is_file_writable(same_file)
        if not check_writable:
            raise PermissionError("ФАЙЛ ОТКРЫТ И НЕДОСТУПЕН ДЛЯ ЗАПИСИ")
        logsuc("Файл с данными существует")

    def check_exists(self):
        """
        Проверка файла на существование
        :return:
        """
        if not self._is_new:
            if not self._file_path.exists():
                raise FileNotFoundError("Файл с данными не найден")
            logsuc("Файл с данными доступен для записи")
        else:
            logsuc("Файл является новым и ожидает записи")

    def is_file_writable(self, same_file: bool = True) -> bool:
        """
        INNER-METHOD
        Проверяет, доступен ли файл для записи.
        Возвращает True если файл доступен для записи, False если заблокирован.
        """
        file: Path = self._file_path
        if not same_file:
            file = self._file_output

        if not file.exists():
            return True  # Файл не существует - можно создавать

        try:
            # Пытаемся открыть файл в режиме append для проверки блокировки
            with open(file, 'a'):
                pass
            return True
        except PermissionError:
            return False
        except Exception as e:
            print(f"Неожиданная ошибка при проверке файла: {e}")
            return False

    @property
    def rows_total(self):
        """Вообще все строки"""
        return self.rows_data + 1

    @property
    def rows_data(self):
        """Только строки с данными без заголовков"""
        return len(self._dataframe)

    def get_sheet_names(self):
        """Имена листов"""
        return self._get_excel_sheet_names()

    def _sheet_read(self, sheet_name: Optional[str] = None) -> DFType:
        """Считывает все данные в словарь с преобразованием всех значений в строки"""
        if sheet_name is None:
            dataframe = read_excel(self._file_path)
        else:
            try:
                dataframe = read_excel(self._file_path, sheet_name=sheet_name)
            except Exception as e:
                raise ValueError(e)

        # Заменяем NaN на пустую строку
        dataframe = dataframe.fillna('')

        # Обрабатываем каждую ячейку: приводим к строке, убираем .0 у чисел
        for col in dataframe.columns:
            dataframe[col] = dataframe[col].map(self._convert_to_string)

        return dataframe.to_dict('records')

    @staticmethod
    def _convert_to_string(value) -> str:
        """Преобразует значение в строку, удаляя .0 у float, если это целое число"""
        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return str(value)
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return value.strip()
        return str(value)

    def get_data(self, sheet_name: Optional[str] = None):
        """Получение данных если их нет"""
        if not len(self._dataframe):
            self.read_data(sheet_name=sheet_name)
        return self._dataframe

    def perfect_data(self, data_list: DFType):
        """Только не нульные строки"""
        data = self.local_idfy(data_list)
        return self.get_not_nulled_data(data)

    @deprecated("ДАННЫЙ МЕТОД НЕ ИСПОЛЬЗУЕТСЯ ИЗ-ЗА УСТАРЕВШЕЙ МЕТОДИКИ ПРИСВОЕНИЯ LOCAL_ID")
    def idfy_data(self, data_list: XLSGood):
        """
        Присваивает нумерацию строк в зависимости от ПОРЯДКОВОГО НОМЕРА строки

        :param data_list:
        :return:
        """

        warnings.warn(
            "ReaderController.idfy_data() устарел и будет удалён в будущих версиях. "
            "Используйте local_idfy() или idfy_to_dataframe().",
            DeprecationWarning,
            stacklevel=2
        )
        self._idfy_dataframe = {int(idx) + 1: item for idx, item in enumerate(data_list)}
        return self._idfy_dataframe

    def local_idfy(self, data_list: DFType):
        """Присваивает номера в зависимости от РАНЕЕ ПРИСВОЕННОГО номера - по сути ID"""
        item: dict
        self._local_idfy_dataframe = {
            int(item.get(ColumnStrings.DATA_LOCAL_ID)): item for item in data_list
        }
        return self._local_idfy_dataframe

    def update_file(self, same_file=True):
        """
        Обновляет Excel-файл по self._file_path данными из data_list.
        :param same_file:
        """
        check_writable: bool = self.is_file_writable(same_file=same_file)
        if not check_writable:
            raise PermissionError("ФАЙЛ НЕ ДОСТУПЕН ДЛЯ ЗАПИСИ, ОТКРЫТ!")
        df = DataFrame(self._dataframe)
        if not same_file:
            df.to_excel(self._file_output, index=False)
        else:
            df.to_excel(self._file_path, index=False)
        return True

    @classmethod
    def response_validator_substr(
        cls,
        data_response: list[dict],
        validated_fields: list[str],
        is_ignore: bool = False,
        filled: bool = False
    ):
        """

        :param data_response:
        :param validated_fields:
        :param is_ignore:
        :param filled:
        :return:
        """
        # TODO ПРОВЕРИТЬ СОВПАДЕНИЕ ID ТОГО, ЧТО ОТПРАВИЛ И ТОГО ЧТО ВЕРНУЛА НЕЙРОНКА - raise
        result = []
        for data in data_response:
            if 'ID' not in data:
                logerr("Не найден ID строки")
                pretty_print(data, title=f"data", m2d=False)
                raise

            for field in validated_fields:
                if field not in data:
                    logerr(f"Не найдено поле {field}")
                    pretty_print(data, title=f"data", m2d=False)
                    raise

            if not is_ignore:
                for field in validated_fields:
                    search_value: Optional[str] = data.get(field)
                    if not search_value:
                        # logerr(f"Данные в поле {field} не обнаружены")
                        # pretty_print(data, title=f"data", m2d=False)
                        # raise
                        data[field] = "no_data"
                        search_value = data[field]

                    if search_value not in ["wrong_cat", "no_data"]:
                        source_data: Optional[str] = data.get("source_name")
                        if not source_data:
                            logerr(f"Источник в ответе не обнаружен")
                            pretty_print(data, title=f"data", m2d=False)
                            raise

                        if search_value.lower() not in source_data.lower():
                            logerr(f"Подстрока {field}={search_value} НЕ НАЙДЕНА в source_name")
                            pretty_print(data, title=f"data", m2d=False)
                            raise

            result.append(data)

        return result

    def override_dataframe(self, data_list, is_hard: bool = False):
        """
        Перезапись датафрейма
        :param data_list:
        :param is_hard: ПРИНУДИТЕЛЬНО БЕЗ ПРОВЕРОК
        :return:
        """
        if not len(data_list):
            raise ValueError("СОДЕРЖИМОЕ ПУСТОЕ, НЕ МОГУ ПЕРЕЗАПИСАТЬ ДАТАФРЕЙМ")
        if not is_hard:
            if len(self._dataframe) != len(data_list):
                raise ValueError("СОДЕРЖИМОЕ ПО КОЛИЧЕСТВУ РАЗНОЕ, НЕ МОГУ ПЕРЕЗАПИСАТЬ ДАТАФРЕЙМ")
        self._dataframe = data_list

    def _rewrite_dataframe_by_local(self):
        len_local = len(self._local_idfy_dataframe)
        len_main = len(self._dataframe)
        if len_local != len_main:
            raise ValueError("Датафреймы не равны для обновления")
        result = []
        for _, data_item in self._local_idfy_dataframe.items():
            result.append(data_item)
        return result

    def update_dataframe_from_updated_dataframe(
        self,
        updated_dataframe,
        updated_fields: list,
        field_id: str = "ID",
    ) -> Optional[bool]:
        """Обновляет главный датафрейм, используя данные обновлённого датафрейма"""
        if not len(updated_dataframe):
            logerr("Пустой обновлённый датафрейм")
            return None
        if not len(updated_fields):
            logerr("Не указаны обновляемые поля")
            return None

        # pretty_print(self._local_idfy_dataframe, title=f"self._local_idfy_dataframe", m2d=False)
        for u_id, u_data in updated_dataframe.items():
            ID: int = int(u_id)
            if ID not in self._local_idfy_dataframe:
                print(f"{ID=}")
                print(f"{u_id=}")
                pretty_print(u_data, title=f"u_data", m2d=False)
                # self.show_local_idfy_dataframe()
                raise IndexError("ID НЕ НАЙДЕН В LOCAL_IDFY")

            for field in updated_fields:
                if field not in u_data:
                    print(f"{ID=}")
                    print(f"{field=}")
                    pretty_print(u_data, title=f"u_data", m2d=False)
                    raise IndexError("FIELD НЕ НАЙДЕН В U_DATA")

                local_id_data_item: dict = self._local_idfy_dataframe.get(ID)
                if field not in local_id_data_item:
                    print(f"{ID=}")
                    print(f"{field=}")
                    pretty_print(local_id_data_item, title=f"local_id_data_item", m2d=False)
                    raise IndexError("FIELD НЕ НАЙДЕН В local_id_data_item")

                self._local_idfy_dataframe[ID][field] = u_data[field]
        self._dataframe = self._rewrite_dataframe_by_local()
        return True

    def update_dataframe(
        self,
        data_response: list[dict],
        required_fields: list[str],
        primary_key: Optional[str] = None,
    ):
        """
        Старый метод обновления датафрейма
        Обновляет idfy_dataframe из приходящего list[dict]
        :param data_response:
        :param required_fields:
        :param primary_key:
        :return:
        """
        if primary_key is None:
            primary_key = System.ID

        if not len(data_response):
            loginf("Нет данных для изменений")
            return self._dataframe
        data: dict
        for data in data_response:
            ID: Optional[str] = data.get(primary_key, None)
            if not ID:
                pretty_print(data, title=f"data", m2d=False)
                raise ValueError("ID НЕ УКАЗАН В RESPONSE")
            index: Optional[int] = int(ID)
            if not index:
                logerr("INDEX не определён")
                pretty_print(data, title=f"data", m2d=False)
                raise
            if index not in self._idfy_dataframe:
                logerr("INDEX не найден")
                pretty_print(data, title=f"data", m2d=False)
                raise

            for field in required_fields:
                self._idfy_dataframe[index][field] = data.get(field)

    def modify_dataframe(self):
        """
        Применение изменений из idfy в основной dataframe
        :return:
        """
        self._dataframe = list(self._idfy_dataframe.values())
        return self._dataframe

    @classmethod
    def _check_field_in_data_item(cls, data_item: dict, field: str) -> bool:
        """Проверяет поле field в data_item"""
        return field in data_item

    def _right_sheet(self, data_item: dict) -> bool:
        """Поиск SOURCE_NAME и URL"""
        loginf("Right sheet?..")
        if (
            self._check_field_in_data_item(data_item, ColumnStrings.DATA_SOURCE_NAME)
            and
            self._check_field_in_data_item(data_item, ColumnStrings.DATA_URL)
        ):
            return True
        # raise WrongDocumentErr("ПЕРВЫЙ ЛИСТ ДОКУМЕНТА НЕ ЯВЛЯЕТСЯ ЛИСТОМ С ДАННЫМИ")
        return False

    def cycle_right_sheet(self) -> None:
        """
        Циклически проверяет первый лист Excel-файла.
        Если не содержит нужные поля (source_name, url) — удаляет его и повторяет.
        Останавливается, когда находит подходящий лист или остаётся один лист.
        """
        loginf("Запуск поиска подходящего листа...")

        while True:
            sheet_names = self._get_excel_sheet_names()
            loginf(f"Остались листы: {sheet_names}")

            # Пытаемся прочитать первый лист
            try:
                # Временно читаем только первый лист, как делает _sheet_read
                temp_df = read_excel(self._file_path, sheet_name=sheet_names[0])
                temp_df = temp_df.fillna('')
                for col in temp_df.columns:
                    temp_df[col] = temp_df[col].map(self._convert_to_string)
                records = temp_df.to_dict('records')
            except Exception as e:
                logerr(f"Не удалось прочитать лист '{sheet_names[0]}': {e}")
                if len(sheet_names) == 1:
                    raise WrongSheetListError("Единственный лист повреждён или пуст") from e
                else:
                    # Пробуем следующий
                    self._remove_first_sheet_and_rewrite()
                    continue

            # Проверяем, подходит ли первый элемент
            if records and self._right_sheet(records[0]):
                logsuc(f"Найден подходящий лист: '{sheet_names[0]}'")
                return

            # Лист не подходит
            if len(sheet_names) == 1:
                logerr(f"Последний лист '{sheet_names[0]}' не содержит source_name и url")
                raise WrongSheetListError("Ни один лист не содержит обязательных полей")

            # Удаляем первый лист и повторяем
            self._remove_first_sheet_and_rewrite()

            # Сбрасываем внутреннее состояние, чтобы при следующем read_data() был перечитан файл
            self._dataframe = []

    def check_local_id(self, find_it: bool = True):
        """Проверяет, присутствует ли в файле local_id"""
        if not self._dataframe:
            self.read_data()
        if not self._dataframe:
            raise ContentLengthError("Нет данных")
        data_item: XLSGood = self._dataframe[0]
        if not data_item.keys():
            raise ContentLengthError("Нет данных в позиции")

        self.cycle_right_sheet()
        if find_it:
            return self._check_field_in_data_item(data_item, ColumnStrings.DATA_LOCAL_ID)

        return True

    def process_local_idfying(self, field: str = ColumnStrings.DATA_LOCAL_ID):
        """Проставляем {field} внутрь файла"""
        log("Добавляю LOCAL_ID...")
        if not self._dataframe:
            self.read_data()

        data: DFType = self.get_data()
        data_item: XLSGood
        for index, data_item in enumerate(data):
            data_idfy: dict = {
                "local_id": index + 1,
                **data_item
            }
            data[index] = data_idfy

        self.override_dataframe(data)
        self.update_file()
        logsuc("В файл добавлен LOCAL_ID")

    def get_asis_fields(self):
        """Получает все asis-столбцы"""
        if not self._dataframe:
            self.read_data()
        if not self._dataframe:
            raise ContentLengthError("Нет данных")
        data_item: XLSGood = self._dataframe[0]
        if not data_item.keys():
            raise AttributeError("Нет данных в итеме")
        result: list[str] = []
        for field, _ in data_item.items():
            if "_asis" in field:
                result.append(field)
        return sorted(result)

    def get_tobe_fields(self):
        """Получает все tobe-столбцы"""
        if not self._dataframe:
            self.read_data()
        if not self._dataframe:
            raise ContentLengthError("Нет данных")
        data_item: XLSGood = self._dataframe[0]
        if not data_item.keys():
            raise AttributeError("Нет данных в итеме")
        result: list[str] = []
        for field, _ in data_item.items():
            if "_tobe" in field:
                result.append(field)
        return sorted(result)

    def get_all_fields(self):
        """Получает все столбцы"""
        return sorted(
            [
                *self.get_asis_fields(),
                *self.get_tobe_fields()
            ]
        )

    def idfy_to_dataframe(self, idfy_data: IdfyGoods):
        """Преобразовать idfy-данные в DFType (датафрейм)"""
        self._dataframe = [data_item for _, data_item in idfy_data.items()]
        return self._dataframe

    def save_to_csv(self, same_file=True):
        """
        Сохранить в формате CSV
        Необходимо в _file_path|_file_output прописывать .csv
        """
        df = DataFrame(self._dataframe)
        if not same_file:
            df.to_csv(self._file_output, index=False)
        else:
            df.to_csv(self._file_path, index=False)
        return True

    def rename(self, new_name: str, same_file: bool = True) -> bool:
        """Переименовывает файл."""
        # Определяем путь и директорию назначения
        file_path = self._file_path if same_file else self._file_output
        target_dir = file_path.parent

        # Формируем новое имя с сохранением расширения
        new_path = target_dir / f"{new_name}{file_path.suffix}"

        # Переименовываем
        file_path.rename(new_path)

        # Обновляем путь в объекте
        if same_file:
            self._file_path = new_path
        else:
            self._file_output = new_path

        return True

    def show_local_idfy_dataframe(self):
        """Показать local_idfy"""
        pretty_print(self._local_idfy_dataframe, title=f"self._local_idfy_dataframe", m2d=False)

    def show_idfy_dataframe(self):
        """Показать idfy_dataframe"""
        pretty_print(self._idfy_dataframe, title=f"self._idfy_dataframe", m2d=False)
