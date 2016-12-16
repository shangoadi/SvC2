import posix_ipc

mqnum = "/68681"
mqnum2= "/89898"

mq = posix_ipc.MessageQueue(mqnum)
mq2 = posix_ipc.MessageQueue(mqnum2)
mq.unlink()
mq2.unlink()