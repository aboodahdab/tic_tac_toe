import socket
import threading

clients = []


def check_winner(board, symbol):
    # Check rows
    for row in board:
        if all(cell == symbol for cell in row):
            return True

    # Check columns
    for col in range(3):
        if all(board[row][col] == symbol for row in range(3)):
            return True

    # Check diagonals
    if all(board[i][i] == symbol for i in range(3)):
        return True
    if all(board[i][2 - i] == symbol for i in range(3)):
        return True

    return False


def format_board(board):
    # Returns a string representation of the board
    lines = []
    for row in board:
        lines.append(' | '.join(cell if cell else ' ' for cell in row))
    return '\n---------\n'.join(lines)


def handle_game(player1, player2):
    board = [['', '', ''], ['', '', ''], ['', '', '']]
    turn = 0
    players = [player1, player2]
    symbols = ['X', 'O']

    try:
        player1.send("Game started. You're Player 1 (X)".encode())
        player2.send("Game started. You're Player 2 (O)".encode())
    except Exception as e:
        print(f"Failed to send start message: {e}")
        player1.close()
        player2.close()
        return

    while True:
        current_player = players[turn % 2]
        other_player = players[(turn + 1) % 2]
        symbol = symbols[turn % 2]

        try:
            current_player.send(
                ("\n" + format_board(board) + "\nYour move (row,col): ").encode())

            move_data = current_player.recv(1024)
            if not move_data:
                raise ConnectionError("No data received (disconnected).")

            move = move_data.decode().strip()
            print(f"Player {turn % 2 + 1} ({symbol}) move: {move}")

            try:
                row, col = map(int, move.split(","))
                row -= 1
                col -= 1
                if row not in range(3) or col not in range(3):
                    current_player.send(
                        "Invalid move. Out of bounds.".encode())
                    continue
                if board[row][col] != "":
                    current_player.send(
                        "Invalid move. Cell already taken.".encode())
                    continue
                board[row][col] = symbol
            except ValueError:
                current_player.send(
                    "Invalid move format. Use row,col".encode())
                continue

            if check_winner(board, symbol):
                board_str = format_board(board)
                current_player.send(
                    (board_str + "\nYou win!").encode())
                other_player.send(
                    (board_str + "\nYou lose!").encode())
                current_player.close()
                other_player.close()
                break
            if all(cell != "" for row in board for cell in row):
                board_str = format_board(board)
                for player in [current_player, other_player]:
                    player.send(
                        (board_str + "\nIt's a draw!").encode())
                    player.close()
                break

            # Notify both players of the move and board
            board_str = format_board(board)
            for player in players:
                try:
                    player.send(
                        (f"Player {turn % 2 + 1} ({symbol}) moved: {move}\n" + board_str).encode())
                except:
                    pass  # It's fine if one player already disconnected

            turn += 1

        except Exception as e:
            print(f"Player {turn % 2 + 1} disconnected or error occurred: {e}")
            try:
                other_player.send(
                    "Your opponent has disconnected. You win!".encode())
            except:
                print("Couldn't notify other player — already disconnected?")
            finally:
                current_player.close()
                other_player.close()
            break


def client_handler(client_socket):
    try:
        clients.append(client_socket)
        if len(clients) >= 2:
            player1 = clients.pop(0)
            player2 = clients.pop(0)
            game_thread = threading.Thread(
                target=handle_game, args=(player1, player2))
            game_thread.start()
    except Exception as e:
        print(f"Error handling client: {e}")
        client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 9999))  # Use a valid IP or localhost
    server.listen()
    print("Server is listening...")

    while True:
        client, addr = server.accept()
        print(f"New connection from {addr}")
        client_handler(client)


start_server()
