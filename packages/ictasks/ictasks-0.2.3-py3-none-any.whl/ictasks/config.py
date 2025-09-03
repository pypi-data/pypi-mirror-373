"""
Module for session configuration
"""

import uuid

from pydantic import BaseModel

from .worker import TaskDistribution
from .scheduler.schedulers import slurm
from .scheduler.schedulers.slurm import SlurmJob
from .stopping_condition import StoppingCondition


class Config(BaseModel):
    """This is the configuration for a task running session

    :param str job_id: An identifier for the session,
    can be the Slurm job id for example.
    :param TaskDistribution task_distribution: The distribution of tasks on
    available resources
    :param list[StroppingCondition] stopping_conditions: Conditions for the
    session to stop
    :param bool stop_on_error: Whether to stop on error
    :param str stdout_filename: The name of the stdout file
    :param str stderr_filename: The name of the stderr file
    :param SlurmJob slurm_job: An optional associated slurm job
    """

    job_id: str = ""
    task_distribution: TaskDistribution = TaskDistribution(
        cores_per_node=0,
        threads_per_core=1,
        cores_per_task=1,
        gpus_per_node=0,
        gpus_per_task=0,
    )
    stopping_conditions: list[StoppingCondition] = []
    stop_on_error: bool = True
    stdout_filename: str = "task_stdout.txt"
    stderr_filename: str = "task_stderr.txt"
    check_slurm: bool = False
    slurm_job: SlurmJob | None = None
    tasks: list = []

    def model_post_init(self, __context):
        if self.check_slurm:
            info = slurm.get_slurm_info()
            if not self.slurm_job and info.job_id:
                self.slurm_job = SlurmJob(id=info.job_id)

        if not self.job_id:
            if self.slurm_job:
                self.job_id = self.slurm_job.id
            else:
                self.job_id = str(uuid.uuid4().hex)
