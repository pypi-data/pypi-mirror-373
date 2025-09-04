import jwt
import uuid
from datetime import datetime, timedelta, timezone
from getpass import getpass
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session

from aps_common_toolkit.utils import argon_hasher


class UserService:
    """
    Service class for user-related operations.
    """

    def __init__(self, db: Session, model: Any):
        self._db = db
        self._model = model

    def create_user(self, data: Dict[str, Any]) -> None:
        """
        Create a new user in the database.
        """
        if "confirm_password" in data:
            data.pop("confirm_password")
        data["password"] = argon_hasher.hash_value(data["password"])
        user = self._model(**data)
        self._db.add(user)
        self._db.commit()

    def get_user_by_email(self, email: str):
        """
        Retrieve a user by email.
        """
        user = self._db.query(self._model).filter_by(email=email).first()
        return user

    def get_user_by_id(self, id: int):
        """
        Retrieve a user  by ID.
        """
        user = self._db.query(self._model).filter_by(id=id).first()
        return user

    def user_exists(self, email: str) -> bool:
        """
        Check if a user exists in the database.
        """
        return self.get_user_by_email(email) is not None

    def create_superuser(self):
        """
        Create a superuser with predefined credentials.
        """
        name: str = input("Enter name: ")
        email: str = input("Enter email: ")
        password: str = getpass("Enter password: ")
        confirm_password: str = getpass("Confirm password: ")

        if password != confirm_password:
            raise ValueError("The two passwords do not match.")

        superuser_data = {  # type: ignore
            "name": name,
            "email": email,
            "password": password,
            "is_superuser": True,
            "is_staff": True,
            "is_active": True,
        }
        self.create_user(superuser_data)  # type: ignore


class JWTService:
    """
    Service class for handling JSON Web Tokens (JWT).
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str | None = None,
        access_token_lifetime: timedelta | None = None,
        refresh_token_lifetime: timedelta | None = None,
    ):
        """
        Initialize the JWTService with a secret key and algorithm.
        """
        self._secret_key = secret_key
        self._algorithm = algorithm or "HS256"
        self._access_token_lifetime = access_token_lifetime or timedelta(minutes=15)
        self._refresh_token_lifetime = refresh_token_lifetime or timedelta(days=1)

    def __token_expiration_time(
        self, is_refresh: bool, lifetime: timedelta | None
    ) -> timedelta:
        """
        Returns the expiration time for the token.
        """
        if lifetime:
            return lifetime

        if is_refresh:
            return self._refresh_token_lifetime
        return self._access_token_lifetime

    def create_token(
        self,
        data: Dict[str, Any],
        is_refresh: bool = False,
        lifetime: timedelta | None = None,
    ) -> str | Tuple[str, str]:
        """
        Creates a JWT token for user.

        Arguments:
            - `data` - The payload data to include in the token.
            - `expires_in_minutes` - The expiration time in minutes for the token.

        Returns:
            - `payload` - The JWT payload (dict).
            - `jti` - The unique identifier (JTI) for the token.
        """
        now = datetime.now(timezone.utc)
        jti = str(uuid.uuid4())

        payload: Dict[str, Any] = {
            "data": data,
            "iat": now,
            "exp": now + self.__token_expiration_time(is_refresh, lifetime),
            "jti": jti,
            "refresh": is_refresh,
        }
        token = jwt.encode(  # type: ignore
            payload=payload, key=self._secret_key, algorithm=self._algorithm
        )
        if is_refresh:
            return token, jti
        return token

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodes the JWT token and return the payload.
        """
        payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])  # type: ignore
        return payload
