#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Node
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import random

class CustomRouter(Node):
    def config(self, **params):
        super(CustomRouter, self).config(**params)

    def terminate(self):
        super(CustomRouter, self).terminate()

def myNetwork():

    net = Mininet( topo=None,
                   build=False)

    mainNetRouter = net.addHost('mr', cls=CustomRouter)
    for branchCounter in range(1, 7):
        mainNetSwitch = net.addSwitch('ms{}'.format(branchCounter), cls=OVSKernelSwitch, 
                                    failMode='standalone')
        net.addLink(mainNetRouter, mainNetSwitch)
        branchRouter = net.addHost('b{}r'.format(branchCounter), cls=CustomRouter, 
                                    ip='10.0.{}.1/24'.format(branchCounter))
        branchSwitch = net.addSwitch('b{}s'.format(branchCounter), cls=OVSKernelSwitch, 
                                    failMode='standalone')
        net.addLink(branchRouter, branchSwitch)
        net.addLink(branchRouter, mainNetSwitch)
        info( '*** Add hosts\n')
        for hostCounter in range(1, random.randint(3, 15)):
            host = net.addHost('h{}b{}'.format(hostCounter, branchCounter), 
                                ip='10.0.{}.{}/24'.format(branchCounter, hostCounter+1))
            net.addLink(host, branchSwitch)

    info( '*** Starting network\n')
    net.build()

    info( '*** Starting switches\n')
    for switch in net.switches:
        switch.start([])

    info( '*** Post configure switches and hosts\n')
    mainNetRouter = net.get('mr')
    mainNetRouter.cmd('sysctl net.ipv4.ip_forward=1')
    for netIntCounter in range(0, 6):
        mainNetRouter.cmd('ip addr add 192.168.100.{}/29 dev mr-eth{}'
                            .format(6+(8*(netIntCounter)), netIntCounter))
        mainNetRouter.cmd('ip route add 10.0.{}.0/24 via 192.168.100.{}'
                            .format(netIntCounter+1, 1+(8*netIntCounter)))
        branchRouter = net.get('b'+str(netIntCounter+1)+'r')
        branchRouter.cmd('ip addr add 192.168.100.{}/29 dev b{}r-eth1'
                            .format(1+(8*(netIntCounter)), netIntCounter+1))
        branchRouter.cmd('ip route add 10.0.0.0/21 via 192.168.100.{}'.format(6+(8*netIntCounter)))
        branchRouter.cmd('sysctl net.ipv4.ip_forward=1')
        hostCounter = 1
        while True:
            try:
                host = net.get('h{}b{}'.format(hostCounter, netIntCounter+1))
                host.cmd('ip route add default via 10.0.{}.1'.format(netIntCounter+1))
                hostCounter += 1
            except KeyError:
                break

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()