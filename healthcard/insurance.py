"""Healthcard insurance module.

This module allows to parse insurance data XML and store insurance data into a python object.
"""
# -*- coding: utf-8 -*-
from lxml import etree

from .utils import get_namespace


class Insurance(object):

    def __init__(self, xml):
        self.xml = xml.decode('iso-8859-15')
        tree = etree.fromstring(xml)
        namsespaces = {}
        namsespaces['vsd'] = get_namespace(tree)

        cost_node = tree.xpath('//vsd:Kostentraeger', namespaces=namsespaces)[0]
        text_list = cost_node.xpath('vsd:Name//text()', namespaces=namsespaces)
        self.insurance_name = text_list[0] if len(text_list) != 0 else ''
