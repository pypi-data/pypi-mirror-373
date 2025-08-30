import importlib
from typing import List, Tuple
import tblib


SerializedException = List[Tuple[str, str, str, bool]]


class RemoteError(Exception):
    pass


class RemoteExit(RemoteError):
    pass


class RemoteSlurmError(RemoteError):
    pass


class RemoteHttpError(RemoteError):
    pass


class SlurmAccessError(Exception):
    pass


class SlurmMissingParameterError(SlurmAccessError):
    pass


class SlurmInvalidUrlError(SlurmAccessError):
    pass


class SlurmTokenInvalidError(SlurmAccessError):
    pass


class SlurmTokenRenewalError(SlurmAccessError):
    pass


def raise_chained_errors(errors: List[Exception]) -> None:
    if not errors:
        return
    if len(errors) == 1:
        raise errors[0]

    try:
        raise_chained_errors(errors[:-1])
    except Exception as e:
        raise errors[-1] from e


def remote_exception_from_tb(exc_info: List[Tuple[str, str, str, bool]]) -> Exception:
    if not exc_info:
        raise ValueError("No exception information provided")
    exc_top = None
    exc_prev = None
    for exc_class_string, exc_message, exc_tb_string, cause in exc_info:
        exc = _exception_from_tb(exc_class_string, exc_message, exc_tb_string)
        if exc_top is None:
            exc_top = exc
            assert cause is None
        else:
            if cause:
                exc_prev.__cause__ = exc
            else:
                exc_prev.__context__ = exc
        exc_prev = exc
    return exc_top


def _exception_from_tb(
    exc_class_string: str, exc_message: str, exc_tb_string: str
) -> Exception:
    module_name, _, class_name = exc_class_string.rpartition(".")

    try:
        mod = importlib.import_module(module_name)
        exc_class = getattr(mod, class_name)
    except (ImportError, AttributeError):
        exc_class = RemoteError

    try:
        exc = exc_class(exc_message)
    except Exception:
        exc = RemoteError(exc_message)

    # We don't want to return a BaseException.
    # A remote BaseException is most likely a job timeout (KeyboardInterrupt for SLURM)
    if not issubclass(exc_class, Exception):
        exc = RemoteExit(exc_message)

    try:
        tb = tblib.Traceback.from_string(exc_tb_string).as_traceback()
    except Exception:
        tb = None

    return exc.with_traceback(tb)


def reraise_remote_exception_from_tb(exc_info: SerializedException) -> None:
    raise remote_exception_from_tb(exc_info)
