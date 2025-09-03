from nose.tools import assert_raises

from cxc_toolkit.integer import (
    to_bytes,
)


class TestInteger():

    def test_to_bytes(self):
        number_1 = 0
        byte_1 = b'\x00'
        assert to_bytes(number_1) == byte_1

        number_1 = 0xa3
        byte_1 = b'\xa3'
        assert to_bytes(number_1) == byte_1
        byte_1 = b'\x00\xa3'
        assert to_bytes(number_1, bytes_size=2) == byte_1
        byte_1 = b'\x00\x00\xa3'
        assert to_bytes(number_1, bytes_size=3) == byte_1

        number_2 = 0x043f
        byte_2 = b'\x04\x3f'
        assert to_bytes(number_2, bytes_size=2) == byte_2
        byte_2 = b'\x00\x04\x3f'
        assert to_bytes(number_2, bytes_size=3) == byte_2

        number_3 = 0xc3913a
        byte_3 = b'\xc3\x91\x3a'
        assert to_bytes(number_3, bytes_size=3) == byte_3
        assert to_bytes(number_3, auto_size=True) == byte_3
        with assert_raises(ValueError):
            assert to_bytes(number_3, bytes_size=1) == number_3

        number_4 = 0x3d89a0283ab3cdf3ca000cd3
        byte_4 = b'\x3d\x89\xa0\x28\x3a\xb3\xcd\xf3\xca\x00\x0c\xd3'
        assert to_bytes(number_4, auto_size=True) == byte_4
