import socket
import time
import posix_ipc
import binascii
import Queue
import threading

# This is an example of a UDP client - it creates
# a socket and sends data through it
# create the UDP socket
XCOUNTER_MAX = 100

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
		ControlLoop1Changed = True
		numberOnly = message.split('\0', 1)
		ControlLoop1 = int(numberOnly[0])
		#print str(mqnum1) + " " + str(ControlLoop1)
def readFromCL2(q,mqnum2):
	global ControlLoop2
	global ControlLoop2Changed
	print "Thread readfromCL: Opening MQ " + str(mqnum2)
	mq = posix_ipc.MessageQueue(mqnum2)

	while 1:
		message, prio = mq.receive()
		ControlLoop2Changed = True
		numberOnly = message.split('\0', 1)
		ControlLoop2 = int(numberOnly[0])
		#print str(mqnum2) + " " + str(ControlLoop2)


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
	#file = open('/home/cells/FINAL2/sourdough/datagrump/books/53661-0.txt', 'r')
	file = open('/home/cells/FINAL2/sourdough/datagrump/books/bit3H.mp4', 'r')

	xcounter = 0
	sleeptime = 0.1
	while True:
		if serialNum > 999999:
			serialNum = 0

		if ControlLoop1Changed and ControlLoop2Changed:
			for pktRqstd in range((ControlLoop2+ControlLoop1)):
				message = file.read(1200)
				if message == '':
					xcounter = xcounter + 1
					data = "x" + str(xcounter)
					UDPSock.sendto(data,addr)
					#If the read from the file is empty send 'x' -> to signify EOF
					#in case x gets lost in transit send, increase xcounter
					if xcounter > XCOUNTER_MAX:
						print "EOF BREAKING"
						exit(1)
					continue
				serialNum = serialNum + 1
				data = str(serialNum).zfill(6) + message
				time.sleep(0.1/(ControlLoop1 + ControlLoop2))
				UDPSock.sendto(data,addr)
			ControlLoop1Changed = False
			ControlLoop2Changed = False
			continue
		if ControlLoop1Changed:
			for pktRqstd in range(ControlLoop1):
				message = file.read(1200)
				if message == '':
					xcounter = xcounter + 1
					data = "x" + str(xcounter)
					UDPSock.sendto(data,addr)
					#If the read from the file is empty send 'x' -> to signify EOF
					#in case x gets lost in transit send, increase xcounter
					if xcounter > XCOUNTER_MAX:
						print "EOF BREAKING"
						exit(1)
					continue
				serialNum = serialNum + 1
				data = str(serialNum).zfill(6) + message
				time.sleep(0.1/ControlLoop1)
				UDPSock.sendto(data,addr)
			ControlLoop1Changed = False
			continue
		if ControlLoop2Changed:
			for pktRqstd in range(ControlLoop2):
				message = file.read(1200)
				if message == '':
					xcounter = xcounter + 1
					data = "x" + str(xcounter)
					UDPSock.sendto(data,addr)
					#If the read from the file is empty send 'x' -> to signify EOF
					#in case x gets lost in transit send, increase xcounter
					if xcounter > XCOUNTER_MAX:
						print "EOF BREAKING"
						exit(1)
					continue
				serialNum = serialNum + 1
				data = str(serialNum).zfill(6) + message
				time.sleep(0.1/ControlLoop2)
				UDPSock.sendto(data,addr)
			ControlLoop2Changed = False
			continue
		print "Looks like Controlloop 1 or 2 havent changed so I will sleep for 20ms"
		time.sleep(0.02)



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


