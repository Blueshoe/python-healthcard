"""Healthcard insurance module.

This module allows to parse insurance data XML and store insurance data into a python object.
"""
# -*- coding: utf-8 -*-
from lxml import etree


class Insurance(object):

    def __init__(self, xml):
        self.xml = xml.decode('iso-8859-15')
        tree = etree.fromstring(xml)
        # xpath only works with a non-empty namespace
        # set namespace for vsd
        nsmap = tree.nsmap
        nsmap['vsd'] = nsmap[None]
        del nsmap[None]

        cost_node = tree.xpath('//vsd:Kostentraeger', namespaces=nsmap)[0]
        text_list = cost_node.xpath('vsd:Name//text()', namespaces=nsmap)
        self.insurance_name = text_list[0] if len(text_list) != 0 else ''
