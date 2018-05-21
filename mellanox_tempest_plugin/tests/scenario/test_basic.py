from tempest import config
from tempest.common.utils import data_utils
from tempest.scenario import manager
from oslo_log import log
from tempest.lib.common.utils import test_utils

CONF = config.CONF
LOG = log.getLogger(__name__)


class BaseV1(manager.ScenarioTest, manager.NetworkScenarioTest):
    credentials = ['primary']

    @classmethod
    def skip_checks(cls):
        super(BaseV1, cls).skip_checks()
        if not CONF.service_available.nova:
            raise cls.skipException("Nova is not available")

    @classmethod
    def setup_credentials(cls):
        cls.set_network_resources()
        super(BaseV1, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseV1, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseV1, cls).resource_setup()
        cls.build_interval = CONF.compute.build_interval
        cls.build_timeout = CONF.compute.build_timeout
        cls.image_ref = CONF.compute.image_ref
        cls.image_ref_alt = CONF.compute.image_ref_alt
        cls.flavor_ref = CONF.compute.flavor_ref
        cls.flavor_ref_alt = CONF.compute.flavor_ref_alt
        cls.ssh_user = CONF.validation.image_ssh_user
        cls.image_ssh_user = CONF.validation.image_ssh_user
        cls.image_ssh_password = CONF.validation.image_ssh_password

        # section for create test requirement

        def _create_network(self, networks_client=None,
                            tenant_id=None,
                            namestart='network-smoke-',
                            port_security_enabled=True):
            if not networks_client:
                networks_client = self.networks_client
            if not tenant_id:
                tenant_id = networks_client.tenant_id
            name = data_utils.rand_name(namestart)
            network_kwargs = dict(name=name, tenant_id=tenant_id)
            # Neutron disables port security by default so we have to check the
            # config before trying to create the network with port_security_enabled
            if CONF.network_feature_enabled.port_security:
                network_kwargs['port_security_enabled'] = port_security_enabled
            result = networks_client.create_network(**network_kwargs)
            network = result['network']

            self.assertEqual(network['name'], name)
            self.addCleanup(test_utils.call_and_ignore_notfound_exc,
                            networks_client.delete_network,
                            network['id'])
            return network

        def create_subnet(self, network, **kwargs):
            super(self).create_subnet(network, subnets_client=None,
                                      namestart='subnet-smoke', **kwargs)

        def create_port(self, network_id, **kwargs):
            super(self).create_port(network_id, client=None, **kwargs)

        def create_server(self, name=None, image_id=None, flavor=None,
                          validatable=False, wait_until='ACTIVE',
                          clients=None, **kwargs):
            super(self).create_server(name=name, image_id=image_id, flavor=flavor,
                                      validatable=validatable, wait_until=wait_until,
                                      clients=clients, **kwargs)
