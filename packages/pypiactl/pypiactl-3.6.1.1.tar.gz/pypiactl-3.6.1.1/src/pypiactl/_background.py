# PIA Background Activity Controller

from ._types import PIACommandResult


class PIABackground:
    def __init__(self, pia):
        self._pia = pia

    def enable(self, **kwargs) -> PIACommandResult[None, None]:
        _, logs = self._pia._exec_one_shot_cmd(
            self._pia._constants.background_enable_cmd, **kwargs
        )

        return PIACommandResult[None, None](None, None, logs)

    def disable(self, **kwargs) -> PIACommandResult[None, None]:
        _, logs = self._pia._exec_one_shot_cmd(
            self._pia._constants.background_disable_cmd, **kwargs
        )

        return PIACommandResult[None, None](None, None, logs)
