from Transport.Socket import *
sla2 = Socket("localhost", 5001)

print(sla2.sourceIp, sla2.sourcePort)

sla2.accept()