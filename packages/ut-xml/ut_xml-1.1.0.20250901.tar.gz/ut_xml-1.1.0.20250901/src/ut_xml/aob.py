# coding=utf-8
"""
Koskya XML general Utilities Module
contains the Kosakya XML general Utilities Classes
"""

from ut_xml.xml2dic import Xml2Dic

from typing import Any
TyAny = Any
TyBytes = bytes
TyAoB = list[TyBytes]
TyDic = dict[Any, Any]
TyStr = str


class AoB:
    """
    Array of Bytes
    """
    @staticmethod
    def to_Bytes(aob: TyAoB) -> TyBytes:
        return b'\n'.join(aob)

    @staticmethod
    def to_String(aob: TyAoB) -> TyStr:
        return '\n'.join(map(str, aob))

    @classmethod
    def to_Dic(cls, aob: TyAoB) -> TyDic:
        _str: str = cls.to_String(aob)
        _dic: TyDic = Xml2Dic.mig(_str)
        return _dic
