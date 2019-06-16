from Transport.Socket import *
sla2 = Socket("localhost", 5001)

print(sla2.sourceIp, sla2.sourcePort)

sla2.accept()
data = sla2.recieve()
print("teste2", data)