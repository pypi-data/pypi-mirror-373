"""
Module to handle workers for running tasks on
"""

from pathlib import Path

from pydantic import BaseModel

from iccore.filesystem import read_file_lines
from iccore.base_models import Range
from iccore.system.cluster.node import ComputeNode
from icsystemutils.cpu import cpu_info
from icsystemutils.gpu import gpu_info


class Worker(BaseModel, frozen=True):
    """
    A worker or processor to run a task on. It has a unique identifier and
    an optional range of 'cores' that the task can run on.
    """

    id: int
    cores: Range
    gpus: Range | None


class Host(BaseModel, frozen=True):
    """
    A network location hosting workers, this can correspond to a cluster node
    or a single laptop
    """

    id: int
    node: ComputeNode
    workers: list[Worker] = []

    @property
    def address(self) -> str:
        return self.node.address


class TaskDistribution(BaseModel, frozen=True):
    """
    This is the task distribution on a host
    """

    cores_per_node: int = 0
    threads_per_core: int = 1
    cores_per_task: int = 1
    gpus_per_node: int = 0
    gpus_per_task: int = 0

    @property
    def num_procs(self) -> int:
        num_procs = (
            int(self.cores_per_node / self.cores_per_task) * self.threads_per_core
        )
        num_gpu_procs = (
            int(self.gpus_per_node / self.gpus_per_task) if self.gpus_per_task else 0
        )
        if num_gpu_procs != 0 and num_gpu_procs < num_procs:
            num_procs = num_gpu_procs
        return num_procs


def _get_core_range(proc_id: int, task_distribution: TaskDistribution) -> Range:
    start = (
        proc_id % task_distribution.cores_per_node * task_distribution.cores_per_task
    )
    end = start + task_distribution.cores_per_task - 1
    return Range(start=start, end=end)


def _get_gpu_range(proc_id: int, task_distribution: TaskDistribution) -> Range | None:
    if task_distribution.gpus_per_node == 0:
        return None
    start = proc_id % task_distribution.gpus_per_node * task_distribution.gpus_per_task
    end = start + task_distribution.gpus_per_task - 1
    return Range(start=start, end=end)


def _get_runtime_task_distribution(
    task_distribution: TaskDistribution,
) -> TaskDistribution:
    if task_distribution.cores_per_node == 0:
        cpu = cpu_info.read()
        cores_per_node = cpu.cores_per_node
        threads_per_core = cpu.threads_per_core
    else:
        cores_per_node = task_distribution.cores_per_node
        threads_per_core = task_distribution.threads_per_core

    if task_distribution.gpus_per_node == 0:
        gpu = gpu_info.read()
        gpus_per_node = len(gpu.physical_procs)
    else:
        gpus_per_node = task_distribution.gpus_per_node

    if gpus_per_node == 0 and task_distribution.gpus_per_task != 0:
        raise RuntimeError("There are no gpus available but they are needed for tasks")

    return TaskDistribution(
        cores_per_node=cores_per_node,
        threads_per_core=threads_per_core,
        cores_per_task=task_distribution.cores_per_task,
        gpus_per_node=gpus_per_node,
        gpus_per_task=task_distribution.gpus_per_task,
    )


def load(nodes: list[ComputeNode], task_distribution: TaskDistribution) -> list[Host]:
    """
    Given a collection of available compute nodes and a task distribution
    set up the worker collection
    """

    task_distribution = _get_runtime_task_distribution(task_distribution)
    return [
        Host(
            id=idx,
            node=node,
            workers=[
                Worker(
                    id=proc_id % task_distribution.num_procs,
                    cores=_get_core_range(proc_id, task_distribution),
                    gpus=_get_gpu_range(proc_id, task_distribution),
                )
                for proc_id in range(task_distribution.num_procs)
            ],
        )
        for idx, node in enumerate(nodes)
    ]


def read(path: Path, task_distribution: TaskDistribution) -> list[Host]:
    """
    Read the node configuration from file and with the given task
    distribution create a collection of workers
    """
    return load(
        [ComputeNode(address=line) for line in read_file_lines(path)], task_distribution
    )
