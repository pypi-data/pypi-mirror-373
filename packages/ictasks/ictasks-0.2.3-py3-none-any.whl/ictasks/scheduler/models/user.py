from .fields import TextField, IntField
from .model import Model


class User(Model):
    _type = "user"
    _fields = [TextField("name", pk=True), IntField("last_contact", null_ok=False)]

    def __init__(self) -> None:
        super().__init__()
        self.name = ""
        self.last_contact = 0

    def save(self, db):
        columns = Model.get_db_columns(User)
        _ = f"INSERT INTO {User._type} ({columns}) VALUES"
        self.db.raw()
