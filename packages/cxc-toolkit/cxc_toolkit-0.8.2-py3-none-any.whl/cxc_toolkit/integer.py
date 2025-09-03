def to_bytes(integer, bytes_size=-1, auto_size=False):
    """
    Convert int to bytes

    :type integer: int
    :rtype: bytes
    """
    if bytes_size < 1:
        auto_size = True

    temp_bytearray = bytearray()
    if integer <= 0xFF:
        temp_bytearray.append(integer)
    else:
        while integer:
            integer, remainder = divmod(integer, 256)
            temp_bytearray = bytearray([remainder]) + temp_bytearray

    if auto_size:
        return bytes(temp_bytearray)

    if len(temp_bytearray) > bytes_size:
        raise ValueError("Argument bytes_size {} is too small to hold integer"
                         .format(bytes_size))

    number_of_vacant_characters = bytes_size - len(temp_bytearray)
    temp_bytearray = (bytearray(
        [0 for _ in range(number_of_vacant_characters)]) + temp_bytearray)
    return bytes(temp_bytearray)
