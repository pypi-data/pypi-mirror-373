import os
import time
from typing import TYPE_CHECKING, Optional

from smartutils.log import logger

try:
    import psutil
except ImportError:  # pragma: no cover
    ...
if TYPE_CHECKING:  # pragma: no cover
    import psutil

msg = "smartutils.system.cgroup.IOController depend on psutil, install before use."


class IOController:  # pragma: no cover
    def __init__(
        self,
        name: str,
        devices: list[str],
        command_names: list[str],
        rbps: Optional[int] = None,
        wbps: Optional[int] = None,
        riops: Optional[int] = None,
        wiops: Optional[int] = None,
        cgroup_version="v2",
    ):
        """
        v2文档：https://facebookmicrosites.github.io/cgroup2/docs/io-controller.html
        :param name: cgroup名
        :param devices: 设备号，可通过ls -l /dev查看
        :param command_names: 进程指令，可通过ps查看
        :param rbps: Max read bytes per second
        :param wbps: Max write bytes per second
        :param riops: Max read IO operations per second
        :param wiops: Max write IO operations per second
        :param cgroup_version: cgroup版本，v1/v2
        """
        assert psutil, msg
        self.devices = devices
        self.command_names = command_names
        self.rbps = rbps
        self.wbps = wbps
        self.riops = riops
        self.wiops = wiops
        self.version = cgroup_version
        self._dir = f"/sys/fs/cgroup/{name}"

    def create_cgroup(self):
        os.makedirs(f"{self._dir}", exist_ok=True)
        if self.version == "v2":
            os.makedirs(f"{self._dir}", exist_ok=True)
            self.enable_io_controller()  # Enable controller if needed
        else:
            raise ValueError(
                "Invalid cgroup version. Supported values are 'v1' and 'v2'."
            )

    def enable_io_controller(self):
        if self.version != "v2":
            return
        controllers_file = f"{self._dir}/cgroup.controllers"
        with open(controllers_file, "r") as f:
            existing_controllers = f.read().strip()
        if "io" not in existing_controllers:
            with open(controllers_file, "a") as f:
                f.write("io ")  # Append 'io' to the existing controllers

    def _get_v2_limit(self) -> str:
        limit = " "
        if self.rbps:
            limit = f"{limit}rbps={self.rbps} "
        if self.wbps:
            limit = f"{limit}wbps={self.wbps} "
        if self.riops:
            limit = f"{limit}riops={self.riops} "
        if self.wiops:
            limit = f"{limit}wiops={self.wiops} "
        return limit

    def set_io_limits(self):
        for device in self.devices:
            if self.version == "v1":
                with open(f"{self._dir}/blkio.throttle.read_bps_device", "a") as f:
                    f.write(f"{device} {self.rbps}")
                with open(f"{self._dir}/blkio.throttle.write_bps_device", "a") as f:
                    f.write(f"{device} {self.wbps}")
            elif self.version == "v2":
                with open(f"{self._dir}/io.max", "a") as f:
                    f.write(f"{device}{self._get_v2_limit()}\n")
            else:
                raise ValueError(
                    "Invalid cgroup version. Supported values are 'v1' and 'v2'."
                )

    def monitor_processes(self):
        running_processes = {}
        while True:
            try:
                assert psutil
                for proc in psutil.process_iter(["pid", "cmdline"]):
                    if not proc.info["cmdline"]:
                        continue
                    pid = proc.info["pid"]

                    need_limit = False
                    for command_name in self.command_names:
                        need_limit = need_limit or command_name in proc.info["cmdline"]

                    if need_limit:
                        if pid not in running_processes:
                            logger.info(f"add {pid}")
                            self.add_process_to_cgroup(pid)
                            running_processes[pid] = True
                    elif pid in running_processes:
                        logger.info(f'remove {pid} {proc.info["cmdline"]}')
                        self.remove_process_from_cgroup(pid)
                time.sleep(2)
            except KeyboardInterrupt:
                logger.info("exit")
                self.remove_process_from_cgroup()
                exit(0)

    def add_process_to_cgroup(self, pid):
        file_path = (
            f"{self._dir}/tasks"
            if self.version == "v1"
            else f"{self._dir}/cgroup.procs"
        )
        try:
            with open(file_path, "a") as f:
                f.write(str(pid) + "\n")
        except ProcessLookupError as e:
            logger.error(f"add process {pid} fail {e}")

    def remove_process_from_cgroup(self, pid=None):
        file_path = (
            f"{self._dir}/tasks"
            if self.version == "v1"
            else f"{self._dir}/cgroup.procs"
        )

        if pid:
            with open(file_path, "r") as f:
                pids = f.readlines()
            pids = [p for p in pids if not p.startswith(str(pid))]
        else:
            pids = []

        with open(file_path, "w") as f:
            f.write("")
        for p in pids:
            self.add_process_to_cgroup(p)

    def main(self):
        self.create_cgroup()
        self.set_io_limits()
        self.monitor_processes()


# Example usage:
# io_controller = IOController(
#     cgroup_name="crawler",
#     devices=["8:0", "8:16"],  # List of devices
#     command_names=["command1", "command2"],  # List of command names
#     read_bps_limit="1048576",  # 1 MB/s
#     write_bps_limit="1048576",  # 1 MB/s
#     cgroup_version="v2"  # or "v1"
# )
#
# io_controller.main()
