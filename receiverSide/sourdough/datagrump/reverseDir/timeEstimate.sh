#wait till all the running process die and print the total received data 
#!/bin/bash


FAIL=0

echo "starting"


time python ./server2.py &
IF=toto0
 
#read stats before test begins
R1=`cat /sys/class/net/toto0/statistics/rx_bytes`
T1=`cat /sys/class/net/toto0/statistics/tx_bytes`



for job in `jobs -p`
do
echo $job
    wait $job || let "FAIL+=1"
done

echo $FAIL

if [ "$FAIL" == "0" ];
then
echo "Successfully completed jobs"
else
echo "FAIL! ($FAIL)"
fi

R2=`cat /sys/class/net/toto0/statistics/rx_bytes`
T2=`cat /sys/class/net/toto0/statistics/tx_bytes`
TBPS=`expr $T2 - $T1`
RBPS=`expr $R2 - $R1`
#TKB=`expr $TBPS / 1024`
#RKB=`expr $RBPS / 1024`
TKB=`expr $TBPS`
RKB=`expr $RBPS`
echo "TX $1: $TKB kB RX $1: $RKB kB"


