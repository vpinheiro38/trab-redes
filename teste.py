from Transport.Socket import *

sla = Socket()

print(sla.sourceIp, sla.sourcePort)

sla.connect("localhost",5001)