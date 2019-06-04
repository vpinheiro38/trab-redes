from graphics import *
import sys
import time
import threading
import socket
from api import *
from application import App
from globals import *
app = App()
canvas = GraphWin("Jogo da Velha", WIDTH, HEIGHT+50)


def wait(sec):
    timeNow = time.time()
    while time.time() - timeNow < sec:
        canvas.checkMouse()


def closeWindow(conn):
    app.sendMessage(conn, 'CLOSE_CONNECTION')
    app.sendMessage(conn, "sla")
    sys.exit()


def connectAsClientP2P(ip, port):
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    wait(2)

    try:
        client.connect((ip, port))
        print("connect %s : %d" % (ip, port))
        conn_handler = threading.Thread(target=handle_conn, args=(client,))
        conn_handler.start()
    except:
        return None, False

    return client, True


def createServerP2P(ip, port):
    global client, deftimeout
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("wait %s : %d" % (ip, port))
    client.bind((ip, port))
    client.listen(5)

    try:
        connection, addr = client.accept()
        print('accept')
        conn_handler = threading.Thread(target=handle_conn, args=(connection,))
        conn_handler.start()

    except:
        return None, False

    return connection, True


def handle_conn(socket):
    global actualCmd, closeWindow, canvas, connectionState, oppConn

    while True:
        response = getP2PMessage(socket)

        if response == 'CLOSE_CONNECTION' or canvas.isClosed():
            connectionState = NET.FALHA_NA_CONEXÃO

            break

        if (response != False):
            if (response == ''):
                break
            print('[*] Recebido: %s' % response)
            actualCmd = response

    socket.close()
    oppConn = None


