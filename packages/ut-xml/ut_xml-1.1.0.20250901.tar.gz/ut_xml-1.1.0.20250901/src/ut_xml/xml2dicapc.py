# coding=utf-8
"""
Koskya XML general Utilities Module
contains the Kosakya XML general Utilities Classes
"""
from collections.abc import Iterator
from typing import Any, TypeAlias

from lxml import etree

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


class Xml2DicApc:

    # @staticmethod
    # def dic_normalize(dic):
    #     return {k: v[0] if len(v) == 1 else v for k, v in dic.items()}

    @staticmethod
    def sh_v(v, child, arr_child) -> str | Any | TyDic:
        a_key_to_agg: TyArr = ['Attribute', 'Step']
        if child.tag == etree.Comment:
            text: str = child.text.strip()
            return text
        if child.tag not in a_key_to_agg:
            return v
        if not child.attrib and not child.text:
            return v
        if child.attrib:
            dic: TyDic = {f'@{k}': v for k, v in child.attrib.items()}
        else:
            dic = {}
        if child.text:
            text = child.text.strip()
            if len(arr_child) > 0 or child.attrib:
                if text:
                    if not dic:
                        dic = {}
                    dic['#text'] = text
            return text
        if not dic:
            dic = {}
        return dic

    @classmethod
    def tree2dic(cls, tree: TyTree) -> TyDic:
        obj: TyDic = {tree.tag: [] if tree.attrib else None}
        a_child: TyArr = list(tree)
        if len(a_child) > 0:
            aod: Iterator[TyDic] = map(cls.tree2dic, a_child)
            dd: TyDic = {}
            a_tree: TyArr = []
            for ix, dic in enumerate(aod):
                child = a_child[ix]
                if child.tag == etree.Comment:
                    continue
                for k, v in dic.items():
                    v = cls.sh_v(v, child, a_child)
                    a_key_to_agg = ['Attribute', 'Step']
                    if k in a_key_to_agg:
                        if k not in dd:
                            dd[k] = []
                        dd[k].append(v)
                    else:
                        if len(dd) > 0:
                            a_tree.append(dd)
                            dd = {}
                        _dic = {}
                        _dic[k] = v
                        a_tree.append(_dic)
            if len(dd) > 0:
                a_tree.append(dd)
                dd = {}
            obj = {tree.tag: a_tree}
            # obj = {tree.tag: cls.dic_normalize(dd)}
        # obj = set_obj(obj, tree, a_child)
        return obj

    @classmethod
    def mig(cls, str, **kwargs) -> TyDoD :
        """
        migrate xml string to etree and etree to dictionary
        """
        tree: TyTree = etree.fromstring(str)
        # Iterate through all XML elements
        for elem in tree.getiterator():
            # Skip comments and processing instructions,
            # because they do not have names
            if not (
                isinstance(elem, etree._Comment)
                or isinstance(elem, etree._ProcessingInstruction)
            ):
                # Remove a namespace URI in the element's name
                elem.tag = etree.QName(elem).localname
        etree.cleanup_namespaces(tree)
        dic = cls.tree2dic(tree)
        return {tree.tag: dic}
