import shutil
from functools import partial

from iccore.serialization import read_yaml
from iccore.test_utils import get_test_output_dir, get_test_data_dir
from iccore.system.process import run_async

from icsystemutils.gpu import gpu_info

import ictasks
from ictasks import Config
import ictasks.task


def test_gpu():
    gpu = gpu_info.read()
    if len(gpu.physical_procs) == 0:
        return

    work_dir = get_test_output_dir()
    config_path = get_test_data_dir() / "gpu_config.yaml"

    config_dict = read_yaml(config_path)
    for task in config_dict["tasks"]:
        task["launch_cmd"] = task["launch_cmd"].replace(
            "<test_path>", f"{str(get_test_data_dir().parent)}"
        )
    config = Config(**config_dict)
    tasks = ictasks.task.queue_from_list(config.tasks)
    write_task_func = partial(ictasks.task.write, work_dir)
    cmd = f"python3 {get_test_data_dir().parent / "mocks" / "gpu_monitor.py"}"
    run_async(cmd=cmd)
    ictasks.run(
        tasks=tasks,
        work_dir=work_dir,
        config=config,
        on_task_launched=write_task_func,
        on_task_completed=write_task_func,
    )

    shutil.rmtree(work_dir)
