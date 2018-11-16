"""Healthcard patient module.

This module allows to parse patient xml data from the eGK (Elektronische Gesundheitskarte) and store it into a python
object.

"""
# -*- coding: utf-8 -*-
from datetime import datetime
from lxml import etree
from pip._vendor.six import python_2_unicode_compatible

from healthcard.address import PostalAddress, ResidenceAddress
import sys

sys.getdefaultencoding()


@python_2_unicode_compatible
class Patient(object):
    """Patient object which parses patient XML string into a python object."""

    def __init__(self, xml):
        self.xml = xml
        tree = etree.fromstring(self.xml)
        # xpath only works with a non-empty namespace
        # set namespace for vsd
        nsmap = tree.nsmap
        nsmap['vsd'] = nsmap[None]
        del nsmap[None]

        text_list = tree.xpath('//vsd:Versicherten_ID//text()', namespaces=nsmap)
        self.insurant_id = text_list[0] if len(text_list) != 0 else ''
        text_list = tree.xpath('//vsd:Geburtsdatum//text()', namespaces=nsmap)
        self.birthdate = text_list[0] if len(text_list) != 0 else ''
        self.birthdate = datetime.strptime(self.birthdate, '%Y%m%d')
        text_list = tree.xpath('//vsd:Vorname//text()', namespaces=nsmap)
        self.first_name = text_list[0] if len(text_list) != 0 else ''
        text_list = tree.xpath('//vsd:Nachname//text()', namespaces=nsmap)
        self.last_name = text_list[0] if len(text_list) != 0 else ''
        text_list = tree.xpath('//vsd:Geschlecht//text()', namespaces=nsmap)
        self.gender = text_list[0] if len(text_list) != 0 else ''
        text_list = tree.xpath('//vsd:Vorsatzwort//text()', namespaces=nsmap)
        self.prefix = text_list[0] if len(text_list) != 0 else ''
        text_list = tree.xpath('//vsd:Namenszusatz//text()', namespaces=nsmap)
        self.name_addition = text_list[0] if len(text_list) != 0 else ''
        text_list = tree.xpath('//vsd:Titel//text()', namespaces=nsmap)
        self.title = text_list[0] if len(text_list) != 0 else ''

        postal_address_node = tree.xpath('//vsd:PostfachAdresse', namespaces=nsmap)
        if postal_address_node:
            self.postal_address = PostalAddress(postal_address_node[0], nsmap)
        residential_address_node = tree.xpath('//vsd:StrassenAdresse', namespaces=nsmap)
        if residential_address_node:
            self.residential_address = ResidenceAddress(residential_address_node[0], nsmap)

    def to_json(self):
        from healthcard.reader import HealthCardJSONEncoder
        return HealthCardJSONEncoder().encode(self)

    def __str__(self):
        return u'{} {}'.format(self.first_name, self.last_name)
