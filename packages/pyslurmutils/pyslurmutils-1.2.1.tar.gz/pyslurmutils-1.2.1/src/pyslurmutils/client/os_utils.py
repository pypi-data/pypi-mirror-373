import os
import logging
from typing import Generator
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def chmod(path: str, mode: int = 0o777) -> None:
    """
    Safely set permissions of `path`.
    """
    with _temporary_umask(0):
        try:
            os.chmod(path, mode)
        except Exception as exc:
            _log_path_warning(path, exc)


def makedirs(dirname: str, mode: int = 0o777) -> None:
    """
    Safely create directories recursively.
    """
    with _temporary_umask(0):
        try:
            os.makedirs(dirname, mode=mode, exist_ok=True)
        except Exception as exc:
            _log_path_warning(dirname, exc)


def nfs_cache_refresh(dirname) -> None:
    # _ = os.listdir(dirname)  # not enough
    # _ = subprocess.run(["ls", "-l", dirname], check=False, text=True, capture_output=True)
    try:
        with os.scandir(dirname) as it:
            for entry in it:
                _ = entry.stat()  # This forces a fresh stat call, similar to "ls -l"
    except Exception as exc:
        _log_path_warning(dirname, exc)


@contextmanager
def _temporary_umask(umask: int = 0) -> Generator[None, None, None]:
    """
    Context manager to temporarily set os.umask, restoring the original value afterward.
    """
    original_umask = None
    try:
        original_umask = os.umask(umask)
    except Exception as exc:
        logger.warning("Failed to set umask: %s", exc)
    try:
        yield
    finally:
        if original_umask is not None:
            try:
                os.umask(original_umask)
            except Exception as exc:
                logger.warning("Failed to restore umask: %s", exc)


def _log_path_warning(path: str, exc: Exception) -> None:
    """
    Log detailed information about a path when an operation on it fails.
    """
    try:
        path_exists = os.path.exists(path)
    except Exception as exists_e:
        logger.warning(
            "Failed operation on '%s': %s. Also failed to check if path exists: %s",
            path,
            exc,
            exists_e,
        )
        return

    if not path_exists:
        logger.warning("Failed operation on '%s': %s. Path does not exist.", path, exc)
        return

    try:
        st = os.stat(path)
        perms = oct(st.st_mode & 0o777)
        uid = st.st_uid
        gid = st.st_gid
        logger.warning(
            "Failed operation on '%s': %s. Path exists with permissions %s, UID %s, GID %s",
            path,
            exc,
            perms,
            uid,
            gid,
        )
    except Exception as stat_e:
        logger.warning(
            "Failed operation on '%s': %s. Also failed to stat existing path: %s",
            path,
            exc,
            stat_e,
        )
