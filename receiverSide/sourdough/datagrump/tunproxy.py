#! /usr/bin/env python

#############################################################################
##                                                                         ##
## tunproxy.py --- small demo program for tunneling over UDP with tun/tap  ##
##                                                                         ##
## Copyright (C) 2003  Philippe Biondi <phil@secdev.org>                   ##
##                                                                         ##
## This program is free software; you can redistribute it and/or modify it ##
## under the terms of the GNU General Public License as published by the   ##
## Free Software Foundation; either version 2, or (at your option) any     ##
## later version.                                                          ##
##                                                                         ##
## This program is distributed in the hope that it will be useful, but     ##
## WITHOUT ANY WARRANTY; without even the implied warranty of              ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU       ##
## General Public License for more details.                                ##
##                                                                         ##
#############################################################################


import os, sys
from socket import *
from fcntl import ioctl
from select import select
import getopt, struct
#import sysv_ipc
import posix_ipc
import binascii
import time
import Queue
import threading



TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_TAP   = 0x0002

TUNMODE = IFF_TUN
MODE = 0
DEBUG = 0

def usage(status=0):
    print "Usage: tunproxy [-s port|-c targetip:port] [-e]"
    sys.exit(status)

opts = getopt.getopt(sys.argv[1:],"s:c:ehd")

for opt,optarg in opts[0]:
    if opt == "-h":
        usage()
    elif opt == "-d":
        DEBUG += 1
    elif opt == "-s":
        MODE = 1
        PORT = int(optarg)
    elif opt == "-c":
        MODE = 2
        IP,PORT = optarg.split(":")
        PORT = int(PORT)
        peer = (IP,PORT)
    elif opt == "-e":
        TUNMODE = IFF_TAP
        
if MODE == 0:
    usage(1)

f = os.open("/dev/net/tun", os.O_RDWR)
ifs = ioctl(f, TUNSETIFF, struct.pack("16sH", "toto%d", TUNMODE))
ifname = ifs[:16].strip("\x00")

print "Allocated interface %s. Configure it and use it" % ifname

print "babananaasdf"

hexify = False
debug = False

def readFromFD(q,mqnum):
    print "Thread readfromFD: Creating MQ " + str(mqnum)
    mq2 = posix_ipc.MessageQueue(mqnum, posix_ipc.O_CREAT,0666,10,1700)
    while 1:
        r = select([f],[],[])[0][0]
        if r == f:
            message = os.read(f,1700)
            if hexify:
                hexifiedMessage = binascii.hexlify(message)
                mq2.send(hexifiedMessage)
            else:
                if debug:
                    print binascii.hexlify(message)
                mq2.send(message)

                

def readFromMQ(q,mqnum2,devName):
    print "Thread readfromMQ: Opening MQ " + str(mqnum2)
    mq = posix_ipc.MessageQueue(mqnum2)
    while 1:
	print devName
        message, prio = mq.receive()
        #r = select([],[f],[])[0]
        os.write(f,message)
        if debug:
            print binascii.hexlify(message)


mqnum = "/68681"
mqnum2= "/89898"
devname1 = "d2"
q = Queue.Queue()

t = threading.Thread(target=readFromFD, args = (q, mqnum))
#t.daemon = True
t.start()
t2 = threading.Thread(target=readFromMQ, args = (q, mqnum2,devname1))
t2.start()


mqnum3 = "/68682"
mqnum4= "/89899"
devname2 = "d1"

t3 = threading.Thread(target=readFromFD, args = (q, mqnum3))
#t.daemon = True
t3.start()
t4 = threading.Thread(target=readFromMQ, args = (q, mqnum4,devname2))
t4.start()
