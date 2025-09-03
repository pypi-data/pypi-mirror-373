class Field:
    def __init__(self, name, pk=False, null_ok=True) -> None:
        self.name = name
        self.is_primary_key = pk
        self.type: str | None = None
        self.null_ok = null_ok

    def db(self):
        ret = f"{self.name} {self.type}"
        if self.is_primary_key:
            ret += " PRIMARY KEY"
        if not self.null_ok:
            ret += " NOT NULL"
        return ret

    def db_refs(self):
        return None


class IntField(Field):
    def __init__(self, name, pk=False, null_ok=True) -> None:
        super().__init__(name, pk, null_ok)
        self.type = "INT"


class TextField(Field):
    def __init__(self, name, pk=False, null_ok=True) -> None:
        super().__init__(name, pk, null_ok)
        self.type = "TEXT"


class ForeignKeyField(Field):
    def __init__(self, name, type, foreign_type, foreign_id) -> None:
        super().__init__(name, False)
        self.foreign_id = foreign_id
        self.type = type
        self.foreign_type = foreign_type

    def db(self):
        return f"{self.name} {self.type}"

    def db_refs(self):
        ref_str = "{self.foreign_type}({self.foreign_id})"
        return f" FOREIGN KEY ({self.name}) REFERENCES {ref_str}"
