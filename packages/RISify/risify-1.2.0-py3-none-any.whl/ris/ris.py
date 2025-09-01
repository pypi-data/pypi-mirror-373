"""
Definition of the RIS module.
"""

import re
from typing import Union

from markupsafe import Markup

_ENCODING_ASCII = "ascii"
_ENCODING_HTML = "html"
_ENCODING_UNICODE = "unicode"

_ENCODINGS = [
    _ENCODING_ASCII,
    _ENCODING_HTML,
    _ENCODING_UNICODE
]

_DEFAULT_ENCODING = _ENCODING_UNICODE

_ORD_A = ord("A")
_ORD_A_RIS = ord("🇦")
_ORD_Z_RIS = ord("🇿")


def _is_valid_ris(code: str) -> bool:
    """
    Indicate whether the specified string is a valid RIS-code.
    """
    return all(_ORD_A_RIS <= ord(c) <= _ORD_Z_RIS for c in code)


def _expand_html(text: str) -> str:
    """
    Expand any occurrences of HTML-encoded RIS into actual RIS in the
    specified text.
    """
    return re.sub(r"&#(\d{6});", lambda m: chr(int(m.group(1))), text)


def _expand_ascii(text: str) -> str:
    """
    Expand any occurrences of ASCII-encoded RIS (both upper and lower case)
    into actual RIS in the specified text.
    """
    return re.sub(r"[a-zA-Z]", lambda m: chr(ord(
        m.group(0).upper()) - _ORD_A + _ORD_A_RIS), text)


class _RISStr(str):
    """
    Wraps a RIS-string and provides several functions for encoding and decoding
    from and to plain alphabetic text and HTML.
    """

    def __new__(cls,
                value: Union[str, "_RISStr"],
                encoding: str = _ENCODING_UNICODE,
                uppercase: bool = False):
        value = _expand_html(value)
        value = _expand_ascii(value)

        if encoding is not None and encoding not in _ENCODINGS:
            raise ValueError(f"unknown encoding: `{encoding}`")
        if not _is_valid_ris(value):
            raise ValueError(f"`{value}` is not a valid ris code")

        instance = super().__new__(cls, value)

        instance._encoding = encoding or \
                             getattr(value, "_encoding", _DEFAULT_ENCODING)
        instance._uppercase = uppercase if uppercase is not None \
            else getattr(value, "_uppercase", False)

        return instance

    def __str__(self):
        if self._encoding == _ENCODING_UNICODE:
            return super().__str__()

        if self._encoding == _ENCODING_HTML:
            return Markup("".join([
                f"&#{ord(c)};" for c in self
            ]))

        if self._encoding == _ENCODING_ASCII:
            string = "".join([
                chr(_ORD_A + (ord(c) - _ORD_A_RIS))
                for c in self
            ])
            return string if self._uppercase else string.lower()

        return NotImplemented

    def __repr__(self):
        return f"ris({str(self)})"

    def __eq__(self, other):
        if isinstance(other, str):
            try:
                other = _RISStr(other)
            except ValueError:
                return False

        return super().__eq__(other)

    def __ne__(self, other):
        if isinstance(other, str):
            try:
                other = _RISStr(other)
            except ValueError:
                return False

        return super().__ne__(other)

    def _apply_operator(self, operator, arg):
        """
        Helper method to apply the specified operator to the int superclass
        and wrap the result in a ris string with the same properties as
        the current one.

        :param operator: The operator to apply.
        :param arg: The argument for the operator.
        """
        return _RISStr(getattr(super(), operator)(arg),
                       self._encoding,
                       self._uppercase)

    def __add__(self, other):
        return self._apply_operator("__add__", other)

    def __mul__(self, other):
        return self._apply_operator("__mul__", other)

    def __getitem__(self, item):
        return self._apply_operator("__getitem__", item)

    def encode(self, encoding="unicode", errors="strict"):
        """
        Return a RIS string of the same value as the current,
        to be encoded as specified.
        """
        return _RISStr(self, encoding, self._uppercase)

    def upper(self):
        """
        Return a RIS string of the same value as the current,
        to be encoded in upper case. Only has effect
        if encoding is set to ASCII.
        """
        return _RISStr(self, self._encoding, True)

    def lower(self):
        """
        Return a RIS string of the same value as the current,
        to be encoded in lower case. Only has effect
        if encoding is set to ASCII.
        """
        return _RISStr(self, self._encoding, False)
