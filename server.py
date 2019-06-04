import socket
import threading
from api import Queue
from api import Client

ID = 0
clientQueue = Queue()
bind_ip = ''
bind_port = 5100
sizeofmessage = 1024

threadLock = threading.Lock()
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind((bind_ip, bind_port))
tcp.listen(5)

print('[*] Escutando %s:%d' % (bind_ip, bind_port))


def getClientP2PMessage(conn):
    try:
        return conn.recv(sizeofmessage).decode()
    except:
        return ''


def sendClientP2PMessage(conn, message):
    try:
        conn.send(str(message).encode())
    except:
        print('[*] Mensagem não enviada - %s' % message)


def checkClientMessage(clientThread, client_socket, message, addr, id):
    msg = message.split()
    if (msg[0] == 'AVAILABLE' and clientThread == None):
        if(id):
            addr = askForSocket(client_socket).split()
            addr[1] = int(addr[1])
        else:
            sendClientP2PMessage(client_socket, 0)

        client = Client(addr, client_socket, id)
        clientQueue.enqueue(client)
        print('[*] Cliente %s:%d disponível' % (addr[0], addr[1]))
        checkQueue()
        return client, False

    elif msg[0] == 'PLAYING':
        client_socket.close()
        print('[*] Fechando conexão com %s:%d' % (addr[0], addr[1]))
        return clientThread, True

    return clientThread, False

def askForSocket(clientSocket):
    sendClientP2PMessage(clientSocket, 1)
    request = getClientP2PMessage(clientSocket)
    return request


def handle_client(client_socket, addr, ID):
    close = False
    clientThread = None

    

    while close == False:
        request = getClientP2PMessage(client_socket)
        print('[*] Recebido: %s' % request)

        if request != '':
            clientThread, close = checkClientMessage(
                clientThread, client_socket, request, addr, ID)
        else:
            close = True

    clientQueue.delete(clientThread)
    client_socket.close()

    for i in clientQueue.queue:
        print('%s %s' % (i.getIP(), i.getPort()), end=' - ')


def makeAvailability(client1, client2):
    global clientQueue
    ip = 0
    port = 0
    if(client1.id):
        ip = client1.getIP()
        port = client1.getPort()
    else:
        ip = client2.getIP()
        port = client2.getPort()
    conn1 = client1.getServerConnection()
    conn2 = client2.getServerConnection()
    
    try:
        sendClientP2PMessage(conn1, '%s %s' % (ip, port))
    except:
        clientQueue.delete(client1)
        return False
    try:
        sendClientP2PMessage(conn2, '%s %s' % (ip, port))

    except:
        clientQueue.delete(client2)
        return False

    return True


def checkQueue():
    global clientQueue
    threadLock.acquire()

    print("[*] Checando fila. Tam.: %d" % len(clientQueue.queue))

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

    print("[*] Checagem terminada. Tam.: %d" % len(clientQueue.queue))
    threadLock.release()


while True:
    client, addr = tcp.accept()
    ID = (ID == 0)
    print('[*] Conexão aceita de : %s:%d' % (addr[0], addr[1]))
    client_handler = threading.Thread(
        target=handle_client, args=(client, addr,ID))
    client_handler.start()

    checkQueue()
