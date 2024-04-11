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
        rootNetRouter = self.addNode('rootNetRouter', cls=CustomRouter, ip='192.168.100.6')
        for branchCounter in range(1, 7):
            rootNetSwitch = self.addSwitch('rootNetSwitch{}'.format(branchCounter))
            self.addLink(rootNetRouter, rootNetSwitch)
            branchRouter = self.addNode('branch'+str(branchCounter)+'Router', cls=CustomRouter, ip='10.0.{}.1/29'.format(branchCounter))
            branchSwitch = self.addSwitch('branch'+str(branchCounter)+'Switch')
            self.addLink(branchRouter, rootNetSwitch)
            self.addLink(branchRouter, branchSwitch)
            for hostCounter in range(0, random.randint(3, 15)):
                host = self.addHost('host'+str(hostCounter)+'Branch'+str(branchCounter))
                self.addLink(host, branchSwitch)

    @staticmethod
    def routing(net):
        rootNetRouter = net.get('rootNetRouter')
        for netInterfaceCounter in range(0, 6):
            if netInterfaceCounter < 5:
                rootNetRouter.cmd('ip addr add 192.168.100.{}/29 dev eth{}'.format(14+(8*netInterfaceCounter), netInterfaceCounter+1))
            rootNetRouter.cmd('ip route add 10.0.{}.0/24 via 192.168.100.{}'.format(netInterfaceCounter+1, 1+(8*netInterfaceCounter)))
            branchRouter = net.get('branch'+str(netInterfaceCounter+1)+'Router')
            branchRouter.cmd('ip addr add 192.168.100.{}/29 dev eth{}'.format(1+(8*netInterfaceCounter), netInterfaceCounter+1))
            branchRouter.cmd('ip route add 10.0.0.0/21 via 192.168.100.{}'.format(6+(8*netInterfaceCounter)))
            

if __name__ == '__main__':
    setLogLevel('info')
    net = Mininet(topo=CustomTopology(), controller=None)
    net.start()
    CustomTopology.routing(net)
    CLI(net)
    net.stop()
