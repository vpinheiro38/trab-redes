from Transport.Socket import *
sla2 = Socket("localhost", 5001)

print(sla2.sourceIp, sla2.sourcePort)

sla2.accept()

for i in range(2000):
    data = sla2.recieve()
    print("teste2", data)