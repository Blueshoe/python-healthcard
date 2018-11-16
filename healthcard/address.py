# -*- coding: utf-8 -*-
"""Address module to parse lxml's etree._Element objects for address data.

There are 2 different formats in which the XML could be read from the eGK (Elektronische Gesundheitskarte):
VSD 5.1.x and VSD 5.2.x

There is a good source which explains the main difference between both formats:
ftp://ftp.kbv.de/ita-update/Abrechnung/KBV_ITA_VGEX_Mapping_KVK.pdf (page 9)
"""
from pip._vendor.six import python_2_unicode_compatible


@python_2_unicode_compatible
class Address(object):

    def __init__(self, root, nsmap):
        text_list = root.xpath('//vsd:Ort//text()', namespaces=nsmap)
        self.city = text_list[0] if len(text_list) != 0 else ''
        text_list = root.xpath('//vsd:Postleitzahl//text()', namespaces=nsmap)
        self.zip_code = text_list[0] if len(text_list) != 0 else ''
        text_list = root.xpath('//vsd:Wohnsitzlaendercode//text()', namespaces=nsmap)
        self.country_code = text_list[0] if len(text_list) != 0 else ''

    def __str__(self):
        return u'{}-{} {}'.format(self.country_code, self.zip_code, self.city)


@python_2_unicode_compatible
class PostalAddress(Address):

    def __init__(self, root, nsmap):
        """Parses an etree._Element for postal address data.

        Since there are two different version for the format of VSD xml data (5.1.x and 5.2.x) there are different tags
        needed to access the same property. If VSD 5.1.x is not found we try to access the VSD 5.2.x version of a tag.
        """
        text_list = root.xpath('//vsd:Ort//text()', namespaces=nsmap)
        self.city = text_list[0] if len(text_list) != 0 else ''
        text_list = root.xpath('//vsd:Postleitzahl//text()', namespaces=nsmap)
        self.zip_code = text_list[0] if len(text_list) != 0 else ''
        text_list = root.xpath('//vsd:Postfach//text()', namespaces=nsmap)
        self.mailbox = text_list[0] if len(text_list) != 0 else ''
        super(PostalAddress, self).__init__(root, nsmap)

    def __str__(self):
        return u'{}-{} {} - Mailbox {}'.format(self.country_code, self.zip_code, self.city, self.mailbox)


@python_2_unicode_compatible
class ResidenceAddress(Address):
    """Parses an etree._Element object for residential address data."""

    def __init__(self, root, nsmap):
        text_list = root.xpath('//vsd:Strasse//text()', namespaces=nsmap)
        self.street = text_list[0] if len(text_list) != 0 else ''
        text_list = root.xpath('//vsd:Hausnummer//text()', namespaces=nsmap)
        self.street_number = text_list[0] if len(text_list) != 0 else ''
        text_list = root.xpath('//vsd:Anschriftenzusatz//text()', namespaces=nsmap)
        self.address_addition = text_list[0] if len(text_list) != 0 else ''
        super(ResidenceAddress, self).__init__(root, nsmap)

    def __str__(self):
        return u'{}-{} {} - {} {}'.format(self.country_code, self.zip_code, self.city, self.street,
                                          self.street_number, self.address_addition)
