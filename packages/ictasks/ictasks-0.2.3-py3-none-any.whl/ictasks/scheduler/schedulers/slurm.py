import os

from pydantic import BaseModel


class SlurmJob(BaseModel):
    id: str = ""
    nodes: list[str] = []


class SlurmInfo(BaseModel, frozen=True):

    job_id: str = ""
    job_nodelist: list[str] = []
    launch_node_ipaddr: str = ""
    nprocs: int = 1  # world size
    procid: int = 0  # myrank


def _parse_brackets(content: str) -> list[str]:
    first_idx = content.index("[")
    last_idx = content.index("]")

    prefix = content[:first_idx]
    bracket_internals = content[first_idx + 1 : last_idx]

    entries = []
    bracket_entries = bracket_internals.split(",")
    for bracket_entry in bracket_entries:
        if "-" in bracket_entry:
            start, end = bracket_entry.split("-")
            for idx in range(int(start), int(end) + 1):
                entries.append(prefix + str(idx))
        else:
            entries.append(prefix + bracket_entry)
    return entries


def _parse_nodelist(nodelist: str) -> list[str]:

    if not nodelist:
        return []

    entries = []
    in_brackets = False
    working = ""
    for c in nodelist:
        if c == "[":
            in_brackets = True
            working += c
        elif c == "]":
            in_brackets = False
            working += c
        elif c == "," and not in_brackets:
            entries.append(working)
            working = ""
        else:
            working += c
    if working:
        entries.append(working)

    nodes = []
    for entry in entries:
        if "[" in entry and "]" in entry:
            nodes.extend(_parse_brackets(entry))
        else:
            nodes.append(entry)
    return nodes


def get_slurm_info() -> SlurmInfo:
    return SlurmInfo(
        job_id=os.environ.get("SLURM_JOB_ID", ""),
        job_nodelist=_parse_nodelist(os.environ.get("SLURM_JOB_NODELIST", "")),
        launch_node_ipaddr=os.environ.get("SLURM_LAUNCH_NODE_IPADDR", ""),
        nprocs=int(os.environ.get("SLURM_NPROCS", 1)),
        procid=int(os.environ.get("SLURM_PROCID", 0)),
    )


def load_job(nodelist: str = "") -> SlurmJob:

    info = get_slurm_info()
    if not nodelist:
        nodes = info.job_nodelist
    else:
        nodes = _parse_nodelist(nodelist)

    return SlurmJob(id=info.job_id, nodes=nodes)
