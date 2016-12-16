#!/usr/bin/env python

"""
client
"""


# if ((msqid_send = mq_open(arg7.c_str() , O_RDONLY, 0664, &attr)) == -1) { /* connect to the queue */
#         perror("unable to connect to 68681 in msgget()");
#         exit(1);
#     }
#     if(debug_all)
#       cerr <<"After MSQID created\n";


#     if ((msqid_commline = mq_open(arg9.c_str() ,O_WRONLY | O_CREAT, 0664, &attr2)) == -1) { /* connect to the queue */
#         perror("unable to connect to comm line in msgget()");
#         exit(1);
#     }
#     if(debug_all)
#       cerr <<"After MSQID created\n";


#   if (mq_send(msqid_commline, s.c_str(), sizeof(unsigned int), 0) == -1) /* +1 for '\0' */
#      perror("error in msgsnd() commline");

#   int receiveLength = mq_receive(msqid_send, buffaray_send, 8192, NULL);


import socket
import posix_ipc
import sys
import time


def readFromFD(mqnum):
    print "Thread readfromFD: Creating MQ " + str(mqnum)
    mq2 = posix_ipc.MessageQueue(mqnum, posix_ipc.O_CREAT,0666,10,1700)

def readFromMQ(mqnum2):
    print "Thread readfromMQ: Opening MQ " + str(mqnum2)
    mq = posix_ipc.MessageQueue(mqnum2)


TCP_CONGESTION = 13
host = sys.argv[1]
port = int(sys.argv[2])
size = 1700








# readFromFD(mqnum)
# readFromMQ(mqnum2)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, 'cubic')
s.bind(( str(sys.argv[5]), int(sys.argv[6]) ))
s.connect((host,port))


mq = posix_ipc.MessageQueue(str(sys.argv[3]))

mq2 = posix_ipc.MessageQueue(str(sys.argv[4]), posix_ipc.O_CREAT,0666,10,1700)

sntCount = 0
print "TCP CUBIC Client ready: " + str(sys.argv[1]) + " Port :" + str(sys.argv[2]) + " MQ :" + str(sys.argv[3]) + " CL: " + str(sys.argv[4]) 
while 1:
	message, prio = mq.receive()
	#message = message + "\0"
	#print message
	s.send(message)
	mq2.send("1\0");
	time.sleep(0.0001)
	print "sent on Echo :" + str(sntCount)
	print "len of message :" + str(len(message)) 
	sntCount = sntCount + 1

