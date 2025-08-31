import binascii
import hashlib
import hmac
import os
from collections.abc import Callable
from typing import Any, ClassVar

from hash_forge.config import DEFAULT_PBKDF2_ITERATIONS, DEFAULT_PBKDF2_SALT_LENGTH, MIN_PBKDF2_ITERATIONS
from hash_forge.exceptions import InvalidHasherError
from hash_forge.protocols import PHasher


class PBKDF2Sha256Hasher(PHasher):
    algorithm: ClassVar[str] = 'pbkdf2_sha256'
    digest: ClassVar[Callable[..., Any]] = hashlib.sha256

    def __init__(
        self, 
        iterations: int = DEFAULT_PBKDF2_ITERATIONS, 
        salt_length: int = DEFAULT_PBKDF2_SALT_LENGTH
    ) -> None:
        if iterations < MIN_PBKDF2_ITERATIONS:
            raise InvalidHasherError(f"PBKDF2 iterations must be at least {MIN_PBKDF2_ITERATIONS}")
        self.iterations = iterations
        self.salt_length = salt_length

    __slots__ = ('iterations', 'salt_length')

    def hash(self, _string: str, /) -> str:
        """
        Hashes a given string using the PBKDF2 (Password-Based Key Derivation Function 2) algorithm.

        Args:
            _string (str): The input string to be hashed.

        Returns:
            str: The hashed string in the format 'algorithm$iterations$salt$hashed'.
        """
        salt: str = binascii.hexlify(os.urandom(self.salt_length)).decode('ascii')
        dk: bytes = hashlib.pbkdf2_hmac(self.digest().name, _string.encode(), salt.encode(), self.iterations)
        hashed: str = binascii.hexlify(dk).decode('ascii')
        return f'{self.algorithm}${self.iterations}${salt}${hashed}'

    def verify(self, _string: str, _hashed_string: str, /) -> bool:
        """
        Verifies if a given string matches the hashed string using PBKDF2 algorithm.

        Args:
            _string (str): The plain text string to verify.
            _hashed_string (str): The hashed string to compare against, formatted as 'algorithm$iterations$salt$hashed'.

        Returns:
            bool: True if the string matches the hashed string, False otherwise.
        """
        try:
            algorithm, iterations, salt, hashed = _hashed_string.split('$', 3)
            if algorithm != self.algorithm:
                return False
            dk: bytes = hashlib.pbkdf2_hmac(self.digest().name, _string.encode(), salt.encode(), int(iterations))
            hashed_input: str = binascii.hexlify(dk).decode('ascii')
            return hmac.compare_digest(hashed, hashed_input)
        except (ValueError, AssertionError):
            return False

    def needs_rehash(self, _hashed_string: str, /) -> bool:
        """
        Determines if a hashed string needs to be rehashed based on the number of iterations.

        Args:
            _hashed_string (str): The hashed string to check.

        Returns:
            bool: True if rehash is needed, False otherwise.
        """
        try:
            _, iterations, *_ = _hashed_string.split('$')
            return int(iterations) != self.iterations
        except ValueError:
            return False


class PBKDF2Sha1Hasher(PBKDF2Sha256Hasher):
    algorithm = "pbkdf2_sha1"
    digest = hashlib.sha1
