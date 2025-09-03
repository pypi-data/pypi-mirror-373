import os

from icschedule.models.user import User
from icschedule.models.task import Task
from icschedule.models.queue import Queue
from icschedule.models.resource import Resource

from icschedule.db import DbInterface
from icschedule.io.slurm_parser import SlurmInputParser


class Scheduler:
    def __init__(self, db_name="icschedule") -> None:
        self.models = [User, Queue, Resource, Task]
        self.db = DbInterface(db_name)
        self.slurm_parser = SlurmInputParser()
        self.default_queue_name = "default"

    def initialize_db(self):
        self.db.create_tables(self.models)

    def create_queue(self, name):
        queue = Queue()
        queue.name = self.default_queue_name
        queue.save(self.db)

    def enqueue(self, task_path, username=None):
        username = username
        if username is None:
            username = os.getlogin()
        task = self.slurm_parser.parse(task_path)
        task.user_name = username
        task.queue_name = self.default_queue_name
        print(task.serialize())
        # task.save(self.db)

    def cancel(self):
        pass

    def list_items(self):
        pass
