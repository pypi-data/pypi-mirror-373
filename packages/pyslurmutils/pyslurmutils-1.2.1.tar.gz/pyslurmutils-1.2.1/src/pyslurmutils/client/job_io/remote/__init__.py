"""Remote execution: remote code declared on the client side with pure python builtins"""

from functools import lru_cache

try:
    from importlib.resources import files as resource_files
except ImportError:
    from importlib_resources import files as resource_files

# For testing: execute remote main locally
from ._tcp import main as tcp_main  # noqa F401
from ._file import main as file_main  # noqa F401


@lru_cache(3)
def remote_script(name: str) -> str:
    package, *parts = __name__.split(".")
    filename = resource_files(package)
    for part in parts:
        filename /= part
    filename /= f"_{name}.py"

    with open(filename, "r") as file:
        file_content = "".join(
            [s for s in file.readlines() if not s.startswith("from ._base")]
        )

    if name == "base":
        return file_content

    base = remote_script("base")
    return "".join([base, file_content, "\n", "main()", "\n"])
