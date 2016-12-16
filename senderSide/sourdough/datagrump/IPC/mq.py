import sysv_ipc
import time


memory = sysv_ipc.MessageQueue(6868, sysv_ipc.IPC_CREAT | 0666)

while True:
    memory.send("testa")
    time.sleep(0.5)

# receive([block = True, [type = 0]])

# remove()
#     Removes (deletes) the message queue. 




