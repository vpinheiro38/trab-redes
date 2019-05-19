from graphics import *
import sys
import time
import threading
from enum import Enum
import socket
from api import *

sizeofmessage = 1024
deftimeout = 20
HOST = 'localhost'     # Endereco IP do Servidor
PORT = 5100            # Porta que o Servidor esta
tcp = None
clientTcp = None
server = (HOST, PORT)

opponentAddr = [None, None]
# Como o cliente irá se conectar com o oponente (enviar ou receber conexão)
oppConnMode = 'TRY_CONNECTION'
oppConn = None

actualCmd = ''

estadoNet = None
jogadorAtual = None
estadoAtual = None
tabuleiro = None
message = None
LINHAS = 3
COLUNAS = 3
CELL_SIZE = 200
WIDTH = CELL_SIZE * COLUNAS
HEIGHT = CELL_SIZE * LINHAS
GRID_WIDTH = 8
GRID_WIDHT_HALF = GRID_WIDTH / 2
CELL_PADDING = CELL_SIZE / 6
TAM_SIMBOLO = CELL_SIZE - CELL_PADDING * 2
GROSSURA_SIMBOLO = 8
TEXT_SIZE = 36

canvas = GraphWin("Jogo da Velha", WIDTH, HEIGHT+TEXT_SIZE)

class NET(Enum):
    INICIO = 1
    CONECTANDO_SERVIDOR = 2
    FALHA_NA_CONEXÃO = 3
    BUSCANDO_ADVERSARIO = 4
    TIMEOUT = 5
    ADVERSARIO_ENCONTRADO = 6
    PRONTO_PARA_JOGAR = 7


class gameState(Enum):
    PLAYING = 1
    EMPATE = 2
    X_GANHOU = 3
    O_GANHOU = 4


class Cell(Enum):
    EMPTY = 1
    X = 2
    O = 3

# TELAS
# INICIO - BOTAO PARA PROCURAR ADVERSÁRIO
# TENTANDO SE CONECTAR COM SERVIDOR
# CONEXÃO FALHOU
# BUSCANDO ADVERSARIO
# TIMEOUT
# ADVERSARIO ENCONTRADO TENTANDO SE CONECTAR
# TIMEOUT
# INICIO DO GAME

# MENSAGENS SOBRE JOGADAS

def wait(sec):
    timeNow = time.time()
    while time.time() - timeNow < sec:
        canvas.checkMouse()

def closeWindow(conn):
    sendP2PMessage(conn, 'CLOSE_CONNECTION')
    sys.exit()

