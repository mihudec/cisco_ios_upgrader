import json
import argparse
import pathlib
from netmiko import ConnectHandler, file_transfer
from nuaal.utils import get_logger
from scp import SCPException
import progressbar
import queue
import threading


from cisco_ios_upgrader import Bar

class FileUploader(object):

    def __init__(self, provider: dict, hosts: list, workers: int = 5, verbosity: int = 4) -> None:
        progressbar.streams.wrap_stderr()
        self.logger = get_logger(name="FileUploader", with_threads=True, verbosity=verbosity)
        self.provider = provider
        self.hosts = hosts
        self.workers = workers
        self.queue = queue.Queue()
        self.threads = []
        self.results = []

    def fill_queue(self):
        for host in self.hosts:
            print(host)
            self.queue.put(host)
        
    def worker(self):
        self.logger.debug(msg="Spawned new worker in {}".format(threading.current_thread().getName()))
        while not self.queue.empty():
            host = self.queue.get()
            if host is None:
                self.logger.info("Queue is empty. Nothing to do.")
                break
            result = {"host": host["ip"]}
            try:
                with ConnectHandler(host=host["ip"], **self.provider) as device:
                    device.send_config_set(config_commands=["ip scp server enable"])

                bar = Bar(peername=[host["hostname"]], filename=host["dest_file"])
                self.logger.info("Working on host {}".format(host["hostname"]))
                device = ConnectHandler(host=host["ip"], **self.provider)
                result_dict = file_transfer(ssh_conn=device, direction="put", disable_md5=True, source_file=host["source_file"], dest_file=host["dest_file"], file_system=host["file_system"], progress4=bar.progress4)
                result.update(result_dict)
                self.logger.info("Result for host {}: {}".format(host["hostname"], result))
                bar.bar.finish()
            except ValueError as e:
                if str(e) == "File already exists and overwrite_file is disabled":
                    self.logger.info("Host {}: {}".format(host["hostname"], repr(e)))
                    result.update({"file_exists": True, "file_transferred": False, "file_verified": False})
                else:
                    self.logger.error("Encountered unhandled ValueError: {}".format(repr(e)))
            except KeyboardInterrupt as e:
                self.logger.info("KeyboardInterrupt")
            except SCPException as e:
                if str(e) == "Administratively disabled.\n":
                    self.logger.error("SCP DISABLED Error on host {}".format(host["hostname"]))
                else:
                    self.logger.error("Encountered unhandled SCP Exception: {}".format(repr(e)))
            except Exception as e:
                self.logger.error("Encountered unhandled exception: {}".format(repr(e)))
            finally:
                self.results.append(result)
                self.queue.task_done()


    def thread_factory(self):
        for i in range(min([self.workers, len(self.hosts)])):
            t = threading.Thread(name="WorkerThread-{}".format(i), target=self.worker, args=())
            self.threads.append(t)

    def run(self):
        self.fill_queue()
        self.thread_factory()
        [t.start() for t in self.threads]
        self.queue.join()
        json.dump(obj=self.results, fp=pathlib.Path(__file__).parent.joinpath("upgrade_results.json").open(mode="w"), indent=2)


def load_hosts(path: pathlib.Path):
    return json.load(path.open(mode="rb"))

def main():
    provider = {
        "device_type": "cisco_ios",
        "username": "mhudec",
        "password": "Sw2$M_V6uv",
    }
    hosts = load_hosts(pathlib.Path(__file__).parent.joinpath("hosts.json"))
    fu = FileUploader(
        provider=provider,
        hosts=hosts,
        verbosity=5
    )
    fu.run()
if __name__ == "__main__":
    main()