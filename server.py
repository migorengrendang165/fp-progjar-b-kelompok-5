import socket
import threading
import pickle
import random

# Inisialisasi server socket
host = "127.0.0.2"
port = 8002
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()
print("Server is running.")

# Daftar room
rooms = {}

player1 = "X"
player2 = "O"
# Kelas untuk mengelola setiap room
class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = []
        self.current_turn = 0
        self.board = [[" " for _ in range(3)] for _ in range(3)]

    def add_player(self, conn):
        self.players.append(conn)

    def broadcast(self, data):
        serialized_data = pickle.dumps(data)
        for player in self.players:
            player.send(serialized_data)

    def handle_turn(self, conn, row, col):
        if conn == self.players[self.current_turn]:
            symbol = player1 if self.current_turn == 0 else player2
            if self.board[row][col] == " ":
                self.board[row][col] = symbol
                self.broadcast(("update", self.board))
                winner = self.check_winner()
                if winner:
                    self.broadcast(("winner", winner))
                    self.reset()
                elif self.check_tie():
                    self.broadcast(("tie", None))
                    self.reset()
                else:
                    self.current_turn = (self.current_turn + 1) % 2
        
    
    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                return self.board[0][i]
            if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
                return self.board[0][0]
            if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
                return self.board[0][2]
            return None
     

    def check_tie(self):
        for row in self.board:
            if " " in row:
                return False
        return True

    def reset(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_turn = 0

    def toss_coin(self):
        return random.choice([0, 1])

# Fungsi untuk mengelola koneksi client dalam thread terpisah
def handle_client(conn):
    room_id = conn.recv(1024).decode()
    if room_id not in rooms:
        rooms[room_id] = Room(room_id)
    room = rooms[room_id]
    room.add_player(conn)
    conn.send(pickle.dumps("Waiting for opponent..."))
    if len(room.players) == 2:
        toss_result = room.toss_coin()
        if toss_result == 0:
            print("Player 1: You got X and the first turn")
        elif toss_result == 1:
            print("Player 2: You got O and the second turn")
        
        room.broadcast(("toss_result", toss_result))
        room.current_turn = toss_result
        room.broadcast(("start", None))
    while True:
        try:
            data = conn.recv(1024)
            if data:
                row, col = pickle.loads(data)
                room.handle_turn(conn, row, col)
            else:
                raise Exception("Disconnected")
        except:
            room.players.remove(conn)
            conn.close()
            break

# Fungsi untuk menerima koneksi dan memulai thread baru
def accept_connections():
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn,)).start()

# Memulai server
accept_connections()
