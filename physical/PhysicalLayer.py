import socket, pickle
import threading

class PhysicalLayer:
    def __init__(self, link, ip='localhost', port=0):
        self.linkLayer = link
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.selectedIP = ip
        self.selectedPort = port
        self.rcvBuffer = []
        self.thread = threading.Thread(target=self.rcvBits, daemon=True) # Daemon = Termina a thread quando o código/processo termina
        # self.thread.start()

    def initPort(self, ip, port):
        try:
            self.selectedIP = ip
            self.selectedPort = port
            self.udp.bind((self.selectedIP, self.selectedPort))
            self.thread.start()
            return True
        except:
            return False

    def sendBits(self, data, destAddress):
        if self.selectedPort == 0:
            return False

        dest = (destAddress[0], destAddress[1])
        data_bytes = pickle.dumps(data)
        # print("SendBits: ", data, dest)
        self.udp.sendto(data_bytes, (dest))
        return True

    def rcvBits(self):
        self.selectedIP = self.udp.getsockname()[0]
        self.selectedPort = self.udp.getsockname()[1]
        # print('RcvBits: ', self.udp.getsockname()) # Socket diferente do sendBits
        while True:
            data_bytes = self.udp.recvfrom(1024)
            data = (pickle.loads(data_bytes[0]), data_bytes[1])
            self.linkLayer.rcvBuffer.append(data)

    # def getData(self):
    #     if len(self.rcvBuffer):
    #         return self.rcvBuffer.pop(0)
    #     return None

    def close(self):
        self.udp.close()