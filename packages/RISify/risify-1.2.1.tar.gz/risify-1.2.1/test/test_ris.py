"""
Tests for the RIS class.
"""
from unittest import TestCase

from ris import ris


class TestRIS(TestCase):
    """
    A test case for the RIS class.
    """

    def test_ris_eq_ris(self):
        """
        Assert that a RIS is equal to another RIS of the same value.
        """
        self.assertEqual(ris("🇳🇱"), ris("🇳🇱"))

    def test_ris_eq_ascii(self):
        """
        Assert that a RIS is equal to a string representing
        the same country code.
        """
        self.assertEqual(ris("🇵🇹"), "PT")

    def test_ris_eq_ascii_lower(self):
        """
        Assert that a RIS is equal to a string representing
        the same country code in lower case.
        """
        self.assertEqual(ris("🇵🇹"), "pt")

    def test_ris_eq_html(self):
        """
        Assert that a RIS is equal to an HTML encoding of the same value.
        """
        self.assertEqual(ris("🇫🇴"), "&#127467;&#127476;")

    def test_ris_ascii_upper(self):
        """
        Assert that uppercase ASCII can be decoded to RIS-codes.
        """
        self.assertEqual(ris("PT"), "🇵🇹")

    def test_ris_ascii_lower(self):
        """
        Assert that lowercase ASCII can be decoded to RIS-codes.
        """
        self.assertEqual(ris("pt"), "🇵🇹")

    def test_ris_html(self):
        """
        Assert that HTML can be decoded to RIS-codes.
        """
        self.assertEqual(ris("&#127467;&#127476;"), "🇫🇴")

    def test_ris_encode_ascii_upper(self):
        """
        Assert that RIS-codes can be encoded to ASCII.
        """
        self.assertEqual(str(ris("🇨🇦").encode("ascii").upper()), "CA")

    def test_ris_encode_ascii_lower(self):
        """
        Assert that RIS-codes can be encoded to lower case ASCII.
        """
        self.assertEqual(str(ris("🇨🇦").encode("ascii").lower()), "ca")

    def test_ris_encode_html(self):
        """
        Assert that RIS-codes can be encoded to HTML.
        """
        self.assertEqual(str(ris("🇳🇱").encode("html")), "&#127475;&#127473;")

    def test_ris_decode_error(self):
        """
        Assert that invalid RIS-codes will result in an error.
        """
        with self.assertRaises(ValueError):
            ris("123")

    def test_ris_concat(self):
        """
        Assert that a RIS-code can be concatenated to a string.
        """
        self.assertEqual("spam " + ris("🇳🇱"), "spam 🇳🇱")
