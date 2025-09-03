from typing import List


class PIAConstants:
    def __init__(self):
        # Options
        self.timeout_flag: str = "-t"
        self.debug_flag: str = "-d"

        # Commands
        self.background_enable_cmd: List[str] = ["background", "enable"]
        self.background_disable_cmd: List[str] = ["background", "disable"]
        self.connect_cmd: List[str] = ["connect"]
        self.dedicatedip_add_cmd: List[str] = ["dedicatedip", "add"]
        self.dedicatedip_remove_cmd: List[str] = ["dedicatedip", "remove"]
        self.disconnect_cmd: List[str] = ["disconnect"]
        self.get_cmd: List[str] = ["get"]
        self.login_cmd: List[str] = ["login"]
        self.logout_cmd: List[str] = ["logout"]
        self.monitor_cmd: List[str] = ["monitor"]
        self.reset_settings_cmd: List[str] = ["resetsettings"]
        self.set_cmd: List[str] = ["set"]
        self.version_cmd: List[str] = ["-v"]
