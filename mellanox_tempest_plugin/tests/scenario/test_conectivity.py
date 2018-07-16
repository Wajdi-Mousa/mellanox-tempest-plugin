from mellanox_tempest_plugin.tests.scenario import base

from oslo_log import log as logging
from tempest import config

LOG = logging.getLogger(__name__)
CONF = config.CONF

class TestConectivity(base.Base):
    @classmethod
    def setup_credentials(cls):
        """Do not create network resources for these tests
        Using public network for ssh
        """
        cls.set_network_resources()
        super(TestConectivity, cls).setup_credentials()

    def setUp(self):
        super(TestConectivity, self).setUp()



def check_ping(self, target_ip):
    msg = "Timed out waiting for to become reachable"
    self.assertTrue(self.ping_ip_address(target_ip['floating_ip_address']), msg)


def verify_ssh_and_test_ping(self, keypair, serv, ip):
    if self.run_ssh:
        # Obtain a floating IP if floating_ips is enabled
        if (CONF.network_feature_enabled.floating_ips):
            self.ip = self.create_floating_ip(serv)['ip']
        else:
            instance = self.servers_client.show_server(
                serv['id'])['server']
            self.ip = self.get_server_ip(instance)
        # Check ssh
        self.ssh_client = self.get_remote_client(
            ip_address=self.ip,
            username=self.ssh_user,
            private_key=keypair,
            server=serv)
    self.check_ping(ip)
    LOG.debug("test ping between vms")


def test_vms_ping(self):
    """This test checks ping between VMs in different hypervisor.
    1. Create networks , subnet , router to lunch vms
    2. Give a FIP to servers
    3. Start up server 1 in network
    4. Start up server 2 in network
    5. Check ssh in server1
    6. check ssh in server2
    7. Check that server 1 can ping server 2
    8. Check that server 1 cannot ping server 2
    """
    self._setup_network_and_servers()
    key = self._get_server_key(self.server)
    key2 = self._get_server_key(self.server1)
    self.verify_ssh_and_test_ping(key, self.server, self.floating_ip1)
    self.verify_ssh_and_test_ping(key2, self.server1, self.floating_ip)