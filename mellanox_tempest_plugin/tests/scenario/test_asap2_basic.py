import testtools

from mellanox_tempest_plugin.tests.scenario import base

from oslo_log import log as logging
from tempest import config
import re
import time

LOG = logging.getLogger(__name__)
CONF = config.CONF


class TestAsap(base.Base):
    @classmethod
    def setup_credentials(cls):
        """Do not create network resources for these tests
        Using public network for ssh
        """
        cls.set_network_resources()
        super(TestAsap, cls).setup_credentials()

    def setUp(self):
        super(TestAsap, self).setUp()

    def get_representor(self, hyper_ip, vm_ip , pkey):
        mac_command = "/sbin/ip link show | grep ether | awk '{print $2}'"
        mac = self._run_command_over_ssh(vm_ip, mac_command , pkey).strip()
        fv_command = "ip link show | grep -i " + mac + " | awk '{print $2}'"
        fv = self._run_command_over_ssh(hyper_ip, fv_command).strip()
        return fv

    def parse_result(self, result_str, regex):
        matches = re.finditer(regex, result_str, re.MULTILINE)
        for matchNum, match in enumerate(matches):
            matchNum = matchNum + 1
            self.assertEqual(match.group() , regex)
            #print("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum=matchNum, start=match.start(),
                                                                                #end=match.end(), match=match.group()))
        self.assertEqual(matchNum , 1)
    def display_asap_result(self, hyper):
        command = "cat asap_test.log"
        test_str = self._run_command_over_ssh(hyper, command).strip()
        regex = r'request'
        self.parse_result(test_str, regex)

    @testtools.skipUnless(CONF.network.port_profile['capabilities'] == ['switchdev'],
                          'Port Error')
    def test_asap(self):
        print(CONF.network.port_profile['capabilities'])
        print(type(CONF.network.port_profile))
        # print(self.client.list_servers_on_hypervisor(hostname , detail=True)
        # ['hypervisors'])
        hyper1_ip = self._get_hypervisor_ip_from_undercloud(**{'shell': '/home/stack/stackrc'})[1]
        hyper2_ip = self._get_hypervisor_ip_from_undercloud(**{'shell': '/home/stack/stackrc'})[0]
        print(hyper1_ip)
        print(hyper2_ip)
        self._setup_network_and_servers()
        time.sleep(50)
        # self.verify_ssh_and_test_ping(key, self.server, self.floating_ip1)
        # self.verify_ssh_and_test_ping(key2, self.server1, self.floating_ip)
        # command = "tcpdump -i eth23 icmp </dev/null > asap_test.log 2>&1 &"
        # command = "nohup tcpdump -i eth31 icmp >> result.txt &"
        # print(self._run_command_over_ssh(hyper2_ip , command , username="root" , password=""))
        vm1_ip = self.server['addresses'].keys()[0]
        self.final_vm1_ip = self.server['addresses'][vm1_ip][0]['addr']
        vm2_ip = self.server1['addresses'].keys()[0]
        self.final_vm2_ip = self.server1['addresses'][vm2_ip][0]['addr']
        f_ip1 = self.floating_ip['floating_ip_address']
        f_ip2 = self.floating_ip1['floating_ip_address']
        print(self.final_vm1_ip)
        print(self.final_vm2_ip)
        key1 = self._get_server_key(self.server)
        key2 = self._get_server_key(self.server1)
        # mac_command="/sbin/ifconfig | grep HWaddr | awk '{print $5}'"
        # command3 = "ping -c 3 "+final_vm1_ip
        # mac = self._run_command_over_ssh(f_ip2,mac_command).strip()
        # print("mac address: "+mac)
        # fv_command = "ip link show | grep -i "+mac+" | awk '{print $2}'"
        # fv = self._run_command_over_ssh(hyper2_ip , fv_command , username="root" , password="").strip()
        # ss="tcpdump </dev/null > asap_test.log 2>&1 &"
        fv = self.get_representor(hyper1_ip, f_ip1, key1)
        tcp_command = "tcpdump -l -i eth" + fv + " icmp </dev/null > asap_test.log 2>&1 &"
        self._run_command_over_ssh(hyper1_ip, tcp_command)
        ping_command = "ping -c 3 " + self.final_vm1_ip
        self._run_command_over_ssh(f_ip2, ping_command , key2)
        # ss = "kill -9 `ps -ef | grep tcpdump | head -1 | awk '{print $2}'`"
        # self._run_command_over_ssh2(hyper2_ip , ss , username="root", password="")
        self.display_asap_result(hyper1_ip)
        # ss = "kill -9 `ps -ef | grep tcpdump | head -1 | awk '{print $2}'` && cat asap_test.log"
        # self._run_command_over_ssh2(hyper2_ip , ss)
        # print (homepage)
        # print(host)