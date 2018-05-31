from mellanox_tempest_plugin.tests.scenario import base
from tempest.common import utils
from tempest import config
from tempest.lib import decorators
from tempest.lib import exceptions
from tempest.scenario import manager

CONF = config.CONF


class TestPingBetweenServers(base.BaseV1):

    @utils.services('compute', 'network')
    def test_create_servers_in_different_hypervisors(self):
        available_zone = \
            self.os_admin.availability_zone_client.list_availability_zones(
                detail=True)['availabilityZoneInfo']
        hosts = []
        for zone in available_zone:
            if zone['zoneState']['available']:
                for host in zone['hosts']:
                    if 'nova-compute' in zone['hosts'][host] and \
                            zone['hosts'][host]['nova-compute']['available']:
                        hosts.append({'zone': zone['zoneName'],
                                      'host_name': host})

        # ensure we have at least as many compute hosts as we expect
        if len(hosts) < CONF.compute.min_compute_nodes:
            raise exceptions.InvalidConfiguration(
                "Host list %s is shorter than min_compute_nodes. "
                "Did a compute worker not boot correctly?" % hosts)

        # create 1 compute for each node, up to the min_compute_nodes
        # threshold (so that things don't get crazy if you have 1000
        # compute nodes but set min to 3).
        servers = []

        for host in hosts[:CONF.compute.min_compute_nodes]:
            # by getting to active state here, this means this has
            # landed on the host in question.
            # in order to use the availability_zone:host scheduler hint,
            # admin client is need here.
            inst = self.create_server(
                clients=self.os_admin,
                availability_zone='%(zone)s:%(host_name)s' % host)
            server = self.os_admin.servers_client.show_server(
                inst['id'])['server']
            # ensure server is located on the requested host
            self.assertEqual(host['host_name'], server['OS-EXT-SRV-ATTR:host'])
            servers.append(server)

        # make sure we really have the number of servers we think we should
        self.assertEqual(
            len(servers), CONF.compute.min_compute_nodes,
            "Incorrect number of servers built %s" % servers)

        # ensure that every server ended up on a different host
        host_ids = [x['hostId'] for x in servers]
        self.assertEqual(
            len(set(host_ids)), len(servers),
            "Incorrect number of distinct host_ids scheduled to %s" % servers)
