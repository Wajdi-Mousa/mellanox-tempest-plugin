'''
Created on Jun 29, 2016
@author: ad_cjmarti2
'''
import netaddr
import re
import subprocess
import time

from tempest import config
from tempest.lib.exceptions import TimeoutException

CONF = config.CONF


def ping_host(host, count=CONF.validation.ping_count,
              size=CONF.validation.ping_size, nic=None):
    """
    @summary: Ping a server with a IP
    @param host: IP address to ping
    @type host: string
    @param count: The number of ping packets originated
    @type count: int
    @param size: The packet size for ping packets
    @type size: int
    @param nic:
    @type nic: string
    @return: True if the server was reachable, False otherwise
    @rtype: bool
    """

    # Regex that looks for a text with the following format:
    # 33.333% packet loss
    # and keeps the int value before the % symbol as group 1
    PING_PACKET_LOSS_REGEX = '(\d{1,3})\.?\d*\%.*loss'
    addr = netaddr.IPAddress(host)
    cmd = 'ping6' if addr.version == 6 else 'ping'
    if nic:
        cmd = 'sudo {cmd} -I {nic}'.format(cmd=cmd, nic=nic)
    cmd += ' -c{0} -w{0} -s{1} {2}'.format(count, size, host)
    process = subprocess.Popen(cmd, shell=True,
                               stdout=subprocess.PIPE)
    process.wait()
    ping_output = process.stdout.read()
    try:
        packet_loss_percent = re.search(
            PING_PACKET_LOSS_REGEX,
            ping_output).group(1)
    except Exception:
        # If there is no match, fail
        return False
    # If at least one packet made it through, return True
    return packet_loss_percent != '100'


def ping_until_reachable(ip, timeout=CONF.validation.ping_timeout):
    """
    @summary: Ping an IP address until it responds or a timeout
              is reached
    @param ip: The IP address to ping (either IPv4 or IPv6)
    @type ip: string
    @param timeout: The amount of time in seconds to wait before aborting.
    @type timeout: int
     """

    end_time = time.time() + timeout

    while time.time() < end_time:
        if ping_host(ip):
            return True

    raise TimeoutException()

