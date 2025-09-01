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
