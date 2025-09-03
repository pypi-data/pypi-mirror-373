from .fields import IntField, TextField, ForeignKeyField
from .model import Model


class Task(Model):
    _type = "task"
    _fields = [
        IntField("id", pk=True),
        IntField("num_tasks", null_ok=False),
        TextField("command"),
        TextField("status"),
        TextField("job_name"),
        IntField("duration", null_ok=False),
        ForeignKeyField("queue", "TEXT", "queue", "name"),
        ForeignKeyField("user", "TEXT", "user", "name"),
    ]

    def __init__(self) -> None:
        self.id = None
        self.num_tasks = 1
        self.command = ""
        self.status = "unset"
        self.job_name = ""
        self.duration = 0
        self.queue_name = None
        self.user_name = None
        super().__init__()

    def serialize(self):
        return {
            "id": self.id,
            "num_tasks": self.num_tasks,
            "command": self.command,
            "status": self.status,
            "job_name": self.job_name,
            "duration": self.duration,
            "queue_name": self.queue_name,
            "user_name": self.user_name,
        }
