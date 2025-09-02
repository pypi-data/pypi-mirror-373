import re
from typing import Tuple
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError


class ArgonHashUtility:
    """
    ArgonHashUtility provides methods to hash and
    verify passwords using the PasswordHasher.
    """

    _ph = PasswordHasher()

    @classmethod
    def hash_value(cls, value: str) -> str:
        """
        Hash the value using the Argon2 PasswordHasher.
        """
        return cls._ph.hash(value)

    @classmethod
    def verify_value(cls, hashed_value: str, value: str) -> Tuple[bool, str | None]:
        """
        Verifies if the provided value matches the hashed value.

        Returns:
            Tuple(bool, str | None):
            - A boolean indicating whether the value is correct.
            - The new hashed value, if hash needs to be updated (rehash).
        """

        try:
            verified = cls._ph.verify(hashed_value, value)

            new_hash = None
            # Check if the hash needs to be updated (rehash)
            if verified and cls._ph.check_needs_rehash(hashed_value):
                new_hash = cls._ph.hash(value)

            return verified, new_hash
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False, None


argon_hasher = ArgonHashUtility()


def validate_strong_password(password: str) -> str:
    """
    Validates the given password based on the following criteria:
    - Must contain at least 1 lowercase letter.
    - Must contain at least 1 uppercase letter.
    - Must contain at least 1 digit.
    - Must contain at least 1 special character from (@, #, $).
    - Must be at least 8 characters long.
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least 1 lowercase letter")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least 1 uppercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least 1 digit")
    if not re.search(r"[@#$]", password):
        raise ValueError(
            "Password must contain at least 1 special character from (@, #, $)"
        )
    return password
