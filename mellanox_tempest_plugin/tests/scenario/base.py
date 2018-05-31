from tempest import config
from tempest.scenario import manager

CONF = config.CONF


class BaseV1(manager.ScenarioTest):
    """This is a set of tests specific to servers in different hypervisors testing."""
    credentials = ['primary', 'admin']

    @classmethod
    def skip_checks(cls):
        super(BaseV1, cls).skip_checks()

        if CONF.compute.min_compute_nodes < 2:
            raise cls.skipException(
                "Less than 2 compute nodes, skipping tests.")

    @classmethod
    def setup_credentials(cls):
        super(BaseV1, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseV1, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseV1, cls).resource_setup()
