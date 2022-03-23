import logging
import os
from typing import List, Union

from appdirs import AppDirs
from sqlalchemy import create_engine, inspect, func, select
from sqlalchemy.orm import Session

from .basic_config import app_name, app_author, database_name, Base
from .datatypes import Rulegroup, Question, MultipleChoice


class DatabaseConnector:
    engine = None

    def __init__(self):
        dirs = AppDirs(appname=app_name, appauthor=app_author)
        database_path = os.path.join(dirs.user_data_dir, database_name)
        logging.debug(dirs.user_data_dir)
        self.initialized = True
        if not os.path.isdir(dirs.user_data_dir):
            os.makedirs(dirs.user_data_dir, )
            self.initialized = False
        elif not os.path.isfile(database_path):
            self.initialized = False
        self.engine = create_engine(f"sqlite+pysqlite:///{database_path}?check_same_thread=False", future=True)
        if not inspect(self.engine).has_table(Rulegroup.__tablename__) or \
                not inspect(self.engine).has_table(Question.__tablename__) or \
                not inspect(self.engine).has_table(MultipleChoice.__tablename__):
            self.clear_database()

        if not self.initialized:
            self._init_database()

    def _init_database(self):
        # Create database based on basis - need to read docu first lol
        Base.metadata.create_all(self.engine)

    def __bool__(self):
        # check if database is empty :)
        return self.initialized

    def clear_database(self):
        Base.metadata.drop_all(self.engine)
        self.initialized = False

    def get_rulegroups(self):
        with Session(self.engine, expire_on_commit=False) as session:
            rulegroups = session.query(Rulegroup)
            session.close()
        return rulegroups

    def get_question_multiplechoice(self):
        return_dict = []
        with Session(self.engine, expire_on_commit=False) as session:
            for question in session.query(Question):
                return_dict += [(question, session.query(MultipleChoice).where(MultipleChoice.rule == question).all())]
        return return_dict

    def update_question_set(self, question: Question, mchoice: List[MultipleChoice]):
        with Session(self.engine) as session:
            session.add(question)
            question.multiple_choice = mchoice
            session.commit()
            signature = question.signature
            session.close()
        return signature

    def get_question_by_primarykey(self, signature: str):
        with Session(self.engine, expire_on_commit=False) as session:
            question = session.query(Question).where(Question.signature == signature).first()
            session.close()
        return question

    def get_rulegroup_by_primarykey(self, rulegroup_index: int):
        with Session(self.engine, expire_on_commit=False) as session:
            rulegroup = session.query(Rulegroup).where(Rulegroup.id == rulegroup_index).first()
            session.close()
        return rulegroup

    def get_questions_by_foreignkey(self, rulegroup_id: int, mchoice=None, randomize: bool = False):
        with Session(self.engine, expire_on_commit=False) as session:
            questions = session.query(Question).where(Question.group_id == rulegroup_id)
            if mchoice is not None:
                if mchoice:
                    questions = questions.where(Question.answer_index != -1)
                else:
                    questions = questions.where(Question.answer_index == -1)
            if randomize:
                questions = questions.order_by(func.random())
            session.close()
        return questions

    def get_multiplechoice_by_foreignkey(self, question_signature: str):
        with Session(self.engine, expire_on_commit=False) as session:
            mchoice = session.query(MultipleChoice).where(MultipleChoice.rule_signature == question_signature).all()
            session.close()
        return mchoice

    def fill_database(self, dataset: List[Union[Rulegroup, Question, MultipleChoice]]):
        # insert processed values into db
        if not self.initialized:
            self._init_database()

        with Session(self.engine) as session:
            session.add_all(dataset)
            session.commit()
            session.close()

    def delete(self, item: Union[Rulegroup, Question]):
        with Session(self.engine) as session:
            session.delete(item)
            session.commit()
            session.close()

    def get_new_question_id(self, rulegroup_index: int):
        with Session(self.engine) as session:
            stmt = select(Question.rule_id).where(Question.group_id.like(rulegroup_index))
            return_val = max(session.execute(stmt))[0] + 1
            session.close()
        return return_val


db = DatabaseConnector()
