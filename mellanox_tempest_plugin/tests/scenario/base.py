import collections
from tempest import config
from tempest.scenario import manager
from oslo_log import log as logging
from tempest.api.compute import base
import subprocess as sp
import paramiko
import re
import StringIO

CONF = config.CONF
LOG = logging.getLogger(__name__)
Floating_IP_tuple = collections.namedtuple('Floating_IP_tuple',
                                           ['floating_ip', 'server'])


class Base(manager.NetworkScenarioTest, base.BaseV2ComputeAdminTest):
    """The MellanoxTestV1 test case use to test openstack features with
    mellanox product , all tests in this test case applied if
    number of compute node >= 2.
    """
    credentials = ['primary', 'admin']

    @classmethod
    def skip_checks(cls):
        super(Base, cls).skip_checks()
        if CONF.compute.min_compute_nodes < 2:
            raise cls.skipException(
                "Less than 2 compute nodes, skipping tests.")

    @classmethod
    def setup_credentials(cls):
        """Do not create network resources for these tests
        Using public network for ssh
        """
        cls.set_network_resources()
        super(Base, cls).setup_credentials()

    def setUp(self):
        super(Base, self).setUp()
        self.keypairs = {}
        self.servers = []
        self.run_ssh = CONF.validation.run_validation
        self.ssh_user = CONF.validation.image_ssh_user

    @classmethod
    def setup_clients(cls):
        super(Base, cls).setup_clients()
        cls.client = cls.os_admin.hypervisor_client
        cls.hypervisor_client = cls.os_primary.hypervisor_client
        cls.aggregates_client = cls.os_primary.aggregates_client

    def _list_aggregate(self, name=None):
        """Aggregation listing
        This Method lists aggregation based on name, and returns the
        aggregated hosts lists.
        TBD: Add support to return, hosts list
        TBD: Return None in case no aggregation found.
        :param name
        """
        host = None

        if not name:
            return host

        aggregate = self.aggregates_client.list_aggregates()['aggregates']
        #       Assertion check
        if aggregate:
            aggr_result = []
            for i in aggregate:
                if name in i['name']:
                    aggr_result.append(self.aggregates_client.
                                       show_aggregate(i['id'])['aggregate'])
            host = aggr_result[0]['hosts']
        return host

    def _run_local_cmd_shell_with_venv(self, command, shell_file_to_exec=None):
        """This Method runs command on tester local host
        Shell_file_to_exec path to source file default is None
        TBD: Add support to return, hosts list
        TBD: Return None in case no aggregation found.
        :param command
        :param shell_file_to_exec
        """
        self.assertNotEmpty(command, "missing command parameter")
        if shell_file_to_exec is not None:
            source = 'source %s' % shell_file_to_exec
            pipe = sp.Popen(['/bin/bash', '-c', '%s && %s' % (
                source, command)], stdout=sp.PIPE)
        else:
            pipe = sp.Popen(['/bin/bash', '-c', '%s' % command],
                            stdout=sp.PIPE)
        result = pipe.stdout.read()
        return result.split()

    def _get_hypervisor_ip_from_undercloud(self, **kwargs):
        """This Method lists aggregation based on name
        Returns the aggregated search for IP through Hypervisor list API
        Add support in case of NoAggregation, and Hypervisor list is not empty
        if host=None, no aggregation, or name=None and if hypervisor list has
        one member return the member
        :param kwargs['shell']
        :param kwargs['server_id']
        :param kwargs['aggregation_name']
        :param kwargs['hyper_name']
        """
        host = None
        ip_address = ''
        if 'aggregation_name' in kwargs:
            host = self._list_aggregate(kwargs['aggregation_name'])

        hyper = self.os_primary.hypervisor_client.list_hypervisors()
        """                                                         
        if hosts in aggregations                                    
        """
        if host:
            host_name = re.split("\.", host[0])[0]
            if host_name is None:
                host_name = host

            for i in hyper['hypervisors']:
                if i['hypervisor_hostname'] == host[0]:
                    command = 'openstack ' \           
                              'server show ' + host_name + \
                              ' -c \'addresses\' -f value | cut -d\"=\" -f2'
                    ip_address = self. \
                        _run_local_cmd_shell_with_venv(command,
                                                       kwargs['shell'])
        else:
            """                                                             
            no hosts in aggregations, select with 'server_id' in kwargs     
            """
            compute = 'compute'
            if 'hyper_name' in kwargs:
                compute = kwargs['hyper_name']
            if 'server_id' in kwargs:
                server = self. \
                    os_admin.servers_client.show_server(kwargs['server_id'])
                compute = \
                    server['server']['OS-EXT-SRV-ATTR:host'].partition('.')[0]

            for i in hyper['hypervisors']:
                if i['state'] == 'up':
                    command = 'openstack server list -c \'Name\' -c ' \
                              '\'Networks\' -f value | grep -i {0} | ' \
                              'cut -d\"=\" -f2'.format(compute)
                    ip_address = self. \
                        _run_local_cmd_shell_with_venv(command, kwargs['shell'])

        return ip_address

    @staticmethod
    def _run_command_over_ssh(host, command, pkey=None , username="root", password=""):
        """This Method run Command Over SSH
        Provide Host, user and pass into configuration file
        :param host
        :param command
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if pkey is not None :
                not_really_a_file = StringIO.StringIO(pkey)
                private_key = paramiko.RSAKey.from_private_key(not_really_a_file)
                """Assuming all check done in Setup,                                   
                otherwise Assert failing the test                                      
                """
                ssh.connect(host, username=CONF.validation.image_ssh_user, pkey=private_key)
        else :
                ssh.connect(host, username=username,password=password)
        stdin, stdout, stderr = ssh.exec_command(command)  # get_pty
        result = stdout.read()
        ssh.close()
        return result

    def _list_hypervisors(self):
        # List of hypervisors
        hypers = self.client.list_hypervisors(detail=True)['hypervisors']
        return hypers

    def _get_hypervisor_host_ip(self, name=None):
        host = None
        ip_address = ''
        hyper = self.os_primary.hypervisor_client.list_hypervisors()

        for i in hyper['hypervisors']:
            if i['state'] == 'up':
                ip_address = \
                    self.os_primary.hypervisor_client.show_hypervisor(
                        i['id'])['hypervisor']['host_ip']
                print(ip_address)

    def _create_server(self, network, port_id=None, hyper=""):
        avzone = "nova:" + hyper
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
            security_groups=security_groups, availability_zone=avzone, wait_until='ACTIVE')
        self.servers.append(server)
        return server

    def _setup_network_and_servers(self, **kwargs):
        boot_with_port = kwargs.pop('boot_with_port', False)
        self.network, self.subnet, self.router = self.create_networks(**kwargs)
        all_networks = self.os_admin.networks_client.list_networks()
        my_network_name = [n['name'] for n in all_networks['networks']]
        self.assertIn(self.network['name'], my_network_name)
        LOG.debug("check network test in network list")
        self.ports = []
        port_id = None
        port_id1 = None
        if boot_with_port:
            # create a port on the network and boot with that
            port_id = self.create_port(self.network['id'])['id']
            port_id1 = self.create_port(self.network['id'])['id']
            self.ports.append({'port': port_id})
            self.ports.append({'port': port_id1})
        hypers = self._list_hypervisors()
        hostname1 = hypers[0]['hypervisor_hostname']
        hostname2 = hypers[1]['hypervisor_hostname']
        self.server = self._create_server(self.network, port_id, hostname1)
        self.server1 = self._create_server(self.network, port_id1, hostname2)
        self.floating_ip = self.create_floating_ip(self.server)
        self.floating_ip_tuple = Floating_IP_tuple(self.floating_ip, self.server)
        self.floating_ip1 = self.create_floating_ip(self.server1)
        self.floating_ip_tuple = Floating_IP_tuple(self.floating_ip1, self.server1)
        LOG.debug("create servers with floating ips")

    def _get_server_key(self, server):
        return self.keypairs[server['key_name']]['private_key']