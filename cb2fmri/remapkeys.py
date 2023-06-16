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
        subprocess.call(["sudo", "ls"])

    def remap(self):
        logger.info(
            f"opening a process with binary {self.binary} and config {self.config}"
        )
        # without sudo, we get: kmonad-0.4.1-linux: /dev/uinput: openFd: permission denied (Permission denied)
        self.proc = subprocess.Popen(
            " ".join(["sudo", self.binary, self.config]), shell=True
        )

    def reset(self):
        logger.info("shutting down kmonad process")
        if self.proc:
            self.proc.terminate()
            subprocess.Popen(" ".join(["sudo", "pkill", "kmonad"]), shell=True)
        else:
            logger.warn("no kmonad process to terminate. exiting silently.")
