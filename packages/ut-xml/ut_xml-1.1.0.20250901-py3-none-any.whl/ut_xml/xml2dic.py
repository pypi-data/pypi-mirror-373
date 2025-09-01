# coding=utf-8
"""
Koskya XML general Utilities Module
contains the Kosakya XML general Utilities Classes
"""
from collections.abc import Iterator
from typing import Any, TypeAlias

from lxml import etree

from ut_dic.dic import Dic

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


class Xml2Dic:
    """
    XML to Dictionary String Class
    Convert xml to dic, using lxml xml processing library.
    see http://lxml.de/
    """
    @staticmethod
    def init_dic(tree: TyTree) -> TyDic:
        """
        initialise tree dictionary
        """
        if tree.tag is etree.Comment:
            return {}
        if tree.attrib:
            dic: TyDic = {}
            dic[tree.tag] = {}
        else:
            if tree.tag:
                dic = {}
                dic[tree.tag] = None
            else:
                dic = {}
        return dic

    # @staticmethod
    # def normalize_value(dic):
    #     """
    #     show normalized dictionary
    #     """
    #     dic_new = {}
    #     for k, v in dic.items():
    #         if len(v) == 1:
    #             dic_new[k] = v[0]
    #         else:
    #             dic_new[k] = v
    #     return dic_new

    @classmethod
    def sh_dic(cls, iterator: Iterator[TyDic]) -> TyDic:
        """
        show children dictionary for children map
        """
        _dic: TyDoA = {}
        for c_tree in iterator:
            for k, v in c_tree.items():
                if k not in _dic:
                    _dic[k] = []
                _dic[k].append(v)

        # if value is list with 1 element use element as value
        _dic_normalized: TyDic = Dic.normalize_values(_dic)
        return _dic_normalized

    @staticmethod
    def update_with_attribs(dic: TyDic, tree: TyTree) -> None:
        """
        update dictionary with attributes dictionary
        """
        attribs = {f'@{k}': v for k, v in tree.attrib.items()}
        dic[tree.tag].update(attribs)

    @staticmethod
    def update_with_text(dic: TyDic, tree: TyTree, children) -> TyDic:
        """
        update dictionary with text
        """
        text: str = tree.text.strip()
        if children or tree.attrib:
            if text:
                dic[tree.tag]['#text'] = text
        else:
            dic[tree.tag] = text
        return dic

    @classmethod
    def update(cls, dic: TyDic, tree: TyTree, children) -> TyDic:
        """
        update dictionary
        """
        if tree.tag is etree.Comment:
            return dic
        if tree.attrib:
            cls.update_with_attribs(dic, tree)
        if tree.text:
            cls.update_with_text(dic, tree, children)
        return dic

    @staticmethod
    def map_seq(fnc, lst) -> TyArr:
        """
        apply function on list using list comprehension

        :param fnc: function
        :param List lst: List
        :return List: List of all elements of lst modified by fnc
        """
        return [fnc(entry) for entry in lst]

    @classmethod
    def tree2dic(cls, tree: TyTree) -> TyDic:
        """
        migrate tree to dictionary
        """
        children: TyArr = list(tree)
        if len(children) > 0:
            iod: Iterator[TyDic] = map(cls.tree2dic, children)
            dic: TyDic = {}
            if tree.tag is not etree.Comment:
                dic[tree.tag] = cls.sh_dic(iod)
        else:
            dic = cls.init_dic(tree)
        cls.update(dic, tree, children)
        return dic

    @classmethod
    def mig(cls, string: str) -> TyDic:
        """
        migrate xml string to etree and etree to dictionary
        """
        tree: TyTree = etree.fromstring(string)
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
