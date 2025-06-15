import socket
import threading


def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            if not message:
                print("Disconnected from server.")
                break
            print(f"\n{message}")
            if "Your move" in message:
                move = input("")
                sock.send(move.encode())
        except Exception as e:
            print(f"Error receiving data. Connection closed. ({e})")
            break


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 9999))
        print("Connected to the server.")
    except Exception as e:
        print(f"Could not connect: {e}")
        return
    recv_thread = threading.Thread(
        target=receive_messages, args=(client,), daemon=True)
    recv_thread.start()
    recv_thread.join()  # Wait for the receive thread to finish
    client.close()


if __name__ == "__main__":
    start_client()
