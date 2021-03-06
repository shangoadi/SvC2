import socket
import Queue
import threading	
import select
import signal
import sys
import time
import os
from itertools import imap, chain
from operator import sub


BUFFER_SIZE = 500000
PKT_SERIALNUM_MAX = 999999
# Set up a UDP server
UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)




# Listen on port 21567
# (to all IP addresses on this system)
listen_addr = ("",21567)
UDPSock.bind(listen_addr)

bufferList1 = []
bufferList2 = []

packetCount = 0


def signal_handler(signal, frame):
	global bufferList1
        print('You pressed Ctrl+C! Writing to file')

	writeToTargetFile(q,bufferList1)
	sys.exit(0)


def writeToTargetFile(q,BufferListLocal):
	global packetCount 
	global BUFFER_SIZE
	global PKT_SERIALNUM_MAX
	
	file = open("newfile_TCP.txt", "w")
	#select.select([file],[],[])
	tempLocalList = []	
	a = []
	outOfOrder = 0
	localIndex = 0
	#take the recieved BufferList 
	for dt in BufferListLocal:

		if dt[0]=="x":
			continue
		#sort it based on the recvd serial numbers
		index,data = int(dt[0:6]),dt[6:]

		tempLocalList.insert( index, data)
		a.insert( localIndex, int(index))
		#localIndex used for inserting into a
		localIndex = localIndex + 1
	
	for item in tempLocalList:
		file.write("%s" % item)
	file.close()
	print "FINISHED WRITING TO FILE, press Ctrl + c"

	
	packetCount = packetCount + BUFFER_SIZE
	if packetCount > PKT_SERIALNUM_MAX:
		packetCount = 0


	print "OUT OF ORDER PKTS: " + str(outOfOrder)
	print "MISSING PACKETS"	
	print len(list(chain.from_iterable((a[i] + d for d in xrange(1, diff))
                        for i, diff in enumerate(imap(sub, a[1:], a))
                        if diff > 1)))
	print "NUMBER OF PAKCETS RECVD " + str(len(BufferListLocal))
	#print a
	os._exit(1)



q = Queue.Queue()

iterationCounter = 0

print('Listening for Packets')


while True:
        data,addr = UDPSock.recvfrom(1700)
	bufferList1.append( data )
	iterationCounter = iterationCounter + 1
	print iterationCounter
	#print data
	print data[6:]
	#if data[0]=="x":
	#	print "BLANK ENDING"
	#	time.sleep(1)
	print iterationCounter
	if len(bufferList1) > BUFFER_SIZE or data[0]=="x":
		bufferList2=bufferList1
		t = threading.Thread(target=writeToTargetFile, args = (q, bufferList2))
		t.start()
		print "GOT STOP WRITING NOW"
		time.sleep(1000)
		print "After WAIT EXITING"
		exit(1)
		
		bufferList1=[]

