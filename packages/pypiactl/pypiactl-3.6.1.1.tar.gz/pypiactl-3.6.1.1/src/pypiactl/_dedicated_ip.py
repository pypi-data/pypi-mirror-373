from pathlib import Path
from typing import Optional

from ._types import PIACommandResult, PIACommandStatus


class PIADedicatedIP:
    def __init__(self, pia):
        self._pia = pia

    def add(
        self, token: str | None = None, token_file: str | Path | None = None, **kwargs
    ) -> PIACommandResult[PIACommandStatus, Optional[Exception]]:
        """
        To add, pass in a dedicated IP token with the `token`
        argument, or place it in a text file, by itself like
        so:\n
        `DIP20000000000000000000000000000`\n
        and pass in its path with the `token_file` argument.
        (This ensures the token is not visible in the process
        command line or environment.)\n
        Command status may be `INVALID_ARGS`, `TEMP_FILE_ERROR`,
        or `SUCCESS`.
        """
        return self._pia._exec_temp_file_cmd(
            self._pia._constants.dedicatedip_add_cmd, token, token_file, **kwargs
        )

    def remove(
        self, region_id: str, **kwargs
    ) -> PIACommandResult[PIACommandStatus, None]:
        """
        To remove, specify the dedicated IP region ID, such as
        `dedicated-sweden-000.000.000.000`.
        """
        return self._pia._exec_simple_cmd(
            self._pia._constants.dedicatedip_remove_cmd + [region_id], **kwargs
        )
