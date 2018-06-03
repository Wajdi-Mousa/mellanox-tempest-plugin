from tempest.scenario import manager
from tempest import config

from tempest.common import utils
from tempest.common import waiters

CONF = config.CONF


class Test(manager.ScenarioTest):
    credentials = ['primary', 'admin']

    def setUp(self):
        super(Test, self).setUp()
        self.run_ssh = CONF.validation.run_validation
        self.ssh_user = CONF.validation.image_ssh_user

    def verify_ssh(self, keypair):
        if self.run_ssh:
            # Obtain a floating IP if floating_ips is enabled
            if (CONF.network_feature_enabled.floating_ips and
                    CONF.network.floating_network_name):
                self.ip = self.create_floating_ip(self.instance)['ip']
            else:
                server = self.servers_client.show_server(
                    self.instance['id'])['server']
                self.ip = self.get_server_ip(server)
            # Check ssh
            self.ssh_client = self.get_remote_client(
                ip_address=self.ip,
                username=self.ssh_user,
                private_key=keypair['private_key'],
                server=self.instance)

    @utils.services('compute', 'network')
    def test_server(self):
        keypair = self.create_keypair()
        keypair1 = self.create_keypair()
        security_group = self._create_security_group()
        security_group1 = self._create_security_group()
        self.instance = self.create_server(
            key_name=keypair['name'],
            security_groups=[{'name': security_group['name']}])
        self.instance1 = self.create_server(
            key_name=keypair1['name'],
            security_groups=[{'name': security_group1['name']}])
        self.verify_ssh(keypair)
        self.verify_ssh(keypair1)

    def test_wajdi(self):
        name = "wajdi"
        self.assertEqual(name, "wajdi")
