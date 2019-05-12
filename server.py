
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
    try: return conn.recv(sizeofmessage).decode()
    except: return ''

def sendClientP2PMessage(conn, message):
    try: conn.send(message.encode())
    except: print('[*] Mensagem não enviada - %s' %message)

def checkClientMessage(clientThread, client_socket, message, addr):
    msg = message.split()
    if (msg[0] == 'AVAILABLE' and clientThread == None):
        client = Client(addr, client_socket)
        if (clientQueue.enqueue(client)):
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

            checkQueue()

    return clientThread, False

def handle_client(client_socket, addr):
    close = False
    clientThread = None
    
    while close == False:
        request = client_socket.recv(1024)
        request = request.decode()
        print ('[*] Recebido: %s' %request)
        
        clientThread, close = checkClientMessage(clientThread, client_socket, request, addr)

def makeAvailability(client1, client2):
    ip1 = client1.getIP()
    port1 = client1.getPort()
    conn1 = client1.getServerConnection()
    conn2 = client2.getServerConnection()

    sendClientP2PMessage(conn1, 'WAIT_CONNECTION %s %s' %(ip1, port1))
    sendClientP2PMessage(conn2, 'TRY_CONNECTION %s %s' %(ip1, port1))

def checkQueue():
    threadLock.acquire()
    if (clientQueue.size() > 1):
        print("[*] Check Queue")
        client1 = clientQueue.dequeue()
        client2 = clientQueue.dequeue()
        print("[*] Client 1 = %s"%(client1))
        print("[*] Client 2 = %s"%(client2))
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