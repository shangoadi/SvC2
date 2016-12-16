#!/bin/bash



# sudo killall sender
# sudo killall receiver
sudo killall python
sudo ./kill_ipc.sh
#sudo python ./IPC/cleaner.py	

#sudo ./receiver 1255&

sudo python ./tunproxy.py -c 50.78.21.22:1231 &
sleep 2
#setup the tunnel
sudo ifconfig toto0 192.168.17.21 txqueuelen 1000000
sudo ip route add 192.168.17.0/24 dev toto0
sleep 1

# wlan0IP="$(ifconfig wlan0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
# sudo python ./echoClient.py 50.78.21.22 $1 /68681 /CL1 $wlan0IP 0&

# wlan1IP="$(ifconfig wlan1 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
# sudo python ./echoClient.py 50.78.21.22 $2 /68682 /CL2 $wlan1IP 0&

wwan0IP="$(ifconfig wwan0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
sudo python ./echoClient.py 50.78.21.22 $1 /68681 /CL1 $wwan0IP 0&

 eth1IP="$(ifconfig eth1 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
sudo python ./echoClient.py 50.78.21.22 $2 /68682 /CL2 $eth1IP 0&