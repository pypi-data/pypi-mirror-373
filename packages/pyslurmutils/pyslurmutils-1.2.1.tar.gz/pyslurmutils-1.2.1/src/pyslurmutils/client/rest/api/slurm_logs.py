import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

from pydantic import BaseModel


@dataclass
class StdInfo:
    """Information about a SLURM job stdout/stderr log file"""

    name: str
    filename: Optional[str]
    content: Optional[List[str]]

    def lines(self) -> List[str]:
        title = f"{self.name}: {self.filename}\n"
        line = "-" * len(title) + "\n"
        if self.content is None:
            return [title, line, " <not found>"]
        if not self.content:
            return [title, line, " <empty>"]
        return [title, line] + self.content


def read_slurm_log(
    job_properties: BaseModel, stderr: bool = False
) -> Tuple[Optional[str], Optional[List[str]]]:
    if stderr:
        filename = job_properties.standard_error
    else:
        filename = job_properties.standard_output
    filename = slurm_log_filename(job_properties, filename)
    if not filename:
        return None, None
    try:
        with open(filename) as f:
            return filename, list(f)
    except FileNotFoundError:
        return None, None


def remove_slurm_log(job_properties: BaseModel, stderr: bool = False) -> None:
    if stderr:
        filename = job_properties.standard_error
    else:
        filename = job_properties.standard_output
    filename = slurm_log_filename(job_properties, filename)
    if not filename or filename == "/dev/null":
        return
    try:
        os.remove(filename)
    except (FileNotFoundError, PermissionError):
        pass


def get_stdout_stderr(job_properties: BaseModel) -> Tuple[StdInfo, Optional[StdInfo]]:
    if (
        not job_properties.standard_error
        or job_properties.standard_output == job_properties.standard_error
    ):
        ofilename, ocontent = read_slurm_log(job_properties, stderr=False)
        std = StdInfo(name="STDOUT/STDERR", filename=ofilename, content=ocontent)
        return std, None

    ofilename, ocontent = read_slurm_log(job_properties, stderr=False)
    efilename, econtent = read_slurm_log(job_properties, stderr=True)
    stdout = StdInfo(name="STDOUT", filename=ofilename, content=ocontent)
    stderr = StdInfo(name="STDERR", filename=efilename, content=econtent)
    return stdout, stderr


def slurm_log_filename(
    job_properties: BaseModel, filename: Optional[str]
) -> Optional[str]:
    if filename:
        return filename.replace("%j", str(job_properties.job_id))
