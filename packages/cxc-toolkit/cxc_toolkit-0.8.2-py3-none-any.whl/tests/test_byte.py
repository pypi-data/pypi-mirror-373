import struct
from cxc_toolkit.byte import (
    xor,
    to_int,
    add,
)


class TestByte():

    def test_xor(self):
        byte_1 = b"h3ib"
        byte_2 = b"wkmn"
        xor_shortest_hex = "1f58040c"
        xor_longest_hex = xor_shortest_hex
        assert xor_shortest_hex == xor(byte_1, byte_2).hex()
        assert xor_shortest_hex == xor(byte_2, byte_1).hex()
        assert xor_longest_hex == xor(byte_1, byte_2, longest=True).hex()
        assert xor_longest_hex == xor(byte_2, byte_1, longest=True).hex()

        byte_1 = b"1\".# s_hi+"
        byte_2 = b"@w-ch`~ss123&&"
        xor_shortest_hex = "715503404813211b1a1a"
        xor_longest_hex = "715503404813211b1a1a32332626"
        assert xor_shortest_hex == xor(byte_1, byte_2).hex()
        assert xor_shortest_hex == xor(byte_2, byte_1).hex()
        assert xor_longest_hex == xor(byte_1, byte_2, longest=True).hex()
        assert xor_longest_hex == xor(byte_2, byte_1, longest=True).hex()

    def test_to_int(self):
        number_1 = 199
        byte_1 = struct.pack('>B', number_1)
        assert to_int(byte_1) == number_1

        number_2 = 312
        byte_2 = struct.pack('>H', number_2)
        assert to_int(byte_2) == number_2

        number_3 = 588899
        byte_3 = struct.pack('>L', number_3)
        assert to_int(byte_3) == number_3

        number_4 = 42949672953
        byte_4 = struct.pack('>Q', number_4)
        assert to_int(byte_4) == number_4

        number = number_4 * 65536 + number_2
        byte = byte_4 + byte_2
        assert to_int(byte) == number

    def test_add(self):
        byte = b'\x3d\x89\xa0\x28\x3a\xb3\xcd\xf3\xca\x00\x0c\xd3'
        number = 1
        byte_sum = b'\x3d\x89\xa0\x28\x3a\xb3\xcd\xf3\xca\x00\x0c\xd4'
        assert add(byte, number) == byte_sum
        number = 37017096
        byte_sum = b'\x3d\x89\xa0\x28\x3a\xb3\xcd\xf3\xcc\x34\xe2\xdb'
        assert add(byte, number) == byte_sum
