from mellanox_tempest_plugin.tests.scenario import test_basic
from tempest import config

from tempest.lib import decorators

CONF = config.CONF


class TestServers(test_basic.BaseV1):
    @classmethod
    def skip_checks(cls):
        super(TestServers, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(TestServers, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(TestServers, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(TestServers, cls).resource_setup()

    @decorators.attr(type='smoke')
    def test_list_servers(self):
        body = self.client.list_servers()
        servers = body['servers']
        found = [i for i in servers if i['id'] == self.server['id']]
        self.assertNotEmpty(found)

    def test_list_servers_with_detail(self):
        body = self.client.list_servers(detail=True)
        servers = body['servers']
        found = [i for i in servers if i['id'] == self.server['id']]
        self.assertNotEmpty(found)
