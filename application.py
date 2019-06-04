from globals import NET


class App:
    def __init__(self):
        self.connectionState = NET.INICIO
        self.tcp = None

    def conectToServer(self):
        try:
            self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp.connect(server)
            self.tcp.setblocking(False)
            self.connectionState = NET.BUSCANDO_ADVERSARIO
            return True
        except:
            self.connectionState = NET.FALHA_NA_CONEXÃO
            return False

    def sendMessage(self, client, message):
        try:
            client.send(message.encode())
        except ConnectionResetError | ConnectionError | ConnectionAbortedError:
            return 'CLOSE_CONNECTION'
        except:
            return False
