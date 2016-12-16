import socket
import time
import posix_ipc
import binascii
import Queue
import threading
import subprocess
import sys

# This is an example of a UDP client - it creates
# a socket and sends data through it
# create the UDP socket
XCOUNTER_MAX = 3

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

ControlLoop1=1
ControlLoop2=1
ControlLoop1Changed = True
ControlLoop2Changed = True
debug = False
def readFromCL(q,mqnum1):
	global ControlLoop1
	global ControlLoop1Changed
	print "Thread readfromCL: Opening MQ " + str(mqnum1)
	mq = posix_ipc.MessageQueue(mqnum1)
	while 1:
		try:
			message, prio = mq.receive(0.1)
			#print message
			if message == None:
				print "nothing changed"
				continue
			numberOnly = message.split('\0', 1)
			#print message
			prevControlLoopVal1 = ControlLoop1
			ControlLoop1 = int(numberOnly[0])
			ControlLoop1Changed = True
		except:
			if debug:
				print "busy error sleep 10ms" 
			#To prevent the sender from sedning packets into the tun interface	
			# ControlLoop1 = 0
			time.sleep(0.1)
			# ControlLoop1Changed = True


def readFromCL2(q,mqnum2):
	global ControlLoop2
	global ControlLoop2Changed
	print "Thread readfromCL: Opening MQ " + str(mqnum2)
	mq2 = posix_ipc.MessageQueue(mqnum2)
	while 1:
		try:
			message, prio = mq2.receive(0.1)
			#print message
			if message == None:
				print "nothing changed"
				continue
			numberOnly = message.split('\0', 1)
			print message
			prevControlLoopVal2 = ControlLoop2
			ControlLoop2 = int(numberOnly[0])
			ControlLoop2Changed = True
		except:
			if debug:
				print "busy error sleep 10ms" 
			#To prevent the sender from sedning packets into the tun interface	
			# ControlLoop1 = 0
			time.sleep(0.1)
			# ControlLoop2Changed = True
		

def startSending():
	global ControlLoop1
	global ControlLoop2
	global ControlLoop1Changed
	global ControlLoop2Changed
	
	#data = "\n"
	serialNum = 0
	# Simply set up a target address and port ...
	addr = ("192.168.17.22",21567)
	# ... and send data out to it!`	
	#file = open('/home/cells/FINAL2/sourdough/datagrump/books/nasa.jpg', 'r')
	file = open('/home/cells/FINAL2/sourdough/datagrump/books/car.jpg', 'r')
	#file = open('/home/cells/FINAL2/sourdough/datagrump/books/bit3H.mp4', 'r')
	#file = open('/home/cells/FINAL2/sourdough/datagrump/books/53661-0.txt', 'r')

	
	xcounter = 0
	sleeptime = 0.1

	sentDataLength = 0
	initialSend = True
	while 1:
		#ControlLoop1Changed = True
		while ControlLoop1Changed or ControlLoop2Changed:
			#time.sleep(0.01)
			
			if serialNum > 999999:
				serialNum = 0

			serialNum = serialNum + 1

			message = file.read(1200)
			if message == '' or sys.getsizeof(message)<1234:
				print "message less than read size"
				time.sleep(5)
				for x in xrange(0,XCOUNTER_MAX):
					xcounter = xcounter + 1
					data = "x" #+ str(xcounter)
					
					for i in xrange(1,1206):
						data = data + "x"
					print "x str len" + str(sys.getsizeof(data))
					UDPSock.sendto(data,addr)
					#If the read from the file is empty send 'x' -> to signify EOF
					print "tx sent pkt cnt: " + str(serialNum)
					if xcounter > XCOUNTER_MAX:
						print "EOF BREAKING"
						exit(1)

			
			data = str(serialNum).zfill(6) + message

			UDPSock.sendto(data,addr)
			#print "tx going " + str(serialNum)
			#print "leng data :" + str(sys.getsizeof(data))
			sentDataLength = len(data) + 28 + sentDataLength
			if initialSend:
				initialSend = False
				continue
			ControlLoop1Changed = False
			ControlLoop2Changed = False
			time.sleep(0.00001)
			

mqnum2= "/CL2"
mqnum1= "/CL1"

q = Queue.Queue()
ControlLoop1 = 0
ControlLoop2 = 0
t2 = threading.Thread(target=readFromCL, args = (q, mqnum1))
t2.start()
t3 = threading.Thread(target=readFromCL2, args = (q, mqnum2))
t3.start()


startSending()


