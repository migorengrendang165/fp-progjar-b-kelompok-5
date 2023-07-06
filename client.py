import pygame
import socket
import threading

HOST = '127.0.0.2'
PORT = 8002

room_id = ''

player_id = -1
player_mark = ''
turn = True

# Flag untuk menandai kotak yang sudah diisi
filled_boxes = [False] * 9


def draw_board(board):
    screen.fill((193, 227, 226))
    pygame.draw.line(screen, (11, 13, 12), (100, 0), (100, 300), 2)
    pygame.draw.line(screen, (11, 13, 12), (200, 0), (200, 300), 2)
    pygame.draw.line(screen, (11, 13, 12), (0, 100), (300, 100), 2)
    pygame.draw.line(screen, (11, 13, 12), (0, 200), (300, 200), 2)

    font = pygame.font.Font('freesansbold.ttf', 90)
    for i in range(9):
        x = (i % 3) * 100
        y = (i // 3) * 100

        if board[i] != '-':
            text = font.render(board[i], True, (0, 0, 0))
            screen.blit(text, (x + 30, y + 15))


def coin_toss():
    global player_mark, turn

    player_mark = 'X' if int(client.recv(1024).decode()) == 0 else 'O'
    if player_mark == 'X':
        print("Player 1: You got X and the first turn")
    if player_mark == 'O':
        print("Player 2: You got O and the second turn")


def send_data(pos):
    global turn

    if turn and board[pos] == '-' and (player_mark == 'X' or (player_mark == 'O' and not filled_boxes[pos])):
        board[pos] = player_mark
        filled_boxes[pos] = True
        draw_board(board)
        pygame.display.flip()

        data = player_mark + str(pos)
        client.sendall(str.encode(data))

        turn = turn


def send_data_thread():
    global turn  # Menambahkan kata kunci global

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and turn:
                x, y = pygame.mouse.get_pos()
                pos = (y // 100) * 3 + (x // 100)
                if 0 <= pos <= 8:
                    send_data(pos)
        pygame.event.pump()

        if check_winner(board) != -1 or '-' not in board:
            turn = False


def check_winner(board):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]  # diagonals
    ]
    for combination in winning_combinations:
        if board[combination[0]] == board[combination[1]] == board[combination[2]] != '-':
            return combination[0]
    return -1


def join_room():
    global room_id

    room_id = input("Enter room ID: ")
    client.sendall(str.encode(room_id))


pygame.init()
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Tic Tac Toe")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client.connect((HOST, PORT))

join_room()
coin_toss()

board = ['-' for _ in range(9)]
draw_board(board)

thread = threading.Thread(target=send_data_thread)
thread.start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            client.sendall(str.encode('quit'))
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and turn:
            x, y = pygame.mouse.get_pos()
            pos = (y // 100) * 3 + (x // 100)
            if 0 <= pos <= 8:
                send_data(pos)

    pygame.display.update()
    
# Add a game_over flag
game_over = False

while running and not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
            break
        elif event.type == pygame.MOUSEBUTTONDOWN and turn:
            x, y = pygame.mouse.get_pos()
            pos = (y // 100) * 3 + (x // 100)
            if 0 <= pos <= 8:
                send_data(pos)

# Close the connection before exiting the program
client.sendall(str.encode('quit'))
client.close()



pygame.quit()







