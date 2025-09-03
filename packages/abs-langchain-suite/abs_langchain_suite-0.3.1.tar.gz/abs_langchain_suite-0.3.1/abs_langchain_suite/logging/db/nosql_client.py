from .base import BaseDBClient


class NoSQLDBClient(BaseDBClient):
    def __init__(self, db):
        """
        Args:
            db: A pymongo/cosmos-compatible database object
        """
        self.db = db

    def write(self, table: str, data: dict):
        try:
            self.db[table].insert_one(data)
        except Exception as e:
            print(f"[NoSQL Error] Failed to log token usage: {e}")
