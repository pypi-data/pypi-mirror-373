# coding=utf-8
"""
Koskya XML general Utilities Module
contains the Kosakya XML general Utilities Classes
"""
from collections.abc import Iterator
from typing import Any, TypeAlias

from lxml import etree
import xmltodict

from ut_dic.dic import Dic
from ut_obj.byte import Byte

from ut_xml.xml2dicapc import Xml2DicApc
from ut_xml.aox import AoX
from ut_xml.xml2dic import Xml2Dic

TyDocInfo: TypeAlias = etree.DocInfo
TyTree: TypeAlias = etree._Element

TyAny = Any
TyArr = list[Any]
TyBytes = bytes
TyDic = dict[Any, Any]
TyAoB = list[TyBytes]
TyAoD = list[TyDic]
TyAoX = list[str]
TyDoA = dict[Any, TyArr]
TyDoD = dict[Any, TyDic]
TyIterAny = Iterator[Any]
TyPath = str
TyToD = tuple[TyDic, ...]

TnAny = None | Any
TnArr = None | TyArr
TnBool = None | bool
TnDic = None | TyDic


class XML:
    """
    XML Class
    """
    @staticmethod
    def write_aob(aob: TyAoB, path_: TyPath) -> None:
        with open(path_, 'wb') as fd:
            for bytes in aob:
                fd.write(bytes)

    @classmethod
    def write_aox(cls, aox: TyAoX, path: TyPath, kwargs: TyDic) -> None:
        docinfo: TyDocInfo = kwargs.get('docinfo')
        aob: TyAoB = AoX.to_aob(aox, docinfo)
        with open(path, 'wb') as fd:
            for bytes in aob:
                fd.write(bytes)

    @staticmethod
    def write_aox_bytes(aox: TyAoX, path: TyPath, kwargs) -> None:
        # def write_bytes(aox, path_, kwargs) -> None:
        # aox, path_, b_header=None, b_footer=None, docinfo=None):
        b_header: TyBytes = kwargs.get('b_header')
        b_footer: TyBytes = kwargs.get('b_footer')
        docinfo: TyDocInfo = kwargs.get('docinfo')
        with open(path, 'wb') as fd:
            if b_header is not None:
                fd.write(b_header)
            for item in aox:
                out_xml = etree.tostring(
                            item,
                            xml_declaration=False,
                            with_comments=True,
                            encoding=docinfo.encoding,
                            pretty_print=True)
                fd.write(out_xml)
            if b_footer is not None:
                fd.write(b_footer)

    @staticmethod
    def read_2_obj(path: TyPath, **kwargs) -> TnAny:
        mode: str = kwargs.get('mode', 'rb')
        keys: TnArr = kwargs.get('keys')
        with open(path, mode) as fd:
            _bytes: TyBytes = fd.read()
            _str = Byte.replace_by_dic(_bytes, **kwargs)
            dic: TyDic = Xml2Dic.mig(_str)
            if keys is None:
                return None
            return Dic.get(dic, keys)

    @staticmethod
    def read_2_dic_with_xml2dicapc_mig(path, **kwargs) -> TyAny:
        mode = kwargs.get('mode', 'rb')
        with open(path, mode) as fd:
            _bytes = fd.read()
            return Xml2DicApc.mig(_bytes, **kwargs)

    @staticmethod
    def read_2_dic_with_xmltodict(path, **kwargs) -> TyAny:
        mode: str = kwargs.get('mode', 'rb')
        with open(path, mode) as fd:
            _bytes: TyBytes = fd.read()
            return xmltodict.parse(_bytes, **kwargs)

    @staticmethod
    def sh_root_docinfo(path: TyPath):
        tree: TyTree = etree.parse(path)
        docinfo: TyDocInfo = tree.docinfo
        root = tree.getroot()
        return root, docinfo
