from graphics import *
import sys, time, threading

from enum import Enum

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

class NET(Enum):
    INICIO = 1
    CONECTANDO_SERVIDOR = 2
    FALHA_NA_CONEXÃO= 3
    BUSCANDO_ADVERSARIO = 4
    TIMEOUT = 5
    ADVERSARIO_ENCONTRADO = 6
    PRONTO_PARA_JOGAR = 7

class estados(Enum):
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



def Game():
    global estadoNet
    global message 
    canvas = GraphWin("Jogo da Velha", WIDTH, HEIGHT+TEXT_SIZE)
    canvas.setBackground("white")
    message = Text(Point(WIDTH/2,HEIGHT+TEXT_SIZE/2), " ")
    message.setStyle("bold")
    estadoNet = NET.INICIO

    def animacaoEspera():
        a = 1
        #TODO: FAZER ANIMAÇAO

    def limpaTela():
        for item in canvas.items[:]:
            item.undraw()
        canvas.update()

    def drawX(x1,y1,x2,y2):
        diagonal11 = Line(Point(x1,y1), Point(x2,y2))
        diagonal11.setOutline("black") 
        diagonal11.setWidth(5) 
        diagonal11.draw(canvas)

        diagonal12 = Line(Point(x1,y1), Point(x2,y2))
        diagonal12.setOutline("red") 
        diagonal12.setWidth(3) 
        diagonal12.draw(canvas)

        diagonal21 = Line(Point(x2,y1), Point(x1,y2))
        diagonal21.setOutline("black") 
        diagonal21.setWidth(5) 
        diagonal21.draw(canvas)

        diagonal22 = Line(Point(x2,y1), Point(x1,y2))
        diagonal22.setOutline("red") 
        diagonal22.setWidth(3) 
        diagonal22.draw(canvas)
        
    def drawO(x,y,r):
        bolaOutline = Circle(Point(x,y),r)
        bolaOutline.setOutline("black") 
        bolaOutline.setWidth(5) 
        bolaOutline.draw(canvas)

        bola = Circle(Point(x,y),r)
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
        for linha in range(1,LINHAS):
            vertical = Line(Point(0,CELL_SIZE * linha), Point(WIDTH,CELL_SIZE * linha))
            vertical.setWidth(3)
            vertical.draw(canvas)
                    
        for coluna in range(1,COLUNAS):
            horizontal =  Line(Point(CELL_SIZE * coluna, 0), Point(CELL_SIZE * coluna,HEIGHT))
            horizontal.setWidth(3)
            horizontal.draw(canvas)

        for linha in range(LINHAS):
            for coluna in range(COLUNAS):
                x1 = coluna * CELL_SIZE + CELL_PADDING
                y1 = linha * CELL_SIZE + CELL_PADDING
                if tabuleiro[linha][coluna]==Cell.X:
                    x2 = (coluna + 1) * CELL_SIZE - CELL_PADDING
                    y2 = (linha + 1) * CELL_SIZE - CELL_PADDING
                    drawX(x1,y1,x2,y2)
                if tabuleiro[linha][coluna]==Cell.O:
                    x = coluna * CELL_SIZE +CELL_SIZE/2
                    y = linha * CELL_SIZE +CELL_SIZE/2
                    drawO(x,y,TAM_SIMBOLO/2)
                    

        message.setSize(TEXT_SIZE-20)
        if (estadoAtual == estados.PLAYING):
            message.setSize(TEXT_SIZE)
            if (jogadorAtual == Cell.X):
                message.setText("Vez do X")
            else:
               message.setText("Vez da O")
            
        elif (estadoAtual == estados.EMPATE):
            message.setText("É um empate! Clique para jogar novamente.")
        elif (estadoAtual == estados.X_GANHOU):
            message.setText("'O' Ganhou! Clique para jogar novamente.")
        elif (estadoAtual == estados.O_GANHOU):
            message.setText("'X' Ganhou! Clique para jogar novamente.")
        message.setFace("arial")
        message.undraw();
        message.draw(canvas);
         
    
    def onClick(pos):
        global tabuleiro
        global estadoAtual
        print(estadoAtual)
        colunaunaSelecionada= int(pos.getX() / CELL_SIZE)
        linhaSelecionada = int(pos.getY() / CELL_SIZE)
 
        if estadoAtual == estados.PLAYING:
            if (linhaSelecionada >= 0 and linhaSelecionada < LINHAS and colunaunaSelecionada >= 0 and colunaunaSelecionada < COLUNAS 
            and tabuleiro[linhaSelecionada][colunaunaSelecionada] == Cell.EMPTY):
                updateGame(jogadorAtual, linhaSelecionada, colunaunaSelecionada)
                
            
        else:
            initGame()

    def initGame():
        global estadoAtual 
        global jogadorAtual
        global tabuleiro
        
        limpaTela()

        estadoAtual = estados.PLAYING
        jogadorAtual = Cell.X
        row = [Cell.EMPTY]*LINHAS
        tabuleiro = [list(row) for i in range(COLUNAS)]
        drawCanvas()

    def updateGame(player, linha, coluna):
        global estadoAtual 
        global jogadorAtual
        global tabuleiro
        global estadoAtual
        global message
        tabuleiro[linha][coluna] = player
        if (ganhou(player, linha, coluna)):
            estadoAtual = (estados.X_GANHOU, estados.O_GANHOU)[player == Cell.X]
        elif (empatou()):
            estadoAtual = estados.EMPATE
        jogadorAtual = (Cell.X,Cell.O)[player == Cell.X]
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
        text.draw(canvas)
        while(True):
            text.move(-4,0)
            text.setText("Conectando ao servidor.")
            time.sleep(0.3)
            text.move(2,0)
            text.setText("Conectando ao servidor..")
            time.sleep(0.3)
            text.move(2,0)
            text.setText("Conectando ao servidor...")
            time.sleep(0.3)
            if(True):#TODO: FUNCAO PARA CONECTAR AO SERVIDOR
                estadoNet = NET.BUSCANDO_ADVERSARIO
                return True
            else:
                estadoNet = NET.FALHA_NA_CONEXÃO
                return False

    def buscaAdversario(text):
        global estadoNet
        text.draw(canvas)
        count = 0
        while(count < 10):
            count += 1
            text.move(-4,0)
            text.setText("Buscando adversário.")
            time.sleep(0.3)
            text.move(2,0)
            text.setText("Buscando adversário..")
            time.sleep(0.3)
            text.move(2,0)
            text.setText("Buscando adversário...")
            time.sleep(0.3)
            if(True):#TODO: FUNCAO PARA PROCURAR ADVERSARIO
                estadoNet = NET.ADVERSARIO_ENCONTRADO
                return True
        return False

    def conectaAdversario(text):
        global estadoNet
        text.draw(canvas)
        count = 0
        while(count < 10):
            count += 1
            text.move(-4,0)
            text.setText("Adversário encontrado! Tentando se conectar.")
            time.sleep(0.3)
            text.move(2,0)
            text.setText("Adversário encontrado! Tentando se conectar..")
            time.sleep(0.3)
            text.move(2,0)
            text.setText("Adversário encontrado! Tentando se conectar...")
            time.sleep(0.3)
            if(False):#TODO: FUNCAO PARA CONECTAR AO ADVERSARIO
                estadoNet = NET.PRONTO_PARA_JOGAR
                return True
        return False

    while(True):
        limpaTela()
        if(estadoNet == NET.INICIO):
            iniciarJogo = Rectangle(Point(WIDTH/2-100, 2*HEIGHT/3-50), Point(WIDTH/2+100, 2*HEIGHT/3+50))
            iniciarJogo.setWidth(3)
            text = Text(Point(WIDTH/2, 2*HEIGHT/3), "Iniciar o jogo!")
            text.draw(canvas)
            drawX(WIDTH/2-100,HEIGHT/3-50,WIDTH/2,HEIGHT/3+50)
            drawO(WIDTH/2+50,HEIGHT/3,50)
            iniciarJogo.draw(canvas)
            click = canvas.getMouse()
            if(inside(click,iniciarJogo)):
                estadoNet = NET.CONECTANDO_SERVIDOR

        elif(estadoNet == NET.CONECTANDO_SERVIDOR):
            text = Text(Point(WIDTH/2, 2*HEIGHT/3), "Conectando ao servidor.")
            ok = esperaServidor(text)
            if(not ok):
                text.setText("Não foi possível se conectar ao servidor, tente novamente mais tarde.")
                time.sleep(3)
                estadoNet = NET.INICIO
            

        elif(estadoNet == NET.BUSCANDO_ADVERSARIO):
            text = Text(Point(WIDTH/2, 2*HEIGHT/3), "Buscando adversário.")
            ok = buscaAdversario(text)
            if(not ok):
                text.setText("Nenhum adversário encontrado, tente novamente mais tarde.")
                time.sleep(3)
                estadoNet = NET.INICIO

        elif(estadoNet == NET.ADVERSARIO_ENCONTRADO):
            text = Text(Point(WIDTH/2, 2*HEIGHT/3), "Adversário encontrado! Tentando se conectar.")
            ok = conectaAdversario(text)
            if(not ok):
                text.setText("Não foi possível se conectar ao adversário.")
                canvas.update()
                time.sleep(3)
                estadoNet = NET.BUSCANDO_ADVERSARIO

        
        else:
            initGame()
            while(True):
                onClick(canvas.getMouse())
    

Game()
