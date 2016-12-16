import socket
import time
import posix_ipc
import binascii
import Queue
import threading
import subprocess

# This is an example of a UDP client - it creates
# a socket and sends data through it
# create the UDP socket
XCOUNTER_MAX = 10

ControlLoop1=1
ControlLoop2=1
ControlLoop1Changed = True
ControlLoop2Changed = True

def readFromCL(q,mqnum1):
	global ControlLoop1
	global ControlLoop1Changed
	print "Thread readfromCL: Opening MQ " + str(mqnum1)
	mq = posix_ipc.MessageQueue(mqnum1)

	while 1:
		message, prio = mq.receive()
		
		numberOnly = message.split('\0', 1)
		prevControlLoopVal1 = ControlLoop1
		ControlLoop1 = int(numberOnly[0])
		

def readFromCL2(q,mqnum2):
	global ControlLoop2
	global ControlLoop2Changed
	print "Thread readfromCL: Opening MQ " + str(mqnum2)
	mq = posix_ipc.MessageQueue(mqnum2)

	while 1:
		message, prio = mq.receive()
		
		numberOnly = message.split('\0', 1)
		prevControlLoopVal2 = ControlLoop2
		ControlLoop2 = int(numberOnly[0])
		

def startSending():
	global ControlLoop1
	global ControlLoop2
	global ControlLoop1Changed
	global ControlLoop2Changed
	UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	#data = "\n"
	serialNum = 0
	# Simply set up a target address and port ...
	addr = ("192.168.17.22",21567)
	# ... and send data out to it!`	
	file = open('/home/cells/FINAL2/sourdough/datagrump/books/nasa.jpg', 'r')
	#file = open('/home/cells/FINAL2/sourdough/datagrump/books/bit3H.mp4', 'r')
	#file = open('/home/cells/FINAL2/sourdough/datagrump/books/53661-0.txt', 'r')
	fileC = open('/sys/class/net/toto0/statistics/tx_bytes', 'r')
	
	xcounter = 0
	sleeptime = 0.1

	sentDataLength = 0

	while True:
		if serialNum > 999999:
			serialNum = 0



		if ControlLoop2 != 0 or ControlLoop1 !=0:
			
			#read how many bytes tx'd
			actualTxdDataLength = fileC.read()			
			fileC.seek(0)

			# if difference b/w tx'd and sent 
			#greater than 30pkts then wait for 5ms
		
			# if int(actualTxdDataLength) - sentDataLength > 1234:
			# 	time.sleep(0.005)
			# 	print "sleeping"
			# 	continue
			# else:
		
			message = file.read(1200)
			if message == '':
				xcounter = xcounter + 1
				data = "x" + str(xcounter)
				UDPSock.sendto(data,addr)
				#If the read from the file is empty send 'x' -> to signify EOF
				if xcounter > XCOUNTER_MAX:
					print "EOF BREAKING"
					exit(1)

			serialNum = serialNum + 1
			data = str(serialNum).zfill(6) + message

			UDPSock.sendto(data,addr)
			print "tx going " + str(serialNum)
			sentDataLength = len(data) + 28 + sentDataLength


mqnum2= "/CL2"
mqnum1= "/CL1"

q = Queue.Queue()
ControlLoop1 = 1
ControlLoop2 = 1
t2 = threading.Thread(target=readFromCL, args = (q, mqnum2))
t2.start()
t3 = threading.Thread(target=readFromCL, args = (q, mqnum1))
t3.start()


startSending()


