import socket, pickle
import threading

class PhysicalLayer:
    def __init__(self):
        self.selectedPort = 0
        self.rcvBuffer = []
        self.thread = threading.Thread(target=self.rcvBits, daemon=True) # Daemon = Termina a thread quando o código/processo termina
        self.thread.start()

    def sendBits(self, data, destIP):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.selectedPort == 0:
            return False

        dest = (destIP, self.selectedPort)
        data_bytes = pickle.dumps(data)
        udp.sendto(data_bytes, (dest))
        udp.close()
        return True

    def rcvBits(self, address='localhost'):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        orig = (address, self.selectedPort)
        udp.bind(orig)
        self.selectedPort = udp.getsockname()[1]
        #print(udp.getsockname()) # Socket diferente do sendBits
        while True:
            data_bytes = udp.recvfrom(1024)
            data = (pickle.loads(data_bytes[0]), data_bytes[1])
            self.rcvBuffer.append(data)

        udp.close()

    def getData(self):
        if self.rcvBuffer.count() > 0:
            return self.rcvBuffer.pop(0)
        return None
        
while True: continue