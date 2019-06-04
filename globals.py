from enum import Enum
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
    DRAW = 2
    X_GANHOU = 3
    O_GANHOU = 4


class Cell(Enum):
    EMPTY = 1
    X = 2
    O = 3


sizeofmessage = 1024
deftimeout = 20
HOST = 'localhost'     # Endereco IP do Servidor
PORT = 5100            # Porta que o Servidor esta
tcp = None
client = None
server = (HOST, PORT)
opponentAddr = [None, None]
oppConnMode = 'TRY_CONNECTION'
oppConn = None
actualCmd = ''
connectionState = None
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
TEXT_SIZE = 12
