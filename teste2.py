from transport.Socket import *
import threading
sla2 = Socket("localhost", 5001)

def server(conn):
    while True:
        if len(conn.appBuffer):
            data = conn.appBuffer.pop(0)
            print(data)

print(sla2.sourceIp, sla2.sourcePort)
sla2.listen()

while True:
    socket = sla2.accept()
    thread = threading.Thread(target=server, args=(socket, ))
    thread.start()



# sla2.close()