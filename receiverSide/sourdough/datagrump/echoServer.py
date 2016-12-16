#!/usr/bin/env python

"""
server
"""

import socket
import posix_ipc
import sys
import time

TCP_CONGESTION = 13
host = ''



port = int(sys.argv[1])
backlog = 1


mqnum2= str(sys.argv[2])
mq2 = posix_ipc.MessageQueue(mqnum2, posix_ipc.O_CREAT,0666,10,1700)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, 'cubic')
s.bind((host,port))
s.listen(backlog)

print "Started TCP CUBIC Server: port -> " + str(port) + " mqnum -> " + str(mqnum2)

client, address = s.accept()
print "Connected to client in " + str(port)
pktCount = 0
while 1:
    data = client.recv(1238, socket.MSG_WAITALL)
    #print pktCount
    #pktCount = pktCount + 1
    #print "len : " + str(len(data))
    time.sleep(0.000001)
    mq2.send(data)

