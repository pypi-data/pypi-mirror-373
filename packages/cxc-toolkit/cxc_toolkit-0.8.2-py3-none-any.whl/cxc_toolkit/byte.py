from cxc_toolkit import integer


def xor(byte_1, byte_2, longest=False):
    """
    Xor byte_1 and byte_2, return the result as a bytes

    :type ytes_1: bytes
    :type byte_2: bytes
    :rtype: bytes
    """
    # init variables
    bytearray_1 = bytearray(byte_1)
    bytearray_2 = bytearray(byte_2)
    xor_bytearray = bytearray()

    # make bytearray_1 be the longest bytearray
    if len(bytearray_1) < len(bytearray_2):
        bytearray_1, bytearray_2 = bytearray_2, bytearray_1

    for i in range(len(bytearray_1)):
        if i < len(bytearray_2):
            xor_bytearray.append(bytearray_1[i] ^ bytearray_2[i])
        else:
            if longest:
                xor_bytearray += bytearray_1[i:]
            break
    return bytes(xor_bytearray)


def to_int(byte):
    """
    Convert bytes to int

    :type byte: bytes
    :rtype: int
    """
    s = 0
    for i, number in enumerate(byte):
        s = s * 256 + number
    return s


def add(byte, addtions):
    """
    Add int to bytes

    :type byte: bytes
    :type addtions: int
    :rtype: bytes
    """
    return integer.to_bytes(to_int(byte) + addtions, bytes_size=len(byte))
