"""Дополнительная типизация данных"""

from typing import TypeAlias

XLSGood: TypeAlias = dict[str, str]
DictStr: TypeAlias = XLSGood
DFType: TypeAlias = list[XLSGood]
IdfyGoods: TypeAlias = dict[int, XLSGood]
