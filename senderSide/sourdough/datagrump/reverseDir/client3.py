import socket
import time
import posix_ipc
import binascii
import Queue
from select import select
import threading

XCOUNTER_MAX = 100

addr = ("192.168.17.22",21567)
UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
file = open('/home/cells/FINAL2/sourdough/datagrump/books/bit3H.mp4', 'r')

serialNum = 0
xcounter = 0


def readFromCL(q,mqnum1):
	global UDPSock
	global file
	global addr
	global serialNum
	global xcounter

	print "Thread readfromCL: Opening MQ " + str(mqnum1)
	mq = posix_ipc.MessageQueue(mqnum1)
	
	numberOfPacketsToSend = 2
	
	while 1:

		print "number of packets to send " + str(numberOfPacketsToSend)
		for xxxtemp in range(numberOfPacketsToSend):
			select([file],[],[])[0][0]
			message = file.read(1200)
			#print xxxtemp
			#if file empty
			if len(message) <10:
				xcounter = xcounter + 1
				data = "x" + str(xcounter)
				#select([],[UDPSock],[])[0]
				UDPSock.sendto(data,addr)

				if xcounter > XCOUNTER_MAX:
					print "EOF BREAKING"
					exit(1)
				continue

			select([],[UDPSock],[])[0]
			serialNum = serialNum + 1
			data = str(serialNum).zfill(6) + message
			UDPSock.sendto(data,addr)
		time.sleep(0.03)

		#keep waiting to listen from the message Q
		message, prio = mq.receive()
		numberOnly = message.split('\0', 1)
		numberOfPacketsToSend = int(numberOnly[0])
		


		#print str(mqnum1) + " " + str(ControlLoop1)

# def readFromCL2(q,mqnum2):
# 	print "Thread readfromCL: Opening MQ " + str(mqnum2)
# 	mq = posix_ipc.MessageQueue(mqnum2)

# 	while 1:
# 		message, prio = mq.receive()
# 		numberOnly = message.split('\0', 1)
# 		ControlLoop2 = int(numberOnly[0])
# 		#print str(mqnum2) + " " + str(ControlLoop2)


# def startSending():
# 	global ControlLoop1
# 	global ControlLoop2
	
# 	#data = "\n"
# 	serialNum = 0
# 	# Simply set up a target address and port ...

# 	# ... and send data out to it!`	
# 	#file = open('/home/cells/FINAL2/sourdough/datagrump/books/53661-0.txt', 'r')
	

# 	xcounter = 0
# 	sleeptime = 0.1
# 	while True:
# 		message = file.read(1200)
# 		if message == '':
# 			xcounter = xcounter + 1
# 			data = "x" + str(xcounter)
# 			UDPSock.sendto(data,addr)
# 			if xcounter > 1:
# 				print "EOF BREAKING"
# 				break
# 		serialNum = serialNum + 1
# 		data = str(serialNum).zfill(6) + message

		
# 		UDPSock.sendto(data,addr)

# 		if serialNum > 999999:
# 			serialNum = 0

# 		print ControlLoop1 + ControlLoop2
# 		if ControlLoop1 == 0:
# 			time.sleep(sleeptime/(ControlLoop2))
# 			continue

# 		if ControlLoop2 == 0:
# 			time.sleep(sleeptime/(ControlLoop1))
# 			ControlLoop2 = 1
# 			continue
		
# 		if ControlLoop2 == 0 and ControlLoop1 == 0:
# 			time.sleep(0.4)
# 			continue
		
# 		time.sleep(sleeptime/(ControlLoop1+ControlLoop2))
# 		# print "CL :" + str(ControlLoop)
# 		# print "STIME" + str(sleeptime)



mqnum2= "/CL2"
mqnum1= "/CL1"

q = Queue.Queue()
ControlLoop1 = 1
ControlLoop2 = 1
t2 = threading.Thread(target=readFromCL, args = (q, mqnum1))
t2.start()
# t3 = threading.Thread(target=readFromCL, args = (q, mqnum1))
# t3.start()


#startSending()


