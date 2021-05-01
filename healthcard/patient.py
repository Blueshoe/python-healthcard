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

from healthcard.utils import get_namespace

sys.getdefaultencoding()


@python_2_unicode_compatible
class Patient(object):
    """Patient object which parses patient XML string into a python object."""

    def __init__(self, xml):
        self.xml = xml
        tree = etree.fromstring(self.xml)
        # xpath only works with a non-empty namespace
        # set namespace for vsd
        namsespaces = {}
        namsespaces["vsd"] = get_namespace(tree)

        text_list = tree.xpath("//vsd:Versicherten_ID//text()", namespaces=namsespaces)
        self.insurant_id = text_list[0] if len(text_list) != 0 else ""
        text_list = tree.xpath("//vsd:Geburtsdatum//text()", namespaces=namsespaces)
        self.birthdate = text_list[0] if len(text_list) != 0 else ""
        self.birthdate = datetime.strptime(self.birthdate, "%Y%m%d")
        text_list = tree.xpath("//vsd:Vorname//text()", namespaces=namsespaces)
        self.first_name = text_list[0] if len(text_list) != 0 else ""
        text_list = tree.xpath("//vsd:Nachname//text()", namespaces=namsespaces)
        self.last_name = text_list[0] if len(text_list) != 0 else ""
        text_list = tree.xpath("//vsd:Geschlecht//text()", namespaces=namsespaces)
        self.gender = text_list[0] if len(text_list) != 0 else ""
        text_list = tree.xpath("//vsd:Vorsatzwort//text()", namespaces=namsespaces)
        self.prefix = text_list[0] if len(text_list) != 0 else ""
        text_list = tree.xpath("//vsd:Namenszusatz//text()", namespaces=namsespaces)
        self.name_addition = text_list[0] if len(text_list) != 0 else ""
        text_list = tree.xpath("//vsd:Titel//text()", namespaces=namsespaces)
        self.title = text_list[0] if len(text_list) != 0 else ""

        postal_address_node = tree.xpath(
            "//vsd:PostfachAdresse", namespaces=namsespaces
        )
        if postal_address_node:
            self.postal_address = PostalAddress(postal_address_node[0], namsespaces)
        residential_address_node = tree.xpath(
            "//vsd:StrassenAdresse", namespaces=namsespaces
        )
        if residential_address_node:
            self.residential_address = ResidenceAddress(
                residential_address_node[0], namsespaces
            )

    @property
    def address(self):
        return (
            self.postal_address
            if getattr(self, "postal_address", None)
            else self.residential_address
        )

    def to_json(self):
        from healthcard.reader import HealthCardJSONEncoder

        return HealthCardJSONEncoder().encode(self)

    def __str__(self):
        return u"{} {}".format(self.first_name, self.last_name)
