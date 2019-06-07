from globals import *
import socket
import time
import threading


class App:
    def __init__(self):
        self.connectionState = NET.INICIO
        self.serverSocket = None
        self.opponentAddr = {}
        self.oppConnMode = None
        self.p2pSocket = None
        self.choosenSocket = None
        self.response = None

    def conectToServer(self):
        try:
            self.serverSocket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.serverSocket.connect(server)
            self.serverSocket.setblocking(False)
            self.connectionState = NET.BUSCANDO_ADVERSARIO
            return True
        except:
            self.connectionState = NET.FALHA_NA_CONEXÃO
            return False

    def sendMessage(self, addr, message):
        try:
            addr.send(message.encode())
        except ConnectionResetError or ConnectionError or ConnectionAbortedError:
            return 'CLOSE_CONNECTION'
        except:
            return False

    def getMessage(self, socket):
        try:
            return socket.recv(1024).decode()
        except TimeoutError:
            return 'TIMEOUT'
        except ConnectionResetError or ConnectionError or ConnectionAbortedError:
            return 'CLOSE_CONNECTION'
        except:
            return False

    def searchOpponent(self):
        self.sendMessage(self.serverSocket, 'AVAILABLE')
        timeNow = time.time()
        response = ''

        while (response == '' or response == False) and time.time() - timeNow < 20:
            response = self.getMessage(self.serverSocket)
            if (response == False):
                pass
            elif response == 'CLOSE_CONNECTION':
                return False

        response = str(response).split()
        if len(response) == 1 and response[0] == 'WAIT_CONNECTION':
            print("RESPOSTINHA ", response)
            self.choosenSocket = self.getSocketP2P()
            addr = self.choosenSocket.getsockname()
            self.oppConnMode = 'WAIT_CONNECTION'
            self.sendMessage(self.serverSocket, 'SOCKET %s %s' % (str(addr[0]), str(addr[1])))
        elif len(response) == 1 and response[0] == 'TRY_CONNECTION':
            self.oppConnMode = 'TRY_CONNECTION'
        else:
            return False

        response = ''
        timeNow = time.time()
        while (response == '' or response == False) and time.time() - timeNow < 20:
            response = self.getMessage(self.serverSocket)
            if (response == False):
                pass
            elif response == 'CLOSE_CONNECTION':
                return False

        response = str(response).split()
        if len(response) == 3 and response[0] == 'CONNECT':
            self.sendMessage(self.serverSocket, 'TRYING_TO_PLAY')
            print("addr ", response[1], response[2])
            self.opponentAddr[0] = response[1]
            self.opponentAddr[1] = response[2]
            self.connectionState = NET.ADVERSARIO_ENCONTRADO
            return True

        return False

    def conectaAdversario(self):
        if(self.oppConnMode == 'TRY_CONNECTION'):
            success = self.connectAsClientP2P(
                self.opponentAddr[0], int(self.opponentAddr[1]))
            print('Sucesso?', success)
        else:
            success = self.waitConnection(self.choosenSocket)
            print('Sucesso?', success)
        if(success == True):
            self.sendMessage(self.serverSocket, 'PLAYING')
            self.serverSocket.close()
            self.connectionState = NET.PRONTO_PARA_JOGAR
            return True

        return False

    def getSocketP2P(self):
        connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connectionSocket.bind(('localhost', 0))
        choosenSocket = connectionSocket.getsockname()
        print("[*] Escutando  %s : %d" % (choosenSocket[0], choosenSocket[1]))
        connectionSocket.listen(5)
        return connectionSocket

    def waitConnection(self, connectionSocket):
        try:
            self.p2pSocket, addr = connectionSocket.accept()
            print('Connection accepted', addr)
            connectionThread = threading.Thread(
                target=self.handle_conn)
            connectionThread.start()
            return True

        except:
            return False

        return True

    def connectAsClientP2P(self, ip, port):
        self.p2pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time.sleep(2)
        try:
            self.p2pSocket.connect((ip, port))
            print("[*] Conectando %s : %d" % (ip, port))
            connectionThread = threading.Thread(
                target=self.handle_conn)
            connectionThread.start()
            return True
        except:
            return False

        return True

    def handle_conn(self):

        while True:
            response = self.getMessage(self.p2pSocket)

            if response == 'CLOSE_CONNECTION':
                self.connectionState = NET.FALHA_NA_CONEXÃO
                break

            if (response != False):
                if (response == ''):
                    break
                print('[*] Recebido: %s' % response)
                self.response = response

        self.p2pSocket.close()

    def closeServerConnection(self):
        print("Closing conection: ", self.serverSocket)
        self.serverSocket.close()
        self.connectionState = NET.INICIO

    def closeP2PConnection(self):
        self.sendMessage(self.p2pSocket, 'CLOSE_CONNECTION')
        print("Closing conection: ", self.p2pSocket)
        self.p2pSocket.close()
        self.connectionState = NET.INICIO

    def makeMove(self, linha, coluna):
        self.sendMessage(self.p2pSocket, 'CLICKED %s %s' % (linha, coluna))

    def playAgain(self):
        self.sendMessage(self.p2pSocket, 'PLAY_AGAIN')
