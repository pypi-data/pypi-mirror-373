import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any


class DatabaseService:
    """
    Database connection manager using SQLAlchemy.
    """

    def __init__(self, **engine_kwargs: Dict[str, Any]):
        config: Dict[str, Any] = self.__load_config()
        # create the database engine
        self._engine = create_engine(config.pop("url"), **config, **engine_kwargs)
        # create a configured "Session" class
        self._SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    def __load_config(self) -> Dict[str, Any]:
        """
        Load database configuration from environment variables.
        """
        return {
            "url": os.getenv("DB_URI"),
            "max_overflow": self.__parse_env("DB_MAX_OVERFLOW", 20, int),
            "pool_size": self.__parse_env("DB_POOL_SIZE", 10, int),
            "pool_pre_ping": True,
            "pool_timeout": self.__parse_env("DB_POOL_TIMEOUT", 30, float),
            "pool_recycle": self.__parse_env("DB_POOL_RECYCLE", 1800, int),
        }

    def __parse_env(self, name: str, default: int, value_type: type) -> int:
        try:
            return value_type(os.getenv(name, default))
        except (ValueError, TypeError):
            return default

    @contextmanager
    def db_session(self):
        """
        Context manager for database session.
        """
        db = self._SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @property
    def db_engine(self):
        """
        Get the database engine.
        """
        return self._engine
