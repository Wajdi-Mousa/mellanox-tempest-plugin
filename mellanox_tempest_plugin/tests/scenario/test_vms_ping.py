import collections
from tempest import config
from tempest.scenario import manager

CONF = config.CONF
Floating_IP_tuple = collections.namedtuple('Floating_IP_tuple',
                                           ['floating_ip', 'server'])


class MellanoxTestV1(manager.NetworkScenarioTest):
    credentials = ['primary', 'admin']

    @classmethod
    def setup_credentials(cls):
        """Do not create network resources for these tests
        Using public network for ssh
        """
        cls.set_network_resources()
        super(MellanoxTestV1, cls).setup_credentials()

    def setUp(self):
        super(MellanoxTestV1, self).setUp()
        self.keypairs = {}
        self.servers = []
        self.run_ssh = CONF.validation.run_validation
        self.ssh_user = CONF.validation.image_ssh_user

    def _setup_network_and_server(self, **kwargs):
        boot_with_port = kwargs.pop('boot_with_port', False)
        self.network, self.subnet, self.router = self.create_networks(**kwargs)
        all_networks = self.os_admin.networks_client.list_networks()
        my_network_name = [n['name'] for n in all_networks['networks']]
        self.assertIn(self.network['name'], my_network_name)
        self.ports = []
        port_id = None
        port_id1 = None
        if boot_with_port:
            # create a port on the network and boot with that
            port_id = self.create_port(self.network['id'])['id']
            port_id1 = self.create_port(self.network['id'])['id']
            self.ports.append({'port': port_id})
            self.ports.append({'port': port_id1})
        self.server = self._create_server(self.network, port_id)
        self.server1 = self._create_server(self.network, port_id1)
        floating_ip = self.create_floating_ip(self.server)
        self.floating_ip_tuple = Floating_IP_tuple(floating_ip, self.server)
        floating_ip1 = self.create_floating_ip(self.server1)
        self.floating_ip_tuple = Floating_IP_tuple(floating_ip1, self.server1)

    def _create_server(self, network, port_id=None):
        keypair = self.create_keypair()
        self.keypairs[keypair['name']] = keypair
        security_groups = [
            {'name': self._create_security_group()['name']}
        ]
        network = {'uuid': network['id']}
        if port_id is not None:
            network['port'] = port_id
        server = self.create_server(
            networks=[network],
            key_name=keypair['name'],
            security_groups=security_groups)
        self.servers.append(server)
        return server

    def _get_server_key(self, server):
        return self.keypairs[server['key_name']]['private_key']

    def verify_ssh(self, keypair, server):
        if self.run_ssh:
            # Obtain a floating IP if floating_ips is enabled
            if CONF.network_feature_enabled.floating_ips:
                self.ip = self.create_floating_ip(server)['ip']
            else:
                instance = self.servers_client.show_server(
                    server['id'])['server']
                self.ip = self.get_server_ip(instance)
            # Check ssh
            self.ssh_client = self.get_remote_client(
                ip_address=self.ip,
                username=self.ssh_user,
                private_key=keypair,
                server=server)

    def test_network(self):
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
        self._setup_network_and_server()
        key = self._get_server_key(self.server)
        key1 = self._get_server_key(self.server1)
        self.verify_ssh(key, self.server)
        self.verify_ssh(key1, self.server1)
