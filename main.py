import pygame as pg,sys
from pygame.locals import *
import time


#inisialisasi
XO = 'x'
pemenang = None; gambar = False
lebar = 400; tinggi = 400
biru = (0, 255, 255)
warna_garis = (10,10,10)

#papan 3x3
TTT = [[None]*3,[None]*3,[None]*3]

#inisialisasi pygame
pg.init()
fps = 30
CLOCK = pg.time.Clock()
screen = pg.display.set_mode((lebar, tinggi+100),0,32)
pg.display.set_caption("Tic Tac Toe")

#muat gambar
opening = pg.image.load('tic tac toe.png')
x_img = pg.image.load('x.png')
o_img = pg.image.load('o.png')

#atur ukuran gambar
x_img = pg.transform.scale(x_img, (80,80))
o_img = pg.transform.scale(o_img, (80,80))
opening = pg.transform.scale(opening, (lebar, tinggi+100))

def tampilan_game():
    screen.blit(opening,(0,0))
    pg.display.update()
    time.sleep(1)
    screen.fill(biru)

    # buat garis vertikal
    pg.draw.line(screen,warna_garis,(lebar/3,0),(lebar/3, tinggi),7)
    pg.draw.line(screen,warna_garis,(lebar/3*2,0),(lebar/3*2, tinggi),7)
    # buat garis horizontal
    pg.draw.line(screen,warna_garis,(0,tinggi/3),(lebar, tinggi/3),7)
    pg.draw.line(screen,warna_garis,(0,tinggi/3*2),(lebar, tinggi/3*2),7)
    gambar_status()

def gambar_status():
    global gambar

    if pemenang is None:
        message = "Gilirannya " + XO.upper()
    else:
        message = pemenang.upper() + " MENANG...!"
    if gambar:
        message = 'Game gambar!'

    font = pg.font.Font(None, 30)
    text = font.render(message, 1, (255, 255, 255))

    # copy the rendered message onto the board
    screen.fill ((0, 0, 0), (0, 400, 500, 100))
    text_rect = text.get_rect(center=(lebar/2, 500-50))
    screen.blit(text, text_rect)
    pg.display.update()

def cek_menang():
    global TTT, pemenang,gambar

    # meriksa pemenang baris
    for row in range (0,3):
        if ((TTT [row][0] == TTT[row][1] == TTT[row][2]) and(TTT [row][0] is not None)):
            # baris menang
            pemenang = TTT[row][0]
            pg.draw.line(screen, (250,0,0), (0, (row + 1)*tinggi/3 -tinggi/6),\
                              (lebar, (row + 1)*tinggi/3 - tinggi/6 ), 4)
            break

    # periksa pemenang kolom
    for col in range (0, 3):
        if (TTT[0][col] == TTT[1][col] == TTT[2][col]) and (TTT[0][col] is not None):
            # kolom menang
            pemenang = TTT[0][col]
            #buat garis menang
            pg.draw.line (screen, (250,0,0),((col + 1)* lebar/3 - lebar/6, 0),\
                          ((col + 1)* lebar/3 - lebar/6, tinggi), 4)
            break

    # periksa untuk diagonal pemenangs
    if (TTT[0][0] == TTT[1][1] == TTT[2][2]) and (TTT[0][0] is not None):
        # game won diagonally left to right
        pemenang = TTT[0][0]
        pg.draw.line (screen, (250,70,70), (50, 50), (350, 350), 4)

    if (TTT[0][2] == TTT[1][1] == TTT[2][0]) and (TTT[0][2] is not None):
        # game won diagonally right to left
        pemenang = TTT[0][2]
        pg.draw.line (screen, (250,70,70), (350, 50), (50, 350), 4)

    if(all([all(row) for row in TTT]) and pemenang is None ):
        draw = True
    gambar_status()

def gambarXO(row,col):
    global TTT,XO
    if row==1:
        posx = 30
    if row==2:
        posx = lebar/3 + 30
    if row==3:
        posx = lebar/3*2 + 30

    if col==1:
        posy = 30
    if col==2:
        posy = tinggi/3 + 30
    if col==3:
        posy = tinggi/3*2 + 30
    TTT[row-1][col-1] = XO
    if(XO == 'x'):
        screen.blit(x_img,(posy,posx))
        XO= 'o'
    else:
        screen.blit(o_img,(posy,posx))
        XO= 'x'
    pg.display.update()
    #print(posx,posy)
    #print(TTT)

def userInput():
    #get coordinates of mouse click
    x,y = pg.mouse.get_pos()

    #get column of mouse click (1-3)
    if(x<lebar/3):
        col = 1
    elif (x<lebar/3*2):
        col = 2
    elif(x<lebar):
        col = 3
    else:
        col = None

    #get row of mouse click (1-3)
    if(y<tinggi/3):
        row = 1
    elif (y<tinggi/3*2):
        row = 2
    elif(y<tinggi):
        row = 3
    else:
        row = None
    #print(row,col)

    if(row and col and TTT[row-1][col-1] is None):
        global XO

        #gambar the x or o on screen
        gambarXO(row,col)
        cek_menang()

def ulangi():
    global TTT, pemenang,XO, gambar
    time.sleep(3)
    XO = 'x'
    gambar = False
    tampilan_game()
    pemenang=None
    TTT = [[None]*3,[None]*3,[None]*3]

tampilan_game()

# run the game loop forever
while(True):
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit(); sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            # the user clicked; place an X or O
            userInput()
            if(pemenang or gambar):
                ulangi()

    pg.display.update()
    CLOCK.tick(fps)