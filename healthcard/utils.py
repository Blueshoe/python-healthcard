# -*- coding: utf-8 -*-


def unpack_bcd(byte_array):
    half_byte_array = []
    for byte in byte_array:
        half_byte_array.append(byte >> 4 & 0x0F)
        half_byte_array.append(byte & 0x0F)
    return half_byte_array


def decode_bcd(half_byte_array):
    num = ''
    for byte in half_byte_array:
        byte &= 0b00001111
        assert byte < 10
        num += str(byte)
    return int(num)
