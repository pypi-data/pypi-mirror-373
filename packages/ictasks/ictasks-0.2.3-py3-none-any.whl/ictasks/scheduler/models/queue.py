from .fields import TextField


class Queue:
    _type = "queue"
    _fields = [TextField("name", pk=True)]

    def __init__(self) -> None:
        super().__init__()
