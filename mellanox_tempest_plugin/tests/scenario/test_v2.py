'''
Created on Jun 17, 2016
@author: castulo, jlwhite
'''
import testtools
from unittest.suite import TestSuite

from tempest.api.compute import base
from tempest.common.utils.linux import remote_client
from tempest import config
from tempest import test

from mellanox_tempest_plugin.common import ping

CONF = config.CONF

class Test(base.BaseV2ComputeTest):

    @classmethod
    def resource_setup(cls):
        cls.set_validation_resources()
        super(Test, cls).resource_setup()

    def test_create_server_burn_in(self):
        server = self.create_test_server(validatable=True,
                                         wait_until='ACTIVE')
        self.assertTrue(server['id'])

    def test_can_ping_created_server(self):
        server = (self.servers_client.show_server(self.servers[0]['id'])
                  ['server'])
        server_ip = self.get_server_ip(server)
        # ping the server until it becomes reachable or times out
        msg = ("ping_until_reachable ran for {timeout} seconds and did not "
               "receive a ping response from {ip}"
               .format(timeout=CONF.validation.ping_timeout, ip=server_ip))
        self.assertTrue(ping.ping_until_reachable(server_ip), msg)

    def test_can_ssh_into_created_server(self):
        server = (self.servers_client.show_server(self.servers[0]['id'])
                  ['server'])
        server_ip = self.get_server_ip(server)
        # Try connecting to the server through SSH
        linux_client = remote_client.RemoteClient(
            server_ip,
            self.image_ssh_user,
            self.image_ssh_password,
            self.validation_resources['keypair']['private_key'],
            server=server,
            servers_client=self.servers_client)
        self.assertTrue(linux_client.validate_authentication())