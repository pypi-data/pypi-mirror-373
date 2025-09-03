from pathlib import Path

import iccore.filesystem as fs
from iccore.test_utils import get_test_data_dir

from ictasks.scheduler.schedulers import slurm


def test_slurm_reader():
    pass


def test_slurm_job():
    nodelist_path = get_test_data_dir() / "sample_nodelist.dat"

    job = slurm.load_job(fs.read_file(nodelist_path))
    assert len(job.nodes) == 12
