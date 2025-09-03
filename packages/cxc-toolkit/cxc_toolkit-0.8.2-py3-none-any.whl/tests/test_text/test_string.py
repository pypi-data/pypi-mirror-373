import unittest

from cxc_toolkit.text.string.intern_conversion import (
    utf8_to_hex,
    hex_to_utf8,
    hex_to_ascii,
)


class TestInternConversion(unittest.TestCase):

    def test_utf8_and_hex(self):
        """
        Test convert between unicode utf8_string and hex string
        """
        utf8_string = "123"
        hex_string = "313233"
        assert utf8_to_hex(utf8_string) == hex_string
        assert utf8_string == hex_to_utf8(hex_string)
        utf8_string = "az9?"
        hex_string = "617a393f"
        assert utf8_to_hex(utf8_string) == hex_string
        assert utf8_string == hex_to_utf8(hex_string)
        utf8_string = "崔晓晨"
        hex_string = "e5b494e69993e699a8"
        assert utf8_to_hex(utf8_string) == hex_string
        assert utf8_string == hex_to_utf8(hex_string)
        utf8_string = "\\xff\\xff"
        hex_string = "ffff"
        assert utf8_string == hex_to_utf8(hex_string)

    def test_ascii_and_hex(self):
        """
        Test convert between ascii string and hex string
        """
        ascii_string = "123"
        hex_string = "313233"
        assert ascii_string == hex_to_ascii(hex_string)
        ascii_string = "az9?"
        hex_string = "617a393f"
        assert ascii_string == hex_to_ascii(hex_string)
        ascii_string = "\\xe5\\xb4\\x94\\xe6\\x99\\x93\\xe6\\x99\\xa8"
        hex_string = "e5b494e69993e699a8"
        assert ascii_string == hex_to_ascii(hex_string)
        ascii_string = "\\xff\\xff"
        hex_string = "ffff"
        assert ascii_string == hex_to_ascii(hex_string)
