def value_to_bool(value: any) -> bool:
    """
    Преобразует значение в bool по расширенным правилам.

    True: 'true', '1', 1, 'yes', 'on', '+', 'ok', 'да', 'вкл', True
    False: 'false', '0', 0, 'no', 'off', '-', 'нет', 'выкл', False, None, '', ' '

    :param value: Любое значение
    :return: bool
    :raises: ValueError при неоднозначных строках (если включить strict)
    """
    if value is None:
        return False

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if not isinstance(value, str):
        # Если не строка, не число и не bool — пытаемся привести к строке
        try:
            value = str(value).strip()
        except Exception:
            return False

    # Приводим к строке и очищаем
    value = value.strip()

    if not value:
        return False

    # Нормализуем к нижнему регистру
    normalized = value.lower()

    # Списки значений
    true_values = {
        'true', '1', 'yes', 'on', 'ok', 'да', 'вкл', 'y', 't', '+', 'enable', 'enabled'
    }
    false_values = {
        'false', '0', 'no', 'off', 'нет', 'выкл', 'n', 'f', '-', 'disable', 'disabled', 'null',
        'none'
    }

    if normalized in true_values:
        return True
    if normalized in false_values:
        return False

    # Если значение не распознано
    # Можно выбросить ошибку или вернуть False (по умолчанию — False)
    return False
