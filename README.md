Tempest integration tests for Tripleo OpenStack deployment
===

The mellanox-tempest-plugin contains various tempest tests for OpenStack deployment with mellanox product.

Installation
===

When Tempest runs, it will automatically discover the installed plugins. So we just need to install the Python packages that contains the plugin.

Clone the repository in your machine and install the package from the src tree:

```

$ cd mellanox-tempest-plugin
$ sudo pip install -e .

```

How to run the tests
===

1. To validate that Tempest discovered the test in the plugin, you can run:

```

$ ostestr -l | grep mellanox_tempest_plugin

```

This command will show your complete list of test cases inside the plugin.