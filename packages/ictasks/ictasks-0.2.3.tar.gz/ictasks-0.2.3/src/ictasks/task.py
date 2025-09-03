"""
This module describes a task, i.e. a small unit of work
"""

import queue
from uuid import uuid4
from pathlib import Path
from typing import Callable
import time

from pydantic import BaseModel, Field

from iccore.filesystem import read_file, get_dirs
from iccore.serialization import read_json, write_model
from iccore.string_utils import split_strip_lines


class Task(BaseModel):
    """
    This is a computational task executed as a process with a launch command.
    :param id: An identifier for the task
    :param launch_cmd: The command to launch the task as a process
    :param state: The current state of the task
    :param return_code: The return code from the task process.
    :param launch_time: The time the process was launched at
    :param finish_time: The time the process finished at
    :param worker_id: Identifier of the worker the task ran on
    :param host_id: Identifier of the host the task ran on
    :param pid: Identifier for the task process
    """

    id: str = Field(default_factory=lambda: str(uuid4().hex))
    launch_cmd: str = ""
    launch_func: Callable | None = Field(default=None, exclude=True)
    state: str = "created"
    return_code: int = 0
    launch_time: float = Field(default=0.0, ge=0.0)
    finish_time: float = Field(default=0.0, ge=0.0)
    worker_id: int = -1
    host_id: int = -1
    pid: int = Field(default=0, ge=0)

    @property
    def finished(self) -> bool:
        return self.state == "finished"

    @property
    def running(self) -> bool:
        return self.state == "running"


def on_finished(task: Task, pid: int, return_code: int) -> Task:
    return Task(
        pid=pid,
        return_code=return_code,
        state="finished",
        finish_time=time.time(),
        id=task.id,
        launch_cmd=task.launch_cmd,
        launch_func=task.launch_func,
        launch_time=task.launch_time,
        worker_id=task.worker_id,
        host_id=task.host_id,
    )


def on_launched(task: Task, host_id: int, worker_id: int) -> Task:
    return Task(
        host_id=host_id,
        worker_id=worker_id,
        launch_time=time.time(),
        state="running",
        pid=task.pid,
        return_code=task.return_code,
        finish_time=task.finish_time,
        id=task.id,
        launch_cmd=task.launch_cmd,
        launch_func=task.launch_func,
    )


def get_task_dirname(task: Task) -> Path:
    """
    Get the task's directory name as a Path
    """
    return Path(f"task_{task.id}")


def write(path: Path, task: Task, filename: str = "task.json"):
    """
    Write the task to file
    """
    write_model(task, path / get_task_dirname(task) / filename)


def read(path: Path, filename: str = "task.json") -> Task:
    """
    Read a task from the given path
    """
    return Task(**read_json(path / filename))


def read_all(path: Path) -> list[Task]:
    """
    Read all tasks in a given directory
    """
    return [read(eachDir) for eachDir in get_dirs(path, "task_")]


def load_taskfile(content: str) -> list[Task]:
    """
    Load tasks from a string, with one launch command per line.
    The string %TASKNUM% will be replaced with the task id.
    """
    lines = split_strip_lines(content)
    return [
        Task(id=str(idx), launch_cmd=lines[idx].replace("%TASKID%", str(idx)))
        for idx in range(len(lines))
    ]


def read_taskfile(path: Path) -> list[Task]:
    """
    Read tasks from a file, with one launch command per line.
    """
    return load_taskfile(read_file(path))


def queue_from_taskfile(path: Path) -> queue.Queue:
    """
    Create a task queue from the provided taskfile
    """
    task_queue: queue.Queue = queue.Queue()
    for task in read_taskfile(path):
        task_queue.put(task)
    return task_queue


def to_str(task: Task, attributes: list[str] | None) -> str:
    """
    Convert a task to a string. If attributes are given only serialize those
    instance attributes
    TODO: This should use Pydantic filtering instead
    """
    if attributes:
        return "".join(f"{key}: {getattr(task, key)}\n" for key in attributes)
    return str(task)


def tasks_to_str(tasks: list[Task], attributes: list[str] | None) -> str:
    """
    Convert a list of tasks to a string. If attributes are given only serialize
    those task attributes.
    """
    return "".join(to_str(t, attributes) + "\n" for t in tasks)


def queue_from_list(config_task_list: list) -> queue.Queue:
    """
    Create a task queue from the provided config list of tasks
    """
    task_queue: queue.Queue = queue.Queue()
    for task_dict in config_task_list:
        task_queue.put(Task(**task_dict))
    return task_queue


def get_gpu_ids(task_dir: Path) -> list:
    """
    Get a list of gpu ids that are available to the task.
    This is done via the gpu_ids.txt file which has one gpu id per line,
    this file is automatically created in task directories in taskfarm.
    """
    with open(task_dir / "gpu_ids.txt", "r", encoding="utf-8") as f:
        return [int(line.strip()) for line in f]
