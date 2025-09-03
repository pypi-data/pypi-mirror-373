import sqlite3

from icschedule.models.model import Model


class DbInterface:

    _table_create = "CREATE TABLE IF NOT EXISTS"

    def __init__(self, name) -> None:
        self.name = name
        self.con = None
        self.cur = None

    def connect(self):
        if self.con is None:
            # sqlite3.enable_callback_tracebacks(True)
            self.con = sqlite3.connect(f"{self.name}.db")
            self.cur = self.con.cursor()

    def create_tables(self, types):
        self.connect()
        for eachType in types:
            op = f"{DbInterface._table_create} {Model.get_db_schema(eachType)}"
            print(op)
            self.cur.execute(op)

    def raw(self, op):
        self.cur.execute(op)

    def upsert(self, model):
        pass

    def remove(self, model):
        pass

    def select_one(self, type, pid):
        pass

    def select(self, query):
        pass
