import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Tuple


class DB:
    def __init__(self, db_url: str):
        """
        Initializes the DB class with the provided database configuration.

        :param db_url: The database URL (e.g., postgresql://user:password@localhost/dbname).
        """
        self.engine = create_engine(db_url, pool_size=20, max_overflow=100)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

    def init_db_connection(self) -> Tuple[create_engine, sessionmaker]:
        """
        Initializes the database connection and returns the engine and session maker.

        :return: A tuple containing the SQLAlchemy engine and session maker.
        """
        logging.info("Database connection initialized successfully.")
        return self.engine, self.SessionLocal

    def create_tables(self):
        """
        Creates all tables stored in declarative Base.
        """
        logging.info("Creating tables...")
        self.Base.metadata.create_all(bind=self.engine)
        logging.info("Tables created successfully.")

    def close_session(self):
        """
        Closes the database session.
        """
        self.SessionLocal.remove()
        logging.info("Session closed successfully.")
