# -*- coding:utf8 -*-
""" UDP Client"""
# !/usr/bin/python
# Python:   3.5.1
# Platform: Windows
# Author:   Heyn (heyunhuan@gmail.com)
# Program:  UDP Client
# History:  2016/10/11
#           [PyLint Message: See web: http://pylint-messages.wikidot.com/]

import re
import errno
import socket
import threading


IPADDR = '192.168.0.101'
PORTNUM = 54320
BUFFER_SIZE = 1024

PACKETDATA = b'Hello,Amp!'

# UDP_SOCKET_BLOCKING     = 1         # No Blocking (=0), or Blocking (=1)
UDP_SOCKET_NO_BLOCKING = 0

DONGLESTRING = ''


def udpconnect(server_ip='127.0.0.1'):
    """UDP Connect Server."""

    dongle_message = ''
    address = (server_ip, PORTNUM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    sock.setblocking(UDP_SOCKET_NO_BLOCKING)
    sock.settimeout(0.5)
    try:
        sock.connect(address)
    except socket.error as err:
        if err.errno != errno.EWOULDBLOCK:
            return 0
    sock.send(PACKETDATA)
    try:
        dongle_message = sock.recv(BUFFER_SIZE)
    except socket.error as err:
        sock.close()
        return ''

    global DONGLESTRING     # pylint: disable=W0603
    DONGLESTRING += dongle_message.decode() + ',' + server_ip + '##'

    sock.close()


class UdpThread(threading.Thread):
    """UDP Thread."""

    def __init__(self, ipaddr='127.0.0.1'):
        threading.Thread.__init__(self)
        self.ipaddr = ipaddr

    def run(self):
        udpconnect(self.ipaddr)


def broadcast(broadip=('255.255.255.255', PORTNUM)):
    """ UDP BroadCast Client"""

    server_message = ''
    loacladdr = ('0.0.0.0', 10013)
    sockudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    sockudp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sockudp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockudp.settimeout(0.5)
    sockudp.bind(loacladdr)
    sockudp.sendto(PACKETDATA, broadip)
    server_message = sockudp.recv(BUFFER_SIZE)
    server_message = server_message.decode() + '##'
    print(server_message)
    return server_message

if __name__ == '__main__':
    broadcast()

    THREADPOOL = []
    LOCALIP = socket.gethostbyname(socket.gethostname())
    LOCALIP = re.sub(r'[^\.][\d]{1,3}$', '', LOCALIP)

    for i in range(255):
        # print(LOCALIP + str(i))
        th = UdpThread(LOCALIP + str(i))
        th.start()
        THREADPOOL.append(th)

    for th in THREADPOOL:
        th.join()

    print(DONGLESTRING)
