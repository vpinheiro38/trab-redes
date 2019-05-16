
import socket
import threading
from api import *

clientQueue = Queue()
state = ['']
bind_ip = ''
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
        clientQueue.enqueue(client)
        print('[*] Cliente %s:%d disponível' %(addr[0], addr[1]))
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

            print('[*] Cliente %s:%d não conseguiu se conectar com jogador' %(addr[0], addr[1]))

            checkQueue()

    return clientThread, False

def handle_client(client_socket, addr):
    close = False
    clientThread = None
    
    while close == False:
        request = getClientP2PMessage(client_socket)
        print ('[*] Recebido: %s' %request)
        
        if request != '':
            clientThread, close = checkClientMessage(clientThread, client_socket, request, addr)
        else:
            close = True

    clientQueue.delete(clientThread)
    client_socket.close()

    for i in clientQueue.queue:
        print('%s %s' %(i.getIP(), i.getPort()), end=' - ')

def makeAvailability(client1, client2):
    global clientQueue
    ip1 = client1.getIP()
    port1 = 5101
    conn1 = client1.getServerConnection()
    conn2 = client2.getServerConnection()

    try:
        sendClientP2PMessage(conn1, 'WAIT_CONNECTION %s %s' %(ip1, port1))
    except:
        clientQueue.delete(client1)
        return False
    try:
        sendClientP2PMessage(conn2, 'TRY_CONNECTION %s %s' %(ip1, port1))
    except:
        clientQueue.delete(client2)
        return False

    return True

def checkQueue():
    global clientQueue
    threadLock.acquire()
    
    print("[*] Checando fila. Tam.: %d" %len(clientQueue.queue))
    
    if (clientQueue.size() > 1):
        success = False
        while success == False:
            
            client1 = clientQueue.dequeue()
            client2 = clientQueue.dequeue()

            if (client1 == False or client2 == False):
                return
            
            client1.setTryClient(client2)
            client2.setTryClient(client1)

            success = makeAvailability(client1, client2)
    
    print("[*] Checagem terminada. Tam.: %d" %len(clientQueue.queue))
    threadLock.release()

while True:
    client, addr = tcp.accept()
    print ('[*] Conexão aceita de : %s:%d' %(addr[0], addr[1]))
    client_handler = threading.Thread(target=handle_client, args=(client, addr,))
    client_handler.start()

    checkQueue()
