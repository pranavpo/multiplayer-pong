import socket
import threading
import pickle

# Initializing the players list to hold two player objects or None
players = [None, None]

# This function handles communication with each connected client


def handle_client(conn, addr, player_number):
    print(f"Player {player_number} connected from {addr}")
    try:
        while True:
            data = conn.recv(4096)  # Receive data from client
            if not data:
                print(f"Player {player_number} disconnected.")
                break
            # Deserialize the received data (Striker object)
            striker = pickle.loads(data)
            # Store the player's striker object
            players[player_number - 1] = striker

            # Determine the other player's number
            other_player = 1 if player_number == 2 else 2

            # If the other player is ready, send their striker object
            if players[other_player - 1]:
                # Send data back to the player
                conn.sendall(pickle.dumps(players[other_player - 1]))
    except Exception as e:
        print(f"Error handling Player {player_number}: {e}")
    finally:
        conn.close()  # Ensure the connection is closed when done

# Main server function


def server():
    host = "127.0.0.1"
    port = 65434
    player_count = 0  # Counter to track the number of players connected

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(2)  # Maximum of 2 players

        print(f"Server listening on {host}:{port}...")

        # Accept connections for 2 players
        while player_count < 2:
            conn, addr = server_socket.accept()

            # Assign player number (1 or 2)
            player_count += 1
            player_number = player_count  # Assign player_number based on connection order

            threading.Thread(target=handle_client, args=(
                conn, addr, player_number)).start()

        print("Both players are connected. Server is running...")


# Start the server
if __name__ == "__main__":
    server()
