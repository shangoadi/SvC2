#!/usr/bin/env python

"""
server
"""

import socket
import posix_ipc


TCP_CONGESTION = 13
host = ''
port = 50000
backlog = 1
size = 1024

mqnum2= "/68681"
mq2 = posix_ipc.MessageQueue(mqnum, posix_ipc.O_CREAT,0666,10,1700)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, 'cubic')
s.bind((host,port))
s.listen(backlog)

client, address = s.accept()
while 1:
    data = client.recv(size)
    mq2.send(data)
