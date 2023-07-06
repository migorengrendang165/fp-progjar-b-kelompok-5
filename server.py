import socket
import threading

HOST = '127.0.0.2'
PORT = 8002

rooms = {}
player_marks = {}
room_locks = {}


def handle_client(client_socket, room_id, player_id):
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            if data == 'quit':
                break
            if data.isdigit():
                opponent_id = 1 - player_id
                opponent_socket = rooms[room_id][opponent_id]
                opponent_socket.sendall(str.encode(data))
            else:
                mark, pos = data[0], int(data[1:])
                room_lock = room_locks[room_id]
                with room_lock:
                    board = rooms[room_id][2]
                    if mark == player_marks[player_id] and board[pos] == '-' and (
                            (player_marks[player_id] == 'X' and not rooms[room_id][3]) or
                            (player_marks[player_id] == 'O' and rooms[room_id][3])
                    ):
                        board[pos] = mark
                        if player_marks[player_id] == 'X':
                            rooms[room_id][3] = True
                        opponent_id = 1 - player_id
                        opponent_socket = rooms[room_id][opponent_id]
                        opponent_socket.sendall(str.encode(data))
                        opponent_socket.sendall(str.encode(opponent_socket.recv(1024).decode()))  # Send the updated board state to the opponent
                    else:
                        if mark == player_marks[player_id]:
                            client_socket.sendall(str.encode('-2'))  # Invalid move by the player
                        else:
                            client_socket.sendall(str.encode('-3'))  # Invalid move, it's not player's turn
        except:
            break

    client_socket.close()
    if room_id in rooms:
        del rooms[room_id]


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(2)
    print("Server is running.")

    while True:
        client_socket, addr = server_socket.accept()
        room_id = client_socket.recv(1024).decode()
        if room_id in rooms:
            if len(rooms[room_id]) < 4:
                player_id = len(rooms[room_id])
                rooms[room_id].append(client_socket)
                player_marks[player_id] = 'O' if player_id % 2 == 1 else 'X'
                client_socket.sendall(str.encode(str(player_id)))
                print(f"Player {player_id} joined room {room_id}")
                if len(rooms[room_id]) == 4:
                    room_locks[room_id] = threading.Lock()
                    thread = threading.Thread(target=handle_client, args=(rooms[room_id][1], room_id, 1))
                    thread.start()
                    thread = threading.Thread(target=handle_client, args=(rooms[room_id][2], room_id, 2))
                    thread.start()
                    rooms[room_id][3] = False  # Flag to track whether player X has made a move
            else:
                client_socket.sendall(str.encode('-1'))  # Room is full
                client_socket.close()
        else:
            rooms[room_id] = [client_socket]
            player_id = 0
            player_marks[player_id] = 'X'
            client_socket.sendall(str.encode(str(player_id)))
            print(f"Player {player_id} created room {room_id}")

    server_socket.close()


start_server()
