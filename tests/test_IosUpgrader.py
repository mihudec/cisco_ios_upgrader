import pathlib
import unittest

from cisco_ios_upgrader import IosUpgrader, HostModel, NetmikoProvider

RESOURCES_DIR = pathlib.Path(__file__).parent.joinpath('resources')
SSH_CONFIG = RESOURCES_DIR.joinpath('test_ssh_config.conf')

PROVIDER = NetmikoProvider(username="admin", password="cisco", device_type='cisco_ios', ssh_config_file=SSH_CONFIG)

class TestIosUpgrader(unittest.TestCase):

    def test_check_path(self):
        # TODO:
        pass

    def test_load_hosts(self):

        hosts_file = RESOURCES_DIR.joinpath('sample_hosts.json')

        test_instance = IosUpgrader(hosts_file=hosts_file, provider=PROVIDER)
        hosts = test_instance.load_hosts()
        print(hosts)
        self.assertTrue(all([isinstance(x, HostModel) for x in hosts]))

    def test_backup_hosts(self):
        hosts_file = RESOURCES_DIR.joinpath('sample_hosts.json')
        test_instance = IosUpgrader(hosts_file=hosts_file, provider=PROVIDER)
        test_instance.backup_hosts()

    def test_store_hosts(self):
        hosts_file = RESOURCES_DIR.joinpath('sample_hosts.json')
        test_instance = IosUpgrader(hosts_file=hosts_file, provider=PROVIDER)
        test_instance.store_hosts()


    def test_run(self):
        hosts_file = RESOURCES_DIR.joinpath('sample_hosts.json')
        test_instance = IosUpgrader(hosts_file=hosts_file, provider=PROVIDER)
        test_instance.run()
