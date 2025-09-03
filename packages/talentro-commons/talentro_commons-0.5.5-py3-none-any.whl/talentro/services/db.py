import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from ..util.singleton import SingletonMeta


class DB(metaclass=SingletonMeta):

    def __init__(self):
        print(f"  DB - Initializing...")

        username = os.environ.get('POSTGRES_USER')
        password = os.environ.get('POSTGRES_PASSWORD')
        host = os.environ.get('POSTGRES_HOST')
        port = os.environ.get('POSTGRES_PORT')
        db = os.environ.get('POSTGRES_DB')

        self.sqlite_url = f"postgresql://{username}:{password}@{host}:{port}/{db}"

        self.engine = create_engine(self.sqlite_url)

    def get_session(self):
        with Session(self.engine) as session:
            yield session

    SessionDep = Annotated[Session, Depends(get_session)]
