import pathlib
import ipaddress
import datetime
import queue
import shutil
import json

import yaml
from pydantic import BaseModel, constr, root_validator
from pydantic.typing import Optional, List, Union

from cisco_ios_upgrader import get_logger, UploadWorker, HostModel, HostsFile, NetmikoProvider

class IosUpgrader:

    def __init__(self,
                 hosts_file: pathlib.Path,
                 provider: NetmikoProvider):
        self.logger = get_logger(name='IosUpgrader')
        self.hosts_file = self.check_path(hosts_file)
        self.hosts = {x.name: x for x in self.load_hosts()}
        self.workers = None
        self.task_queue = None
        self.results_queue = None
        self.provider = provider

    def check_path(self, path: pathlib.Path):
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        path = path.resolve()
        if path.exists() and path.is_file():
            return path
        else:
            raise FileNotFoundError

    def load_hosts(self):
        data = None
        with self.hosts_file.open(mode='rb') as f:
            data = HostsFile.parse_obj(json.load(fp=f))
        hosts = data.hosts
        hosts = [HostModel.parse_obj(x) for x in hosts]
        self.logger.info(msg=f"Loaded {len(hosts)} hosts.")
        return hosts


    def store_hosts(self):
        with self.hosts_file.open(mode='w') as f:
            f.write(HostsFile(hosts=list(self.hosts.values())).json(indent=2))


    def backup_hosts(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_hosts_file = self.hosts_file.parent.joinpath(f"backup_{timestamp}_{self.hosts_file.name}")
        self.logger.info(msg="Creating backup of hosts_file.")
        shutil.copy(self.hosts_file, backup_hosts_file)

    def run(self, num_workers: int = 5):

        self.task_queue = queue.Queue()
        self.results_queue = queue.Queue()

        run_hosts = [x for x in self.hosts.values()]

        for host in run_hosts:
            self.task_queue.put(host)

        if len(run_hosts) < num_workers:
            num_workers = len(run_hosts)

        self.workers = UploadWorker.worker_factory(
            task_queue=self.task_queue,
            result_queue=self.results_queue,
            provider=self.provider,
            num_workers=num_workers
        )

        UploadWorker.start_workers(
            task_queue=self.task_queue,
            workers=self.workers
        )


