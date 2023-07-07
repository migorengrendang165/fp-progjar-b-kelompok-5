import pygame, sys
import numpy as np
import socket
import pickle
import threading

host = '127.0.0.2'
port = 8002
# Inisialisasi Pygame
pygame.init()
width = 400
height = width
line_width = 8
board_row = 3
board_colom = 3
square_size = width//board_colom
circle_width = 15 
cross_width = 25
circle_radius = square_size//3
space = square_size//4 
# Warna
BLACK = (193, 227, 226)
WHITE = (255, 255, 255)
BG_Color = (193, 227, 226)
line_color = (11, 13, 12)
circle_color = (5, 117, 8)
cross_color = (145, 143, 3)

# Membuat layar
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tic Tac Toe")
screen.fill(BG_Color)

player1 = "X"
player2 = "O"
player_mark = ''
turn = True

# Flag untuk menandai kotak yang sudah diisi
filled_boxes = [False] * 9

# Fungsi untuk menggambar grid
def draw_grid():
    #horizontal
    pygame.draw.line (screen, line_color,(0, square_size), (width, square_size), line_width)
    pygame.draw.line (screen, line_color,(0, 2 * square_size), (width, 2 * square_size), line_width)
    #vertikal
    pygame.draw.line (screen, line_color,(square_size, 0), (square_size, height), line_width)
    pygame.draw.line (screen, line_color,(2 * square_size, 0), (2 * square_size, height), line_width)

# Fungsi untuk menggambar simbol X atau O
def draw_symbols(board):
    for row in range(board_row):
        for col in range(board_colom):
            if board[row][col] == player1:
                pygame.draw.circle(screen, circle_color, (int(col * square_size + square_size // 2), int(row * square_size + square_size // 2)), circle_radius, circle_width)
            elif board[row][col] == player2:
                pygame.draw.line(screen, cross_color, (col * square_size + space, row * square_size + square_size - space), (col * square_size + square_size - space, row * square_size + space), cross_width) 
                pygame.draw.line(screen, cross_color, (col* square_size + space, row * square_size + space), (col * square_size + square_size - space, row * square_size + square_size - space), cross_width)

# Fungsi untuk mengirim data ke server
def send_data(conn, data):
    serialized_data = pickle.dumps(data)
    conn.send(serialized_data)

# Fungsi untuk menerima data dari server
def receive_data(conn):
    serialized_data = conn.recv(1024)
    data = pickle.loads(serialized_data)
    return data

# Fungsi untuk menangani input dari pemain
def handle_input(conn):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                conn.close()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Mendapatkan posisi klik mouse
                mouse_pos = pygame.mouse.get_pos()
                col = mouse_pos[0] // square_size
                row = mouse_pos[1] // square_size
                # Mengirim langkah ke server
                send_data(conn, (row, col))

def drawVerticalWin(colom, player):
    vertical = colom * square_size + square_size // 2
    if player == player1:
        color = circle_color
    elif player == player2:
        color = cross_color
    pygame.draw.line(screen, color, (vertical, 15), (vertical, height - 15), 15)
    
def drawHorisontalWin(row, player):
    horizontal = row * square_size + square_size // 2
    if player == player1:
        color = circle_color
    elif player == player2:
        color = cross_color
    pygame.draw.line(screen, color, (15, horizontal), (width - 15, horizontal), 15)

def draw_asc_diagonalWin(player):
    if player == player1:
        color = circle_color
    elif player == player2:
        color = cross_color
    pygame.draw.line(screen, color, (15, height - 15), (width - 15, 15), 15)

def draw_desc_diagonalWin(player):
    if player == player1:
        color = circle_color
    elif player == player2:
        color = cross_color  
    pygame.draw.line(screen, color, (15, 15), (width - 15, height - 15), 15)
    
def check_winner(self):
    for i in range(3):
        if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
            drawVerticalWin(colom, player)
            return self.board[i][0]
        if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
            drawHorisontalWin(row, player)
            return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            draw_desc_diagonalWin(player)
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            draw_asc_diagonalWin(player)
            return self.board[0][2]
        return None
    
def cekWin(player):
    #verticalwin
    for col in range (board_colom):
        if board[0][col] == player and board[1][col] == player and board[2][col] == player:
            drawVerticalWin(col, player)
            return True
       
    #horizontalwin
    for row in range (board_row):
        if board[row][0] == player and board[row][1] == player and board[row][2] == player:
            drawHorisontalWin(row, player)
            return True
        
    #asc_diagonalwin
    if board[2][0] == player and board[1][1] == player and board[0][2] == player:
        draw_asc_diagonalWin(player)
        return True
    
    #desc_diagonalwin
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        draw_desc_diagonalWin(player)
        return True
    return False

def mark_square(row,col, player):
    board[row][col] = player
 
def availableSquare (row, col):   
    return board [row][col] == 0 

# Fungsi untuk menjalankan client
def run_client(room_id):
    # Koneksi ke server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.send(room_id.encode())

    # Menentukan simbol pemain
    #coin_toss()
    toss_result = receive_data(client_socket)
    if toss_result == 0:
        symbol = player1
        print("Player 1: You got X and the first turn")
    elif toss_result == 1:
        symbol = player2
        print("Player 2: You got O and the second turn")
        
    # Thread untuk menangani input pemain
    threading.Thread(target=handle_input, args=(client_socket,)).start()

    # Loop permainan
    running = True
    gameOver = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                conn.close()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not gameOver:
                # Mendapatkan posisi klik mouse
                mouse_pos = pygame.mouse.get_pos()
                col = mouse_pos[0] // (width // 3)
                row = mouse_pos[1] // (height // 3)
                
                if availableSquare(col, row):  
                    if player == player1:
                        mark_square(col, row, player1)
                        if check_winner():
                            gameOver = True
                        player = player2
                       
                    elif player == player2:
                        mark_square(col, row, player2)
                        if check_winner():
                            gameOver = True
                        player = player1
                       
                    draw_grid()
        pygame.display.update()
            
        # Menerima data dari server
        action, data = receive_data(client_socket)

        if action == "start":
            print("Game started! Waiting for opponent's move...")
        elif action == "update":
            # Menggambar grid dan simbol
            draw_grid()
            draw_symbols(data)
            pygame.display.flip()
        elif action == "winner":
            if data == symbol:
                print("You win!")
            else:
                print("You lose!")
            running = False
        elif action == "tie":
            print("Game ended. It's a tie.")
            running = False

    # Menutup koneksi
    client_socket.close()
    pygame.quit()

# Menjalankan client
room_id = input("Enter room ID: ")
run_client(room_id)
