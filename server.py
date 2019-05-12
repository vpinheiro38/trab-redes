import socket
import threading
from api import *

clientQueue = Queue()
state = ['']
bind_ip = 'localhost'
bind_port = 5100
sizeofmessage = 1024

threadLock = threading.Lock()

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind((bind_ip,bind_port))
tcp.listen(5)
print ('[*] Escutando %s:%d' %(bind_ip,bind_port))

def getClientP2PMessage(conn):
    try: return conn.recv(sizeofmessage)
    except: return ''

def sendClientP2PMessage(conn, message):
    try: conn.send(message)
    except: print('[*] Mensagem não enviada - %s' %message)

def checkClientMessage(clientThread, client_socket, message, addr):
    msg = message.split()
    if (msg[0] == 'AVAILABLE'):
        client = Client(msg[1], addr, client_socket)
        if clientQueue.enqueue(client):
            print('[*] Cliente %s:%d disponível\n' %(addr[0], addr[1]))
            checkQueue()
        return client, False
    elif msg[0] == 'PLAYING':
        client_socket.close()
        print('[*] Fechando conexão com %s:%d' %(addr[0], addr[1]))
        return clientThread, True
    elif msg[0] == 'ERROR':
        if (msg[1] == '0' and clientThread != None):
            clientQueue.enqueue(clientThread)
            clientQueue.enqueue(clientThread.getTryClient())
            clientThread.setTryClient(None)
            clientThread.getTryClient().setTryClient(None)

            print('[*] Cliente %s:%d não conseguiu se conectar com jogador\n' %(addr[0], addr[1]))

    return clientThread, False

def handle_client(client_socket, addr):
    close = False
    clientThread = None
    
    while close == False:
        request = client_socket.recv(1024)
        request = request.decode()
        print ('[*] Recebido: %s' %request)
        
        clientThread, close = checkClientMessage(clientThread, client_socket, request, addr)
        
        msg = ('ACK - %s' %request)
        byte = msg.encode()
        try:
            client_socket.send(byte)
        except:
            return

def makeAvailability(client1, client2):
    ip1 = client1.getIP()
    name1 = client1.getName()
    conn2 = client2.getServerConnection()

    sendClientP2PMessage(conn2, 'TRY_CONNECTION %s %s' %(name1, ip1))

def checkQueue():
    threadLock.acquire()
    if (clientQueue.size() > 1):
        print("[*] Check Queue")
        client1 = clientQueue.dequeue()
        client2 = clientQueue.dequeue()

        client1.setTryClient(client2)
        client2.setTryClient(client1)

        makeAvailability(client1, client2)
    threadLock.release()

while True:
    client, addr = tcp.accept()
    print ('[*] Conexão aceita de : %s:%d' %(addr[0], addr[1]))
    client_handler = threading.Thread(target=handle_client, args=(client, addr,))
    client_handler.start()

    checkQueue()