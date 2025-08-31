"""КАСТОМНЫЕ ОШИБКИ"""


class ContentLengthError(Exception):
    """Нет содержимого"""
    pass


class WrongSheetListError(Exception):
    """Неверный лист документа"""
    pass


class LocalIDError(Exception):
    """Отсутствует local_id"""
    pass
