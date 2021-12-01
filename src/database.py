import os
from typing import List, Union

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from appdirs import AppDirs
from .basic_config import app_name, app_author, app_version, database_name, Base
from .datatypes import Rulegroup, Question, MultipleChoice


class DatabaseConnector:
    engine = None

    def __init__(self):
        dirs = AppDirs(appname=app_name, appauthor=app_author, version=app_version)
        database_path = os.path.join(dirs.user_data_dir, database_name)
        print(dirs.user_data_dir)
        self.initialized = True
        if not os.path.isdir(dirs.user_data_dir):
            os.makedirs(dirs.user_data_dir, )
            self.initialized = False
        elif not os.path.isfile(database_path):
            self.initialized = False
        self.engine = create_engine(f"sqlite+pysqlite:///{database_path}", future=True)
        if not inspect(self.engine).has_table(Rulegroup.__tablename__) or \
                not inspect(self.engine).has_table(Question.__tablename__) or \
                not inspect(self.engine).has_table(MultipleChoice.__tablename__):
            self.reset_database()

    def _init_database(self):
        # Create database based on basis - need to read docu first lol
        Base.metadata.create_all(self.engine)

    def __bool__(self):
        # check if database is empty :)
        return self.initialized

    def reset_database(self):
        Base.metadata.drop_all(self.engine)
        self.initialized = False

    def fill_database(self, dataset: List[Union[Rulegroup, Question, MultipleChoice]]):
        # insert processed values into db
        if not self.initialized:
            self._init_database()

        with Session(self.engine) as session:
            session.add_all(dataset)
            session.flush()
            session.commit()


db = DatabaseConnector()
