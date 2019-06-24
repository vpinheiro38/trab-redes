from transport.Socket import *
sla2 = Socket("localhost", 5001)

print(sla2.sourceIp, sla2.sourcePort)

sla2.accept()

while True:
    if len(sla2.appBuffer):
        data = sla2.appBuffer.pop(0)
        print(data)

# sla2.close()