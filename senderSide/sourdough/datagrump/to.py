from subprocess import Popen, PIPE
from sys import argv

input = ' '.join(argv[1:])
if not input: input = "no arguments given"
cproc = Popen("./sender", stdin=PIPE, stdout=PIPE)
out, err = cproc.communicate(input)
print "output:", out
print "errors:", err