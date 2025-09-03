import shutil
import queue
from functools import partial

from iccore.test_utils import get_test_output_dir, get_test_data_dir

import ictasks
import ictasks.task
from ictasks.task import Task


def test_basic_tasks_session():

    work_dir = get_test_output_dir()

    task_queue = queue.Queue()
    task_queue.put(Task(id="0", launch_cmd="echo 'hello from task 0'"))
    task_queue.put(Task(id="1", launch_cmd="echo 'hello from task 1'"))

    write_task_func = partial(ictasks.task.write, work_dir)

    ictasks.run(
        task_queue,
        work_dir,
        on_task_launched=write_task_func,
        on_task_completed=write_task_func,
    )

    shutil.rmtree(work_dir)


def test_function_tasks_session():

    work_dir = get_test_output_dir()
    write_task_func = partial(ictasks.task.write, work_dir)

    tasks = [
        Task(id="0", launch_func=write_task_func),
        Task(id="1", launch_func=write_task_func),
    ]

    ictasks.run_funcs(tasks)

    shutil.rmtree(work_dir)


def test_taskfarm_using_config():

    work_dir = get_test_output_dir()
    config = get_test_data_dir() / "sample_config.yaml"
    ictasks.taskfarm(config_path=config, work_dir=work_dir)
    for dir in work_dir.iterdir():
        with open(dir / "task_stdout.txt", "r", encoding="utf-8") as f:
            for line in f:
                assert "task 0" in line or "task 1" in line

    shutil.rmtree(work_dir)


def test_taskfarm_using_tasklist():

    work_dir = get_test_output_dir()
    config = get_test_data_dir() / "sample_config.yaml"
    tasklist = get_test_data_dir() / "tasklist.dat"
    ictasks.taskfarm(config_path=config, tasklist=tasklist, work_dir=work_dir)
    for dir in work_dir.iterdir():
        with open(dir / "task_stdout.txt", "r", encoding="utf-8") as f:
            for line in f:
                assert "task 1" in line or "task 2" in line

    shutil.rmtree(work_dir)
