# SvC2

README:
--------

1. The sender and receiver files have been merged together into a single process. The make file has been modified so as  	to accomodate the compilation into a single binary "sender" instead of 2 seperates binaries, sender and receiver. This 
   has been done to assist in future modifications that would assist a mechanism similar to hole punching that would allow
   for bi-directional communication. For now the test fixture is designed to work one way only.

2. Sender.cc has been modified to allow for the following commandline arguments:
   1. destinationIP, 2. DestionationPort, 3. debug, 4. ListenPort, 5. SenderBindIP, 6.SenderBindPort, 7. MessageQueueIDTx
   8. MessageQueueIDRx 9. MessageQueueIDFeedBackLoop1 10. MessageQueueIDFeedBackLoop2
   Sender.cc has also been modified to accomodate to send the data content received on MessageQueueIDTx and to place the 
   estimated TxWindow size onto MessageQueueIDFeedBackLoop1 and MessageQueueIDFeedBackLoop2

3. Receiver.cc has been modified so as to receive the packets and place the received packets onto MessageQueueIDRx

4. Tunproxy.py is used to read messages between the sender and receiver message queues and to copy them safely to and from
   the /dev/net/tun file descriptor. The tunproxy.py does not take any arguments as of now the MessageQueueuIDs are stati-
   -cally placed in the code.

5. The client and server processes in the /reverseDir use the information on the MessageQueueIDFeedBackLoop1 and Loop2 to 
   produce and consume right number of packets.

6. simpleReceiver. The simpleReceiver and simpleSender scripts configure the sender and receiver and tunproxy process app

HOW TO RUN:
-----------
1. Configure routes on the sender side to allow for 2 default routes by running
   sudo ./autoConfScript

2. After making sure that the ports are open on the public IP (receiver side), the receiver may be started with:
   a. sudo ./simpleReceiver & 
   
3. make sure that the routes on the sender are setup properly by performing an interface specific ping test
   ex: ping www.google.com -I wwan0   (for wwan0)
   after which start the Sender by
   a. sudo ./simpleSender &

4. Start server process behind the tunnel interface on the receiver side in the reverseDir.
   sudo server.py

5. Start the client process behind the tunnel on the sender side in the reverseDir.
   sudo client.py