def connectAsClientP2P(ip, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    wait(2)

    try:
        client.connect((ip, port))
        print("connect %s : %d" % (ip, port))
        client.settimeout(60)
        # sendP2PMessage(client, 'CONNECTED')
        # response = getP2PMessage(client)

        conn_handler = threading.Thread(target=handle_conn, args=(client,))
        conn_handler.start()
    except:
        return None, False

    return client, True


def createServerP2P(ip, port):
    global clientTcp, deftimeout
    clientTcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("wait %s : %d" % (ip, port))
    clientTcp.bind((ip, port))
    clientTcp.listen(5)
    # clientTcp.settimeout(deftimeout)

    try:
        connection, addr = clientTcp.accept()
        print('accept')
        connection.settimeout(60)

        conn_handler = threading.Thread(target=handle_conn, args=(connection,))
        conn_handler.start()

    except:
        return None, False

    return connection, True


def handle_conn(socket):
    global actualCmd, canvas, estadoNet, oppConn

    while True:
        response = getP2PMessage(socket)
        if response == False or response == 'TIMEOUT' or response == 'CLOSE_CONNECTION':
            estadoNet = NET.FALHA_NA_CONEXÃO
            break

        if (response != False):
            if (response == ''):
                break
            print('[*] Recebido: %s' % response)
            actualCmd = response

    socket.close()
    oppConn = None


def Game():
    global estadoNet
    global message, oppConn, oppConnMode, actualCmd, canvas, tcp, clientTcp
    canvas.setBackground("white")
    message = Text(Point(WIDTH/2, HEIGHT+TEXT_SIZE/2), " ")
    message.setStyle("bold")
    estadoNet = NET.INICIO

    def animacaoEspera():
        a = 1
        # TODO: FAZER ANIMAÇAO

    def limpaTela():
        for item in canvas.items[:]:
            item.undraw()
        canvas.update()

    def drawX(x1, y1, x2, y2):
        diagonal11 = Line(Point(x1, y1), Point(x2, y2))
        diagonal11.setOutline("black")
        diagonal11.setWidth(5)
        diagonal11.draw(canvas)

        diagonal12 = Line(Point(x1, y1), Point(x2, y2))
        diagonal12.setOutline("red")
        diagonal12.setWidth(3)
        diagonal12.draw(canvas)

        diagonal21 = Line(Point(x2, y1), Point(x1, y2))
        diagonal21.setOutline("black")
        diagonal21.setWidth(5)
        diagonal21.draw(canvas)

        diagonal22 = Line(Point(x2, y1), Point(x1, y2))
        diagonal22.setOutline("red")
        diagonal22.setWidth(3)
        diagonal22.draw(canvas)

    def drawO(x, y, r):
        bolaOutline = Circle(Point(x, y), r)
        bolaOutline.setOutline("black")
        bolaOutline.setWidth(5)
        bolaOutline.draw(canvas)

        bola = Circle(Point(x, y), r)
        bola.setOutline("blue")
        bola.setWidth(3)
        bola.draw(canvas)

    def inside(point, rectangle):
        ll = rectangle.getP1()
        ur = rectangle.getP2()

        return ll.getX() < point.getX() < ur.getX() and ll.getY() < point.getY() < ur.getY()

    def drawCanvas():
        global tabuleiro
        global message
        for linha in range(1, LINHAS):
            vertical = Line(Point(0, CELL_SIZE * linha),
                            Point(WIDTH, CELL_SIZE * linha))
            vertical.setWidth(3)
            vertical.draw(canvas)

        for coluna in range(1, COLUNAS):
            horizontal = Line(Point(CELL_SIZE * coluna, 0),
                              Point(CELL_SIZE * coluna, HEIGHT))
            horizontal.setWidth(3)
            horizontal.draw(canvas)

        for linha in range(LINHAS):
            for coluna in range(COLUNAS):
                x1 = coluna * CELL_SIZE + CELL_PADDING
                y1 = linha * CELL_SIZE + CELL_PADDING
                if tabuleiro[linha][coluna] == Cell.X:
                    x2 = (coluna + 1) * CELL_SIZE - CELL_PADDING
                    y2 = (linha + 1) * CELL_SIZE - CELL_PADDING
                    drawX(x1, y1, x2, y2)
                if tabuleiro[linha][coluna] == Cell.O:
                    x = coluna * CELL_SIZE + CELL_SIZE/2
                    y = linha * CELL_SIZE + CELL_SIZE/2
                    drawO(x, y, TAM_SIMBOLO/2)

        message.setSize(TEXT_SIZE-20)
        if (estadoAtual == gameState.PLAYING):
            message.setSize(TEXT_SIZE)
            if (oppConnMode == 'TRY_CONNECTION'):
                if (jogadorAtual == Cell.X):
                    message.setText("Sua vez - X")
                else:
                    message.setText("Vez do oponente - O")
            elif (oppConnMode == 'WAIT_CONNECTION'):
                if (jogadorAtual == Cell.O):
                    message.setText("Sua vez - O")
                else:
                    message.setText("Vez do oponente - X")

        elif (estadoAtual == gameState.EMPATE):
            message.setText("É um empate! Clique para jogar novamente.")
        elif (estadoAtual == gameState.X_GANHOU):
            message.setText("'O' Ganhou! Clique para jogar novamente.")
        elif (estadoAtual == gameState.O_GANHOU):
            message.setText("'X' Ganhou! Clique para jogar novamente.")

        message.setFace("arial")
        message.undraw()
        message.draw(canvas)

    def onClick(pos):
        global tabuleiro
        global estadoAtual, oppConn
        print(estadoAtual)
        colunaSelecionada = int(pos.getX() / CELL_SIZE)
        linhaSelecionada = int(pos.getY() / CELL_SIZE)

        if estadoAtual == gameState.PLAYING:
            if (linhaSelecionada >= 0 and linhaSelecionada < LINHAS and colunaSelecionada >= 0 and colunaSelecionada < COLUNAS
                    and tabuleiro[linhaSelecionada][colunaSelecionada] == Cell.EMPTY):
                updateGame(jogadorAtual, linhaSelecionada, colunaSelecionada)

        else:
            sendP2PMessage(oppConn, 'PLAY_AGAIN')
            initGame()

    def initGame():
        global estadoAtual
        global jogadorAtual
        global tabuleiro

        limpaTela()

        estadoAtual = gameState.PLAYING
        jogadorAtual = Cell.X
        row = [Cell.EMPTY]*LINHAS
        tabuleiro = [list(row) for i in range(COLUNAS)]
        drawCanvas()

    def updateGame(player, linha, coluna):
        global estadoAtual, jogadorAtual, tabuleiro
        global message, oppConn

        sendP2PMessage(oppConn, 'CLICKED %s %s' % (linha, coluna))
        tabuleiro[linha][coluna] = player

        if (ganhou(player, linha, coluna)):
            estadoAtual = (gameState.X_GANHOU, gameState.O_GANHOU)[
                player == Cell.X]
        elif (empatou()):
            estadoAtual = gameState.EMPATE
        else:
            jogadorAtual = (Cell.X, Cell.O)[player == Cell.X]
        drawCanvas()

    def updateWaitGame(response):
        global estadoAtual, jogadorAtual, tabuleiro
        global message, oppConn, oppConnMode, actualCmd

        linha = 0
        coluna = 0
        response = response.split()
        actualCmd = ''
        if (len(response) == 3 and response[0] == 'CLICKED'):
            linha = int(response[1])
            coluna = int(response[2])

        if (oppConnMode == 'WAIT_CONNECTION'):
            player = Cell.X
        else:
            player = Cell.O

        tabuleiro[linha][coluna] = player

        if (ganhou(player, linha, coluna)):
            estadoAtual = (gameState.X_GANHOU, gameState.O_GANHOU)[
                player == Cell.X]
        elif (empatou()):
            estadoAtual = gameState.EMPATE
        else:
            jogadorAtual = (Cell.X, Cell.O)[player == Cell.X]
        drawCanvas()

    def ganhou(player, linha, coluna):
        global tabuleiro
        print(linha == coluna
              and tabuleiro[0][0] == player
              and tabuleiro[1][1] == player
              and tabuleiro[2][2] == player)

        return ((tabuleiro[linha][0] == player
                 and tabuleiro[linha][1] == player
                 and tabuleiro[linha][2] == player)
                or (tabuleiro[0][coluna] == player
                    and tabuleiro[1][coluna] == player
                    and tabuleiro[2][coluna] == player)
                or (linha == coluna
                    and tabuleiro[0][0] == player
                    and tabuleiro[1][1] == player
                    and tabuleiro[2][2] == player
                    or tabuleiro[0][2] == player
                    and tabuleiro[1][1] == player
                    and tabuleiro[2][0] == player))

    def empatou():
        global tabuleiro
        for i in range(LINHAS):
            for j in range(COLUNAS):
                if tabuleiro[i][j] == Cell.EMPTY:
                    return False
        return True

    def esperaServidor(text):
        global estadoNet
        global tcp, deftimeout
        text.draw(canvas)

        wait(2)

        try:
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp.connect(server)
            # tcp.settimeout(deftimeout)
            tcp.setblocking(False)
            estadoNet = NET.BUSCANDO_ADVERSARIO
            return True
        except:
            estadoNet = NET.FALHA_NA_CONEXÃO
            return False

    def buscaAdversario(text):
        global estadoNet
        global tcp, oppConnMode, opponentAddr, actualCmd
        text.draw(canvas)
        count = 0

        sendP2PMessage(tcp, 'AVAILABLE')

        timeNow = time.time()
        response = ''
        while (response == '' or response == False) and time.time() - timeNow < 20:
            response = getP2PMessage(tcp)
            if (response == False):
                pass
            elif response == 'CLOSE_CONNECTION':
                return False
            canvas.checkMouse()

        response = str(response).split()

        if len(response) == 3 and response[0] == 'TRY_CONNECTION':
            oppConnMode = response[0]
            sendP2PMessage(tcp, 'TRYING_TO_PLAY')
            opponentAddr[0] = response[1]
            opponentAddr[1] = response[2]
            estadoNet = NET.ADVERSARIO_ENCONTRADO
            return True
        elif len(response) == 3 and response[0] == 'WAIT_CONNECTION':
            oppConnMode = response[0]
            sendP2PMessage(tcp, 'TRYING_TO_PLAY')
            opponentAddr[0] = response[1]
            opponentAddr[1] = response[2]
            estadoNet = NET.ADVERSARIO_ENCONTRADO
            return True

        return False

    def conectaAdversario(text):
        global estadoNet
        global tcp, oppConnMode, opponentAddr, oppConn
        text.draw(canvas)
        print(opponentAddr[0])
        if (oppConnMode == 'TRY_CONNECTION'):
            client, success = connectAsClientP2P(
                opponentAddr[0], int(opponentAddr[1]))
        elif (oppConnMode == 'WAIT_CONNECTION'):
            client, success = createServerP2P(
                '', int(opponentAddr[1]))

        if(success == True):
            oppConn = client
            sendP2PMessage(tcp, 'PLAYING')
            tcp.close()
            estadoNet = NET.PRONTO_PARA_JOGAR
            return True

        return False

    while(True):
        if canvas.isClosed():
            closeWindow(oppConn)

        limpaTela()

        if(estadoNet == NET.INICIO):
            iniciarJogo = Rectangle(
                Point(WIDTH/2-100, 2*HEIGHT/3-50), Point(WIDTH/2+100, 2*HEIGHT/3+50))
            iniciarJogo.setWidth(3)
            text = Text(Point(WIDTH/2, 2*HEIGHT/3), "Iniciar o jogo!")
            text.draw(canvas)
            drawX(WIDTH/2-100, HEIGHT/3-50, WIDTH/2, HEIGHT/3+50)
            drawO(WIDTH/2+50, HEIGHT/3, 50)
            iniciarJogo.draw(canvas)
            click = canvas.getMouse()

            if(inside(click, iniciarJogo)):
                estadoNet = NET.CONECTANDO_SERVIDOR

        elif(estadoNet == NET.CONECTANDO_SERVIDOR):
            print(server)
            text = Text(Point(WIDTH/2, 2*HEIGHT/3), "Conectando ao servidor.")

            ok = esperaServidor(text)

            if(not ok):
                text.setText(
                    "Não foi possível se conectar ao servidor, tente novamente mais tarde.")
                wait(2)
                estadoNet = NET.INICIO

        elif(estadoNet == NET.BUSCANDO_ADVERSARIO):
            text = Text(Point(WIDTH/2, 2*HEIGHT/3), "Buscando adversário.")
            wait(2)
            ok = buscaAdversario(text)
            if(not ok):
                text.setText(
                    "Nenhum adversário encontrado, tente novamente mais tarde.")
                tcp.close()
                tcp = None
                wait(2)
                estadoNet = NET.INICIO

        elif(estadoNet == NET.ADVERSARIO_ENCONTRADO):
            text = Text(Point(WIDTH/2, 2*HEIGHT/3),
                        "Adversário encontrado! Tentando se conectar.")
            wait(2)
            ok = conectaAdversario(text)

            if(not ok):
                text.setText("Não foi possível se conectar ao adversário.")
                canvas.update()
                wait(2)
                estadoNet = NET.BUSCANDO_ADVERSARIO

        elif (estadoNet == NET.FALHA_NA_CONEXÃO):
            text = Text(Point(WIDTH/2, 2*HEIGHT/3),
                        "A conexão com o adversário caiu ou ele está ausente.")
            oppConn = None
            if clientTcp != None:
                clientTcp.close()
            clientTcp = None
            text.draw(canvas)
            wait(2)
            estadoNet = NET.INICIO

        else:
            initGame()
            while(True):
                if canvas.isClosed():
                    closeWindow(oppConn)
                    break
                if (estadoNet == NET.FALHA_NA_CONEXÃO):
                    break
                if (estadoAtual == gameState.PLAYING):
                    if (oppConnMode == 'TRY_CONNECTION'):
                        if (jogadorAtual == Cell.X):
                            try:
                                onClick(canvas.getMouse())
                            except:
                                oppConn = None
                                estadoNet = NET.INICIO
                                break
                        else:
                            canvas.checkMouse()
                            response = actualCmd
                            if response == '':
                                continue
                            elif response == 'CLOSE_CONNECTION':
                                estadoNet = NET.INICIO
                                oppConn = None
                                break
                            else:
                                updateWaitGame(response)
                    elif (oppConnMode == 'WAIT_CONNECTION'):
                        if (jogadorAtual == Cell.O):
                            try:
                                onClick(canvas.getMouse())
                            except:
                                oppConn = None
                                estadoNet = NET.INICIO
                                break
                        else:
                            canvas.checkMouse()
                            response = actualCmd
                            if response == '':
                                continue
                            elif response == 'CLOSE_CONNECTION':
                                oppConn = None
                                estadoNet = NET.INICIO
                                break
                            else:
                                updateWaitGame(response)
                else:
                    mouse = canvas.checkMouse()
                    if mouse == None and actualCmd == '':
                        continue

                    if (actualCmd != ''):
                        response = actualCmd
                        actualCmd = ''

                        response = response.split()
                        if len(response) == 1 and response[0] == 'PLAY_AGAIN':
                            initGame()
                            continue
                        elif len(response) == 1 and response[0] == 'CLOSE_CONNECTION':
                            oppConn = None
                            estadoNet = NET.INICIO
                            continue
                    onClick(mouse)


Game()
