# -*- coding: utf-8 -*-


def unpack_bcd(byte_array):
    half_byte_array = []
    for byte in byte_array:
        half_byte_array.append(byte >> 4 & 0x0F)
        half_byte_array.append(byte & 0x0F)
    return half_byte_array


def decode_bcd(half_byte_array):
    num = ""
    for byte in half_byte_array:
        byte &= 0b00001111
        assert byte < 10
        num += str(byte)
    return int(num)


def get_namespace(tree):
    """Create an artificial namespace to query xml.

    Try to extract the first namespace from the document. If there isn't any, assume a default namespace.
    This util is necessary since we do not know if prefix is used for the xml namespace or not.
    """
    keys = list(tree.nsmap.keys())
    if len(keys) > 0:
        key = keys[0]
        ns = tree.nsmap[key]
    else:
        ns = "http://ws.gematik.de/fa/vsdm/vsd/v5.2"

    return ns
