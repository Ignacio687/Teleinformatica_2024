#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import random

class CustomRouter(Node):
    def config(self, **params):
        super(CustomRouter, self).config(**params)

    def terminate(self):
        super(CustomRouter, self).terminate()

def myNetwork():

    net = Mininet( topo=None,
                   build=False)

    mainNetRouter = net.addHost('r1', cls=CustomRouter, ip='192.168.100.1/29')
    mainNetSwitch = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
    host1 = net.addHost('h1', ip='192.168.100.6/29')
    host2 = net.addHost('h2', ip='10.0.1.8/24')
    net.addLink(mainNetRouter, mainNetSwitch)
    net.addLink(host1, mainNetSwitch)
    net.addLink(host2, mainNetSwitch)

    info( '*** Starting network\n')
    net.build()

    info( '*** Starting switches\n')
    for switch in net.switches:
        switch.start([])

    info( '*** Post configure switches and hosts\n')
    mainNetRouter = net.get("r1")
    mainNetRouter.cmd("ip addr add 10.0.1.1/24 dev r1-eth0")
    mainNetRouter.cmd("sysctl net.ipv4.ip_forward=1")
    host1 = net.get("h1")
    host1.cmd("ip route add default via 192.168.100.1")
    host2 = net.get("h2")
    host2.cmd("ip route add default via 10.0.1.1")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()