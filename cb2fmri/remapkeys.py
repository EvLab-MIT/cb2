import subprocess
import logging

logger = logging.getLogger(__file__)


class KmonadProcessTracker:
    proc = None

    def __init__(
        self,
        kmonad_binary_path="cb2fmri/kmonad-0.4.1-linux",
        kmonad_config_path="cb2fmri/cb2.kbd",
    ) -> None:
        self.binary = kmonad_binary_path
        self.config = kmonad_config_path

    @classmethod
    def obtain_sudo(cls):
        """
        a non-consequential action just so our
        script can obtain sudo privileges for later
        """
        logger.info(
            "a non-consequential action, 'ls' just so our script can obtain sudo privileges for later"
        )
        subprocess.Popen(["sudo", "ls"])

    def remap(self):
        logger.info(
            f"opening a process with binary {self.binary} and config {self.config}"
        )
        self.proc = subprocess.Popen([self.binary, self.config])

    def reset(self):
        logger.info("shutting down kmonad process")
        self.proc.terminate()
