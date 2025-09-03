"""
This module is for a single batch job or session
"""

import logging
from pathlib import Path
import os
from queue import Queue, SimpleQueue
from typing import Callable
from functools import partial
from concurrent.futures import ProcessPoolExecutor

from iccore.serialization import read_yaml
from iccore.system.process import ProcessLauncher
from iccore.system.cluster.node import ComputeNode

import ictasks
import ictasks.task

from .config import Config
from .task import Task, get_task_dirname
from .worker import Host, Worker

logger = logging.getLogger(__name__)


HostWorker = tuple[Host, Worker]


def _on_task_finished(
    workers: SimpleQueue[HostWorker],
    tasks: Queue[Task],
    on_task_completed: Callable | None,
    task: Task,
    host_worker: HostWorker,
    pid: int,
    returncode: int,
):
    """
    This is called when a task is finished. We update the task and worker
    queues (which are thread safe) and if a user completion callback is provided
    we fire it.
    """

    tasks.task_done()
    workers.put(host_worker)

    logging.info("Task %s on pid %d finished with code %d", task.id, pid, returncode)

    if on_task_completed:
        on_task_completed(ictasks.task.on_finished(task, pid, returncode))


def _get_launch_command(config: Config, host: Host, worker: Worker, task: Task):
    if config.slurm_job:
        cmd = f"srun -env I_MPI_PIN_PROCESSOR_LIST {worker.cores.as_string()} -n"
        host_info = f"--host {host.address} {task.launch_cmd}"
        cmd += f"{config.task_distribution.cores_per_task} {host_info}"
        return cmd
    return task.launch_cmd


def _write_gpu_ids(worker: Worker, path: Path) -> None:
    if not worker.gpus:
        return
    with open(path / "gpu_ids.txt", "w", encoding="utf-8") as f:
        for i in range(worker.gpus.start, worker.gpus.end + 1):
            f.write(f"{i}\n")


def _launch_task(
    host_worker: HostWorker,
    launcher: ProcessLauncher,
    on_task_finished: Callable,
    work_dir: Path,
    config: Config,
    task: Task,
    on_task_launched: Callable | None,
):
    """
    Launch the task async on the allotted worker and host
    """

    # Write the pre-launch state to file
    ictasks.task.write(work_dir, task)

    task_dir = work_dir / get_task_dirname(task)

    host, worker = host_worker
    launched_task = ictasks.task.on_launched(task, host.id, worker.id)
    _write_gpu_ids(worker, task_dir)

    # Launch the task async, it will fire the provided callback when
    # finished
    proc = launcher.run(
        _get_launch_command(config, host, worker, task),
        task_dir,
        stdout_path=task_dir / config.stdout_filename,
        stderr_path=task_dir / config.stderr_filename,
        callback=partial(
            on_task_finished,
            launched_task,
            (host, worker),
        ),
    )

    if on_task_launched:
        launched_task.pid = proc.pid
        on_task_launched(launched_task)

    logger.info("Task %s launched with pid: %d", task.id, proc.pid)


def _setup_worker_queue(
    config: Config, nodes: list[ComputeNode]
) -> SimpleQueue[HostWorker]:
    """
    Find available workers, one per available processor across
    compute nodes and add them to a queue.
    """

    workers: SimpleQueue[tuple[Host, Worker]] = SimpleQueue()
    for host in ictasks.worker.load(nodes, config.task_distribution):
        for worker in host.workers:
            workers.put((host, worker))
    return workers


def _launch_func(task: Task):
    if task.launch_func:
        return task.launch_func(task)


def run_funcs(tasks: list[Task]):
    with ProcessPoolExecutor() as executor:
        running_tasks = [executor.submit(partial(_launch_func, t)) for t in tasks]
        for t in running_tasks:
            t.result()


def run(
    tasks: Queue[Task],
    work_dir: Path = Path(os.getcwd()),
    config: Config = Config(),
    nodes: list[ComputeNode] | None = None,
    on_task_launched: Callable | None = None,
    on_task_completed: Callable | None = None,
):
    """
    Run the session by iterating over all tasks and assigning them to waiting workers.
    :param config: The configuration for this run
    :param tasks: A queue populated with tasks to run
    :param nodes: Compute nodes to run tasks on, defaults to localhost if not provided
    :param work_dir: Directory to write output to
    :param on_task_launched: Callback fired when a task launches
    :param on_task_complete: Callback fired when a task completes
    """

    if not nodes:
        if config.slurm_job:
            nodes = [ComputeNode(address=a) for a in config.slurm_job.nodes]
        else:
            nodes = [ComputeNode(address="localhost")]

    workers = _setup_worker_queue(config, nodes)
    launcher = ProcessLauncher()

    logger.info("Starting with %d workers and %d tasks", workers.qsize(), tasks.qsize())
    while not tasks.empty():
        task = tasks.get()
        logger.info(
            "Launching task id: %s. %d remaining in queue.", task.id, tasks.qsize()
        )
        host_worker = workers.get()
        _launch_task(
            host_worker,
            launcher,
            partial(_on_task_finished, workers, tasks, on_task_completed),
            work_dir,
            config,
            task,
            on_task_launched,
        )

    logger.info("Task queue is empty. Waiting for running tasks to finish.")
    tasks.join()
    logger.info("Task queue is empty and all tasks finished, stopping run.")


def taskfarm(
    work_dir: Path,
    config_path: Path | None = None,
    tasklist: Path | None = None,
):
    """
    Run the session in taskfarm format using configurations from disk

    :param Path config_path: Path to the config file
    :param Path tasklist: Path to a file with the list of tasks
    :param Path workdir: Directory to run the session in
    """

    config_dict = read_yaml(config_path) if config_path else {}
    config = Config(**config_dict)
    # Prioritise using taskfile for task queue
    tasks = (
        ictasks.task.queue_from_taskfile(tasklist)
        if tasklist
        else ictasks.task.queue_from_list(config.tasks)
    )

    write_task_func = partial(ictasks.task.write, work_dir)

    ictasks.run(
        tasks=tasks,
        work_dir=work_dir,
        config=config,
        on_task_launched=write_task_func,
        on_task_completed=write_task_func,
    )
