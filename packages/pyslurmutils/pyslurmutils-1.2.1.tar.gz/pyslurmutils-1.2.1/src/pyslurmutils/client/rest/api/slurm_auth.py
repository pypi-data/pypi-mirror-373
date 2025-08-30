import os
import shlex
import getpass
import subprocess
import datetime
import logging
from urllib.parse import urlparse, ParseResult
from typing import Optional, List

import jwt

from ... import url_utils
from ...errors import SlurmMissingParameterError
from ...errors import SlurmTokenInvalidError
from ...errors import SlurmTokenRenewalError
from ...errors import SlurmInvalidUrlError

logger = logging.getLogger(__name__)


class SlurmAuthManager:
    def __init__(
        self,
        user_name: Optional[str] = None,
        token: Optional[str] = None,
        renewal_url: Optional[str] = None,
        renewal_margin_seconds: int = 60,
        renewal_lifespan: int = 3600,
        renewal_timeout: int = 6,
        use_os_environment: bool = True,
    ):
        """
        Initializes the SLURM authentication manager.

        :param user_name: SLURM username (fallback to SLURM_USER or system user)
        :param token: SLURM JWT token (fallback to SLURM_TOKEN env)
        :param renewal_url: Url for SLURM JWT token renewal (fallback to SLURM_RENEWAL_URL env)
        :param renewal_margin_seconds: Time before expiry to trigger renewal
        :param renewal_lifespan: Requested lifespan in seconds for a new token
        :param renewal_timeout: Token renewal timeout in seconds
        :param use_os_environment: Use ``SLURM_*`` environment variables
        :raises SlurmTokenInvalidError:
        :raises SlurmInvalidUrlError:
        """
        self._use_os_environment = use_os_environment

        if not user_name and use_os_environment:
            user_name = os.environ.get("SLURM_USER")
        if not user_name:
            user_name = getpass.getuser()
        self._user_name = user_name.strip()

        if not token and use_os_environment:
            token = os.environ.get("SLURM_TOKEN")
        self._token = token

        if not renewal_url and use_os_environment:
            renewal_url = os.environ.get("SLURM_RENEWAL_URL")
        if renewal_url:
            self._renewal_url = _parse_renewal_url(renewal_url)
        else:
            self._renewal_url = None

        self._renewal_lifespan = renewal_lifespan
        self._renewal_margin_seconds = datetime.timedelta(
            seconds=renewal_margin_seconds
        )
        self._renewal_timeout = renewal_timeout

    @property
    def user_name(self) -> str:
        return self._user_name

    @property
    def _token(self) -> Optional[str]:
        return self.__token

    @_token.setter
    def _token(self, value: Optional[str]) -> None:
        """
        :raises SlurmTokenInvalidError:
        """
        if value is not None and not isinstance(value, str):
            raise TypeError(f"Token must be str or None, got {type(value).__name__}")
        if value:
            value = _parse_token(value)
            self.__token = value
            if self._use_os_environment:
                os.environ["SLURM_TOKEN"] = value
        else:
            self.__token = None
            if self._use_os_environment:
                _ = os.environ.pop("SLURM_TOKEN", None)

    def headers(self) -> dict:
        """
        Returns authentication headers for a SLURM request.

        If the current token is expired, a new token is retrieved automatically.

        :return: Dictionary containing authentication headers
        :raises SlurmTokenRenewalError:
        :raises SlurmTokenInvalidError:
        :raises SlurmMissingParameterError:
        """
        renewal_required = self._token_renewal_required()
        if renewal_required:
            self._token = self._create_new_token()
        self._raise_on_missing_token()
        return {
            "X-SLURM-USER-NAME": self._user_name,
            "X-SLURM-USER-TOKEN": self._token,
        }

    def retry_headers(self) -> Optional[dict]:
        """
        Returns authentication headers for a retry attempt on a SLURM request.

        Triggers token renewal if the token is close to expiring (within the configured margin).

        :return: Dictionary containing authentication headers, or None if the token is not renewed
        :raises SlurmTokenRenewalError:
        :raises SlurmTokenInvalidError:
        :raises SlurmMissingParameterError:
        """
        renewal_required = self._token_renewal_required(use_offset=True)
        if renewal_required:
            self._token = self._create_new_token()
            self._raise_on_missing_token()
            return {
                "X-SLURM-USER-NAME": self._user_name,
                "X-SLURM-USER-TOKEN": self._token,
            }
        return None

    def _token_renewal_required(self, use_offset: bool = False) -> bool:
        """
        Determines whether the current token should be renewed.

        :param use_offset: Use configured renewal_margin_seconds for early renewal
        :return: True if token should be renewed
        """
        if not self._token:
            return True

        try:
            payload = jwt.decode(self._token, options={"verify_signature": False})
        except jwt.DecodeError:
            return True

        exp = payload.get("exp")
        if not exp:
            return True

        expiry_time = datetime.datetime.fromtimestamp(exp).astimezone(
            datetime.timezone.utc
        )
        margin = self._renewal_margin_seconds if use_offset else datetime.timedelta(0)
        time_left = expiry_time - datetime.datetime.now(datetime.timezone.utc)
        expired = time_left <= margin
        if expired:
            logger.warning("SLURM token expired on %s", expiry_time)
        return expired

    def _create_new_token(self) -> str:
        """
        Attempts to renew the SLURM token (local first, then remote).

        :return: New token as a string
        :raises SlurmTokenRenewalError:
        :raises SlurmTokenInvalidError:
        :raises SlurmMissingParameterError:
        """
        new_token = self._create_new_token_local()
        if new_token:
            return new_token
        return self._create_new_token_ssh()

    def _create_new_token_local(self) -> Optional[str]:
        """
        Attempts to renew the token using local `scontrol`.

        :return: New token if successful, else None
        :raises SlurmTokenInvalidError:
        """
        cmd = self._renewal_command()
        return self._execute_renewal(cmd)

    def _create_new_token_ssh(self) -> str:
        """
        Attempts to renew the token via SSH to the configured renewal host.

        :return: New token if successful
        :raises SlurmTokenRenewalError:
        :raises SlurmTokenInvalidError:
        :raises SlurmMissingParameterError:
        """
        if not self._renewal_url:
            self._raise_on_missing_token()
            raise SlurmMissingParameterError(
                "SLURM token renewal failed: 'renewal_url' most be provided or set environment variable SLURM_RENEWAL_URL."
            )
        cmd = self._renewal_command()
        user = self._renewal_url.username or self._user_name
        destination = f"{user}@{self._renewal_url.hostname}"
        ssh_cmd = ["ssh", destination, "-p", str(self._renewal_url.port), " ".join(cmd)]
        return self._execute_renewal(
            ssh_cmd, timeout=self._renewal_timeout, raise_on_error=True
        )

    def _renewal_command(self) -> List[str]:
        """
        Constructs the `scontrol token` command.

        :return: List of command components
        """
        return [
            "scontrol",
            "token",
            f"username={self._user_name}",
            f"lifespan={self._renewal_lifespan}",
        ]

    def _execute_renewal(
        self, cmd: List[str], raise_on_error: bool = False, **kwargs
    ) -> Optional[str]:
        """
        Executes a command to retrieve a new SLURM token.

        :param cmd: Command as list of strings
        :param raise_on_error: Raise when failed
        :param kwargs: Additional subprocess parameters (e.g., timeout)
        :return: Parsed token if successful, else None
        :raises SlurmTokenInvalidError: If the renewal failed
        """
        s_cmd = shlex.join(cmd)
        try:
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, universal_newlines=True, **kwargs
            )
            if output:
                logger.info("Successfully renewed SLURM token via: %s", s_cmd)
                return output
        except Exception as ex:
            if raise_on_error:
                self._raise_on_missing_token()
                raise SlurmTokenRenewalError(
                    f"SLURM token renewal failed: {s_cmd}"
                ) from ex
        return None

    def _raise_on_missing_token(self):
        """
        :raises SlurmMissingParameterError:
        """
        if not self._token:
            raise SlurmMissingParameterError(
                "SLURM authentication failed: 'token' must be provided or set environment variable SLURM_TOKEN or SLURM_RENEWAL_URL."
            )


def _parse_token(token: str) -> str:
    """
    Cleans and validates a SLURM JWT token.

    :param token: Raw token string
    :return: Cleaned token string
    :raises SlurmTokenInvalidError:
    """
    result = token.strip().split("\n")[-1]
    result = result.replace("SLURM_JWT=", "")
    if not result:
        raise SlurmTokenInvalidError("Slurm token is empty.")
    try:
        jwt.decode(result, options={"verify_signature": False})
    except jwt.DecodeError:
        raise SlurmTokenInvalidError("SLURM token is invalid.") from None
    return result


def _parse_renewal_url(renewal_url: str, default_port: int = 22) -> ParseResult:
    """
    :raises SlurmInvalidUrlError:
    """
    parsed = urlparse(renewal_url)
    if parsed.scheme != "ssh":
        raise SlurmInvalidUrlError(
            f"Invalid SLURM renewal URL scheme: {parsed.scheme}. Expected 'ssh'."
        )

    if not parsed.hostname:
        raise SlurmInvalidUrlError("Missing hostname.")

    if parsed.port is None:
        return url_utils.set_url_port(parsed, default_port)

    return parsed
