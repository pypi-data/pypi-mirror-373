import binascii


def utf8_to_hex(s):
    """
    Return hex representation of s

    :param s:
    :type s: str
    :return:
    :rtype: str
    """
    return s.encode("utf-8", errors="backslashreplace").hex()


def hex_to_utf8(h):
    """
    Return utf-8 string who's hexadecimal corresponds to hex

    :param h:
    :type h: str
    :return:
    :rtype: str
    """
    return binascii.unhexlify(h).decode("utf-8", errors="backslashreplace")


def hex_to_ascii(h):
    """
    Return ascii decoded string who's hexadecimal corresponds to hex

    :param h:
    :type h: str
    :return:
    :rtype: str
    """
    return binascii.unhexlify(h).decode("ascii", errors="backslashreplace")
