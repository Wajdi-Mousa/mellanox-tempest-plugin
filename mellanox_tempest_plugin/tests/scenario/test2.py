import collections
import re

from oslo_log import log as logging
import testtools

from tempest.common import utils
from tempest.common import waiters
from tempest import config
from tempest.lib.common.utils import test_utils
from tempest.lib import decorators
from tempest.lib import exceptions
from tempest.scenario import manager

CONF = config.CONF


class Test2(manager.NetworkScenarioTest):
    credentials = ['primary', 'admin']

    @classmethod
    def setup_credentials(cls):
        """Do not create network resources for these tests
        Using public network for ssh
        """
        cls.set_network_resources()
        super(Test2, cls).setup_credentials()

    def _setup_network(self, **kwargs):
        self.wajdi = self.create_networks(self, **kwargs)
        all_networks = self.os_admin.networks_client.list_networks()
        my_network_name = [n['name'] for n in all_networks['networks']]
        self.assertIn(self.wajdi['name'], my_network_name)

    def test_network(self):
        self._setup_network()
