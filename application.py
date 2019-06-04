from globals import *
import time
import socket


class App:
    def __init__(self):
        self.connectionState = NET.INICIO
        self.tcp = None
        self.opponentAddr = {}
        self.oppConnMode = None

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

    def sendMessage(self, message):
        try:
            self.tcp.send(message.encode())
        except ConnectionResetError or ConnectionError or ConnectionAbortedError:
            return 'CLOSE_CONNECTION'
        except:
            return False

    def getP2PMessage(self):
        try:
            return self.tcp.recv(1024).decode()
        except TimeoutError:
            return 'TIMEOUT'
        except ConnectionResetError or ConnectionError or ConnectionAbortedError:
            return 'CLOSE_CONNECTION'
        except:
            return False

    def searchOpponent(self):

        self.sendMessage('AVAILABLE')

        timeNow = time.time()
        response = ''
        while (response == '' or response == False) and time.time() - timeNow < 20:
            response = self.getP2PMessage()
            if (response == False):
                pass
            elif response == 'CLOSE_CONNECTION':
                return False

        response = str(response).split()

        if len(response) == 3:
            self.oppConnMode = response[0]
            self.sendMessage('TRYING_TO_PLAY')
            self.opponentAddr[0] = response[1]
            self.opponentAddr[1] = response[2]
            self.connectionState = NET.ADVERSARIO_ENCONTRADO
            return True

        return False
