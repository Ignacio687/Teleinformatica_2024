#!/usr/bin/env python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import Node
import random

class CustomRouter(Node):
    def config(self, **params):
        super(CustomRouter, self).config(**params)
        # Habilitar el reenvío de IP
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(CustomRouter, self).terminate()

class CustomTopology(Topo):

    def build(self):
        rootNetSwitch = self.addSwitch('rootNetSwitch', dpid='0000000000000100')
        rootNetRouter = self.addNode('rootNetRouter', cls=CustomRouter, ip='100.100.100.100/29')
        self.addLink(rootNetRouter, rootNetSwitch, intfName1='r-eth0', intfName2='s-eth0', params1={'ip': '100.100.100.100/29'})
        rootRouterIpAddrTuple = ('192.168.100.6', '192.168.100.14', '192.168.100.22', '192.168.100.30', '192.168.100.38', '192.168.100.46')
        branchRouterIpAddrTuple = ('192.168.100.1', '192.168.100.9', '192.168.100.17', '192.168.100.25', '192.168.100.33', '192.168.100.41')
        for branchCounter in range(0, 6):
            self.addLink(rootNetRouter, rootNetSwitch, intfName1='r-eth{}'.format(branchCounter+1), intfName2='s-eth{}'.format(branchCounter+1), params1={'ip': rootRouterIpAddrTuple[branchCounter]+"/29"})
            branchSwitch = self.addSwitch('branch'+str(branchCounter)+'Switch', dpid='0000000000000{}'.format(branchCounter+1))
            branchRouter = self.addNode('branch'+str(branchCounter)+'Router', cls=CustomRouter, ip='branchRouterIpAddrTuple[branchCounter]+"/29"')
            self.addLink(branchRouter, rootNetSwitch, intfName1='r{}-eth0'.format(branchCounter), intfName2='s-eth{}'.format(branchCounter+10), params1={'ip': branchRouterIpAddrTuple[branchCounter]+"/29"})
            self.addLink(branchRouter, branchSwitch, intfName1='r{}-eth1'.format(branchCounter), intfName2='s{}-eth0'.format(branchCounter), params1={'ip': '10.0.{}.1'.format(branchCounter+1)+"/24"})
            for hostCounter in range(0, random.randint(3, 15)):
                host = self.addHost('host'+str(hostCounter)+'Branch'+str(branchCounter), ip='10.0.{}.{}'.format(branchCounter+1, hostCounter+2)+"/24")
                self.addLink(host, branchSwitch, intfName1='h{}b{}-eth0'.format(hostCounter, branchCounter), intfName2='s{}-eth{}'.format(branchCounter, hostCounter+2, params1={'ip': '10.0.{}.{}'.format(branchCounter+1, hostCounter+2)+"/24"}))

if __name__ == '__main__':
    setLogLevel('info')
    net = Mininet(topo=CustomTopology(), controller=None)
    CLI(net)
    net.stop()