def Game():
    global connectionState, closeWindow
    global message, oppConn, oppConnMode, actualCmd, canvas, tcp

    canvas.setBackground("white")
    message = Text(Point(WIDTH/2, HEIGHT+TEXT_SIZE/2), " ")
    message.setStyle("bold")
    connectionState = NET.INICIO

    def clearScreen():
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
        circleOutline = Circle(Point(x, y), r)
        circleOutline.setOutline("black")
        circleOutline.setWidth(5)
        circleOutline.draw(canvas)

        circle = Circle(Point(x, y), r)
        circle.setOutline("blue")
        circle.setWidth(3)
        circle.draw(canvas)

    def drawBoardLines():
        for linha in range(1, LINHAS):
            horizontal = Line(Point(0, CELL_SIZE * linha),
                              Point(WIDTH, CELL_SIZE * linha))
            horizontal.setWidth(3)
            horizontal.draw(canvas)

        for coluna in range(1, COLUNAS):
            vertical = Line(Point(CELL_SIZE * coluna, 0),
                            Point(CELL_SIZE * coluna, HEIGHT))
            vertical.setWidth(3)
            vertical.draw(canvas)

    def drawUserInputs():
        global tabuleiro
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

    def drawGameText():
        global message
        message.setSize(TEXT_SIZE)
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
        elif (estadoAtual == gameState.DRAW):
            message.setText("É um empate! Clique para jogar novamente.")
        elif (estadoAtual == gameState.X_GANHOU):
            message.setText("'O' Ganhou! Clique para jogar novamente.")
        elif (estadoAtual == gameState.O_GANHOU):
            message.setText("'X' Ganhou! Clique para jogar novamente.")
        message.setFace("arial")
        message.undraw()
        message.draw(canvas)

    def drawExitButton():
        sair = Rectangle(
            Point(WIDTH/2-30, HEIGHT+TEXT_SIZE+10), Point(WIDTH/2+30, HEIGHT+TEXT_SIZE+30))
        sair.setWidth(3)
        text = Text(Point(WIDTH/2,  HEIGHT+TEXT_SIZE+20), "Sair")
        text.setTextColor("red")
        sair.draw(canvas)
        text.draw(canvas)

    def inside(clickedPoint, rectangle):
        lowerLeft = rectangle.getP1()
        upperRight = rectangle.getP2()
        return lowerLeft.getX() < clickedPoint.getX() < upperRight.getX() and lowerLeft.getY() < clickedPoint.getY() < upperRight.getY()

    def updateCanvas():
        drawBoardLines()
        drawUserInputs()
        drawGameText()
        drawExitButton()

    def closeConection():
        global connectionState, oppConn, client
        connectionState = NET.INICIO
        app.sendMessage(oppConn, 'CLOSE_CONNECTION')
        oppConn = None
        client.close()
        print("closeConenction: ", client)

    def isValidCell(line, column):
        return (line >= 0 and line < LINHAS and column >= 0 and column < COLUNAS
                and tabuleiro[line][column] == Cell.EMPTY)

    def makeMove(player, linha, coluna):
        global estadoAtual, jogadorAtual, tabuleiro
        global message, oppConn

        app.sendMessage(oppConn, 'CLICKED %s %s' % (linha, coluna))
        tabuleiro[linha][coluna] = player

        if (ganhou(player, linha, coluna)):
            estadoAtual = (gameState.X_GANHOU, gameState.O_GANHOU)[
                player == Cell.X]
        elif (empatou()):
            estadoAtual = gameState.DRAW
        else:
            jogadorAtual = (Cell.X, Cell.O)[player == Cell.X]
        updateCanvas()

    def onClick(pos, isMyTurn):
        global tabuleiro
        global estadoAtual, oppConn

        sair = Rectangle(Point(WIDTH/2-30, HEIGHT+TEXT_SIZE+10),
                         Point(WIDTH/2+30, HEIGHT+TEXT_SIZE+30))
        selectedColumn = int(pos.getX() / CELL_SIZE)
        selectedLine = int(pos.getY() / CELL_SIZE)

        if(inside(pos, sair)):
            closeConection()
            return
        if(isMyTurn):
            if (estadoAtual == gameState.PLAYING):
                if isValidCell(selectedLine, selectedColumn):
                    makeMove(jogadorAtual, selectedLine, selectedColumn)
            else:
                app.sendMessage(oppConn, 'PLAY_AGAIN')
                initGame()

    def initGame():
        global estadoAtual
        global jogadorAtual
        global tabuleiro

        clearScreen()
        estadoAtual = gameState.PLAYING
        jogadorAtual = Cell.X
        row = [Cell.EMPTY]*LINHAS
        tabuleiro = [list(row) for i in range(COLUNAS)]
        updateCanvas()

    def updateWaitingGame(response):
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
            estadoAtual = gameState.DRAW
        else:
            jogadorAtual = (Cell.X, Cell.O)[player == Cell.X]
        updateCanvas()

    def ganhou(player, linha, coluna):
        global tabuleiro
        print("ganhou: ", linha == coluna
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

    

    def searchOpponent(text):
        global connectionState
        global tcp, oppConnMode, opponentAddr, actualCmd
        text.draw(canvas)

        app.sendMessage(tcp, 'AVAILABLE')

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
            app.sendMessage(tcp, 'TRYING_TO_PLAY')
            opponentAddr[0] = response[1]
            opponentAddr[1] = response[2]
            connectionState = NET.ADVERSARIO_ENCONTRADO
            return True
        elif len(response) == 3 and response[0] == 'WAIT_CONNECTION':
            oppConnMode = response[0]
            app.sendMessage(tcp, 'TRYING_TO_PLAY')
            opponentAddr[0] = response[1]
            opponentAddr[1] = response[2]
            connectionState = NET.ADVERSARIO_ENCONTRADO
            return True

        return False

    def conectaAdversario(text):
        global connectionState
        global tcp, oppConnMode, opponentAddr, oppConn
        text.draw(canvas)

        if (oppConnMode == 'TRY_CONNECTION'):
            client, success = connectAsClientP2P(
                opponentAddr[0], int(opponentAddr[1]))
        elif (oppConnMode == 'WAIT_CONNECTION'):
            client, success = createServerP2P(
                '', int(opponentAddr[1]))

        if(success == True):
            oppConn = client
            app.sendMessage(tcp, 'PLAYING')
            tcp.close()
            connectionState = NET.PRONTO_PARA_JOGAR
            return True

        return False

    def drawInitialScreen():
        global connectionState
        # TODO: DRAW BUTTON FUNCTION
        iniciarJogo = Rectangle(
            Point(WIDTH/2-100, 2*HEIGHT/3-50), Point(WIDTH/2+100, 2*HEIGHT/3+50))
        iniciarJogo.setWidth(3)
        text = Text(Point(WIDTH/2, 2*HEIGHT/3), "Iniciar o jogo!")
        iniciarJogo.draw(canvas)
        text.draw(canvas)
        drawX(WIDTH/2-100, HEIGHT/3-50, WIDTH/2, HEIGHT/3+50)
        drawO(WIDTH/2+50, HEIGHT/3, 50)
        click = canvas.getMouse()

        if(inside(click, iniciarJogo)):
            connectionState = NET.CONECTANDO_SERVIDOR

    def closeTcpConnection():
        global tcp, connectionState
        tcp.close()
        tcp = None
        connectionState = NET.INICIO

    def setWaitText(string):
        text = Text(Point(WIDTH/2, 2*HEIGHT/3), string)
        return text

    def connectingToServerScreen():
        global connectionState
        text = setWaitText("Conectando ao servidor.")
        text.draw(canvas)
        wait(2)
        ok = app.conectToServer()

        if(not ok):
            text.setText(
                "Não foi possível se conectar ao servidor, tente novamente mais tarde.")
            wait(2)
            connectionState = NET.INICIO

    def searchOpponentScreen():
        text = setWaitText("Buscando adversário.")
        ok = searchOpponent(text)
        if(not ok):
            text.setText(
                "Nenhum adversário encontrado, tente novamente mais tarde.")
            closeTcpConnection()
            wait(2)

    def connectingToOpponentScreen():
        global connectionState
        text = setWaitText("Adversário encontrado! Tentando se conectar.")
        ok = conectaAdversario(text)

        if(not ok):
            text.setText("Não foi possível se conectar ao adversário.")
            canvas.update()
            wait(2)
            connectionState = NET.BUSCANDO_ADVERSARIO

    def connectionFailScreen():
        global oppConn, connectionState
        text = setWaitText("A conexão com o adversário caiu.")
        client.close()
        oppConn = None
        text.draw(canvas)
        wait(2)
        connectionState = NET.INICIO

    def dealWithUserInput():
        global oppConn, closeWindow, connectionState
        if (oppConnMode == 'TRY_CONNECTION'):
            if (jogadorAtual == Cell.X):
                # Make my move
                try:
                    onClick(canvas.getMouse(), True)
                except:
                    oppConn = None
                    closeWindow = True
                    connectionState = NET.INICIO
            else:
                # Wait opponent move
                mouse = canvas.checkMouse()
                if mouse != None:
                    onClick(mouse, False)
                response = actualCmd
                if response == '':
                    return
                elif response == 'CLOSE_CONNECTION':
                    connectionState = NET.INICIO
                    oppConn = None
                else:
                    updateWaitingGame(response)
        elif (oppConnMode == 'WAIT_CONNECTION'):
            if (jogadorAtual == Cell.O):
                # Make my move
                try:
                    onClick(canvas.getMouse(), True)
                except:
                    oppConn = None
                    connectionState = NET.INICIO
            else:
                # Wait opponent move
                mouse = canvas.checkMouse()
                if mouse != None:
                    onClick(mouse, False)
                response = actualCmd
                if response == '':
                    return
                elif response == 'CLOSE_CONNECTION':
                    print("dealWithUserInput: ", response)
                    oppConn = None
                    connectionState = NET.INICIO
                else:
                    print("dealWithUserInput: ", response)
                    updateWaitingGame(response)

    while(True):
        if canvas.isClosed():
            closeWindow(oppConn)

        clearScreen()

        if(connectionState == NET.INICIO):
            drawInitialScreen()

        elif(connectionState == NET.CONECTANDO_SERVIDOR):
            connectingToServerScreen()

        elif(connectionState == NET.BUSCANDO_ADVERSARIO):
            searchOpponentScreen()

        elif(connectionState == NET.ADVERSARIO_ENCONTRADO):
            connectingToOpponentScreen()

        elif (connectionState == NET.FALHA_NA_CONEXÃO):
            connectionFailScreen()

        else:
            initGame()
            while(True):
                if (connectionState != NET.PRONTO_PARA_JOGAR):
                    break
                if (estadoAtual == gameState.PLAYING):
                    dealWithUserInput()
                else:
                    mouse = canvas.checkMouse()
                    if (mouse == None and actualCmd != ''):
                        response = actualCmd
                        actualCmd = ''
                        response = response.split()
                        if len(response) == 1 and response[0] == 'PLAY_AGAIN':
                            initGame()
                            continue
                        elif len(response) == 1 and response[0] == 'CLOSE_CONNECTION':
                            oppConn = None
                            connectionState = NET.INICIO
                            continue

                    if(mouse != None):
                        onClick(mouse, True)


Game()
