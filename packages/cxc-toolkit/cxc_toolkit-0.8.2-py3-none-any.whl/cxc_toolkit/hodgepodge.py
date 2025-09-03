import re


def xor_hex(hex_1, hex_2, longest=False):
    """
    Xor hex_1 and hex_2, return the result as a hex

    :param hex_1: string represent of a hex
    :param hex_2: string represent of another hex
    :type hex_1: str
    :type hex_2: str
    :return: xor of hex_1 and hex_2 and present as string
    :rtype: str
    """
    # init variable
    xor_hex = ""

    # make hex_1 be the longer string
    if len(hex_1) < len(hex_2):
        hex_1, hex_2 = hex_2, hex_1

    for i in range(len(hex_1)):
        if i < len(hex_2):
            xor_hex += "{:x}".format(int(hex_1[i], 16) ^ int(hex_2[i], 16))
        else:
            if longest:
                xor_hex += hex_1[i:]
            break
    return xor_hex


def is_word(c):
    """
    Determine if character c is word.
    Word means in set {a-z, A-Z, 0-9, "_"}

    :param c:
    :type c: str/bytes
    :return:
    :rtype: bool
    """
    if len(c) != 1:
        raise ValueError("c must be a string with length 1")

    if isinstance(c, bytes):
        c = c.decode("ascii", errors="ignore")

    regex = r"^\w$"
    pattern = re.compile(regex)
    match = pattern.match(c)
    return bool(match)


def is_normal_character(c):
    """
    Determine if character c is normal character.
    Normal character means in set {word, space, ",", "."}

    :param c:
    :type c: str/bytes
    :return:
    :rtype: bool
    """
    if isinstance(c, bytes):
        c = c.decode("ascii", errors="ignore")

    if is_word(c) or c.isspace() or c in ",.":
        return True
    return False
