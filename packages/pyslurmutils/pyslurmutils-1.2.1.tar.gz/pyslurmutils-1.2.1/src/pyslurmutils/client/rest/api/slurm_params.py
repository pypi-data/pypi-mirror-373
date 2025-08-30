import datetime
from typing import Any, Dict, List, Tuple, Union, Optional

_VersionType = Tuple[int, int, int]


def coerce_parameters(version: _VersionType, parameters: dict) -> None:
    for key in ("time_limit", "time_minimum"):
        if key in parameters:
            parameters[key] = _timedelta_in_minutes(version, parameters[key])

    if "environment" in parameters:
        parameters["environment"] = _environment(version, parameters["environment"])

    for key in ("memory_per_cpu", "memory_per_node"):
        if key in parameters:
            parameters[key] = _memory_in_megabytes(version, parameters[key])

    for key in ("memory_per_tres",):
        if key in parameters:
            parameters[key] = _tres_memory_in_megabytes(version, parameters[key])


def _integral_number(
    version: _VersionType,
    number: Any,
    lower_bound: Optional[int] = None,
    invalid: Optional[int] = None,
) -> Any:
    """Convert a number into Slurm API dict format.
    For example "10.4", "10", 10.4 and 10 all result in 10.
    """
    if isinstance(number, str):
        try:
            number = int(number)
        except Exception:
            try:
                number = float(number)
            except Exception:
                return number

    if isinstance(number, float):
        number = int(round(number))

    if isinstance(number, int):
        if lower_bound is not None:
            number = max(number, lower_bound)
        return {"number": number, "set": number != invalid, "infinite": False}

    return number


def _timedelta_in_minutes(version: _VersionType, delta_time: Any) -> Any:
    """Convert a Slurm time limit string "HH:MM:SS" or number into minutes."""
    if isinstance(delta_time, str):
        try:
            hours, minutes, seconds = map(int, delta_time.split(":"))
            delta_time = (
                datetime.timedelta(
                    hours=hours, minutes=minutes, seconds=seconds
                ).total_seconds()
                / 60.0
            )
        except Exception:
            return delta_time

    if isinstance(delta_time, (int, float)):
        return _integral_number(version, delta_time, lower_bound=1)

    return delta_time


def _environment(
    version: _VersionType, env: Dict[str, Any]
) -> Union[Dict[str, str], List[str]]:
    """
    Convert environment dict into proper Slurm API format.
    - For version < 0.0.39 → dict {k: str(v)}
    - For version >= 0.0.39 → list of "KEY=VALUE" strings
    """
    if version < (0, 0, 39):
        return {k: str(v) for k, v in env.items()}
    return [f"{k}={v}" for k, v in env.items()]


def _memory_in_megabytes(version: _VersionType, mem: Any) -> Any:
    """Convert memory specification into Slurm dict format in MB.

    Accepts:

      - int/float (already MB)
      - str with unit suffix (e.g., "1G", "512M")
    """
    if version < (0, 0, 39):
        return mem

    if isinstance(mem, str):
        mem = _parse_mem_string(mem)

    if isinstance(mem, (int, float)):
        return _integral_number(version, mem, lower_bound=1)

    return mem


def _tres_memory_in_megabytes(version: _VersionType, tres_mem: Any) -> Any:
    """Convert TRES memory string into a semicolon-delimited string with MB values.

    Example:
      "gres/gpu:2G;gres/mic:512M" → "gres/gpu:2048;gres/mic:512"
    """
    if version < (0, 0, 39):
        return tres_mem
    if not isinstance(tres_mem, str):
        return tres_mem

    tres_map: Dict[str, int] = {}
    for part in tres_mem.replace(" ", "").split(";"):
        if not part:
            continue
        if ":" not in part:
            return tres_mem
        tres, mem = part.split(":", 1)
        number = max(1, int(round(_parse_mem_string(mem))))
        tres_map[tres] = tres_map.get(tres, 0) + number

    return ";".join(f"{k}:{v}" for k, v in tres_map.items())


def _parse_mem_string(mem: str) -> float:
    """Convert a memory string like '2T', '2G', '512M', '100K' to MB (float)."""
    s = mem.strip().upper()
    if not s:
        return 0.0

    if s.endswith("TB"):
        return float(s[:-2]) * 1024 * 1024
    if s.endswith("T"):
        return float(s[:-1]) * 1024 * 1024
    if s.endswith("GB"):
        return float(s[:-2]) * 1024
    if s.endswith("G"):
        return float(s[:-1]) * 1024
    if s.endswith("MB"):
        return float(s[:-2])
    if s.endswith("M"):
        return float(s[:-1])
    if s.endswith("KB"):
        return float(s[:-2]) / 1024
    if s.endswith("K"):
        return float(s[:-1]) / 1024
    return float(s)
