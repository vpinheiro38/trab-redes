from graphics import *
from enum import Enum

currentPlayer = None
estadoAtual = None
tabuleiro = None
message = None
LINHAS = 3
COLUNAS = 3
CELL_SIZE = 250
WIDTH = CELL_SIZE * COLUNAS
HEIGHT = CELL_SIZE * LINHAS
GRID_WIDTH = 8                   
GRID_WIDHT_HALF = GRID_WIDTH / 2
CELL_PADDING = CELL_SIZE / 6
TAM_SIMBOLO = CELL_SIZE - CELL_PADDING * 2
GROSSURA_SIMBOLO = 8
TEXT_SIZE = 36

class estados(Enum):
    PLAYING = 1
    EMPATE = 2
    X_GANHOU = 3
    O_GANHOU = 4

class Cell(Enum):
    EMPTY = 1
    X = 2
    O = 3


def Game():
    global message 
    canvas = GraphWin("Jogo da Velha", WIDTH, HEIGHT+TEXT_SIZE)
    message = Text(Point(WIDTH/2,HEIGHT+TEXT_SIZE/2), " ")
    message.setStyle("bold")
    

    def drawCanvas():
        global tabuleiro
        global message
        canvas.setBackground("white")
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
                    diagonal1 = Line(Point(x1,y1), Point(x2,y2))
                    diagonal1.setOutline("red") 
                    diagonal1.setWidth(3) 
                    diagonal1.draw(canvas)
                    diagonal2 = Line(Point(x2,y1), Point(x1,y2))
                    diagonal2.setOutline("red") 
                    diagonal2.setWidth(3) 
                    diagonal2.draw(canvas)
                if tabuleiro[linha][coluna]==Cell.O:
                    x1 = coluna * CELL_SIZE +CELL_SIZE/2
                    y1 = linha * CELL_SIZE +CELL_SIZE/2
                    bola = Circle(Point(x1,y1),TAM_SIMBOLO/2)
                    bola.setOutline("blue") 
                    bola.setWidth(3) 
                    bola.draw(canvas)

        message.setSize(TEXT_SIZE-20)
        if (estadoAtual == estados.PLAYING):
            message.setSize(TEXT_SIZE)
            if (currentPlayer == Cell.X):
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
                updateGame(currentPlayer, linhaSelecionada, colunaunaSelecionada)
                
            
        else:
            initGame()

    def initGame():
        global estadoAtual 
        global currentPlayer
        global tabuleiro
        
        for item in canvas.items[:]:
            item.undraw()
        canvas.update()

        estadoAtual = estados.PLAYING
        currentPlayer = Cell.X
        row = [Cell.EMPTY]*LINHAS
        tabuleiro = [list(row) for i in range(COLUNAS)]
        drawCanvas()

    def updateGame(player, linha, coluna):
        global estadoAtual 
        global currentPlayer
        global tabuleiro
        global estadoAtual
        global message
        tabuleiro[linha][coluna] = player
        if (ganhou(player, linha, coluna)):
            print("xasDSADASDASDAS")
            estadoAtual = (estados.X_GANHOU, estados.O_GANHOU)[player == Cell.X]
        elif (empatou()):
            estadoAtual = estados.EMPATE
        currentPlayer = (Cell.X,Cell.O)[player == Cell.X]
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
        

    initGame()
    while(True):
        onClick(canvas.getMouse())

Game()
