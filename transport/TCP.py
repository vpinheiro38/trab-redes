class TCP:
    def __init__(self):
        self.freePorts = list(range(1024, 65535))

    def getFreePort(self):
        freePort = self.freePorts[0]
        del self.freePorts[0]
        return freePort


tcp = TCP()
