from .fields import TextField, ForeignKeyField
from .model import Model


class Resource(Model):
    _type = "resource"
    _fields = [
        TextField("name", pk=True),
        ForeignKeyField("queue", "TEXT", "queue", "name"),
    ]

    def __init__(self) -> None:
        super().__init__()
