# Library configuration object


class PIAConfig:
    def __init__(
        self,
        executable_path: str = "piactl",
        one_shot_timeout_in_s: None | int = None,
        debug_option: bool = False,
    ):
        self.executable_path = executable_path
        """
        The name or path of the executable used to 
        control the PIA client.
        """

        # Sanity check
        if one_shot_timeout_in_s and one_shot_timeout_in_s < 1:
            raise RuntimeError("One shot timeout must be 1 or greater if not None!")

        self.one_shot_timeout_in_s = one_shot_timeout_in_s
        """
        Optional global timeout for one-shot commands, in seconds.
        """

        self.debug_option = debug_option
        """
        Global option to include debug information in command logs.
        """
