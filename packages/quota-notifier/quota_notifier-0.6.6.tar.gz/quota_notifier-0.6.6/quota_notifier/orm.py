"""Object relational mapper for connecting to the application database.

Module Contents
---------------
"""

import logging
from typing import Callable, Optional

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, create_engine, func
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker, validates

Base = declarative_base()


class Notification(Base):
    """History of user notifications

    Fields:
      - id           (Integer): Primary key for this table
      - username      (String): Unique account name
      - threshold    (Integer): Disk usage threshold that triggered the notification
      - file_system   (String): Name of the file system triggering the notification
      - last_update (DateTime): Datetime of the last user notification
    """

    __tablename__ = 'notification'
    __table_args__ = (UniqueConstraint('username', 'file_system', sqlite_on_conflict='REPLACE'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    threshold = Column(Integer, nullable=False)
    file_system = Column(String, nullable=False)
    last_update = Column(DateTime, nullable=False, onupdate=func.now(), server_default=func.now())

    @validates('threshold')
    def validate_percent(self, key: str, value: int) -> int:
        """Verify the given value is between 0 and 100 (inclusive)

        Args:
            key: Name of the database column being tested
            value: The value to test

        Returns:
            The validated value

        Raises:
            ValueError: If the given value does not match required criteria
        """

        if 0 <= value <= 100:
            return value

        raise ValueError(f'Value for {key} column must be between 0 and 100 (got {value}).')


class DBConnection:
    """A configurable connection to the application database

    This class acts as the primary interface for connecting to the application
    database. Use the ``configure`` method to change the location of the
    underlying application database. Changes made via this class will
    propagate to the entire parent application.
    """

    url: str = None
    engine: Engine = None
    connection: Optional[Connection] = None
    _session_maker: Callable[[], Session] = None

    @classmethod
    def configure(cls, url: str) -> None:
        """Update the connection information for the underlying database

        Changes made here will affect the entire running application

        Args:
            url: URL information for the application database
        """

        logging.info(f'Configuring database URL: {url}')

        cls.url = url
        if cls.connection:
            cls.connection.close()

        cls.connection = None
        cls.engine = create_engine(cls.url)
        cls._session_maker = sessionmaker(cls.engine)

    @classmethod
    def session(cls) -> Session:
        """Connect to the database and return a new database session"""

        if cls.connection is None:
            cls.connection = cls.engine.connect()

        Base.metadata.create_all(cls.engine)
        return cls._session_maker()
