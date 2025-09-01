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


class Xml2Dic2:

    """
    There is no one-true-mapping from an XML to a Python dict;
    one is a node tree, the other is a hash map,
    it's just an "apples and something-else comparison",
    so you'll have to make design decisions for yourself,
    considering what you want.

    The link by Sreehari has a solution that does a decent job of
    converting an lxml node to a Python dict, but:

    it requires lxml, which is fine, but I like standard modules
    when they do the job it doesn't capture attributes.
    I've taken that code and converted it work with Python's standard
    xml.ElementTree module/class, and it handles attributes in its own way.

    When I run this code against your sample, I get the following dict:

    {'fees': [{'@attribs': {'mail_retail': 'MAIL', 'member_group': '00400F'},
               'admin_fee': '0.76',
               'processing_fee': '1.83'},
              {'@attribs': {'mail_retail': 'RETAIL', 'member_group': '00400F'},
               'admin_fee': '1.335',
               'processing_fee': '1.645'},
              {'@attribs': {'mail_retail': 'MAIL', 'member_group': '00460G'},
               'admin_fee': '0.88',
           'processing_fee': '1.18'}]}
    Notice the @attribs key, that's how I decided attributes should be stored.
    If you need something else, you can modify it to your liking:
    """

    @classmethod
    def node_2_dic(cls, node) -> TyDic:
        # def elem2dict(cls, node) -> TyDic:
        """
        Convert an xml.ElementTree node tree into a dict.
        """
        result: TyDic = {}

        for element in node:
            key = element.tag
            if '}' in key:
                # Remove namespace prefix
                key = key.split('}')[1]
            if node.attrib:
                result['@attribs'] = dict(node.items())
            # Process element as tree element if the inner XML contains
            # non-whitespace content
            if element.text and element.text.strip():
                value = element.text
            else:
                value = cls.node_2_dic(element)
            # Check if a node with this name at this depth was already found
            if key in result:
                if not isinstance(result[key], list):
                    # We've seen it before, but only once, we need to
                    # convert it to a list
                    tempvalue = result[key].copy()
                    result[key] = [tempvalue, value]
                else:
                    # We've seen it at least once, it's already a list,
                    # just append the node's inner XML
                    result[key].append(value)
            else:
                # First time we've seen it
                result[key] = value
        return result

    @classmethod
    def mig(cls, path: TyPath) -> TyDic:
        from xml.etree import ElementTree as ET
        return cls.node_2_dic(ET.parse('input.xml').getroot())
