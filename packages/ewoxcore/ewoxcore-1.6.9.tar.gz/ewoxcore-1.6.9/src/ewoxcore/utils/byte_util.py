from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
import base64
import binascii
import re

class ByteUtil:

    @staticmethod
    def to_base64(data: bytes) -> str:
        """
        Convert bytes to a Base64 encoded string.
        """
        return base64.b64encode(data).decode('utf-8')
    

    @staticmethod
    def from_base64(encoded_data: str) -> bytes:
        """
        Convert a Base64 encoded string back to bytes.
        """
        return base64.b64decode(encoded_data.encode('utf-8'), validate=True)


    @staticmethod
    def is_base64(encoded_data: str) -> bool:
        """ Check if a string is a valid Base64 encoded string.
        This method handles both standard and URL-safe Base64 formats.
        It also accepts data URIs (e.g., "data:...;base64,<data>"). """
        if not isinstance(encoded_data, str) or not encoded_data.strip():
            return False

        # Strip data URI prefix, whitespace, newlines
        enc_cleaned = encoded_data.strip().split(",")[-1].replace("\n", "").replace("\r", "")
        # Fast character filter (std + url-safe + '=')
        if not re.fullmatch(r"[A-Za-z0-9+/=_-]+", enc_cleaned):
            return False

        # Pad to multiple of 4
        enc_cleaned += "=" * (-len(enc_cleaned) % 4)

        try:
            # URL-safe decode accepts both alphabets when altchars are given
            base64.b64decode(enc_cleaned, altchars=b"-_", validate=True)
            return True
        except binascii.Error:
            return False


    @staticmethod
    def decode_base64(encoded_data: str) -> bytes:
        """ Decode a Base64 encoded string, handling both standard and URL-safe formats. """
        # keep only the data (handles "data:...;base64,<data>" too)
        encoded_data = encoded_data.strip().replace("\n", "").replace("\r", "").split(",")[-1]
        # pad to a multiple of 4 (Base64 requirement)
        encoded_data += "=" * (-len(encoded_data) % 4)
        # decode using URL-safe alphabet
        return base64.urlsafe_b64decode(encoded_data)