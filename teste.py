from transport.Socket import *

sla = Socket()

print(sla.sourceIp, sla.sourcePort)

sla.connect("localhost", 5001)
for i in range(2000):
    sla.send("oi")