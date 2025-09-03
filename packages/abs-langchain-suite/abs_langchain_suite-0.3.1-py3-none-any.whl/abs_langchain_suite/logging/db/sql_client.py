from .base import BaseDBClient
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


class SQLDBClient(BaseDBClient):
    def __init__(self, session: Session, model_class):
        self.session = session
        self.model_class = model_class

    def write(self, table: str, data: dict):
        try:
            record = self.model_class(**data)
            self.session.add(record)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"[SQL Error] Failed to log token usage: {e}")
