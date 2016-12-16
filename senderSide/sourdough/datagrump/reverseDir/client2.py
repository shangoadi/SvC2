import socket
import time
import posix_ipc
import binascii
import Queue
import threading

# This is an example of a UDP client - it creates
# a socket and sends data through it
# create the UDP socket
XCOUNTER_MAX = 1

ControlLoop1=1
ControlLoop2=1

def readFromCL(q,mqnum1):
	global ControlLoop1
	print "Thread readfromCL: Opening MQ " + str(mqnum1)
	mq = posix_ipc.MessageQueue(mqnum1)

	while 1:
		message, prio = mq.receive()
		numberOnly = message.split('\0', 1)
		ControlLoop1 = int(numberOnly[0])
		#print str(mqnum1) + " " + str(ControlLoop1)
def readFromCL2(q,mqnum2):
	global ControlLoop2
	print "Thread readfromCL: Opening MQ " + str(mqnum2)
	mq = posix_ipc.MessageQueue(mqnum2)

	while 1:
		message, prio = mq.receive()
		numberOnly = message.split('\0', 1)
		ControlLoop2 = int(numberOnly[0])
		#print str(mqnum2) + " " + str(ControlLoop2)


def startSending():
	global ControlLoop1
	global ControlLoop2
	UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	#data = "\n"
	serialNum = 0
	# Simply set up a target address and port ...
	addr = ("192.168.17.22",21567)
	# ... and send data out to it!`	
	file = open('/home/cells/FINAL2/sourdough/datagrump/books/53661-0.txt', 'r')
	#file = open('/home/cells/FINAL2/sourdough/datagrump/books/bit2.mp4', 'r')

	xcounter = 0
	sleeptime = 0.1
	while True:
		message = file.read(1200)
		if message == '':
			xcounter = xcounter + 1
			data = "x" + str(xcounter)
			UDPSock.sendto(data,addr)
			#If the read from the file is empty send 'x' -> to signify EOF
			#in case x gets lost in transit send, increase xcounter
			if xcounter > 1:
				print "EOF BREAKING"
				break
		serialNum = serialNum + 1
		data = str(serialNum).zfill(6) + message

		
		UDPSock.sendto(data,addr)

		if serialNum > 999999:
			serialNum = 0

		print ControlLoop1 + ControlLoop2
		if ControlLoop1 == 0:
			time.sleep(sleeptime/(ControlLoop2))
			continue

		if ControlLoop2 == 0:
			time.sleep(sleeptime/(ControlLoop1))
			ControlLoop2 = 1
			continue
		
		if ControlLoop2 == 0 and ControlLoop1 == 0:
			time.sleep(0.4)
			continue
		
		time.sleep(sleeptime/(ControlLoop1+ControlLoop2))
		# print "CL :" + str(ControlLoop)
		# print "STIME" + str(sleeptime)



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


