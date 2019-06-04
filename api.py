class Queue:
    def __init__(self):
        self.queue = list()

    def enqueue(self, data):
        if data not in self.queue:
            self.queue.insert(0, data)

    def dequeue(self):
        if (len(self.queue) > 0):
            return self.queue.pop()

        return False

    def delete(self, socket):
        for i in range(self.queue.count(socket)):
            self.queue.remove(socket)

    def size(self):
        return len(self.queue)

    def findClient(self, client):
        return self.queue.index(client)

    def findClientByAddr(self, addr):
        for a in self.queue:
            if (a.getIP() == addr[0]):
                return a


class Client:
    def __init__(self, addr, server_conn):
        self.addr = addr
        self.server_conn = server_conn

    def getIP(self):
        return self.addr[0]

    def getPort(self):
        return self.addr[1]

    def getAddr(self):
        return self.addr

    def getServerConnection(self):
        return self.server_conn

    def setTryClient(self, client):
        self.tryclient = client

    def getTryClient(self):
        return self.tryclient