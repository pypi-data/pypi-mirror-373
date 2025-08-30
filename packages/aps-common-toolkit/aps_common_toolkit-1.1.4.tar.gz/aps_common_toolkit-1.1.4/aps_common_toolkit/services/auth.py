from getpass import getpass
from typing import Dict, Any
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
