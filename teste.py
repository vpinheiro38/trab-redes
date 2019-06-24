from transport.Socket import *

sla = Socket()

print(sla.sourceIp, sla.sourcePort)

sla.connect("localhost", 5001)

while True:
    msg = str(input())
    sla.send(msg)