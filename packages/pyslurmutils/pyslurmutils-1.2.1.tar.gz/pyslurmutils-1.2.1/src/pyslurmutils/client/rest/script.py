"""SLURM API to submit, cancel and monitor scripts"""

from typing import Optional, Union, Sequence

from .base import SlurmBaseRestClient
from .. import defaults


class SlurmScriptRestClient(SlurmBaseRestClient):
    """SLURM API to submit, cancel and monitor scripts.
    This class does not contain any job-related state."""

    def submit_script(
        self,
        script: Union[str, Sequence[str]],
        parameters: Optional[dict] = None,
        metadata: Optional[Union[str, dict]] = None,
        request_options: Optional[dict] = None,
    ) -> int:
        """Submit a script. Assume it is a bash script in the absence of a shebang."""
        if not isinstance(script, str) and isinstance(script, Sequence):
            script = "\n".join(script)
        if not script.startswith("#!"):
            script = f"{defaults.SHEBANG}\n" + script
        return self.submit_job(
            script,
            parameters=parameters,
            metadata=metadata,
            request_options=request_options,
        )
