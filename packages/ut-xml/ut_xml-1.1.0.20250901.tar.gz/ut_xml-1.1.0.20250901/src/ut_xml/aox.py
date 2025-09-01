# coding=utf-8
"""
Koskya XML general Utilities Module
contains the Kosakya XML general Utilities Classes
"""
from typing import Any, TypeAlias

from lxml import etree

TyDocInfo: TypeAlias = etree.DocInfo
TyArr = list[Any]
TyBytes = bytes
TyAoB = list[TyBytes]
TyAoX = list[str]
TnBytes = None | TyBytes
TnDocInfo = None | TyDocInfo


class AoX:
    """
    Array of Xml Objects
    """
    @staticmethod
    def to_aob(aox: TyAoX, docinfo: TnDocInfo = None) -> TyAoB:
        aob: TyAoB = []
        if docinfo is None:
            encoding = None
        else:
            encoding = docinfo.encoding
        for item in aox:
            b_xmlstr: TyBytes = etree.tostring(
                         item,
                         xml_declaration=False,
                         with_comments=True,
                         encoding=encoding,
                         pretty_print=True)
            aob.append(b_xmlstr)
        return aob

    @classmethod
    def to_ByteStr(
            cls, aox: TyAoX,
            b_header: TnBytes = None,
            b_footer: TnBytes = None,
            docinfo: TnDocInfo = None) -> TyBytes:
        return b'\n'.join(cls.to_aob(aox, docinfo))
